import os
from fastapi import FastAPI, HTTPException, Body, Depends
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

app = FastAPI(title="API Monopoly", description="API segura para gerenciamento de partidas e jogadores")

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
    players: List[str] = Field(..., min_items=2, max_items=6)  # Limite de jogadores
    turn: Optional[str] = None
    status: Optional[str] = Field("in_progress", regex="^(in_progress|finished)$")
    history: Optional[List[Action]] = []

class PlayerHistory(BaseModel):
    player_id: str = Field(..., min_length=3)
    balance: float = Field(..., ge=0)
    properties: List[str] = []
    actions: List[Action] = []

# ----- Endpoints -----

@app.post("/games/", response_model=dict)
async def create_game(game: Game):
    game_dict = game.dict()
    result = await db.games.insert_one(game_dict)
    game_dict["_id"] = result.inserted_id
    return await convert_id(game_dict)

@app.get("/games/{game_id}", response_model=dict)
async def get_game(game_id: str):
    game = await db.games.find_one({"_id": ObjectId(game_id)})
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return await convert_id(game)

@app.patch("/games/{game_id}", response_model=dict)
async def update_game(game_id: str, update: Dict = Body(...)):
    allowed_fields = {"players", "turn", "status", "history"}
    update = {k: v for k, v in update.items() if k in allowed_fields}  # Evita injeção
    result = await db.games.update_one({"_id": ObjectId(game_id)}, {"$set": update})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Game not found")
    return await get_game(game_id)

@app.post("/games/{game_id}/actions", response_model=dict)
async def add_game_action(game_id: str, action: Action):
    result = await db.games.update_one({"_id": ObjectId(game_id)}, {"$push": {"history": action.dict()}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Game not found")
    return await get_game(game_id)

@app.get("/players/{player_id}/history", response_model=dict)
async def get_player_history(player_id: str):
    history = await db.player_history.find_one({"player_id": player_id})
    if not history:
        raise HTTPException(status_code=404, detail="Player history not found")
    return await convert_id(history)

@app.post("/players/{player_id}/history", response_model=dict)
async def update_player_history(player_id: str, action: Action):
    result = await db.player_history.update_one(
        {"player_id": player_id},
        {"$push": {"actions": action.dict()}},
        upsert=True
    )
    return await get_player_history(player_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
