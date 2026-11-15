# Projeto 2-SAT vs 3-SAT

## 1. O que é SAT?

SAT (*Boolean Satisfiability Problem*) é um problema que busca descobrir se existe uma combinação de valores **verdadeiro (V)** e **falso (F)** capaz de satisfazer uma expressão lógica.

Por exemplo:

`(A ∨ B) ∧ (¬A ∨ C)`

Onde:
- `∨` significa **OU**.
- `∧` significa **E**.
- `¬` significa **NÃO**.

Nesse exemplo, precisamos encontrar valores para A, B e C que tornem **todas as cláusulas verdadeiras ao mesmo tempo**.

Se existir pelo menos uma combinação válida, o resultado é **SAT**. Caso nenhuma combinação funcione, o resultado é **UNSAT**.

## 2. Diferença entre 2-SAT e 3-SAT

A principal diferença é a quantidade de literais permitidos em cada cláusula.

**2-SAT:** cada cláusula possui no máximo 2 literais.

`(A ∨ B) ∧ (¬A ∨ C)`

**3-SAT:** cada cláusula possui no máximo 3 literais.

`(A ∨ B ∨ C) ∧ (¬A ∨ B ∨ ¬C)`

Apesar da pequena diferença, o 2-SAT pode ser resolvido em tempo polinomial, enquanto o 3-SAT é um problema NP-completo.

## 3. Como os algoritmos funcionam?

### 2-SAT — Kosaraju

O algoritmo transforma as cláusulas em um **grafo de implicações**.

Por exemplo, a cláusula:

`(A ∨ B)`

Pode ser representada por duas implicações:

- Se A for falso, B precisa ser verdadeiro.
- Se B for falso, A precisa ser verdadeiro.

Depois, Kosaraju identifica as **componentes fortemente conexas** do grafo.

Se uma variável e sua negação estiverem na mesma componente, a expressão é UNSAT. Caso contrário, é SAT.

**Complexidade:** `O(n + m)`, onde `n` é o número de variáveis e `m` é o número de cláusulas.

### 3-SAT — DPLL

O DPLL utiliza uma estratégia de busca com *backtracking*.

Basicamente:

1. Analisa as cláusulas e simplifica o que for possível.
2. Escolhe uma variável e atribui verdadeiro ou falso.
3. Verifica as consequências dessa escolha.
4. Se encontrar uma contradição, volta e tenta outra possibilidade.
5. Continua até encontrar uma solução ou provar que nenhuma existe.

O DPLL pode precisar explorar uma quantidade exponencial de possibilidades no pior caso.

## 4. Como funcionam as entradas?

Vamos utilizar arquivos `.cnf`, seguindo o formato DIMACS CNF.

Exemplo de entrada 2-SAT:

```
c Exemplo de entrada
p cnf 3 3
1 2 0
-1 3 0
-2 -3 0
```

Nesse formato:

- `c` indica um comentário.
- `p cnf 3 3` significa 3 variáveis e 3 cláusulas.
- Números positivos representam variáveis.
- Números negativos representam negações.
- `0` indica o final de uma cláusula.

O exemplo representa:

`(A ∨ B) ∧ (¬A ∨ C) ∧ (¬B ∨ ¬C)`

O algoritmo recebe esse arquivo e responde **SAT** ou **UNSAT**.

## 5. O que vamos desenvolver?

O projeto exige quatro implementações:

| Problema | Algoritmo | Linguagem |
|---|---|---|
| 2-SAT | Kosaraju | C |
| 2-SAT | Kosaraju | Python |
| 3-SAT | DPLL | C |
| 3-SAT | DPLL | Python |

Além disso, precisamos:

- Criar entradas de diferentes tamanhos.
- Testar se os algoritmos estão retornando resultados corretos.
- Medir o tempo de execução.
- Comparar o desempenho entre C e Python.
- Comparar os resultados experimentais com as complexidades teóricas.
- Gerar gráficos e elaborar um relatório.