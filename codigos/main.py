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

# Rolar dados
@app.get("/roll/{player_id}")
async def roll_dice(player_id: str):
    roll = random.randint(1, 6) + random.randint(1, 6)
    player = await db.jogadores.find_one({"_id": player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    new_position = (player["posicao"] + roll) % 40  # Tabuleiro de 40 casas
    await db.jogadores.update_one({"_id": player_id}, {"$set": {"posicao": new_position}})
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
    
    rent = property_["aluguel"]["base"]  # Pode ser expandido para calcular com casas e hotéis
    owner = await db.jogadores.find_one({"_id": property_["owner"]})
    
    if player["saldo"] < rent:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    await db.jogadores.update_one({"_id": player_id}, {"$inc": {"saldo": -rent}})
    await db.jogadores.update_one({"_id": owner["_id"]}, {"$inc": {"saldo": rent}})
    return {"message": "Rent paid", "payer": player_id, "owner": owner["_id"], "amount": rent}

# Sair da prisão
@app.post("/jail/{player_id}")
async def leave_jail(player_id: str, pay: bool = False):
    player = await db.jogadores.find_one({"_id": player_id})
    
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    if not player.get("preso", False):
        return {"message": "Player is not in jail"}
    
    if pay:
        if player["saldo"] < 50:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        await db.jogadores.update_one({"_id": player_id}, {"$inc": {"saldo": -50}, "$set": {"preso": False}})
        return {"message": "Player paid fine and left jail"}
    
    return {"message": "Player must roll doubles or use 'Get Out of Jail Free' card"}

# Verificar falência e eliminar jogador
@app.post("/check_bankruptcy/{player_id}")
async def check_bankruptcy(player_id: str):
    player = await db.jogadores.find_one({"_id": player_id})
    
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    if player["saldo"] >= 0:
        return {"message": "Player is not bankrupt"}
    
    await db.jogadores.delete_one({"_id": player_id})
    return {"message": "Player removed due to bankruptcy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
