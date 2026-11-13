# Prova AEDI — Grupo 4

Estudo de caso **ANDI: Risco Cibernético por Simulação de Monte Carlo**
Análise Estatística de Dados e Informações (PPCA/UnB), Prof. João Carlos Félix Souza. Entrega: 09/12/2026.

## Como rodar

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py --grupo 4
```

Semente do gerador: **202604** (= 202600 + 4). Rodar o comando acima recria exatamente as bases de `dados/`;
os hashes sha256 esperados estão em `dados/sha256.json`. Testado com Python 3.13 e as versões de `requirements.txt`.

## Estrutura

| Caminho | Conteúdo |
| --- | --- |
| `main.py` | Executa tudo, em ordem |
| `src/gerador.py` | Parte A: etapas A1–A5 e bases derivadas (Q1-a) |
| `src/inversa.py` | Q1-b: transformação inversa da Exponencial e da Triangular, comparada com numpy |
| `dados/` | `unidades`, `ataques`, `perdas`, `painel_trimestral`, `serie_mensal` (entregáveis) + `lambda_programado.csv` (auxiliar da Q2) |
| `saidas/tabelas/`, `saidas/figuras/` | Tabelas e gráficos do relatório |
| `saidas/resultados.xlsx` | Bases e tabelas em planilha |
| `relatorio/` | Relatório técnico (Q1–Q14) e parecer executivo (Q15) |
| `memorial_ia/` | Memorial do Uso de IA e anexos |

## Decisões de implementação

- Dias do mês pelo calendário real (fevereiro de 2024 com 29 dias).
- `trimestre` = q(t) = ⌈t/3⌉, de 1 a 12 (coerente com o painel de 288 linhas).
- `p_programado` (p_i da Etapa A4) fica como coluna extra de `ataques.csv` e só é usado na verificação (Q2) e nas comparações com o gerador.
- Exponencial e Triangular são sorteadas pela inversa do próprio grupo (`src/inversa.py`); Poisson e Normal, pelo numpy.
- `tempo_deteccao_h` gravado com 4 casas e `perda_rs` com 2; os cálculos internos usam a precisão completa.

## Andamento

- [x] Parte A — gerador e bases
- [x] Q1-b — inversas
- [ ] Q2 a Q13 — Parte B
- [ ] Q14 — Parte C
- [ ] Q15, relatório e memorial
