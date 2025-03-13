import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "monopoly"

def conectar_banco():
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]

def carregar_json(arquivo):
    """Lê um arquivo JSON e retorna os dados."""
    with open(arquivo, "r", encoding="utf-8") as f:
        return json.load(f)

def inserir_dados():
    db = conectar_banco()
    
    # Carregar dados dos arquivos JSON
    board_data = carregar_json("board_data.json")
    cartas_data = carregar_json("cartas.json")
    
    # Inserir jogadores
    jogadores = db.jogadores
    if jogadores.count_documents({}) == 0:
        jogadores.insert_many(board_data["jogadores"])
        print("Jogadores inseridos com sucesso!")
    else:
        print("Jogadores já cadastrados.")
    
    # Inserir propriedades
    propriedades = db.propriedades
    if propriedades.count_documents({}) == 0:
        propriedades.insert_many(board_data["propriedades"])
        print("Propriedades inseridas com sucesso!")
    else:
        print("Propriedades já cadastradas.")
    
    # Inserir cartas
    cartas = db.cartas
    if cartas.count_documents({}) == 0:
        cartas.insert_many(cartas_data)
        print("Cartas inseridas com sucesso!")
    else:
        print("Cartas já cadastradas.")
    
    # Criar partida inicial
    partidas = db.partidas
    if partidas.count_documents({}) == 0:
        partidas.insert_one({
            "_id": "partida_1",
            "jogadores": [j["_id"] for j in board_data["jogadores"]],
            "turno_atual": board_data["jogadores"][0]["_id"],
            "status": "em_andamento",
            "vencedor": None
        })
        print("Partida inicial criada!")
    else:
        print("Partida já existente.")

if __name__ == "__main__":
    inserir_dados()
