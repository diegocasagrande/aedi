"""Parte A — Modelo gerador (Simulação de Monte Carlo dos dados).

Prova AEDI — Estudo de caso ANDI. Grupo 4, semente = 202600 + 4 = 202604.

Organização pelos quatro passos da Seção 12.2 do livro (Questão 1-a):
  PASSO 1 — MODELAR  : constantes e equações das etapas A1 a A5 (bloco PARAMETROS).
  PASSO 2 — SORTEAR  : funções etapa_a1 ... etapa_a5, todas a partir de um único
                       gerador uniforme rng (numpy.random.Generator, PCG64).
  PASSO 3 — CALCULAR : montagem das bases e das agregações derivadas
                       (painel_trimestral e serie_mensal).
  PASSO 4 — ANALISAR : feito na Questão 2 (verificação do gerador), em outro módulo.

Como cada distribuição é sorteada a partir de U ~ Uniforme(0, 1) (Questão 1-b):
  - Uniforme discreta {a..b}  : a + floor(U * (b - a + 1))
  - Uniforme contínua (a, b)  : a + U * (b - a)
  - Bernoulli(p)              : 1 se U < p
  - Categórica (tipo)         : primeiro k com U < F(k), F = probabilidades acumuladas
  - Triangular(a; c; b)       : transformação inversa implementada em inversa.py
  - Exponencial(média theta)  : transformação inversa T = -theta * ln(1 - U), em inversa.py
  - Poisson(lambda)           : rng.poisson (numpy usa inversão/PTRS sobre uniformes)
  - Normal(0; sigma)          : rng.normal (numpy usa o método ziggurat sobre uniformes)

Ordem dos sorteios (fixa; mudá-la muda as bases):
  A1 para as 24 unidades -> para cada mês t = 1..36: N de todas as unidades ->
  para cada unidade com N > 0, na ordem 1..24: dia, tipo, fora_expediente, cvss,
  tempo, materialização e, só para os materializados, o erro da severidade.

Decisões registradas no roteiro do grupo:
  - dias do mês pelo calendário real (fevereiro de 2024 tem 29 dias);
  - coluna 'trimestre' = q(t) de 1 a 12;
  - p_i programado guardado na coluna extra 'p_programado' (não usada na Parte B).
"""
from __future__ import annotations

import calendar
from dataclasses import dataclass

import numpy as np
import pandas as pd

try:  # execução como pacote (python -m src.gerador) ou a partir de main.py
    from .inversa import exponencial_inversa, triangular_inversa
except ImportError:  # execução direta
    from inversa import exponencial_inversa, triangular_inversa

# --------------------------------------------------------------------------
# PASSO 1 — MODELAR: parâmetros "verdadeiros" do gerador (enunciado, Parte A)
# --------------------------------------------------------------------------
GRUPO = 4
SEMENTE_BASE = 202600
N_UNIDADES = 24
N_MESES = 36
ANO_INICIAL = 2023

# Etapa A2 — regressão da taxa trimestral (Seção 10.7 + tendência)
BETA_LAMBDA = {"const": 8.0, "servicos": 0.50, "patch": -0.08,
               "treino": -0.20, "soc": -1.40, "q": 0.15}
SAZONAL = np.array([0.90, 0.85, 1.10, 1.10, 1.00, 0.95,
                    0.90, 0.95, 1.00, 1.05, 1.15, 1.05])  # S_m, média 1
T_CAMPANHA, C_CAMPANHA = 28, 1.8  # abril de 2025

# Etapa A3 — atributos do ataque
TIPOS = ["Phishing", "Força bruta", "Malware",
         "Exploração de vulnerabilidade", "DDoS", "Ransomware"]
P_TIPO = np.array([0.35, 0.20, 0.15, 0.15, 0.10, 0.05])
CVSS_TRI = np.array([[2, 5, 8], [2, 4, 7], [4, 6, 9],
                     [5, 7.5, 10], [3, 5, 8], [6, 8.5, 10]], dtype=float)  # mín, moda, máx
MEDIANA_PERDA = np.array([15_000, 10_000, 30_000, 45_000, 25_000, 150_000], dtype=float)
P_FORA = 0.35
THETA_SOC, THETA_SEM_SOC, FATOR_FORA = 4.0, 12.0, 1.5

# Etapa A4 — materialização (logística)
BETA_LOGIT = {"const": -2.8, "cvss": 0.45, "tempo": 0.06,
              "soc": -0.80, "treino": -0.08, "fora": 0.50}

# Etapa A5 — severidade (Lognormal condicional)
BETA_TEMPO_SEV, SIGMA_EPS = 0.02, 0.9  # 0,9 é o desvio-padrão (variância 0,81)


@dataclass
class Bases:
    unidades: pd.DataFrame
    ataques: pd.DataFrame
    perdas: pd.DataFrame
    painel_trimestral: pd.DataFrame
    serie_mensal: pd.DataFrame
    lambdas: pd.DataFrame  # lambda_(u,t) programado, para a Questão 2


def semente(grupo: int = GRUPO) -> int:
    return SEMENTE_BASE + grupo


def calendario(t: int) -> tuple[int, int, int]:
    """Converte t (1..36) em (ano, mês do calendário m(t), trimestre q(t))."""
    ano = ANO_INICIAL + (t - 1) // 12
    mes = (t - 1) % 12 + 1
    q = -(-t // 3)  # teto de t/3
    return ano, mes, q


def lambda_trimestral(servicos, patch, treino, soc, q):
    b = BETA_LAMBDA
    return (b["const"] + b["servicos"] * servicos + b["patch"] * patch
            + b["treino"] * treino + b["soc"] * soc + b["q"] * q)


# --------------------------------------------------------------------------
# PASSO 2 — SORTEAR
# --------------------------------------------------------------------------
def etapa_a1(rng: np.random.Generator) -> pd.DataFrame:
    """A1 — perfil das 24 unidades (fixo nos 36 meses)."""
    u = rng.random(N_UNIDADES)
    servicos = 10 + np.floor(u * 21).astype(int)                 # Uniforme discreta {10..30}
    patch = triangular_inversa(rng.random(N_UNIDADES), 60, 80, 95)  # Triangular(60; 80; 95)
    treino = 0 + rng.random(N_UNIDADES) * 12                     # Uniforme(0; 12)
    soc = (rng.random(N_UNIDADES) < 0.40).astype(int)            # Bernoulli(0,40)
    return pd.DataFrame({"unidade": np.arange(1, N_UNIDADES + 1), "servicos": servicos,
                         "patch": patch, "treino": treino, "soc": soc})


def etapa_a3_a5(rng, n, unidade_row, ano, mes):
    """A3 (atributos), A4 (materialização) e A5 (severidade) para os n ataques
    de uma unidade num mês. Retorna dicionário de colunas."""
    dias_mes = calendar.monthrange(ano, mes)[1]
    dia = 1 + np.floor(rng.random(n) * dias_mes).astype(int)          # Uniforme discreta
    tipo = np.searchsorted(np.cumsum(P_TIPO), rng.random(n), side="right")  # Categórica
    tipo = np.minimum(tipo, len(TIPOS) - 1)
    fora = (rng.random(n) < P_FORA).astype(int)                        # Bernoulli(0,35)
    tri = CVSS_TRI[tipo]
    cvss = np.round(triangular_inversa(rng.random(n), tri[:, 0], tri[:, 1], tri[:, 2]), 1)
    theta = THETA_SOC if unidade_row.soc == 1 else THETA_SEM_SOC
    tempo = exponencial_inversa(rng.random(n), theta) * np.where(fora == 1, FATOR_FORA, 1.0)

    b = BETA_LOGIT
    logit = (b["const"] + b["cvss"] * cvss + b["tempo"] * tempo + b["soc"] * unidade_row.soc
             + b["treino"] * unidade_row.treino + b["fora"] * fora)
    p = 1.0 / (1.0 + np.exp(-logit))
    materializou = (rng.random(n) < p).astype(int)                     # Bernoulli(p_i)

    perda = np.full(n, np.nan)
    idx = np.flatnonzero(materializou)
    if idx.size:
        eps = rng.normal(0.0, SIGMA_EPS, idx.size)
        perda[idx] = np.exp(np.log(MEDIANA_PERDA[tipo[idx]])
                            + BETA_TEMPO_SEV * tempo[idx] + eps)
    return {"dia": dia, "tipo_idx": tipo, "fora_expediente": fora, "cvss": cvss,
            "tempo_deteccao_h": tempo, "p_programado": p,
            "materializou": materializou, "perda_rs": perda}


def gerar(grupo: int = GRUPO) -> Bases:
    rng = np.random.default_rng(semente(grupo))
    unidades = etapa_a1(rng)

    blocos, lambdas = [], []
    for t in range(1, N_MESES + 1):
        ano, mes, q = calendario(t)
        c_t = C_CAMPANHA if t == T_CAMPANHA else 1.0
        lam_trim = lambda_trimestral(unidades.servicos, unidades.patch,
                                     unidades.treino, unidades.soc, q).to_numpy()
        assert (lam_trim > 0).all()
        lam = lam_trim / 3 * SAZONAL[mes - 1] * c_t                  # A2
        n_ataques = rng.poisson(lam)                                 # N ~ Poisson
        lambdas.append(pd.DataFrame({"unidade": unidades.unidade, "t": t, "ano": ano,
                                     "mes": mes, "trimestre": q, "lambda": lam,
                                     "n_ataques": n_ataques}))
        for i, row in enumerate(unidades.itertuples(index=False)):
            n = int(n_ataques[i])
            if n == 0:
                continue
            cols = etapa_a3_a5(rng, n, row, ano, mes)
            cols.update({"unidade": row.unidade, "t": t, "ano": ano, "mes": mes, "trimestre": q})
            blocos.append(pd.DataFrame(cols))

    # ----------------------------------------------------------------------
    # PASSO 3 — CALCULAR: bases entregues
    # ----------------------------------------------------------------------
    at = pd.concat(blocos, ignore_index=True)
    at.insert(0, "id_ataque", np.arange(1, len(at) + 1))
    at["data"] = pd.to_datetime(dict(year=at.ano, month=at.mes, day=at.dia)).dt.strftime("%Y-%m-%d")
    at["tipo"] = np.array(TIPOS)[at.tipo_idx]
    at["cvss"] = at.cvss.round(1)
    at["tempo_deteccao_h"] = at.tempo_deteccao_h.round(4)

    ataques = at[["id_ataque", "unidade", "data", "ano", "mes", "trimestre", "tipo",
                  "fora_expediente", "cvss", "tempo_deteccao_h", "materializou",
                  "p_programado"]].copy()

    pe = at.loc[at.materializou == 1].copy()
    pe.insert(0, "id_perda", np.arange(1, len(pe) + 1))
    pe["perda_rs"] = pe.perda_rs.round(2)
    perdas = pe[["id_perda", "id_ataque", "unidade", "data", "tipo",
                 "tempo_deteccao_h", "perda_rs"]].reset_index(drop=True)

    # painel unidade x trimestre (288 linhas, inclusive trimestres sem ataques)
    grade = pd.MultiIndex.from_product([unidades.unidade, range(1, 13)],
                                       names=["unidade", "trimestre"]).to_frame(index=False)
    ag = at.groupby(["unidade", "trimestre"]).agg(
        n_ataques=("id_ataque", "size"), n_perdas=("materializou", "sum"),
        perda_total=("perda_rs", lambda s: s.sum(min_count=0))).reset_index()
    painel = grade.merge(ag, how="left", on=["unidade", "trimestre"])
    painel[["n_ataques", "n_perdas"]] = painel[["n_ataques", "n_perdas"]].fillna(0).astype(int)
    painel["perda_total"] = painel.perda_total.fillna(0.0).round(2)
    painel = painel.merge(unidades, on="unidade")

    # série mensal (36 linhas)
    meses = pd.DataFrame({"t": range(1, N_MESES + 1)})
    meses["mes_ref"] = [f"{calendario(t)[0]}-{calendario(t)[1]:02d}" for t in meses.t]
    agm = at.groupby("t").agg(n_ataques=("id_ataque", "size"),
                              n_perdas=("materializou", "sum"),
                              perda_total=("perda_rs", lambda s: s.sum(min_count=0))).reset_index()
    serie = meses.merge(agm, how="left", on="t").fillna(0)
    serie[["n_ataques", "n_perdas"]] = serie[["n_ataques", "n_perdas"]].astype(int)
    serie["perda_total"] = serie.perda_total.round(2)
    serie = serie[["mes_ref", "n_ataques", "n_perdas", "perda_total"]]

    return Bases(unidades=unidades, ataques=ataques, perdas=perdas,
                 painel_trimestral=painel[["unidade", "trimestre", "n_ataques", "n_perdas",
                                           "perda_total", "servicos", "patch", "treino", "soc"]],
                 serie_mensal=serie, lambdas=pd.concat(lambdas, ignore_index=True))


def salvar(bases: Bases, pasta: str) -> dict[str, str]:
    """Grava as cinco bases e devolve o sha256 de cada arquivo."""
    import hashlib
    import os
    os.makedirs(pasta, exist_ok=True)
    saida = {}
    for nome in ["unidades", "ataques", "perdas", "painel_trimestral", "serie_mensal"]:
        caminho = os.path.join(pasta, f"{nome}.csv")
        getattr(bases, nome).to_csv(caminho, index=False)
        with open(caminho, "rb") as f:
            saida[nome] = hashlib.sha256(f.read()).hexdigest()
    bases.lambdas.to_csv(os.path.join(pasta, "lambda_programado.csv"), index=False)
    return saida


if __name__ == "__main__":
    b = gerar()
    print(salvar(b, "dados"))
