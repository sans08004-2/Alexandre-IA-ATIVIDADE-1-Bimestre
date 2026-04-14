Neural Pong Adaptativo
Este projeto implementa uma versão experimental do jogo Pong, desenvolvida em Python, que utiliza um modelo de linguagem de grande escala (LLM) para gerenciar a lógica do oponente. O sistema utiliza a API do Groq para permitir que a IA analise suas falhas e adapte sua estratégia em tempo real.

Arquitetura e Funcionamento
O motor do jogo integra o loop de física tradicional com chamadas de inferência assíncronas. O comportamento da IA não é baseado em scripts fixos, mas em decisões geradas pelo modelo Llama-3.1-8b-instant.

Ciclo de Feedback da IA
Gatilho de Evento: Ao sofrer um ponto, o estado do jogo é capturado.

Processamento de Contexto: Dados como placar e velocidade são enviados via JSON para o modelo.

Resposta Adaptativa: O modelo retorna uma nova estratégia e um incremento de performance.

Aplicação: O jogo atualiza o multiplicador de velocidade e a precisão do oponente imediatamente.

Requisitos Técnicos
Linguagem: Python 3.8+

Bibliotecas: * pygame: Interface gráfica e física.

groq: Integração com o motor de inferência.

Infraestrutura: Chave de API válida do Groq Cloud.

Instalação e Execução
Instale as dependências necessárias:

Bash
pip install pygame groq

Inicie o ambiente de teste:

Bash
python main.py
