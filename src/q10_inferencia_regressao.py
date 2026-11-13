"""Questão 10 — Inferência na regressão (cap. 9)."""
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

from util import carregar, registrar, salvar_tabela


def rodar():
    pe = carregar()["perdas"].copy()
    pe["ln_perda"] = np.log(pe.perda_rs)
    pe["tempo"] = pe.tempo_deteccao_h
    m = smf.ols("ln_perda ~ tempo", data=pe).fit()

    # a) ANOVA
    n = int(m.nobs)
    sqt = float(((pe.ln_perda - pe.ln_perda.mean()) ** 2).sum())
    sqres = float(m.ssr)
    sqreg = sqt - sqres
    qmreg, qmres = sqreg / 1, sqres / (n - 2)
    F = qmreg / qmres
    anova = pd.DataFrame({"fonte": ["Regressão", "Resíduos", "Total"],
                          "SQ": [sqreg, sqres, sqt], "gl": [1, n - 2, n - 1],
                          "QM": [qmreg, qmres, np.nan], "F": [F, np.nan, np.nan],
                          "p_valor": [1 - stats.f.cdf(F, 1, n - 2), np.nan, np.nan]})
    salvar_tabela(anova.round(4), "q10a_anova")
    t_b1 = m.tvalues["tempo"]

    # b) IC de beta1
    li, ls = m.conf_int().loc["tempo"]

    # c) IC da média e intervalo de previsão em tempo = 24 h
    pr = m.get_prediction(pd.DataFrame({"tempo": [24.0]})).summary_frame(alpha=0.05)
    c = {k: float(pr[k].iloc[0]) for k in ["mean", "mean_ci_lower", "mean_ci_upper", "obs_ci_lower", "obs_ci_upper"]}
    c_reais = {k: float(np.exp(v)) for k, v in c.items()}
    s2 = qmres
    c["fator_smearing"] = float(np.exp(s2 / 2))
    c["media_reais_lognormal"] = float(np.exp(c["mean"] + s2 / 2))

    # d) com dummies de tipo (base: Phishing)
    md = smf.ols("ln_perda ~ tempo + C(tipo, Treatment(reference='Phishing'))", data=pe).fit()
    lid, lsd = md.conf_int().loc["tempo"]
    coefs_tipo = md.params.drop(["Intercept", "tempo"])
    coefs_tipo.index = [i.split("[T.")[1].rstrip("]") for i in coefs_tipo.index]
    # razão de medianas implicada x programada
    prog = {"Força bruta": 10_000 / 15_000, "Malware": 30_000 / 15_000,
            "Exploração de vulnerabilidade": 45_000 / 15_000, "DDoS": 25_000 / 15_000,
            "Ransomware": 150_000 / 15_000}
    tipos = pd.DataFrame({"coef": coefs_tipo, "razao_medianas_estimada": np.exp(coefs_tipo),
                          "razao_programada": pd.Series(prog)})
    salvar_tabela(tipos.round(4).reset_index().rename(columns={"index": "tipo"}), "q10d_dummies_tipo")
    mediana_phishing = float(np.exp(md.params["Intercept"]))

    registrar("q10", {
        "anova": anova.round(4), "F": F, "t_b1": t_b1, "t2": t_b1 ** 2, "n": n,
        "b1": m.params["tempo"], "ep_b1": m.bse["tempo"], "ic_b1": [li, ls], "contem_002": bool(li <= 0.02 <= ls),
        "t_crit": stats.t.ppf(0.975, n - 2),
        "c_ln": c, "c_reais": c_reais,
        "d": {"r2_simples": m.rsquared, "r2_dummies": md.rsquared, "r2aj_dummies": md.rsquared_adj,
              "b1": md.params["tempo"], "ep_b1": md.bse["tempo"], "ic_b1": [lid, lsd],
              "contem_002": bool(lid <= 0.02 <= lsd), "s": float(np.sqrt(md.mse_resid)),
              "tipos": tipos.round(4).reset_index().rename(columns={"index": "tipo"}),
              "mediana_phishing_tempo0": mediana_phishing,
              "largura_ic_simples": ls - li, "largura_ic_dummies": lsd - lid}})


if __name__ == "__main__":
    rodar()
