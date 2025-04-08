import json
from neo4j_graph import neo4j_graph

def populate_board():
    # Carrega os dados do arquivo JSON com os endereços/propriedades
    with open("board_data.json", "r", encoding="utf-8") as f:
        board_data = json.load(f)
    
    for item in board_data:
        # Cria o nó de Posicao para cada registro
        posicao_id = item.get("_id")
        nome = item.get("nome")
        tipo = item.get("tipo")
        endereco = item.get("endereco")
        
        # utiliza _id como identificador único
        # Atualize o query conforme os atributos do json
        with neo4j_graph._driver.session() as session:
            session.write_transaction(
                lambda tx, posicao_id=posicao_id, nome=nome, tipo=tipo, endereco=endereco: 
                tx.run(
                    "MERGE (p:Posicao {id: $id}) "
                    "SET p.nome = $nome, p.tipo = $tipo, p.endereco = $endereco",
                    id=posicao_id, nome=nome, tipo=tipo, endereco=endereco
                )
            )
        
        if tipo == "propriedade":
            preco = item.get("preco", 0)
            aluguel = item.get("aluguel", 0)
            cor = item.get("cor", None)
            with neo4j_graph._driver.session() as session:
                session.write_transaction(
                    lambda tx, nome=nome, cor=cor, preco=preco, posicao_id=posicao_id, tipo=tipo: 
                    tx.run(
                        "MERGE (prop:Propriedade {nome: $nome}) "
                        "SET prop.cor = $cor, prop.preco = $preco "
                        "WITH prop "
                        "MATCH (p:Posicao {id: $posicao_id}) "
                        "MERGE (prop)-[:LOCALIZADA_EM]->(p)",
                        nome=nome, cor=cor, preco=preco, posicao_id=posicao_id
                    )
                )

if __name__ == '__main__':
    populate_board()
    neo4j_graph.close()
    print("População do grafo concluída!")
