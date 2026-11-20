# Projeto de Complexidade: 2-SAT e 3-SAT

**Disciplina:** Teoria da Computação  
**Professor:** Daniel Bezerra  
**Equipe:** Breno Pereira, Davi de Lucena, Davila Peixoto, João Carlos Vasconcelos, João Pedro Pessôa

Este repositório contém as implementações, testes e scripts de benchmark para a análise de complexidade de tempo do par de problemas **2-SAT (em P)** e **3-SAT (NP-completo)**.

## Estrutura do Repositório

O projeto está organizado da seguinte forma para garantir modularidade e reprodutibilidade:

- algoritmos/: Contém os códigos-fonte das soluções em C e Python.
  - Implementação 2-SAT
  - Implementação 3-SAT
  - Parser CNF
- dados/: Conjunto de instâncias .cnf geradas para os testes, cobrindo diferentes tamanhos de N para o melhor e pior caso.
  - gabarito.csv: Metadados e respostas esperadas (SAT/UNSAT) das instâncias
- scripts/: Ferramentas de automação.
  - benchmark.py: Orquestra a execução de todos os algoritmos, aplica o limite de tempo, realiza repetições e exporta os tempos.
- tests/: 
  - test.py: Bateria de testes automatizados para atestar a corretude cruzada das 4 implementações.
- Dockerfile / Makefile: Arquivos para automação do ambiente e da compilação.
- requirements.txt: Dependências Python necessárias para os scripts.

## Pré-requisitos e Ambiente

Para reproduzir este projeto, pode utilizar o ambiente Docker fornecido ou rodar localmente com:
- **Compilador C:** GCC
- **Python:** 3.8+ 
- Instale as dependências executando: pip install -r requirements.txt

### Especificações de hardware utilizadas: "escrever aqui"

## Como Compilar e Executar

### 1. Compilação Automatizada (C)
make all

### 2. Execução dos Testes de Corretude
python3 tests/test.py

### 3. Execução do Benchmark
python3 scripts/benchmark.py

## Execução via Docker (Opcional)
Para garantir um ambiente de execução totalmente isolado e reprodutível:

docker build -t complexidade-sat .
docker run -it complexidade-sat
