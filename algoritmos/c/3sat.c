#define _XOPEN_SOURCE 700

#include "cnf.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/resource.h>
#include <time.h>

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

int dpll(FormulaCNF *formula, int *valores, size_t *mem_atual, size_t *mem_pico) {
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
    size_t bytes = (size_t)tamanho * sizeof(int);
    int *copia = malloc(bytes);
    if (copia == NULL) {
        return -1;
    }

    if (mem_atual != NULL && mem_pico != NULL) {
        *mem_atual += bytes;
        if (*mem_atual > *mem_pico) {
            *mem_pico = *mem_atual;
        }
    }

    memcpy(copia, valores, bytes);
    copia[escolhida] = 1;
    int resultado = dpll(formula, copia, mem_atual, mem_pico);

    if (resultado == 0) {
        memcpy(copia, valores, bytes);
        copia[escolhida] = 0;
        resultado = dpll(formula, copia, mem_atual, mem_pico);
    }

    free(copia);
    if (mem_atual != NULL) {
        *mem_atual -= bytes;
    }
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
    if (cnf_carregar(argv[1], 3, &formula) == 0) {
        printf("Erro ao ler arquivo CNF\n");
        return 1;
    }

    size_t bytes_base = ((size_t)formula.variaveis + 1) * sizeof(int);
    int *valores = malloc(bytes_base);
    if (valores == NULL) {
        cnf_liberar(&formula);
        printf("Erro de memoria\n");
        return 1;
    }

    if (modo_bench == 0) {
        for (int i = 0; i <= formula.variaveis; i++) {
            valores[i] = -1;
        }

        int resultado = dpll(&formula, valores, NULL, NULL);
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

    long long *tempos = malloc((size_t)repeticoes * sizeof(long long));
    if (tempos == NULL) {
        free(valores);
        cnf_liberar(&formula);
        printf("Erro de memoria\n");
        return 1;
    }

    int resultado = 0;
    size_t memoria_pico = 0;

    for (int r = 0; r < repeticoes; r++) {
        struct timespec inicio, fim;
        size_t mem_atual = bytes_base;
        size_t mem_exec = bytes_base;

        for (int i = 0; i <= formula.variaveis; i++) {
            valores[i] = -1;
        }

        clock_gettime(CLOCK_MONOTONIC, &inicio);
        resultado = dpll(&formula, valores, &mem_atual, &mem_exec);
        clock_gettime(CLOCK_MONOTONIC, &fim);

        if (resultado < 0) {
            free(tempos);
            free(valores);
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
    free(valores);
    cnf_liberar(&formula);
    return 0;
}