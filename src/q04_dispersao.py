"""Questão 4 — Dispersão, formato e associação (cap. 2)."""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from util import COR, TIPOS, TIPO_CURTO, carregar, registrar, salvar_figura, salvar_tabela


def rodar():
    b = carregar()
    pe, pn, se = b["perdas"], b["painel_trimestral"], b["serie_mensal"]

    # a) dispersão por tipo
    linhas, outl = [], []
    for t in TIPOS:
        v = pe.loc[pe.tipo == t, "perda_rs"].to_numpy()
        q1, q3 = np.percentile(v, [25, 75])
        aiq = q3 - q1
        lim_sup = q3 + 1.5 * aiq
        n_out = int((v > lim_sup).sum() + (v < q1 - 1.5 * aiq).sum())
        linhas.append({"tipo": t, "n": len(v), "media": v.mean(), "desvio_padrao": v.std(ddof=1),
                       "cv": v.std(ddof=1) / v.mean(), "q1": q1, "mediana": np.median(v), "q3": q3,
                       "aiq": aiq, "limite_outlier_sup": lim_sup, "n_outliers": n_out,
                       "pct_outliers": n_out / len(v), "maximo": v.max(),
                       "soma_outliers_pct": v[v > lim_sup].sum() / v.sum()})
    disp = pd.DataFrame(linhas)
    salvar_tabela(disp.round(4), "q04a_dispersao_por_tipo")

    # b) box-plots (escala log para que todos os tipos fiquem legíveis)
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
    dados = [pe.loc[pe.tipo == t, "perda_rs"] / 1e3 for t in TIPOS]
    rot = [TIPO_CURTO[t] for t in TIPOS]
    for a, log in zip(ax, [False, True]):
        a.boxplot(dados, whis=1.5, flierprops=dict(marker="o", ms=2.5, mfc=COR["vermelho"], mec="none", alpha=0.6),
                  medianprops=dict(color=COR["laranja"]))
        a.set_xticks(range(1, 7), rot, rotation=20)
        a.set_ylabel("Perda (R$ mil)")
        if log:
            a.set_yscale("log")
    ax[0].set_title("Q4-b  Box-plots da perda por tipo (escala linear)")
    ax[1].set_title("Mesmos dados em escala logarítmica")
    salvar_figura(fig, "q04b_boxplots")

    # c) assimetria e curtose (curtose de Pearson; normal = 3)
    x = pe.perda_rs.to_numpy()
    lx = np.log(x)
    forma = pd.DataFrame({
        "variavel": ["perda_rs", "ln(perda)"],
        "assimetria": [stats.skew(x, bias=False), stats.skew(lx, bias=False)],
        "curtose": [stats.kurtosis(x, fisher=False, bias=False), stats.kurtosis(lx, fisher=False, bias=False)],
    })
    salvar_tabela(forma.round(4), "q04c_forma")

    # d) covariâncias e correlações no painel
    cols = ["n_ataques", "perda_total", "servicos", "patch", "treino", "soc"]
    cov = pn[cols].cov()
    cor = pn[cols].corr()
    salvar_tabela(cov.round(3), "q04d_covariancias", index=True)
    salvar_tabela(cor.round(3), "q04d_correlacoes", index=True)
    fig, ax = plt.subplots(figsize=(5.4, 4.4))
    im = ax.imshow(cor, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(6), cols, rotation=35, ha="right")
    ax.set_yticks(range(6), cols)
    ax.grid(False)
    for i in range(6):
        for j in range(6):
            ax.text(j, i, f"{cor.iloc[i, j]:.2f}".replace(".", ","), ha="center", va="center", fontsize=8,
                    color="white" if abs(cor.iloc[i, j]) > 0.6 else "black")
    fig.colorbar(im, ax=ax, shrink=0.8)
    ax.set_title("Q4-d  Correlações no painel trimestral")
    salvar_figura(fig, "q04d_correlacoes")

    # e) VaR histórico 95% da perda mensal total
    m = se.perda_total.to_numpy()
    var95 = float(np.percentile(m, 95))  # interpolação linear entre as estatísticas de ordem
    ordenado = np.sort(m)
    registrar("q04", {"dispersao": disp.round(4), "forma": forma.round(4),
                      "cor": cor.round(3), "cov": cov.round(2),
                      "var95_mensal": var95, "media_mensal": float(m.mean()),
                      "maior_mes": float(ordenado[-1]), "segundo_maior": float(ordenado[-2]),
                      "terceiro_maior": float(ordenado[-3]),
                      "posicao_quantil": 0.95 * (len(m) - 1) + 1,
                      "mes_maior": se.loc[se.perda_total.idxmax(), "mes_ref"],
                      "var95_sem_maior": float(np.percentile(ordenado[:-1], 95))})


if __name__ == "__main__":
    rodar()
