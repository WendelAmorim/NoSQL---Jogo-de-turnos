# MONOPOLY EM NOSQL

Este projeto de Monopoly é uma solução completa que integra conceitos de NoSQL e desenvolvimento de APIs para simular e gerenciar partidas do clássico jogo de tabuleiro. Ele foi desenvolvido como trabalho da disciplina Banco de Dados NoSQL do curso de Gestão da Informação da UFU.

# Principais Aspectos do Projeto
**Armazenamento Flexível com MongoDB:**
O MongoDB é utilizado para armazenar dados de forma persistente e estruturada, incluindo:

- Informações dos jogadores

- Propriedades do tabuleiro

- Cartas de Sorte/Reves

- Histórico completo das partidas

**Otimização com Redis**
O Redis foi integrado para melhorar o desempenho e a eficiência do sistema, sendo usado para:

- Cache de jogadores → evita consultas repetitivas ao MongoDB

- Histórico de compras com listas (LIST)

- Gerenciamento de propriedades dos jogadores com conjuntos (SET)

- Controle de turnos utilizando chave-valor (SET/GET)

**API com FastAPI, MongoDB e Redis**
A API foi desenvolvida com FastAPI, permitindo a criação, atualização e consulta de partidas.

- O MongoDB é acessado via Motor (AsyncIO) para operações assíncronas eficientes.

- O Redis acelera operações frequentes, reduzindo a carga no banco de dados principal.

**Gerenciamento Inteligente das Partidas**
O sistema automatiza o fluxo do jogo, incluindo:

- Controle de turnos dos jogadores

- Registro automático de transações (compra de propriedades, pagamento de aluguéis, etc.)

- Atualização em tempo real do status do jogo

**Registro e Acompanhamento do Histórico**

Todas as ações dos jogadores são registradas, permitindo:

- Análise detalhada da evolução de cada partida

- Acesso rápido ao histórico de compras e movimentações no tabuleiro

Este projeto representa uma solução integrada que combina bancos de dados NoSQL com desenvolvimento de APIs escaláveis, proporcionando um gerenciamento rápido, eficiente e automatizado das partidas de Monopoly.
