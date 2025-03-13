{
  "jogadores": [
    {
      "_id": "player_1",
      "nome": "Lucas Verde",
      "saldo": 1500,
      "posicao": 0,
      "propriedades": [
        {"_id": "avenida_atlantica", "casas": 2, "hotel": false},
        {"_id": "copacabana", "casas": 1, "hotel": false}
      ],
      "preso": false,
      "cartoes_sair_da_prisao": 1,
      "endereco": "Rua das Flores, 123"
    }
  ],
  "partidas": [
    {
      "_id": "partida_1",
      "jogadores": ["player_1", "player_2", "player_3", "player_4"],
      "turno_atual": "player_2",
      "status": "em_andamento",
      "vencedor": null
    }
  ],
  "cartas": [
    {
      "_id": "sorte_1",
      "tipo": "sorte",
      "descricao": "Avance para o ponto de partida e receba R$200",
      "acao": {"tipo": "mover", "destino": 0, "bonus": 200}
    }
  ],
  "historico_jogadores": [
    {
      "player_id": "player_1",
      "actions": [
        {"action": "comprar", "details": {"propriedade": "copacabana", "valor": 350}},
        {"action": "pagar", "details": {"destinatario": "player_3", "valor": 50}}
      ]
    }
  ],
  "aggregations": {
    "buscar_status_jogo": [
      {"$match": {"_id": "partida_1"}},
      {"$project": {"jogadores": 1, "turno_atual": 1, "status": 1}}
    ],
    "historico_acoes_jogador": [
      {"$match": {"player_id": "player_1"}},
      {"$unwind": "$actions"},
      {"$sort": {"actions.timestamp": -1}},
      {"$limit": 10}
    ],
    "saldo_atualizado": [
      {"$match": {"_id": "player_1"}},
      {"$project": {"nome": 1, "saldo": 1}}
    ],
    "listar_propriedades_jogador": [
      {"$match": {"_id": "player_1"}},
      {"$lookup": {
        "from": "propriedades",
        "localField": "propriedades._id",
        "foreignField": "_id",
        "as": "detalhes_propriedades"
      }},
      {"$project": {"nome": 1, "detalhes_propriedades": 1}}
    ]
  }
}
