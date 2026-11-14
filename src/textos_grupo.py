"""Textos do grupo: leituras das questões para a ANDI (relatório), parecer executivo
(Q15), decisões do memorial e reflexão final."""
from __future__ import annotations

import re

FERRAMENTAS = ("Claude (Anthropic), modelo configurado claude-opus-5-5 (Interações 1 a 12), e Gemini (Google), "
               "interface web (Interação 13)")
AUTORES = "Diego Casagrande, Mateus Martins, Silvio Sznifer, Vinícius Chiconato"
PRAZO = "04/12/2026"

# ------------------------------------------------------------------ relatório
LEITURAS = {
    1: "Para o grupo, a Questão 1 estabelece a fundação metodológica de todo o estudo: como nós mesmos implementamos o modelo gerador a partir da semente 202604, conhecemos os parâmetros populacionais verdadeiros e conseguimos medir, nas etapas seguintes, o grau de precisão e os vieses de cada técnica estatística aplicada. A implementação manual das transformações inversas demonstrou na prática como qualquer distribuição de probabilidade pode ser derivada de uma Uniforme(0,1), e os testes de Kolmogorov-Smirnov (com p-valores entre 0,36 e 0,98) comprovaram que nossas funções equivalem às rotinas nativas da biblioteca. Sob a ótica da gestão de risco da ANDI, a decisão crítica desta etapa é modelar a severidade via distribuição Lognormal: uma abordagem Normal geraria 28,5% de perdas negativas (inexistentes na realidade) e subestimaria severamente a cauda extrema (R$ 452 mil contra R$ 1,29 milhão no percentil 99,9%), levando a agência a um subprovisionamento financeiro perigoso.",
    2: "Concluímos que o modelo gerador opera exatamente conforme especificado: as pequenas divergências entre os valores simulados e os parâmetros programados estão dentro da margem esperada do erro de simulação (σ/√n), o que é corroborado pelo teste qui-quadrado de aderência (p = 0,054) e pela forte correlação entre médias mensais observadas e teóricas (r = 0,92). O achado mais relevante para o grupo foi a superdispersão nas contagens agregadas (razão variância/média de 1,47 no conjunto, contra 1,07 quando ajustada mês a mês por unidade). Isso prova que a distribuição de Poisson não está mal especificada; o fenômeno decorre da forte heterogeneidade estrutural entre as 24 unidades da ANDI e das oscilações temporais (tendência e campanhas). Para a governança da agência, a lição é clara: monitorar indicadores de segurança apenas pela média global da instituição mascara unidades críticas, exigindo acompanhamento individualizado por unidade de negócio.",
    3: "A principal lição gerencial desta etapa é que o impacto de um incidente cotidiano e o impacto que compromete o orçamento anual exigem métricas distintas. Como a distribuição das perdas é fortemente assimétrica à direita (95,2% dos casos concentram-se abaixo de R$ 262 mil, enquanto a cauda chega a R$ 1,44 milhão), a mediana geral de R$ 29.734 retrata fielmente a \"perda típica\" de um incidente comum, sem ser distorcida por eventos extremos. Contudo, para fins de planejamento orçamentário e reserva de contingência, a diretoria precisa olhar para a média (R$ 70.051 no geral, chegando a R$ 264.802 no Ransomware), pois é ela que determina o desembolso total acumulado. Recomendamos, portanto, que os painéis executivos da ANDI reportem sempre a mediana e a média em conjunto para evitar tanto o alarmismo operacional quanto a subestimação financeira.",
    4: "Na leitura do grupo, os valores extremos (outliers) identificados pela regra do box-plot não são anomalias estatísticas a serem descartadas, mas a própria materialização do risco cibernético da ANDI: apenas 6% a 9% dos incidentes respondem por até 49% do prejuízo financeiro de cada categoria (caso do DDoS, que apresentou o maior risco relativo, com CV = 2,27, enquanto o Ransomware concentra o maior impacto absoluto). Excluir esses registros comprometeria diretamente o cálculo de capital de risco. Além disso, a correlação bivariada nula entre cobertura de patches e número de ataques (r = 0,00) demonstrou que análises simples podem ser mascaradas por variáveis de confusão — no caso, unidades com mais serviços expostos tendem a ter maior cobertura de patches (r = 0,30) —, justificando o uso da regressão múltipla na Questão 11. Por fim, a instabilidade do VaR histórico de 36 meses (que cai de R$ 4,48 mi para R$ 4,27 mi ao remover um único mês de pico) confirma que amostras históricas curtas são insuficientes para estimar perdas extremas, motivando a simulação da Parte C.",
    5: "O alerta mais importante que levamos à equipe de segurança da ANDI é a distinção prática entre P(materializou | ransomware) = 64,3% e P(ransomware | materializou) = 8,1%. Embora o Ransomware seja o vetor com maior probabilidade individual de causar prejuízo quando ocorre, sua baixa frequência relativa faz com que ele represente uma fração menor do total de incidentes materializados; uma defesa focada exclusivamente nele deixaria a agência vulnerável à maior parte das ocorrências (como Phishing e Exploração). Quanto à regra de triagem baseada apenas em CVSS ≥ 7, ela apresenta um gargalo operacional severo: acerta 62,6% dos alarmes emitidos, mas deixa passar 67,1% dos ataques que efetivamente geram perda (baixa sensibilidade). Além disso, a árvore de Bayes demonstra que, se a prevalência (a fração de ataques que viram perda) cair pela metade, o valor preditivo positivo despenca para 38,0%, inundando o SOC com falsos positivos. A triagem da ANDI precisa incorporar o tempo de detecção e o contexto operacional, como demonstramos na Questão 13.",
    6: "Optamos por analisar a unidade 23 por representar a mediana de ataques mensais entre as unidades sem SOC (3,33 ataques/mês), refletindo o comportamento de uma unidade típica da agência em vez de um caso atípico. Nas três frentes avaliadas — frequência mensal (Poisson), tempo de resposta (Exponencial) e severidade financeira (Lognormal) —, os modelos teóricos ajustaram-se consistentemente aos dados empíricos. Para a gestão operacional da ANDI, a validação da Poisson permite dimensionar a capacidade de atendimento das equipes locais: em uma unidade padrão sem SOC, há 12,1% de probabilidade de enfrentar seis ou mais ataques em um único mês (próximo aos 13,9% observados), cenário que exige planos de contingência. Já a aderência à Lognormal (confirmada nos gráficos Q-Q com p > 0,15 no teste de Shapiro-Wilk) mostra que perdas milionárias, como um Ransomware de R$ 1,17 milhão (Z = 2,03 na escala logarítmica), não são eventos impossíveis, mas ocorrências naturais dentro da cauda esperada para o volume de incidentes da agência.",
    7: "O principal aprendizado desta etapa para a governança de contratos da ANDI está na discrepância entre os intervalos de confiança globais e os parâmetros nominais do gerador: os ICs de 95% para o tempo médio de detecção (4,39 h a 5,01 h com SOC; 13,27 h a 14,51 h sem SOC) não contêm os valores de 4 h e 12 h porque estes se aplicam estritamente ao horário comercial. Como 35% dos ataques ocorrem fora do expediente e sofrem um acréscimo de 50% no tempo de resposta, qualquer SLA contratual da agência precisa especificar explicitamente se a meta é medida apenas em horário comercial ou em regime 24/7. Adicionalmente, a simulação do Teorema Central do Limite evidenciou que, devido à forte assimetria das perdas (5,03), amostras pequenas (n = 30) ainda geram médias amostrais assimétricas (0,99), exigindo amostras maiores (como os n ≈ 2.341 ataques calculados para auditar a taxa de materialização com margem de ±2 p.p.) para garantir estimativas financeiras confiáveis.",
    8: "Os testes de hipóteses trazem diagnósticos objetivos para três frentes de gestão da ANDI. Primeiro, o fornecedor do SOC cumpre a meta de 4 horas durante o expediente (x̄ = 3,91 h; p = 0,723), mas descumpre o contrato na operação global (x̄ = 4,70 h; p < 0,0001) devido à lentidão nos turnos noturnos e fins de semana. Como o Erro Tipo II (ignorar uma lentidão real do SOC, encarecendo cada perda em ~2% por hora) é muito mais oneroso para a agência do que o Erro Tipo I, recomendamos aditar o contrato para reforçar a cobertura fora do expediente, em vez de substituir o fornecedor. Segundo, a taxa global de materialização de 42,1% viola estatisticamente o teto institucional de 40% (p = 0,0101), reforçando a urgência do pacote de controles da Questão 14. Terceiro, o backtesting de 2025 rejeitou o VaR histórico estático calibrado em 2023–2024 (25 exceções contra 14,4 esperadas; p = 0,0091 no teste de Kupiec): em um cenário de crescimento contínuo de ameaças e campanhas atípicas (como abril/2025), modelos de risco estáticos subestimam a exposição e precisam de recalibração periódica.",
    9: "A principal mensagem estratégica desta análise para a diretoria é que agilidade na resposta reduz diretamente o prejuízo financeiro: cada hora adicional até a detecção eleva o custo esperado do incidente em cerca de 1,68% (quase 49% em um atraso de 24 horas). O R² baixo (0,052) não invalida essa conclusão, pois o efeito do tempo é altamente significativo (t = 8,27; p < 0,0001); ele apenas reflete que a maior parte da variação dos custos decorre da natureza do ataque (que vai de R$ 10 mil na Força Bruta a R$ 150 mil no Ransomware). Além disso, identificamos um fenômeno metodológico importante: como só observamos perdas nos ataques que se materializam, e ataques mais baratos dependem de longos tempos de demora para gerar dano, a amostra de perdas sofre de viés de seleção. Isso atenua o coeficiente estimado na regressão simples (0,0166 contra 0,0225 ao controlar pelo tipo), o que significa que o ganho real de detectar incidentes rapidamente é ainda maior do que o modelo simples aparenta.",
    10: "Os resultados da inferência trazem um alerta essencial para o planejamento financeiro de incidentes na ANDI: embora consigamos estimar com alta precisão o custo típico (mediana) de um ataque detectado em 24 horas — situado entre R$ 35,0 mil e R$ 40,4 mil (com média esperada de R$ 73,6 mil) —, o intervalo de previsão para um único incidente individual é extremamente amplo, variando de R$ 3,9 mil a R$ 366,0 mil (um fator de quase 95 vezes). Isso ocorre porque a incerteza intrínseca de cada ataque individual não desaparece mesmo com amostras grandes, exigindo que a agência mantenha reservas de liquidez para absorver choques isolados. Por fim, a inclusão das variáveis indicadoras (dummies) de tipo de ataque elevou o poder explicativo do modelo (R²) de 5,2% para 43,2% e reduziu a atenuação do efeito do tempo causada pela seleção (β₁ = 0,0225, com IC de 95% que contém o valor programado de 0,02), provando que políticas de mitigação precisam ser segmentadas por vetor de ameaça.",
    11: "A regressão múltipla fornece um mapa quantitativo das alavancas de prevenção à disposição da gestão da ANDI: mantendo os demais fatores constantes, a implantação de um SOC dedicado reduz em média 1,53 ataque por trimestre em cada unidade; cada 10 serviços expostos fechados evitam 5,64 ataques; cada 10 pontos percentuais a mais na cobertura de patches evitam 1,46 ataque; e cada 10 horas anuais de treinamento evitam 3,25 ataques trimestrais. Metodologicamente, o fato de apenas 3 dos 5 intervalos de confiança de 95% conterem os parâmetros verdadeiros revelou duas lições importantes: primeiro, a omissão da campanha atípica de abril/2025 inflou a tendência linear estimada (0,265 contra 0,150 real); segundo, a natureza de contagem dos dados gera heterocedasticidade (padrão de funil nos resíduos, p = 0,016). Ao levarmos essa equação para a simulação da Questão 14, mantivemos essa limitação no radar sabendo que ela projeta um cenário base ligeiramente conservador (com tendência superestimada).",
    12: "A projeção de 1.153 ataques para 2026 (com banda de 95% de ±17 ataques/mês) oferece à ANDI uma referência concreta para escalonar a capacidade de resposta ao longo do ano, reforçando equipes nos meses historicamente mais pressionados, como março, abril e novembro (onde a previsão chega a 114 ataques). No monitoramento contínuo, a regra dos 3σ aplicada aos resíduos dessazonalizados mostrou-se altamente eficaz: detectou o surto anômalo de abril/2025 (165 ataques, resíduo de 8,6σ) sem gerar nenhum falso alarme nos demais 35 meses. Recomendamos que a agência adote essa regra como gatilho automático de alerta operacional, tomando o cuidado metodológico de excluir o mês sob avaliação do cálculo do desvio-padrão e dos índices sazonais para que a própria anomalia não mascare o limite de controle. Como limitação, ressaltamos que três anos de histórico ainda geram margem de erro de cerca de ±0,05 nos fatores sazonais.",
    13: "Para a operação diária do SOC da ANDI, o resultado mais transformador desta questão é a demonstração de que o limiar padrão de classificação (0,50) é financeiramente inadequado quando os custos dos erros são assimétricos. Como deixar passar um ataque real custa em média R$ 29,2 mil contra R$ 3,0 mil de uma investigação improdutiva, calibrar o limiar de decisão para 0,14 reduziu o custo total esperado dos erros em 2025 de R$ 6,57 milhões para R$ 1,89 milhão (uma economia de 71%), elevando a detecção de incidentes críticos (recall) de 54,1% para 97,0% e reduzindo os incidentes não tratados para apenas 14 casos. Recomendamos adotar a regressão logística como motor principal de triagem, tanto pela sua capacidade discriminatória superior (AUC = 0,770 contra 0,723 da árvore) quanto pela leitura direta de seus coeficientes em razões de chances, mantendo a árvore de decisão apenas como guia visual rápido para treinamento de analistas júnior.",
    14: "Na avaliação conclusiva do grupo, o pacote de controles (95% de patches, 12 horas de treinamento e SOC dedicado em todas as 24 unidades) deve ser aprovado com prioridade pela diretoria da ANDI. Ao custo anual de R$ 8,0 milhões, o investimento reduz a perda média esperada de R$ 34,93 milhões para R$ 9,33 milhões, gerando um benefício líquido médio de R$ 17,60 milhões por ano (ROI = 220%) e zerando, nas simulações, a chance de perdas anuais acima de R$ 30 milhões (que cai de 94,0% para 0,0%). Mais importante ainda, o pacote protege a agência contra cenários extremos: o VaR 95% despenca de R$ 40,74 milhões para R$ 12,28 milhões, e em 100% das 100.000 simulações pareadas o investimento se pagou (e permaneceu vantajoso em todos os cenários da análise de sensibilidade). Por fim, o confronto com o gerador verdadeiro revelou que nossa simulação estima bem o centro da distribuição (erro de apenas 1,9%), mas subestima levemente a cauda extrema (CVaR 95% de R$ 42,49 mi contra R$ 43,37 mi reais) por não propagar a incerteza dos parâmetros estimados; assim, recomendamos utilizar os valores de VaR e CVaR como pisos mínimos de provisionamento e recalibrar os modelos trimestralmente.",
}


def inserir_leituras(md: str) -> str:
    """Coloca a leitura do grupo ao fim da seção de cada questão."""
    pend = dict(LEITURAS)
    out, atual = [], None
    for li in md.split("\n"):
        if (li.startswith("## Questão ") or li.startswith("# Parte ")) and atual in pend:
            out += ["**Leitura do grupo para a ANDI.** " + pend.pop(atual), ""]
            atual = None
        m = re.match(r"^## Questão (\d+)", li)
        if m:
            atual = int(m.group(1))
        out.append(li)
    if atual in pend:
        out += ["", "**Leitura do grupo para a ANDI.** " + pend.pop(atual)]
    return "\n".join(out)


# ------------------------------------------------------------------ parecer (Q15)
PARECER = f"""---
title: "Parecer executivo à diretoria da ANDI"
lang: pt-BR
---

**Assunto:** Exposição ao risco cibernético em 2026 e viabilidade do pacote de controles

**De:** Grupo 4 ({AUTORES}) — Análise Estatística de Dados e Informações (PPCA/UnB) · **Data:** {PRAZO}

**Recomendação executiva:** **aprovar integralmente o pacote de controles de R$ 8,0 milhões/ano**, priorizando a implantação imediata de Centros de Operações de Segurança (SOC) dedicados nas 16 unidades hoje descobertas, acompanhada da revisão contratual para cobertura fora do expediente e da calibração dos filtros de triagem de alertas. O investimento gera um **benefício líquido médio de R$ 17,6 milhões por ano (retorno de 220%)** e, nas simulações, praticamente elimina o risco de perdas anuais acima de R$ 30 milhões.

**1. Quanto a ANDI deve esperar perder em 2026 se mantiver o cenário atual?** Caso a estrutura atual de segurança seja mantida, a ANDI deve sofrer cerca de 1.192 ataques ao longo de 2026, dos quais aproximadamente 493 resultarão em prejuízo financeiro efetivo. A **perda média anual esperada é de R$ 34,9 milhões** (com mediana de R$ 34,8 milhões). Como a perda esperada já supera R$ 30 milhões, a agência enfrenta **94% de probabilidade de registrar perdas anuais superiores a R$ 30 milhões**. Em cenários severos, que ocorrem em média uma vez a cada 20 anos, o prejuízo ultrapassa **R$ 40,7 milhões (VaR 95%)**, alcançando uma **perda média de R$ 42,5 milhões nos 5% piores cenários (CVaR 95%)**. Em um ano extremo a cada século, a perda supera **R$ 43,5 milhões (VaR 99%)**. Embora incidentes como *Phishing* gerem maior volume operacional, ataques de *Ransomware* e *Exploração de vulnerabilidades* concentram a maior parcela do impacto financeiro. Essas projeções baseiam-se em 100.000 cenários anuais simulados a partir do histórico de 2023 a 2025 das 24 unidades.

**2. O pacote de controles de R$ 8 milhões por ano compensa financeiramente?** **Sim, com ampla margem de segurança.** Ao elevar a cobertura de *patches* para 95%, ampliar o treinamento anual para 12 horas por colaborador e universalizar o SOC dedicado nas 24 unidades, o número esperado de incidentes com prejuízo cai de 493 para 140 ao ano. Como resultado, a **perda média anual cai de R$ 34,9 milhões para R$ 9,3 milhões**. Essa economia bruta de R$ 25,6 milhões ao ano cobre o investimento de R$ 8,0 milhões e entrega um **benefício líquido médio de R$ 17,6 milhões/ano, equivalente a um retorno sobre o investimento (ROI) de 220%**.

Além de reduzir o custo médio, o pacote comprime drasticamente o risco de cauda: a perda em anos ruins (VaR 95%) recua de **R$ 40,7 milhões para R$ 12,3 milhões**, enquanto a média dos piores cenários (CVaR 95%) cai de **R$ 42,5 milhões para R$ 13,3 milhões**, zerando a probabilidade de perdas anuais acima de R$ 30 milhões. Em nenhuma das 100.000 simulações pareadas o custo do pacote superou a economia gerada; o investimento continuaria vantajoso mesmo que custasse até R$ 25,6 milhões por ano. O principal motor desse resultado é o SOC: ele reduz o número de ataques, corta pela metade a chance de materialização e acelera a detecção, evitando o encarecimento progressivo dos incidentes (cada hora de atraso na resposta eleva o prejuízo em cerca de 2%).

**3. Quão confiáveis são esses números e quais são os limites do modelo?** A decisão de investir é altamente robusta: na análise de sensibilidade, mesmo variando a gravidade das perdas em 20% para mais ou para menos e a frequência de ataques em 10% para mais ou para menos, **o benefício líquido permanece positivo em todos os cenários, oscilando entre R$ 13,7 milhões e R$ 23,3 milhões ao ano**. Ainda assim, a diretoria deve considerar quatro limitações técnicas ao utilizar essas cifras para provisionamento orçamentário:

* **Subestimação das perdas extremas:** o confronto do modelo estimado com o processo gerador real mostra alta precisão na média (diferença de apenas 1,9%), mas revela que a simulação subestima a volatilidade anual em 11,8% e as perdas de cauda (VaR 99% e CVaR 95%) entre 2% e 3%, por tratar os parâmetros estimados como fixos e ignorar correlações na cauda. Assim, os valores de VaR e CVaR devem ser adotados como **pisos mínimos de reserva**, acrescidos de margem prudencial.
* **Base histórica curta e distorção por campanha atípica:** as projeções apoiam-se em apenas 36 meses de dados. O surto coordenado de ataques de abril de 2025 inflou a tendência de crescimento estimada, tornando o cenário base ligeiramente conservador, e três anos constituem uma janela estreita para capturar mudanças estruturais nas táticas dos atacantes.
* **Extrapolação dos efeitos operacionais:** nenhuma unidade da ANDI opera hoje com a combinação simultânea dos três controles nos níveis propostos; logo, o ganho conjunto é uma projeção estatística. Além disso, os dados mostraram que o SOC atual cumpre a meta de detecção em 4 horas apenas em horário comercial, demorando 50% mais fora do expediente; o benefício projetado pressupõe que os novos contratos garantam atendimento pleno em regime integral.
* **Eventos inéditos ("cisnes negros"):** modelos baseados em histórico não capturam falhas tecnológicas sistêmicas sem precedentes ou ataques catastróficos fora do padrão observado nos últimos três anos.

**Próximos passos recomendados:** (1) aprovar o orçamento de R$ 8,0 milhões e iniciar a implantação do SOC pelas 16 unidades descobertas; (2) revisar os contratos de SOC para exigir o tempo de resposta de 4 horas também à noite e aos fins de semana; (3) recalibrar os sistemas de alerta para priorizar o custo esperado do incidente em vez de filtrar apenas pela nota técnica de gravidade (CVSS); e (4) reestimar o modelo trimestralmente, confrontando as perdas reais de 2026 com as faixas projetadas (*backtesting*).
"""

# ------------------------------------------------------------------ memorial
DECISOES = [
    "Aceitamos o roteiro como plano de trabalho e mantivemos a divisão por questões e o cronograma até 04/12. "
    "O protótipo com a semente de teste serviu só para dar ordens de grandeza; nenhum número dele foi usado no relatório.",
    "Aceitamos todas as decisões propostas, porque seguem o enunciado e o livro. As duas escolhas que eram "
    "nossas, o número do grupo e a linguagem Python, foram informadas por nós.",
    "Aceitamos o gerador depois de conferir, etapa por etapa, as fórmulas do código contra o enunciado (λ por "
    "unidade e mês, Triangular do CVSS, Exponencial com fator 1,5 fora do expediente, logística e Lognormal). "
    "Mantivemos as inversas próprias da Exponencial e da Triangular, pedidas na Q1-b, em vez de usar só as funções do numpy.",
    "Usamos a planilha como apoio para conferir a Parte A. Ela não substitui o resultados.xlsx gerado pelo "
    "código, que é o arquivo entregue.",
    "Aceitamos a explicação e a usamos na Q1 e na preparação para a arguição: a semente só reproduz as bases "
    "se a ordem dos sorteios for mantida.",
    "Usamos o plano em quatro marcos como guia interno de controle de progresso e, na reta final, abrimos issues no "
    "GitHub (#1 a #3) para acompanhar as verificações e a revisão dos textos.",
    "O erro foi nosso, não da IA: informamos o grupo 3 no início. Pedimos a correção, regeneramos tudo com a "
    "semente 202604 e separamos os arquivos antigos numa pasta própria, para não entregá-los por engano.",
    "Aceitamos as análises depois de recalcular os resultados principais (ver Verificação) e de ler cada "
    "interpretação. Mantivemos as três escolhas de modelagem listadas em Erros da IA: o VaR da Q8-d com todas "
    "as unidades-mês dá 576 observações de treino, contra 24 por unidade; os índices sazonais da Q12 aparecem "
    "com e sem abril/2025, o que deixa a escolha transparente; e o efeito do SOC na Q14-d usa apenas modelos "
    "estimados na Parte B, como pede o enunciado. As interpretações foram revistas e reescritas pelo grupo (interações 11 e 12).",
    "Concedemos acesso apenas a este repositório e conferimos no GitHub os commits enviados.",
    "Aceitamos o checklist. Os itens que só o grupo pode fazer (nomes, interpretações, decisões deste memorial, "
    "reflexão final e anexo da conversa) ficaram conosco.",
    "Utilizamos as sugestões como estrutura inicial e submetemos os textos a uma revisão crítica e ampliação "
    "(Interação 12) para aprofundar a conexão com o contexto gerencial da ANDI antes de remover os destaques amarelos.",
    "Aceitamos as cinco correções de coerência apontadas na conferência (parecer: perdas catastróficas, causa dos 94% e "
    "superfície de ataque; Q5: prevalência; Q10: viés de seleção). Na Q13, retiramos \"precisão na calibração de "
    "probabilidades\", que não foi testada; na Q14, trocamos \"eliminando por completo\" por \"nas simulações\". "
    "Registro na issue #3 do GitHub.",
    "Acatamos as sugestões de revisão textual e os ajustes de conformidade: consolidamos os textos revisados para "
    "incorporação no código (Interação 12), retiramos os registros sem IA da tabela do memorial (movendo a descrição "
    "da revisão humana para a Reflexão final), sincronizamos registro.xlsx com este documento e formalizamos esta "
    "etapa de auditoria com a segunda ferramenta de IA.",
]

VERIF_6 = ("Conferência da cobertura de todas as 15 questões e dos 5 entregáveis obrigatórios do enunciado nas "
           "etapas do plano.")

VERIF_8 = ("Verificação independente feita pela IA a partir das bases, sem o código do projeto: t da Q8-a, z da "
           "Q8-b, VaR da Q4-e, F = t² da Q10, LR de Kupiec da Q8-d, valor preditivo da Q5-c e ROI da Q14-e "
           "coincidiram; duas execuções com resultados idênticos. Conferência pelo grupo (14/11/2026, execução local): "
           "recalculamos na planilha `saidas/resultados.xlsx` o teste t da Q8-a, (4,70 − 4)/(4,73/√904) ≈ 4,45, o teste Z "
           "da Q8-b, (0,4209 − 0,40)/√(0,24/2965) ≈ 2,32, e o ROI da Q14-e, (25,60 − 8)/8 = 220%; em outro computador, "
           "clonamos o repositório, instalamos as dependências (`pip install -r requirements.txt`) e executamos "
           "`python main.py --grupo 4 --sem-relatorio`, e o `dados/sha256.json` gerado coincidiu com o do repositório "
           "(`git diff` sem mudanças).")

INTERACAO_11 = dict(
    data="13/11/2026", questao="Q1–Q14 (interpretações) e memorial",
    exig="Ter uma primeira versão, para revisar, das partes do relatório e do memorial que cabem ao grupo.",
    prompt="\"faça nos docs destacados, menos a parte dos nomes, sugestões de tudo o que temos que fazer como se "
           "fosse o grupo... ao fim também faça uma lista detalhada aqui de quais passos devemos executar passo a passo\"",
    resp="Sugestões destacadas em amarelo: um parágrafo \"Leitura do grupo para a ANDI\" ao fim de cada questão "
         "do relatório, o campo Decisão do grupo de cada interação e a reflexão final deste memorial; lista de passos "
         "para a revisão (commit ee86338).",
    verif="Leitura crítica de cada parágrafo sugerido, conferindo todos os valores numéricos, percentuais e "
          "p-valores contra as tabelas geradas em `saidas/tabelas/` e o texto técnico de cada questão.",
)

INTERACAO_12 = dict(
    data="14/11/2026", questao="Q1–Q15 e memorial (revisão crítica e ampliação)",
    exig="Incorporar aos documentos os textos revisados e ampliados pelo grupo (leituras das Q1–Q14 e novo parecer "
         "executivo), conferindo a coerência dos números com os resultados; ajustar prazo interno, autoria, "
         "formatação e campos pendentes do memorial.",
    prompt="Pedido em nove itens, enviado com os anexos TextosDoGrupo.docx (leituras revisadas) e "
           "relatorio_tecnico.docx (novo parecer); texto integral no histórico exportado da conversa, em anexo.",
    resp="Textos do grupo incorporados ao relatório e ao parecer, com correções pontuais de coerência; parágrafos "
         "justificados; prazo interno de 04/12 e autoria com os quatro integrantes; campos das interações 6, 8 e 11 "
         "preenchidos; destaques amarelos removidos.",
    verif="A IA conferiu cada número dos textos do grupo contra `saidas/resultados.json` e `saidas/tabelas/` e apontou "
          "as incoerências encontradas antes da incorporação.",
)

INTERACAO_13 = dict(
    ferramenta="Gemini (Google), interface web (gemini.google.com)",
    data="14/11/2026", questao="Q1–Q15 e entregáveis finais (auditoria e revisão cruzada)",
    exig="Realizar auditoria independente de todo o conjunto de entregáveis (relatório técnico, parecer executivo, "
         "memorial de uso de IA e planilha de registro) frente às regras do enunciado, além de apoiar a revisão "
         "redacional das interpretações gerenciais e do parecer executivo.",
    prompt="Envio sequencial dos arquivos (AEDI_Enunciado_Prova.pdf, relatorio_tecnico.pdf, parecer_executivo.pdf, "
           "registro_interacoes.pdf e registro.xlsx) solicitando revisão crítica dos textos das Questões 1 a 15, revisão "
           "do parecer executivo para a diretoria da ANDI e auditoria geral de conformidade dos entregáveis.",
    resp="Revisão redacional das interpretações gerenciais, estruturação do parecer executivo em 1 página, diagnóstico "
         "de conformidade com o enunciado (sincronização da planilha registro.xlsx e inclusão deste registro) e "
         "apontamento de falhas de renderização de símbolos matemáticos (letras gregas) no PDF.",
    verif="Conferência de cada apontamento de auditoria e de cada métrica revisada contra o enunciado da prova, a "
          "planilha `saidas/resultados.xlsx`, as tabelas em `saidas/tabelas/` e os limites de extensão (27 páginas no "
          "relatório técnico contra o teto de 30, e 1 página exata no parecer executivo).",
    erros="Durante a inspeção da planilha anexada, a IA inicialmente tentou ler o arquivo pelo nome de exibição em vez "
          "do nome interno no ambiente, corrigindo o caminho de leitura na sequência; não houve erros nas verificações "
          "de conteúdo ou conformidade.",
)

REFLEXAO = """**Em que a IA ajudou.** As ferramentas de IA aceleraram significativamente a estruturação do plano de trabalho a partir do enunciado, a implementação modular do gerador de dados e das rotinas estatísticas em Python, bem como a geração automatizada de tabelas, gráficos e documentos. Também foram úteis na etapa de auditoria cruzada: a IA recalculou métricas-chave diretamente a partir das bases (independentemente dos scripts principais) para confirmar a consistência dos resultados e auxiliou na revisão crítica da clareza executiva das interpretações para a diretoria da ANDI. Essa automação permitiu que o grupo concentrasse esforços na análise estatística, na comparação entre estimativas e parâmetros verdadeiros e na fundamentação das recomendações de negócio.

**Em que atrapalhou ou errou.** Identificamos falhas pontuais que exigiriam correção manual caso não houvesse revisão rigorosa: na geração inicial das bases, o arredondamento para 6 algarismos significativos distorcia somatórios elevados (`perda_total`); houve problemas de formatação em tabelas e listas do relatório; e uma formulação inicial do parecer executivo confundia a subestimação do desvio-padrão com a subestimação do VaR e do CVaR. Além disso, a IA tomou decisões de modelagem em pontos abertos do enunciado (como o cálculo do VaR agrupado na Q8-d, o tratamento de abril/2025 nos índices sazonais da Q12 e a parametrização do efeito do SOC na Q14-d) que precisaram ser tecnicamente avaliadas e validadas pelo grupo. O maior risco metodológico foi a velocidade de geração de código e texto, que poderia induzir à entrega sem domínio pleno do conteúdo — risco mitigado pela leitura, conferência numérica e reescrita ativa de todas as interpretações.

**O que consideramos exclusivamente nosso.** São integralmente do grupo as decisões de projeto (uso da semente do grupo, 202604, conforme a regra do enunciado, adoção da pilha em Python e validação das premissas de modelagem nas Questões 8, 12 e 14), a auditoria independente dos códigos e fórmulas contra o enunciado, os recálculos de verificação realizados na planilha e em ambiente separado, a revisão humana do relatório e de todas as respostas, com leitura cruzada entre os integrantes, conferência dos números contra `saidas/resultados.xlsx` e validação final da versão de entrega entre 20 e 29/11/2026, a redação final das interpretações gerenciais e do parecer executivo, bem como a responsabilidade técnica e a defesa do estudo na arguição."""
