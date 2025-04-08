import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()  # Carrega variáveis do arquivo .env

class Neo4jGraph:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self._driver.close()
    
    def registrar_jogador(self, nome, saldo):
        """Cria ou atualiza um nó de Jogador com o nome e saldo fornecidos."""
        with self._driver.session() as session:
            session.write_transaction(self._registrar_jogador_tx, nome, saldo)
    
    @staticmethod
    def _registrar_jogador_tx(tx, nome, saldo):
        query = (
            "MERGE (j:Jogador {nome: $nome}) "
            "SET j.saldo = $saldo "
            "RETURN j"
        )
        tx.run(query, nome=nome, saldo=saldo)
    
    def registrar_posse(self, jogador_nome, propriedade_nome):
        """Cria a relação de posse entre um Jogador e uma Propriedade."""
        with self._driver.session() as session:
            session.write_transaction(self._registrar_posse_tx, jogador_nome, propriedade_nome)
    
    @staticmethod
    def _registrar_posse_tx(tx, jogador_nome, propriedade_nome):
        query = (
            "MATCH (j:Jogador {nome: $jogador_nome}) "
            "MATCH (p:Propriedade {nome: $propriedade_nome}) "
            "MERGE (j)-[:POSSESS]->(p) "
            "RETURN j, p"
        )
        tx.run(query, jogador_nome=jogador_nome, propriedade_nome=propriedade_nome)
    
    def criar_propriedade_com_posicao(self, propriedade_nome, cor, preco, posicao_id, posicao_nome, posicao_tipo):
        """Cria (ou atualiza) um nó de Propriedade e associa-o a um nó de Posicao."""
        with self._driver.session() as session:
            session.write_transaction(
                self._criar_propriedade_com_posicao_tx,
                propriedade_nome, cor, preco, posicao_id, posicao_nome, posicao_tipo
            )
    
    @staticmethod
    def _criar_propriedade_com_posicao_tx(tx, propriedade_nome, cor, preco, posicao_id, posicao_nome, posicao_tipo):
        query = (
            "MERGE (p:Propriedade {nome: $propriedade_nome}) "
            "SET p.cor = $cor, p.preco = $preco "
            "WITH p "
            "MERGE (pos:Posicao {id: $posicao_id}) "
            "SET pos.nome = $posicao_nome, pos.tipo = $posicao_tipo "
            "MERGE (p)-[:LOCALIZADA_EM]->(pos) "
            "RETURN p, pos"
        )
        tx.run(query, propriedade_nome=propriedade_nome, cor=cor, preco=preco,
               posicao_id=posicao_id, posicao_nome=posicao_nome, posicao_tipo=posicao_tipo)

# Carrega as credenciais do .env de forma segura
neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
neo4j_user = os.getenv("NEO4J_USER", "neo4j")
neo4j_password = os.getenv("NEO4J_PASSWORD")
neo4j_graph = Neo4jGraph(neo4j_uri, neo4j_user, neo4j_password)
