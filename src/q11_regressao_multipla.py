"""Questão 11 — Regressão múltipla (cap. 10). Painel unidade x trimestre (288)."""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor

from util import COR, carregar, registrar, salvar_figura, salvar_tabela

VERDADEIROS = {"servicos": 0.50, "patch": -0.08, "treino": -0.20, "soc": -1.40, "trimestre": 0.15}
FORMULA = "n_ataques ~ servicos + patch + treino + soc + trimestre"


def tabela_coef(m):
    ic = m.conf_int()
    return pd.DataFrame({"coeficiente": m.params, "erro_padrao": m.bse, "t": m.tvalues,
                         "p_valor": m.pvalues, "ic95_inf": ic[0], "ic95_sup": ic[1]})


def preparar(pn):
    pn = pn.copy()
    pn["tri_ano"] = (pn.trimestre - 1) % 4 + 1
    for k in (2, 3, 4):
        pn[f"Q{k}"] = (pn.tri_ano == k).astype(int)
    pn["campanha"] = (pn.trimestre == 10).astype(int)  # abr-jun/2025 contém t = 28
    return pn


def ajustar(pn):
    """Modelo usado na Q14 (o mesmo da Q11-a)."""
    return smf.ols(FORMULA, data=pn).fit()


def rodar(semente: int):
    pn = preparar(carregar()["painel_trimestral"])

    # a, b) modelo principal
    m = ajustar(pn)
    tab = tabela_coef(m)
    salvar_tabela(tab.round(4).reset_index().rename(columns={"index": "termo"}), "q11a_coeficientes")

    # c) comparação com os verdadeiros
    comp = tab.loc[list(VERDADEIROS)].copy()
    comp["verdadeiro"] = pd.Series(VERDADEIROS)
    comp["contem"] = (comp.ic95_inf <= comp.verdadeiro) & (comp.verdadeiro <= comp.ic95_sup)
    comp["z_vs_verdadeiro"] = (comp.coeficiente - comp.verdadeiro) / comp.erro_padrao
    salvar_tabela(comp.round(4).reset_index().rename(columns={"index": "termo"}), "q11c_estimado_vs_verdadeiro")
    p_todos_5 = 0.95 ** 5

    # d) sazonalidade e campanha
    md = smf.ols(FORMULA + " + Q2 + Q3 + Q4 + campanha", data=pn).fit()
    tabd = tabela_coef(md)
    salvar_tabela(tabd.round(4).reset_index().rename(columns={"index": "termo"}), "q11d_coeficientes_sazonal")
    f_parcial = md.compare_f_test(m)  # (F, p, gl)
    S = [0.90, 0.85, 1.10, 1.10, 1.00, 0.95, 0.90, 0.95, 1.00, 1.05, 1.15, 1.05]
    s_tri = [np.mean(S[3 * k:3 * k + 3]) for k in range(4)]
    lam_medio = pn.n_ataques.mean()

    # e) VIF e resíduos
    X = sm.add_constant(pn[["servicos", "patch", "treino", "soc", "trimestre"]])
    vif = {c: float(variance_inflation_factor(X.values, i)) for i, c in enumerate(X.columns) if c != "const"}
    bp = het_breuschpagan(m.resid, m.model.exog)
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.6))
    ax[0].scatter(m.fittedvalues, m.resid, s=8, alpha=0.6, color=COR["azul"])
    ax[0].axhline(0, color=COR["vermelho"], lw=1)
    # envelope de +-2 desvios Poisson: 2*sqrt(ajustado)
    g = np.linspace(max(m.fittedvalues.min(), 0.1), m.fittedvalues.max(), 50)
    ax[0].plot(g, 2 * np.sqrt(g), "--", color=COR["cinza"], lw=1, label="±2·√ajustado (Poisson)")
    ax[0].plot(g, -2 * np.sqrt(g), "--", color=COR["cinza"], lw=1)
    ax[0].set_xlabel("n_ataques ajustado")
    ax[0].set_ylabel("Resíduo")
    ax[0].set_title("Q11-e  Resíduos × ajustados")
    ax[0].legend(fontsize=8)
    (osm, osr), (sl, it, r) = stats.probplot(m.resid, dist="norm")
    ax[1].plot(osm, osr, "o", ms=3, color=COR["azul"], alpha=0.7)
    ax[1].plot(osm, sl * osm + it, color=COR["vermelho"], lw=1)
    ax[1].set_title("Q-Q dos resíduos")
    ax[1].set_xlabel("Quantis teóricos")
    ax[1].set_ylabel("Resíduos")
    salvar_figura(fig, "q11e_residuos")
    # variância dos resíduos por faixa de ajustado
    faixa = pd.qcut(m.fittedvalues, 4, labels=["1º quartil", "2º", "3º", "4º"])
    var_faixa = m.resid.groupby(faixa, observed=True).var()
    aj_faixa = m.fittedvalues.groupby(faixa, observed=True).mean()

    # f) sobreajuste com 5 ruídos
    rng = np.random.default_rng([semente, 11])
    for k in range(1, 6):
        pn[f"ruido{k}"] = rng.standard_normal(len(pn))
    tr, te = pn[pn.trimestre <= 8], pn[pn.trimestre >= 9]
    res_f = {}
    for nome, f in [("sem_ruido", FORMULA), ("com_ruido", FORMULA + " + " + " + ".join(f"ruido{k}" for k in range(1, 6)))]:
        mf = smf.ols(f, data=tr).fit()
        prev = mf.predict(te)
        res_f[nome] = {"r2_treino": mf.rsquared, "r2aj_treino": mf.rsquared_adj,
                       "rmse_treino": float(np.sqrt(mf.mse_resid * (len(tr) - len(mf.params)) / len(tr))),
                       "rmse_teste": float(np.sqrt(((te.n_ataques - prev) ** 2).mean())),
                       "mae_teste": float((te.n_ataques - prev).abs().mean())}

    registrar("q11", {
        "a": tab.round(5).reset_index().rename(columns={"index": "termo"}),
        "b": {"F": m.fvalue, "F_p": m.f_pvalue, "gl1": int(m.df_model), "gl2": int(m.df_resid),
              "r2": m.rsquared, "r2aj": m.rsquared_adj, "s": float(np.sqrt(m.mse_resid)), "n": int(m.nobs)},
        "c": comp.round(5).reset_index().rename(columns={"index": "termo"}), "n_contem": int(comp.contem.sum()),
        "p_todos_5": p_todos_5,
        "d": {"coef": tabd.round(5).reset_index().rename(columns={"index": "termo"}),
              "r2": md.rsquared, "r2aj": md.rsquared_adj, "F_parcial": float(f_parcial[0]),
              "F_parcial_p": float(f_parcial[1]), "s_trimestral_programado": s_tri, "lambda_medio": lam_medio},
        "e": {"vif": vif, "bp_p": float(bp[1]), "bp_stat": float(bp[0]),
              "var_por_faixa": var_faixa.round(3), "ajustado_por_faixa": aj_faixa.round(3)},
        "f": res_f})


if __name__ == "__main__":
    rodar(202604)
