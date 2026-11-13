"""Questão 1-b — Transformação inversa F^-1(U), implementada pelo grupo.

Se U ~ Uniforme(0, 1) e F é a função de distribuição acumulada de X,
então X = F^-1(U) tem distribuição F (Seção 12.5 do livro).
"""
from __future__ import annotations

import numpy as np


def exponencial_inversa(u, theta):
    """Exponencial com média theta.
    F(t) = 1 - exp(-t/theta)  =>  F^-1(u) = -theta * ln(1 - u)."""
    u = np.asarray(u, dtype=float)
    return -theta * np.log1p(-u)


def triangular_inversa(u, a, c, b):
    """Triangular com mínimo a, moda c e máximo b.
    F(x) = (x-a)^2 / ((b-a)(c-a))            para a <= x <= c
    F(x) = 1 - (b-x)^2 / ((b-a)(b-c))        para c <  x <= b
    Com F_c = (c-a)/(b-a):
    F^-1(u) = a + sqrt(u (b-a)(c-a))          se u <  F_c
    F^-1(u) = b - sqrt((1-u)(b-a)(b-c))       se u >= F_c
    """
    u = np.asarray(u, dtype=float)
    a, c, b = (np.broadcast_to(np.asarray(v, dtype=float), u.shape) for v in (a, c, b))
    fc = (c - a) / (b - a)
    esquerda = a + np.sqrt(u * (b - a) * (c - a))
    direita = b - np.sqrt((1 - u) * (b - a) * (b - c))
    return np.where(u < fc, esquerda, direita)


def comparar_com_biblioteca(n: int = 100_000, semente: int = 202603) -> "pd.DataFrame":
    """Compara a inversa do grupo com numpy (quantis e teste KS de duas amostras)."""
    import pandas as pd
    from scipy import stats

    rng = np.random.default_rng(semente)
    casos = {
        "Exponencial(θ=4)": (exponencial_inversa(rng.random(n), 4.0), rng.exponential(4.0, n)),
        "Exponencial(θ=12)": (exponencial_inversa(rng.random(n), 12.0), rng.exponential(12.0, n)),
        "Triangular(60;80;95)": (triangular_inversa(rng.random(n), 60, 80, 95),
                                 rng.triangular(60, 80, 95, n)),
        "Triangular(5;7,5;10)": (triangular_inversa(rng.random(n), 5, 7.5, 10),
                                 rng.triangular(5, 7.5, 10, n)),
    }
    linhas = []
    for nome, (nosso, lib) in casos.items():
        ks = stats.ks_2samp(nosso, lib)
        linha = {"distribuicao": nome, "media_grupo": nosso.mean(), "media_numpy": lib.mean()}
        for q in (0.05, 0.50, 0.95):
            linha[f"q{int(q*100)}_grupo"] = np.quantile(nosso, q)
            linha[f"q{int(q*100)}_numpy"] = np.quantile(lib, q)
        linha.update({"ks_estatistica": ks.statistic, "ks_p_valor": ks.pvalue})
        linhas.append(linha)
    return pd.DataFrame(linhas)


if __name__ == "__main__":
    import pandas as pd
    pd.set_option("display.width", 200)
    print(comparar_com_biblioteca().round(4).to_string(index=False))
