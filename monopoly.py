{
  "_id": "player_1",
  "nome": "Lucas Verde",
  "saldo": 1500,
  "posicao": 0,
  "propriedades": [
    {
      "_id": "avenida_atlantica",
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
      "casas": 2,
      "hotel": false
    },
    {
      "_id": "copacabana",
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
      "casas": 0,
      "hotel": false
    }
  ],
  "preso": false,
  "cartoes_sair_da_prisao": 1
}

{
  "_id": "sorte_1",
  "tipo": "sorte",
  "descricao": "Avance até o ponto de partida e receba R$200",
  "acao": {
    "tipo": "mover",
    "destino": 0,
    "bonus": 200
  }
}

{
  "_id": "partida_1",
  "jogadores": ["player_1", "player_2", "player_3", "player_4"],
  "turno_atual": "player_2",
  "status": "em_andamento",
  "vencedor": null
}
