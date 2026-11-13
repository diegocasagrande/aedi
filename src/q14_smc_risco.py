"""Questão 14 — Perda anual de 2026 e o pacote de controles (cap. 12, Parte C).

Arquitetura da Seção 12.7, usando SÓ o que foi estimado na Parte B:
  frequência   -> regressão múltipla da Q11 (trimestres 13 a 16, perfil de cada unidade)
  materializ.  -> logística da Q13 (probabilidade média por unidade)
  severidade   -> Lognormal por tipo, (mu, sigma) de ln(perda) estimados em perdas.csv
Thinning: se N_u ~ Poisson(lambda_u) e cada ataque vira perda com prob. p_u, de forma
independente, então o número de perdas é Poisson(lambda_u * p_u); separando por tipo,
N_(u,k) ~ Poisson(lambda_u * p_u * w_(u,k)) independentes, e somando unidades,
N_k ~ Poisson(Lambda_k) com Lambda_k = soma_u lambda_u p_u w_(u,k).

Números aleatórios comuns: os dois cenários usam as MESMAS uniformes (contagens pela
inversa da Poisson) e as MESMAS normais (severidades), réplica a réplica.
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

import gerador as G
import q10_inferencia_regressao  # noqa: F401  (documenta a origem do beta do tempo)
import q11_regressao_multipla as Q11
import q13_classificacao as Q13
from util import COR, TIPOS, TIPO_CURTO, carregar, fmt, registrar, salvar_figura, salvar_tabela

CUSTO_PACOTE = 8e6
LIMIAR_RELEVANTE = 30e6


# --------------------------------------------------------------------------- a) MODELAR
def entradas(cenario: str, m11, m13, beta_tempo: float, b: dict) -> dict:
    """Taxas Lambda_k de perdas por tipo e parâmetros (mu_k, sigma_k) para um cenário."""
    un = b["unidades"].copy()
    at = b["ataques"].merge(un[["unidade", "soc", "treino"]], on="unidade")
    pe = b["perdas"]
    ln = np.log(pe.perda_rs)
    mu = ln.groupby(pe.tipo).mean().reindex(TIPOS)
    sig = ln.groupby(pe.tipo).std(ddof=1).reindex(TIPOS)

    # tempo médio estimado (Q7) com e sem SOC: fator de escala da Exponencial
    th_soc = at.loc[at.soc == 1, "tempo_deteccao_h"].mean()
    th_sem = at.loc[at.soc == 0, "tempo_deteccao_h"].mean()

    perfil = un.copy()
    at_c = at.copy()
    if cenario == "controles":
        perfil[["patch", "treino", "soc"]] = [95.0, 12.0, 1]
        # SOC reduz o tempo: reescala os tempos das unidades sem SOC pela razão das médias estimadas
        fator = np.where(at_c.soc == 0, th_soc / th_sem, 1.0)
        at_c["tempo_deteccao_h"] = at_c.tempo_deteccao_h * fator
        at_c["soc"] = 1
        at_c["treino"] = 12.0

    # frequência anual por unidade: soma das previsões da Q11 para q = 13..16
    lin = []
    for q in range(13, 17):
        d = perfil.assign(trimestre=q)
        lin.append(m11.predict(d).clip(lower=0).to_numpy())
    lam = np.sum(lin, axis=0)

    # materialização: p previsto pela Q13 para os ataques observados de cada unidade
    at_c["p"] = m13.predict(at_c)
    p_med = at_c.groupby("unidade").p.mean().reindex(perfil.unidade).to_numpy()
    w = (at_c.groupby(["unidade", "tipo"]).p.sum().unstack().reindex(index=perfil.unidade, columns=TIPOS)
         .fillna(0.0))
    w = w.div(w.sum(axis=1), axis=0).to_numpy()
    Lam = (lam * p_med)[:, None] * w
    Lam_k = Lam.sum(axis=0)

    # severidade: no cenário com controles, desloca mu_k pelo efeito do tempo (Q10-d)
    mu_c = mu.copy()
    if cenario == "controles":
        at0 = at.assign(p=m13.predict(at))
        t0 = (at0.p * at0.tempo_deteccao_h).groupby(at0.tipo).sum() / at0.p.groupby(at0.tipo).sum()
        t1 = (at_c.p * at_c.tempo_deteccao_h).groupby(at_c.tipo).sum() / at_c.p.groupby(at_c.tipo).sum()
        mu_c = mu + beta_tempo * (t1 - t0).reindex(TIPOS)
    return {"lam_unidade": lam, "p_unidade": p_med, "Lam_k": Lam_k, "mu": mu_c.to_numpy(),
            "sigma": sig.to_numpy(), "th_soc": th_soc, "th_sem": th_sem,
            "tempo_medio_perdas": float((at_c.p * at_c.tempo_deteccao_h).sum() / at_c.p.sum())}


# ----------------------------------------------------------------- b) SORTEAR e CALCULAR
def simular(cenarios: list[dict], n: int, semente, lote: int = 5000) -> list[np.ndarray]:
    """Perda anual para vários cenários com números aleatórios comuns."""
    rng = np.random.default_rng(semente)
    Lmax = np.max([c["Lam_k"] for c in cenarios], axis=0)
    M = stats.poisson.ppf(1 - 1e-10, Lmax).astype(int) + 1  # colunas de normais reservadas por tipo
    saidas = [np.empty(n) for _ in cenarios]
    feito = 0
    while feito < n:
        r = min(lote, n - feito)
        U = rng.random((r, len(TIPOS)))
        Z = [rng.standard_normal((r, M[k])) for k in range(len(TIPOS))]
        for c, s in zip(cenarios, saidas):
            tot = np.zeros(r)
            for k in range(len(TIPOS)):
                N = stats.poisson.ppf(U[:, k], c["Lam_k"][k]).astype(int)
                N = np.minimum(N, M[k])
                sev = np.exp(c["mu"][k] + c["sigma"][k] * Z[k])
                cs = np.concatenate([np.zeros((r, 1)), np.cumsum(sev, axis=1)], axis=1)
                tot += cs[np.arange(r), N]
            s[feito:feito + r] = tot
        feito += r
    return saidas


def metricas(x: np.ndarray) -> dict:
    v95, v99 = np.quantile(x, [0.95, 0.99])
    return {"media": x.mean(), "mediana": np.median(x), "desvio": x.std(ddof=1), "var95": v95, "var99": v99,
            "cvar95": x[x >= v95].mean(), "p_acima_30mi": (x > LIMIAR_RELEVANTE).mean(),
            "ep_media": x.std(ddof=1) / np.sqrt(len(x))}


# -------------------------------------------------------------- g) GERADOR VERDADEIRO 2026
def gerador_verdadeiro_2026(n_anos: int, semente) -> np.ndarray:
    """Roda as Etapas A2 a A5 com os parâmetros verdadeiros para t = 37..48 (sem campanha)."""
    rng = np.random.default_rng(semente)
    un = carregar()["unidades"]
    perdas_ano = np.zeros(n_anos)
    cont = {"ataques": 0, "perdas": 0, "soma_perdas": 0.0}
    cum_tipo = np.cumsum(G.P_TIPO)
    for t in range(37, 49):
        _, mes, q = G.calendario(t)
        lam = G.lambda_trimestral(un.servicos, un.patch, un.treino, un.soc, q).to_numpy() / 3 * G.SAZONAL[mes - 1]
        N = rng.poisson(lam, size=(n_anos, len(un)))
        ano_idx = np.repeat(np.arange(n_anos), N.sum(axis=1))
        u_idx = np.concatenate([np.repeat(np.arange(len(un)), linha) for linha in N])
        n = len(u_idx)
        tipo = np.minimum(np.searchsorted(cum_tipo, rng.random(n), side="right"), 5)
        fora = rng.random(n) < G.P_FORA
        tri = G.CVSS_TRI[tipo]
        cvss = np.round(rng.triangular(tri[:, 0], tri[:, 1], tri[:, 2]), 1)
        soc = un.soc.to_numpy()[u_idx]
        tre = un.treino.to_numpy()[u_idx]
        tempo = rng.exponential(np.where(soc == 1, G.THETA_SOC, G.THETA_SEM_SOC)) * np.where(fora, G.FATOR_FORA, 1.0)
        bl = G.BETA_LOGIT
        p = 1 / (1 + np.exp(-(bl["const"] + bl["cvss"] * cvss + bl["tempo"] * tempo + bl["soc"] * soc
                              + bl["treino"] * tre + bl["fora"] * fora)))
        mat = rng.random(n) < p
        perda = np.exp(np.log(G.MEDIANA_PERDA[tipo]) + G.BETA_TEMPO_SEV * tempo + rng.normal(0, G.SIGMA_EPS, n))
        perdas_ano += np.bincount(ano_idx[mat], weights=perda[mat], minlength=n_anos)
        cont["ataques"] += n
        cont["perdas"] += int(mat.sum())
        cont["soma_perdas"] += float(perda[mat].sum())
    cont = {"ataques_ano": cont["ataques"] / n_anos, "perdas_ano": cont["perdas"] / n_anos,
            "p_medio": cont["perdas"] / cont["ataques"], "sev_media": cont["soma_perdas"] / cont["perdas"]}
    return perdas_ano, cont


# --------------------------------------------------------------------------- ANALISAR
def rodar(semente: int, n: int = 100_000):
    b = carregar()
    pn = Q11.preparar(b["painel_trimestral"])
    m11 = Q11.ajustar(pn)
    at13, _ = Q13.base_classificacao()
    m13 = Q13.ajustar(at13)
    pe = b["perdas"].assign(ln=np.log(b["perdas"].perda_rs))
    import statsmodels.formula.api as smf
    beta_tempo = float(smf.ols("ln ~ tempo_deteccao_h + C(tipo)", data=pe).fit().params["tempo_deteccao_h"])

    base = entradas("atual", m11, m13, beta_tempo, b)
    ctrl = entradas("controles", m11, m13, beta_tempo, b)

    tab_ent = pd.DataFrame({
        "tipo": TIPOS, "mu_ln": base["mu"], "sigma_ln": base["sigma"],
        "mediana_rs": np.exp(base["mu"]), "media_rs": np.exp(base["mu"] + base["sigma"] ** 2 / 2),
        "Lambda_atual": base["Lam_k"], "mu_ln_controles": ctrl["mu"], "Lambda_controles": ctrl["Lam_k"]})
    salvar_tabela(tab_ent.round(4), "q14a_entradas_por_tipo")
    un = b["unidades"]
    tab_un = pd.DataFrame({"unidade": un.unidade, "soc": un.soc, "ataques_ano_atual": base["lam_unidade"],
                           "p_medio_atual": base["p_unidade"], "ataques_ano_controles": ctrl["lam_unidade"],
                           "p_medio_controles": ctrl["p_unidade"]})
    salvar_tabela(tab_un.round(4), "q14a_entradas_por_unidade")

    # b) 100.000 réplicas, com números comuns entre cenários
    x0, x1 = simular([base, ctrl], n, [semente, 14])
    m0, m1 = metricas(x0), metricas(x1)

    fig, ax = plt.subplots(figsize=(8, 3.8))
    ax.hist(x0 / 1e6, bins=120, color=COR["azul"], alpha=0.85, density=True)
    for chave, rot, cor, ls in [("media", "Média", COR["verde"], "-"), ("var95", "VaR 95%", COR["laranja"], "--"),
                                ("cvar95", "CVaR 95%", COR["vermelho"], "--"), ("var99", "VaR 99%", COR["roxo"], ":")]:
        ax.axvline(m0[chave] / 1e6, color=cor, ls=ls, lw=1.5, label=f"{rot}: R$ {fmt(m0[chave] / 1e6, 1)} mi")
    ax.set_xlabel("Perda anual simulada em 2026 (R$ milhões)")
    ax.set_ylabel("Densidade")
    ax.set_title("Q14-b  Distribuição simulada da perda anual (cenário atual, 100.000 réplicas)")
    ax.legend(fontsize=8)
    salvar_figura(fig, "q14b_distribuicao_atual")

    # c) convergência (prefixos da mesma sequência) + réplicas independentes para o EP do VaR
    conv = []
    for k in [1000, 4000, 16000, 64000, 100000]:
        s = x0[:k]
        conv.append({"n": k, "media": s.mean(), "ep_media": s.std(ddof=1) / np.sqrt(k),
                     "var95": np.quantile(s, 0.95)})
    conv = pd.DataFrame(conv)
    conv["razao_ep"] = conv.ep_media.shift(1) / conv.ep_media
    salvar_tabela(conv.round(2), "q14c_convergencia")
    fig, ax = plt.subplots(1, 2, figsize=(9.5, 3.3))
    ax[0].errorbar(conv.n, conv.media / 1e6, yerr=1.96 * conv.ep_media / 1e6, fmt="o-", color=COR["azul"], capsize=3)
    ax[0].set_xscale("log")
    ax[0].set_title("Perda média ± 1,96 EP")
    ax[0].set_xlabel("n (réplicas)")
    ax[0].set_ylabel("R$ milhões")
    ax[1].loglog(conv.n, conv.ep_media / 1e6, "o-", color=COR["laranja"], label="EP observado")
    ax[1].loglog(conv.n, conv.ep_media.iloc[0] / 1e6 * np.sqrt(conv.n.iloc[0] / conv.n), "--", color=COR["cinza"],
                 label="referência 1/√n")
    ax[1].set_title("Erro padrão da média")
    ax[1].set_xlabel("n (réplicas)")
    ax[1].legend(fontsize=8)
    fig.suptitle("Q14-c  Convergência da simulação", fontsize=10.5, fontweight="bold")
    salvar_figura(fig, "q14c_convergencia")

    # d) tabela no formato da Seção 12.7.3
    linhas = []
    for chave, rot in [("media", "Perda média anual"), ("mediana", "Mediana"), ("var95", "VaR 95%"),
                       ("var99", "VaR 99%"), ("cvar95", "CVaR 95%")]:
        linhas.append({"metrica": rot, "atual": m0[chave], "com_controles": m1[chave],
                       "reducao": m0[chave] - m1[chave], "reducao_pct": 1 - m1[chave] / m0[chave]})
    linhas.append({"metrica": "P(perda > R$ 30 mi)", "atual": m0["p_acima_30mi"], "com_controles": m1["p_acima_30mi"],
                   "reducao": m0["p_acima_30mi"] - m1["p_acima_30mi"], "reducao_pct": np.nan})
    comp = pd.DataFrame(linhas)
    salvar_tabela(comp, "q14d_comparacao_cenarios")
    fig, ax = plt.subplots(figsize=(8, 3.6))
    bins = np.linspace(0, np.quantile(x0, 0.999) / 1e6, 120)
    ax.hist(x0 / 1e6, bins=bins, color=COR["azul"], alpha=0.6, density=True, label="Atual")
    ax.hist(x1 / 1e6, bins=bins, color=COR["verde"], alpha=0.6, density=True, label="Com controles")
    ax.axvline(m0["var95"] / 1e6, color=COR["azul"], ls="--", lw=1.2)
    ax.axvline(m1["var95"] / 1e6, color=COR["verde"], ls="--", lw=1.2)
    ax.set_xlabel("Perda anual simulada em 2026 (R$ milhões); tracejado: VaR 95%")
    ax.set_ylabel("Densidade")
    ax.set_title("Q14-d  O pacote de controles desloca a distribuição para a esquerda")
    ax.legend(fontsize=8)
    salvar_figura(fig, "q14d_comparacao")

    # e) decisão
    reducao = m0["media"] - m1["media"]
    roi = (reducao - CUSTO_PACOTE) / CUSTO_PACOTE
    p_pior = float(((x1 + CUSTO_PACOTE) > x0).mean())
    beneficio = x0 - x1 - CUSTO_PACOTE

    # f) sensibilidade: sigma +-20% e frequência +-10% nos dois cenários
    sens = []
    for nome, fs, fl in [("base", 1.0, 1.0), ("σ −20%", 0.8, 1.0), ("σ +20%", 1.2, 1.0),
                         ("frequência −10%", 1.0, 0.9), ("frequência +10%", 1.0, 1.1)]:
        cs = [dict(c, sigma=c["sigma"] * fs, Lam_k=c["Lam_k"] * fl) for c in (base, ctrl)]
        a0, a1 = simular(cs, 50_000, [semente, 141])
        red = a0.mean() - a1.mean()
        sens.append({"cenario": nome, "media_atual": a0.mean(), "media_controles": a1.mean(), "reducao": red,
                     "beneficio_liquido": red - CUSTO_PACOTE, "roi": (red - CUSTO_PACOTE) / CUSTO_PACOTE,
                     "var95_atual": np.quantile(a0, 0.95), "var95_controles": np.quantile(a1, 0.95),
                     "decisao": "investir" if red > CUSTO_PACOTE else "não investir"})
    sens = pd.DataFrame(sens)
    salvar_tabela(sens.round(4), "q14f_sensibilidade")
    bl = sens.loc[0, "beneficio_liquido"]
    fig, ax = plt.subplots(figsize=(7, 2.8))
    pares = [("σ da Lognormal ±20%", "σ −20%", "σ +20%"), ("Frequência ±10%", "frequência −10%", "frequência +10%")]
    for i, (rot, lo, hi) in enumerate(pares):
        vlo = sens.set_index("cenario").loc[lo, "beneficio_liquido"]
        vhi = sens.set_index("cenario").loc[hi, "beneficio_liquido"]
        ax.barh(i, (vlo - bl) / 1e6, left=bl / 1e6, color=COR["laranja"], height=0.5)
        ax.barh(i, (vhi - bl) / 1e6, left=bl / 1e6, color=COR["azul"], height=0.5)
        ax.text(min(vlo, vhi) / 1e6 - 0.2, i, f"{fmt(min(vlo, vhi) / 1e6, 1)}", va="center", ha="right", fontsize=8)
        ax.text(max(vlo, vhi) / 1e6 + 0.2, i, f"{fmt(max(vlo, vhi) / 1e6, 1)}", va="center", ha="left", fontsize=8)
    ax.axvline(bl / 1e6, color="black", lw=1)
    ax.axvline(0, color=COR["vermelho"], lw=1, ls="--")
    ax.set_yticks([0, 1], [p[0] for p in pares])
    ax.set_xlabel("Benefício líquido médio do pacote (R$ milhões/ano); laranja: −, azul: +")
    ax.set_title("Q14-f  Tornado: o benefício nunca cruza zero (linha vermelha)")
    xmin = min(0, sens.beneficio_liquido.min() / 1e6) - 2
    ax.set_xlim(xmin, sens.beneficio_liquido.max() / 1e6 + 3)
    salvar_figura(fig, "q14f_tornado")

    # g) erro de modelo: gerador verdadeiro para 2026
    xv, cont_v = gerador_verdadeiro_2026(10_000, [semente, 142])
    mv = metricas(xv)
    erro = pd.DataFrame([{"metrica": k, "modelo_estimado": m0[k], "gerador_verdadeiro": mv[k],
                          "razao_estimado_verdadeiro": m0[k] / mv[k]}
                         for k in ["media", "mediana", "desvio", "var95", "var99", "cvar95", "p_acima_30mi"]])
    salvar_tabela(erro, "q14g_erro_de_modelo")
    fig, ax = plt.subplots(figsize=(8, 3.6))
    bins = np.linspace(min(x0.min(), xv.min()) / 1e6, np.quantile(np.r_[x0, xv], 0.999) / 1e6, 100)
    ax.hist(x0 / 1e6, bins=bins, color=COR["azul"], alpha=0.55, density=True, label="SMC com modelos estimados (b)")
    ax.hist(xv / 1e6, bins=bins, color=COR["laranja"], alpha=0.55, density=True, label="Gerador verdadeiro (10.000 anos)")
    for m_, cor in [(m0, COR["azul"]), (mv, COR["laranja"])]:
        ax.axvline(m_["var99"] / 1e6, color=cor, ls=":", lw=1.4)
    ax.set_xlabel("Perda anual em 2026 (R$ milhões); pontilhado: VaR 99%")
    ax.set_ylabel("Densidade")
    ax.set_title("Q14-g  Modelo estimado × gerador verdadeiro")
    ax.legend(fontsize=8)
    salvar_figura(fig, "q14g_erro_modelo")

    # decomposição do erro: frequência e severidade médias implicadas
    n_perdas_est = base["Lam_k"].sum()
    sev_media_est = (base["Lam_k"] * np.exp(base["mu"] + base["sigma"] ** 2 / 2)).sum() / n_perdas_est

    registrar("q14", {
        "beta_tempo": beta_tempo, "th_soc": base["th_soc"], "th_sem": base["th_sem"],
        "fator_tempo": base["th_soc"] / base["th_sem"],
        "tempo_medio_perdas_atual": base["tempo_medio_perdas"], "tempo_medio_perdas_ctrl": ctrl["tempo_medio_perdas"],
        "entradas_tipo": tab_ent.round(4), "entradas_unidade": tab_un.round(3),
        "ataques_ano_atual": float(base["lam_unidade"].sum()), "ataques_ano_ctrl": float(ctrl["lam_unidade"].sum()),
        "perdas_ano_atual": float(base["Lam_k"].sum()), "perdas_ano_ctrl": float(ctrl["Lam_k"].sum()),
        "p_medio_atual": float(base["Lam_k"].sum() / base["lam_unidade"].sum()),
        "p_medio_ctrl": float(ctrl["Lam_k"].sum() / ctrl["lam_unidade"].sum()),
        "sev_media_est": float(sev_media_est),
        "b": m0, "b_controles": m1, "c": conv.round(2), "d": comp,
        "e": {"reducao_media": reducao, "roi": roi, "p_pior_com_pacote": p_pior, "custo_maximo": reducao,
              "beneficio_p5": float(np.quantile(beneficio, 0.05)), "beneficio_mediana": float(np.median(beneficio)),
              "reducao_var95": m0["var95"] - m1["var95"], "reducao_cvar95": m0["cvar95"] - m1["cvar95"]},
        "f": sens.round(2), "g": {"verdadeiro": mv, "tabela": erro, "contagens": cont_v}, "n": n})


if __name__ == "__main__":
    rodar(202604)
