import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# String de conexão do MongoDB Atlas armazenada como variável de ambiente
MONGO_URI = os.getenv("MONGO_URI")

def conectar_banco():
    client = MongoClient(MONGO_URI)
    return client["monopoly"]  # Nome do banco de dados

def inserir_dados():
    db = conectar_banco()
    
    # Inserir jogadores (4 usuários) com campo "endereco"
    jogadores = db.jogadores
    jogadores.insert_many([
        {
            "_id": "player_1",
            "nome": "Lucas Verde",
            "saldo": 1500,
            "posicao": 0,
            "propriedades": ["avenida_atlantica", "copacabana"],
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
    
    # Inserir propriedades do tabuleiro com campo "endereco"
    tabuleiro = db.tabuleiro
    tabuleiro.insert_many([
        {
            "_id": "avenida_atlantica",
            "tipo": "propriedade",
            "nome": "Avenida Atlântica",
            "cor": "azul",
            "preco": 400,
            "aluguel": {
                "base": 50,
                "com_1_casa": 200,
                "com_2_casas": 600,
                "com_3_casas": 1400,
                "com_4_casas": 1700,
                "hotel": 2000
            },
            "dono": "player_1",
            "casas": 2,
            "hotel": False,
            "endereco": "Avenida Atlântica, 1000"
        },
        {
            "_id": "copacabana",
            "tipo": "propriedade",
            "nome": "Copacabana",
            "cor": "azul",
            "preco": 350,
            "aluguel": {
                "base": 35,
                "com_1_casa": 175,
                "com_2_casas": 500,
                "com_3_casas": 1100,
                "com_4_casas": 1300,
                "hotel": 1500
            },
            "dono": "player_1",
            "casas": 1,
            "hotel": False,
            "endereco": "Rua Copacabana, 2000"
        }
    ])
    
    # Inserir cartas de sorte/reves
    cartas = db.cartas
    cartas.insert_many([
        {
            "_id": "sorte_1",
            "tipo": "sorte",
            "descricao": "Avance até o ponto de partida e receba R$200",
            "acao": {
                "tipo": "mover",
                "destino": 0,
                "bonus": 200
            }
        },
        {
            "_id": "sorte_2",
            "tipo": "sorte",
            "descricao": "Pague R$100 de taxa",
            "acao": {
                "tipo": "pagar",
                "valor": 100
            }
        }
    ])
    
    # Criar partida com os 4 jogadores
    partidas = db.partidas
    partidas.insert_one({
        "_id": "partida_1",
        "jogadores": ["player_1", "player_2", "player_3", "player_4"],
        "turno_atual": "player_2",
        "status": "em_andamento",
        "vencedor": None
    })
    
    print("Dados inseridos com sucesso!")

if __name__ == "__main__":
    inserir_dados()
