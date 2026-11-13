"""Questão 6 — Distribuições (caps. 4 e 5)."""
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

from util import COR, carregar, registrar, salvar_figura


def rodar():
    b = carregar()
    lam, un, at, pe = b["lambda"], b["unidades"], b["ataques"], b["perdas"]

    # a) unidade sem SOC: a de média mensal mediana entre as sem SOC (a mesma da Q2-b)
    med = lam.groupby("unidade").n_ataques.mean()
    sem = un.loc[un.soc == 0, "unidade"]
    ordem = med.loc[sem].sort_values()
    u = int(ordem.index[len(ordem) // 2])
    contagens = lam.loc[lam.unidade == u, "n_ataques"].to_numpy()
    lam_hat = contagens.mean()
    p_teor = 1 - stats.poisson.cdf(5, lam_hat)
    p_emp = (contagens >= 6).mean()
    dist = [(k, stats.poisson.pmf(k, lam_hat), (contagens == k).mean()) for k in range(0, contagens.max() + 2)]

    fig, ax = plt.subplots(figsize=(6, 3.4))
    ks = np.array([d[0] for d in dist])
    ax.bar(ks - 0.2, [d[2] for d in dist], width=0.4, color=COR["azul"], label="frequência observada (36 meses)")
    ax.bar(ks + 0.2, [d[1] for d in dist], width=0.4, color=COR["laranja"], label=f"Poisson(λ = {lam_hat:.2f})".replace(".", ","))
    ax.axvline(5.5, color=COR["cinza"], ls="--", lw=1)
    ax.set_xlabel("Ataques no mês")
    ax.set_ylabel("Proporção de meses")
    ax.set_title(f"Q6-a  Unidade {u} (sem SOC): contagem mensal × Poisson")
    ax.legend(fontsize=8)
    salvar_figura(fig, "q06a_poisson_unidade")

    # b) SOC e fora_expediente = 0: P(T > 8)
    at2 = at.merge(un[["unidade", "soc"]], on="unidade")
    t = at2.loc[(at2.soc == 1) & (at2.fora_expediente == 0), "tempo_deteccao_h"].to_numpy()
    p_teor_b = np.exp(-8 / 4)              # Exponencial com média programada de 4 h
    theta_hat = t.mean()
    p_teor_b_hat = np.exp(-8 / theta_hat)  # com a média estimada
    p_obs_b = (t > 8).mean()
    ep_b = np.sqrt(p_teor_b * (1 - p_teor_b) / len(t))

    # c) Q-Q de ln(perda): ransomware e phishing
    fig, ax = plt.subplots(1, 2, figsize=(9, 3.6))
    resc = {}
    for a, tipo in zip(ax, ["Ransomware", "Phishing"]):
        lx = np.log(pe.loc[pe.tipo == tipo, "perda_rs"].to_numpy())
        (osm, osr), (slope, inter, r) = stats.probplot(lx, dist="norm")
        a.plot(osm, osr, "o", ms=3, color=COR["azul"], alpha=0.7)
        a.plot(osm, slope * osm + inter, color=COR["vermelho"], lw=1)
        a.set_title(f"Q6-c  Q-Q de ln(perda) — {tipo} (n = {len(lx)})")
        a.set_xlabel("Quantis teóricos da Normal padrão")
        a.set_ylabel("Quantis de ln(perda)")
        sw = stats.shapiro(lx)
        z_max = (lx.max() - lx.mean()) / lx.std(ddof=1)
        resc[tipo] = {"n": len(lx), "media_ln": lx.mean(), "dp_ln": lx.std(ddof=1), "r_qq": r,
                      "shapiro_w": sw.statistic, "shapiro_p": sw.pvalue,
                      "maior_perda": float(np.exp(lx.max())), "z_max_ln": z_max,
                      "p_cauda_normal": float(1 - stats.norm.cdf(z_max)),
                      "z_max_bruto": float((np.exp(lx.max()) - np.exp(lx).mean()) / np.exp(lx).std(ddof=1)),
                      "assimetria_ln": float(stats.skew(lx, bias=False))}
    salvar_figura(fig, "q06c_qq_lognormal")

    registrar("q06", {"a": {"unidade": u, "lambda_hat": lam_hat, "p_teorica": p_teor, "p_empirica": p_emp,
                            "meses_ge6": int((contagens >= 6).sum()), "var": contagens.var(ddof=1)},
                      "b": {"n": len(t), "p_teorica_theta4": p_teor_b, "theta_hat": theta_hat,
                            "p_teorica_theta_hat": p_teor_b_hat, "p_observada": p_obs_b,
                            "erro_padrao": ep_b, "z": (p_obs_b - p_teor_b) / ep_b},
                      "c": resc})


if __name__ == "__main__":
    rodar()
