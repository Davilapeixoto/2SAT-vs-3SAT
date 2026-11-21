import sys
import time
import tracemalloc
from cnf import cnf_carregar

try:
    import resource
except ImportError:
    resource = None


class Grafo:
    def __init__(self, vertices, arestas):
        self.inicio = [-1] * (vertices + 1)
        self.destino = [0] * (arestas + 1)
        self.proximo = [0] * (arestas + 1)
        self.arestas = 0


def adicionar_aresta(grafo, origem, destino):
    i = grafo.arestas
    grafo.destino[i] = destino
    grafo.proximo[i] = grafo.inicio[origem]
    grafo.inicio[origem] = i
    grafo.arestas += 1


def indice(literal):
    posicao = (abs(literal) - 1) * 2
    if literal < 0:
        posicao += 1
    return posicao


def negacao(vertice):
    if vertice % 2 == 0:
        return vertice + 1
    else:
        return vertice - 1


def dfs1(grafo, atual, visitado, ordem, total):
    visitado[atual] = 1
    e = grafo.inicio[atual]
    while e != -1:
        vizinho = grafo.destino[e]
        if visitado[vizinho] == 0:
            dfs1(grafo, vizinho, visitado, ordem, total)
        e = grafo.proximo[e]

    ordem[total[0]] = atual
    total[0] += 1


def dfs2(grafo, atual, grupo, componentes):
    componentes[atual] = grupo
    e = grafo.inicio[atual]
    while e != -1:
        vizinho = grafo.destino[e]
        if componentes[vizinho] == -1:
            dfs2(grafo, vizinho, grupo, componentes)
        e = grafo.proximo[e]


def resolver_2sat(formula):
    n = formula.variaveis
    vertices = 2 * n
    limite_arestas = 2 * formula.quantidade
    resultado = 1

    for i in range(formula.quantidade):
        if formula.clausulas[i].tamanho == 0:
            return 0

    if vertices + 1000 > sys.getrecursionlimit():
        sys.setrecursionlimit(vertices + 1000)

    grafo = Grafo(vertices, limite_arestas)
    invertido = Grafo(vertices, limite_arestas)

    for i in range(formula.quantidade):
        clausula = formula.clausulas[i]
        a = indice(clausula.literais[0])
        b = a
        if clausula.tamanho == 2:
            b = indice(clausula.literais[1])

        adicionar_aresta(grafo, negacao(a), b)
        adicionar_aresta(grafo, negacao(b), a)
        adicionar_aresta(invertido, b, negacao(a))
        adicionar_aresta(invertido, a, negacao(b))

    visitado = [0] * (vertices + 1)
    ordem = [0] * (vertices + 1)
    componentes = [-1] * (vertices + 1)

    total = [0]
    for i in range(vertices):
        if visitado[i] == 0:
            dfs1(grafo, i, visitado, ordem, total)
        componentes[i] = -1

    grupo = 0
    for i in range(total[0] - 1, -1, -1):
        vertice = ordem[i]
        if componentes[vertice] == -1:
            dfs2(invertido, vertice, grupo, componentes)
            grupo += 1

    for i in range(n):
        if componentes[2 * i] == componentes[2 * i + 1]:
            resultado = 0
            break

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

    formula = cnf_carregar(sys.argv[1], 2)
    if formula is None:
        print("Erro ao ler arquivo CNF")
        sys.exit(1)

    if not modo_bench:
        resultado = resolver_2sat(formula)
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
        inicio = time.perf_counter_ns()
        resultado = resolver_2sat(formula)
        fim = time.perf_counter_ns()
        tempos.append(fim - inicio)

    tracemalloc.start()
    resolver_2sat(formula)
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