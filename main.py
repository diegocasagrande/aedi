"""Prova AEDI — Grupo 4. Executa todo o trabalho com um único comando:

    python main.py --grupo 4

Ordem: Parte A (gerador e bases) -> Q1-b -> Parte B (Q2 a Q13) -> Parte C (Q14)
-> planilha de resultados -> relatório técnico, parecer executivo (Q15) e memorial.

Cada questão que sorteia números usa um fluxo próprio, derivado da semente do grupo:
numpy.random.default_rng([semente, número da questão]). Assim as análises nunca
consomem números do gerador das bases, e cada uma é reprodutível isoladamente.
"""
import argparse
import json
import os
import sys
import time

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(RAIZ, "src"))

import pandas as pd  # noqa: E402

import gerador  # noqa: E402
import inversa  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--grupo", type=int, default=4)
    ap.add_argument("--sem-relatorio", action="store_true", help="não gera relatório/parecer (só dados e análises)")
    args = ap.parse_args()
    semente = gerador.semente(args.grupo)
    print(f"Grupo {args.grupo} — semente {semente}")
    t0 = time.time()

    # Parte A — gerador
    bases = gerador.gerar(args.grupo)
    hashes = gerador.salvar(bases, os.path.join(RAIZ, "dados"))
    with open(os.path.join(RAIZ, "dados", "sha256.json"), "w") as f:
        json.dump(hashes, f, indent=2)
    print(f"[A] bases: {len(bases.ataques)} ataques, {len(bases.perdas)} perdas")

    os.makedirs(os.path.join(RAIZ, "saidas", "tabelas"), exist_ok=True)
    res = os.path.join(RAIZ, "saidas", "resultados.json")
    if os.path.exists(res):
        os.remove(res)

    # Q1-b — inversa do grupo x biblioteca
    tab = inversa.comparar_com_biblioteca(semente=semente)
    tab.to_csv(os.path.join(RAIZ, "saidas", "tabelas", "q01b_inversa_vs_numpy.csv"), index=False)
    from util import registrar
    registrar("q01", {"inversa": tab.round(4), "semente": semente, "grupo": args.grupo, "hashes": hashes})

    # Parte B
    import q02_verificacao, q03_descritiva, q04_dispersao, q05_probabilidade, q06_distribuicoes  # noqa: E401
    import q07_estimacao, q08_testes, q09_regressao_simples, q10_inferencia_regressao  # noqa: E401
    import q11_regressao_multipla, q12_series, q13_classificacao  # noqa: E401
    for m in [q02_verificacao, q03_descritiva, q04_dispersao, q05_probabilidade, q06_distribuicoes]:
        m.rodar()
        print(f"[B] {m.__name__} ok")
    q07_estimacao.rodar(semente)
    for m in [q08_testes, q09_regressao_simples, q10_inferencia_regressao]:
        m.rodar()
        print(f"[B] {m.__name__} ok")
    q11_regressao_multipla.rodar(semente)
    q12_series.rodar()
    q13_classificacao.rodar(semente)
    print("[B] q11, q12, q13 ok")

    # Parte C
    import q14_smc_risco
    q14_smc_risco.rodar(semente)
    print("[C] q14 ok")

    # Planilha com as bases e todas as tabelas
    tdir = os.path.join(RAIZ, "saidas", "tabelas")
    with pd.ExcelWriter(os.path.join(RAIZ, "saidas", "resultados.xlsx")) as xw:
        for nome in ["unidades", "ataques", "perdas", "painel_trimestral", "serie_mensal"]:
            getattr(bases, nome).to_excel(xw, sheet_name=nome, index=False)
        for arq in sorted(os.listdir(tdir)):
            if arq.endswith(".csv"):
                pd.read_csv(os.path.join(tdir, arq)).to_excel(xw, sheet_name=arq[:-4][:31], index=False)

    if not args.sem_relatorio:
        import relatorio
        relatorio.gerar()
        print("[Q15] relatório, parecer e memorial gerados")
    print(f"Concluído em {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
