# Registro SIMULADO de prompts — material de estudo

**Prova AEDI — Grupo 4 (semente 202604)**

> **Aviso:** este documento é **simulado**. Os prompts abaixo **não foram enviados** a nenhuma ferramenta de IA. Eles foram redigidos pela IA (Claude, claude-opus-5-5, em 25/11/2026) como exemplo de estudo: mostram como cada questão poderia ser pedida a uma IA e como conferir a resposta. **O registro real do uso de IA no trabalho está em `memorial_ia/registro_interacoes.pdf`**, o único que vale como Memorial do Uso de IA.

| Nº | Questão | Prompt simulado | O que a IA entregaria | Como o grupo conferiria |
|--|---|-----------|--------|-------|
| S1 | Q1-a | "Implemente em Python o gerador da Parte A (etapas A1 a A5) com a semente 202604 e marque no código os 4 passos da Seção 12.2." | `src/gerador.py` com as cinco etapas comentadas por passo | Rodar duas vezes e comparar os sha256 das bases |
| S2 | Q1-b | "Escreva F⁻¹(U) da Exponencial e da Triangular, implemente à mão e compare com o numpy." | Fórmulas da transformação inversa e gráfico Q-Q manual × biblioteca | Conferir as fórmulas na Seção 12.5 e o teste KS |
| S3 | Q1-c | "Justifique cada distribuição de entrada pela tabela da Seção 12.4. Por que não usar a Normal na severidade?" | Tabela de justificativas; Normal gera perdas negativas e não tem cauda | Comparar com a Seção 12.4 do livro |
| S4 | Q2 | "Compare médias observadas e teóricas por unidade, a razão variância/média e as frequências dos tipos com o erro σ/√n." | Tabelas de verificação e escores z | Conferir com os parâmetros programados |
| S5 | Q3 | "Classifique as colunas, monte as frequências do tipo e da perda (Sturges) e calcule média, mediana e moda." | Classificação, tabelas de frequência e medidas de posição | Recontar no Excel |
| S6 | Q4 | "Calcule DP, CV e AIQ por tipo, box-plots com outliers por 1,5×AIQ, assimetria/curtose, covariâncias e VaR mensal de 95%." | Tabelas, figuras e VaR histórico (R$ 4,48 mi) | Conferir o percentil 95 na planilha |

| Nº | Questão | Prompt simulado | O que a IA entregaria | Como o grupo conferiria |
|--|---|-----------|--------|-------|
| S7 | Q5 | "Monte a contingência tipo × materializou, aplique Bayes à regra 'alarme se CVSS ≥ 7' e desenhe a árvore." | P(mat. dado ransomware) = 0,643; P(ransomware dado mat.) = 0,081; VPP = 0,626 | Comparar Bayes com a contagem direta |
| S8 | Q6 | "Calcule P(N ≥ 6) pela Poisson, P(tempo > 8 h) pela Exponencial e o Q-Q de ln(perda)." | Probabilidades teóricas × empíricas e Q-Q | Calcular à mão uma das probabilidades |
| S9 | Q7 | "ICs de 95% do tempo de detecção e da proporção materializada, tamanho de amostra para ±2 p.p. e TCL por reamostragem." | ICs, n necessário e histogramas do TCL | Conferir o n pela fórmula do cap. 6 |
| S10 | Q8 | "Teste unilateral do tempo ≤ 4 h, teste da meta de 40% e backtesting do VaR com Kupiec." | t = 4,45; Z = 2,32; contagem de exceções e LR de Kupiec | Recalcular t e Z a partir dos CSVs |
| S11 | Q9–Q10 | "Regrida ln(perda) sobre o tempo, interprete β₁, monte a ANOVA (F = t²), os ICs e o intervalo de previsão em 24 h." | β₁ = 0,0166 (≈1,7% por hora); ANOVA; IC e IP em R$ | Verificar se o IC de β₁ contém 0,02 |
| S12 | Q11 | "Regressão múltipla no painel trimestral, testes, VIF, resíduos, dummies sazonais e teste de sobreajuste com ruído." | Tabela no formato da Seção 10.7 e diagnósticos | Contar quantos ICs contêm os valores verdadeiros |

| Nº | Questão | Prompt simulado | O que a IA entregaria | Como o grupo conferiria |
|--|---|-----------|--------|-------|
| S13 | Q12 | "Médias móveis, suavização, decomposição, ACF, previsão de 2026 e regra dos 3σ." | Figuras, índices sazonais e detecção de abril/2025 | Comparar os índices com os S_m programados |
| S14 | Q13 | "Logística e árvore (profundidade 3) com treino 2023–2024 e teste 2025: métricas, ROC/AUC e limiar de custo mínimo." | Coeficientes, regras, matrizes de confusão e limiar ótimo | Comparar os coeficientes com a Etapa A4 |
| S15 | Q14 | "SMC de 2026 com os modelos estimados: VaR/CVaR, convergência, cenário com controles, ROI, sensibilidade e erro de modelo." | Média R$ 34,9 mi; VaR 95% R$ 40,7 mi; com controles R$ 9,3 mi; ROI 220% | Rodar de novo com n maior e números aleatórios comuns |
| S16 | Q15 | "Redija um parecer de uma página, sem fórmulas, respondendo às três perguntas da diretoria." | Parecer executivo com recomendação e limitações | Conferir cada número do parecer contra a Q14 |

**Para estudar:** em cada linha, a coluna "Como o grupo conferiria" é a parte que a prova avalia. A IA propõe; o grupo verifica contra o livro, os parâmetros do gerador e um recálculo independente.
