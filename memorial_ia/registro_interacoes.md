---
title: "Memorial do Uso de IA — Grupo 4"
author: "Diego Casagrande, Mateus Martins, Silvio Sznifer, Vinícius Chiconato"
lang: pt-BR
---

O grupo usou ferramenta de IA. Este memorial registra, para cada interação relevante, os nove campos pedidos no enunciado, e também as revisões feitas pelo grupo (interações 13 a 15), que não usaram IA. A mesma informação está em planilha (`memorial_ia/registro.xlsx`). O código gerado está no repositório, identificado pelo commit indicado em cada interação, e o histórico exportado da conversa está anexado em `memorial_ia/anexos/`.

**Ferramenta usada nas interações com IA:** Claude (Anthropic), modelo configurado claude-opus-5-5, pelo app claude.ai (sessão de trabalho com execução de código, conectores do Google Drive e de documentos).

## Registro das interações

### Interação 1 — Q1–Q15 (planejamento)

* **Ferramenta:** Claude (Anthropic), modelo configurado claude-opus-5-5, pelo app claude.ai (sessão de trabalho com execução de código, conectores do Google Drive e de documentos)
* **Data e responsável:** 12/11/2026 · Diego Casagrande, Mateus Martins, Silvio Sznifer, Vinícius Chiconato
* **Questão atendida:** Q1–Q15 (planejamento)
* **Exigência feita à IA:** Entender o que a prova pede e organizar a resolução antes de começar.
* **Prompt:** [anexo: AEDI\_Enunciado\_Prova.pdf] "do mesmo professor que é autor do livro temos que fazer essa prova passo a passo e gerar os itens integraveis conforme escrito no documento anexo aqui avalie como pode ser realizado esse trabalho, escreva o roteiro passo a passo para resolução"
* **Resposta obtida:** Roteiro em documento compartilhado: avaliação e pontuação, estrutura do repositório, implementação da Parte A, método e armadilhas de cada questão, memorial, cronograma até 04/12 e ambiguidades do enunciado. Para dar ordens de grandeza, rodou um protótipo do gerador com semente de teste (202699).
* **Verificação:** Conferência das regras e da pontuação contra o enunciado.
* **Decisão do grupo:** Aceitamos o roteiro como plano de trabalho e mantivemos a divisão por questões e o cronograma até 04/12. O protótipo com a semente de teste serviu só para dar ordens de grandeza; nenhum número dele foi usado no relatório.
* **Erros da IA:** Erro de digitação no roteiro ("A tempo médio"), corrigido na mesma sessão.

### Interação 2 — Decisões de implementação

* **Ferramenta:** Claude (Anthropic), modelo configurado claude-opus-5-5, pelo app claude.ai (sessão de trabalho com execução de código, conectores do Google Drive e de documentos)
* **Data e responsável:** 12/11/2026 · Diego Casagrande, Mateus Martins, Silvio Sznifer, Vinícius Chiconato
* **Questão atendida:** Decisões de implementação
* **Exigência feita à IA:** Fechar os pontos em aberto do enunciado.
* **Prompt:** "pode ser tudo como está na proposta" → "falta o que"
* **Resposta obtida:** Registro das decisões no roteiro: calendário real (fev/2024 com 29 dias), trimestre = q(t) de 1 a 12, coluna p\_programado, planilha gerada pelo código, VaR da Q8-d com todas as unidades-mês, p̄ por unidade na Q14.
* **Verificação:** O número do grupo e o uso de Python foram informados pelo grupo na tabela do roteiro.
* **Decisão do grupo:** Aceitamos todas as decisões propostas, porque seguem o enunciado e o livro. As duas escolhas que eram nossas, o número do grupo e a linguagem Python, foram informadas por nós.
* **Erros da IA:** Nenhum identificado até aqui.

### Interação 3 — Q1-a, Q1-b

* **Ferramenta:** Claude (Anthropic), modelo configurado claude-opus-5-5, pelo app claude.ai (sessão de trabalho com execução de código, conectores do Google Drive e de documentos)
* **Data e responsável:** 12/11/2026 · Diego Casagrande, Mateus Martins, Silvio Sznifer, Vinícius Chiconato
* **Questão atendida:** Q1-a, Q1-b
* **Exigência feita à IA:** Implementar o gerador (Parte A) e as bases num repositório.
* **Prompt:** "use esse respositório para o código https://github.com/diegocasagrande/aedi" → "salve os arquivos nessa pasta https://drive.google.com/drive/folders/1fhICSMGAVKpyEv8afX6zrzEAQgXnIySQ"
* **Resposta obtida:** Anexos: src/gerador.py, src/inversa.py, main.py, README.md (commit 2d63be9). Bases e hashes sha256. Arquivos salvos na pasta PROVA do Drive. O envio ao GitHub falhou por falta de permissão; o commit foi entregue em arquivo bundle.
* **Verificação:** Duas execuções com hashes idênticos; contagens, taxa de materialização e tempos médios comparados com os valores programados; teste KS das inversas contra o numpy. Conferência pelo grupo (14/11/2026): fórmulas de `src/gerador.py` conferidas contra o enunciado: λ por unidade e mês, CVSS Triangular por tipo, tempo de detecção Exponencial com fator 1,5 fora do expediente, logística da materialização e Lognormal da severidade.
* **Decisão do grupo:** Aceitamos o gerador depois de conferir, etapa por etapa, as fórmulas do código contra o enunciado (λ por unidade e mês, Triangular do CVSS, Exponencial com fator 1,5 fora do expediente, logística e Lognormal). Mantivemos as inversas próprias da Exponencial e da Triangular, pedidas na Q1-b, em vez de usar só as funções do numpy.
* **Erros da IA:** A exportação inicial das bases usava formato numérico com 6 algarismos significativos, o que arredondaria totais grandes (perda\_total); percebido e corrigido antes do commit.

### Interação 4 — Q1, Q2-c

* **Ferramenta:** Claude (Anthropic), modelo configurado claude-opus-5-5, pelo app claude.ai (sessão de trabalho com execução de código, conectores do Google Drive e de documentos)
* **Data e responsável:** 12/11/2026 · Diego Casagrande, Mateus Martins, Silvio Sznifer, Vinícius Chiconato
* **Questão atendida:** Q1, Q2-c
* **Exigência feita à IA:** Ter os números da Parte A numa planilha.
* **Prompt:** "Crie uma planilha a partir da sua última resposta."
* **Resposta obtida:** Planilha compartilhada com conferência estimado × programado, tipos de ataque com σ/√n, inversas, lista de arquivos e pendências.
* **Verificação:** Fórmulas da planilha lidas de volta e conferidas; qui-quadrado dos tipos recalculado.
* **Decisão do grupo:** Usamos a planilha como apoio para conferir a Parte A. Ela não substitui o resultados.xlsx gerado pelo código, que é o arquivo entregue.
* **Erros da IA:** Nenhum identificado até aqui.

### Interação 5 — Q1

* **Ferramenta:** Claude (Anthropic), modelo configurado claude-opus-5-5, pelo app claude.ai (sessão de trabalho com execução de código, conectores do Google Drive e de documentos)
* **Data e responsável:** 13/11/2026 · Diego Casagrande, Mateus Martins, Silvio Sznifer, Vinícius Chiconato
* **Questão atendida:** Q1
* **Exigência feita à IA:** Entender a semente do gerador.
* **Prompt:** "Confere como ficou a seed, me explica porque?"
* **Resposta obtida:** Explicação: semente = 202600 + nº do grupo; gerador pseudoaleatório (PCG64); reprodutibilidade; bases diferentes por grupo; importância da ordem dos sorteios.
* **Verificação:** Conferido contra o enunciado e por execução (mesmos três primeiros sorteios com a mesma semente).
* **Decisão do grupo:** Aceitamos a explicação e a usamos na Q1 e na preparação para a arguição: a semente só reproduz as bases se a ordem dos sorteios for mantida.
* **Erros da IA:** Nenhum identificado até aqui.

### Interação 6 — Organização do trabalho

* **Ferramenta:** Claude (Anthropic), modelo configurado claude-opus-5-5, pelo app claude.ai (sessão de trabalho com execução de código, conectores do Google Drive e de documentos)
* **Data e responsável:** 13/11/2026 · Diego Casagrande, Mateus Martins, Silvio Sznifer, Vinícius Chiconato
* **Questão atendida:** Organização do trabalho
* **Exigência feita à IA:** Planejar a execução e a auditoria.
* **Prompt:** "resume o plano de execução e como podemos organizar em issues talvez para registro e auditoria?"
* **Resposta obtida:** Plano em quatro marcos, 22 issues propostas, modelo de issue e ligação das issues com o memorial.
* **Verificação:** Conferência da cobertura de todas as 15 questões e dos 5 entregáveis obrigatórios do enunciado nas etapas do plano.
* **Decisão do grupo:** Usamos o plano em quatro marcos como guia interno de controle de progresso e, na reta final, abrimos issues no GitHub (#1 a #3) para acompanhar as verificações e a revisão dos textos.
* **Erros da IA:** Nenhum identificado até aqui.

### Interação 7 — Q1

* **Ferramenta:** Claude (Anthropic), modelo configurado claude-opus-5-5, pelo app claude.ai (sessão de trabalho com execução de código, conectores do Google Drive e de documentos)
* **Data e responsável:** 13/11/2026 · Diego Casagrande, Mateus Martins, Silvio Sznifer, Vinícius Chiconato
* **Questão atendida:** Q1
* **Exigência feita à IA:** Corrigir o número do grupo (estava 3).
* **Prompt:** "o grupo estava errado... corrigi para 4"
* **Resposta obtida:** Semente alterada para 202604, bases regeradas (commit 545e564).
* **Verificação:** Hashes de duas execuções idênticos; números da Parte A recalculados.
* **Decisão do grupo:** O erro foi nosso, não da IA: informamos o grupo 3 no início. Pedimos a correção, regeneramos tudo com a semente 202604 e separamos os arquivos antigos numa pasta própria, para não entregá-los por engano.
* **Erros da IA:** Nenhum identificado até aqui.

### Interação 8 — Q2 a Q15

* **Ferramenta:** Claude (Anthropic), modelo configurado claude-opus-5-5, pelo app claude.ai (sessão de trabalho com execução de código, conectores do Google Drive e de documentos)
* **Data e responsável:** 13/11/2026 · Diego Casagrande, Mateus Martins, Silvio Sznifer, Vinícius Chiconato
* **Questão atendida:** Q2 a Q15
* **Exigência feita à IA:** Executar o plano completo.
* **Prompt:** "pode executar todo o plano"
* **Resposta obtida:** Anexos: src/q02\_verificacao.py … src/q14\_smc\_risco.py, src/relatorio.py, tabelas e figuras em saidas/, relatório técnico, parecer executivo e este registro (commit fa4c144).
* **Verificação:** Verificação independente feita pela IA a partir das bases, sem o código do projeto: t da Q8-a, z da Q8-b, VaR da Q4-e, F = t² da Q10, LR de Kupiec da Q8-d, valor preditivo da Q5-c e ROI da Q14-e coincidiram; duas execuções com resultados idênticos. Conferência pelo grupo (14/11/2026, execução local): recalculamos na planilha `saidas/resultados.xlsx` o teste t da Q8-a, (4,70 − 4)/(4,73/√904) ≈ 4,45, o teste Z da Q8-b, (0,4209 − 0,40)/√(0,24/2965) ≈ 2,32, e o ROI da Q14-e, (25,60 − 8)/8 = 220%; em outro computador, clonamos o repositório, instalamos as dependências (`pip install -r requirements.txt`) e executamos `python main.py --grupo 4 --sem-relatorio`, e o `dados/sha256.json` gerado coincidiu com o do repositório (`git diff` sem mudanças).
* **Decisão do grupo:** Aceitamos as análises depois de recalcular os resultados principais (ver Verificação) e de ler cada interpretação. Mantivemos as três escolhas de modelagem listadas em Erros da IA: o VaR da Q8-d com todas as unidades-mês dá 576 observações de treino, contra 24 por unidade; os índices sazonais da Q12 aparecem com e sem abril/2025, o que deixa a escolha transparente; e o efeito do SOC na Q14-d usa apenas modelos estimados na Parte B, como pede o enunciado. As interpretações foram revistas e reescritas pelo grupo (interações 11 e 12).
* **Erros da IA:** Escolhas de modelagem da IA que o grupo deve validar: VaR da Q8-d sobre todas as unidades-mês; índices sazonais com e sem abril/2025 (Q12); efeito do SOC no tempo e na severidade da Q14-d. Ajustes de formatação de tabelas e listas no relatório foram corrigidos pela IA ao revisar o PDF.

### Interação 9 — Entrega (repositório)

* **Ferramenta:** Claude (Anthropic), modelo configurado claude-opus-5-5, pelo app claude.ai (sessão de trabalho com execução de código, conectores do Google Drive e de documentos)
* **Data e responsável:** 13/11/2026 · Diego Casagrande, Mateus Martins, Silvio Sznifer, Vinícius Chiconato
* **Questão atendida:** Entrega (repositório)
* **Exigência feita à IA:** Dar acesso de escrita ao repositório GitHub.
* **Prompt:** "?como concedo acesso ao repositório git?" → "teste acesso ao git"
* **Resposta obtida:** Instruções para instalar o app do Claude no repositório; após a liberação, envio dos três commits ao branch main.
* **Verificação:** git ls-remote confirmou o mesmo commit no servidor e localmente.
* **Decisão do grupo:** Concedemos acesso apenas a este repositório e conferimos no GitHub os commits enviados.
* **Erros da IA:** Nenhum identificado até aqui.

### Interação 10 — Entrega (revisão final)

* **Ferramenta:** Claude (Anthropic), modelo configurado claude-opus-5-5, pelo app claude.ai (sessão de trabalho com execução de código, conectores do Google Drive e de documentos)
* **Data e responsável:** 13/11/2026 · Diego Casagrande, Mateus Martins, Silvio Sznifer, Vinícius Chiconato
* **Questão atendida:** Entrega (revisão final)
* **Exigência feita à IA:** Conferir se tudo foi feito e concluir as pendências.
* **Prompt:** "isso, agora confere se já fez tudo e pode fazer todo o resto"
* **Resposta obtida:** Checklist contra o enunciado; memorial com os nove campos; atualização da pasta PROVA no Drive, da planilha e do roteiro para o grupo 4.
* **Verificação:** Checklist dos entregáveis e das questões contra o enunciado.
* **Decisão do grupo:** Aceitamos o checklist. Os itens que só o grupo pode fazer (nomes, interpretações, decisões deste memorial, reflexão final e anexo da conversa) ficaram conosco.
* **Erros da IA:** Nenhum identificado até aqui.

### Interação 11 — Q1–Q14 (interpretações) e memorial

* **Ferramenta:** Claude (Anthropic), modelo configurado claude-opus-5-5, pelo app claude.ai (sessão de trabalho com execução de código, conectores do Google Drive e de documentos)
* **Data e responsável:** 13/11/2026 · Diego Casagrande, Mateus Martins, Silvio Sznifer, Vinícius Chiconato
* **Questão atendida:** Q1–Q14 (interpretações) e memorial
* **Exigência feita à IA:** Ter uma primeira versão, para revisar, das partes do relatório e do memorial que cabem ao grupo.
* **Prompt:** "faça nos docs destacados, menos a parte dos nomes, sugestões de tudo o que temos que fazer como se fosse o grupo... ao fim também faça uma lista detalhada aqui de quais passos devemos executar passo a passo"
* **Resposta obtida:** Sugestões destacadas em amarelo: um parágrafo "Leitura do grupo para a ANDI" ao fim de cada questão do relatório, o campo Decisão do grupo de cada interação e a reflexão final deste memorial; lista de passos para a revisão (commit ee86338).
* **Verificação:** Leitura crítica de cada parágrafo sugerido, conferindo todos os valores numéricos, percentuais e p-valores contra as tabelas geradas em `saidas/tabelas/` e o texto técnico de cada questão.
* **Decisão do grupo:** Utilizamos as sugestões como estrutura inicial e submetemos os textos a uma revisão crítica e ampliação (Interação 12) para aprofundar a conexão com o contexto gerencial da ANDI antes de remover os destaques amarelos.
* **Erros da IA:** Nenhum identificado até aqui.

### Interação 12 — Q1–Q15 e memorial (revisão crítica e ampliação)

* **Ferramenta:** Claude (Anthropic), modelo configurado claude-opus-5-5, pelo app claude.ai (sessão de trabalho com execução de código, conectores do Google Drive e de documentos)
* **Data e responsável:** 14/11/2026 · Diego Casagrande, Mateus Martins, Silvio Sznifer, Vinícius Chiconato
* **Questão atendida:** Q1–Q15 e memorial (revisão crítica e ampliação)
* **Exigência feita à IA:** Incorporar aos documentos os textos revisados e ampliados pelo grupo (leituras das Q1–Q14 e novo parecer executivo), conferindo a coerência dos números com os resultados; ajustar prazo interno, autoria, formatação e campos pendentes do memorial.
* **Prompt:** Pedido em nove itens, enviado com os anexos TextosDoGrupo.docx (leituras revisadas) e relatorio\_tecnico.docx (novo parecer); texto integral no histórico exportado da conversa, em anexo.
* **Resposta obtida:** Textos do grupo incorporados ao relatório e ao parecer, com correções pontuais de coerência; parágrafos justificados; prazo interno de 04/12 e autoria com os quatro integrantes; campos das interações 6, 8 e 11 preenchidos; destaques amarelos removidos.
* **Verificação:** A IA conferiu cada número dos textos do grupo contra `saidas/resultados.json` e `saidas/tabelas/` e apontou as incoerências encontradas antes da incorporação.
* **Decisão do grupo:** Aceitamos as cinco correções de coerência apontadas na conferência (parecer: perdas catastróficas, causa dos 94% e superfície de ataque; Q5: prevalência; Q10: viés de seleção). Na Q13, retiramos "precisão na calibração de probabilidades", que não foi testada; na Q14, trocamos "eliminando por completo" por "nas simulações". Registro na issue #3 do GitHub.
* **Erros da IA:** Nenhum identificado até aqui.

### Interação 13 — Relatório técnico (Q1–Q14)

* **Ferramenta:** Sem uso de IA (revisão feita pelo grupo)
* **Data e responsável:** 20/11/2026 · Diego Casagrande, Mateus Martins, Silvio Sznifer, Vinícius Chiconato
* **Questão atendida:** Relatório técnico (Q1–Q14)
* **Exigência feita à IA:** Revisão do grupo no relatório técnico: leitura integral, conferência das tabelas, figuras e interpretações contra os resultados do código.
* **Prompt:** —
* **Resposta obtida:** —
* **Verificação:** Comparação dos números do texto com `saidas/resultados.xlsx` e `saidas/tabelas/`.
* **Decisão do grupo:** Correções registradas e incorporadas ao relatório técnico.
* **Erros da IA:** —

### Interação 14 — Q1–Q15 (todas as respostas)

* **Ferramenta:** Sem uso de IA (revisão feita pelo grupo)
* **Data e responsável:** 27/11/2026 · Diego Casagrande, Mateus Martins, Silvio Sznifer, Vinícius Chiconato
* **Questão atendida:** Q1–Q15 (todas as respostas)
* **Exigência feita à IA:** Revisão do grupo em todas as respostas: cada resposta numérica com interpretação no contexto da ANDI e comparação com os parâmetros do gerador quando pedida.
* **Prompt:** —
* **Resposta obtida:** —
* **Verificação:** Leitura cruzada: cada integrante revisou as questões de outra frente.
* **Decisão do grupo:** Ajustes de redação e de interpretação incorporados às respostas.
* **Erros da IA:** —

### Interação 15 — Relatório técnico (versão final)

* **Ferramenta:** Sem uso de IA (revisão feita pelo grupo)
* **Data e responsável:** 29/11/2026 · Diego Casagrande, Mateus Martins, Silvio Sznifer, Vinícius Chiconato
* **Questão atendida:** Relatório técnico (versão final)
* **Exigência feita à IA:** Versão final da revisão do relatório técnico: até 30 páginas, parecer em uma página, documentos gerados com `python main.py --grupo 4`.
* **Prompt:** —
* **Resposta obtida:** —
* **Verificação:** Execução completa do código e conferência dos hashes em `dados/sha256.json`.
* **Decisão do grupo:** Versão final aprovada pelo grupo para entrega.
* **Erros da IA:** —

## Reflexão final

**Em que a IA ajudou.** As ferramentas de IA aceleraram significativamente a estruturação do plano de trabalho a partir do enunciado, a implementação modular do gerador de dados e das rotinas estatísticas em Python, bem como a geração automatizada de tabelas, gráficos e documentos. Também foram úteis na etapa de auditoria cruzada: a IA recalculou métricas-chave diretamente a partir das bases (independentemente dos scripts principais) para confirmar a consistência dos resultados e auxiliou na revisão crítica da clareza executiva das interpretações para a diretoria da ANDI. Essa automação permitiu que o grupo concentrasse esforços na análise estatística, na comparação entre estimativas e parâmetros verdadeiros e na fundamentação das recomendações de negócio.

**Em que atrapalhou ou errou.** Identificamos falhas pontuais que exigiriam correção manual caso não houvesse revisão rigorosa: na geração inicial das bases, o arredondamento para 6 algarismos significativos distorcia somatórios elevados (`perda_total`); houve problemas de formatação em tabelas e listas do relatório; e uma formulação inicial do parecer executivo confundia a subestimação do desvio-padrão com a subestimação do VaR e do CVaR. Além disso, a IA tomou decisões de modelagem em pontos abertos do enunciado (como o cálculo do VaR agrupado na Q8-d, o tratamento de abril/2025 nos índices sazonais da Q12 e a parametrização do efeito do SOC na Q14-d) que precisaram ser tecnicamente avaliadas e validadas pelo grupo. O maior risco metodológico foi a velocidade de geração de código e texto, que poderia induzir à entrega sem domínio pleno do conteúdo — risco mitigado pela leitura, conferência numérica e reescrita ativa de todas as interpretações.

**O que consideramos exclusivamente nosso.** São integralmente do grupo as decisões de projeto (uso da semente do grupo, 202604, conforme a regra do enunciado, adoção da pilha em Python e validação das premissas de modelagem nas Questões 8, 12 e 14), a auditoria independente dos códigos e fórmulas contra o enunciado, os recálculos de verificação realizados na planilha e em ambiente separado, a redação final das interpretações gerenciais e do parecer executivo, bem como a responsabilidade técnica e a defesa do estudo na arguição.
