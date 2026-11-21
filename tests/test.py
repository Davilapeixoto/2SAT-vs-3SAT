import csv
import subprocess
import sys
from pathlib import Path


RAIZ = Path(__file__).resolve().parent.parent
DIR_DADOS = RAIZ / "dados"
ARQUIVO_GABARITO = DIR_DADOS / "gabarito.csv"
TIMEOUT_SEGUNDOS = 60


def localizar_binario(nome):
    candidatos = [RAIZ / nome, RAIZ / f"{nome}.exe"]
    for caminho in candidatos:
        if caminho.is_file():
            return str(caminho)
    return None


def executar(comando, arquivo_cnf):
    try:
        resultado = subprocess.run(
            [*comando, str(arquivo_cnf)],
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SEGUNDOS,
        )
    except subprocess.TimeoutExpired:
        return None, f"TIMEOUT (>{TIMEOUT_SEGUNDOS}s)"
    except OSError as erro:
        return None, f"ERRO_EXECUCAO ({erro})"

    saida = resultado.stdout.strip()
    if resultado.returncode != 0:
        detalhe = saida or resultado.stderr.strip() or f"codigo {resultado.returncode}"
        return None, f"ERRO ({detalhe})"

    return saida, None


def main():
    bin_2sat = localizar_binario("2sat")
    bin_3sat = localizar_binario("3sat")
    py_2sat = RAIZ / "algoritmos" / "python" / "2sat.py"
    py_3sat = RAIZ / "algoritmos" / "python" / "3sat.py"

    faltando = []
    if bin_2sat is None:
        faltando.append("binario C './2sat' (execute 'make' primeiro)")
    if bin_3sat is None:
        faltando.append("binario C './3sat' (execute 'make' primeiro)")
    if not py_2sat.is_file():
        faltando.append(str(py_2sat))
    if not py_3sat.is_file():
        faltando.append(str(py_3sat))
    if not ARQUIVO_GABARITO.is_file():
        faltando.append(str(ARQUIVO_GABARITO))

    if faltando:
        print("Erro: arquivos necessarios nao encontrados:")
        for item in faltando:
            print(f"  - {item}")
        sys.exit(1)

    implementacoes = {
        "2-SAT": {
            "C": [bin_2sat],
            "Python": [sys.executable, str(py_2sat)],
        },
        "3-SAT": {
            "C": [bin_3sat],
            "Python": [sys.executable, str(py_3sat)],
        },
    }

    total_casos = 0
    total_falhas = 0
    divergencias_linguagem = 0

    with open(ARQUIVO_GABARITO, "r", encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)

        for linha in leitor:
            nome_arquivo = linha["arquivo"].strip()
            problema = linha["problema"].strip()
            esperado = linha["esperado"].strip()
            caminho_cnf = DIR_DADOS / nome_arquivo

            if problema not in implementacoes:
                print(f"[ERRO] {nome_arquivo}: problema desconhecido '{problema}'")
                total_falhas += 1
                continue

            if not caminho_cnf.is_file():
                print(f"[ERRO] {nome_arquivo}: arquivo nao encontrado em {DIR_DADOS}")
                total_falhas += 1
                continue

            total_casos += 1
            respostas = {}
            falhou_caso = False

            for linguagem, comando in implementacoes[problema].items():
                saida, erro = executar(comando, caminho_cnf)
                respostas[linguagem] = saida if erro is None else erro
                if erro is not None or saida != esperado:
                    falhou_caso = True

            iguais = respostas["C"] == respostas["Python"]
            if not iguais:
                divergencias_linguagem += 1
                falhou_caso = True

            status = "FALHA" if falhou_caso else "OK"
            if falhou_caso:
                total_falhas += 1

            print(
                f"[{status:5}] {problema} | {nome_arquivo:<24} | "
                f"esperado={esperado:<5} | C={respostas['C']:<5} | Python={respostas['Python']}"
            )

    print("-" * 80)
    print(
        f"Resumo: {total_casos - total_falhas}/{total_casos} casos aprovados | "
        f"falhas={total_falhas} | divergencias C vs Python={divergencias_linguagem}"
    )

    if total_falhas > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()