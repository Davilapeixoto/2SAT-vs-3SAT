#include "cnf.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int literal_verdadeiro(int literal, int valor) {
    if (literal > 0 && valor == 1) {
        return 1;
    }
    if (literal < 0 && valor == 0) {
        return 1;
    }
    return 0;
}

int propagar(FormulaCNF *formula, int *valores) {
    int mudou = 1;

    while (mudou == 1) {
        mudou = 0;
        for (int i = 0; i < formula->quantidade; i++) {
            Clausula clausula = formula->clausulas[i];
            int satisfeita = 0;
            int livres = 0;
            int ultimo = 0;

            for (int j = 0; j < clausula.tamanho; j++) {
                int literal = clausula.literais[j];
                int valor = valores[abs(literal)];

                if (valor == -1) {
                    livres++;
                    ultimo = literal;
                } else if (literal_verdadeiro(literal, valor) == 1) {
                    satisfeita = 1;
                    break;
                }
            }

            if (satisfeita == 1) {
                continue;
            }
            if (livres == 0) {
                return 0;
            }
            if (livres == 1) {
                int variavel = abs(ultimo);
                if (ultimo > 0) {
                    valores[variavel] = 1;
                } else {
                    valores[variavel] = 0;
                }
                mudou = 1;
            }
        }
    }
    return 1;
}

int dpll(FormulaCNF *formula, int *valores) {
    if (propagar(formula, valores) == 0) {
        return 0;
    }

    int escolhida = 0;
    for (int i = 0; i < formula->quantidade; i++) {
        Clausula clausula = formula->clausulas[i];
        int satisfeita = 0;
        int candidata = 0;

        for (int j = 0; j < clausula.tamanho; j++) {
            int literal = clausula.literais[j];
            int variavel = abs(literal);
            int valor = valores[variavel];

            if (literal_verdadeiro(literal, valor) == 1) {
                satisfeita = 1;
                break;
            }
            if (valor == -1 && candidata == 0) {
                candidata = variavel;
            }
        }

        if (satisfeita == 0) {
            escolhida = candidata;
            break;
        }
    }

    if (escolhida == 0) {
        return 1;
    }

    int tamanho = formula->variaveis + 1;
    int *copia = malloc((size_t)tamanho * sizeof(int));
    if (copia == NULL) {
        return -1;
    }

    memcpy(copia, valores, (size_t)tamanho * sizeof(int));
    copia[escolhida] = 1;
    int resultado = dpll(formula, copia);

    if (resultado == 0) {
        memcpy(copia, valores, (size_t)tamanho * sizeof(int));
        copia[escolhida] = 0;
        resultado = dpll(formula, copia);
    }

    free(copia);
    return resultado;
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Uso: %s arquivo.cnf\n", argv[0]);
        return 1;
    }

    FormulaCNF formula;
    if (cnf_carregar(argv[1], 3, &formula) == 0) {
        printf("Erro ao ler arquivo CNF\n");
        return 1;
    }

    int *valores = malloc(((size_t)formula.variaveis + 1) * sizeof(int));
    if (valores == NULL) {
        cnf_liberar(&formula);
        printf("Erro de memoria\n");
        return 1;
    }

    for (int i = 0; i <= formula.variaveis; i++) {
        valores[i] = -1;
    }

    int resultado = dpll(&formula, valores);
    free(valores);
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
