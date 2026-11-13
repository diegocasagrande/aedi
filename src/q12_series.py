"""Questão 12 — Séries temporais (cap. 11, Parte A). Série mensal de ataques (36 meses)."""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
from statsmodels.tsa.stattools import acf

from util import COR, carregar, registrar, salvar_figura, salvar_tabela

S_PROG = np.array([0.90, 0.85, 1.10, 1.10, 1.00, 0.95, 0.90, 0.95, 1.00, 1.05, 1.15, 1.05])
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def indices_sazonais(y, excluir=None):
    """Decomposição multiplicativa clássica: razão à média móvel centrada 2x12."""
    mm = y.rolling(12, center=True).mean().rolling(2).mean().shift(-1)
    razao = y / mm
    df = pd.DataFrame({"mes": (np.arange(len(y)) % 12) + 1, "razao": razao})
    if excluir is not None:
        df.loc[excluir, "razao"] = np.nan
    bruto = df.groupby("mes").razao.mean()
    return bruto / bruto.mean(), mm, razao


def modelo_tendencia_sazonal(y, idx):
    """Dessazonaliza, ajusta tendência linear e devolve ajuste, parâmetros e resíduos (escala original)."""
    t = np.arange(1, len(y) + 1)
    s = idx.to_numpy()[(t - 1) % 12]
    yd = y.to_numpy() / s
    b1, b0 = np.polyfit(t, yd, 1)
    ajuste = (b0 + b1 * t) * s
    return ajuste, b0, b1, y.to_numpy() - ajuste


def rodar():
    se = carregar()["serie_mensal"].copy()
    y = se.n_ataques.astype(float)
    t = np.arange(1, 37)

    # a) médias móveis e suavização exponencial
    mm3 = y.rolling(3).mean()
    mm12 = y.rolling(12).mean()
    ses = SimpleExpSmoothing(y.to_numpy(), initialization_method="estimated").fit()
    fig, ax = plt.subplots(figsize=(9, 3.6))
    ax.plot(t, y, "o-", ms=3, color=COR["cinza"], lw=1, label="n_ataques")
    ax.plot(t, mm3, color=COR["azul"], lw=1.4, label="média móvel 3 meses")
    ax.plot(t, mm12, color=COR["laranja"], lw=2, label="média móvel 12 meses")
    ax.plot(t, ses.fittedvalues, "--", color=COR["verde"], lw=1.2,
            label=f"suavização exponencial (α = {ses.params['smoothing_level']:.2f})".replace(".", ","))
    ax.set_xticks(range(1, 37, 3), [f"{MESES[(k - 1) % 12]}/{23 + (k - 1) // 12}" for k in range(1, 37, 3)])
    ax.set_ylabel("Ataques no mês")
    ax.set_title("Q12-a  Ataques mensais à ANDI, 2023–2025")
    ax.legend(fontsize=8, ncol=2)
    salvar_figura(fig, "q12a_serie")
    anual = y.groupby(np.arange(36) // 12).sum()

    # b) decomposição multiplicativa e índices sazonais
    idx_todos, mm, razao = indices_sazonais(y)
    idx_sem_camp, _, _ = indices_sazonais(y, excluir=[27])  # t = 28 -> posição 27
    comp = pd.DataFrame({"mes": MESES, "S_programado": S_PROG, "indice_estimado": idx_todos.to_numpy(),
                         "indice_sem_abril_2025": idx_sem_camp.to_numpy()})
    comp["erro"] = comp.indice_estimado - comp.S_programado
    comp["erro_sem_abril_2025"] = comp.indice_sem_abril_2025 - comp.S_programado
    salvar_tabela(comp.round(4), "q12b_indices_sazonais")
    fig, ax = plt.subplots(figsize=(7.5, 3.2))
    x = np.arange(12)
    ax.bar(x - 0.27, S_PROG, 0.27, color=COR["cinza"], label="S_m programado")
    ax.bar(x, idx_todos, 0.27, color=COR["laranja"], label="estimado (todos os meses)")
    ax.bar(x + 0.27, idx_sem_camp, 0.27, color=COR["azul"], label="estimado sem abril/2025")
    ax.axhline(1, color="black", lw=0.6)
    ax.set_xticks(x, MESES)
    ax.set_ylim(0.6, max(1.7, idx_todos.max() + 0.1))
    ax.set_title("Q12-b  Índices sazonais: estimados × programados")
    ax.legend(fontsize=8)
    salvar_figura(fig, "q12b_indices")

    # c) ACF
    r = acf(y, nlags=12, fft=False)
    banda = 1.96 / np.sqrt(len(y))
    fig, ax = plt.subplots(figsize=(6.5, 2.9))
    ax.bar(range(13), r, width=0.3, color=COR["azul"])
    ax.axhspan(-banda, banda, color=COR["cinza"], alpha=0.15)
    ax.set_xticks(range(13))
    ax.set_xlabel("Defasagem (meses)")
    ax.set_title("Q12-c  Autocorrelação da série mensal (faixa: ±1,96/√36)")
    salvar_figura(fig, "q12c_acf")

    # d) previsão 2026 e regra dos 3 sigma
    res_d = {}
    for nome, idx in [("indices_todos", idx_todos), ("indices_sem_abril_2025", idx_sem_camp)]:
        ajuste, b0, b1, resid = modelo_tendencia_sazonal(y, idx)
        sigma = resid.std(ddof=2)
        z = resid / sigma
        alarmes = [int(k + 1) for k in np.flatnonzero(np.abs(z) > 3)]
        res_d[nome] = {"b0": b0, "b1": b1, "sigma": sigma, "z_abril_2025": float(z[27]),
                       "residuo_abril_2025": float(resid[27]), "alarmes_t": alarmes,
                       "falsos_alarmes": [a for a in alarmes if a != 28], "z_max_outros": float(np.delete(np.abs(z), 27).max())}
        # robusto: sigma pelos demais meses (sem o próprio mês anômalo)
        sig_rob = np.delete(resid, 27).std(ddof=2)
        res_d[nome]["z_abril_2025_sigma_sem_ele"] = float(resid[27] / sig_rob)
    # previsão com o modelo robusto
    ajuste, b0, b1, resid = modelo_tendencia_sazonal(y, idx_sem_camp)
    sigma = np.delete(resid, 27).std(ddof=2)
    t_f = np.arange(37, 49)
    s_f = idx_sem_camp.to_numpy()
    prev = (b0 + b1 * t_f) * s_f
    li, ls = prev - 1.96 * sigma, prev + 1.96 * sigma
    prev_tab = pd.DataFrame({"mes_ref": [f"2026-{m:02d}" for m in range(1, 13)], "previsao": prev,
                             "li95": li, "ls95": ls})
    salvar_tabela(prev_tab.round(2), "q12d_previsao_2026")
    fig, ax = plt.subplots(figsize=(9, 3.6))
    ax.plot(t, y, "o-", ms=3, color=COR["cinza"], lw=1, label="observado")
    ax.plot(t, ajuste, color=COR["azul"], lw=1.2, label="ajuste tendência × sazonalidade")
    ax.plot(t_f, prev, color=COR["laranja"], lw=1.6, label="previsão 2026")
    ax.fill_between(t_f, li, ls, color=COR["laranja"], alpha=0.2, label="banda 95%")
    ax.fill_between(t, ajuste - 3 * sigma, ajuste + 3 * sigma, color=COR["azul"], alpha=0.08, label="±3σ")
    alarmes = res_d["indices_sem_abril_2025"]["alarmes_t"]
    ax.scatter(alarmes, y.to_numpy()[np.array(alarmes) - 1] if alarmes else [], s=60, facecolors="none",
               edgecolors=COR["vermelho"], lw=1.5, label="alarme 3σ")
    ax.set_xticks(range(1, 49, 3), [f"{MESES[(k - 1) % 12]}/{23 + (k - 1) // 12}" for k in range(1, 49, 3)], fontsize=7.5)
    ax.set_ylabel("Ataques no mês")
    ax.set_title("Q12-d  Previsão de 2026 e detecção de anomalias pela regra dos 3σ")
    ax.legend(fontsize=7.5, ncol=3)
    salvar_figura(fig, "q12d_previsao")

    registrar("q12", {"anual": anual.tolist(), "alpha_ses": float(ses.params["smoothing_level"]),
                      "mm12_inicio": float(mm12.iloc[11]), "mm12_fim": float(mm12.iloc[-1]),
                      "maximo": float(y.max()), "mes_maximo": se.mes_ref.iloc[int(y.idxmax())],
                      "indices": comp.round(4), "mae_indices": float(comp.erro.abs().mean()),
                      "mae_indices_sem": float(comp.erro_sem_abril_2025.abs().mean()),
                      "corr_indices": float(np.corrcoef(comp.indice_estimado, S_PROG)[0, 1]),
                      "corr_indices_sem": float(np.corrcoef(comp.indice_sem_abril_2025, S_PROG)[0, 1]),
                      "acf": [float(v) for v in r], "banda_acf": banda, "d": res_d,
                      "previsao": prev_tab.round(1), "total_2026": float(prev.sum()), "sigma_prev": float(sigma)})


if __name__ == "__main__":
    rodar()
