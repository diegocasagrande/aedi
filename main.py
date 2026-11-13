"""Prova AEDI — Grupo 3. Executa todo o trabalho com um único comando:

    python main.py --grupo 3

Etapas já implementadas: Parte A (gerador + bases) e Q1-b (inversas).
As análises das Partes B e C entram em src/qNN_*.py e são chamadas aqui, em ordem.
"""
import argparse
import json
import os
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(RAIZ, "src"))

import gerador  # noqa: E402
import inversa  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--grupo", type=int, default=3)
    args = ap.parse_args()

    print(f"Grupo {args.grupo} — semente {gerador.semente(args.grupo)}")

    # Parte A — gerador
    bases = gerador.gerar(args.grupo)
    hashes = gerador.salvar(bases, os.path.join(RAIZ, "dados"))
    with open(os.path.join(RAIZ, "dados", "sha256.json"), "w") as f:
        json.dump(hashes, f, indent=2)
    print(f"Bases: {len(bases.ataques)} ataques, {len(bases.perdas)} perdas")

    # Q1-b — inversa do grupo x biblioteca
    os.makedirs(os.path.join(RAIZ, "saidas", "tabelas"), exist_ok=True)
    inversa.comparar_com_biblioteca(semente=gerador.semente(args.grupo)).to_csv(
        os.path.join(RAIZ, "saidas", "tabelas", "q01b_inversa_vs_numpy.csv"), index=False)

    # Planilha com as bases (atende "Planilha Excel"); tabelas das questões entram depois
    with __import__("pandas").ExcelWriter(os.path.join(RAIZ, "saidas", "resultados.xlsx")) as xw:
        for nome in ["unidades", "ataques", "perdas", "painel_trimestral", "serie_mensal"]:
            getattr(bases, nome).to_excel(xw, sheet_name=nome, index=False)

    # Partes B e C: a implementar (q02_verificacao.py ... q14_smc_risco.py)


if __name__ == "__main__":
    main()
