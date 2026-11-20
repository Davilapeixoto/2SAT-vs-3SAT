INT_MAX = 2147483647


class Clausula:
    def __init__(self):
        self.literais = [0, 0, 0]
        self.tamanho = 0


class FormulaCNF:
    def __init__(self):
        self.variaveis = 0
        self.quantidade = 0
        self.clausulas = []


def cnf_carregar(caminho, limite):
    formula = FormulaCNF()
    cabecalho = 0
    quantidade_lida = 0
    tamanho_atual = 0
    valido = 1

    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            for linha in arquivo:
                if valido == 0:
                    break

                p = linha.lstrip()
                if not p or p[0] == "c":
                    continue

                if cabecalho == 0:
                    partes = p.split()
                    if len(partes) < 4 or partes[0] != "p" or partes[1] != "cnf":
                        valido = 0
                        break
                    try:
                        n = int(partes[2])
                        m = int(partes[3])
                    except ValueError:
                        valido = 0
                        break

                    if n < 0 or m < 0 or n > INT_MAX // 2 or m > INT_MAX // 2:
                        valido = 0
                        break

                    formula.variaveis = n
                    formula.quantidade = m
                    formula.clausulas = [Clausula() for _ in range(m + 1)]
                    cabecalho = 1
                    continue

                for token in p.split():
                    try:
                        numero = int(token)
                    except ValueError:
                        valido = 0
                        break

                    if numero < -INT_MAX or numero > INT_MAX or quantidade_lida >= formula.quantidade:
                        valido = 0
                        break

                    if numero == 0:
                        formula.clausulas[quantidade_lida].tamanho = tamanho_atual
                        quantidade_lida += 1
                        tamanho_atual = 0
                    else:
                        if abs(numero) > formula.variaveis or tamanho_atual >= limite:
                            valido = 0
                            break
                        formula.clausulas[quantidade_lida].literais[tamanho_atual] = numero
                        tamanho_atual += 1
    except OSError:
        return None

    if valido == 0 or cabecalho == 0 or tamanho_atual != 0 or quantidade_lida != formula.quantidade:
        return None

    return formula