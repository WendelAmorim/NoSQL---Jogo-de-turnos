import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()  # Carrega as variáveis de ambiente do .env

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

class AdvancedGraphAnalysis:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def run_pagerank(self):
        """
        Executa o algoritmo PageRank no conjunto dos nós do tipo Propriedade,
        utilizando a relação LOCALIZADA_EM, que conecta cada propriedade à posição no tabuleiro.
        O PageRank é um algoritmo espectral que serve para rankear a importância dos nós.
        """
        with self.driver.session() as session:
            result = session.run(
                """
                CALL gds.pageRank.stream({
                    nodeProjection: 'Propriedade',
                    relationshipProjection: {
                        LOCALIZADA_EM: {
                            type: 'LOCALIZADA_EM',
                            orientation: 'UNDIRECTED'
                        }
                    },
                    maxIterations: 20,
                    dampingFactor: 0.85
                })
                YIELD nodeId, score
                RETURN gds.util.asNode(nodeId).nome AS nome, score
                ORDER BY score DESC
                """
            )
            print("PageRank dos nós (Propriedades):")
            for record in result:
                print(f"{record['nome']}: {record['score']:.4f}")
    
    def run_betweenness(self):
        """
        Executa o algoritmo de betweenness centrality nos nós do tipo Propriedade.
        Essa métrica identifica os nós que atuam como "pontes" na comunicação do grafo,
        podendo representar pontos estratégicos no tabuleiro.
        """
        with self.driver.session() as session:
            result = session.run(
                """
                CALL gds.betweenness.stream({
                    nodeProjection: 'Propriedade',
                    relationshipProjection: {
                        LOCALIZADA_EM: {
                            type: 'LOCALIZADA_EM',
                            orientation: 'UNDIRECTED'
                        }
                    }
                })
                YIELD nodeId, score
                RETURN gds.util.asNode(nodeId).nome AS nome, score
                ORDER BY score DESC
                """
            )
            print("Betweenness Centrality dos nós (Propriedades):")
            for record in result:
                print(f"{record['nome']}: {record['score']:.4f}")

if __name__ == '__main__':
    analysis = AdvancedGraphAnalysis(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    analysis.run_pagerank()
    print("\n")
    analysis.run_betweenness()
    analysis.close()
