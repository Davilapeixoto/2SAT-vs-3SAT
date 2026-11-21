#define _XOPEN_SOURCE 700

#include "cnf.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/resource.h>
#include <time.h>

typedef struct {
    int *inicio;
    int *destino;
    int *proximo;
    int arestas;
} Grafo;

int criar_grafo(Grafo *grafo, int vertices, int arestas) {
    grafo->inicio = malloc(((size_t)vertices + 1) * sizeof(int));
    grafo->destino = malloc(((size_t)arestas + 1) * sizeof(int));
    grafo->proximo = malloc(((size_t)arestas + 1) * sizeof(int));
    grafo->arestas = 0;

    if (grafo->inicio == NULL || grafo->destino == NULL || grafo->proximo == NULL) {
        return 0;
    }
    for (int i = 0; i < vertices; i++) {
        grafo->inicio[i] = -1;
    }
    return 1;
}

void liberar_grafo(Grafo *grafo) {
    free(grafo->inicio);
    free(grafo->destino);
    free(grafo->proximo);
}

void adicionar_aresta(Grafo *grafo, int origem, int destino) {
    int i = grafo->arestas;
    grafo->destino[i] = destino;
    grafo->proximo[i] = grafo->inicio[origem];
    grafo->inicio[origem] = i;
    grafo->arestas++;
}

int indice(int literal) {
    int posicao = (abs(literal) - 1) * 2;
    if (literal < 0) {
        posicao++;
    }
    return posicao;
}

int negacao(int vertice) {
    if (vertice % 2 == 0) {
        return vertice + 1;
    } else {
        return vertice - 1;
    }
}

void dfs1(Grafo *grafo, int atual, int *visitado, int *ordem, int *total) {
    visitado[atual] = 1;
    for (int e = grafo->inicio[atual]; e != -1; e = grafo->proximo[e]) {
        int vizinho = grafo->destino[e];
        if (visitado[vizinho] == 0) {
            dfs1(grafo, vizinho, visitado, ordem, total);
        }
    }

    ordem[*total] = atual;
    (*total)++;
}

void dfs2(Grafo *grafo, int atual, int grupo, int *componentes) {
    componentes[atual] = grupo;
    for (int e = grafo->inicio[atual]; e != -1; e = grafo->proximo[e]) {
        int vizinho = grafo->destino[e];
        if (componentes[vizinho] == -1) {
            dfs2(grafo, vizinho, grupo, componentes);
        }
    }
}

int resolver_2sat(FormulaCNF *formula, size_t *memoria_pico) {
    int n = formula->variaveis;
    int vertices = 2 * n;
    int limite_arestas = 2 * formula->quantidade;
    Grafo grafo = {0};
    Grafo invertido = {0};
    int resultado = 1;

    if (memoria_pico != NULL) {
        *memoria_pico = 0;
    }

    for (int i = 0; i < formula->quantidade; i++) {
        if (formula->clausulas[i].tamanho == 0) {
            return 0;
        }
    }

    if (criar_grafo(&grafo, vertices, limite_arestas) == 0 ||
        criar_grafo(&invertido, vertices, limite_arestas) == 0) {
        liberar_grafo(&grafo);
        liberar_grafo(&invertido);
        return -1;
    }

    for (int i = 0; i < formula->quantidade; i++) {
        Clausula clausula = formula->clausulas[i];
        int a = indice(clausula.literais[0]);
        int b = a;
        if (clausula.tamanho == 2) {
            b = indice(clausula.literais[1]);
        }

        adicionar_aresta(&grafo, negacao(a), b);
        adicionar_aresta(&grafo, negacao(b), a);
        adicionar_aresta(&invertido, b, negacao(a));
        adicionar_aresta(&invertido, a, negacao(b));
    }

    int *visitado = calloc((size_t)vertices + 1, sizeof(int));
    int *ordem = malloc(((size_t)vertices + 1) * sizeof(int));
    int *componentes = malloc(((size_t)vertices + 1) * sizeof(int));

    if (visitado == NULL || ordem == NULL || componentes == NULL) {
        free(visitado);
        free(ordem);
        free(componentes);
        liberar_grafo(&grafo);
        liberar_grafo(&invertido);
        return -1;
    }

    if (memoria_pico != NULL) {
        size_t mem_grafo = ((size_t)vertices + 1 + 2 * ((size_t)limite_arestas + 1)) * sizeof(int);
        size_t mem_aux = 3 * ((size_t)vertices + 1) * sizeof(int);
        *memoria_pico = 2 * mem_grafo + mem_aux;
    }

    int total = 0;
    for (int i = 0; i < vertices; i++) {
        if (visitado[i] == 0) {
            dfs1(&grafo, i, visitado, ordem, &total);
        }
        componentes[i] = -1;
    }

    int grupo = 0;
    for (int i = total - 1; i >= 0; i--) {
        int vertice = ordem[i];
        if (componentes[vertice] == -1) {
            dfs2(&invertido, vertice, grupo, componentes);
            grupo++;
        }
    }

    for (int i = 0; i < n; i++) {
        if (componentes[2 * i] == componentes[2 * i + 1]) {
            resultado = 0;
            break;
        }
    }

    free(visitado);
    free(ordem);
    free(componentes);

    liberar_grafo(&grafo);
    liberar_grafo(&invertido);
    return resultado;
}

int main(int argc, char *argv[]) {
    int modo_bench = 0;
    int repeticoes = 1;

    if (argc == 4 && strcmp(argv[2], "--bench") == 0) {
        modo_bench = 1;
        repeticoes = atoi(argv[3]);
        if (repeticoes <= 0) {
            printf("Uso: %s arquivo.cnf [--bench repeticoes]\n", argv[0]);
            return 1;
        }
    } else if (argc != 2) {
        printf("Uso: %s arquivo.cnf [--bench repeticoes]\n", argv[0]);
        return 1;
    }

    FormulaCNF formula;
    if (cnf_carregar(argv[1], 2, &formula) == 0) {
        printf("Erro ao ler arquivo CNF\n");
        return 1;
    }

    if (modo_bench == 0) {
        int resultado = resolver_2sat(&formula, NULL);
        cnf_liberar(&formula);

        if (resultado == 1) {
            printf("SAT\n");
        } else if (resultado == 0) {
            printf("UNSAT\n");
        } else {
            printf("Erro de memoria\n");
            return 1;
        }
        return 0;
    }

    long long *tempos = malloc((size_t)repeticoes * sizeof(long long));
    if (tempos == NULL) {
        cnf_liberar(&formula);
        printf("Erro de memoria\n");
        return 1;
    }

    int resultado = 0;
    size_t memoria_pico = 0;

    for (int r = 0; r < repeticoes; r++) {
        struct timespec inicio, fim;
        size_t mem_exec = 0;

        clock_gettime(CLOCK_MONOTONIC, &inicio);
        resultado = resolver_2sat(&formula, &mem_exec);
        clock_gettime(CLOCK_MONOTONIC, &fim);

        if (resultado < 0) {
            free(tempos);
            cnf_liberar(&formula);
            printf("Erro de memoria\n");
            return 1;
        }

        if (mem_exec > memoria_pico) {
            memoria_pico = mem_exec;
        }

        tempos[r] = (long long)(fim.tv_sec - inicio.tv_sec) * 1000000000LL +
                    (long long)(fim.tv_nsec - inicio.tv_nsec);
    }

    struct rusage uso;
    long rss_kb = 0;
    if (getrusage(RUSAGE_SELF, &uso) == 0) {
        rss_kb = uso.ru_maxrss;
    }

    printf("RESULTADO:%s\n", resultado == 1 ? "SAT" : "UNSAT");
    printf("TEMPOS_NS:");
    for (int r = 0; r < repeticoes; r++) {
        if (r > 0) {
            printf(",");
        }
        printf("%lld", tempos[r]);
    }
    printf("\n");
    printf("MEMORIA_PICO_BYTES:%zu\n", memoria_pico);
    printf("MEMORIA_RSS_KB:%ld\n", rss_kb);

    free(tempos);
    cnf_liberar(&formula);
    return 0;
}