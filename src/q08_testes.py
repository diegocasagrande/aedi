"""Questão 8 — Testes de hipóteses e backtesting (cap. 7)."""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from util import ALFA, COR, carregar, registrar, salvar_figura, salvar_tabela


def kupiec(N, T, p):
    """LR de Kupiec (POF), Seção 7.10.2."""
    taxa = N / T
    l0 = (T - N) * np.log(1 - p) + N * np.log(p)
    l1 = (T - N) * np.log(1 - taxa) + (N * np.log(taxa) if N > 0 else 0.0)
    lr = -2 * (l0 - l1)
    return lr, 1 - stats.chi2.cdf(lr, 1)


def rodar():
    b = carregar()
    at, un, pe = b["ataques"], b["unidades"], b["perdas"]
    at = at.merge(un[["unidade", "soc"]], on="unidade")

    # a) H0: mu <= 4 h  x  Ha: mu > 4 h (unidades com SOC), teste t unilateral
    t_soc = at.loc[at.soc == 1, "tempo_deteccao_h"].to_numpy()
    n_a, m_a, s_a = len(t_soc), t_soc.mean(), t_soc.std(ddof=1)
    t_a = (m_a - 4) / (s_a / np.sqrt(n_a))
    tc_a = stats.t.ppf(1 - ALFA, n_a - 1)
    p_a = 1 - stats.t.cdf(t_a, n_a - 1)
    t_exp = at.loc[(at.soc == 1) & (at.fora_expediente == 0), "tempo_deteccao_h"].to_numpy()
    t_exp_stat = (t_exp.mean() - 4) / (t_exp.std(ddof=1) / np.sqrt(len(t_exp)))
    p_exp = 1 - stats.t.cdf(t_exp_stat, len(t_exp) - 1)

    # b) H0: p <= 0,40  x  Ha: p > 0,40, teste Z para proporção
    n_b = len(at)
    p_hat = at.materializou.mean()
    z_b = (p_hat - 0.40) / np.sqrt(0.40 * 0.60 / n_b)
    zc_b = stats.norm.ppf(1 - ALFA)
    p_b = 1 - stats.norm.cdf(z_b)

    # d) backtesting: perda mensal por unidade (zeros incluídos)
    pe = pe.assign(ano=pd.to_datetime(pe.data).dt.year, mes=pd.to_datetime(pe.data).dt.month)
    grade = pd.MultiIndex.from_product([un.unidade, [2023, 2024, 2025], range(1, 13)],
                                       names=["unidade", "ano", "mes"]).to_frame(index=False)
    um = grade.merge(pe.groupby(["unidade", "ano", "mes"]).perda_rs.sum().reset_index(),
                     how="left", on=["unidade", "ano", "mes"]).fillna({"perda_rs": 0.0})
    treino = um[um.ano <= 2024].perda_rs.to_numpy()
    teste = um[um.ano == 2025]
    var95 = float(np.percentile(treino, 95))
    excecoes = (teste.perda_rs > var95)
    N, T = int(excecoes.sum()), len(teste)
    lr, p_lr = kupiec(N, T, 0.05)
    exc_mes = teste.assign(exc=excecoes).groupby("mes").exc.sum()
    taxa_treino_por_ano = {int(a): float((um[um.ano == a].perda_rs > var95).mean()) for a in (2023, 2024)}
    salvar_tabela(exc_mes.rename("excecoes").reset_index(), "q08d_excecoes_por_mes_2025")

    fig, ax = plt.subplots(figsize=(7.5, 3.3))
    teste_ord = teste.reset_index(drop=True)
    x = np.arange(T)
    ax.scatter(x[~excecoes.to_numpy()], teste_ord.perda_rs[~excecoes.to_numpy()] / 1e3, s=6, color=COR["cinza"],
               label="perda mensal da unidade (2025)")
    ax.scatter(x[excecoes.to_numpy()], teste_ord.perda_rs[excecoes.to_numpy()] / 1e3, s=14, color=COR["vermelho"],
               label=f"exceções: {N} (esperado {T * 0.05:.1f})".replace(".", ","))
    ax.axhline(var95 / 1e3, color=COR["azul"], lw=1.2, label="VaR 95% estimado em 2023–2024")
    ax.set_yscale("symlog", linthresh=10)
    ax.set_ylim(bottom=0)
    ax.set_xlabel("Unidade-mês de 2025 (ordenado por unidade e mês)")
    ax.set_ylabel("Perda (R$ mil)")
    ax.set_title("Q8-d  Backtesting do VaR 95% mensal por unidade")
    ax.legend(fontsize=7.5, loc="upper left")
    salvar_figura(fig, "q08d_backtesting")

    registrar("q08", {
        "a": {"n": n_a, "media": m_a, "dp": s_a, "t": t_a, "t_critico": tc_a, "p": p_a,
              "n_expediente": len(t_exp), "media_expediente": t_exp.mean(), "t_expediente": t_exp_stat,
              "p_expediente": p_exp},
        "b": {"n": n_b, "p_hat": p_hat, "z": z_b, "z_critico": zc_b, "p": p_b,
              "ep_h0": np.sqrt(0.24 / n_b)},
        "d": {"var95": var95, "T_treino": len(treino), "T": T, "N": N, "esperado": T * 0.05,
              "taxa": N / T, "lr": lr, "p": p_lr, "critico": stats.chi2.ppf(0.95, 1),
              "excecoes_abril": int(exc_mes.loc[4]), "excecoes_por_mes": exc_mes,
              "zeros_treino": float((treino == 0).mean()), "taxa_treino_por_ano": taxa_treino_por_ano,
              "media_treino": float(treino.mean()), "media_teste": float(teste.perda_rs.mean())}})


if __name__ == "__main__":
    rodar()
