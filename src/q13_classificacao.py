"""Questão 13 — Classificação (cap. 11, Parte B). Treino 2023–2024, teste 2025."""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score, precision_score, recall_score,
                             roc_auc_score, roc_curve)
from sklearn.tree import DecisionTreeClassifier, export_text

from util import COR, TABELAS, carregar, registrar, salvar_figura, salvar_tabela

PROGRAMADOS = {"Intercept": -2.8, "cvss": 0.45, "tempo_deteccao_h": 0.06, "soc": -0.80,
               "treino": -0.08, "fora_expediente": 0.50}
FORMULA = "materializou ~ cvss + tempo_deteccao_h + soc + treino + fora_expediente"
X_ARV = ["cvss", "tempo_deteccao_h", "soc", "treino", "fora_expediente"]


def base_classificacao():
    b = carregar()
    at = b["ataques"].merge(b["unidades"][["unidade", "soc", "treino"]], on="unidade")
    return at, b["perdas"]


def ajustar(at):
    """Logística usada também na Q14 (treino 2023–2024)."""
    return smf.logit(FORMULA, data=at[at.ano <= 2024]).fit(disp=0)


def metricas(y, p, lim=0.5):
    yhat = (p >= lim).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, yhat).ravel()
    return {"VN": int(tn), "FP": int(fp), "FN": int(fn), "VP": int(tp),
            "acuracia": accuracy_score(y, yhat), "precisao": precision_score(y, yhat, zero_division=0),
            "recall": recall_score(y, yhat), "f1": f1_score(y, yhat), "auc": roc_auc_score(y, p)}


def rodar(semente: int):
    at, pe = base_classificacao()
    tr, te = at[at.ano <= 2024].copy(), at[at.ano == 2025].copy()

    # a) logística
    m = ajustar(at)
    ic = m.conf_int()
    tab = pd.DataFrame({"coeficiente": m.params, "erro_padrao": m.bse, "z": m.tvalues, "p_valor": m.pvalues,
                        "ic95_inf": ic[0], "ic95_sup": ic[1], "razao_chances": np.exp(m.params),
                        "programado": pd.Series(PROGRAMADOS)})
    tab["contem_programado"] = (tab.ic95_inf <= tab.programado) & (tab.programado <= tab.ic95_sup)
    salvar_tabela(tab.round(4).reset_index().rename(columns={"index": "termo"}), "q13a_logistica")

    # b) com dummies de tipo
    mb = smf.logit(FORMULA + " + C(tipo, Treatment(reference='Phishing'))", data=tr).fit(disp=0)
    lr = 2 * (mb.llf - m.llf)
    gl = int(mb.df_model - m.df_model)
    p_lr = 1 - stats.chi2.cdf(lr, gl)
    dum = mb.params.filter(like="C(tipo")
    dum_p = mb.pvalues.filter(like="C(tipo")
    tab_b = pd.DataFrame({"coeficiente": dum.values, "p_valor": dum_p.values},
                         index=[i.split("[T.")[1].rstrip("]") for i in dum.index])
    salvar_tabela(tab_b.round(4).reset_index().rename(columns={"index": "tipo"}), "q13b_dummies_tipo")
    # sem cvss, as dummies absorvem o efeito do cvss
    m_sem_cvss = smf.logit("materializou ~ tempo_deteccao_h + soc + treino + fora_expediente"
                           " + C(tipo, Treatment(reference='Phishing'))", data=tr).fit(disp=0)
    p_sem_cvss = m_sem_cvss.pvalues.filter(like="C(tipo")

    # c) árvore de decisão (profundidade 3)
    arv = DecisionTreeClassifier(max_depth=3, random_state=int(np.random.default_rng([semente, 13]).integers(1e6)))
    arv.fit(tr[X_ARV], tr.materializou)
    regras = export_text(arv, feature_names=X_ARV, show_weights=True, decimals=2)
    with open(TABELAS + "/q13c_regras_arvore.txt", "w", encoding="utf-8") as f:
        f.write(regras)
    folhas = []
    for no in range(arv.tree_.node_count):
        if arv.tree_.children_left[no] == -1:
            v = arv.tree_.value[no][0]
            folhas.append({"no": no, "n": int(arv.tree_.n_node_samples[no]), "p_materializa": float(v[1] / v.sum())})

    # d) avaliação no teste
    p_log = m.predict(te)
    p_arv = arv.predict_proba(te[X_ARV])[:, 1]
    res_d = {"logistica": metricas(te.materializou, p_log), "arvore": metricas(te.materializou, p_arv)}
    salvar_tabela(pd.DataFrame(res_d).T.round(4).reset_index().rename(columns={"index": "modelo"}), "q13d_metricas_teste")
    fig, ax = plt.subplots(figsize=(4.6, 4.2))
    for nome, p, cor in [("Logística", p_log, COR["azul"]), ("Árvore (prof. 3)", p_arv, COR["laranja"])]:
        fpr, tpr, _ = roc_curve(te.materializou, p)
        ax.plot(fpr, tpr, color=cor, lw=1.6, label=f"{nome}: AUC = {roc_auc_score(te.materializou, p):.3f}".replace(".", ","))
    ax.plot([0, 1], [0, 1], "--", color=COR["cinza"], lw=1)
    ax.set_xlabel("Taxa de falsos positivos (1 − especificidade)")
    ax.set_ylabel("Taxa de verdadeiros positivos (recall)")
    ax.set_title("Q13-d  Curva ROC no teste (2025)")
    ax.legend(fontsize=8, loc="lower right")
    salvar_figura(fig, "q13d_roc")

    # e) limiar de custo mínimo (escolhido no treino, avaliado no teste)
    c_fn = float(pe.loc[pd.to_datetime(pe.data).dt.year <= 2024, "perda_rs"].median())
    c_fp = 3000.0
    lims = np.round(np.arange(0.01, 1.0, 0.01), 2)

    def custo(y, p):
        return np.array([((p < l) & (y == 1)).sum() * c_fn + ((p >= l) & (y == 0)).sum() * c_fp for l in lims])

    custo_tr = custo(tr.materializou.to_numpy(), m.predict(tr).to_numpy())
    custo_te = custo(te.materializou.to_numpy(), p_log.to_numpy())
    l_otimo = float(lims[np.argmin(custo_tr)])
    l_teorico = c_fp / (c_fp + c_fn)
    i05 = int(np.where(lims == 0.5)[0][0])
    i_ot = int(np.argmin(custo_tr))
    fig, ax = plt.subplots(figsize=(6, 3.3))
    ax.plot(lims, custo_te / 1e6, color=COR["azul"], lw=1.5, label="custo no teste (2025)")
    ax.axvline(l_otimo, color=COR["verde"], ls="--", lw=1, label=f"limiar ótimo (treino) = {l_otimo:.2f}".replace(".", ","))
    ax.axvline(0.5, color=COR["cinza"], ls=":", lw=1, label="limiar 0,5")
    ax.set_xlabel("Limiar de decisão")
    ax.set_ylabel("Custo esperado (R$ milhões)")
    ax.set_title("Q13-e  Custo total de erros × limiar (logística)")
    ax.legend(fontsize=8)
    salvar_figura(fig, "q13e_limiar_custo")

    registrar("q13", {
        "n_treino": len(tr), "n_teste": len(te), "a": tab.round(4).reset_index().rename(columns={"index": "termo"}),
        "pseudo_r2": m.prsquared, "llr_p": m.llr_pvalue,
        "b": {"dummies": tab_b.round(4).reset_index().rename(columns={"index": "tipo"}), "lr": lr, "gl": gl,
              "p": p_lr, "p_dummies_sem_cvss": p_sem_cvss.round(6).to_dict()},
        "c": {"regras": regras, "folhas": folhas,
              "importancias": dict(zip(X_ARV, arv.feature_importances_.round(4)))},
        "d": res_d,
        "e": {"c_fn": c_fn, "c_fp": c_fp, "limiar_otimo_treino": l_otimo, "limiar_teorico": l_teorico,
              "custo_teste_05": float(custo_te[i05]), "custo_teste_otimo": float(custo_te[i_ot]),
              "metricas_otimo": metricas(te.materializou, p_log, l_otimo),
              "economia": float(custo_te[i05] - custo_te[i_ot])}})


if __name__ == "__main__":
    rodar(202604)
