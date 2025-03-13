import os
import random
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# Configuração segura do MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = "monopoly"

# Conectar ao MongoDB de forma assíncrona
client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]

app = FastAPI(title="API Monopoly", description="API para gerenciamento de partidas e jogadores")

# Função auxiliar para converter documentos MongoDB
async def convert_id(doc):
    if doc and "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    return doc

# Modelos Pydantic para validação
class Action(BaseModel):
    action: str = Field(..., min_length=3)
    details: Optional[Dict] = {}

class Game(BaseModel):
    players: List[str] = Field(..., min_items=2, max_items=6)
    turn: Optional[str] = None
    status: Optional[str] = Field("in_progress", regex="^(in_progress|finished)$")
    history: Optional[List[Action]] = []

# Rolar dados e movimentar jogador
@app.get("/roll/{player_id}")
async def roll_dice(player_id: str):
    roll = random.randint(1, 6) + random.randint(1, 6)
    player = await db.jogadores.find_one({"_id": player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    old_position = player["posicao"]
    new_position = (old_position + roll) % 40  # Tabuleiro de 40 casas
    
    # Se passar pelo ponto de partida
    if old_position > new_position:
        await db.jogadores.update_one({"_id": player_id}, {"$inc": {"saldo": 200}})
    
    await db.jogadores.update_one({"_id": player_id}, {"$set": {"posicao": new_position}})
    
    # Verificar ações da casa
    endereco = await db.enderecos.find_one({"_id": str(new_position)})
    if endereco:
        if endereco["tipo"] == "especial" and endereco["_id"] == "go_to_jail":
            await db.jogadores.update_one({"_id": player_id}, {"$set": {"posicao": 10, "preso": True}})
            return {"player_id": player_id, "dice_roll": roll, "new_position": 10, "message": "Sent to jail"}
    
    return {"player_id": player_id, "dice_roll": roll, "new_position": new_position}

# Comprar propriedade
@app.post("/buy/{player_id}/{property_id}")
async def buy_property(player_id: str, property_id: str):
    player = await db.jogadores.find_one({"_id": player_id})
    property_ = await db.propriedades.find_one({"_id": property_id})
    
    if not player or not property_:
        raise HTTPException(status_code=404, detail="Player or property not found")
    
    if "owner" in property_ and property_["owner"]:
        raise HTTPException(status_code=400, detail="Property already owned")
    
    if player["saldo"] < property_["preco"]:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    await db.jogadores.update_one({"_id": player_id}, {"$inc": {"saldo": -property_["preco"]}})
    await db.propriedades.update_one({"_id": property_id}, {"$set": {"owner": player_id}})
    return {"message": "Property purchased", "player_id": player_id, "property_id": property_id}

# Pagar aluguel
@app.post("/pay_rent/{player_id}/{property_id}")
async def pay_rent(player_id: str, property_id: str):
    player = await db.jogadores.find_one({"_id": player_id})
    property_ = await db.propriedades.find_one({"_id": property_id})
    
    if not player or not property_:
        raise HTTPException(status_code=404, detail="Player or property not found")
    
    if "owner" not in property_ or not property_["owner"] or property_["owner"] == player_id:
        raise HTTPException(status_code=400, detail="No rent to pay")
    
    rent = property_["aluguel"]
    owner = await db.jogadores.find_one({"_id": property_["owner"]})
    
    if player["saldo"] < rent:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    await db.jogadores.update_one({"_id": player_id}, {"$inc": {"saldo": -rent}})
    await db.jogadores.update_one({"_id": owner["_id"]}, {"$inc": {"saldo": rent}})
    return {"message": "Rent paid", "payer": player_id, "owner": owner["_id"], "amount": rent}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
