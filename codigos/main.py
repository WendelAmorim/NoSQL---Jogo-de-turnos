import os
import redis
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
from neo4j_graph import neo4j_graph  # Importa funções para interação com o Neo4j

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração segura do MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = "monopoly"

# Conectar ao MongoDB de forma assíncrona
client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]

# Conectar ao Redis com namespace específico
redis_client = redis.Redis(
    host='localhost', port=6379, db=0, decode_responses=True, key_prefix='monopoly:'
)

# Criar API FastAPI
app = FastAPI(title="API Monopoly", description="API para gerenciamento de partidas e jogadores")

# Modelos de Dados
class Jogador(BaseModel):
    nome: str
    saldo: int

class Propriedade(BaseModel):
    nome: str
    preco: int
    aluguel: int
    cor: str

# 1. Cache de jogadores no Redis (HASH)
async def cache_jogador(jogador_id: str, jogador: Jogador):
    redis_client.hset(f"jogador:{jogador_id}", mapping=jogador.dict())

async def get_jogador_cache(jogador_id: str):
    dados = redis_client.hgetall(f"jogador:{jogador_id}")
    if dados:
        return Jogador(**dados)
    return None

@app.post("/jogador/")
async def criar_jogador(jogador: Jogador):
    jogador_id = jogador.nome.lower().replace(" ", "_")
    # Salvar no MongoDB
    await db.jogadores.insert_one(jogador.dict())
    # Salvar no Redis (cache)
    await cache_jogador(jogador_id, jogador)
    # Registrar o jogador no Neo4j
    neo4j_graph.registrar_jogador(jogador.nome, jogador.saldo)
    return {"mensagem": "Jogador criado com sucesso!"}

@app.get("/jogador/{jogador_id}")
async def obter_jogador(jogador_id: str):
    jogador = await get_jogador_cache(jogador_id)
    if jogador:
        return {"jogador": jogador}
    jogador = await db.jogadores.find_one({"nome": jogador_id})
    if jogador:
        await cache_jogador(jogador_id, Jogador(**jogador))
        return {"jogador": jogador}
    return {"erro": "Jogador não encontrado"}

# 2. Histórico de compras de propriedades (LIST) e contagem de compradores únicos (HyperLogLog)
@app.post("/comprar/{jogador_id}/{propriedade}")
async def comprar_propriedade(jogador_id: str, propriedade: str):
    redis_client.lpush(f"compras:{jogador_id}", propriedade)
    redis_client.pfadd("compradores_unicos", jogador_id)  # Registra o jogador em HyperLogLog
    return {"mensagem": f"{propriedade} comprada por {jogador_id}"}

@app.get("/historico-compras/{jogador_id}")
async def historico_compras(jogador_id: str):
    compras = redis_client.lrange(f"compras:{jogador_id}", 0, -1)
    return {"compras": compras}

@app.get("/total-jogadores-unicos")
async def total_jogadores_unicos():
    count = redis_client.pfcount("compradores_unicos")
    return {"total_jogadores_unicos": count}

# 3. Gerenciamento das propriedades do jogador (SET) e uso de Bloom Filter
@app.post("/adicionar_propriedade/{jogador_id}/{propriedade}")
async def adicionar_propriedade(jogador_id: str, propriedade: str):
    redis_client.sadd(f"propriedades:{jogador_id}", propriedade)
    redis_client.bfadd("propriedades_existem", propriedade)
    # Registrar a posse da propriedade no Neo4j
    neo4j_graph.registrar_posse(jogador_id, propriedade)
    return {"mensagem": f"Propriedade {propriedade} adicionada ao jogador {jogador_id}"}

@app.get("/propriedades/{jogador_id}")
async def listar_propriedades(jogador_id: str):
    propriedades = redis_client.smembers(f"propriedades:{jogador_id}")
    return {"propriedades": list(propriedades)}

@app.get("/tem_conjunto/{jogador_id}/{cor}")
async def verificar_conjunto(jogador_id: str, cor: str):
    propriedades = list(redis_client.smembers(f"propriedades:{jogador_id}"))
    todas_propriedades = await db.propriedades.find({"cor": cor}).to_list(None)
    nomes_propriedades = [p["nome"] for p in todas_propriedades]
    possui_todas = all(prop in propriedades for prop in nomes_propriedades)
    return {"tem_conjunto": possui_todas}

@app.get("/propriedade_existe/{propriedade}")
async def propriedade_existe(propriedade: str):
    existe = redis_client.bfexists("propriedades_existem", propriedade)
    return {"existe": bool(existe)}

# 4. Gerenciamento de turnos (STRING)
@app.post("/set_turno/{jogador_id}")
async def set_turno(jogador_id: str):
    redis_client.set("turno_atual", jogador_id)
    return {"mensagem": f"Turno do jogador {jogador_id}"}

@app.get("/turno_atual")
async def get_turno():
    turno = redis_client.get("turno_atual")
    return {"turno_atual": turno}
