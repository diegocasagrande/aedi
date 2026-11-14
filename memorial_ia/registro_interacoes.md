---
title: "Memorial do Uso de IA — Grupo 4"
lang: pt-BR
---

O grupo usou ferramenta de IA. Este memorial registra, para cada interação relevante, os nove campos pedidos no enunciado. A mesma informação está em planilha (`memorial_ia/registro.xlsx`). O código gerado está no repositório, identificado pelo commit indicado em cada interação, e o histórico exportado da conversa deve ser anexado em `memorial_ia/anexos/`.

**Ferramenta usada em todas as interações:** Claude (Anthropic), modelo configurado claude-opus-5-5, pelo app claude.ai (sessão de trabalho com execução de código, conectores do Google Drive e de documentos).

**A preencher pelo grupo antes da entrega:** o campo *Decisão do grupo* de cada interação, interações de outros integrantes (se houver), o anexo com o histórico da conversa e a reflexão final.

## Registro das interações

### Interação 1 — Q1–Q15 (planejamento)

* **Ferramenta:** Claude (Anthropic), modelo configurado claude-opus-5-5, pelo app claude.ai (sessão de trabalho com execução de código, conectores do Google Drive e de documentos)
* **Data e responsável:** 12/11/2026 · Diego Casagrande
* **Questão atendida:** Q1–Q15 (planejamento)
* **Exigência feita à IA:** Entender o que a prova pede e organizar a resolução antes de começar.
* **Prompt:** [anexo: AEDI\_Enunciado\_Prova.pdf] "do mesmo professor que é autor do livro temos que fazer essa prova passo a passo e gerar os itens integraveis conforme escrito no documento anexo aqui avalie como pode ser realizado esse trabalho, escreva o roteiro passo a passo para resolução"
* **Resposta obtida:** Roteiro em documento compartilhado: avaliação e pontuação, estrutura do repositório, implementação da Parte A, método e armadilhas de cada questão, memorial, cronograma até 09/12 e ambiguidades do enunciado. Para dar ordens de grandeza, rodou um protótipo do gerador com semente de teste (202699).
* **Verificação:** Conferência das regras e da pontuação contra o enunciado.
* **Decisão do grupo:** (a preencher pelo grupo)
* **Erros da IA:** Erro de digitação no roteiro ("A tempo médio"), corrigido na mesma sessão.

### Interação 2 — Decisões de implementação

* **Ferramenta:** Claude (Anthropic), modelo configurado claude-opus-5-5, pelo app claude.ai (sessão de trabalho com execução de código, conectores do Google Drive e de documentos)
* **Data e responsável:** 12/11/2026 · Diego Casagrande
* **Questão atendida:** Decisões de implementação
* **Exigência feita à IA:** Fechar os pontos em aberto do enunciado.
* **Prompt:** "pode ser tudo como está na proposta" → "falta o que"
* **Resposta obtida:** Registro das decisões no roteiro: calendário real (fev/2024 com 29 dias), trimestre = q(t) de 1 a 12, coluna p\_programado, planilha gerada pelo código, VaR da Q8-d com todas as unidades-mês, p̄ por unidade na Q14.
* **Verificação:** O número do grupo e o uso de Python foram informados pelo grupo na tabela do roteiro.
* **Decisão do grupo:** (a preencher pelo grupo)
* **Erros da IA:** Nenhum identificado até aqui.

### Interação 3 — Q1-a, Q1-b

* **Ferramenta:** Claude (Anthropic), modelo configurado claude-opus-5-5, pelo app claude.ai (sessão de trabalho com execução de código, conectores do Google Drive e de documentos)
* **Data e responsável:** 12/11/2026 · Diego Casagrande
* **Questão atendida:** Q1-a, Q1-b
* **Exigência feita à IA:** Implementar o gerador (Parte A) e as bases num repositório.
* **Prompt:** "use esse respositório para o código https://github.com/diegocasagrande/aedi" → "salve os arquivos nessa pasta https://drive.google.com/drive/folders/1fhICSMGAVKpyEv8afX6zrzEAQgXnIySQ"
* **Resposta obtida:** Anexos: src/gerador.py, src/inversa.py, main.py, README.md (commit 2d63be9). Bases e hashes sha256. Arquivos salvos na pasta PROVA do Drive. O envio ao GitHub falhou por falta de permissão; o commit foi entregue em arquivo bundle.
* **Verificação:** Duas execuções com hashes idênticos; contagens, taxa de materialização e tempos médios comparados com os valores programados; teste KS das inversas contra o numpy.
* **Decisão do grupo:** (a preencher pelo grupo)
* **Erros da IA:** A exportação inicial das bases usava formato numérico com 6 algarismos significativos, o que arredondaria totais grandes (perda\_total); percebido e corrigido antes do commit.

### Interação 4 — Q1, Q2-c

* **Ferramenta:** Claude (Anthropic), modelo configurado claude-opus-5-5, pelo app claude.ai (sessão de trabalho com execução de código, conectores do Google Drive e de documentos)
* **Data e responsável:** 12/11/2026 · Diego Casagrande
* **Questão atendida:** Q1, Q2-c
* **Exigência feita à IA:** Ter os números da Parte A numa planilha.
* **Prompt:** "Crie uma planilha a partir da sua última resposta."
* **Resposta obtida:** Planilha compartilhada com conferência estimado × programado, tipos de ataque com σ/√n, inversas, lista de arquivos e pendências.
* **Verificação:** Fórmulas da planilha lidas de volta e conferidas; qui-quadrado dos tipos recalculado.
* **Decisão do grupo:** (a preencher pelo grupo)
* **Erros da IA:** Nenhum identificado até aqui.

### Interação 5 — Q1

* **Ferramenta:** Claude (Anthropic), modelo configurado claude-opus-5-5, pelo app claude.ai (sessão de trabalho com execução de código, conectores do Google Drive e de documentos)
* **Data e responsável:** 13/11/2026 · Diego Casagrande
* **Questão atendida:** Q1
* **Exigência feita à IA:** Entender a semente do gerador.
* **Prompt:** "Confere como ficou a seed, me explica porque?"
* **Resposta obtida:** Explicação: semente = 202600 + nº do grupo; gerador pseudoaleatório (PCG64); reprodutibilidade; bases diferentes por grupo; importância da ordem dos sorteios.
* **Verificação:** Conferido contra o enunciado e por execução (mesmos três primeiros sorteios com a mesma semente).
* **Decisão do grupo:** (a preencher pelo grupo)
* **Erros da IA:** Nenhum identificado até aqui.

### Interação 6 — Organização do trabalho

* **Ferramenta:** Claude (Anthropic), modelo configurado claude-opus-5-5, pelo app claude.ai (sessão de trabalho com execução de código, conectores do Google Drive e de documentos)
* **Data e responsável:** 13/11/2026 · Diego Casagrande
* **Questão atendida:** Organização do trabalho
* **Exigência feita à IA:** Planejar a execução e a auditoria.
* **Prompt:** "resume o plano de execução e como podemos organizar em issues talvez para registro e auditoria?"
* **Resposta obtida:** Plano em quatro marcos, 22 issues propostas, modelo de issue e ligação das issues com o memorial.
* **Verificação:** —
* **Decisão do grupo:** (a preencher pelo grupo)
* **Erros da IA:** Nenhum identificado até aqui.

### Interação 7 — Q1

* **Ferramenta:** Claude (Anthropic), modelo configurado claude-opus-5-5, pelo app claude.ai (sessão de trabalho com execução de código, conectores do Google Drive e de documentos)
* **Data e responsável:** 13/11/2026 · Diego Casagrande
* **Questão atendida:** Q1
* **Exigência feita à IA:** Corrigir o número do grupo (estava 3).
* **Prompt:** "o grupo estava errado... corrigi para 4"
* **Resposta obtida:** Semente alterada para 202604, bases regeradas (commit 545e564).
* **Verificação:** Hashes de duas execuções idênticos; números da Parte A recalculados.
* **Decisão do grupo:** (a preencher pelo grupo)
* **Erros da IA:** Nenhum identificado até aqui.

### Interação 8 — Q2 a Q15

* **Ferramenta:** Claude (Anthropic), modelo configurado claude-opus-5-5, pelo app claude.ai (sessão de trabalho com execução de código, conectores do Google Drive e de documentos)
* **Data e responsável:** 13/11/2026 · Diego Casagrande
* **Questão atendida:** Q2 a Q15
* **Exigência feita à IA:** Executar o plano completo.
* **Prompt:** "pode executar todo o plano"
* **Resposta obtida:** Anexos: src/q02\_verificacao.py … src/q14\_smc\_risco.py, src/relatorio.py, tabelas e figuras em saidas/, relatório técnico, parecer executivo e este registro (commit fa4c144).
* **Verificação:** Verificação independente feita pela IA a partir das bases, sem o código do projeto: t da Q8-a, z da Q8-b, VaR da Q4-e, F = t² da Q10, LR de Kupiec da Q8-d, valor preditivo da Q5-c e ROI da Q14-e coincidiram; duas execuções com resultados idênticos. Conferência pelo grupo: (a preencher pelo grupo)
* **Decisão do grupo:** (a preencher pelo grupo)
* **Erros da IA:** Escolhas de modelagem da IA que o grupo deve validar: VaR da Q8-d sobre todas as unidades-mês; índices sazonais com e sem abril/2025 (Q12); efeito do SOC no tempo e na severidade da Q14-d. Ajustes de formatação de tabelas e listas no relatório foram corrigidos pela IA ao revisar o PDF.

### Interação 9 — Entrega (repositório)

* **Ferramenta:** Claude (Anthropic), modelo configurado claude-opus-5-5, pelo app claude.ai (sessão de trabalho com execução de código, conectores do Google Drive e de documentos)
* **Data e responsável:** 13/11/2026 · Diego Casagrande
* **Questão atendida:** Entrega (repositório)
* **Exigência feita à IA:** Dar acesso de escrita ao repositório GitHub.
* **Prompt:** "?como concedo acesso ao repositório git?" → "teste acesso ao git"
* **Resposta obtida:** Instruções para instalar o app do Claude no repositório; após a liberação, envio dos três commits ao branch main.
* **Verificação:** git ls-remote confirmou o mesmo commit no servidor e localmente.
* **Decisão do grupo:** (a preencher pelo grupo)
* **Erros da IA:** Nenhum identificado até aqui.

### Interação 10 — Entrega (revisão final)

* **Ferramenta:** Claude (Anthropic), modelo configurado claude-opus-5-5, pelo app claude.ai (sessão de trabalho com execução de código, conectores do Google Drive e de documentos)
* **Data e responsável:** 13/11/2026 · Diego Casagrande
* **Questão atendida:** Entrega (revisão final)
* **Exigência feita à IA:** Conferir se tudo foi feito e concluir as pendências.
* **Prompt:** "isso, agora confere se já fez tudo e pode fazer todo o resto"
* **Resposta obtida:** Checklist contra o enunciado; memorial com os nove campos; atualização da pasta PROVA no Drive, da planilha e do roteiro para o grupo 4.
* **Verificação:** Checklist dos entregáveis e das questões contra o enunciado.
* **Decisão do grupo:** (a preencher pelo grupo)
* **Erros da IA:** Nenhum identificado até aqui.

## Verificações sugeridas antes da entrega

1. Rodar `python main.py --grupo 4` em outra máquina e comparar `dados/sha256.json`.
2. Recalcular à mão, ou na planilha, um resultado por questão: por exemplo o t da Q8-a, o VaR da Q4-e, o F = t² da Q10-a e o ROI da Q14-e.
3. Ler cada interpretação do relatório e reescrevê-la com as palavras do grupo: a arguição cobra o entendimento de todos.

## Reflexão final (até uma página — a escrever pelo grupo)

*Em que a IA ajudou, em que atrapalhou ou errou, e qual parte do trabalho o grupo considera exclusivamente sua.*
