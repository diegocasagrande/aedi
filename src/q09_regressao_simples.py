"""Questão 9 — Correlação e regressão simples (cap. 8)."""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

from util import COR, TIPOS, carregar, registrar, salvar_figura


def teste_rho(x, y):
    r = np.corrcoef(x, y)[0, 1]
    n = len(x)
    t = r * np.sqrt(n - 2) / np.sqrt(1 - r ** 2)
    return r, t, 2 * (1 - stats.t.cdf(abs(t), n - 2))


def rodar():
    b = carregar()
    pe = b["perdas"].copy()
    pe["ln_perda"] = np.log(pe.perda_rs)

    r1, t1, p1 = teste_rho(pe.tempo_deteccao_h, pe.perda_rs)
    r2, t2, p2 = teste_rho(pe.tempo_deteccao_h, pe.ln_perda)
    sp = stats.spearmanr(pe.tempo_deteccao_h, pe.perda_rs)

    m = smf.ols("ln_perda ~ tempo_deteccao_h", data=pe).fit()
    b0, b1 = m.params
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.6))
    ax[0].scatter(pe.tempo_deteccao_h, pe.perda_rs / 1e3, s=5, alpha=0.4, color=COR["azul"])
    ax[0].set_title(f"Q9-a  perda × tempo (r = {r1:.3f})".replace(".", ","))
    ax[0].set_xlabel("Tempo até a detecção (h)")
    ax[0].set_ylabel("Perda (R$ mil)")
    ax[1].scatter(pe.tempo_deteccao_h, pe.ln_perda, s=5, alpha=0.4, color=COR["azul"])
    g = np.linspace(0, pe.tempo_deteccao_h.max(), 50)
    ax[1].plot(g, b0 + b1 * g, color=COR["vermelho"], lw=1.5,
               label=f"ln(perda) = {b0:.3f} + {b1:.4f}·tempo".replace(".", ","))
    ax[1].set_title(f"ln(perda) × tempo (r = {r2:.3f})".replace(".", ","))
    ax[1].set_xlabel("Tempo até a detecção (h)")
    ax[1].set_ylabel("ln(perda)")
    ax[1].legend(fontsize=8)
    salvar_figura(fig, "q09_dispersao")

    # d) pista do viés de seleção: tempo e tipo ficam associados entre os materializados
    at = b["ataques"]
    tempo_por_tipo_todos = at.groupby("tipo").tempo_deteccao_h.mean().reindex(TIPOS)
    tempo_por_tipo_mat = pe.groupby("tipo").tempo_deteccao_h.mean().reindex(TIPOS)
    sel = pd.DataFrame({"todos_ataques": tempo_por_tipo_todos, "so_materializados": tempo_por_tipo_mat})
    resid = m.resid
    fig, ax = plt.subplots(figsize=(5.5, 3.3))
    ax.scatter(m.fittedvalues, resid, s=5, alpha=0.4, color=COR["azul"])
    ax.axhline(0, color=COR["vermelho"], lw=1)
    ax.set_xlabel("ln(perda) ajustado")
    ax.set_ylabel("Resíduo")
    ax.set_title("Q9-d  Resíduos × ajustados")
    salvar_figura(fig, "q09d_residuos")
    bp = __import__("statsmodels.stats.diagnostic", fromlist=["het_breuschpagan"]).het_breuschpagan(resid, m.model.exog)

    registrar("q09", {
        "n": int(m.nobs), "r_perda": r1, "t_perda": t1, "p_perda": p1,
        "r_ln": r2, "t_ln": t2, "p_ln": p2, "spearman": sp.statistic,
        "b0": b0, "b1": b1, "ep_b1": m.bse.iloc[1], "pct_por_hora": 100 * (np.exp(b1) - 1),
        "r2": m.rsquared, "s": np.sqrt(m.mse_resid),
        "tempo_medio_por_tipo": sel.round(3).reset_index().rename(columns={"index": "tipo"}),
        "breusch_pagan_p": float(bp[1]), "jarque_bera_p": float(stats.jarque_bera(resid).pvalue),
        "durbin_watson": float(__import__("statsmodels.stats.stattools", fromlist=["durbin_watson"]).durbin_watson(resid)),
    })


if __name__ == "__main__":
    rodar()
