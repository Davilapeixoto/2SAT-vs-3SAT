import csv
import json
import os
import platform
import statistics
import subprocess
import sys
from pathlib import Path


RAIZ = Path(__file__).resolve().parent.parent
DIR_BENCH = RAIZ / "dados" / "benchmark"
MANIFESTO = DIR_BENCH / "manifesto.csv"
DIR_RESULTADOS = RAIZ / "resultados"
CSV_SAIDA = DIR_RESULTADOS / "benchmark.csv"
JSON_AMBIENTE = DIR_RESULTADOS / "ambiente.json"

TIMEOUT_EXECUCAO_S = 60.0
REPETICOES_PADRAO = 20
REPETICOES_LENTO = 15
LIMIAR_LENTO_S = 2.0


def localizar_binario(nome):
    for candidato in (RAIZ / nome, RAIZ / f"{nome}.exe"):
        if candidato.is_file():
            return str(candidato)
    return None


def obter_cpu():
    try:
        with open("/proc/cpuinfo", "r", encoding="utf-8") as f:
            for linha in f:
                if "model name" in linha:
                    return linha.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or "desconhecido"


def obter_ram_gb():
    try:
        with open("/proc/meminfo", "r", encoding="utf-8") as f:
            for linha in f:
                if linha.startswith("MemTotal:"):
                    kb = int(linha.split()[1])
                    return round(kb / (1024 * 1024), 2)
    except (OSError, ValueError):
        pass
    return None


def obter_versao_gcc():
    try:
        res = subprocess.run(["gcc", "--version"], capture_output=True, text=True, timeout=5)
        if res.returncode == 0 and res.stdout:
            return res.stdout.splitlines()[0].strip()
    except OSError:
        pass
    return "desconhecido"


def coletar_ambiente():
    return {
        "sistema_operacional": platform.platform(),
        "arquitetura": platform.machine(),
        "cpu": obter_cpu(),
        "nucleos_logicos": os.cpu_count(),
        "ram_total_gb": obter_ram_gb(),
        "gcc_versao": obter_versao_gcc(),
        "flags_compilacao_c": "-std=c11 -O2 -Wall -Wextra -Wpedantic",
        "python_versao": sys.version.split()[0],
        "repeticoes_padrao": REPETICOES_PADRAO,
        "repeticoes_lento": REPETICOES_LENTO,
        "timeout_limite_s": TIMEOUT_EXECUCAO_S,
    }


def parse_saida_bench(stdout):
    dados = {}
    for linha in stdout.strip().splitlines():
        if ":" not in linha:
            continue
        chave, valor = linha.split(":", 1)
        dados[chave.strip()] = valor.strip()

    tempos_ns = [int(x) for x in dados["TEMPOS_NS"].split(",") if x]
    return {
        "resultado": dados["RESULTADO"],
        "tempos_ns": tempos_ns,
        "memoria_pico_bytes": int(dados["MEMORIA_PICO_BYTES"]),
        "memoria_rss_kb": int(dados["MEMORIA_RSS_KB"]),
    }


def rodar_bench(comando, caminho_cnf, repeticoes, timeout_s):
    try:
        res = subprocess.run(
            [*comando, str(caminho_cnf), "--bench", str(repeticoes)],
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
    except subprocess.TimeoutExpired:
        return None, "TIMEOUT"
    except OSError:
        return None, "ERRO"

    if res.returncode != 0:
        return None, "ERRO"

    try:
        return parse_saida_bench(res.stdout), "OK"
    except (KeyError, ValueError):
        return None, "ERRO"


def main():
    if not MANIFESTO.is_file():
        print("Manifesto nao encontrado. Execute primeiro: python3 scripts/gerar_entradas.py")
        sys.exit(1)

    bin_2sat = localizar_binario("2sat")
    bin_3sat = localizar_binario("3sat")
    py_2sat = RAIZ / "algoritmos" / "python" / "2sat.py"
    py_3sat = RAIZ / "algoritmos" / "python" / "3sat.py"

    if not bin_2sat or not bin_3sat:
        print("Binarios C nao encontrados. Execute 'make' primeiro.")
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

    DIR_RESULTADOS.mkdir(parents=True, exist_ok=True)
    ambiente = coletar_ambiente()
    with open(JSON_AMBIENTE, "w", encoding="utf-8") as f:
        json.dump(ambiente, f, indent=2, ensure_ascii=False)

    print("Ambiente registrado em", JSON_AMBIENTE)
    print(f"CPU: {ambiente['cpu']} | RAM: {ambiente['ram_total_gb']} GB | "
          f"GCC: {ambiente['gcc_versao']} | Python: {ambiente['python_versao']}")
    print("-" * 96)

    with open(MANIFESTO, "r", encoding="utf-8", newline="") as f:
        instancias = list(csv.DictReader(f))

    linhas_csv = []
    bloqueados = set()
    maior_n_viavel = {}

    for item in instancias:
        nome = item["arquivo"]
        problema = item["problema"]
        caso = item["caso"]
        n = int(item["variaveis"])
        m = int(item["clausulas"])
        caminho = DIR_BENCH / nome

        respostas_instancia = {}

        for linguagem in ("C", "Python"):
            chave_fluxo = (problema, caso, linguagem)
            if chave_fluxo in bloqueados:
                continue

            comando = implementacoes[problema][linguagem]

            sonda, status_sonda = rodar_bench(comando, caminho, 1, TIMEOUT_EXECUCAO_S)
            if status_sonda != "OK":
                bloqueados.add(chave_fluxo)
                print(f"[{status_sonda:7}] {problema} | {caso:<6} | {linguagem:<6} | n={n:<5} m={m:<6}")
                linhas_csv.append({
                    "problema": problema,
                    "caso": caso,
                    "arquivo": nome,
                    "variaveis": n,
                    "clausulas": m,
                    "linguagem": linguagem,
                    "resultado": "",
                    "status": status_sonda,
                    "repeticoes": 0,
                    "media_ms": "",
                    "desvio_ms": "",
                    "min_ms": "",
                    "max_ms": "",
                    "memoria_pico_bytes": "",
                    "memoria_rss_kb": "",
                })
                continue

            tempo_sonda_s = sonda["tempos_ns"][0] / 1e9
            reps = REPETICOES_LENTO if tempo_sonda_s >= LIMIAR_LENTO_S else REPETICOES_PADRAO
            timeout_lote = max(TIMEOUT_EXECUCAO_S, tempo_sonda_s * reps * 2.5 + 30.0)

            dados, status = rodar_bench(comando, caminho, reps, timeout_lote)
            if status != "OK":
                bloqueados.add(chave_fluxo)
                print(f"[{status:7}] {problema} | {caso:<6} | {linguagem:<6} | n={n:<5} m={m:<6}")
                continue

            tempos_ms = [t / 1e6 for t in dados["tempos_ns"]]
            media_ms = statistics.mean(tempos_ms)
            desvio_ms = statistics.stdev(tempos_ms) if len(tempos_ms) > 1 else 0.0
            min_ms = min(tempos_ms)
            max_ms = max(tempos_ms)

            respostas_instancia[linguagem] = dados["resultado"]
            anterior = maior_n_viavel.get(chave_fluxo, 0)
            if n > anterior:
                maior_n_viavel[chave_fluxo] = n

            print(
                f"[OK     ] {problema} | {caso:<6} | {linguagem:<6} | "
                f"n={n:<5} m={m:<6} | {dados['resultado']:<5} | "
                f"media={media_ms:9.4f} ms +- {desvio_ms:7.4f} ms | "
                f"mem={dados['memoria_pico_bytes']} B"
            )

            linhas_csv.append({
                "problema": problema,
                "caso": caso,
                "arquivo": nome,
                "variaveis": n,
                "clausulas": m,
                "linguagem": linguagem,
                "resultado": dados["resultado"],
                "status": "OK",
                "repeticoes": reps,
                "media_ms": f"{media_ms:.6f}",
                "desvio_ms": f"{desvio_ms:.6f}",
                "min_ms": f"{min_ms:.6f}",
                "max_ms": f"{max_ms:.6f}",
                "memoria_pico_bytes": dados["memoria_pico_bytes"],
                "memoria_rss_kb": dados["memoria_rss_kb"],
            })

        if "C" in respostas_instancia and "Python" in respostas_instancia:
            if respostas_instancia["C"] != respostas_instancia["Python"]:
                print(
                    f"[ALERTA ] Divergencia em {nome}: "
                    f"C={respostas_instancia['C']} vs Python={respostas_instancia['Python']}"
                )

    campos = [
        "problema", "caso", "arquivo", "variaveis", "clausulas", "linguagem",
        "resultado", "status", "repeticoes", "media_ms", "desvio_ms",
        "min_ms", "max_ms", "memoria_pico_bytes", "memoria_rss_kb",
    ]
    with open(CSV_SAIDA, "w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(linhas_csv)

    print("-" * 96)
    print("Resultados salvos em:", CSV_SAIDA)
    print("Maior n viavel (<= 60 s por execucao):")
    for (prob, caso, ling), max_n in sorted(maior_n_viavel.items()):
        print(f"  - {prob} ({caso:<6}) | {ling:<6}: n = {max_n}")


if __name__ == "__main__":
    main()