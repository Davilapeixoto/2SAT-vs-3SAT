# Projeto de Complexidade: 2-SAT vs. 3-SAT

**Disciplina:** Teoria da Computação  
**Professor:** Daniel Bezerra  
**Equipe:** Breno Pereira, Davi de Lucena, Davila Peixoto, João Carlos Vasconcelos, João Pedro Pessôa

Este repositório reúne as implementações, testes automatizados, gerador de instâncias, scripts de benchmark e geração de gráficos para a análise teórica e experimental da complexidade de tempo (e espaço) do par de contraste **P vs. NP**: **2-SAT (classe P)** e **3-SAT (NP-completo)**.

Foram desenvolvidas **4 implementações** equivalentes (2 algoritmos x 2 linguagens), todas executadas sobre exatamente as mesmas entradas no formato DIMACS CNF:

| Problema | Classe | Algoritmo | Complexidade de Tempo | Complexidade de Espaço | Linguagens |
| :--- | :---: | :--- | :--- | :--- | :---: |
| **2-SAT** | P | Kosaraju (SCC em grafo de implicações) | `Θ(n + m)` | `Θ(n + m)` | C e Python |
| **3-SAT** | NP-completo | DPLL (Backtracking + Propagação Unitária) | O(2ⁿ * m) no pior caso | O(n² + m) | C e Python |

## Estrutura do Repositório

```text
.
├── algoritmos/
│   ├── c/
│   │   ├── 2sat.c              # Implementação do 2-SAT (Kosaraju) em C
│   │   ├── 3sat.c              # Implementação do 3-SAT (DPLL) em C
│   │   ├── cnf.c               # Parser de arquivos DIMACS CNF em C
│   │   └── cnf.h               # Estruturas e cabeçalho do parser CNF
│   └── python/
│       ├── 2sat.py             # Implementação fiel do 2-SAT (Kosaraju) em Python
│       ├── 3sat.py             # Implementação fiel do 3-SAT (DPLL) em Python
│       └── cnf.py              # Parser equivalente de arquivos DIMACS CNF em Python
├── dados/
│   ├── *.cnf                   # 28 instâncias fixas (básicas e escalonadas) para validação
│   ├── gabarito.csv            # Metadados e respostas esperadas (SAT/UNSAT) das 28 instâncias
│   └── benchmark/              # (Gerado) 67 instâncias reprodutíveis (SEED = 42)
├── resultados/                 # (Gerado) Métricas, tabelas e gráficos dos experimentos
│   ├── ambiente.json           # Especificações de hardware/software coletadas automaticamente
│   ├── benchmark.csv           # Tempos (média, DP, mín, máx) e uso de memória (pico e RSS)
│   ├── tabelas_resumo.md       # Tabelas formatadas em Markdown para o relatório
│   └── graficos/               # 6 gráficos em alta resolução (300 DPI)
├── scripts/
│   ├── gerar_entradas.py       # Gerador determinístico de entradas (melhor, médio e pior caso)
│   ├── benchmark.py            # Orquestrador de medições (repetições, timeout de 60 s, memória)
│   └── graficos.py             # Geração automática dos gráficos e tabelas resumo
├── tests/
│   └── test.py                 # Testes automatizados de corretude cruzada (C vs. Python vs. Gabarito)
├── Dockerfile                  # Ambiente isolado opcional
├── Makefile                    # Automação de compilação, testes, execução e benchmark
├── requirements.txt            # Dependências Python para geração dos gráficos
└── README.md
```

## Pré-requisitos e Ambiente

Para reproduzir integralmente o projeto em ambiente Linux (recomendado para os experimentos oficiais):

* **Compilador C:** `gcc` (C11) e `make`
* **Python:** 3.8+ (com suporte a `venv` para isolar as bibliotecas de gráficos)
* **Flags de compilação C:** `-std=c11 -O2 -Wall -Wextra -Wpedantic`

### Configuração do Ambiente Python (`venv`)

Os algoritmos (`2sat.py`, `3sat.py`), os testes (`test.py`), o gerador (`gerar_entradas.py`) e o benchmark (`benchmark.py`) utilizam **apenas a biblioteca padrão do Python**. As dependências de `requirements.txt` (`matplotlib`, `numpy`, `pandas`) são usadas exclusivamente pelo script `scripts/graficos.py`.

Para evitar conflitos com pacotes do sistema (especialmente no Ubuntu 24.04+), recomenda-se criar um ambiente virtual:

```bash
# Caso necessário em sistemas Debian/Ubuntu:
sudo apt update && sudo apt install -y build-essential python3-venv

# Criar e ativar o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependências para os gráficos
pip install -r requirements.txt
```

### Ambiente de Execução Oficial

Os dados abaixo foram coletados automaticamente em `resultados/ambiente.json` durante a execução do benchmark.

| Parâmetro | Valor |
| :--- | :--- |
| **Sistema Operacional** | Linux 7.3.4-1-cachyos (x86_64, glibc 2.44) |
| **CPU** | AMD Ryzen 7 7735HS with Radeon Graphics |
| **Núcleos Lógicos** | 16 |
| **Memória RAM Total** | 14,92 GB |
| **Compilador C (`gcc`)** | GCC 16.2.1 (20260810) |
| **Flags de Compilação** | `-std=c11 -O2 -Wall -Wextra -Wpedantic` |
| **Interpretador Python** | Python 3.14.10 |

## Como Reproduzir os Resultados (Passo a Passo)

### 1. Compilação (C) e Verificação de Sintaxe (Python)

Compila os executáveis `./2sat` e `./3sat` com otimização `-O2` e valida o bytecode dos arquivos Python:

```bash
make all
```

### 2. Testes Automatizados de Corretude

Executa as 4 implementações sobre as 28 instâncias fixas de `dados/` e verifica se C e Python concordam entre si e com o `dados/gabarito.csv`:

```bash
make test
```

### 3. Geração das Entradas do Benchmark (Semente Fixa)

Gera de forma determinística (`SEED = 42`) as 67 instâncias em `dados/benchmark/`, cobrindo caso médio, melhor caso e pior caso para ambos os problemas:

* **2-SAT:** 7 tamanhos em escala geométrica (`n = 100, 200, 400, 800, 1600, 3200 e 6400`), com caso médio (`m = 3n`), melhor caso (cláusula vazia em `O(1)`) e pior caso (grafo denso com `m = 6n`).
* **3-SAT:** `n = 10` até `n = 160` na transição de fase (razão `m/n = 4,26`) para o caso médio, além de melhor caso (satisfatível sem *backtracking*) e pior caso (sobre-restrito com razão `m/n = 5,0`).

```bash
python3 scripts/gerar_entradas.py
```

### 4. Execução do Benchmark Oficial (Tempo e Memória)

> **Recomendação metodológica:** Antes de rodar o benchmark definitivo, feche navegadores, chamadas de vídeo e programas pesados para evitar preempção de CPU e minimizar o desvio-padrão das medições.

```bash
make benchmark
```

O script `scripts/benchmark.py` executa a metodologia experimental automaticamente:

* Isola **apenas o tempo do algoritmo** (leitura de arquivo e impressão ficam fora da medição), usando `clock_gettime(CLOCK_MONOTONIC)` em C e `time.perf_counter_ns()` em Python.
* Realiza de **15 a 20 repetições** por instância, reportando média, desvio-padrão, mínimo e máximo.
* Aplica o limite de **60 segundos** por execução individual para identificar automaticamente o maior `n` viável no 3-SAT.
* Registra o **pico de memória dinâmica** (bytes alocados pelo algoritmo) e o **RSS** do processo (KB) para comparação com a complexidade de espaço teórica.
* Salva os resultados em `resultados/benchmark.csv` e o perfil da máquina em `resultados/ambiente.json`.

### 5. Geração dos Gráficos e Tabelas

Com o ambiente virtual `.venv` ativado, execute:

```bash
python3 scripts/graficos.py
```

Serão gerados `resultados/tabelas_resumo.md` e 6 gráficos em `resultados/graficos/`:

1. `01_2sat_vs_3sat.png` — Contraste P vs. NP (2-SAT linear vs. 3-SAT exponencial com limite de 60 s).
2. `02_2sat_teorico_vs_medido.png` — Validação assintótica do 2-SAT em escala log-log e razão `T(n) / (n + m)`.
3. `03_3sat_teorico_vs_medido.png` — Curva medida do 3-SAT (SAT vs. UNSAT) com ajuste exponencial c * b^n.
4. `04_comparacao_linguagens.png` — Speedup médio de C (`-O2`) sobre Python 3.
5. `05_casos_forcados.png` — Comparação entre melhor caso, caso médio e pior caso.
6. `06_memoria_teorico_vs_medido.png` — Memória dinâmica medida vs. complexidade de espaço teórica (`Θ(n + m)` e O(n²)).

## Execução Individual e Limpeza

Para executar qualquer uma das 4 implementações isoladamente sobre um arquivo `.cnf`:

```bash
# Atalhos via Makefile (usa instância básica padrão se FILE não for informado)
make run-2sat-c FILE=dados/2sat_n320_sat.cnf
make run-2sat-py FILE=dados/2sat_n320_sat.cnf
make run-3sat-c FILE=dados/3sat_n040_unsat.cnf
make run-3sat-py FILE=dados/3sat_n040_unsat.cnf

# Modo de medição interna (tempo em nanossegundos + memória)
./2sat dados/2sat_n320_sat.cnf --bench 20
python3 algoritmos/python/2sat.py dados/2sat_n320_sat.cnf --bench 20
```

Para remover os binários compilados e caches Python:

```bash
make clean
```

## Execução via Docker (Opcional)

Para executar o projeto em um container isolado:

```bash
docker build -t complexidade-sat .
docker run -it complexidade-sat
```
