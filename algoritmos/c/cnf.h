#ifndef CNF_H
#define CNF_H

typedef struct {
    int literais[3];
    int tamanho;
} Clausula;

typedef struct {
    int variaveis;
    int quantidade;
    Clausula *clausulas;
} FormulaCNF;

int cnf_carregar(const char *caminho, int limite, FormulaCNF *formula);
void cnf_liberar(FormulaCNF *formula);

#endif
