#include "cnf.h"
#include <stdio.h>
#include <stdlib.h>

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

int resolver_2sat(FormulaCNF *formula) {
    int n = formula->variaveis;
    int vertices = 2 * n;
    int limite_arestas = 2 * formula->quantidade;
    Grafo grafo = {0};
    Grafo invertido = {0};
    int resultado = 1;

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
    if (argc != 2) {
        printf("Uso: %s arquivo.cnf\n", argv[0]);
        return 1;
    }

    FormulaCNF formula;
    if (cnf_carregar(argv[1], 2, &formula) == 0) {
        printf("Erro ao ler arquivo CNF\n");
        return 1;
    }

    int resultado = resolver_2sat(&formula);
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
