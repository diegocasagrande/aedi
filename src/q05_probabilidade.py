"""Questão 5 — Probabilidade e Bayes (cap. 3)."""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from util import TIPOS, carregar, fmt, registrar, salvar_figura, salvar_tabela


def arvore(ax, prev, sens, espec, titulo):
    """Árvore de triagem (Seção 3.8): estado -> alarme, com probabilidades conjuntas."""
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_title(titulo, fontsize=11)
    nos = {"raiz": (0.6, 5), "M": (4, 7.5), "N": (4, 2.5),
           "MA": (8, 8.8), "MS": (8, 6.2), "NA": (8, 3.8), "NS": (8, 1.2)}
    ramos = [("raiz", "M", f"Materializa\n{fmt(prev, 3)}"), ("raiz", "N", f"Não materializa\n{fmt(1 - prev, 3)}"),
             ("M", "MA", f"alarme {fmt(sens, 3)}"), ("M", "MS", f"sem alarme {fmt(1 - sens, 3)}"),
             ("N", "NA", f"alarme {fmt(1 - espec, 3)}"), ("N", "NS", f"sem alarme {fmt(espec, 3)}")]
    for a, b_, rot in ramos:
        (x0, y0), (x1, y1) = nos[a], nos[b_]
        ax.plot([x0, x1], [y0, y1], color="#6b7280", lw=1)
        ax.text((x0 + x1) / 2, (y0 + y1) / 2 + 0.35, rot, ha="center", fontsize=9)
    folhas = {"MA": prev * sens, "MS": prev * (1 - sens), "NA": (1 - prev) * (1 - espec), "NS": (1 - prev) * espec}
    nomes = {"MA": "VP", "MS": "FN", "NA": "FP", "NS": "VN"}
    for k, v in folhas.items():
        x, y = nos[k]
        ax.text(x + 0.15, y, f"{nomes[k]} = {fmt(v, 3)}", va="center", fontsize=9.5,
                fontweight="bold" if k in ("MA", "NA") else "normal")
    vpp = folhas["MA"] / (folhas["MA"] + folhas["NA"])
    ax.text(0.2, 0.2, f"P(materializa | alarme) = {fmt(vpp, 3)}", fontsize=10, fontweight="bold")
    return vpp


def rodar():
    b = carregar()
    at, un = b["ataques"], b["unidades"]
    at = at.merge(un[["unidade", "soc"]], on="unidade")
    n = len(at)

    # a) contingência tipo x materializou
    ct = pd.crosstab(at.tipo, at.materializou).reindex(TIPOS)
    ct.columns = ["nao_materializou", "materializou"]
    ct["total"] = ct.sum(axis=1)
    ct.loc["Total"] = ct.sum()
    conj = ct / n
    salvar_tabela(ct, "q05a_contingencia", index=True)
    salvar_tabela(conj.round(4), "q05a_conjuntas", index=True)
    p_mat_ransom = ct.loc["Ransomware", "materializou"] / ct.loc["Ransomware", "total"]
    p_ransom_mat = ct.loc["Ransomware", "materializou"] / ct.loc["Total", "materializou"]
    p_mat_tipo = (ct["materializou"] / ct["total"]).drop("Total")

    # b) SOC x materializou
    pA = at.soc.mean()
    pB = at.materializou.mean()
    pAB = ((at.soc == 1) & (at.materializou == 1)).mean()
    qui = stats.chi2_contingency(pd.crosstab(at.soc, at.materializou), correction=False)

    # c) regra de triagem cvss >= 7
    alarme = at.cvss >= 7
    mat = at.materializou == 1
    sens = (alarme & mat).sum() / mat.sum()
    espec = (~alarme & ~mat).sum() / (~mat).sum()
    prev = mat.mean()
    vpp_bayes = sens * prev / (sens * prev + (1 - espec) * (1 - prev))
    vpp_direto = (alarme & mat).sum() / alarme.sum()
    vpn = espec * (1 - prev) / (espec * (1 - prev) + (1 - sens) * prev)

    # d) árvores: prevalência observada e metade
    fig, ax = plt.subplots(1, 2, figsize=(11, 3.8))
    arvore(ax[0], prev, sens, espec, f"Prevalência observada ({fmt(prev * 100, 1)}%)")
    vpp_metade = arvore(ax[1], prev / 2, sens, espec, f"Prevalência pela metade ({fmt(prev * 50, 1)}%)")
    salvar_figura(fig, "q05d_arvore_triagem")

    registrar("q05", {
        "contingencia": ct.reset_index().rename(columns={"index": "tipo"}),
        "p_mat_ransom": float(p_mat_ransom), "p_ransom_mat": float(p_ransom_mat),
        "p_ransom": float(ct.loc["Ransomware", "total"] / n), "p_mat": float(pB),
        "p_mat_tipo": p_mat_tipo.round(4),
        "pA_soc": float(pA), "pB_mat": float(pB), "pAB": float(pAB), "pA_x_pB": float(pA * pB),
        "p_mat_dado_soc": float(at.loc[at.soc == 1, "materializou"].mean()),
        "p_mat_dado_sem_soc": float(at.loc[at.soc == 0, "materializou"].mean()),
        "qui2_indep": float(qui.statistic), "qui2_indep_p": float(qui.pvalue),
        "sens": float(sens), "espec": float(espec), "prev": float(prev),
        "vpp_bayes": float(vpp_bayes), "vpp_direto": float(vpp_direto), "vpn": float(vpn),
        "n_alarmes": int(alarme.sum()), "vp": int((alarme & mat).sum()),
        "vpp_prev_metade": float(vpp_metade), "taxa_alarme": float(alarme.mean())})


if __name__ == "__main__":
    rodar()
