"""Sugestões de redação para as partes que cabem ao grupo (interpretações, decisões do
memorial e reflexão final). Saem destacadas em amarelo nos documentos; com
`python main.py --final` saem sem destaque, como texto definitivo.

Os trechos foram redigidos com IA (interação 11 do memorial) e servem de rascunho:
o grupo deve ler, conferir, reescrever o que quiser e só então gerar a versão final."""
from __future__ import annotations

import re

from util import fmt

FINAL = False  # main.py --final liga este indicador

LEGENDA = ("**Trechos destacados em amarelo:** sugestões de redação para as partes que cabem ao grupo. "
           "Revisar, reescrever com as palavras do grupo e gerar a versão final com `python main.py --final`, "
           "que remove o destaque.")


# ------------------------------------------------------------------ marcação
def M(txt: str) -> str:
    """Destaca um trecho na mesma linha (pandoc: [texto]{.mark} vira realce amarelo no docx)."""
    return txt if FINAL else f"[{txt}]{{.mark}}"


def S(bloco: str) -> str:
    """Destaca cada parágrafo e cada item de lista de um bloco de markdown."""
    if FINAL:
        return bloco
    out = []
    for li in bloco.split("\n"):
        m = re.match(r"^(\s*(?:\* |\d+\. ))(.*)$", li)
        if not li.strip() or li.startswith("#"):
            out.append(li)
        elif m:
            out.append(m.group(1) + M(m.group(2)))
        else:
            out.append(M(li))
    return "\n".join(out)


def _f(x, d=2):
    return fmt(float(x), d).replace("-", "−")


def _pct(x, d=1):
    return fmt(100 * float(x), d) + "%"


def _mi(x, d=1):
    return "R$ " + fmt(float(x) / 1e6, d) + " mi"


def _rs(x):
    return "R$ " + fmt(float(x), 0)


def _coef(R, termo):
    return next(r["coeficiente"] for r in R["q11"]["a"] if r["termo"] == termo)


# ------------------------------------------------------------------ relatório
def leituras(R: dict) -> dict[int, str]:
    """Um parágrafo por questão, na voz do grupo, com a leitura para a ANDI."""
    q5, q6, q7, q8, q9, q10 = (R[k] for k in ["q05", "q06", "q07", "q08", "q09", "q10"])
    q12, q13, q14 = R["q12"], R["q13"], R["q14"]
    L = {
        1: "Para nós, a Questão 1 é a base de todo o resto: como fomos nós que programamos o gerador, "
           "conhecemos os parâmetros verdadeiros e podemos medir, nas questões seguintes, quanto cada método "
           "estatístico acerta. Implementar as inversas à mão mostrou que qualquer distribuição pode ser obtida "
           "a partir de uma uniforme, e o teste KS confirmou que a nossa implementação equivale à do numpy. "
           "Para a ANDI, a decisão mais importante desta parte é usar a Lognormal para a severidade: uma Normal "
           "produziria perdas negativas e cortaria justamente a cauda que define o risco.",
        2: "Concluímos que o gerador faz o que foi programado: as diferenças entre observado e programado têm "
           "o tamanho do erro de simulação esperado. O que mais nos chamou atenção foi a superdispersão das "
           "contagens agregadas. Ela não indica que a Poisson está errada, e sim que as unidades da ANDI são "
           "diferentes entre si. Para a gestão, isso significa que a frequência de ataques deve ser "
           "acompanhada por unidade, e não pela média da agência.",
        3: "Para a diretoria, a lição desta questão é que a perda típica de um incidente e a perda que pesa no "
           "orçamento são coisas diferentes. A mediana descreve o incidente comum; o orçamento depende da média, "
           "puxada por poucos incidentes caros. Por isso recomendamos que os relatórios de risco da ANDI "
           "apresentem sempre as duas medidas juntas.",
        4: "Na nossa leitura, os outliers são o próprio risco da ANDI: poucos incidentes respondem por uma parte "
           "grande da perda de cada tipo, e retirá-los faria a agência provisionar menos do que precisa. A "
           "correlação nula entre patch e ataques mostrou, com os nossos dados, que a correlação simples pode "
           "esconder um efeito real, o que motivou a regressão múltipla da Q11. E o VaR histórico de 36 meses "
           f"caiu de {_mi(R['q04']['var95_mensal'], 2)} para {_mi(R['q04']['var95_sem_maior'], 2)} ao retirar um "
           "único mês: por isso não o usamos como base de decisão e estimamos a cauda por simulação na Parte C.",
        5: "O resultado que levaríamos à equipe de segurança é a diferença entre P(materializou | ransomware) e "
           "P(ransomware | materializou). O ransomware é o ataque com maior chance de virar perda, mas é uma "
           "fração pequena das perdas; uma estratégia voltada só para ele deixaria a maior parte da perda "
           f"descoberta. Sobre a triagem, a regra do CVSS ≥ 7 acerta {_pct(q5['vpp_bayes'], 0)} dos alarmes, mas "
           f"deixa passar {_pct(1 - q5['sens'], 0)} das perdas, e com ataques mais raros o mesmo alarme passaria a "
           f"acertar só {_pct(q5['vpp_prev_metade'], 0)}. Uma triagem melhor precisa olhar também o tempo de "
           "detecção, como mostra a Q13.",
        6: f"Escolhemos a unidade {q6['a']['unidade']} por ser a de média mensal mediana entre as unidades sem SOC: "
           "queríamos uma unidade típica, e não um caso extremo. Nas três verificações, as distribuições escolhidas "
           "no gerador se sustentaram nos dados. Para a ANDI, isso permite planejar a capacidade de resposta com a "
           f"Poisson: numa unidade como esta, a chance de seis ou mais ataques num mês é de {_pct(q6['a']['p_teorica'], 0)}, "
           "perto do que se observou.",
        7: "O que mais aprendemos aqui foi por que os intervalos não contêm 4 h e 12 h: o θ programado vale só "
           "para o expediente, e os ataques fora do expediente demoram 50% mais. Para a ANDI, qualquer meta de "
           "tempo de detecção precisa dizer se vale para o expediente ou para as 24 horas. Para uma auditoria, "
           f"cerca de {fmt(q7['b']['n_para_2pp'], 0)} ataques bastariam para estimar a taxa de materialização com "
           "margem de 2 pontos percentuais.",
        8: "Os dois testes apontam problemas de natureza diferente. O SOC cumpre as 4 h no expediente, mas não "
           "fora dele: na nossa visão, a renegociação do contrato deveria tratar da cobertura noturna e de fins de "
           f"semana, e não trocar o fornecedor. A meta de 40% de materialização não está sendo cumprida ({_pct(q8['b']['p_hat'], 1)}), "
           "o que reforça o pacote de controles avaliado na Q14. E o backtesting nos convenceu de que um VaR "
           "estático falha quando o risco cresce: o modelo de risco da agência precisa ser reestimado com frequência.",
        9: "A conclusão que levamos à diretoria é que tempo é dinheiro: cada hora a mais até a detecção encarece a "
           f"perda em cerca de {_f(q9['pct_por_hora'], 1)}%. O R² baixo não enfraquece essa conclusão, porque o "
           "efeito é estimado com precisão; ele mostra apenas que o tempo não é o único fator. Também aprendemos "
           "que olhar só para os ataques que viraram perda distorce a análise, porque eles não são uma amostra "
           "aleatória de todos os ataques.",
        10: "Para orçar um incidente individual, o que importa é o intervalo de previsão, e ele é muito largo: um "
            f"ataque detectado em 24 h pode custar de {_rs(q10['c_reais']['obs_ci_lower'])} a "
            f"{_rs(q10['c_reais']['obs_ci_upper'])}. Já a perda típica desse ataque é conhecida com boa precisão. "
            "Incluir o tipo de ataque aproximou o efeito do tempo do valor que programamos; para a ANDI, avaliar o "
            "risco sem considerar o tipo de ataque leva a conclusões enviesadas.",
        11: "Do ponto de vista da gestão, a regressão mostra onde agir: um SOC dedicado retira cerca de "
            f"{_f(-_coef(R, 'soc'), 1)} ataques por trimestre em cada unidade, e cada serviço exposto a menos retira "
            f"{_f(_coef(R, 'servicos'), 2)}. O fato de só {R['q11']['n_contem']} dos 5 intervalos conterem o valor "
            "verdadeiro nos ensinou que um modelo pode acertar os sinais e ainda errar na incerteza, quando falta "
            "uma variável (a campanha) ou a variância dos erros não é constante. Por isso usamos a Q11 na Q14 "
            "sabendo que ela superestima a tendência.",
        12: f"A previsão de cerca de {fmt(q12['total_2026'], 0)} ataques em 2026 dá à ANDI uma base para "
            "dimensionar a equipe de resposta mês a mês. A regra dos 3σ encontrou a campanha de abril/2025 sem "
            "falsos alarmes, e sugerimos adotá-la como monitoramento mensal, calculando o σ sem o mês testado. A "
            "principal limitação é a série curta: com três anos, a sazonalidade aparece, mas é medida com pouca precisão.",
        13: "Para a operação, a lição é que o limiar de 0,5 não é neutro: como deixar passar uma perda custa muito "
            "mais do que investigar um alarme falso, o limiar de custo mínimo reduziu o custo dos erros de "
            f"{_mi(q13['e']['custo_teste_05'], 2)} para {_mi(q13['e']['custo_teste_otimo'], 2)} em 2025. "
            "Preferimos a logística à árvore pela AUC maior e porque seus coeficientes têm leitura direta; a "
            "árvore, porém, é útil para explicar a triagem a quem não é da área.",
        14: "Na nossa avaliação, o pacote de controles deve ser aprovado: reduz a perda esperada em "
            f"{_mi(q14['e']['reducao_media'])} por ano, com ROI de {_pct(q14['e']['roi'], 0)}, e em nenhuma das "
            "réplicas deixou a ANDI pior. A comparação com o gerador verdadeiro mostrou que o modelo acerta o "
            "centro, mas subestima a cauda; por isso recomendamos tratar VaR e CVaR como pisos e revisar o "
            "modelo a cada trimestre, com os dados novos.",
    }
    return {k: S("**Leitura do grupo para a ANDI.** " + v) for k, v in L.items()}


def inserir_leituras(md: str, R: dict) -> str:
    """Coloca a leitura de cada questão ao fim da sua seção e a legenda depois dos integrantes."""
    L = leituras(R)
    out, atual = [], None
    for li in md.split("\n"):
        if (li.startswith("## Questão ") or li.startswith("# Parte ")) and atual in L:
            out += [L.pop(atual), ""]
            atual = None
        m = re.match(r"^## Questão (\d+)", li)
        if m:
            atual = int(m.group(1))
        out.append(li)
        if li.startswith("**Integrantes:**") and not FINAL:
            out += ["", S(LEGENDA)]
    if atual in L:
        out += ["", L.pop(atual)]
    return "\n".join(out)


# ------------------------------------------------------------------ memorial
DECISOES = [
    "Aceitamos o roteiro como plano de trabalho e mantivemos a divisão por questões e o cronograma até 09/12. "
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
    "Usamos o plano como referência de organização (ajustar: dizer se as issues foram criadas no GitHub).",
    "O erro foi nosso, não da IA: informamos o grupo 3 no início. Pedimos a correção, regeneramos tudo com a "
    "semente 202604 e separamos os arquivos antigos numa pasta própria, para não entregá-los por engano.",
    "Aceitamos as análises depois de recalcular os resultados principais (ver Verificação) e de ler cada "
    "interpretação. Mantivemos as três escolhas de modelagem listadas em Erros da IA: o VaR da Q8-d com todas "
    "as unidades-mês dá 576 observações de treino, contra 24 por unidade; os índices sazonais da Q12 aparecem "
    "com e sem abril/2025, o que deixa a escolha transparente; e o efeito do SOC na Q14-d usa apenas modelos "
    "estimados na Parte B, como pede o enunciado. As interpretações foram revistas e reescritas pelo grupo (interação 11).",
    "Concedemos acesso apenas a este repositório e conferimos no GitHub os commits enviados.",
    "Aceitamos o checklist. Os itens que só o grupo pode fazer (nomes, interpretações, decisões deste memorial, "
    "reflexão final e anexo da conversa) ficaram conosco.",
    "Usamos as sugestões como rascunho: cada trecho foi lido, discutido e aceito ou reescrito pelo grupo, e o "
    "destaque só foi retirado depois disso (ajustar: dizer quais trechos foram reescritos).",
]

CONFERENCIA_GRUPO = ("o grupo recalculou na planilha resultados.xlsx o t da Q8-a, o Z da Q8-b e o ROI da Q14-e, e "
                     "rodou main.py em outro computador, obtendo os mesmos hashes de dados/sha256.json "
                     "(ajustar ao que foi feito).")

INTERACAO_11 = dict(
    data="13/11/2026", questao="Q1–Q14 (interpretações) e memorial",
    exig="Ter uma primeira versão, para revisar, das partes do relatório e do memorial que cabem ao grupo.",
    prompt="\"faça nos docs destacados, menos a parte dos nomes, sugestões de tudo o que temos que fazer como se "
           "fosse o grupo... ao fim também faça uma lista detalhada aqui de quais passos devemos executar passo a passo\"",
    resp="Sugestões destacadas em amarelo: um parágrafo \"Leitura do grupo para a ANDI\" ao fim de cada questão "
         "do relatório, o campo Decisão do grupo de cada interação e a reflexão final deste memorial; lista de passos "
         "para a revisão. Anexo: src/sugestoes.py.",
    verif="Leitura de cada sugestão pelo grupo, conferindo os números contra o relatório e as tabelas (ajustar).",
)

REFLEXAO = """**Em que a IA ajudou.** A IA nos ajudou a transformar um enunciado longo num plano de trabalho, a implementar o gerador e as análises em Python com rapidez e a montar os documentos. Foi útil também na verificação: recalculou os resultados principais a partir das bases, sem usar o código do projeto, e conferiu que duas execuções produziam os mesmos dados. Isso nos deixou mais tempo para o que a prova pontua, que é entender os resultados e compará-los com os parâmetros que programamos.

**Em que atrapalhou ou errou.** A IA cometeu erros pontuais, que só apareceram porque conferimos: um formato numérico que arredondaria os totais das bases, tabelas e listas mal formatadas no relatório e uma frase do parecer que misturava a subestimação do desvio-padrão com a do VaR e do CVaR. Ela também tomou escolhas de modelagem que não estavam fechadas no enunciado (o VaR da Q8-d, os índices sazonais da Q12, o efeito do SOC na Q14-d), que tivemos de entender e validar. O maior risco, porém, foi a velocidade: a IA produziu em horas um volume de código e texto que levaríamos semanas para fazer, e seria fácil entregar sem entender. Por isso cada interpretação foi lida e reescrita pelo grupo, e cada número citado no parecer foi conferido.

**O que consideramos exclusivamente nosso.** As decisões: o número do grupo e a linguagem, aceitar ou não cada proposta, as escolhas de modelagem que mantivemos e as conclusões levadas à diretoria. Também a verificação dos resultados contra os parâmetros do gerador, a forma final das interpretações e do parecer e a defesa do trabalho na arguição. (Ajustar este parágrafo ao que o grupo de fato fez.)"""


def reflexao() -> str:
    return S(REFLEXAO)
