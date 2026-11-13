"""Questão 7 — Amostragem e estimação (cap. 6)."""
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

from util import COR, carregar, fmt, registrar, salvar_figura, salvar_tabela
import pandas as pd


def ic_media(v, conf=0.95):
    n = len(v)
    m, s = v.mean(), v.std(ddof=1)
    t = stats.t.ppf(1 - (1 - conf) / 2, n - 1)
    e = t * s / np.sqrt(n)
    return {"n": n, "media": m, "dp": s, "t": t, "margem": e, "li": m - e, "ls": m + e}


def rodar(semente: int):
    b = carregar()
    at, un, pe = b["ataques"], b["unidades"], b["perdas"]
    at = at.merge(un[["unidade", "soc"]], on="unidade")

    # a) IC do tempo médio de detecção, com e sem SOC (e só no expediente, para a pista)
    linhas = []
    for soc, theta in [(1, 4.0), (0, 12.0)]:
        for rot, filtro in [("todos", at.soc == soc), ("só no expediente", (at.soc == soc) & (at.fora_expediente == 0))]:
            r = ic_media(at.loc[filtro, "tempo_deteccao_h"].to_numpy())
            esperado = theta * (0.65 + 0.35 * 1.5) if rot == "todos" else theta
            r.update({"soc": soc, "subconjunto": rot, "theta_programado": theta, "media_verdadeira": esperado,
                      "contem_theta": r["li"] <= theta <= r["ls"],
                      "contem_media_verdadeira": r["li"] <= esperado <= r["ls"]})
            linhas.append(r)
    ic_tempo = pd.DataFrame(linhas)
    salvar_tabela(ic_tempo.round(4), "q07a_ic_tempo")

    # b) IC da proporção e tamanho de amostra para +-2 p.p.
    n = len(at)
    p = at.materializou.mean()
    z = stats.norm.ppf(0.975)
    ep = np.sqrt(p * (1 - p) / n)
    n_p = int(np.ceil(z ** 2 * p * (1 - p) / 0.02 ** 2))
    n_pior = int(np.ceil(z ** 2 * 0.25 / 0.02 ** 2))

    # c) TCL por bootstrap
    rng = np.random.default_rng([semente, 7])  # fluxo próprio da Q7, independente do gerador
    x = pe.perda_rs.to_numpy()
    sigma = x.std(ddof=0)
    fig, ax = plt.subplots(1, 3, figsize=(10, 3.2))
    tcl = []
    for a, m in zip(ax, [5, 30, 100]):
        medias = rng.choice(x, size=(2000, m), replace=True).mean(axis=1)
        tcl.append({"n": m, "dp_medias": medias.std(ddof=1), "sigma_sobre_raiz_n": sigma / np.sqrt(m),
                    "assimetria_medias": stats.skew(medias), "media_das_medias": medias.mean()})
        a.hist(medias / 1e3, bins=40, color=COR["azul"], edgecolor="white", density=True)
        g = np.linspace(medias.min(), medias.max(), 200)
        a.plot(g / 1e3, stats.norm.pdf(g, x.mean(), sigma / np.sqrt(m)) * 1e3, color=COR["vermelho"], lw=1.2)
        a.set_title(f"n = {m}  (assimetria {fmt(stats.skew(medias), 2)})")
        a.set_xlabel("Média amostral (R$ mil)")
    ax[0].set_ylabel("Densidade")
    fig.suptitle("Q7-c  TCL na base: 2.000 médias de perda_rs (curva: Normal prevista pelo TCL)",
                 fontsize=10, fontweight="bold")
    salvar_figura(fig, "q07c_tcl")
    tcl = pd.DataFrame(tcl)
    salvar_tabela(tcl.round(2), "q07c_tcl")

    registrar("q07", {"a": ic_tempo.round(4),
                      "b": {"n": n, "p": p, "ep": ep, "li": p - z * ep, "ls": p + z * ep,
                            "n_para_2pp": n_p, "n_pior_caso": n_pior},
                      "c": {"sigma": sigma, "media": x.mean(), "assimetria_perda": float(stats.skew(x)),
                            "tabela": tcl.round(3)}})


if __name__ == "__main__":
    rodar(202604)
