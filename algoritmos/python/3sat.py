import sys
import time
import tracemalloc
from cnf import cnf_carregar

try:
    import resource
except ImportError:
    resource = None


def literal_verdadeiro(literal, valor):
    if literal > 0 and valor == 1:
        return 1
    if literal < 0 and valor == 0:
        return 1
    return 0


def propagar(formula, valores):
    mudou = 1

    while mudou == 1:
        mudou = 0
        for i in range(formula.quantidade):
            clausula = formula.clausulas[i]
            satisfeita = 0
            livres = 0
            ultimo = 0

            for j in range(clausula.tamanho):
                literal = clausula.literais[j]
                valor = valores[abs(literal)]

                if valor == -1:
                    livres += 1
                    ultimo = literal
                elif literal_verdadeiro(literal, valor) == 1:
                    satisfeita = 1
                    break

            if satisfeita == 1:
                continue
            if livres == 0:
                return 0
            if livres == 1:
                variavel = abs(ultimo)
                if ultimo > 0:
                    valores[variavel] = 1
                else:
                    valores[variavel] = 0
                mudou = 1
    return 1


def dpll(formula, valores):
    if propagar(formula, valores) == 0:
        return 0

    escolhida = 0
    for i in range(formula.quantidade):
        clausula = formula.clausulas[i]
        satisfeita = 0
        candidata = 0

        for j in range(clausula.tamanho):
            literal = clausula.literais[j]
            variavel = abs(literal)
            valor = valores[variavel]

            if literal_verdadeiro(literal, valor) == 1:
                satisfeita = 1
                break
            if valor == -1 and candidata == 0:
                candidata = variavel

        if satisfeita == 0:
            escolhida = candidata
            break

    if escolhida == 0:
        return 1

    copia = valores.copy()
    copia[escolhida] = 1
    resultado = dpll(formula, copia)

    if resultado == 0:
        copia = valores.copy()
        copia[escolhida] = 0
        resultado = dpll(formula, copia)

    return resultado


def main():
    modo_bench = False
    repeticoes = 1

    if len(sys.argv) == 4 and sys.argv[2] == "--bench":
        modo_bench = True
        try:
            repeticoes = int(sys.argv[3])
        except ValueError:
            repeticoes = 0
        if repeticoes <= 0:
            print(f"Uso: {sys.argv[0]} arquivo.cnf [--bench repeticoes]")
            sys.exit(1)
    elif len(sys.argv) != 2:
        print(f"Uso: {sys.argv[0]} arquivo.cnf [--bench repeticoes]")
        sys.exit(1)

    formula = cnf_carregar(sys.argv[1], 3)
    if formula is None:
        print("Erro ao ler arquivo CNF")
        sys.exit(1)

    if not modo_bench:
        valores = [-1] * (formula.variaveis + 1)
        resultado = dpll(formula, valores)
        if resultado == 1:
            print("SAT")
        elif resultado == 0:
            print("UNSAT")
        else:
            print("Erro de memoria")
            sys.exit(1)
        return

    tempos = []
    resultado = 0
    for _ in range(repeticoes):
        valores = [-1] * (formula.variaveis + 1)
        inicio = time.perf_counter_ns()
        resultado = dpll(formula, valores)
        fim = time.perf_counter_ns()
        tempos.append(fim - inicio)

    tracemalloc.start()
    valores = [-1] * (formula.variaveis + 1)
    dpll(formula, valores)
    _, memoria_pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    rss_kb = 0
    if resource is not None:
        rss_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

    print(f"RESULTADO:{'SAT' if resultado == 1 else 'UNSAT'}")
    print("TEMPOS_NS:" + ",".join(str(t) for t in tempos))
    print(f"MEMORIA_PICO_BYTES:{memoria_pico}")
    print(f"MEMORIA_RSS_KB:{rss_kb}")


if __name__ == "__main__":
    main()