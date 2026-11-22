
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


RAIZ = Path(__file__).resolve().parent.parent
CSV_BENCH = RAIZ / "resultados" / "benchmark.csv"
DIR_GRAFICOS = RAIZ / "resultados" / "graficos"
ARQ_TABELAS = RAIZ / "resultados" / "tabelas_resumo.md"
ARQ_AMBIENTE = RAIZ / "resultados" / "ambiente.json"

COR_C = "#1f77b4"
COR_PY = "#ff7f0e"
COR_TEORICO = "#2ca02c"
COR_LIMITE = "#d62728"

plt.rcParams.update({
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.titleweight": "bold",
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linestyle": "--",
})


def carregar_dados():
    df = pd.read_csv(CSV_BENCH)
    df["n_mais_m"] = df["variaveis"] + df["clausulas"]
    return df


def grafico_01_contraste_p_np(df):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.2))

    d2 = df[(df["problema"] == "2-SAT") & (df["caso"] == "medio") & (df["status"] == "OK")]
    d3 = df[(df["problema"] == "3-SAT") & (df["caso"] == "medio")]

    for ling, cor, marc in (("C", COR_C, "o"), ("Python", COR_PY, "s")):
        s2 = d2[d2["linguagem"] == ling].sort_values("variaveis")
        ax1.errorbar(
            s2["variaveis"], s2["media_ms"], yerr=s2["desvio_ms"],
            label=f"2-SAT ({ling})", color=cor, marker=marc, capsize=3, linewidth=2
        )

    ax1.set_title("2-SAT (Classe P) — Escala Linear até n = 6.400")
    ax1.set_xlabel("Número de variáveis (n)  [m = 3n]")
    ax1.set_ylabel("Tempo médio (ms)")
    ax1.legend()

    for ling, cor, marc in (("C", COR_C, "o"), ("Python", COR_PY, "s")):
        s3_ok = d3[(d3["linguagem"] == ling) & (d3["status"] == "OK")].sort_values("variaveis")
        ax2.errorbar(
            s3_ok["variaveis"], s3_ok["media_ms"] / 1000.0, yerr=s3_ok["desvio_ms"] / 1000.0,
            label=f"3-SAT ({ling})", color=cor, marker=marc, capsize=3, linewidth=2
        )
        s3_to = d3[(d3["linguagem"] == ling) & (d3["status"] == "TIMEOUT")]
        if not s3_to.empty:
            n_to = int(s3_to["variaveis"].iloc[0])
            ax2.scatter([n_to], [60.0], color=COR_LIMITE, marker="X", s=110, zorder=5,
                        label=f"Timeout >60s ({ling}, n={n_to})")

    ax2.axhline(60.0, color=COR_LIMITE, linestyle=":", linewidth=1.8, label="Limite de inviabilidade (60 s)")
    ax2.set_yscale("log")
    ax2.set_title("3-SAT (NP-completo) — Explosão Exponencial até n = 160")
    ax2.set_xlabel("Número de variáveis (n)  [m ≈ 4,26n]")
    ax2.set_ylabel("Tempo médio (s) — escala log")
    ax2.legend(fontsize=8.5)

    fig.suptitle("Contraste P × NP: 2-SAT (Kosaraju) vs. 3-SAT (DPLL)", fontsize=13, fontweight="bold")
    fig.tight_layout()
    fig.savefig(DIR_GRAFICOS / "01_2sat_vs_3sat.png")
    plt.close(fig)


def grafico_02_2sat_teorico_medido(df):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.2))
    d2 = df[(df["problema"] == "2-SAT") & (df["caso"] == "medio") & (df["status"] == "OK")]

    for ling, cor, marc in (("C", COR_C, "o"), ("Python", COR_PY, "s")):
        s = d2[d2["linguagem"] == ling].sort_values("n_mais_m")
        x = s["n_mais_m"].to_numpy()
        y = s["media_ms"].to_numpy()

        ax1.loglog(x, y, marker=marc, color=cor, linewidth=2, label=f"Medido ({ling})")

        const_ref = y[-1] / x[-1]
        ax1.loglog(x, const_ref * x, linestyle="--", color=cor, alpha=0.55,
                   label=f"Ref. O(n + m) ({ling})")

        razao_ns = (y * 1e6) / x
        ax2.plot(x, razao_ns, marker=marc, color=cor, linewidth=2, label=f"T(n)/(n+m) — {ling}")

    ax1.set_title("2-SAT: Curva Medida vs. Teórica O(n + m) [Log-Log]")
    ax1.set_xlabel("Tamanho da entrada (n + m) — escala log")
    ax1.set_ylabel("Tempo médio (ms) — escala log")
    ax1.legend(fontsize=8.5)

    ax2.set_xscale("log")
    ax2.set_yscale("log")
    ax2.set_title("2-SAT: Estabilidade da Razão T(n) / (n + m)")
    ax2.set_xlabel("Tamanho da entrada (n + m) — escala log")
    ax2.set_ylabel("Tempo por unidade [ns / (n + m)] — escala log")
    ax2.legend()

    fig.suptitle("Validação Assintótica do 2-SAT — Complexidade Teórica Θ(n + m)", fontsize=13, fontweight="bold")
    fig.tight_layout()
    fig.savefig(DIR_GRAFICOS / "02_2sat_teorico_vs_medido.png")
    plt.close(fig)


def grafico_03_3sat_teorico_medido(df):
    fig, ax = plt.subplots(figsize=(9.5, 5.5))
    d3 = df[(df["problema"] == "3-SAT") & (df["caso"] == "medio")]

    for ling, cor, marc in (("C", COR_C, "o"), ("Python", COR_PY, "s")):
        s_ok = d3[(d3["linguagem"] == ling) & (d3["status"] == "OK")].sort_values("variaveis")
        s_unsat = s_ok[s_ok["resultado"] == "UNSAT"]
        s_sat = s_ok[s_ok["resultado"] == "SAT"]

        ax.plot(s_ok["variaveis"], s_ok["media_ms"], color=cor, alpha=0.35, linewidth=1.2)
        ax.scatter(s_unsat["variaveis"], s_unsat["media_ms"], color=cor, marker=marc, s=55,
                   label=f"{ling} — UNSAT", zorder=4)
        ax.scatter(s_sat["variaveis"], s_sat["media_ms"], facecolors="none", edgecolors=cor,
                   marker=marc, s=55, linewidths=1.6, label=f"{ling} — SAT", zorder=4)

        fit_df = s_unsat[s_unsat["variaveis"] >= 42]
        if len(fit_df) >= 3:
            x_fit = fit_df["variaveis"].to_numpy()
            y_fit = fit_df["media_ms"].to_numpy()
            b, a = np.polyfit(x_fit, np.log(y_fit), 1)
            base = np.exp(b)
            r2 = np.corrcoef(x_fit, np.log(y_fit))[0, 1] ** 2
            x_line = np.linspace(x_fit.min(), x_fit.max(), 100)
            ax.plot(x_line, np.exp(a + b * x_line), linestyle="--", color=cor, linewidth=1.8,
                    label=f"Ajuste {ling} UNSAT: c·{base:.3f}^n (R²={r2:.3f})")

        s_to = d3[(d3["linguagem"] == ling) & (d3["status"] == "TIMEOUT")]
        if not s_to.empty:
            n_to = int(s_to["variaveis"].iloc[0])
            ax.scatter([n_to], [60000.0], color=COR_LIMITE, marker="X", s=120, zorder=6,
                       label=f"Timeout >60s ({ling}, n={n_to})")

    ax.axhline(60000.0, color=COR_LIMITE, linestyle=":", linewidth=1.8, label="Limite 60 s (60.000 ms)")
    ax.set_yscale("log")
    ax.set_title("3-SAT (Transição de Fase α ≈ 4,26): Curva Medida vs. Ajuste Exponencial")
    ax.set_xlabel("Número de variáveis (n)")
    ax.set_ylabel("Tempo médio (ms) — escala log")
    ax.legend(fontsize=8.2, ncol=2)

    fig.tight_layout()
    fig.savefig(DIR_GRAFICOS / "03_3sat_teorico_vs_medido.png")
    plt.close(fig)


def grafico_04_comparacao_linguagens(df):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.2))

    for ax, prob, titulo in (
        (ax1, "2-SAT", "2-SAT (Caso Médio): Speedup C sobre Python"),
        (ax2, "3-SAT", "3-SAT (Caso Médio): Speedup C sobre Python"),
    ):
        sub = df[(df["problema"] == prob) & (df["caso"] == "medio") & (df["status"] == "OK")]
        piv = sub.pivot(index="variaveis", columns="linguagem", values="media_ms").dropna()
        speedup = piv["Python"] / piv["C"]
        media_sp = speedup.mean()

        x_pos = np.arange(len(speedup))
        barras = ax.bar(x_pos, speedup.to_numpy(), color=COR_C, alpha=0.85, edgecolor="black", linewidth=0.6)
        ax.axhline(media_sp, color=COR_LIMITE, linestyle="--", linewidth=1.8,
                   label=f"Speedup médio = {media_sp:.1f}x")

        for barra, val in zip(barras, speedup.to_numpy()):
            ax.text(barra.get_x() + barra.get_width() / 2.0, val + 1.0, f"{val:.1f}x",
                    ha="center", va="bottom", fontsize=7.5, rotation=45 if len(speedup) > 10 else 0)

        ax.set_xticks(x_pos)
        ax.set_xticklabels([str(n) for n in speedup.index], rotation=45 if len(speedup) > 10 else 0)
        ax.set_xlabel("Número de variáveis (n)")
        ax.set_ylabel("Razão de tempo (Python / C)")
        ax.set_title(titulo)
        ax.set_ylim(0, speedup.max() * 1.18)
        ax.legend()

    versao_python = "3"
    if ARQ_AMBIENTE.is_file():
        with ARQ_AMBIENTE.open(encoding="utf-8") as arquivo:
            ambiente = json.load(arquivo)
            versao_python = ambiente.get("python_versao", "3")

    fig.suptitle(
        f"Comparação entre Linguagens: C (-O2) vs. Python {versao_python}",
        fontsize=13,
        fontweight="bold"
    )
    fig.tight_layout()
    fig.savefig(DIR_GRAFICOS / "04_comparacao_linguagens.png")
    plt.close(fig)


def grafico_05_casos_forcados(df):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.2))

    estilos = {
        ("melhor", "C"): ("#2ca02c", "o", "-"),
        ("medio", "C"): (COR_C, "s", "-"),
        ("pior", "C"): (COR_LIMITE, "^", "-"),
        ("melhor", "Python"): ("#98df8a", "o", "--"),
        ("medio", "Python"): (COR_PY, "s", "--"),
        ("pior", "Python"): ("#ff9896", "^", "--"),
    }

    for ax, prob, limite_n, titulo in (
        (ax1, "2-SAT", 6400, "2-SAT: Melhor (cláusula vazia), Médio (m=3n) e Pior (m=6n)"),
        (ax2, "3-SAT", 50, "3-SAT: Melhor (sem backtrack), Médio (α=4,26) e Pior (α=5,0)"),
    ):
        sub = df[(df["problema"] == prob) & (df["status"] == "OK") & (df["variaveis"] <= limite_n)]
        for (caso, ling), (cor, marc, ls) in estilos.items():
            s = sub[(sub["caso"] == caso) & (sub["linguagem"] == ling)].sort_values("variaveis")
            if s.empty:
                continue
            y = np.maximum(s["media_ms"].to_numpy(), 1e-5)
            ax.plot(s["variaveis"], y, color=cor, marker=marc, linestyle=ls, linewidth=1.8,
                    label=f"{caso.capitalize()} ({ling})")

        ax.set_yscale("log")
        ax.set_title(titulo, fontsize=10.5)
        ax.set_xlabel("Número de variáveis (n)")
        ax.set_ylabel("Tempo médio (ms) — escala log")
        ax.legend(fontsize=8, ncol=2)

    fig.suptitle("Análise de Melhor Caso, Caso Médio e Pior Caso", fontsize=13, fontweight="bold")
    fig.tight_layout()
    fig.savefig(DIR_GRAFICOS / "05_casos_forcados.png")
    plt.close(fig)


def grafico_06_memoria(df):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.2))

    d2 = df[(df["problema"] == "2-SAT") & (df["caso"] == "medio") & (df["status"] == "OK")]
    for ling, cor, marc in (("C", COR_C, "o"), ("Python", COR_PY, "s")):
        s = d2[d2["linguagem"] == ling].sort_values("n_mais_m")
        x = s["n_mais_m"].to_numpy()
        y_kb = s["memoria_pico_bytes"].to_numpy() / 1024.0
        ax1.plot(x, y_kb, marker=marc, color=cor, linewidth=2, label=f"Medido ({ling})")
        ref = (y_kb[-1] / x[-1]) * x
        ax1.plot(x, ref, linestyle="--", color=cor, alpha=0.55, label=f"Ref. linear O(n+m) ({ling})")

    ax1.set_title("2-SAT: Memória Dinâmica vs. Espaço Teórico Θ(n + m)")
    ax1.set_xlabel("Tamanho da entrada (n + m)")
    ax1.set_ylabel("Pico de memória dinâmica (KB)")
    ax1.legend(fontsize=8.5)

    d3 = df[(df["problema"] == "3-SAT") & (df["caso"] == "medio") & (df["status"] == "OK")]
    for ling, cor, marc in (("C", COR_C, "o"), ("Python", COR_PY, "s")):
        s = d3[d3["linguagem"] == ling].sort_values("variaveis")
        x = s["variaveis"].to_numpy()
        y_kb = s["memoria_pico_bytes"].to_numpy() / 1024.0
        ax2.plot(x, y_kb, marker=marc, color=cor, linewidth=2, label=f"Medido ({ling})")
        coef = np.polyfit(x ** 2, y_kb, 1)[0]
        ax2.plot(x, coef * (x ** 2), linestyle="--", color=cor, alpha=0.55,
                 label=f"Ref. quadrática O(n²) ({ling})")

    ax2.set_title("3-SAT: Memória Dinâmica vs. Espaço Teórico O(n²)")
    ax2.set_xlabel("Número de variáveis (n)")
    ax2.set_ylabel("Pico de memória dinâmica (KB)")
    ax2.legend(fontsize=8.5)

    fig.suptitle("Análise de Complexidade de Espaço (Memória Dinâmica): C vs. Python", fontsize=13, fontweight="bold")
    fig.tight_layout()
    fig.savefig(DIR_GRAFICOS / "06_memoria_teorico_vs_medido.png")
    plt.close(fig)


def exportar_tabelas_markdown(df):
    linhas = ["# Tabelas Resumo — Benchmark 2-SAT vs. 3-SAT\n"]

    for prob in ("2-SAT", "3-SAT"):
        linhas.append(f"## {prob} — Caso Médio\n")
        linhas.append("| n | m | Resp. | C: Média ± DP (ms) | Python: Média ± DP (ms) | Speedup (Py/C) | Mem. C (B) | Mem. Py (B) |")
        linhas.append("|---:|---:|:---:|---:|---:|---:|---:|---:|")

        sub = df[(df["problema"] == prob) & (df["caso"] == "medio")]
        for n in sorted(sub["variaveis"].unique()):
            grupo = sub[sub["variaveis"] == n]
            m = int(grupo["clausulas"].iloc[0])
            row_c = grupo[grupo["linguagem"] == "C"]
            row_p = grupo[grupo["linguagem"] == "Python"]

            resp = ""
            if not row_c.empty and row_c["status"].iloc[0] == "OK":
                resp = str(row_c["resultado"].iloc[0])
                c_str = f"{row_c['media_ms'].iloc[0]:.4f} ± {row_c['desvio_ms'].iloc[0]:.4f}"
                mem_c = f"{int(row_c['memoria_pico_bytes'].iloc[0])}"
            else:
                c_str = "TIMEOUT (>60s)"
                mem_c = "-"

            if not row_p.empty and row_p["status"].iloc[0] == "OK":
                p_str = f"{row_p['media_ms'].iloc[0]:.4f} ± {row_p['desvio_ms'].iloc[0]:.4f}"
                mem_p = f"{int(row_p['memoria_pico_bytes'].iloc[0])}"
                sp_str = f"{row_p['media_ms'].iloc[0] / row_c['media_ms'].iloc[0]:.1f}x"
            elif not row_p.empty and row_p["status"].iloc[0] == "TIMEOUT":
                p_str = "TIMEOUT (>60s)"
                mem_p = "-"
                sp_str = "-"
            else:
                p_str = "-"
                mem_p = "-"
                sp_str = "-"

            linhas.append(f"| {n} | {m} | {resp} | {c_str} | {p_str} | {sp_str} | {mem_c} | {mem_p} |")
        linhas.append("")

    ARQ_TABELAS.write_text("\n".join(linhas), encoding="utf-8")


def main():
    if not CSV_BENCH.is_file():
        raise FileNotFoundError(f"Arquivo nao encontrado: {CSV_BENCH}")

    DIR_GRAFICOS.mkdir(parents=True, exist_ok=True)
    df = carregar_dados()

    grafico_01_contraste_p_np(df)
    grafico_02_2sat_teorico_medido(df)
    grafico_03_3sat_teorico_medido(df)
    grafico_04_comparacao_linguagens(df)
    grafico_05_casos_forcados(df)
    grafico_06_memoria(df)
    exportar_tabelas_markdown(df)

    print("Graficos gerados em:", DIR_GRAFICOS)
    for arq in sorted(DIR_GRAFICOS.glob("*.png")):
        print("  -", arq.name)
    print("Tabelas resumo salvas em:", ARQ_TABELAS)


if __name__ == "__main__":
    main()
