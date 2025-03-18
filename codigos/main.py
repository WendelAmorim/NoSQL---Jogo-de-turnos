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

# Aggregation Pipeline para calcular o total de saldo dos jogadores
async def total_balance():
    pipeline = [
        {"$group": {"_id": None, "total": {"$sum": "$saldo"}}}
    ]
    result = await db.jogadores.aggregate(pipeline).to_list(length=None)
    return result[0]["total"] if result else 0

# Aggregation Pipeline para listar propriedades e seus donos
async def properties_with_owners():
    pipeline = [
        {"$lookup": {
            "from": "jogadores",
            "localField": "owner",
            "foreignField": "_id",
            "as": "proprietario"
        }},
        {"$unwind": {"path": "$proprietario", "preserveNullAndEmptyArrays": True}}
    ]
    return await db.propriedades.aggregate(pipeline).to_list(length=None)

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

# Exibir o total de saldo de todos os jogadores
@app.get("/total_balance")
async def get_total_balance():
    total = await total_balance()
    return {"total_balance": total}

# Inicializar índices eficientes
@app.on_event("startup")
async def startup_event():
    # Criação de índices para otimização
    await db.jogadores.create_index([("nome", 1)], unique=True)  # Índice único para nome dos jogadores
    await db.propriedades.create_index([("owner", 1)])  # Índice no campo "owner" para otimizar o lookup

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
