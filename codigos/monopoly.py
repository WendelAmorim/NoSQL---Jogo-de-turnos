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

def carregar_dados_arquivos():
    with open("board_data.json", "r", encoding="utf-8") as f:
        board_data = json.load(f)
    with open("cartas.json", "r", encoding="utf-8") as f:
        cartas = json.load(f)
    return board_data, cartas

def inserir_dados():
    db = conectar_banco()
    board_data, cartas = carregar_dados_arquivos()
    
    # Inserir jogadores com endereços, propriedades e características
    jogadores = db.jogadores
    jogadores.insert_many([
        {
            "_id": "player_1", "nome": "Lucas Verde", "saldo": 1500, "posicao": 0, "preso": False,
            "cartoes_sair_da_prisao": 1, "endereco": "Rua das Flores, 123",
            "propriedades": [
                {"_id": "avenida_atlantica", "nome": "Avenida Atlântica", "cor": "azul", "preco": 400, 
                 "aluguel": {"base": 50, "com_1_casa": 200, "com_2_casas": 600, "com_3_casas": 1400, "com_4_casas": 1700, "hotel": 2000},
                 "casas": 2, "hotel": False},
                {"_id": "copacabana", "nome": "Copacabana", "cor": "azul", "preco": 350, 
                 "aluguel": {"base": 35, "com_1_casa": 175, "com_2_casas": 500, "com_3_casas": 1100, "com_4_casas": 1300, "hotel": 1500},
                 "casas": 1, "hotel": False}
            ]
        },
        {
            "_id": "player_2", "nome": "Ana Souza", "saldo": 1500, "posicao": 0, "preso": False,
            "cartoes_sair_da_prisao": 0, "endereco": "Av. Paulista, 456",
            "propriedades": []
        },
        {
            "_id": "player_3", "nome": "Carlos Lima", "saldo": 1500, "posicao": 0, "preso": False,
            "cartoes_sair_da_prisao": 0, "endereco": "Rua do Sol, 789",
            "propriedades": []
        },
        {
            "_id": "player_4", "nome": "Mariana Costa", "saldo": 1500, "posicao": 0, "preso": False,
            "cartoes_sair_da_prisao": 0, "endereco": "Av. Brasil, 101",
            "propriedades": []
        }
    ])
    
    # Inserir cartas
    db.cartas.insert_many(cartas)
    
    print("Jogadores e cartas inseridos com sucesso!")

if __name__ == "__main__":
    inserir_dados()
