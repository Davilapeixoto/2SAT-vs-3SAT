#include "cnf.h"
#include <ctype.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>

void cnf_liberar(FormulaCNF *formula) {
    free(formula->clausulas);
    formula->clausulas = NULL;
}

int cnf_carregar(const char *caminho, int limite, FormulaCNF *formula) {
    FILE *arquivo = fopen(caminho, "r");
    if (arquivo == NULL) {
        return 0;
    }

    formula->variaveis = 0;
    formula->quantidade = 0;
    formula->clausulas = NULL;

    char linha[4096];
    int cabecalho = 0;
    int quantidade_lida = 0;
    int tamanho_atual = 0;
    int valido = 1;

    while (fgets(linha, sizeof(linha), arquivo) != NULL && valido == 1) {
        char *p = linha;
        while (isspace((unsigned char)*p)) {
            p++;
        }

        if (*p == 'c' || *p == '\0') {
            continue;
        }

        if (cabecalho == 0) {
            int n, m;
            if (sscanf(p, "p cnf %d %d", &n, &m) != 2 || n < 0 || m < 0 ||
                n > INT_MAX / 2 || m > INT_MAX / 2) {
                valido = 0;
                break;
            }

            formula->variaveis = n;
            formula->quantidade = m;
            formula->clausulas = calloc((size_t)m + 1, sizeof(Clausula));
            if (formula->clausulas == NULL) {
                valido = 0;
                break;
            }
            cabecalho = 1;
            continue;
        }

        while (*p != '\0') {
            while (isspace((unsigned char)*p)) {
                p++;
            }
            if (*p == '\0') {
                break;
            }

            char *fim;
            long numero = strtol(p, &fim, 10);
            if (fim == p || numero < -INT_MAX || numero > INT_MAX ||
                quantidade_lida >= formula->quantidade) {
                valido = 0;
                break;
            }
            p = fim;

            if (numero == 0) {
                formula->clausulas[quantidade_lida].tamanho = tamanho_atual;
                quantidade_lida++;
                tamanho_atual = 0;
            } else {
                if (labs(numero) > formula->variaveis || tamanho_atual >= limite) {
                    valido = 0;
                    break;
                }
                formula->clausulas[quantidade_lida].literais[tamanho_atual] = (int)numero;
                tamanho_atual++;
            }
        }
    }

    if (ferror(arquivo)) {
        valido = 0;
    }
    fclose(arquivo);

    if (valido == 0 || cabecalho == 0 || tamanho_atual != 0 ||
        quantidade_lida != formula->quantidade) {
        cnf_liberar(formula);
        return 0;
    }
    return 1;
}
