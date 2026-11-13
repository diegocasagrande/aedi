"""Questão 3 — Dos dados à decisão (cap. 1)."""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from util import COR, TIPOS, carregar, registrar, salvar_figura, salvar_tabela

CLASSIFICACAO = [
    ("ataques", "id_ataque", "Qualitativa nominal (identificador)", "Chave primária"),
    ("ataques", "unidade", "Qualitativa nominal", "Chave estrangeira para unidades"),
    ("ataques", "data", "Quantitativa (tempo); tratada como data", "Carimbo temporal"),
    ("ataques", "ano", "Quantitativa discreta (ou ordinal)", "Derivada de data"),
    ("ataques", "mes", "Qualitativa ordinal (cíclica)", "Derivada de data"),
    ("ataques", "trimestre", "Quantitativa discreta (índice de tempo q = 1..12)", "Derivada de data"),
    ("ataques", "tipo", "Qualitativa nominal", "Categoria"),
    ("ataques", "fora_expediente", "Qualitativa nominal dicotômica (0/1)", "Indicador"),
    ("ataques", "cvss", "Quantitativa contínua (registrada com 1 casa)", "Escore 0–10"),
    ("ataques", "tempo_deteccao_h", "Quantitativa contínua", "Horas"),
    ("ataques", "materializou", "Qualitativa nominal dicotômica (0/1)", "Variável-resposta da Q13"),
    ("perdas", "id_perda / id_ataque", "Qualitativa nominal (identificadores)", "Chaves"),
    ("perdas", "unidade, tipo", "Qualitativa nominal", "Categorias"),
    ("perdas", "data", "Quantitativa (tempo)", "Carimbo temporal"),
    ("perdas", "tempo_deteccao_h", "Quantitativa contínua", "Horas"),
    ("perdas", "perda_rs", "Quantitativa contínua", "Reais; assimétrica à direita"),
]


def rodar():
    b = carregar()
    at, pe = b["ataques"], b["perdas"]
    salvar_tabela(pd.DataFrame(CLASSIFICACAO, columns=["base", "coluna", "tipo_de_variavel", "papel"]),
                  "q03a_classificacao")

    # b) frequências do tipo (ordenadas da mais à menos frequente)
    f = at.tipo.value_counts().rename_axis("tipo").reset_index(name="freq_absoluta")
    f["freq_relativa"] = f.freq_absoluta / f.freq_absoluta.sum()
    f["freq_abs_acumulada"] = f.freq_absoluta.cumsum()
    f["freq_rel_acumulada"] = f.freq_relativa.cumsum()
    salvar_tabela(f.round(4), "q03b_freq_tipo")

    # classes de perda pela regra de Sturges
    x = pe.perda_rs.to_numpy()
    n = len(x)
    k = int(round(1 + 3.322 * np.log10(n)))
    bordas = np.linspace(x.min(), x.max(), k + 1)
    cont, _ = np.histogram(x, bordas)
    classes = pd.DataFrame({"classe": [f"{bordas[i]:,.0f} |– {bordas[i+1]:,.0f}" for i in range(k)],
                            "lim_inf": bordas[:-1], "lim_sup": bordas[1:], "ponto_medio": (bordas[:-1] + bordas[1:]) / 2,
                            "freq_absoluta": cont})
    classes["freq_relativa"] = classes.freq_absoluta / n
    classes["freq_rel_acumulada"] = classes.freq_relativa.cumsum()
    salvar_tabela(classes.round(4), "q03b_classes_perda")

    fig, ax = plt.subplots(1, 2, figsize=(9, 3.4))
    ax[0].hist(x / 1e3, bins=bordas / 1e3, color=COR["azul"], edgecolor="white")
    ax[0].set_title(f"Perda por incidente — {k} classes (Sturges)")
    ax[0].set_xlabel("Perda (R$ mil)")
    ax[0].set_ylabel("Frequência")
    ax[1].hist(np.log10(x), bins=k, color=COR["laranja"], edgecolor="white")
    ax[1].set_title("A mesma variável em escala log10")
    ax[1].set_xlabel("log10(perda em R$)")
    salvar_figura(fig, "q03b_histograma_perda")

    # c) média, mediana e moda (classe modal pela regra de Sturges) por tipo e geral
    def moda_classe(v):
        kk = int(round(1 + 3.322 * np.log10(len(v))))
        c, e = np.histogram(v, kk)
        i = int(np.argmax(c))
        return (e[i] + e[i + 1]) / 2

    linhas = []
    for t in TIPOS + ["Geral"]:
        v = x if t == "Geral" else pe.loc[pe.tipo == t, "perda_rs"].to_numpy()
        linhas.append({"tipo": t, "n": len(v), "media": v.mean(), "mediana": np.median(v),
                       "moda_classe_modal": moda_classe(v), "media_sobre_mediana": v.mean() / np.median(v)})
        # moda bruta não existe: valores contínuos não se repetem
    tc = pd.DataFrame(linhas)
    salvar_tabela(tc.round(2), "q03c_centrais")

    registrar("q03", {"n_ataques": len(at), "n_perdas": n, "k_sturges": k,
                      "amplitude_classe": float(bordas[1] - bordas[0]),
                      "primeira_classe_freq": float(classes.freq_relativa.iloc[0]),
                      "duas_primeiras_freq": float(classes.freq_relativa.iloc[:2].sum()),
                      "freq_tipo": f.round(4), "classes": classes.round(2), "centrais": tc.round(2),
                      "valores_repetidos": int(pd.Series(x).duplicated().sum())})


if __name__ == "__main__":
    rodar()
