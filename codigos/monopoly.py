import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# String de conexão do MongoDB Atlas armazenada como variável de ambiente
MONGO_URI = os.getenv("MONGO_URI")

def conectar_banco():
    client = MongoClient(MONGO_URI)
    return client["monopoly"]  # Nome do banco de dados

def carregar_arquivos():
    with open("board_data.json", "r", encoding="utf-8") as f:
        board_data = json.load(f)
    with open("cartas.json", "r", encoding="utf-8") as f:
        cartas = json.load(f)
    return board_data, cartas

def inserir_dados():
    db = conectar_banco()
    board_data, cartas = carregar_arquivos()
    
    # Inserir jogadores (4 usuários) com campo "endereco" e propriedades detalhadas
    jogadores = db.jogadores
    jogadores.insert_many([
        {
            "_id": "player_1",
            "nome": "Lucas Verde",
            "saldo": 1500,
            "posicao": 0,
            "propriedades": [],
            "preso": False,
            "cartoes_sair_da_prisao": 1,
            "endereco": "Rua das Flores, 123"
        },
        {
            "_id": "player_2",
            "nome": "Ana Souza",
            "saldo": 1500,
            "posicao": 0,
            "propriedades": [],
            "preso": False,
            "cartoes_sair_da_prisao": 0,
            "endereco": "Av. Paulista, 456"
        },
        {
            "_id": "player_3",
            "nome": "Carlos Lima",
            "saldo": 1500,
            "posicao": 0,
            "propriedades": [],
            "preso": False,
            "cartoes_sair_da_prisao": 0,
            "endereco": "Rua do Sol, 789"
        },
        {
            "_id": "player_4",
            "nome": "Mariana Costa",
            "saldo": 1500,
            "posicao": 0,
            "propriedades": [],
            "preso": False,
            "cartoes_sair_da_prisao": 0,
            "endereco": "Av. Brasil, 101"
        }
    ])
    
    # Inserir cartas de sorte/revés
    db.cartas.insert_many(cartas)
    
    print("Dados inseridos com sucesso!")

if __name__ == "__main__":
    inserir_dados()
