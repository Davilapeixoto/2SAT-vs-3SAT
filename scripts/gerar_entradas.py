import csv
import random
from pathlib import Path


SEED = 42
RAIZ = Path(__file__).resolve().parent.parent
DIR_SAIDA = RAIZ / "dados" / "benchmark"
MANIFESTO = DIR_SAIDA / "manifesto.csv"

TAMANHOS_2SAT = [100, 200, 400, 800, 1600, 3200, 6400]
TAMANHOS_3SAT_MEDIO = [10, 14, 18, 22, 26, 30, 34, 38, 42, 46, 50, 55, 60, 65, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160]
TAMANHOS_3SAT_EXTREMOS = [10, 14, 18, 22, 26, 30, 34, 38, 42, 46, 50]


def salvar_cnf(caminho, n, clausulas, comentario):
    with open(caminho, "w", encoding="utf-8", newline="\n") as arquivo:
        arquivo.write(f"c {comentario}\n")
        arquivo.write(f"p cnf {n} {len(clausulas)}\n")
        for clausula in clausulas:
            if clausula:
                arquivo.write(" ".join(str(lit) for lit in clausula) + " 0\n")
            else:
                arquivo.write("0\n")


def gerar_clausulas_aleatorias(rng, n, m, k):
    clausulas = []
    for _ in range(m):
        vars_escolhidas = rng.sample(range(1, n + 1), k)
        clausula = [v if rng.random() < 0.5 else -v for v in vars_escolhidas]
        clausulas.append(clausula)
    return clausulas


def gerar_3sat_melhor_caso(rng, n, m):
    clausulas = []
    for _ in range(m):
        vars_escolhidas = rng.sample(range(1, n + 1), 3)
        clausula = [
            vars_escolhidas[0],
            vars_escolhidas[1] if rng.random() < 0.5 else -vars_escolhidas[1],
            vars_escolhidas[2] if rng.random() < 0.5 else -vars_escolhidas[2],
        ]
        rng.shuffle(clausula)
        clausulas.append(clausula)
    return clausulas


def main():
    DIR_SAIDA.mkdir(parents=True, exist_ok=True)
    rng = random.Random(SEED)
    registros = []

    for n in TAMANHOS_2SAT:
        m_medio = 3 * n
        nome = f"2sat_medio_n{n:05d}.cnf"
        clausulas = gerar_clausulas_aleatorias(rng, n, m_medio, 2)
        salvar_cnf(DIR_SAIDA / nome, n, clausulas, f"2-SAT caso medio (seed={SEED}, n={n}, m={m_medio})")
        registros.append((nome, "2-SAT", "medio", n, m_medio))

        nome_melhor = f"2sat_melhor_n{n:05d}.cnf"
        clausulas_melhor = [[]] + gerar_clausulas_aleatorias(rng, n, m_medio - 1, 2)
        salvar_cnf(DIR_SAIDA / nome_melhor, n, clausulas_melhor, f"2-SAT melhor caso - clausula vazia (seed={SEED})")
        registros.append((nome_melhor, "2-SAT", "melhor", n, m_medio))

        m_pior = 6 * n
        nome_pior = f"2sat_pior_n{n:05d}.cnf"
        clausulas_pior = gerar_clausulas_aleatorias(rng, n, m_pior, 2)
        salvar_cnf(DIR_SAIDA / nome_pior, n, clausulas_pior, f"2-SAT pior caso - grafo denso (seed={SEED}, m=6n)")
        registros.append((nome_pior, "2-SAT", "pior", n, m_pior))

    for n in TAMANHOS_3SAT_MEDIO:
        m = round(4.26 * n)
        nome = f"3sat_medio_n{n:03d}.cnf"
        clausulas = gerar_clausulas_aleatorias(rng, n, m, 3)
        salvar_cnf(DIR_SAIDA / nome, n, clausulas, f"3-SAT caso medio - transicao de fase alpha=4.26 (seed={SEED})")
        registros.append((nome, "3-SAT", "medio", n, m))

    for n in TAMANHOS_3SAT_EXTREMOS:
        m_melhor = round(4.26 * n)
        nome_melhor = f"3sat_melhor_n{n:03d}.cnf"
        clausulas_melhor = gerar_3sat_melhor_caso(rng, n, m_melhor)
        salvar_cnf(DIR_SAIDA / nome_melhor, n, clausulas_melhor, f"3-SAT melhor caso - satisfativel sem backtracking (seed={SEED})")
        registros.append((nome_melhor, "3-SAT", "melhor", n, m_melhor))

        m_pior = round(5.0 * n)
        nome_pior = f"3sat_pior_n{n:03d}.cnf"
        clausulas_pior = gerar_clausulas_aleatorias(rng, n, m_pior, 3)
        salvar_cnf(DIR_SAIDA / nome_pior, n, clausulas_pior, f"3-SAT pior caso - sobre-restrito alpha=5.0 (seed={SEED})")
        registros.append((nome_pior, "3-SAT", "pior", n, m_pior))

    with open(MANIFESTO, "w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(["arquivo", "problema", "caso", "variaveis", "clausulas"])
        escritor.writerows(registros)

    print(f"Geradas {len(registros)} instancias em {DIR_SAIDA} (seed={SEED}).")


if __name__ == "__main__":
    main()