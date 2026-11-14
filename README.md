# Prova AEDI — Grupo 4

Estudo de caso **ANDI: Risco Cibernético por Simulação de Monte Carlo**
Análise Estatística de Dados e Informações (PPCA/UnB), Prof. João Carlos Félix Souza. Entrega: 04/12/2026.
Grupo 4: Diego Casagrande, Mateus Martins, Silvio Sznifer, Vinícius Chiconato.

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
| `src/q02_*.py` … `src/q14_*.py` | Uma questão por arquivo (Partes B e C) |
| `src/relatorio.py` | Gera relatório, parecer e registro do memorial a partir dos resultados |
| `src/textos_grupo.py` | Textos do grupo: leituras das questões, parecer executivo, decisões e reflexão do memorial |
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

## Entregáveis

| # | Entregável | Onde |
| --- | --- | --- |
| 1 | Código (Partes A, B e C), um único comando | `main.py`, `src/` |
| 2 | Bases | `dados/*.csv` (+ `sha256.json`) |
| 3 | Relatório técnico (Q1–Q14) | `relatorio/relatorio_tecnico.pdf` (e `.docx`, `.md`) |
| 4 | Parecer executivo (Q15) | `relatorio/parecer_executivo.pdf` (e `.docx`, `.md`) |
| 5 | Memorial do Uso de IA | `memorial_ia/registro_interacoes.*` e `memorial_ia/registro.xlsx` (nove campos por interação; decisão do grupo, anexo da conversa e reflexão final a completar pelo grupo) |

`python main.py --grupo 4` roda tudo em cerca de 1 minuto: gerador, questões 1 a 14 (`src/q02_…py` a `src/q14_…py`),
planilha `saidas/resultados.xlsx` (bases + todas as tabelas), resultados numéricos em `saidas/resultados.json`
e os documentos (requer `pandoc` para o DOCX e o Chromium do Playwright para o PDF — `playwright install chromium`; use `--sem-relatorio` para pular essa etapa).

## Andamento

- [x] Parte A — gerador e bases
- [x] Parte B — Q2 a Q13
- [x] Parte C — Q14
- [x] Q15 — parecer executivo
- [x] Leituras do grupo (Q1–Q14), parecer e memorial com os textos do grupo
- [ ] Revisões do grupo (20/11, 27/11 e versão final em 29/11) e anexo da conversa exportada
