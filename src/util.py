"""Utilidades comuns às Partes B e C: caminhos, leitura das bases, gravação de
tabelas, figuras e do dicionário de resultados usado pelo relatório."""
from __future__ import annotations

import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DADOS = os.path.join(RAIZ, "dados")
TABELAS = os.path.join(RAIZ, "saidas", "tabelas")
FIGURAS = os.path.join(RAIZ, "saidas", "figuras")
ARQ_RESULTADOS = os.path.join(RAIZ, "saidas", "resultados.json")

ALFA = 0.05
TIPOS = ["Phishing", "Força bruta", "Malware",
         "Exploração de vulnerabilidade", "DDoS", "Ransomware"]
TIPO_CURTO = {"Phishing": "Phishing", "Força bruta": "Força bruta", "Malware": "Malware",
              "Exploração de vulnerabilidade": "Exploração", "DDoS": "DDoS",
              "Ransomware": "Ransomware"}

plt.rcParams.update({
    "figure.dpi": 110, "savefig.dpi": 160, "font.size": 9.5,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.25, "axes.titlesize": 10.5,
    "axes.titleweight": "bold", "figure.autolayout": True,
    "axes.formatter.use_locale": False,
})
COR = {"azul": "#2563eb", "laranja": "#ea580c", "verde": "#16a34a", "vermelho": "#dc2626",
       "cinza": "#6b7280", "roxo": "#7c3aed"}


def carregar() -> dict[str, pd.DataFrame]:
    b = {n: pd.read_csv(os.path.join(DADOS, f"{n}.csv"))
         for n in ["unidades", "ataques", "perdas", "painel_trimestral", "serie_mensal"]}
    b["lambda"] = pd.read_csv(os.path.join(DADOS, "lambda_programado.csv"))
    return b


def salvar_tabela(df: pd.DataFrame, nome: str, index: bool = False) -> pd.DataFrame:
    os.makedirs(TABELAS, exist_ok=True)
    df.to_csv(os.path.join(TABELAS, f"{nome}.csv"), index=index)
    return df


def salvar_figura(fig, nome: str) -> str:
    os.makedirs(FIGURAS, exist_ok=True)
    caminho = os.path.join(FIGURAS, f"{nome}.png")
    fig.savefig(caminho, bbox_inches="tight")
    plt.close(fig)
    return caminho


def _jsonavel(x):
    if isinstance(x, dict):
        return {str(k): _jsonavel(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_jsonavel(v) for v in x]
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.floating,)):
        return float(x)
    if isinstance(x, (np.bool_,)):
        return bool(x)
    if isinstance(x, pd.DataFrame):
        return _jsonavel(x.to_dict("records"))
    if isinstance(x, pd.Series):
        return _jsonavel(x.to_dict())
    return x


def registrar(questao: str, resultados: dict) -> None:
    """Acrescenta os resultados de uma questão ao arquivo saidas/resultados.json."""
    dados = {}
    if os.path.exists(ARQ_RESULTADOS):
        with open(ARQ_RESULTADOS, encoding="utf-8") as f:
            dados = json.load(f)
    dados[questao] = _jsonavel(resultados)
    with open(ARQ_RESULTADOS, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=1)


def reais(x, casas: int = 0) -> str:
    return fmt(x, casas)


def fmt(x, casas: int = 2) -> str:
    """Número no padrão brasileiro: 1.234,56."""
    s = f"{x:,.{casas}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")
