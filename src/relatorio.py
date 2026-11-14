"""Gera o relatório técnico (Q1–Q14), o parecer executivo (Q15) e o registro do
memorial de IA a partir de saidas/resultados.json e das tabelas e figuras.

Todos os números do texto vêm dos resultados calculados pelo código: rodar de novo
com a mesma semente reproduz o mesmo relatório."""
from __future__ import annotations

import json
import os
import subprocess

import numpy as np
import pandas as pd
from scipy import stats

import sugestoes
from util import ARQ_RESULTADOS, FIGURAS, RAIZ, TABELAS, TIPOS, carregar, fmt

REL = os.path.join(RAIZ, "relatorio")


# ------------------------------------------------------------------ formatação
def f(x, d=2):
    return fmt(float(x), d).replace("-", "−")


def pct(x, d=1):
    return fmt(100 * float(x), d) + "%"


def mi(x, d=1):
    return "R$ " + fmt(float(x) / 1e6, d) + " mi"


def rs(x, d=0):
    return "R$ " + fmt(float(x), d)


def pv(p):
    p = float(p)
    if p < 0.0001:
        return "< 0,0001"
    return fmt(p, 4)


def tabela(linhas: list[list], cab: list[str], alin: str | None = None) -> str:
    """Tabela pipe do pandoc; a largura relativa das colunas segue o maior conteúdo."""
    alin = alin or "l" + "r" * (len(cab) - 1)
    curto = {"Exploração de vulnerabilidade": "Exploração", "Intercept": "Intercepto"}
    linhas = [[curto.get(str(c), str(c)) for c in li] for li in linhas]
    larg = []
    for j, h in enumerate(cab):
        palavras = [w for li in linhas for w in li[j].split()] + str(h).split()
        maior_palavra = max([len(w) for w in palavras] + [3])
        conteudo = max([len(li[j]) for li in linhas] + [min(len(str(h)), 14)])
        larg.append(max(9, maior_palavra + 3, min(conteudo + 3, 60)))
    sep = [("-" * (w - 1) + ":") if a == "r" else (":" + "-" * (w - 2) + ":") if a == "c" else (":" + "-" * (w - 1))
           for a, w in zip(alin, larg)]
    out = ["| " + " | ".join(cab) + " |", "| " + " | ".join(sep) + " |"]
    for li in linhas:
        out.append("| " + " | ".join(li) + " |")
    return "\n".join(out) + "\n"


def escapar_sublinhados(md: str) -> str:
    """Escapa '_' fora de código e de imagens, para o pandoc não ler ênfase (ex.: p̄_u, w_(u,k))."""
    out = []
    for li in md.split("\n"):
        if li.startswith("![") or li.startswith("title:") or li.startswith("author:"):
            out.append(li)
            continue
        partes = li.split("`")
        for i in range(0, len(partes), 2):
            partes[i] = partes[i].replace("\\_", "_").replace("_", "\\_")
        out.append("`".join(partes))
    return "\n".join(out)


def espacar_listas(md: str) -> str:
    """Garante linha em branco antes de cada lista (exigência do pandoc)."""
    import re
    linhas = md.split("\n")
    out = []
    item = re.compile(r"^(\* |\d+\. )")
    for i, li in enumerate(linhas):
        if item.match(li) and out and out[-1].strip() and not item.match(out[-1]) and not out[-1].startswith("    "):
            out.append("")
        out.append(li)
    return "\n".join(out)


def fig(nome, legenda, largura="15cm"):
    return f"![{legenda}]({os.path.join(FIGURAS, nome + '.png')}){{width={largura}}}\n"


def T(nome):
    return pd.read_csv(os.path.join(TABELAS, nome + ".csv"))


# ------------------------------------------------------------------ relatório
def texto_relatorio(R: dict, b: dict) -> str:
    q1, q2, q3, q4, q5, q6, q7 = (R[k] for k in ["q01", "q02", "q03", "q04", "q05", "q06", "q07"])
    q8, q9, q10, q11, q12, q13, q14 = (R[k] for k in ["q08", "q09", "q10", "q11", "q12", "q13", "q14"])
    pe = b["perdas"]
    x = pe.perda_rs.to_numpy()
    p_neg_normal = stats.norm.cdf(0, x.mean(), x.std(ddof=1))
    q99_emp = np.quantile(x, 0.99)
    q99_norm = stats.norm.ppf(0.99, x.mean(), x.std(ddof=1))
    q999_emp = np.quantile(x, 0.999)
    q999_norm = stats.norm.ppf(0.999, x.mean(), x.std(ddof=1))
    s = []
    A = s.append
    zs_fora = ", ".join(f(r['z']) for r in q2['a']['tabela'] if abs(r['z']) > 1.96)
    cv_max = max(q4['dispersao'], key=lambda r: r['cv'])
    dmu = [r['mu_ln_controles'] - r['mu_ln'] for r in q14['entradas_tipo']]
    red_sev_min, red_sev_max = 1 - np.exp(max(dmu)), 1 - np.exp(min(dmu))

    A(f"""---
title: "Risco Cibernético por Simulação de Monte Carlo — Estudo de caso ANDI"
subtitle: "Relatório técnico — Questões 1 a 14"
author: "Grupo {q1['grupo']} · Análise Estatística de Dados e Informações (PPCA/UnB)"
date: "Semente do gerador: {q1['semente']} · Entrega: 09/12/2026"
lang: pt-BR
---

**Integrantes:** (preencher)

**Como reproduzir.** `python main.py --grupo {q1['grupo']}` recria as cinco bases (hashes sha256 em `dados/sha256.json`), todas as tabelas (`saidas/tabelas/`), figuras (`saidas/figuras/`), a planilha `saidas/resultados.xlsx` e este relatório. Nível de significância: α = 5% em todos os testes, salvo indicação. Cada análise que sorteia números usa um fluxo próprio derivado da semente, `default_rng([{q1['semente']}, nº da questão])`, para não consumir números do gerador das bases.

# Parte A — O modelo gerador

## Questão 1 — Implementação

**a) Os quatro passos da Seção 12.2 no código.** O arquivo `src/gerador.py` está organizado pelos quatro passos, marcados em comentários:

{tabela([
    ["1. Modelar", "Bloco de parâmetros: equações e constantes das Etapas A1 a A5 (λ trimestral, S_m, C_t, tabela de tipos, logística, severidade)"],
    ["2. Sortear", "`etapa_a1` (unidades), laço mensal com N ~ Poisson (A2) e `etapa_a3_a5` (atributos, materialização e severidade), todos a partir de um único gerador uniforme"],
    ["3. Calcular", "Montagem de `ataques`, `perdas` e das agregações `painel_trimestral` (288 linhas, com zeros) e `serie_mensal` (36 linhas)"],
    ["4. Analisar", "Questão 2 (`src/q02_verificacao.py`): o que foi gerado é comparado com o que foi programado"],
], ["Passo", "Onde está no código"], "ll")}
A ordem dos sorteios é fixa (unidades → contagens do mês → atributos de cada ataque, unidade por unidade). Ela faz parte da reprodutibilidade: com a semente {q1['semente']}, a mesma ordem gera sempre as mesmas bases, verificado pelos hashes.

**b) Do uniforme a cada distribuição (Seção 12.5).** Tudo parte de U ~ Uniforme(0, 1) do gerador PCG64 do numpy:

{tabela([
    ["Uniforme discreta {a..b}", "a + ⌊U·(b − a + 1)⌋", "servicos (10..30), dia do mês"],
    ["Uniforme contínua (a, b)", "a + U·(b − a)", "treino (0..12 h)"],
    ["Bernoulli(p)", "1 se U < p", "soc, fora_expediente, materializou"],
    ["Categórica", "menor k com U < F(k) (probabilidades acumuladas)", "tipo de ataque"],
    ["Triangular(a; c; b)", "inversa implementada pelo grupo (abaixo)", "patch, cvss"],
    ["Exponencial(θ)", "T = −θ·ln(1 − U), implementada pelo grupo", "tempo de detecção"],
    ["Poisson(λ)", "`rng.poisson` (inversão da acumulada / PTRS)", "ataques por unidade-mês"],
    ["Normal(0; σ)", "`rng.normal` (método ziggurat)", "erro ε da severidade"],
], ["Distribuição", "Como é sorteada a partir de U", "Uso"], "lll")}
Para a Triangular, com F_c = (c − a)/(b − a), a inversa é X = a + √(U(b − a)(c − a)) se U < F_c e X = b − √((1 − U)(b − a)(b − c)) caso contrário. As duas inversas (`src/inversa.py`) foram comparadas com as funções do numpy em 100.000 sorteios:

{tabela([[r['distribuicao'], f(r['media_grupo'], 3), f(r['media_numpy'], 3), f(r['q95_grupo'], 2), f(r['q95_numpy'], 2), f(r['ks_estatistica'], 3), f(r['ks_p_valor'], 3)] for r in q1['inversa']],
         ["Distribuição", "Média (grupo)", "Média (numpy)", "P95 (grupo)", "P95 (numpy)", "KS", "p-valor"])}
Em nenhum caso o teste de Kolmogorov-Smirnov rejeita a igualdade das distribuições (p-valores entre {f(min(r['ks_p_valor'] for r in q1['inversa']), 2)} e {f(max(r['ks_p_valor'] for r in q1['inversa']), 2)}): a inversa do grupo e a função pronta geram a mesma distribuição.

**c) Justificativa das distribuições (tabela da Seção 12.4).** Contagem de eventos raros por período → **Poisson**; ocorre/não ocorre (SOC, fora do expediente, materialização) → **Bernoulli**; severidade em R$ (positiva, assimétrica, cauda pesada) → **Lognormal**; tempo até a detecção → **Exponencial**; grandezas com pouca informação, só faixa plausível (patch, CVSS por tipo) → **Triangular**; treino sem valor mais provável → **Uniforme**; erro do log da perda, soma de muitos fatores → **Normal**.

Usar a Normal para a severidade seria um erro grave por três motivos, que os próprios dados mostram. (i) Ajustando uma Normal às perdas observadas (média {rs(x.mean())}, desvio {rs(x.std(ddof=1))}), {pct(p_neg_normal)} das perdas seriam **negativas**, o que não existe. (ii) A Normal é simétrica, e as perdas têm assimetria {f(q4['forma'][0]['assimetria'])}. (iii) A Normal subestima a cauda: seu quantil de 99,9% é {rs(q999_norm)}, contra {rs(q999_emp)} observado. A cauda é justamente o que define o risco, e a Normal a cortaria.

## Questão 2 — Verificação do gerador

**a) Média mensal por unidade.** A média observada de ataques por mês acompanha a média teórica dos λ_u,t (correlação {f(q2['a']['corr_obs_teo'], 2)}; Figura 1). Medindo a diferença em erros padrão (√(λ̄/36)), {q2['a']['fora_ic95']} das 24 unidades ficam fora de ±1,96 (z de {f(q2['a']['z_min'])} a {f(q2['a']['z_max'])}); o esperado por acaso seria cerca de 1,2. As unidades fora da faixa têm z de {zs_fora}; o excesso é pequeno e compatível com a flutuação de 36 meses (a correlação forte mostra que o gerador segue λ).

{fig('q02a_media_por_unidade', 'Figura 1 — Média mensal observada × teórica por unidade (barras: IC 95%).', '11cm')}
**b) Dispersão.** Na unidade {q2['b']['unidade_escolhida']} (sem SOC), a razão variância/média das 36 contagens é {f(q2['b']['indice_unidade'])}; entre as unidades sem SOC ela varia de {f(q2['b']['indice_min_sem_soc'])} a {f(q2['b']['indice_max_sem_soc'])} (média {f(q2['b']['indice_medio_sem_soc'])}). Fica um pouco acima de 1 porque λ muda de mês a mês (sazonalidade, tendência e a campanha de abril/2025): medindo a dispersão em torno do λ de cada mês, o índice médio cai para {f(q2['b']['dispersao_vs_lambda_media'])}, como exige a Poisson. Juntando as 24 unidades, a razão sobe para {f(q2['b']['indice_todas'])} (variância {f(q2['b']['var_todas'])} para média {f(q2['b']['media_todas'])}). A variância total soma a variância dentro das unidades ({f(q2['b']['var_dentro'])}) e a variância entre as médias das unidades ({f(q2['b']['var_entre'])}): é a **heterogeneidade** (unidades com λ diferentes) que gera a superdispersão, não uma falha da Poisson.

**c) Tipos e materialização.**

{tabela([[r['tipo'], r['ataques'], pct(r['freq_observada']), pct(r['prob_programada'], 0), pct(r['erro_simulacao'], 2), f(r['z'])] for r in q2['c']['tipos']],
         ["Tipo", "Ataques", "Observado", "Programado", "σ/√n", "z"])}
O qui-quadrado de aderência dá {f(q2['c']['qui2'])} com 5 g.l. (crítico {f(q2['c']['qui2_critico'])}, p = {pv(q2['c']['qui2_p'])}): as frequências são compatíveis com as programadas a 5%, ainda que por pouco, puxadas por Força bruta (z = {f(q2['c']['tipos'][1]['z'])}). Com seis comparações, um z perto de 3 é raro mas não impossível. A taxa de materialização observada é {pct(q2['c']['taxa_materializacao'], 2)} contra a média dos p_i de {pct(q2['c']['p_medio'], 2)}; o erro de simulação (√Σp_i(1 − p_i)/n) é {pct(q2['c']['erro_padrao_taxa'], 2)}, então a diferença equivale a z = {f(q2['c']['z_taxa'])}. As discrepâncias são do tamanho do erro σ/√n da Seção 12.3: o gerador faz o que foi programado.

# Parte B — Análise das bases

## Questão 3 — Dos dados à decisão

**a) Tipos de variáveis e estrutura.** Em `ataques.csv`: tipo, unidade, fora_expediente e materializou são **qualitativas nominais** (as duas últimas dicotômicas 0/1); mês é qualitativa ordinal (cíclica); trimestre e ano são quantitativas discretas (índices de tempo); cvss e tempo_deteccao_h são **quantitativas contínuas** (o CVSS é registrado com uma casa, mas é contínuo por natureza); id_ataque e data são identificador e carimbo temporal. Em `perdas.csv`, perda_rs é quantitativa contínua. Quanto à estrutura, ataques e perdas são **microdados em painel** (cada evento ligado a uma unidade e a uma data); o painel trimestral é um painel balanceado 24 × 12 e a série mensal é uma série temporal.

* **População:** todos os ataques que a ANDI sofre (o processo gerador, em qualquer período).
* **Amostra:** os {fmt(q3['n_ataques'], 0)} ataques e {fmt(q3['n_perdas'], 0)} perdas observados em 2023–2025.
* **Unidade de observação:** o ataque (em `perdas.csv`, o incidente materializado).
* **Parâmetros:** quantidades da população, como a taxa média de ataques λ, a probabilidade de materialização p e a mediana da perda por tipo; as estatísticas da amostra os estimam.

**b) Distribuições de frequências.**

{tabela([[r['tipo'], r['freq_absoluta'], pct(r['freq_relativa']), r['freq_abs_acumulada'], pct(r['freq_rel_acumulada'])] for r in q3['freq_tipo']],
         ["Tipo", "Freq. absoluta", "Freq. relativa", "Abs. acumulada", "Rel. acumulada"])}
Para a perda, a regra de Sturges dá k = 1 + 3,322·log₁₀({fmt(q3['n_perdas'], 0)}) ≈ {q3['k_sturges']} classes de amplitude {rs(q3['amplitude_classe'])}. A primeira classe concentra {pct(q3['primeira_classe_freq'])} das perdas e as duas primeiras, {pct(q3['duas_primeiras_freq'])}; as nove restantes guardam poucas perdas cada, até {rs(x.max())}. Classes de mesma amplitude escondem a forma de uma variável tão assimétrica, como mostra a Figura 2: em escala logarítmica o histograma fica quase simétrico.

{fig('q03b_histograma_perda', 'Figura 2 — Perda por incidente: 11 classes de Sturges (esquerda) e escala log10 (direita).', '14cm')}
**c) Medidas de posição.**

{tabela([[r['tipo'], r['n'], rs(r['media']), rs(r['mediana']), rs(r['moda_classe_modal']), f(r['media_sobre_mediana'])] for r in q3['centrais']],
         ["Tipo", "n", "Média", "Mediana", "Moda (classe modal)", "Média/mediana"])}
Como a perda é contínua, nenhum valor se repete; a moda é o ponto médio da classe modal (Sturges dentro de cada tipo) e depende da largura escolhida. A média é de {f(min(r['media_sobre_mediana'] for r in q3['centrais']), 1)} a {f(max(r['media_sobre_mediana'] for r in q3['centrais']), 1)} vezes a mediana: poucas perdas muito grandes a puxam para cima. **A mediana representa melhor a "perda típica" de um incidente** (geral {rs(q3['centrais'][-1]['mediana'])}). A média continua necessária para o orçamento: a perda total é o número de incidentes vezes a média, não a mediana.

## Questão 4 — Dispersão, formato e associação

**a) Dispersão por tipo.**

{tabela([[r['tipo'], rs(r['desvio_padrao']), f(r['cv']), rs(r['aiq']), r['n_outliers'], pct(r['soma_outliers_pct'], 0)] for r in q4['dispersao']],
         ["Tipo", "Desvio-padrão", "CV", "AIQ", "Outliers", "% da perda do tipo nos outliers"])}
Em termos relativos o tipo mais arriscado é **{cv_max['tipo']}** (CV = {f(cv_max['cv'])}): sua perda média é moderada, mas o desvio-padrão é {f(cv_max['cv'], 1)} vezes a média. Ransomware tem o maior desvio absoluto e CV de {f(q4['dispersao'][5]['cv'])}: é caro de forma mais consistente.

**b) Outliers.** A regra de 1,5 × AIQ marca de {pct(min(r['pct_outliers'] for r in q4['dispersao']), 0)} a {pct(max(r['pct_outliers'] for r in q4['dispersao']), 0)} das perdas de cada tipo (Figura 3). Elas **não são erros a remover: são a essência do risco**. Esses poucos casos respondem por {pct(min(r['soma_outliers_pct'] for r in q4['dispersao']), 0)} a {pct(max(r['soma_outliers_pct'] for r in q4['dispersao']), 0)} da perda total de cada tipo; retirá-los subestimaria a perda anual e, sobretudo, a cauda que o VaR e o CVaR medem. Em dados Lognormais a regra do box-plot sempre "acusa" valores na cauda direita.

{fig('q04b_boxplots', 'Figura 3 — Box-plots da perda por tipo, em escala linear e logarítmica.', '15cm')}
**c) Formato.** A perda tem assimetria {f(q4['forma'][0]['assimetria'])} e curtose {f(q4['forma'][0]['curtose'])} (a Normal tem 0 e 3). O ln(perda) tem assimetria {f(q4['forma'][1]['assimetria'])} e curtose {f(q4['forma'][1]['curtose'])}: **o logaritmo transforma uma distribuição muito assimétrica e de cauda pesada em outra quase Normal**, o que é a definição da Lognormal e justifica modelar ln(perda) por regressão (Q9–Q10).

**d) Covariâncias e correlações (painel).** As matrizes completas estão em `saidas/tabelas/q04d_*.csv`; as correlações estão na Figura 4. n_ataques cresce com serviços expostos (r = {f(q4['cor'][0]['servicos'])}) e cai com SOC ({f(q4['cor'][0]['soc'])}) e treino ({f(q4['cor'][0]['treino'])}), nos sentidos esperados. A correlação de n_ataques com patch é praticamente nula ({f(q4['cor'][0]['patch'])}), embora patch reduza ataques no gerador: nesta amostra de 24 unidades, patch é positivamente correlacionado com serviços ({f(q4['cor'][2]['patch'])}), e o efeito de serviços mascara o de patch. **Correlação simples não é efeito parcial**: a regressão múltipla da Q11 separa os dois. A perda total trimestral correlaciona com o número de ataques ({f(q4['cor'][0]['perda_total'])}) e, mais fortemente que ele, com SOC ({f(q4['cor'][1]['soc'])}), porque o SOC reduz ataques, materialização e severidade ao mesmo tempo.

{fig('q04d_correlacoes', 'Figura 4 — Matriz de correlações no painel trimestral (288 observações).', '9cm')}
**e) VaR histórico.** O percentil 95 das 36 perdas mensais totais é **{mi(q4['var95_mensal'], 2)}** (média mensal {mi(q4['media_mensal'], 2)}). Com 36 pontos, esse quantil fica na posição {f(q4['posicao_quantil'])} da amostra ordenada, entre o 2º maior mês ({mi(q4['segundo_maior'], 2)}) e o 3º ({mi(q4['terceiro_maior'], 2)}). Ele depende de dois ou três meses: retirando só o maior mês ({q4['mes_maior']}), o VaR cai para {mi(q4['var95_sem_maior'], 2)}. Um quantil de cauda estimado com tão poucas observações é muito instável, e é por isso que a Parte C o estima por simulação.

## Questão 5 — Probabilidade e Bayes

**a) Tipo × materialização.** A tabela de contingência completa e as probabilidades conjuntas estão em `saidas/tabelas/q05a_*.csv`. A probabilidade de materializar varia de {pct(min(q5['p_mat_tipo'].values()))} ({min(q5['p_mat_tipo'], key=q5['p_mat_tipo'].get)}) a {pct(max(q5['p_mat_tipo'].values()))} ({max(q5['p_mat_tipo'], key=q5['p_mat_tipo'].get)}). **P(materializou | ransomware) = {f(q5['p_mat_ransom'], 3)}**, mas **P(ransomware | materializou) = {f(q5['p_ransom_mat'], 3)}**. As duas diferem porque têm denominadores diferentes: a primeira divide pelos {q5['contingencia'][5]['total']} ransomwares, a segunda pelas {fmt(q5['contingencia'][6]['materializou'], 0)} perdas. Ransomware materializa muito (CVSS alto), mas é só {pct(q5['p_ransom'])} dos ataques, então é uma fração pequena das perdas. Confundir as duas é o erro de inverter a condição.

**b) SOC e materialização.** P(SOC) = {f(q5['pA_soc'], 3)}, P(materializou) = {f(q5['pB_mat'], 3)} e P(SOC ∩ materializou) = {f(q5['pAB'], 4)}, bem abaixo de P(SOC)·P(materializou) = {f(q5['pA_x_pB'], 4)}. **Os eventos não são independentes**: com SOC, materializam {pct(q5['p_mat_dado_soc'])} dos ataques; sem SOC, {pct(q5['p_mat_dado_sem_soc'])} (qui-quadrado de independência = {f(q5['qui2_indep'], 1)}, p {pv(q5['qui2_indep_p'])}).

**c) Regra "alarme se cvss ≥ 7".** Sensibilidade P(alarme | materializou) = **{f(q5['sens'], 3)}**; especificidade P(sem alarme | não materializou) = **{f(q5['espec'], 3)}**; prevalência = **{f(q5['prev'], 3)}**. Por Bayes,

P(materializou | alarme) = ({f(q5['sens'], 3)} × {f(q5['prev'], 3)}) / ({f(q5['sens'], 3)} × {f(q5['prev'], 3)} + {f(1 - q5['espec'], 3)} × {f(1 - q5['prev'], 3)}) = **{f(q5['vpp_bayes'], 3)}**,

idêntico à contagem direta ({q5['vp']} materializados entre {q5['n_alarmes']} alarmes = {f(q5['vpp_direto'], 3)}). A regra é específica mas pouco sensível: deixa passar dois terços das perdas, porque muitos ataques de CVSS moderado materializam quando a detecção demora.

**d) Árvore de triagem.** A Figura 5 mostra a árvore da Seção 3.8. Com a prevalência pela metade ({pct(q5['prev'] / 2)}), sensibilidade e especificidade não mudam, mas o valor preditivo do alarme cai de {f(q5['vpp_bayes'], 3)} para **{f(q5['vpp_prev_metade'], 3)}**: a maioria dos alarmes passa a ser falso positivo. Quanto mais raro o evento, menos um alarme significa, mesmo com o mesmo detector.

{fig('q05d_arvore_triagem', 'Figura 5 — Árvore de triagem com a prevalência observada e com a prevalência pela metade.', '15.5cm')}
## Questão 6 — Distribuições

**a) Poisson.** Para a unidade {q6['a']['unidade']} (sem SOC, média mensal mediana entre as sem SOC), λ̂ = {f(q6['a']['lambda_hat'])} ataques/mês. Pela Poisson, P(N ≥ 6) = 1 − P(N ≤ 5) = **{f(q6['a']['p_teorica'], 3)}**; na base, {q6['a']['meses_ge6']} dos 36 meses tiveram 6 ou mais ataques (**{f(q6['a']['p_empirica'], 3)}**). A diferença corresponde a menos de um mês, dentro do esperado para 36 observações (Figura 6).

{fig('q06a_poisson_unidade', 'Figura 6 — Contagem mensal da unidade e distribuição de Poisson ajustada.', '10cm')}
**b) Exponencial.** Para unidades com SOC e ataques no expediente ({q6['b']['n']} ataques), a Exponencial de média 4 h dá P(T > 8) = e^(−8/4) = **{f(q6['b']['p_teorica_theta4'], 3)}**; com a média estimada ({f(q6['b']['theta_hat'])} h), {f(q6['b']['p_teorica_theta_hat'], 3)}. A proporção observada é **{f(q6['b']['p_observada'], 3)}** (z = {f(q6['b']['z'])} contra o valor teórico): o modelo Exponencial se sustenta.

**c) Lognormal.** Nos gráficos Q-Q (Figura 7), ln(perda) segue a reta da Normal para os dois tipos (correlação do Q-Q de {f(q6['c']['Ransomware']['r_qq'], 3)} e {f(q6['c']['Phishing']['r_qq'], 3)}; Shapiro-Wilk p = {f(q6['c']['Ransomware']['shapiro_p'], 2)} e {f(q6['c']['Phishing']['shapiro_p'], 2)}): **a hipótese Lognormal se sustenta**. A maior perda de ransomware ({rs(q6['c']['Ransomware']['maior_perda'])}) tem escore Z de {f(q6['c']['Ransomware']['z_max_ln'])} na escala log; a de phishing ({rs(q6['c']['Phishing']['maior_perda'])}), {f(q6['c']['Phishing']['z_max_ln'])}. São máximos normais para amostras de {q6['c']['Ransomware']['n']} e {q6['c']['Phishing']['n']} valores (o maior de n Normais costuma ficar perto de 2,5 e 2,8 desvios). Na escala original, os mesmos valores teriam Z de {f(q6['c']['Ransomware']['z_max_bruto'])} e {f(q6['c']['Phishing']['z_max_bruto'])}, o que parece "extremo" só porque o escore Z supõe simetria.

{fig('q06c_qq_lognormal', 'Figura 7 — Gráficos Q-Q de ln(perda) contra a Normal: ransomware e phishing.', '13cm')}
""")

    ic = {(r['soc'], r['subconjunto']): r for r in q7['a']}
    A(f"""## Questão 7 — Amostragem e estimação

**a) Tempo médio de detecção.**

{tabela([[("Com SOC" if k[0] == 1 else "Sem SOC") + (" (todos)" if k[1] == 'todos' else " (só expediente)"), r['n'], f(r['media']), f"[{f(r['li'])}; {f(r['ls'])}]", f(r['theta_programado'], 0), "sim" if r['contem_theta'] else "não"] for k, r in ic.items()],
         ["Grupo", "n", "Média (h)", "IC 95% (t)", "θ programado", "Contém θ?"])}
Os intervalos com todos os ataques **não contêm** 4 h nem 12 h. O motivo é fora_expediente: 35% dos ataques têm o tempo multiplicado por 1,5, então a média verdadeira é θ·(0,65 + 0,35·1,5) = 1,175·θ, isto é, 4,7 h com SOC e 14,1 h sem SOC, valores que os ICs contêm. Restringindo aos ataques no expediente, os intervalos voltam a conter 4 h e 12 h. O θ programado é a média de uma subpopulação, não a da população toda.

**b) Proporção de materializados.** p̂ = {f(q7['b']['p'], 4)}, IC 95% = [{f(q7['b']['li'], 4)}; {f(q7['b']['ls'], 4)}]. Para uma margem de ±2 p.p. com 95%, n = 1,96²·p̂(1 − p̂)/0,02² = **{fmt(q7['b']['n_para_2pp'], 0)}** ataques auditados ({fmt(q7['b']['n_pior_caso'], 0)} no pior caso, p = 0,5).

**c) Teorema Central do Limite.**

{tabela([[r['n'], rs(r['dp_medias']), rs(r['sigma_sobre_raiz_n']), f(r['assimetria_medias'])] for r in q7['c']['tabela']],
         ["n", "Desvio das 2.000 médias", "σ/√n", "Assimetria das médias"], "rrrr")}
O desvio das médias acompanha σ/√n nos três tamanhos (Figura 8). Mas a forma converge devagar: com n = 30 as médias ainda têm assimetria {f(q7['c']['tabela'][1]['assimetria_medias'])}, e mesmo com n = 100 ela é {f(q7['c']['tabela'][2]['assimetria_medias'])}. A regra prática "n = 30 basta" vale para variáveis pouco assimétricas; perda_rs tem assimetria {f(q7['c']['assimetria_perda'])} e cauda pesada, então um IC Normal para a perda média com n = 30 ficaria curto do lado direito.

{fig('q07c_tcl', 'Figura 8 — Distribuição de 2.000 médias amostrais de perda_rs para n = 5, 30 e 100.', '15cm')}
""")

    A(f"""## Questão 8 — Testes de hipóteses e backtesting

**a) Contrato do SOC (máximo 4 h).** (1) H₀: μ ≤ 4 h; Hₐ: μ > 4 h. (2) Estatística t de Student (σ desconhecido). (3) α = 5%, unilateral à direita. (4) Rejeitar H₀ se t > t₀,₀₅;{q8['a']['n'] - 1} = {f(q8['a']['t_critico'], 3)}. (5) n = {q8['a']['n']}, x̄ = {f(q8['a']['media'])} h, s = {f(q8['a']['dp'])} h, t = (x̄ − 4)/(s/√n) = **{f(q8['a']['t'])}**, p-valor {pv(q8['a']['p'])}. (6) **Rejeita-se H₀**: o tempo médio de detecção nas unidades com SOC supera o prometido. O resultado não deveria surpreender: o θ = 4 h vale só para ataques no expediente; com o fator 1,5 fora do expediente a média verdadeira é 4,7 h. Testando apenas os ataques no expediente, x̄ = {f(q8['a']['media_expediente'])} h, t = {f(q8['a']['t_expediente'])} e p = {f(q8['a']['p_expediente'], 3)}: o contrato é cumprido no expediente e descumprido fora dele.

**b) Meta de materialização (máximo 40%).** (1) H₀: p ≤ 0,40; Hₐ: p > 0,40. (2) Z para proporção. (3) α = 5%, unilateral. (4) Rejeitar se Z > {f(q8['b']['z_critico'], 3)}. (5) p̂ = {f(q8['b']['p_hat'], 4)}, Z = (p̂ − 0,40)/√(0,40·0,60/{q8['b']['n']}) = **{f(q8['b']['z'])}**, p-valor = {pv(q8['b']['p'])}. (6) **Rejeita-se H₀**: há evidência de que mais de 40% dos ataques se materializam; a meta não está sendo cumprida.

**c) Erros no item (a).** Erro Tipo I: concluir que o SOC descumpre o contrato quando ele cumpre, e aplicar multa ou trocar de fornecedor sem razão. Erro Tipo II: aceitar que o SOC cumpre as 4 h quando ele é mais lento, deixando a ANDI exposta por mais tempo a cada ataque. Para a ANDI o **Tipo II é mais caro**: cada hora a mais encarece a perda em cerca de 2% e aumenta a chance de materialização, numa base de dezenas de milhões por ano; o custo do Tipo I é uma disputa contratual.

**d) Backtesting.** Com 2023–2024 ({q8['d']['T_treino']} unidades-mês, {pct(q8['d']['zeros_treino'], 0)} delas sem perda), o VaR 95% da perda mensal por unidade é **{rs(q8['d']['var95'])}**. Em 2025 ({q8['d']['T']} unidades-mês) ele foi excedido **{q8['d']['N']} vezes**, contra {f(q8['d']['esperado'], 1)} esperadas ({pct(q8['d']['taxa'])} contra 5%). Kupiec: LR = **{f(q8['d']['lr'])}** > 3,84 (p = {f(q8['d']['p'], 4)}): **o modelo é rejeitado**, por subestimar o risco. Nos próprios anos de estimação a taxa de exceções foi {pct(q8['d']['taxa_treino_por_ano']['2023'])} (2023) e {pct(q8['d']['taxa_treino_por_ano']['2024'])} (2024). As causas, à luz do gerador: (i) **tendência**, já que λ cresce 0,15 ataque por trimestre e a perda mensal média por unidade subiu de {rs(q8['d']['media_treino'])} no treino para {rs(q8['d']['media_teste'])} em 2025; (ii) **campanha de abril/2025**, que elevou os ataques em 80% naquele mês. Um VaR histórico estático não acompanha um processo que muda no tempo.

{fig('q08d_backtesting', 'Figura 9 — Perdas mensais por unidade em 2025 e o VaR 95% estimado em 2023–2024.', '13cm')}
## Questão 9 — Correlação e regressão simples

**a) Correlação.** Entre perda_rs e tempo, r = {f(q9['r_perda'], 3)} (t = {f(q9['t_perda'])}); entre ln(perda) e tempo, r = {f(q9['r_ln'], 3)} (t = {f(q9['t_ln'])}). Nos dois casos rejeita-se H₀: ρ = 0 (p {pv(q9['p_ln'])}). A correlação com a perda bruta é dominada por poucos valores extremos (Figura 10); o log torna a relação linear e homogênea.

{fig('q09_dispersao', 'Figura 10 — perda e ln(perda) contra o tempo até a detecção, com a reta de mínimos quadrados.', '15cm')}
**b) Regressão.** ln(perda) = {f(q9['b0'], 3)} + {f(q9['b1'], 5)}·tempo. Como o modelo é log-linear, cada hora a mais de atraso multiplica a perda por e^β₁, ou seja, **+{f(q9['pct_por_hora'])}% por hora** (um dia a mais, cerca de +{f(100 * (np.exp(24 * q9['b1']) - 1), 0)}%).

**c) Ajuste.** R² = {f(q9['r2'], 3)} e erro padrão da regressão s = {f(q9['s'], 3)} (em ln). Um R² baixo **não** invalida a conclusão: o coeficiente é estimado com precisão (t = {f(q9['t_ln'])}) e o efeito existe; o tempo simplesmente explica uma parte pequena da variação. A variável omitida que mais infla o resíduo é o **tipo de ataque**: as medianas vão de R$ 10 mil a R$ 150 mil, e incluí-lo leva o R² a {f(q10['d']['r2_dummies'], 2)} (Q10-d); o restante é o erro ε próprio da Lognormal.

**d) Gauss-Markov.** São plausíveis: linearidade em ln(perda); independência entre perdas (Durbin-Watson = {f(q9['durbin_watson'])}); homocedasticidade (Breusch-Pagan p = {f(q9['breusch_pagan_p'], 2)}). A normalidade dos erros é aproximada (Jarque-Bera p = {f(q9['jarque_bera_p'], 3)}), pois o resíduo mistura tipos com medianas diferentes. O problema maior é o **viés de seleção**: só vemos perdas de ataques que se materializaram, e a materialização depende do tempo e do CVSS. Ataques de tipos baratos (CVSS baixo) quase só materializam quando a detecção demora: o tempo médio do phishing é {f(q9['tempo_medio_por_tipo'][0]['todos_ataques'], 1)} h entre todos os ataques e {f(q9['tempo_medio_por_tipo'][0]['so_materializados'], 1)} h entre os materializados; no ransomware, {f(q9['tempo_medio_por_tipo'][5]['todos_ataques'], 1)} h e {f(q9['tempo_medio_por_tipo'][5]['so_materializados'], 1)} h. Entre as perdas, tempos longos ficam associados a tipos baratos, e isso **atenua** β₁ ({f(q9['b1'], 4)} na regressão simples contra {f(q10['d']['b1'], 4)} controlando o tipo).

## Questão 10 — Inferência na regressão

**a) ANOVA.**

{tabela([[r['fonte'], f(r['SQ'], 2), r['gl'], f(r['QM'], 4) if r['QM'] == r['QM'] else "", f(r['F'], 2) if r['F'] == r['F'] else ""] for r in q10['anova']],
         ["Fonte", "SQ", "g.l.", "QM", "F"])}
F = {f(q10['F'], 3)} e t(β₁) = {f(q10['t_b1'], 4)}, com t² = {f(q10['t2'], 3)} = F: na regressão simples os dois testes são o mesmo (p {pv(0)}).

**b) IC de β₁.** {f(q10['b1'], 5)} ± {f(q10['t_crit'], 3)} × {f(q10['ep_b1'], 5)} = **[{f(q10['ic_b1'][0], 5)}; {f(q10['ic_b1'][1], 5)}]**. Contém o valor programado 0,02, mas perto do limite superior, coerente com a atenuação por seleção discutida na Q9-d.

**c) Ataque detectado em 24 h.** Média de ln(perda): {f(q10['c_ln']['mean'], 3)}, IC 95% [{f(q10['c_ln']['mean_ci_lower'], 3)}; {f(q10['c_ln']['mean_ci_upper'], 3)}], que em reais é **[{rs(q10['c_reais']['mean_ci_lower'])}; {rs(q10['c_reais']['mean_ci_upper'])}]**. Intervalo de previsão para uma perda individual: [{f(q10['c_ln']['obs_ci_lower'], 3)}; {f(q10['c_ln']['obs_ci_upper'], 3)}], que em reais é **[{rs(q10['c_reais']['obs_ci_lower'])}; {rs(q10['c_reais']['obs_ci_upper'])}]**. Ao converter com exp(), o IC refere-se à **mediana** da perda (exp da média de um log); a média em reais seria {rs(q10['c_ln']['media_reais_lognormal'])} (fator e^(s²/2) = {f(q10['c_ln']['fator_smearing'])}). O intervalo de previsão é muito mais largo porque soma à incerteza sobre a reta a variância individual da perda (s² = {f(q10['anova'][1]['QM'], 3)} em ln), que não diminui com n; na escala original isso vira um fator de cerca de {fmt(q10['c_reais']['obs_ci_upper'] / q10['c_reais']['obs_ci_lower'], 0)} entre os limites.

**d) Com dummies de tipo.** O R² vai de {f(q10['d']['r2_simples'], 3)} para **{f(q10['d']['r2_dummies'], 3)}**, o erro padrão cai para {f(q10['d']['s'], 3)} (próximo do σ = 0,9 programado), e β₁ = {f(q10['d']['b1'], 5)} com IC **[{f(q10['d']['ic_b1'][0], 5)}; {f(q10['d']['ic_b1'][1], 5)}]**, mais estreito (amplitude {f(q10['d']['largura_ic_dummies'], 4)} contra {f(q10['d']['largura_ic_simples'], 4)}) e centrado perto de 0,02. As dummies recuperam as razões entre medianas programadas:

{tabela([[r['tipo'], f(r['razao_medianas_estimada'], 2), f(r['razao_programada'], 2)] for r in q10['d']['tipos']], ["Tipo (base: Phishing)", "Razão de medianas estimada", "Programada"])}""")

    co = {r['termo']: r for r in q11['a']}
    A(f"""
## Questão 11 — Regressão múltipla

**a) Modelo.** n_ataques = β₀ + β₁·servicos + β₂·patch + β₃·treino + β₄·soc + β₅·trimestre + erro, no painel de 288 unidades-trimestre:

{tabela([[k, f(r['coeficiente'], 4), f(r['erro_padrao'], 4), f(r['t'], 2), pv(r['p_valor']), f"[{f(r['ic95_inf'], 3)}; {f(r['ic95_sup'], 3)}]"] for k, r in co.items()],
         ["Termo", "Coeficiente", "Erro padrão", "t", "p-valor", "IC 95%"])}
**b) Testes e interpretação.** F global = {f(q11['b']['F'], 2)} com ({q11['b']['gl1']}; {q11['b']['gl2']}) g.l., p {pv(q11['b']['F_p'])}: o modelo explica parte relevante dos ataques. Todos os t individuais são significativos a 5%. R² = {f(q11['b']['r2'], 3)} e R² ajustado = {f(q11['b']['r2aj'], 3)}. Para a gestão, mantendo o restante constante e por trimestre:
* cada serviço exposto a mais traz **+{f(co['servicos']['coeficiente'], 2)} ataque**: fechar 10 serviços evitaria cerca de {f(10 * co['servicos']['coeficiente'], 1)} ataques por trimestre na unidade;
* cada ponto percentual de cobertura de patches retira **{f(-co['patch']['coeficiente'], 2)} ataque**;
* cada hora de treinamento retira **{f(-co['treino']['coeficiente'], 2)} ataque**;
* um SOC dedicado retira **{f(-co['soc']['coeficiente'], 2)} ataques**;
* a tendência acrescenta **{f(co['trimestre']['coeficiente'], 2)} ataque** por trimestre que passa.

**c) Comparação com os verdadeiros.**

{tabela([[r['termo'], f(r['coeficiente'], 3), f(r['verdadeiro'], 2), f"[{f(r['ic95_inf'], 3)}; {f(r['ic95_sup'], 3)}]", "sim" if r['contem'] else "não"] for r in q11['c']],
         ["Termo", "Estimado", "Verdadeiro", "IC 95%", "Contém?"])}
**{q11['n_contem']} dos 5 ICs contêm o valor verdadeiro.** "95% de confiança" descreve o procedimento: em muitas amostras, 95% dos intervalos cobririam o parâmetro. Mesmo com cinco ICs independentes, a chance de todos acertarem seria 0,95⁵ = {f(q11['p_todos_5'], 2)}, e errar dois tem probabilidade de cerca de 2%. Aqui há causas além do acaso. O coeficiente do trimestre absorve a campanha de abril/2025 e a sazonalidade, que não estão no modelo; com elas (item d), ele cai para {f([r for r in q11['d']['coef'] if r['termo'] == 'trimestre'][0]['coeficiente'], 3)} e o IC passa a conter 0,15. Além disso, os erros são heterocedásticos (item e), o que torna os erros padrão de MQO pouco confiáveis.

**d) Sazonalidade e campanha.**

{tabela([[r['termo'], f(r['coeficiente'], 3), f(r['erro_padrao'], 3), pv(r['p_valor'])] for r in q11['d']['coef'] if r['termo'] in ('trimestre', 'Q2', 'Q3', 'Q4', 'campanha')],
         ["Termo", "Coeficiente", "Erro padrão", "p-valor"])}
O ajuste melhora: R² ajustado de {f(q11['b']['r2aj'], 3)} para {f(q11['d']['r2aj'], 3)}, e o F parcial das quatro variáveis novas é {f(q11['d']['F_parcial'], 2)} (p = {f(q11['d']['F_parcial_p'], 4)}). O indicador de campanha é o termo mais forte: **+{f([r for r in q11['d']['coef'] if r['termo'] == 'campanha'][0]['coeficiente'], 2)} ataques** por unidade no trimestre abr–jun/2025. Entre as dummies sazonais, só Q4 se aproxima da significância (+{f([r for r in q11['d']['coef'] if r['termo'] == 'Q4'][0]['coeficiente'], 2)}). Isso é coerente com a média dos S_m no 4º trimestre (1,08, contra 0,95 no 1º); com 24 unidades e 3 anos a sazonalidade trimestral é fraca demais para se destacar do ruído.

**e) Diagnóstico.** VIFs entre {f(min(q11['e']['vif'].values()), 2)} e {f(max(q11['e']['vif'].values()), 2)}: não há multicolinearidade. Os resíduos formam um **funil** (Figura 11; Breusch-Pagan p = {f(q11['e']['bp_p'], 3)}): a variância dos resíduos sobe de {f(q11['e']['var_por_faixa']['1º quartil'], 1)} no quartil de menor valor ajustado para {f(q11['e']['var_por_faixa']['4º'], 1)} no maior, acompanhando os ajustados médios ({f(q11['e']['ajustado_por_faixa']['1º quartil'], 1)} e {f(q11['e']['ajustado_por_faixa']['4º'], 1)}). Isso é exatamente o que se espera de uma contagem Poisson, cuja variância é igual à média: unidades com mais ataques esperados oscilam mais. O Q-Q mostra resíduos aproximadamente Normais.

{fig('q11e_residuos', 'Figura 11 — Resíduos × ajustados (com o envelope ±2√ajustado da Poisson) e Q-Q dos resíduos.', '14cm')}
**f) Sobreajuste.**

{tabela([["Sem ruído", f(q11['f']['sem_ruido']['r2_treino'], 3), f(q11['f']['sem_ruido']['r2aj_treino'], 3), f(q11['f']['sem_ruido']['rmse_teste'], 3)],
          ["Com 5 ruídos", f(q11['f']['com_ruido']['r2_treino'], 3), f(q11['f']['com_ruido']['r2aj_treino'], 3), f(q11['f']['com_ruido']['rmse_teste'], 3)]],
         ["Modelo (treino 2023–2024)", "R² treino", "R² ajustado treino", "RMSE teste 2025"])}
As cinco variáveis de puro ruído **aumentam o R² de treino** (como sempre acontece) mas **reduzem o R² ajustado e pioram o erro de previsão** em 2025: o modelo passou a ajustar ruído. O R² de treino não serve para escolher modelos; o R² ajustado e o erro fora da amostra servem.

## Questão 12 — Séries temporais

**a) Tendência e sazonalidade.** Os ataques anuais foram {fmt(q12['anual'][0], 0)} (2023), {fmt(q12['anual'][1], 0)} (2024) e {fmt(q12['anual'][2], 0)} (2025). A média móvel de 12 meses sobe de {f(q12['mm12_inicio'], 1)} para {f(q12['mm12_fim'], 1)} ataques/mês: há **tendência de alta** (Figura 12). A média móvel de 3 meses e a suavização exponencial (α = {f(q12['alpha_ses'], 2)}, estimado) mostram picos em março–abril e novembro e vales em fevereiro e junho, ou seja, **sazonalidade** sobreposta ao ruído. O ponto que mais chama atenção é **abril/2025, com {fmt(q12['maximo'], 0)} ataques**, quase o dobro da média.

{fig('q12a_serie', 'Figura 12 — Série mensal de ataques com médias móveis de 3 e 12 meses e suavização exponencial.', '15cm')}
**b) Decomposição.** Usamos a decomposição **multiplicativa**, porque o gerador multiplica λ pelo fator S_m: o efeito sazonal é proporcional ao nível e cresce com a tendência. Os índices foram calculados pela razão à média móvel centrada 2×12 e normalizados para média 1:

{tabela([[r['mes'], f(r['S_programado'], 2), f(r['indice_estimado'], 3), f(r['indice_sem_abril_2025'], 3)] for r in q12['indices']],
         ["Mês", "S_m programado", "Estimado", "Estimado sem abril/2025"])}
O índice de abril sai **{f(q12['indices'][3]['indice_estimado'], 2)}** contra 1,10 programado: com só dois abris na janela da média móvel, a campanha de abril/2025 contamina o índice sazonal. Excluindo esse mês, o índice de abril cai para {f(q12['indices'][3]['indice_sem_abril_2025'], 2)} e o erro absoluto médio dos 12 índices cai de {f(q12['mae_indices'], 3)} para {f(q12['mae_indices_sem'], 3)} (correlação com os S_m de {f(q12['corr_indices'], 2)} para {f(q12['corr_indices_sem'], 2)}). Com só três anos, cada índice se baseia em dois valores e erra cerca de ±0,05.

**c) ACF.** As autocorrelações ficam todas dentro da faixa ±1,96/√36 = ±{f(q12['banda_acf'], 3)}: a maior é {f(max(q12['acf'][1:]), 2)}. A defasagem 1 ({f(q12['acf'][1], 2)}) reflete a tendência, e a defasagem 12 ({f(q12['acf'][12], 2)}) a sazonalidade anual. Com 36 meses a ACF tem pouco poder: a sazonalidade do gerador é real (S_m varia de 0,85 a 1,15), mas o ruído Poisson de cerca de ±9 ataques/mês é do mesmo tamanho que ela.

{fig('q12b_indices', 'Figura 13 — Índices sazonais estimados (com e sem abril/2025) × programados.', '11cm')}
**d) Previsão e anomalias.** O modelo dessazonaliza a série com os índices sem abril/2025, ajusta uma tendência linear (+{f(q12['d']['indices_sem_abril_2025']['b1'], 2)} ataque/mês) e ressazonaliza. A previsão para 2026 soma **{fmt(q12['total_2026'], 0)} ataques**, de {fmt(min(r['previsao'] for r in q12['previsao']), 0)} (fevereiro) a {fmt(max(r['previsao'] for r in q12['previsao']), 0)} (novembro), com banda de 95% de ±{fmt(1.96 * q12['sigma_prev'], 0)} ataques/mês (Figura 14). A regra dos 3σ sobre os resíduos **encontra abril/2025**, com resíduo de {f(q12['d']['indices_sem_abril_2025']['z_abril_2025_sigma_sem_ele'], 1)}σ (calculando σ sem o próprio mês) e de {f(q12['d']['indices_todos']['z_abril_2025'], 1)}σ mesmo usando os índices contaminados. **Nenhum falso alarme**: o maior |resíduo| dos demais meses é {f(q12['d']['indices_sem_abril_2025']['z_max_outros'], 1)}σ. Há uma ressalva: uma anomalia infla o próprio σ e o índice sazonal que a deveria revelar, então a detecção é mais robusta com estimativas que excluem o ponto testado.

{fig('q12d_previsao', 'Figura 14 — Ajuste, previsão de 2026 com banda de 95% e alarme pela regra dos 3σ.', '15cm')}
""")

    lg = {r['termo']: r for r in q13['a']}
    nomes = {"Intercept": "Intercepto", "cvss": "cvss", "tempo_deteccao_h": "tempo (h)", "soc": "soc",
             "treino": "treino (h)", "fora_expediente": "fora_expediente"}
    d13 = q13['d']
    A(f"""## Questão 13 — Classificação

Treino: {fmt(q13['n_treino'], 0)} ataques de 2023–2024; teste: {fmt(q13['n_teste'], 0)} ataques de 2025.

**a) Regressão logística.**

{tabela([[nomes[k], f(r['coeficiente'], 4), f(r['erro_padrao'], 4), f(r['razao_chances'], 3), f(r['programado'], 2), "sim" if r['contem_programado'] else "não"] for k, r in lg.items()],
         ["Termo", "Coeficiente", "Erro padrão", "Razão de chances e^β", "Programado", "IC 95% contém?"])}
Todos os coeficientes são significativos (p ≤ {pv(max(r['p_valor'] for r in q13['a']))}) e **todos os ICs de 95% contêm o valor programado** na Etapa A4. Em razões de chances: cada ponto de CVSS multiplica as chances de materializar por {f(lg['cvss']['razao_chances'], 2)}; cada hora até a detecção, por {f(lg['tempo_deteccao_h']['razao_chances'], 3)} (+{f(100 * (lg['tempo_deteccao_h']['razao_chances'] - 1), 1)}% por hora); o SOC as multiplica por {f(lg['soc']['razao_chances'], 2)} (menos da metade); cada hora de treino, por {f(lg['treino']['razao_chances'], 3)}; e o ataque fora do expediente, por {f(lg['fora_expediente']['razao_chances'], 2)}.

**b) Dummies de tipo.** **Não deveriam ser significativas**: no gerador, o tipo só afeta a materialização através do CVSS, que já está no modelo. Os dados confirmam: o teste de razão de verossimilhança para as cinco dummies dá LR = {f(q13['b']['lr'], 2)} com {q13['b']['gl']} g.l. (p = {f(q13['b']['p'], 3)}), e nenhuma dummy é significativa isoladamente. Se o CVSS for retirado, as dummies passam a ser significativas (Exploração, Ransomware e Força bruta com p < 0,001): elas absorvem o efeito do CVSS, que difere por tipo. É o mesmo raciocínio de variável omitida da Q9.

**c) Árvore de decisão (profundidade 3).** As regras extraídas (íntegra em `saidas/tabelas/q13c_regras_arvore.txt`):
* **se tempo ≤ 15,1 h e cvss ≤ 6,25** → não materializa (P de 16% a 30%, conforme o CVSS);
* **se tempo ≤ 15,1 h e 6,25 < cvss ≤ 8,15** → não materializa, por margem mínima (49%);
* **se tempo ≤ 15,1 h e cvss > 8,15** → materializa (71%);
* **se tempo > 15,1 h e treino ≤ 10,4 h** → materializa (64% com cvss ≤ 4,95; 84% com cvss maior);
* **se tempo > 15,1 h, treino > 10,4 h e cvss ≤ 5,15** → não materializa (32%); com cvss > 5,15, materializa (64%).

A árvore usa CVSS (importância {f(q13['c']['importancias']['cvss'], 2)}), tempo ({f(q13['c']['importancias']['tempo_deteccao_h'], 2)}) e treino ({f(q13['c']['importancias']['treino'], 2)}); SOC e fora do expediente não entram, pois seu efeito já passa pelo tempo de detecção.

**d) Desempenho no teste (2025, limiar 0,5).**

{tabela([[m_, d13[k]['VN'], d13[k]['FP'], d13[k]['FN'], d13[k]['VP'], f(d13[k]['acuracia'], 3), f(d13[k]['precisao'], 3), f(d13[k]['recall'], 3), f(d13[k]['f1'], 3), f(d13[k]['auc'], 3)] for m_, k in [("Logística", "logistica"), ("Árvore", "arvore")]],
         ["Modelo", "VN", "FP", "FN", "VP", "Acurácia", "Precisão", "Recall", "F1", "AUC"])}
A logística é melhor em quase tudo, e sobretudo na AUC ({f(d13['logistica']['auc'], 3)} contra {f(d13['arvore']['auc'], 3)}; Figura 15). Com profundidade 3 a árvore só produz 8 probabilidades diferentes, e o modelo verdadeiro é ele próprio uma logística. Com limiar 0,5 as duas deixam escapar metade ou mais das perdas (recall {f(d13['logistica']['recall'], 2)} e {f(d13['arvore']['recall'], 2)}).

{fig('q13d_roc', 'Figura 15 — Curvas ROC no conjunto de teste (2025).', '8.5cm')}
**e) Limiar de custo mínimo.** Um falso negativo custa a perda mediana observada em 2023–2024 ({rs(q13['e']['c_fn'])}) e um falso positivo, R$ 3.000. O limiar que minimiza o custo no treino é **{f(q13['e']['limiar_otimo_treino'], 2)}**, próximo do valor teórico C_FP/(C_FP + C_FN) = {f(q13['e']['limiar_teorico'], 3)}. Aplicado em 2025, ele derruba o custo dos erros de {mi(q13['e']['custo_teste_05'], 2)} (limiar 0,5) para **{mi(q13['e']['custo_teste_otimo'], 2)}** (Figura 16): o recall sobe para {f(q13['e']['metricas_otimo']['recall'], 2)} e a precisão cai para {f(q13['e']['metricas_otimo']['precisao'], 2)}, com {q13['e']['metricas_otimo']['FP']} falsos positivos e só {q13['e']['metricas_otimo']['FN']} falsos negativos. É a tensão α × β do cap. 7: baixar o limiar aceita mais erros do Tipo I (alarmes falsos, baratos) para reduzir os do Tipo II (perdas não tratadas, caras). Quando os custos são assimétricos, 0,5 não é neutro: favorece o erro mais caro.

{fig('q13e_limiar_custo', 'Figura 16 — Custo total dos erros no teste em função do limiar.', '10cm')}
""")

    b0, b1c = q14['b'], q14['b_controles']
    e = q14['e']
    tu = {r['tipo']: r for r in q14['entradas_tipo']}
    g = q14['g']
    A(f"""# Parte C — SMC de risco e decisão

## Questão 14 — Perda anual de 2026 e o pacote de controles

**a) Modelar.** A perda agregada anual é L = Σ_u Σ_(i=1..N_u) X_i, com N_u o número de perdas da unidade u. Os três componentes vêm só da Parte B:
* **Frequência:** para cada unidade, a regressão da Q11 prevê os ataques dos trimestres 13 a 16 com o perfil atual; somando, λ_u = ataques esperados em 2026. Total: {fmt(q14['ataques_ano_atual'], 0)} ataques.
* **Materialização:** p̄_u é a média das probabilidades que a logística da Q13 atribui aos ataques observados da unidade (média geral ponderada {f(q14['p_medio_atual'], 3)}). As mesmas probabilidades dão o peso w_(u,k) de cada tipo entre as perdas da unidade.
* **Severidade:** Lognormal por tipo, com (μ_k, σ_k) = média e desvio de ln(perda) em `perdas.csv`.

**Thinning.** Se os ataques de u chegam como Poisson(λ_u) e cada um vira perda com probabilidade p̄_u, independentemente, as perdas são Poisson(λ_u·p̄_u). Separando por tipo, N_(u,k) ~ Poisson(λ_u·p̄_u·w_(u,k)) independentes, e a soma sobre unidades é Poisson(Λ_k). Resultam {fmt(q14['perdas_ano_atual'], 0)} perdas esperadas por ano.

{tabela([[k, f(r['mu_ln'], 3), f(r['sigma_ln'], 3), rs(r['mediana_rs']), rs(r['media_rs']), f(r['Lambda_atual'], 1)] for k, r in tu.items()],
         ["Tipo", "μ (ln)", "σ (ln)", "Mediana", "Média", "Λ_k (perdas/ano)"])}
**b) Distribuição da perda anual (100.000 réplicas).**

{tabela([["Perda média anual", mi(b0['media'], 2), "Expectativa de perda no ano"],
          ["Mediana", mi(b0['mediana'], 2), "Valor central"],
          ["Desvio-padrão", mi(b0['desvio'], 2), "Variabilidade de um ano para outro"],
          ["VaR 95%", mi(b0['var95'], 2), "Perda só superada em 5% dos anos"],
          ["VaR 99%", mi(b0['var99'], 2), "Perda só superada em 1% dos anos"],
          ["CVaR 95%", mi(b0['cvar95'], 2), "Perda média nos 5% piores anos"],
          ["P(perda > R$ 30 mi)", pct(b0['p_acima_30mi']), "Probabilidade de perda relevante"]],
         ["Métrica de risco", "Cenário atual", "Interpretação"], "lrl")}
{fig('q14b_distribuicao_atual', 'Figura 17 — Distribuição simulada da perda anual de 2026 com média, VaR e CVaR (como na Figura 12.6).', '14cm')}
A distribuição é quase simétrica: com cerca de {fmt(q14['perdas_ano_atual'], 0)} perdas por ano, a soma de muitas Lognormais já se aproxima da Normal (TCL). Mesmo assim, a cauda direita é mais longa que a esquerda.

**c) Convergência.**

{tabela([[fmt(r['n'], 0), mi(r['media'], 3), rs(r['ep_media']), mi(r['var95'], 2), (f(r['razao_ep'], 2) if r['razao_ep'] == r['razao_ep'] else "—")] for r in q14['c']],
         ["n", "Perda média", "Erro padrão da média", "VaR 95%", "EP anterior / EP atual"], "rrrrr")}
Cada vez que n quadruplica, o erro padrão cai à metade (razões {f(q14['c'][1]['razao_ep'], 2)}, {f(q14['c'][2]['razao_ep'], 2)}, {f(q14['c'][3]['razao_ep'], 2)}; de 64.000 para 100.000 a razão esperada é √(100/64) = 1,25 e a observada é {f(q14['c'][4]['razao_ep'], 2)}). **O erro cai na proporção 1/√n**, como na Seção 12.3. Com 100.000 réplicas a média tem erro de {rs(q14['c'][4]['ep_media'])}, desprezível frente às incertezas dos modelos.

{fig('q14c_convergencia', 'Figura 18 — Convergência da perda média e do seu erro padrão.', '12cm')}
**d) Cenário com controles (patch 95%, treino 12 h e SOC em todas as unidades).** Os modelos foram realimentados assim:
* **Frequência:** a Q11 prevê {fmt(q14['ataques_ano_ctrl'], 0)} ataques/ano (contra {fmt(q14['ataques_ano_atual'], 0)}).
* **Materialização e tempo de detecção:** o SOC reduz o tempo, e incorporamos isso reescalando os tempos observados das unidades sem SOC pela razão das médias estimadas (Q7): {f(q14['th_soc'])} h / {f(q14['th_sem'])} h = {f(q14['fator_tempo'], 3)}. A Exponencial é uma família de escala, então multiplicar os tempos por esse fator transforma a distribuição sem SOC na distribuição com SOC. Com esses tempos, soc = 1 e treino = 12, a logística da Q13 dá p̄ = {f(q14['p_medio_ctrl'], 3)} (contra {f(q14['p_medio_atual'], 3)}).
* **Severidade:** o tempo médio dos ataques que viram perda cai de {f(q14['tempo_medio_perdas_atual'], 1)} h para {f(q14['tempo_medio_perdas_ctrl'], 1)} h. Cada μ_k foi deslocado por β_tempo × Δtempo do tipo, com β_tempo = {f(q14['beta_tempo'], 4)} da Q10-d, o que reduz a mediana da severidade de cada tipo entre {pct(red_sev_min, 0)} e {pct(red_sev_max, 0)}.

Resultado: {fmt(q14['perdas_ano_ctrl'], 0)} perdas esperadas por ano, contra {fmt(q14['perdas_ano_atual'], 0)}.

{tabela([[r['metrica'], (mi(r['atual'], 2) if 'P(' not in r['metrica'] else pct(r['atual'])), (mi(r['com_controles'], 2) if 'P(' not in r['metrica'] else pct(r['com_controles'])), (mi(r['reducao'], 2) + f" ({pct(r['reducao_pct'], 0)})" if 'P(' not in r['metrica'] else f"−{fmt(100 * r['reducao'], 1)} p.p.")] for r in q14['d']],
         ["Métrica", "Atual", "Com controles", "Redução"])}
{fig('q14d_comparacao', 'Figura 19 — Distribuições da perda anual nos dois cenários (como na Figura 12.7).', '14cm')}
**e) Decisão.** Redução média de {mi(e['reducao_media'], 2)} por ano, a um custo de R$ 8 mi: **ROI = ({fmt(e['reducao_media'] / 1e6, 2)} − 8)/8 = {pct(e['roi'], 0)}**. Com números aleatórios comuns (mesmas uniformes e normais nos dois cenários, réplica a réplica), a probabilidade de a perda com controles somada ao custo superar a perda sem controles é **{pct(e['p_pior_com_pacote'], 2)}**: em nenhuma das 100.000 réplicas o pacote deixou a ANDI pior. Mesmo nos 5% de anos menos favoráveis o benefício líquido é de {mi(e['beneficio_p5'], 1)}. O **custo máximo** que ainda se pagaria na média é a própria redução esperada, **{mi(e['custo_maximo'], 1)} por ano**. O pacote também corta a cauda: VaR 95% −{mi(e['reducao_var95'], 1)} e CVaR 95% −{mi(e['reducao_cvar95'], 1)}.

**f) Sensibilidade.**

{tabela([[r['cenario'], mi(r['media_atual'], 1), mi(r['media_controles'], 1), mi(r['beneficio_liquido'], 1), pct(r['roi'], 0), r['decisao']] for r in q14['f']],
         ["Cenário", "Perda média atual", "Com controles", "Benefício líquido", "ROI", "Decisão"])}
{fig('q14f_tornado', 'Figura 20 — Gráfico de tornado do benefício líquido do pacote.', '11cm')}
**A decisão não muda em nenhum caso.** O σ da Lognormal é o parâmetro mais influente (benefício entre {mi(min(r['beneficio_liquido'] for r in q14['f'][1:3]), 1)} e {mi(max(r['beneficio_liquido'] for r in q14['f'][1:3]), 1)}), porque a média da Lognormal cresce com e^(σ²/2); a frequência ±10% move o benefício de forma proporcional. Para o pacote deixar de compensar, a redução esperada teria de cair abaixo de R$ 8 mi, cerca de um terço do valor estimado.

**g) Erro de modelo.** Rodando o gerador verdadeiro (Etapas A2–A5 com os parâmetros programados, t = 37 a 48, sem campanha, mesmas 24 unidades) por 10.000 anos:

{tabela([[{"media": "Média", "mediana": "Mediana", "desvio": "Desvio-padrão", "var95": "VaR 95%", "var99": "VaR 99%", "cvar95": "CVaR 95%", "p_acima_30mi": "P(> R$ 30 mi)"}[r['metrica']],
           (mi(r['modelo_estimado'], 2) if r['metrica'] != 'p_acima_30mi' else pct(r['modelo_estimado'])),
           (mi(r['gerador_verdadeiro'], 2) if r['metrica'] != 'p_acima_30mi' else pct(r['gerador_verdadeiro'])),
           pct(r['razao_estimado_verdadeiro'] - 1)] for r in g['tabela']],
         ["Métrica", "SMC com modelos estimados", "Gerador verdadeiro", "Diferença"])}
{fig('q14g_erro_modelo', 'Figura 21 — Perda anual de 2026: modelo estimado × gerador verdadeiro.', '13cm')}
A SMC estimada acerta bem o centro (média {pct(g['tabela'][0]['razao_estimado_verdadeiro'] - 1)}), mas **subestima a dispersão e a cauda extrema**: desvio-padrão {pct(g['tabela'][2]['razao_estimado_verdadeiro'] - 1)}, VaR 99% {pct(g['tabela'][4]['razao_estimado_verdadeiro'] - 1)} e CVaR 95% {pct(g['tabela'][5]['razao_estimado_verdadeiro'] - 1)}. Os acertos no centro vêm de erros que se compensam:
* a frequência é superestimada: {fmt(q14['ataques_ano_atual'], 0)} ataques contra {fmt(g['contagens']['ataques_ano'], 0)} verdadeiros (+{pct(q14['ataques_ano_atual'] / g['contagens']['ataques_ano'] - 1, 0)}), porque a tendência da Q11 absorveu a campanha;
* a materialização é subestimada: {f(q14['p_medio_atual'], 3)} contra {f(g['contagens']['p_medio'], 3)};
* a severidade média também é subestimada: {rs(q14['sev_media_est'])} contra {rs(g['contagens']['sev_media'])}.

A cauda fica curta por três razões:
1. A Lognormal com σ único por tipo ignora que o tempo de detecção (Exponencial, assimétrica) entra no log da perda; o ln(perda) é levemente assimétrico à direita (Q4-c), e a cauda real é mais pesada.
2. A simulação trata os parâmetros estimados como certos e não propaga a sua incerteza.
3. A severidade e a materialização são tratadas como independentes, quando ambas crescem com o tempo de detecção, o que produz anos ruins mais concentrados.

Para provisionamento, o VaR e o CVaR estimados devem ser lidos como **limites inferiores** e acompanhados de margem.
""")
    return "\n".join(s)


def texto_parecer(R: dict) -> str:
    q14 = R["q14"]
    b0, b1, e = q14["b"], q14["b_controles"], q14["e"]
    sens = q14["f"]
    g = q14["g"]["tabela"]
    n_sem_soc = int((carregar()["unidades"].soc == 0).sum())
    return f"""---
title: "Parecer executivo à diretoria da ANDI"
subtitle: "Risco cibernético em 2026 e o pacote de controles"
author: "Grupo {R['q01']['grupo']} · AEDI/PPCA-UnB"
lang: pt-BR
---

**1. Quanto a ANDI deve esperar perder em 2026?** Cerca de **{mi(b0['media'])}** em perdas com incidentes cibernéticos. Em 1 ano a cada 20, a perda passa de **{mi(b0['var95'])}** (VaR 95%); nesses 5% piores anos, a perda média é de **{mi(b0['cvar95'])}** (CVaR 95%). Em 1 ano a cada 100 ela ultrapassa {mi(b0['var99'])}. A chance de perder mais de R$ 30 milhões é de {pct(b0['p_acima_30mi'], 0)}. Esses números vêm de 100.000 anos simulados a partir dos dados de 2023–2025 das 24 unidades.

**2. O pacote de controles de R$ 8 milhões por ano compensa?** **Sim, com folga.** O pacote leva a cobertura de patches a 95%, o treinamento a 12 h e cria um SOC em todas as unidades. Com isso, a perda esperada cai para **{mi(b1['media'])}**: uma redução de **{mi(e['reducao_media'])} por ano**, ou **retorno de {pct(e['roi'], 0)}** sobre o custo. A cauda também encolhe: o ano ruim (VaR 95%) passa de {mi(b0['var95'])} para {mi(b1['var95'])}. Em nenhum dos anos simulados o pacote somado ao seu custo saiu mais caro do que não fazer nada. O pacote continuaria valendo a pena até um custo de cerca de **{mi(e['custo_maximo'], 0)} por ano**. O maior ganho vem do SOC: ele reduz o número de ataques, a chance de cada ataque virar perda e o tempo até a detecção, que encarece cada perda em cerca de 2% por hora.

**3. Quão confiáveis são esses números?** A recomendação é robusta: mesmo variando a gravidade das perdas em ±20% e a frequência de ataques em ±10%, o benefício líquido fica entre {mi(min(r['beneficio_liquido'] for r in sens))} e {mi(max(r['beneficio_liquido'] for r in sens))} por ano. Os valores exatos, porém, têm limites que a diretoria deve conhecer:

* **A cauda está subestimada.** Comparado com o processo real que gerou os dados, o modelo acerta a perda média (diferença de {pct(g[0]['razao_estimado_verdadeiro'] - 1, 0)}), mas subestima a variação de um ano para outro em cerca de {pct(1 - g[2]['razao_estimado_verdadeiro'], 0)} e a perda dos anos extremos (VaR 99% e CVaR) em cerca de {pct(1 - g[5]['razao_estimado_verdadeiro'], 0)} a {pct(1 - g[4]['razao_estimado_verdadeiro'], 0)}. VaR e CVaR devem ser tratados como pisos, com margem de segurança.
* **O passado pode não se repetir.** A tendência de alta vem de apenas três anos e foi inflada pela campanha de ataques de abril de 2025. Novas campanhas, novos tipos de ataque ou mudanças de comportamento dos atacantes alteram o quadro.
* **O efeito dos controles foi estimado, não observado.** Nenhuma unidade tem hoje os três controles no nível proposto; o efeito é extrapolado dos modelos. O efeito do SOC no tempo de detecção supõe que o novo SOC funcione como os atuais.
* **Eventos catastróficos raros** (um "cisne negro" acima de tudo o que já foi visto) não estão nos dados e não podem ser previstos por eles.

**Recomendação:** aprovar o pacote, priorizando a implantação do SOC nas {n_sem_soc} unidades que não o têm. O modelo deve ser revisto a cada trimestre com os novos dados, e a perda real de 2026 comparada com a faixa prevista (backtesting).
"""


FERRAMENTA = ("Claude (Anthropic), modelo configurado claude-opus-5-5, pelo app claude.ai "
              "(sessão de trabalho com execução de código, conectores do Google Drive e de documentos)")
RESPONSAVEL = "Diego Casagrande"
A_PREENCHER = "(a preencher pelo grupo)"


def interacoes(grupo: int) -> list[dict]:
    """Uma entrada por interação relevante, com os nove campos exigidos pelo enunciado."""
    def it(data, questao, exig, prompt, resp, verif, erros=""):
        return {"Ferramenta": FERRAMENTA, "Data e responsável": f"{data} · {RESPONSAVEL}",
                "Questão atendida": questao, "Exigência feita à IA": exig, "Prompt": prompt,
                "Resposta obtida": resp, "Verificação": verif, "Decisão do grupo": A_PREENCHER,
                "Erros da IA": erros or "Nenhum identificado até aqui."}
    lista = [
        it("12/11/2026", "Q1–Q15 (planejamento)",
           "Entender o que a prova pede e organizar a resolução antes de começar.",
           "[anexo: AEDI_Enunciado_Prova.pdf] \"do mesmo professor que é autor do livro temos que fazer essa prova passo a passo e gerar os itens integraveis conforme escrito no documento anexo aqui avalie como pode ser realizado esse trabalho, escreva o roteiro passo a passo para resolução\"",
           "Roteiro em documento compartilhado: avaliação e pontuação, estrutura do repositório, implementação da Parte A, método e armadilhas de cada questão, memorial, cronograma até 09/12 e ambiguidades do enunciado. Para dar ordens de grandeza, rodou um protótipo do gerador com semente de teste (202699).",
           "Conferência das regras e da pontuação contra o enunciado.",
           "Erro de digitação no roteiro (\"A tempo médio\"), corrigido na mesma sessão."),
        it("12/11/2026", "Decisões de implementação",
           "Fechar os pontos em aberto do enunciado.",
           "\"pode ser tudo como está na proposta\" → \"falta o que\"",
           "Registro das decisões no roteiro: calendário real (fev/2024 com 29 dias), trimestre = q(t) de 1 a 12, coluna p_programado, planilha gerada pelo código, VaR da Q8-d com todas as unidades-mês, p̄ por unidade na Q14.",
           "O número do grupo e o uso de Python foram informados pelo grupo na tabela do roteiro."),
        it("12/11/2026", "Q1-a, Q1-b",
           "Implementar o gerador (Parte A) e as bases num repositório.",
           "\"use esse respositório para o código https://github.com/diegocasagrande/aedi\" → \"salve os arquivos nessa pasta https://drive.google.com/drive/folders/1fhICSMGAVKpyEv8afX6zrzEAQgXnIySQ\"",
           "Anexos: src/gerador.py, src/inversa.py, main.py, README.md (commit 2d63be9). Bases e hashes sha256. Arquivos salvos na pasta PROVA do Drive. O envio ao GitHub falhou por falta de permissão; o commit foi entregue em arquivo bundle.",
           "Duas execuções com hashes idênticos; contagens, taxa de materialização e tempos médios comparados com os valores programados; teste KS das inversas contra o numpy.",
           "A exportação inicial das bases usava formato numérico com 6 algarismos significativos, o que arredondaria totais grandes (perda_total); percebido e corrigido antes do commit."),
        it("12/11/2026", "Q1, Q2-c",
           "Ter os números da Parte A numa planilha.",
           "\"Crie uma planilha a partir da sua última resposta.\"",
           "Planilha compartilhada com conferência estimado × programado, tipos de ataque com σ/√n, inversas, lista de arquivos e pendências.",
           "Fórmulas da planilha lidas de volta e conferidas; qui-quadrado dos tipos recalculado."),
        it("13/11/2026", "Q1",
           "Entender a semente do gerador.",
           "\"Confere como ficou a seed, me explica porque?\"",
           "Explicação: semente = 202600 + nº do grupo; gerador pseudoaleatório (PCG64); reprodutibilidade; bases diferentes por grupo; importância da ordem dos sorteios.",
           "Conferido contra o enunciado e por execução (mesmos três primeiros sorteios com a mesma semente)."),
        it("13/11/2026", "Organização do trabalho",
           "Planejar a execução e a auditoria.",
           "\"resume o plano de execução e como podemos organizar em issues talvez para registro e auditoria?\"",
           "Plano em quatro marcos, 22 issues propostas, modelo de issue e ligação das issues com o memorial.", "—"),
        it("13/11/2026", "Q1",
           "Corrigir o número do grupo (estava 3).",
           "\"o grupo estava errado... corrigi para 4\"",
           f"Semente alterada para 2026{grupo:02d}, bases regeradas (commit 545e564).",
           "Hashes de duas execuções idênticos; números da Parte A recalculados."),
        it("13/11/2026", "Q2 a Q15",
           "Executar o plano completo.",
           "\"pode executar todo o plano\"",
           "Anexos: src/q02_verificacao.py … src/q14_smc_risco.py, src/relatorio.py, tabelas e figuras em saidas/, relatório técnico, parecer executivo e este registro (commit fa4c144).",
           "Verificação independente feita pela IA a partir das bases, sem o código do projeto: t da Q8-a, z da Q8-b, VaR da Q4-e, F = t² da Q10, LR de Kupiec da Q8-d, valor preditivo da Q5-c e ROI da Q14-e coincidiram; duas execuções com resultados idênticos. Conferência pelo grupo: " + sugestoes.CONFERENCIA_GRUPO,
           "Escolhas de modelagem da IA que o grupo deve validar: VaR da Q8-d sobre todas as unidades-mês; índices sazonais com e sem abril/2025 (Q12); efeito do SOC no tempo e na severidade da Q14-d. Ajustes de formatação de tabelas e listas no relatório foram corrigidos pela IA ao revisar o PDF."),
        it("13/11/2026", "Entrega (repositório)",
           "Dar acesso de escrita ao repositório GitHub.",
           "\"?como concedo acesso ao repositório git?\" → \"teste acesso ao git\"",
           "Instruções para instalar o app do Claude no repositório; após a liberação, envio dos três commits ao branch main.",
           "git ls-remote confirmou o mesmo commit no servidor e localmente."),
        it("13/11/2026", "Entrega (revisão final)",
           "Conferir se tudo foi feito e concluir as pendências.",
           "\"isso, agora confere se já fez tudo e pode fazer todo o resto\"",
           "Checklist contra o enunciado; memorial com os nove campos; atualização da pasta PROVA no Drive, da planilha e do roteiro para o grupo 4.",
           "Checklist dos entregáveis e das questões contra o enunciado."),
        it(**sugestoes.INTERACAO_11),
    ]
    for d, decisao in zip(lista, sugestoes.DECISOES):
        d["Decisão do grupo"] = decisao
    return lista


def texto_memorial(R: dict) -> str:
    grupo = R["q01"]["grupo"]
    blocos = []
    for k, d in enumerate(interacoes(grupo), 1):
        linhas = [f"### Interação {k} — {d['Questão atendida']}", ""]
        for campo, valor in d.items():
            if campo == "Decisão do grupo":
                valor = sugestoes.M(valor)
            valor = valor.replace(sugestoes.CONFERENCIA_GRUPO, sugestoes.M(sugestoes.CONFERENCIA_GRUPO))
            linhas.append(f"* **{campo}:** {valor}")
        blocos.append("\n".join(linhas))
    corpo = "\n\n".join(blocos)
    legenda = "" if sugestoes.FINAL else sugestoes.S(sugestoes.LEGENDA) + "\n"
    return f"""---
title: "Memorial do Uso de IA — Grupo {grupo}"
lang: pt-BR
---

O grupo usou ferramenta de IA. Este memorial registra, para cada interação relevante, os nove campos pedidos no enunciado. A mesma informação está em planilha (`memorial_ia/registro.xlsx`). O código gerado está no repositório, identificado pelo commit indicado em cada interação, e o histórico exportado da conversa deve ser anexado em `memorial_ia/anexos/`.

**Ferramenta usada em todas as interações:** {FERRAMENTA}.

{legenda}

## Registro das interações

{corpo}

## Verificações sugeridas antes da entrega

1. Rodar `python main.py --grupo {grupo}` em outra máquina e comparar `dados/sha256.json`.
2. Recalcular à mão, ou na planilha, um resultado por questão: por exemplo o t da Q8-a, o VaR da Q4-e, o F = t² da Q10-a e o ROI da Q14-e.
3. Ler cada interpretação do relatório e reescrevê-la com as palavras do grupo: a arguição cobra o entendimento de todos.

## Reflexão final

{sugestoes.reflexao()}
"""


def salvar_registro_xlsx(R: dict, caminho: str) -> None:
    df = pd.DataFrame(interacoes(R["q01"]["grupo"]))
    df.to_excel(caminho, index=False, sheet_name="registro")
    if sugestoes.FINAL:
        return
    from openpyxl import load_workbook
    from openpyxl.styles import PatternFill
    wb = load_workbook(caminho)
    ws = wb["registro"]
    amarelo = PatternFill("solid", fgColor="FFFF00")
    col_dec = list(df.columns).index("Decisão do grupo") + 1
    col_ver = list(df.columns).index("Verificação") + 1
    for i, d in enumerate(df.to_dict("records"), start=2):
        ws.cell(i, col_dec).fill = amarelo
        if sugestoes.CONFERENCIA_GRUPO in d["Verificação"] or d["Questão atendida"] == sugestoes.INTERACAO_11["questao"]:
            ws.cell(i, col_ver).fill = amarelo
    wb.save(caminho)


def converter(md_path: str, docx_path: str, pdf: bool = True) -> int | None:
    subprocess.run(["pandoc", md_path, "-o", docx_path, "--resource-path", RAIZ, "--columns", "40"], check=True)
    if not pdf:
        return None
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", os.path.dirname(docx_path), docx_path],
                   check=True, capture_output=True)
    pdf_path = docx_path[:-5] + ".pdf"
    out = subprocess.run(["pdfinfo", pdf_path], capture_output=True, text=True).stdout
    return int([l for l in out.splitlines() if l.startswith("Pages")][0].split()[-1])


def gerar(final: bool = False):
    sugestoes.FINAL = final
    with open(ARQ_RESULTADOS, encoding="utf-8") as fh:
        R = json.load(fh)
    b = carregar()
    os.makedirs(REL, exist_ok=True)
    mem = os.path.join(RAIZ, "memorial_ia")
    os.makedirs(mem, exist_ok=True)
    arquivos = {
        os.path.join(REL, "relatorio_tecnico.md"): sugestoes.inserir_leituras(texto_relatorio(R, b), R),
        os.path.join(REL, "parecer_executivo.md"): texto_parecer(R),
        os.path.join(mem, "registro_interacoes.md"): texto_memorial(R),
    }
    salvar_registro_xlsx(R, os.path.join(mem, "registro.xlsx"))
    paginas = {}
    for caminho, txt in arquivos.items():
        txt = escapar_sublinhados(espacar_listas(txt))
        with open(caminho, "w", encoding="utf-8") as fh:
            fh.write(txt)
        paginas[os.path.basename(caminho)] = converter(caminho, caminho[:-3] + ".docx")
    print("páginas:", paginas)
    return paginas


if __name__ == "__main__":
    gerar()
