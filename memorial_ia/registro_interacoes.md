---
title: "Memorial do Uso de IA — Grupo 4"
lang: pt-BR
---

**Ferramenta:** Claude (Anthropic), modelo configurado `claude-opus-5-5`, acesso pelo app claude.ai (sessão de trabalho com execução de código).
**Responsável pelas interações:** Diego Casagrande. \_(Acrescentar as interações dos demais integrantes, se houver.)\_

Este registro foi preparado a partir da conversa com a IA. As colunas **Decisão do grupo** e **Erros da IA**, e a reflexão final, devem ser escritas pelo grupo.

## Registro das interações

| Data | Questão | Exigência feita à IA | Prompt (íntegra) | Resposta obtida (síntese) | Verificação feita |
| :------------ | :--------------------------- | :----------------------------------------------------------- | :----------------------------------------------------------- | :----------------------------------------------------------- | :----------------------------------------------------------- |
| 12/11/2026 | Q1–Q15 (planejamento) | Avaliar a prova e escrever um roteiro passo a passo de resolução. | "[anexo: AEDI\_Enunciado\_Prova.pdf] do mesmo professor que é autor do livro temos que fazer essa prova passo a passo e gerar os itens integraveis conforme escrito no documento anexo aqui / avalie como pode ser realizado esse trabalho, escreva o roteiro passo a passo para resolução" | Roteiro (documento compartilhado): avaliação, estrutura do repositório, Parte A, roteiro por questão, memorial, cronograma e ambiguidades do enunciado. Incluiu um protótipo do gerador com semente de teste para ordens de grandeza. | Leitura do roteiro pelo grupo e conferência das regras e pontos contra o enunciado. |
| 12/11/2026 | Decisões de implementação | Confirmar as decisões propostas. | "pode ser tudo como está na proposta" / "falta o que" | Registro das decisões no roteiro. | Decisões revistas pelo grupo (o número do grupo foi informado pelo grupo). |
| 12/11/2026 | Q1 (Parte A) | Implementar o gerador e as bases. | "use esse respositório para o código https://github.com/diegocasagrande/aedi" / "salve os arquivos nessa pasta [link do Drive]" | src/gerador.py, src/inversa.py, main.py, README; bases e hashes. A IA não conseguiu enviar ao GitHub (sem permissão) e entregou o commit em arquivo (bundle). | Duas execuções com hashes idênticos; contagens, taxa de materialização e tempos médios comparados com os valores programados; teste KS das inversas. |
| 12/11/2026 | Q1–Q2 | Gerar uma planilha com os números da Parte A. | "Crie uma planilha a partir da sua última resposta." | Planilha com conferência, tipos, inversas, arquivos e pendências. | Fórmulas da planilha lidas de volta e conferidas. |
| 13/11/2026 | Q1 | Explicar a semente. | "Confere como ficou a seed, me explica porque?" | Explicação de gerador pseudoaleatório, reprodutibilidade e bases por grupo. | Conferido contra o enunciado (semente = 202600 + nº do grupo). |
| 13/11/2026 | Organização | Plano de execução e organização em issues. | "resume o plano de execução e como podemos organizar em issues talvez para registro e auditoria?" | Proposta de milestones, 22 issues e modelo de issue. | — |
| 13/11/2026 | Q1 | Corrigir o número do grupo. | "o grupo estava errado... corrigi para 4" | Semente alterada para 202604; bases regeradas; novo commit. | Hashes de duas execuções idênticos; números da Parte A recalculados. |
| 13/11/2026 | Q2–Q15 | Executar todo o plano. | "pode executar todo o plano" | Código das questões 2 a 14 (src/q02…q14), tabelas, figuras, este relatório, o parecer e este registro. | A preencher pelo grupo: conferência de cada número (ver sugestões abaixo). |

## Erros e limitações da IA observados (rascunho para o grupo revisar)

* Na exportação inicial das bases, a IA usou um formato numérico com 6 algarismos significativos que arredondaria totais grandes (ex.: perda\_total). O erro foi percebido e corrigido antes do primeiro commit.
* O roteiro inicial trazia números de um protótipo com semente de teste (202699). Eles servem só como ordem de grandeza e não são as bases do grupo.
* A IA não teve acesso de escrita ao GitHub nem, em parte da sessão, aos conectores do Google Drive e do documento compartilhado; os arquivos foram entregues por outros meios.
* Escolhas de modelagem feitas pela IA que o grupo deve validar: (i) VaR da Q8-d calculado sobre todas as unidades-mês juntas; (ii) na Q12, índices sazonais com e sem abril/2025; (iii) na Q14-d, o efeito do SOC no tempo de detecção entrou como reescala dos tempos (razão das médias estimadas na Q7) e na severidade por β\_tempo da Q10-d.

## Verificações sugeridas antes da entrega

1. Rodar `python main.py --grupo 4` em outra máquina e comparar `dados/sha256.json`.
2. Recalcular à mão (ou na planilha) um resultado por questão: por exemplo, o t da Q8-a, o VaR da Q4-e, o F = t² da Q10-a e o ROI da Q14-e.
3. Ler cada interpretação do relatório e reescrevê-la com as palavras do grupo: a arguição cobra o entendimento de todos.

## Decisão do grupo e reflexão final (1 página — a escrever pelo grupo)

\_Onde a IA ajudou, onde atrapalhou, o que foi aceito, corrigido ou descartado, e qual parte do trabalho o grupo considera exclusivamente sua.\_
