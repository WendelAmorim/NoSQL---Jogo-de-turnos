from fastapi import FastAPI, HTTPException, Body
from pymongo import MongoClient
from pydantic import BaseModel
from bson.objectid import ObjectId
from typing import List, Optional
import os


MONGO_URI = "mongodb+srv://wendelamorimm:FWSIuAL0DmOF30At@cluster0.poyx2.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(MONGO_URI)
db = client["monopoly"]

app = FastAPI(title="API Monopoly", description="API para gerenciar partidas e histórico de jogadores")

# Função auxiliar para converter _id do MongoDB em string
def convert_id(doc):
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc

# Modelos Pydantic para validação dos dados

class Game(BaseModel):
    players: List[str]
    turn: Optional[str] = None
    status: Optional[str] = "in_progress"  # Exemplos: "in_progress", "finished"
    history: Optional[List[dict]] = []      # Histórico de ações na partida

class Action(BaseModel):
    action: str
    details: Optional[dict] = {}

class PlayerHistory(BaseModel):
    player_id: str
    balance: float
    properties: List[str] = []
    actions: List[dict] = []

# ----- Endpoints para Gerenciar Partidas -----

# Cria uma nova partida
@app.post("/games/", response_model=dict)
def create_game(game: Game):
    game_dict = game.dict()
    result = db.games.insert_one(game_dict)
    game_dict["_id"] = result.inserted_id
    return convert_id(game_dict)

# Consulta os dados de uma partida específica
@app.get("/games/{game_id}", response_model=dict)
def get_game(game_id: str):
    game = db.games.find_one({"_id": ObjectId(game_id)})
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return convert_id(game)

# Atualiza dados da partida (ex: progresso dos jogadores, turno, status)
@app.patch("/games/{game_id}", response_model=dict)
def update_game(game_id: str, update: dict = Body(...)):
    result = db.games.update_one({"_id": ObjectId(game_id)}, {"$set": update})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Game not found")
    game = db.games.find_one({"_id": ObjectId(game_id)})
    return convert_id(game)

# Adiciona uma ação ao histórico da partida
@app.post("/games/{game_id}/actions", response_model=dict)
def add_game_action(game_id: str, action: Action):
    result = db.games.update_one(
        {"_id": ObjectId(game_id)},
        {"$push": {"history": action.dict()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Game not found")
    game = db.games.find_one({"_id": ObjectId(game_id)})
    return convert_id(game)

# ----- Endpoints para Gerenciar o Histórico dos Jogadores -----

# Consulta o histórico de um jogador
@app.get("/players/{player_id}/history", response_model=dict)
def get_player_history(player_id: str):
    history = db.player_history.find_one({"player_id": player_id})
    if not history:
        raise HTTPException(status_code=404, detail="Player history not found")
    return convert_id(history)

# Registra ou atualiza uma ação no histórico do jogador
@app.post("/players/{player_id}/history", response_model=dict)
def update_player_history(player_id: str, action: Action):
    # Atualiza (ou cria se não existir) o histórico do jogador, adicionando a ação
    result = db.player_history.update_one(
        {"player_id": player_id},
        {"$push": {"actions": action.dict()}},
        upsert=True
    )
    history = db.player_history.find_one({"player_id": player_id})
    return convert_id(history)

# Executa a aplicação se o arquivo for executado diretamente
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
