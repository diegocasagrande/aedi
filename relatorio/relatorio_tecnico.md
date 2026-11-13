---
title: "Risco Cibernético por Simulação de Monte Carlo — Estudo de caso ANDI"
subtitle: "Relatório técnico — Questões 1 a 14"
author: "Grupo 4 · Análise Estatística de Dados e Informações (PPCA/UnB)"
date: "Semente do gerador: 202604 · Entrega: 09/12/2026"
lang: pt-BR
---

**Integrantes:** (preencher)

**Como reproduzir.** `python main.py --grupo 4` recria as cinco bases (hashes sha256 em `dados/sha256.json`), todas as tabelas (`saidas/tabelas/`), figuras (`saidas/figuras/`), a planilha `saidas/resultados.xlsx` e este relatório. Nível de significância: α = 5% em todos os testes, salvo indicação. Cada análise que sorteia números usa um fluxo próprio derivado da semente, `default_rng([202604, nº da questão])`, para não consumir números do gerador das bases.

# Parte A — O modelo gerador

## Questão 1 — Implementação

**a) Os quatro passos da Seção 12.2 no código.** O arquivo `src/gerador.py` está organizado pelos quatro passos, marcados em comentários:

| Passo | Onde está no código |
| :------------- | :----------------------------------------------------------- |
| 1. Modelar | Bloco de parâmetros: equações e constantes das Etapas A1 a A5 (λ trimestral, S\_m, C\_t, tabela de tipos, logística, severidade) |
| 2. Sortear | `etapa_a1` (unidades), laço mensal com N ~ Poisson (A2) e `etapa_a3_a5` (atributos, materialização e severidade), todos a partir de um único gerador uniforme |
| 3. Calcular | Montagem de `ataques`, `perdas` e das agregações `painel_trimestral` (288 linhas, com zeros) e `serie_mensal` (36 linhas) |
| 4. Analisar | Questão 2 (`src/q02_verificacao.py`): o que foi gerado é comparado com o que foi programado |

A ordem dos sorteios é fixa (unidades → contagens do mês → atributos de cada ataque, unidade por unidade). Ela faz parte da reprodutibilidade: com a semente 202604, a mesma ordem gera sempre as mesmas bases, verificado pelos hashes.

**b) Do uniforme a cada distribuição (Seção 12.5).** Tudo parte de U ~ Uniforme(0, 1) do gerador PCG64 do numpy:

| Distribuição | Como é sorteada a partir de U | Uso |
| :-------------------------- | :-------------------------------------------------- | :------------------------------------ |
| Uniforme discreta {a..b} | a + ⌊U·(b − a + 1)⌋ | servicos (10..30), dia do mês |
| Uniforme contínua (a, b) | a + U·(b − a) | treino (0..12 h) |
| Bernoulli(p) | 1 se U < p | soc, fora\_expediente, materializou |
| Categórica | menor k com U < F(k) (probabilidades acumuladas) | tipo de ataque |
| Triangular(a; c; b) | inversa implementada pelo grupo (abaixo) | patch, cvss |
| Exponencial(θ) | T = −θ·ln(1 − U), implementada pelo grupo | tempo de detecção |
| Poisson(λ) | `rng.poisson` (inversão da acumulada / PTRS) | ataques por unidade-mês |
| Normal(0; σ) | `rng.normal` (método ziggurat) | erro ε da severidade |

Para a Triangular, com F\_c = (c − a)/(b − a), a inversa é X = a + √(U(b − a)(c − a)) se U < F\_c e X = b − √((1 − U)(b − a)(b − c)) caso contrário. As duas inversas (`src/inversa.py`) foram comparadas com as funções do numpy em 100.000 sorteios:

| Distribuição | Média (grupo) | Média (numpy) | P95 (grupo) | P95 (numpy) | KS | p-valor |
| :---------------------- | ---------------: | ---------------: | -------------: | -------------: | --------: | ---------: |
| Exponencial(θ=4) | 4,011 | 3,985 | 12,07 | 11,95 | 0,004 | 0,363 |
| Exponencial(θ=12) | 11,939 | 11,954 | 35,67 | 35,66 | 0,002 | 0,981 |
| Triangular(60;80;95) | 78,355 | 78,329 | 89,87 | 89,90 | 0,004 | 0,503 |
| Triangular(5;7,5;10) | 7,501 | 7,502 | 9,21 | 9,21 | 0,004 | 0,425 |

Em nenhum caso o teste de Kolmogorov-Smirnov rejeita a igualdade das distribuições (p-valores entre 0,36 e 0,98): a inversa do grupo e a função pronta geram a mesma distribuição.

**c) Justificativa das distribuições (tabela da Seção 12.4).** Contagem de eventos raros por período → **Poisson**; ocorre/não ocorre (SOC, fora do expediente, materialização) → **Bernoulli**; severidade em R$ (positiva, assimétrica, cauda pesada) → **Lognormal**; tempo até a detecção → **Exponencial**; grandezas com pouca informação, só faixa plausível (patch, CVSS por tipo) → **Triangular**; treino sem valor mais provável → **Uniforme**; erro do log da perda, soma de muitos fatores → **Normal**.

Usar a Normal para a severidade seria um erro grave por três motivos, que os próprios dados mostram. (i) Ajustando uma Normal às perdas observadas (média R$ 70.051, desvio R$ 123.622), 28,5% das perdas seriam **negativas**, o que não existe. (ii) A Normal é simétrica, e as perdas têm assimetria 5,03. (iii) A Normal subestima a cauda: seu quantil de 99,9% é R$ 452.073, contra R$ 1.287.463 observado. A cauda é justamente o que define o risco, e a Normal a cortaria.

## Questão 2 — Verificação do gerador

**a) Média mensal por unidade.** A média observada de ataques por mês acompanha a média teórica dos λ\_u,t (correlação 0,92; Figura 1). Medindo a diferença em erros padrão (√(λ̄/36)), 3 das 24 unidades ficam fora de ±1,96 (z de −3,00 a 1,96); o esperado por acaso seria cerca de 1,2. As unidades fora da faixa têm z de 1,96, −2,13, −3,00; o excesso é pequeno e compatível com a flutuação de 36 meses (a correlação forte mostra que o gerador segue λ).

![Figura 1 — Média mensal observada × teórica por unidade (barras: IC 95%).](/home/claude/aedi/saidas/figuras/q02a_media_por_unidade.png){width=11cm}

**b) Dispersão.** Na unidade 23 (sem SOC), a razão variância/média das 36 contagens é 1,13; entre as unidades sem SOC ela varia de 0,84 a 1,66 (média 1,20). Fica um pouco acima de 1 porque λ muda de mês a mês (sazonalidade, tendência e a campanha de abril/2025): medindo a dispersão em torno do λ de cada mês, o índice médio cai para 1,07, como exige a Poisson. Juntando as 24 unidades, a razão sobe para 1,47 (variância 5,06 para média 3,43). A variância total soma a variância dentro das unidades (4,26) e a variância entre as médias das unidades (0,95): é a **heterogeneidade** (unidades com λ diferentes) que gera a superdispersão, não uma falha da Poisson.

**c) Tipos e materialização.**

| Tipo | Ataques | Observado | Programado | σ/√n | z |
| :------------- | ---------: | -----------: | ------------: | --------: | --------: |
| Phishing | 1005 | 33,9% | 35% | 0,88% | −1,26 |
| Força bruta | 658 | 22,2% | 20% | 0,73% | 2,98 |
| Malware | 422 | 14,2% | 15% | 0,66% | −1,17 |
| Exploração | 444 | 15,0% | 15% | 0,66% | −0,04 |
| DDoS | 279 | 9,4% | 10% | 0,55% | −1,07 |
| Ransomware | 157 | 5,3% | 5% | 0,40% | 0,74 |

O qui-quadrado de aderência dá 10,87 com 5 g.l. (crítico 11,07, p = 0,0540): as frequências são compatíveis com as programadas a 5%, ainda que por pouco, puxadas por Força bruta (z = 2,98). Com seis comparações, um z perto de 3 é raro mas não impossível. A taxa de materialização observada é 42,09% contra a média dos p\_i de 43,11%; o erro de simulação (√Σp\_i(1 − p\_i)/n) é 0,80%, então a diferença equivale a z = −1,28. As discrepâncias são do tamanho do erro σ/√n da Seção 12.3: o gerador faz o que foi programado.

# Parte B — Análise das bases

## Questão 3 — Dos dados à decisão

**a) Tipos de variáveis e estrutura.** Em `ataques.csv`: tipo, unidade, fora\_expediente e materializou são **qualitativas nominais** (as duas últimas dicotômicas 0/1); mês é qualitativa ordinal (cíclica); trimestre e ano são quantitativas discretas (índices de tempo); cvss e tempo\_deteccao\_h são **quantitativas contínuas** (o CVSS é registrado com uma casa, mas é contínuo por natureza); id\_ataque e data são identificador e carimbo temporal. Em `perdas.csv`, perda\_rs é quantitativa contínua. Quanto à estrutura, ataques e perdas são **microdados em painel** (cada evento ligado a uma unidade e a uma data); o painel trimestral é um painel balanceado 24 × 12 e a série mensal é uma série temporal.

* **População:** todos os ataques que a ANDI sofre (o processo gerador, em qualquer período).
* **Amostra:** os 2.965 ataques e 1.248 perdas observados em 2023–2025.
* **Unidade de observação:** o ataque (em `perdas.csv`, o incidente materializado).
* **Parâmetros:** quantidades da população, como a taxa média de ataques λ, a probabilidade de materialização p e a mediana da perda por tipo; as estatísticas da amostra os estimam.

**b) Distribuições de frequências.**

| Tipo | Freq. absoluta | Freq. relativa | Abs. acumulada | Rel. acumulada |
| :------------- | ----------------: | ----------------: | ----------------: | ----------------: |
| Phishing | 1005 | 33,9% | 1005 | 33,9% |
| Força bruta | 658 | 22,2% | 1663 | 56,1% |
| Exploração | 444 | 15,0% | 2107 | 71,1% |
| Malware | 422 | 14,2% | 2529 | 85,3% |
| DDoS | 279 | 9,4% | 2808 | 94,7% |
| Ransomware | 157 | 5,3% | 2965 | 100,0% |

Para a perda, a regra de Sturges dá k = 1 + 3,322·log₁₀(1.248) ≈ 11 classes de amplitude R$ 131.012. A primeira classe concentra 86,9% das perdas e as duas primeiras, 95,2%; as nove restantes guardam poucas perdas cada, até R$ 1.442.080. Classes de mesma amplitude escondem a forma de uma variável tão assimétrica, como mostra a Figura 2: em escala logarítmica o histograma fica quase simétrico.

![Figura 2 — Perda por incidente: 11 classes de Sturges (esquerda) e escala log10 (direita).](/home/claude/aedi/saidas/figuras/q03b_histograma_perda.png){width=14cm}

**c) Medidas de posição.**

| Tipo | n | Média | Mediana | Moda (classe modal) | Média/mediana |
| :------------- | --------: | ------------: | ------------: | ----------------: | ---------------: |
| Phishing | 384 | R$ 34.081 | R$ 20.301 | R$ 17.531 | 1,68 |
| Força bruta | 199 | R$ 22.502 | R$ 15.417 | R$ 11.264 | 1,46 |
| Malware | 192 | R$ 59.771 | R$ 35.752 | R$ 54.945 | 1,67 |
| Exploração | 254 | R$ 95.614 | R$ 56.110 | R$ 76.808 | 1,70 |
| DDoS | 118 | R$ 62.303 | R$ 29.912 | R$ 93.802 | 2,08 |
| Ransomware | 101 | R$ 264.802 | R$ 187.553 | R$ 89.237 | 1,41 |
| Geral | 1248 | R$ 70.051 | R$ 29.734 | R$ 66.451 | 2,36 |

Como a perda é contínua, nenhum valor se repete; a moda é o ponto médio da classe modal (Sturges dentro de cada tipo) e depende da largura escolhida. A média é de 1,4 a 2,4 vezes a mediana: poucas perdas muito grandes a puxam para cima. **A mediana representa melhor a "perda típica" de um incidente** (geral R$ 29.734). A média continua necessária para o orçamento: a perda total é o número de incidentes vezes a média, não a mediana.

## Questão 4 — Dispersão, formato e associação

**a) Dispersão por tipo.**

| Tipo | Desvio-padrão | CV | AIQ | Outliers | % da perda do tipo nos outliers |
| :------------- | ---------------: | --------: | ------------: | ----------: | ----------------: |
| Phishing | R$ 42.410 | 1,24 | R$ 29.301 | 31 | 34% |
| Força bruta | R$ 24.936 | 1,11 | R$ 20.150 | 18 | 35% |
| Malware | R$ 94.090 | 1,57 | R$ 47.675 | 12 | 33% |
| Exploração | R$ 128.340 | 1,34 | R$ 82.400 | 16 | 31% |
| DDoS | R$ 141.372 | 2,27 | R$ 42.843 | 11 | 49% |
| Ransomware | R$ 225.345 | 0,85 | R$ 218.176 | 9 | 26% |

Em termos relativos o tipo mais arriscado é **DDoS** (CV = 2,27): sua perda média é moderada, mas o desvio-padrão é 2,3 vezes a média. Ransomware tem o maior desvio absoluto e CV de 0,85: é caro de forma mais consistente.

**b) Outliers.** A regra de 1,5 × AIQ marca de 6% a 9% das perdas de cada tipo (Figura 3). Elas **não são erros a remover: são a essência do risco**. Esses poucos casos respondem por 26% a 49% da perda total de cada tipo; retirá-los subestimaria a perda anual e, sobretudo, a cauda que o VaR e o CVaR medem. Em dados Lognormais a regra do box-plot sempre "acusa" valores na cauda direita.

![Figura 3 — Box-plots da perda por tipo, em escala linear e logarítmica.](/home/claude/aedi/saidas/figuras/q04b_boxplots.png){width=15cm}

**c) Formato.** A perda tem assimetria 5,03 e curtose 38,33 (a Normal tem 0 e 3). O ln(perda) tem assimetria 0,24 e curtose 3,00: **o logaritmo transforma uma distribuição muito assimétrica e de cauda pesada em outra quase Normal**, o que é a definição da Lognormal e justifica modelar ln(perda) por regressão (Q9–Q10).

**d) Covariâncias e correlações (painel).** As matrizes completas estão em `saidas/tabelas/q04d_*.csv`; as correlações estão na Figura 4. n\_ataques cresce com serviços expostos (r = 0,50) e cai com SOC (−0,14) e treino (−0,09), nos sentidos esperados. A correlação de n\_ataques com patch é praticamente nula (0,00), embora patch reduza ataques no gerador: nesta amostra de 24 unidades, patch é positivamente correlacionado com serviços (0,30), e o efeito de serviços mascara o de patch. **Correlação simples não é efeito parcial**: a regressão múltipla da Q11 separa os dois. A perda total trimestral correlaciona com o número de ataques (0,41) e, mais fortemente que ele, com SOC (−0,32), porque o SOC reduz ataques, materialização e severidade ao mesmo tempo.

![Figura 4 — Matriz de correlações no painel trimestral (288 observações).](/home/claude/aedi/saidas/figuras/q04d_correlacoes.png){width=9cm}

**e) VaR histórico.** O percentil 95 das 36 perdas mensais totais é **R$ 4,48 mi** (média mensal R$ 2,43 mi). Com 36 pontos, esse quantil fica na posição 34,25 da amostra ordenada, entre o 2º maior mês (R$ 5,10 mi) e o 3º (R$ 4,27 mi). Ele depende de dois ou três meses: retirando só o maior mês (2024-09), o VaR cai para R$ 4,27 mi. Um quantil de cauda estimado com tão poucas observações é muito instável, e é por isso que a Parte C o estima por simulação.

## Questão 5 — Probabilidade e Bayes

**a) Tipo × materialização.** A tabela de contingência completa e as probabilidades conjuntas estão em `saidas/tabelas/q05a_*.csv`. A probabilidade de materializar varia de 30,2% (Força bruta) a 64,3% (Ransomware). **P(materializou | ransomware) = 0,643**, mas **P(ransomware | materializou) = 0,081**. As duas diferem porque têm denominadores diferentes: a primeira divide pelos 157 ransomwares, a segunda pelas 1.248 perdas. Ransomware materializa muito (CVSS alto), mas é só 5,3% dos ataques, então é uma fração pequena das perdas. Confundir as duas é o erro de inverter a condição.

**b) SOC e materialização.** P(SOC) = 0,305, P(materializou) = 0,421 e P(SOC ∩ materializou) = 0,0728, bem abaixo de P(SOC)·P(materializou) = 0,1283. **Os eventos não são independentes**: com SOC, materializam 23,9% dos ataques; sem SOC, 50,1% (qui-quadrado de independência = 176,7, p < 0,0001).

**c) Regra "alarme se cvss ≥ 7".** Sensibilidade P(alarme | materializou) = **0,329**; especificidade P(sem alarme | não materializou) = **0,857**; prevalência = **0,421**. Por Bayes,

P(materializou | alarme) = (0,329 × 0,421) / (0,329 × 0,421 + 0,143 × 0,579) = **0,626**,

idêntico à contagem direta (411 materializados entre 657 alarmes = 0,626). A regra é específica mas pouco sensível: deixa passar dois terços das perdas, porque muitos ataques de CVSS moderado materializam quando a detecção demora.

**d) Árvore de triagem.** A Figura 5 mostra a árvore da Seção 3.8. Com a prevalência pela metade (21,0%), sensibilidade e especificidade não mudam, mas o valor preditivo do alarme cai de 0,626 para **0,380**: a maioria dos alarmes passa a ser falso positivo. Quanto mais raro o evento, menos um alarme significa, mesmo com o mesmo detector.

![Figura 5 — Árvore de triagem com a prevalência observada e com a prevalência pela metade.](/home/claude/aedi/saidas/figuras/q05d_arvore_triagem.png){width=15.5cm}

## Questão 6 — Distribuições

**a) Poisson.** Para a unidade 23 (sem SOC, média mensal mediana entre as sem SOC), λ̂ = 3,33 ataques/mês. Pela Poisson, P(N ≥ 6) = 1 − P(N ≤ 5) = **0,121**; na base, 5 dos 36 meses tiveram 6 ou mais ataques (**0,139**). A diferença corresponde a menos de um mês, dentro do esperado para 36 observações (Figura 6).

![Figura 6 — Contagem mensal da unidade e distribuição de Poisson ajustada.](/home/claude/aedi/saidas/figuras/q06a_poisson_unidade.png){width=10cm}

**b) Exponencial.** Para unidades com SOC e ataques no expediente (591 ataques), a Exponencial de média 4 h dá P(T > 8) = e^(−8/4) = **0,135**; com a média estimada (3,91 h), 0,129. A proporção observada é **0,120** (z = −1,08 contra o valor teórico): o modelo Exponencial se sustenta.

**c) Lognormal.** Nos gráficos Q-Q (Figura 7), ln(perda) segue a reta da Normal para os dois tipos (correlação do Q-Q de 0,992 e 0,999; Shapiro-Wilk p = 0,16 e 0,83): **a hipótese Lognormal se sustenta**. A maior perda de ransomware (R$ 1.174.959) tem escore Z de 2,03 na escala log; a de phishing (R$ 332.677), 2,83. São máximos normais para amostras de 101 e 384 valores (o maior de n Normais costuma ficar perto de 2,5 e 2,8 desvios). Na escala original, os mesmos valores teriam Z de 4,04 e 7,04, o que parece "extremo" só porque o escore Z supõe simetria.

![Figura 7 — Gráficos Q-Q de ln(perda) contra a Normal: ransomware e phishing.](/home/claude/aedi/saidas/figuras/q06c_qq_lognormal.png){width=13cm}


## Questão 7 — Amostragem e estimação

**a) Tempo médio de detecção.**

| Grupo | n | Média (h) | IC 95% (t) | θ programado | Contém θ? |
| :------------------------- | --------: | -----------: | ----------------: | --------------: | -----------: |
| Com SOC (todos) | 904 | 4,70 | [4,39; 5,01] | 4 | não |
| Com SOC (só expediente) | 591 | 3,91 | [3,59; 4,22] | 4 | sim |
| Sem SOC (todos) | 2061 | 13,89 | [13,27; 14,51] | 12 | não |
| Sem SOC (só expediente) | 1341 | 11,53 | [10,91; 12,16] | 12 | sim |

Os intervalos com todos os ataques **não contêm** 4 h nem 12 h. O motivo é fora\_expediente: 35% dos ataques têm o tempo multiplicado por 1,5, então a média verdadeira é θ·(0,65 + 0,35·1,5) = 1,175·θ, isto é, 4,7 h com SOC e 14,1 h sem SOC, valores que os ICs contêm. Restringindo aos ataques no expediente, os intervalos voltam a conter 4 h e 12 h. O θ programado é a média de uma subpopulação, não a da população toda.

**b) Proporção de materializados.** p̂ = 0,4209, IC 95% = [0,4031; 0,4387]. Para uma margem de ±2 p.p. com 95%, n = 1,96²·p̂(1 − p̂)/0,02² = **2.341** ataques auditados (2.401 no pior caso, p = 0,5).

**c) Teorema Central do Limite.**

| n | Desvio das 2.000 médias | σ/√n | Assimetria das médias |
| --------: | ----------------: | -----------: | ----------------: |
| 5 | R$ 54.543 | R$ 55.264 | 2,22 |
| 30 | R$ 22.932 | R$ 22.561 | 0,99 |
| 100 | R$ 12.250 | R$ 12.357 | 0,46 |

O desvio das médias acompanha σ/√n nos três tamanhos (Figura 8). Mas a forma converge devagar: com n = 30 as médias ainda têm assimetria 0,99, e mesmo com n = 100 ela é 0,46. A regra prática "n = 30 basta" vale para variáveis pouco assimétricas; perda\_rs tem assimetria 5,03 e cauda pesada, então um IC Normal para a perda média com n = 30 ficaria curto do lado direito.

![Figura 8 — Distribuição de 2.000 médias amostrais de perda_rs para n = 5, 30 e 100.](/home/claude/aedi/saidas/figuras/q07c_tcl.png){width=15cm}


## Questão 8 — Testes de hipóteses e backtesting

**a) Contrato do SOC (máximo 4 h).** (1) H₀: μ ≤ 4 h; Hₐ: μ > 4 h. (2) Estatística t de Student (σ desconhecido). (3) α = 5%, unilateral à direita. (4) Rejeitar H₀ se t > t₀,₀₅;903 = 1,647. (5) n = 904, x̄ = 4,70 h, s = 4,73 h, t = (x̄ − 4)/(s/√n) = **4,45**, p-valor < 0,0001. (6) **Rejeita-se H₀**: o tempo médio de detecção nas unidades com SOC supera o prometido. O resultado não deveria surpreender: o θ = 4 h vale só para ataques no expediente; com o fator 1,5 fora do expediente a média verdadeira é 4,7 h. Testando apenas os ataques no expediente, x̄ = 3,91 h, t = −0,59 e p = 0,723: o contrato é cumprido no expediente e descumprido fora dele.

**b) Meta de materialização (máximo 40%).** (1) H₀: p ≤ 0,40; Hₐ: p > 0,40. (2) Z para proporção. (3) α = 5%, unilateral. (4) Rejeitar se Z > 1,645. (5) p̂ = 0,4209, Z = (p̂ − 0,40)/√(0,40·0,60/2965) = **2,32**, p-valor = 0,0101. (6) **Rejeita-se H₀**: há evidência de que mais de 40% dos ataques se materializam; a meta não está sendo cumprida.

**c) Erros no item (a).** Erro Tipo I: concluir que o SOC descumpre o contrato quando ele cumpre, e aplicar multa ou trocar de fornecedor sem razão. Erro Tipo II: aceitar que o SOC cumpre as 4 h quando ele é mais lento, deixando a ANDI exposta por mais tempo a cada ataque. Para a ANDI o **Tipo II é mais caro**: cada hora a mais encarece a perda em cerca de 2% e aumenta a chance de materialização, numa base de dezenas de milhões por ano; o custo do Tipo I é uma disputa contratual.

**d) Backtesting.** Com 2023–2024 (576 unidades-mês, 32% delas sem perda), o VaR 95% da perda mensal por unidade é **R$ 346.555**. Em 2025 (288 unidades-mês) ele foi excedido **25 vezes**, contra 14,4 esperadas (8,7% contra 5%). Kupiec: LR = **6,80** > 3,84 (p = 0,0091): **o modelo é rejeitado**, por subestimar o risco. Nos próprios anos de estimação a taxa de exceções foi 5,2% (2023) e 4,9% (2024). As causas, à luz do gerador: (i) **tendência**, já que λ cresce 0,15 ataque por trimestre e a perda mensal média por unidade subiu de R$ 92.832 no treino para R$ 117.890 em 2025; (ii) **campanha de abril/2025**, que elevou os ataques em 80% naquele mês. Um VaR histórico estático não acompanha um processo que muda no tempo.

![Figura 9 — Perdas mensais por unidade em 2025 e o VaR 95% estimado em 2023–2024.](/home/claude/aedi/saidas/figuras/q08d_backtesting.png){width=13cm}

## Questão 9 — Correlação e regressão simples

**a) Correlação.** Entre perda\_rs e tempo, r = 0,217 (t = 7,85); entre ln(perda) e tempo, r = 0,228 (t = 8,27). Nos dois casos rejeita-se H₀: ρ = 0 (p < 0,0001). A correlação com a perda bruta é dominada por poucos valores extremos (Figura 10); o log torna a relação linear e homogênea.

![Figura 10 — perda e ln(perda) contra o tempo até a detecção, com a reta de mínimos quadrados.](/home/claude/aedi/saidas/figuras/q09_dispersao.png){width=15cm}

**b) Regressão.** ln(perda) = 10,136 + 0,01661·tempo. Como o modelo é log-linear, cada hora a mais de atraso multiplica a perda por e^β₁, ou seja, **+1,68% por hora** (um dia a mais, cerca de +49%).

**c) Ajuste.** R² = 0,052 e erro padrão da regressão s = 1,159 (em ln). Um R² baixo **não** invalida a conclusão: o coeficiente é estimado com precisão (t = 8,27) e o efeito existe; o tempo simplesmente explica uma parte pequena da variação. A variável omitida que mais infla o resíduo é o **tipo de ataque**: as medianas vão de R$ 10 mil a R$ 150 mil, e incluí-lo leva o R² a 0,43 (Q10-d); o restante é o erro ε próprio da Lognormal.

**d) Gauss-Markov.** São plausíveis: linearidade em ln(perda); independência entre perdas (Durbin-Watson = 1,94); homocedasticidade (Breusch-Pagan p = 0,78). A normalidade dos erros é aproximada (Jarque-Bera p = 0,004), pois o resíduo mistura tipos com medianas diferentes. O problema maior é o **viés de seleção**: só vemos perdas de ataques que se materializaram, e a materialização depende do tempo e do CVSS. Ataques de tipos baratos (CVSS baixo) quase só materializam quando a detecção demora: o tempo médio do phishing é 11,1 h entre todos os ataques e 17,0 h entre os materializados; no ransomware, 10,3 h e 11,6 h. Entre as perdas, tempos longos ficam associados a tipos baratos, e isso **atenua** β₁ (0,0166 na regressão simples contra 0,0225 controlando o tipo).

## Questão 10 — Inferência na regressão

**a) ANOVA.**

| Fonte | SQ | g.l. | QM | F |
| :----------- | ----------: | --------: | ---------: | --------: |
| Regressão | 91,95 | 1 | 91,9476 | 68,44 |
| Resíduos | 1.674,03 | 1246 | 1,3435 |  |
| Total | 1.765,98 | 1247 |  |  |

F = 68,438 e t(β₁) = 8,2727, com t² = 68,438 = F: na regressão simples os dois testes são o mesmo (p < 0,0001).

**b) IC de β₁.** 0,01661 ± 1,962 × 0,00201 = **[0,01267; 0,02055]**. Contém o valor programado 0,02, mas perto do limite superior, coerente com a atenuação por seleção discutida na Q9-d.

**c) Ataque detectado em 24 h.** Média de ln(perda): 10,535, IC 95% [10,463; 10,607], que em reais é **[R$ 34.998; R$ 40.423]**. Intervalo de previsão para uma perda individual: [8,260; 12,810], que em reais é **[R$ 3.866; R$ 365.951]**. Ao converter com exp(), o IC refere-se à **mediana** da perda (exp da média de um log); a média em reais seria R$ 73.634 (fator e^(s²/2) = 1,96). O intervalo de previsão é muito mais largo porque soma à incerteza sobre a reta a variância individual da perda (s² = 1,343 em ln), que não diminui com n; na escala original isso vira um fator de cerca de 95 entre os limites.

**d) Com dummies de tipo.** O R² vai de 0,052 para **0,432**, o erro padrão cai para 0,899 (próximo do σ = 0,9 programado), e β₁ = 0,02254 com IC **[0,01945; 0,02562]**, mais estreito (amplitude 0,0062 contra 0,0079) e centrado perto de 0,02. As dummies recuperam as razões entre medianas programadas:

| Tipo (base: Phishing) | Razão de medianas estimada | Programada |
| :---------------- | ----------------: | ------------: |
| DDoS | 1,51 | 1,67 |
| Exploração | 2,98 | 3,00 |
| Força bruta | 0,65 | 0,67 |
| Malware | 1,87 | 2,00 |
| Ransomware | 9,91 | 10,00 |


## Questão 11 — Regressão múltipla

**a) Modelo.** n\_ataques = β₀ + β₁·servicos + β₂·patch + β₃·treino + β₄·soc + β₅·trimestre + erro, no painel de 288 unidades-trimestre:

| Termo | Coeficiente | Erro padrão | t | p-valor | IC 95% |
| :------------ | -------------: | -------------: | --------: | ----------: | ------------------: |
| Intercepto | 12,7573 | 2,7764 | 4,59 | < 0,0001 | [7,292; 18,222] |
| servicos | 0,5637 | 0,0441 | 12,79 | < 0,0001 | [0,477; 0,650] |
| patch | −0,1463 | 0,0347 | −4,21 | < 0,0001 | [−0,215; −0,078] |
| treino | −0,3254 | 0,0563 | −5,78 | < 0,0001 | [−0,436; −0,215] |
| soc | −1,5338 | 0,4326 | −3,55 | 0,0005 | [−2,385; −0,682] |
| trimestre | 0,2647 | 0,0583 | 4,54 | < 0,0001 | [0,150; 0,379] |

**b) Testes e interpretação.** F global = 39,72 com (5; 282) g.l., p < 0,0001: o modelo explica parte relevante dos ataques. Todos os t individuais são significativos a 5%. R² = 0,413 e R² ajustado = 0,403. Para a gestão, mantendo o restante constante e por trimestre:

* cada serviço exposto a mais traz **+0,56 ataque**: fechar 10 serviços evitaria cerca de 5,6 ataques por trimestre na unidade;
* cada ponto percentual de cobertura de patches retira **0,15 ataque**;
* cada hora de treinamento retira **0,33 ataque**;
* um SOC dedicado retira **1,53 ataques**;
* a tendência acrescenta **0,26 ataque** por trimestre que passa.

**c) Comparação com os verdadeiros.**

| Termo | Estimado | Verdadeiro | IC 95% | Contém? |
| :----------- | ----------: | ------------: | ------------------: | ---------: |
| servicos | 0,564 | 0,50 | [0,477; 0,650] | sim |
| patch | −0,146 | −0,08 | [−0,215; −0,078] | sim |
| treino | −0,325 | −0,20 | [−0,436; −0,215] | não |
| soc | −1,534 | −1,40 | [−2,385; −0,682] | sim |
| trimestre | 0,265 | 0,15 | [0,150; 0,379] | não |

**3 dos 5 ICs contêm o valor verdadeiro.** "95% de confiança" descreve o procedimento: em muitas amostras, 95% dos intervalos cobririam o parâmetro. Mesmo com cinco ICs independentes, a chance de todos acertarem seria 0,95⁵ = 0,77, e errar dois tem probabilidade de cerca de 2%. Aqui há causas além do acaso. O coeficiente do trimestre absorve a campanha de abril/2025 e a sazonalidade, que não estão no modelo; com elas (item d), ele cai para 0,159 e o IC passa a conter 0,15. Além disso, os erros são heterocedásticos (item e), o que torna os erros padrão de MQO pouco confiáveis.

**d) Sazonalidade e campanha.**

| Termo | Coeficiente | Erro padrão | p-valor |
| :----------- | -------------: | -------------: | ---------: |
| trimestre | 0,159 | 0,067 | 0,0180 |
| Q2 | −0,175 | 0,624 | 0,7798 |
| Q3 | −0,276 | 0,571 | 0,6296 |
| Q4 | 0,968 | 0,590 | 0,1019 |
| campanha | 3,131 | 0,924 | 0,0008 |

O ajuste melhora: R² ajustado de 0,403 para 0,431, e o F parcial das quatro variáveis novas é 4,55 (p = 0,0014). O indicador de campanha é o termo mais forte: **+3,13 ataques** por unidade no trimestre abr–jun/2025. Entre as dummies sazonais, só Q4 se aproxima da significância (+0,97). Isso é coerente com a média dos S\_m no 4º trimestre (1,08, contra 0,95 no 1º); com 24 unidades e 3 anos a sazonalidade trimestral é fraca demais para se destacar do ruído.

**e) Diagnóstico.** VIFs entre 1,00 e 1,20: não há multicolinearidade. Os resíduos formam um **funil** (Figura 11; Breusch-Pagan p = 0,016): a variância dos resíduos sobe de 5,7 no quartil de menor valor ajustado para 16,0 no maior, acompanhando os ajustados médios (6,8 e 13,9). Isso é exatamente o que se espera de uma contagem Poisson, cuja variância é igual à média: unidades com mais ataques esperados oscilam mais. O Q-Q mostra resíduos aproximadamente Normais.

![Figura 11 — Resíduos × ajustados (com o envelope ±2√ajustado da Poisson) e Q-Q dos resíduos.](/home/claude/aedi/saidas/figuras/q11e_residuos.png){width=14cm}

**f) Sobreajuste.**

| Modelo (treino 2023–2024) | R² treino | R² ajustado treino | RMSE teste 2025 |
| :---------------- | -----------: | ----------------: | ----------------: |
| Sem ruído | 0,398 | 0,381 | 3,791 |
| Com 5 ruídos | 0,407 | 0,374 | 3,844 |

As cinco variáveis de puro ruído **aumentam o R² de treino** (como sempre acontece) mas **reduzem o R² ajustado e pioram o erro de previsão** em 2025: o modelo passou a ajustar ruído. O R² de treino não serve para escolher modelos; o R² ajustado e o erro fora da amostra servem.

## Questão 12 — Séries temporais

**a) Tendência e sazonalidade.** Os ataques anuais foram 902 (2023), 964 (2024) e 1.099 (2025). A média móvel de 12 meses sobe de 75,2 para 91,6 ataques/mês: há **tendência de alta** (Figura 12). A média móvel de 3 meses e a suavização exponencial (α = 0,11, estimado) mostram picos em março–abril e novembro e vales em fevereiro e junho, ou seja, **sazonalidade** sobreposta ao ruído. O ponto que mais chama atenção é **abril/2025, com 165 ataques**, quase o dobro da média.

![Figura 12 — Série mensal de ataques com médias móveis de 3 e 12 meses e suavização exponencial.](/home/claude/aedi/saidas/figuras/q12a_serie.png){width=15cm}

**b) Decomposição.** Usamos a decomposição **multiplicativa**, porque o gerador multiplica λ pelo fator S\_m: o efeito sazonal é proporcional ao nível e cresce com a tendência. Os índices foram calculados pela razão à média móvel centrada 2×12 e normalizados para média 1:

| Mês | S\_m programado | Estimado | Estimado sem abril/2025 |
| :-------- | ----------------: | ----------: | ----------------: |
| jan | 0,90 | 0,902 | 0,932 |
| fev | 0,85 | 0,840 | 0,868 |
| mar | 1,10 | 1,137 | 1,175 |
| abr | 1,10 | 1,381 | 1,027 |
| mai | 1,00 | 0,892 | 0,921 |
| jun | 0,95 | 0,840 | 0,868 |
| jul | 0,90 | 0,917 | 0,947 |
| ago | 0,95 | 0,964 | 0,996 |
| set | 1,00 | 1,023 | 1,057 |
| out | 1,05 | 0,964 | 0,996 |
| nov | 1,15 | 1,119 | 1,156 |
| dez | 1,05 | 1,023 | 1,057 |

O índice de abril sai **1,38** contra 1,10 programado: com só dois abris na janela da média móvel, a campanha de abril/2025 contamina o índice sazonal. Excluindo esse mês, o índice de abril cai para 1,03 e o erro absoluto médio dos 12 índices cai de 0,062 para 0,048 (correlação com os S\_m de 0,77 para 0,83). Com só três anos, cada índice se baseia em dois valores e erra cerca de ±0,05.

**c) ACF.** As autocorrelações ficam todas dentro da faixa ±1,96/√36 = ±0,327: a maior é 0,27. A defasagem 1 (0,21) reflete a tendência, e a defasagem 12 (0,11) a sazonalidade anual. Com 36 meses a ACF tem pouco poder: a sazonalidade do gerador é real (S\_m varia de 0,85 a 1,15), mas o ruído Poisson de cerca de ±9 ataques/mês é do mesmo tamanho que ela.

![Figura 13 — Índices sazonais estimados (com e sem abril/2025) × programados.](/home/claude/aedi/saidas/figuras/q12b_indices.png){width=11cm}

**d) Previsão e anomalias.** O modelo dessazonaliza a série com os índices sem abril/2025, ajusta uma tendência linear (+0,57 ataque/mês) e ressazonaliza. A previsão para 2026 soma **1.153 ataques**, de 81 (fevereiro) a 114 (novembro), com banda de 95% de ±17 ataques/mês (Figura 14). A regra dos 3σ sobre os resíduos **encontra abril/2025**, com resíduo de 8,6σ (calculando σ sem o próprio mês) e de 3,5σ mesmo usando os índices contaminados. **Nenhum falso alarme**: o maior |resíduo| dos demais meses é 1,9σ. Há uma ressalva: uma anomalia infla o próprio σ e o índice sazonal que a deveria revelar, então a detecção é mais robusta com estimativas que excluem o ponto testado.

![Figura 14 — Ajuste, previsão de 2026 com banda de 95% e alarme pela regra dos 3σ.](/home/claude/aedi/saidas/figuras/q12d_previsao.png){width=15cm}


## Questão 13 — Classificação

Treino: 1.866 ataques de 2023–2024; teste: 1.099 ataques de 2025.

**a) Regressão logística.**

| Termo | Coeficiente | Erro padrão | Razão de chances e^β | Programado | IC 95% contém? |
| :----------------- | -------------: | -------------: | ----------------: | ------------: | ----------------: |
| Intercepto | −2,9473 | 0,2440 | 0,052 | −2,80 | sim |
| cvss | 0,4853 | 0,0357 | 1,625 | 0,45 | sim |
| tempo (h) | 0,0564 | 0,0055 | 1,058 | 0,06 | sim |
| soc | −0,8633 | 0,1299 | 0,422 | −0,80 | sim |
| treino (h) | −0,0847 | 0,0135 | 0,919 | −0,08 | sim |
| fora\_expediente | 0,3589 | 0,1142 | 1,432 | 0,50 | sim |

Todos os coeficientes são significativos (p ≤ 0,0017) e **todos os ICs de 95% contêm o valor programado** na Etapa A4. Em razões de chances: cada ponto de CVSS multiplica as chances de materializar por 1,62; cada hora até a detecção, por 1,058 (+5,8% por hora); o SOC as multiplica por 0,42 (menos da metade); cada hora de treino, por 0,919; e o ataque fora do expediente, por 1,43.

**b) Dummies de tipo.** **Não deveriam ser significativas**: no gerador, o tipo só afeta a materialização através do CVSS, que já está no modelo. Os dados confirmam: o teste de razão de verossimilhança para as cinco dummies dá LR = 4,00 com 5 g.l. (p = 0,549), e nenhuma dummy é significativa isoladamente. Se o CVSS for retirado, as dummies passam a ser significativas (Exploração, Ransomware e Força bruta com p < 0,001): elas absorvem o efeito do CVSS, que difere por tipo. É o mesmo raciocínio de variável omitida da Q9.

**c) Árvore de decisão (profundidade 3).** As regras extraídas (íntegra em `saidas/tabelas/q13c_regras_arvore.txt`):

* **se tempo ≤ 15,1 h e cvss ≤ 6,25** → não materializa (P de 16% a 30%, conforme o CVSS);
* **se tempo ≤ 15,1 h e 6,25 < cvss ≤ 8,15** → não materializa, por margem mínima (49%);
* **se tempo ≤ 15,1 h e cvss > 8,15** → materializa (71%);
* **se tempo > 15,1 h e treino ≤ 10,4 h** → materializa (64% com cvss ≤ 4,95; 84% com cvss maior);
* **se tempo > 15,1 h, treino > 10,4 h e cvss ≤ 5,15** → não materializa (32%); com cvss > 5,15, materializa (64%).

A árvore usa CVSS (importância 0,53), tempo (0,41) e treino (0,07); SOC e fora do expediente não entram, pois seu efeito já passa pelo tempo de detecção.

**d) Desempenho no teste (2025, limiar 0,5).**

| Modelo | VN | FP | FN | VP | Acurácia | Precisão | Recall | F1 | AUC |
| :----------- | --------: | --------: | --------: | --------: | ----------: | ----------: | --------: | --------: | --------: |
| Logística | 522 | 113 | 213 | 251 | 0,703 | 0,690 | 0,541 | 0,606 | 0,770 |
| Árvore | 548 | 87 | 267 | 197 | 0,678 | 0,694 | 0,425 | 0,527 | 0,723 |

A logística é melhor em quase tudo, e sobretudo na AUC (0,770 contra 0,723; Figura 15). Com profundidade 3 a árvore só produz 8 probabilidades diferentes, e o modelo verdadeiro é ele próprio uma logística. Com limiar 0,5 as duas deixam escapar metade ou mais das perdas (recall 0,54 e 0,42).

![Figura 15 — Curvas ROC no conjunto de teste (2025).](/home/claude/aedi/saidas/figuras/q13d_roc.png){width=8.5cm}

**e) Limiar de custo mínimo.** Um falso negativo custa a perda mediana observada em 2023–2024 (R$ 29.247) e um falso positivo, R$ 3.000. O limiar que minimiza o custo no treino é **0,14**, próximo do valor teórico C\_FP/(C\_FP + C\_FN) = 0,093. Aplicado em 2025, ele derruba o custo dos erros de R$ 6,57 mi (limiar 0,5) para **R$ 1,89 mi** (Figura 16): o recall sobe para 0,97 e a precisão cai para 0,48, com 495 falsos positivos e só 14 falsos negativos. É a tensão α × β do cap. 7: baixar o limiar aceita mais erros do Tipo I (alarmes falsos, baratos) para reduzir os do Tipo II (perdas não tratadas, caras). Quando os custos são assimétricos, 0,5 não é neutro: favorece o erro mais caro.

![Figura 16 — Custo total dos erros no teste em função do limiar.](/home/claude/aedi/saidas/figuras/q13e_limiar_custo.png){width=10cm}


# Parte C — SMC de risco e decisão

## Questão 14 — Perda anual de 2026 e o pacote de controles

**a) Modelar.** A perda agregada anual é L = Σ\_u Σ\_(i=1..N\_u) X\_i, com N\_u o número de perdas da unidade u. Os três componentes vêm só da Parte B:

* **Frequência:** para cada unidade, a regressão da Q11 prevê os ataques dos trimestres 13 a 16 com o perfil atual; somando, λ\_u = ataques esperados em 2026. Total: 1.192 ataques.
* **Materialização:** p̄\_u é a média das probabilidades que a logística da Q13 atribui aos ataques observados da unidade (média geral ponderada 0,414). As mesmas probabilidades dão o peso w\_(u,k) de cada tipo entre as perdas da unidade.
* **Severidade:** Lognormal por tipo, com (μ\_k, σ\_k) = média e desvio de ln(perda) em `perdas.csv`.

**Thinning.** Se os ataques de u chegam como Poisson(λ\_u) e cada um vira perda com probabilidade p̄\_u, independentemente, as perdas são Poisson(λ\_u·p̄\_u). Separando por tipo, N\_(u,k) ~ Poisson(λ\_u·p̄\_u·w\_(u,k)) independentes, e a soma sobre unidades é Poisson(Λ\_k). Resultam 493 perdas esperadas por ano.

| Tipo | μ (ln) | σ (ln) | Mediana | Média | Λ\_k (perdas/ano) |
| :------------- | --------: | --------: | ------------: | ------------: | ----------------: |
| Phishing | 9,951 | 0,978 | R$ 20.973 | R$ 33.844 | 141,7 |
| Força bruta | 9,575 | 0,952 | R$ 14.400 | R$ 22.654 | 80,1 |
| Malware | 10,512 | 0,926 | R$ 36.753 | R$ 56.452 | 81,4 |
| Exploração | 10,969 | 0,984 | R$ 58.062 | R$ 94.194 | 104,9 |
| DDoS | 10,356 | 1,056 | R$ 31.437 | R$ 54.884 | 44,1 |
| Ransomware | 12,123 | 0,912 | R$ 183.990 | R$ 278.978 | 41,0 |

**b) Distribuição da perda anual (100.000 réplicas).**

| Métrica de risco | Cenário atual | Interpretação |
| :--------------------- | ---------------: | :------------------------------------ |
| Perda média anual | R$ 34,93 mi | Expectativa de perda no ano |
| Mediana | R$ 34,75 mi | Valor central |
| Desvio-padrão | R$ 3,36 mi | Variabilidade de um ano para outro |
| VaR 95% | R$ 40,74 mi | Perda só superada em 5% dos anos |
| VaR 99% | R$ 43,50 mi | Perda só superada em 1% dos anos |
| CVaR 95% | R$ 42,49 mi | Perda média nos 5% piores anos |
| P(perda > R$ 30 mi) | 94,0% | Probabilidade de perda relevante |

![Figura 17 — Distribuição simulada da perda anual de 2026 com média, VaR e CVaR (como na Figura 12.6).](/home/claude/aedi/saidas/figuras/q14b_distribuicao_atual.png){width=14cm}

A distribuição é quase simétrica: com cerca de 493 perdas por ano, a soma de muitas Lognormais já se aproxima da Normal (TCL). Mesmo assim, a cauda direita é mais longa que a esquerda.

**c) Convergência.**

| n | Perda média | Erro padrão da média | VaR 95% | EP anterior / EP atual |
| ---------: | --------------: | ----------------: | -------------: | ----------------: |
| 1.000 | R$ 34,867 mi | R$ 107.874 | R$ 40,89 mi | — |
| 4.000 | R$ 34,906 mi | R$ 52.516 | R$ 40,70 mi | 2,05 |
| 16.000 | R$ 34,952 mi | R$ 26.529 | R$ 40,73 mi | 1,98 |
| 64.000 | R$ 34,930 mi | R$ 13.276 | R$ 40,73 mi | 2,00 |
| 100.000 | R$ 34,932 mi | R$ 10.618 | R$ 40,74 mi | 1,25 |

Cada vez que n quadruplica, o erro padrão cai à metade (razões 2,05, 1,98, 2,00; de 64.000 para 100.000 a razão esperada é √(100/64) = 1,25 e a observada é 1,25). **O erro cai na proporção 1/√n**, como na Seção 12.3. Com 100.000 réplicas a média tem erro de R$ 10.618, desprezível frente às incertezas dos modelos.

![Figura 18 — Convergência da perda média e do seu erro padrão.](/home/claude/aedi/saidas/figuras/q14c_convergencia.png){width=12cm}

**d) Cenário com controles (patch 95%, treino 12 h e SOC em todas as unidades).** Os modelos foram realimentados assim:

* **Frequência:** a Q11 prevê 774 ataques/ano (contra 1.192).
* **Materialização e tempo de detecção:** o SOC reduz o tempo, e incorporamos isso reescalando os tempos observados das unidades sem SOC pela razão das médias estimadas (Q7): 4,70 h / 13,89 h = 0,338. A Exponencial é uma família de escala, então multiplicar os tempos por esse fator transforma a distribuição sem SOC na distribuição com SOC. Com esses tempos, soc = 1 e treino = 12, a logística da Q13 dá p̄ = 0,182 (contra 0,414).
* **Severidade:** o tempo médio dos ataques que viram perda cai de 15,9 h para 5,9 h. Cada μ\_k foi deslocado por β\_tempo × Δtempo do tipo, com β\_tempo = 0,0225 da Q10-d, o que reduz a mediana da severidade de cada tipo entre 16% e 24%.

Resultado: 140 perdas esperadas por ano, contra 493.

| Métrica | Atual | Com controles | Redução |
| :--------------------- | -------------: | ---------------: | -------------------: |
| Perda média anual | R$ 34,93 mi | R$ 9,33 mi | R$ 25,60 mi (73%) |
| Mediana | R$ 34,75 mi | R$ 9,18 mi | R$ 25,57 mi (74%) |
| VaR 95% | R$ 40,74 mi | R$ 12,28 mi | R$ 28,46 mi (70%) |
| VaR 99% | R$ 43,50 mi | R$ 13,94 mi | R$ 29,56 mi (68%) |
| CVaR 95% | R$ 42,49 mi | R$ 13,32 mi | R$ 29,17 mi (69%) |
| P(perda > R$ 30 mi) | 94,0% | 0,0% | −94,0 p.p. |

![Figura 19 — Distribuições da perda anual nos dois cenários (como na Figura 12.7).](/home/claude/aedi/saidas/figuras/q14d_comparacao.png){width=14cm}

**e) Decisão.** Redução média de R$ 25,60 mi por ano, a um custo de R$ 8 mi: **ROI = (25,60 − 8)/8 = 220%**. Com números aleatórios comuns (mesmas uniformes e normais nos dois cenários, réplica a réplica), a probabilidade de a perda com controles somada ao custo superar a perda sem controles é **0,00%**: em nenhuma das 100.000 réplicas o pacote deixou a ANDI pior. Mesmo nos 5% de anos menos favoráveis o benefício líquido é de R$ 14,0 mi. O **custo máximo** que ainda se pagaria na média é a própria redução esperada, **R$ 25,6 mi por ano**. O pacote também corta a cauda: VaR 95% −R$ 28,5 mi e CVaR 95% −R$ 29,2 mi.

**f) Sensibilidade.**

| Cenário | Perda média atual | Com controles | Benefício líquido | ROI | Decisão |
| :----------------- | ----------------: | ---------------: | ----------------: | --------: | ----------: |
| base | R$ 34,9 mi | R$ 9,3 mi | R$ 17,6 mi | 220% | investir |
| σ −20% | R$ 29,6 mi | R$ 7,9 mi | R$ 13,7 mi | 171% | investir |
| σ +20% | R$ 42,7 mi | R$ 11,4 mi | R$ 23,3 mi | 292% | investir |
| frequência −10% | R$ 31,4 mi | R$ 8,4 mi | R$ 15,0 mi | 188% | investir |
| frequência +10% | R$ 38,4 mi | R$ 10,3 mi | R$ 20,1 mi | 252% | investir |

![Figura 20 — Gráfico de tornado do benefício líquido do pacote.](/home/claude/aedi/saidas/figuras/q14f_tornado.png){width=11cm}

**A decisão não muda em nenhum caso.** O σ da Lognormal é o parâmetro mais influente (benefício entre R$ 13,7 mi e R$ 23,3 mi), porque a média da Lognormal cresce com e^(σ²/2); a frequência ±10% move o benefício de forma proporcional. Para o pacote deixar de compensar, a redução esperada teria de cair abaixo de R$ 8 mi, cerca de um terço do valor estimado.

**g) Erro de modelo.** Rodando o gerador verdadeiro (Etapas A2–A5 com os parâmetros programados, t = 37 a 48, sem campanha, mesmas 24 unidades) por 10.000 anos:

| Métrica | SMC com modelos estimados | Gerador verdadeiro | Diferença |
| :--------------- | ----------------: | ----------------: | -----------: |
| Média | R$ 34,93 mi | R$ 34,27 mi | 1,9% |
| Mediana | R$ 34,75 mi | R$ 33,95 mi | 2,4% |
| Desvio-padrão | R$ 3,36 mi | R$ 3,81 mi | -11,8% |
| VaR 95% | R$ 40,74 mi | R$ 40,97 mi | -0,6% |
| VaR 99% | R$ 43,50 mi | R$ 44,72 mi | -2,7% |
| CVaR 95% | R$ 42,49 mi | R$ 43,37 mi | -2,0% |
| P(> R$ 30 mi) | 94,0% | 88,1% | 6,7% |

![Figura 21 — Perda anual de 2026: modelo estimado × gerador verdadeiro.](/home/claude/aedi/saidas/figuras/q14g_erro_modelo.png){width=13cm}

A SMC estimada acerta bem o centro (média 1,9%), mas **subestima a dispersão e a cauda extrema**: desvio-padrão -11,8%, VaR 99% -2,7% e CVaR 95% -2,0%. Os acertos no centro vêm de erros que se compensam:

* a frequência é superestimada: 1.192 ataques contra 1.076 verdadeiros (+11%), porque a tendência da Q11 absorveu a campanha;
* a materialização é subestimada: 0,414 contra 0,431;
* a severidade média também é subestimada: R$ 70.842 contra R$ 73.973.

A cauda fica curta por três razões:

1. A Lognormal com σ único por tipo ignora que o tempo de detecção (Exponencial, assimétrica) entra no log da perda; o ln(perda) é levemente assimétrico à direita (Q4-c), e a cauda real é mais pesada.
2. A simulação trata os parâmetros estimados como certos e não propaga a sua incerteza.
3. A severidade e a materialização são tratadas como independentes, quando ambas crescem com o tempo de detecção, o que produz anos ruins mais concentrados.

Para provisionamento, o VaR e o CVaR estimados devem ser lidos como **limites inferiores** e acompanhados de margem.
