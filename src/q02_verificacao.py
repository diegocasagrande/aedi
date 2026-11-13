"""Questão 2 — Verificação do gerador (caps. 4, 5 e 12).

Compara o que o gerador produziu com o que foi programado: frequência por
unidade, dispersão das contagens, tipos de ataque e materialização."""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from gerador import P_TIPO, TIPOS
from util import COR, carregar, registrar, salvar_figura, salvar_tabela


def rodar():
    b = carregar()
    lam, un, at = b["lambda"], b["unidades"], b["ataques"]

    # a) média mensal observada x teórica por unidade
    por_u = lam.groupby("unidade").agg(media_observada=("n_ataques", "mean"),
                                       media_teorica=("lambda", "mean"),
                                       var_observada=("n_ataques", "var")).reset_index()
    por_u = por_u.merge(un[["unidade", "soc"]], on="unidade")
    # erro padrão da média de 36 contagens Poisson: sqrt(media dos lambda / 36)
    por_u["erro_padrao"] = np.sqrt(por_u.media_teorica / 36)
    por_u["z"] = (por_u.media_observada - por_u.media_teorica) / por_u.erro_padrao
    por_u["indice_dispersao"] = por_u.var_observada / por_u.media_observada
    # dispersão em torno do lambda de cada mês (retira tendência e sazonalidade)
    lam["pearson"] = (lam.n_ataques - lam["lambda"]) ** 2 / lam["lambda"]
    por_u = por_u.merge(lam.groupby("unidade").pearson.mean().rename("dispersao_vs_lambda").reset_index(),
                        on="unidade")
    salvar_tabela(por_u.round(4), "q02a_media_por_unidade")

    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    for s, cor, rot in [(0, COR["laranja"], "sem SOC"), (1, COR["azul"], "com SOC")]:
        d = por_u[por_u.soc == s]
        ax.errorbar(d.media_teorica, d.media_observada, yerr=1.96 * d.erro_padrao, fmt="o",
                    color=cor, label=rot, ms=5, capsize=2, lw=0.8)
    lim = [por_u[["media_teorica", "media_observada"]].min().min() - 0.3,
           por_u[["media_teorica", "media_observada"]].max().max() + 0.3]
    ax.plot(lim, lim, "--", color=COR["cinza"], lw=1, label="observado = teórico")
    ax.set_xlabel("Média teórica mensal (média dos λ_u,t)")
    ax.set_ylabel("Média observada de ataques por mês")
    ax.set_title("Q2-a  Média mensal de ataques por unidade (barras: IC 95%)")
    ax.legend()
    salvar_figura(fig, "q02a_media_por_unidade")

    # b) dispersão: dentro de unidade sem SOC x todas juntas
    sem_soc = por_u[por_u.soc == 0]
    u_escolhida = int(sem_soc.sort_values("media_observada").iloc[len(sem_soc) // 2].unidade)
    todas = lam.n_ataques
    disp_todas = todas.var() / todas.mean()
    # decomposição da variância total: média das variâncias + variância das médias
    var_dentro = por_u.var_observada.mean()
    var_entre = por_u.media_observada.var()
    res_b = {
        "unidade_escolhida": u_escolhida,
        "indice_unidade": float(por_u.loc[por_u.unidade == u_escolhida, "indice_dispersao"].item()),
        "dispersao_vs_lambda_unidade": float(por_u.loc[por_u.unidade == u_escolhida, "dispersao_vs_lambda"].item()),
        "indice_medio_sem_soc": float(sem_soc.indice_dispersao.mean()),
        "indice_min_sem_soc": float(sem_soc.indice_dispersao.min()),
        "indice_max_sem_soc": float(sem_soc.indice_dispersao.max()),
        "dispersao_vs_lambda_media": float(por_u.dispersao_vs_lambda.mean()),
        "indice_todas": float(disp_todas), "media_todas": float(todas.mean()),
        "var_todas": float(todas.var()), "var_dentro": float(var_dentro), "var_entre": float(var_entre),
    }

    # c) tipos e materialização
    n = len(at)
    obs = at.tipo.value_counts().reindex(TIPOS).to_numpy()
    tab_tipos = pd.DataFrame({"tipo": TIPOS, "ataques": obs, "freq_observada": obs / n,
                              "prob_programada": P_TIPO})
    tab_tipos["erro_simulacao"] = np.sqrt(tab_tipos.prob_programada * (1 - tab_tipos.prob_programada) / n)
    tab_tipos["z"] = (tab_tipos.freq_observada - tab_tipos.prob_programada) / tab_tipos.erro_simulacao
    salvar_tabela(tab_tipos.round(4), "q02c_tipos")
    qui = stats.chisquare(obs, P_TIPO * n)

    taxa = at.materializou.mean()
    p_med = at.p_programado.mean()
    ep_taxa = np.sqrt((at.p_programado * (1 - at.p_programado)).sum()) / n
    res_c = {"n_ataques": n, "qui2": float(qui.statistic), "qui2_p": float(qui.pvalue),
             "qui2_critico": float(stats.chi2.ppf(0.95, 5)),
             "taxa_materializacao": float(taxa), "p_medio": float(p_med),
             "erro_padrao_taxa": float(ep_taxa), "z_taxa": float((taxa - p_med) / ep_taxa),
             "tipos": tab_tipos.round(4)}

    res_a = {"z_min": float(por_u.z.min()), "z_max": float(por_u.z.max()),
             "fora_ic95": int((por_u.z.abs() > 1.96).sum()),
             "corr_obs_teo": float(np.corrcoef(por_u.media_observada, por_u.media_teorica)[0, 1]),
             "tabela": por_u.round(3)}
    registrar("q02", {"a": res_a, "b": res_b, "c": res_c})


if __name__ == "__main__":
    rodar()
