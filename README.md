Este projeto de Monopoly é uma solução completa que integra conceitos de NoSQL e desenvolvimento de APIs para simular e gerenciar partidas de um jogo de tabuleiro clássico. Ele foi desenvolvido como trabalho da disciplina Banco de Dados NoSQL do curso de Gestão da Informação da UFU.

# Principais Aspectos do Projeto
# Armazenamento Flexível com MongoDB:
Utiliza o MongoDB para armazenar dados de forma flexível, abrangendo informações dos jogadores, propriedades do tabuleiro, cartas de sorte/reves e o histórico de cada partida.

# API com FastAPI e PyMongo:
Uma API foi criada usando FastAPI para expor endpoints que permitem a criação, atualização e consulta de partidas, além do registro de ações e acompanhamento do histórico dos jogadores. O PyMongo é empregado para interagir com o banco de dados MongoDB.

# Gerenciamento Automatizado das Partidas:
O sistema gerencia o andamento das partidas, controlando o progresso dos jogadores, realizando transações automáticas (como compra de propriedades e pagamento de aluguéis) e registrando cada ação no histórico do jogo.

# Registro e Acompanhamento do Histórico:
Todas as ações dos jogadores, como alterações de saldo, aquisição de propriedades e eventos do jogo, são registradas para permitir um acompanhamento detalhado da evolução de cada partida.

Em resumo, o projeto representa uma aplicação integrada que une a prática de banco de dados NoSQL com o desenvolvimento de uma API em Python, proporcionando uma base para o gerenciamento completo e automatizado de partidas de Monopoly.
