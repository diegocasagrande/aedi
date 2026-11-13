---
title: "Parecer executivo à diretoria da ANDI"
subtitle: "Risco cibernético em 2026 e o pacote de controles"
author: "Grupo 4 · AEDI/PPCA-UnB"
lang: pt-BR
---

**1. Quanto a ANDI deve esperar perder em 2026?** Cerca de **R$ 34,9 mi** em perdas com incidentes cibernéticos. Em 1 ano a cada 20, a perda passa de **R$ 40,7 mi** (VaR 95%); nesses 5% piores anos, a perda média é de **R$ 42,5 mi** (CVaR 95%). Em 1 ano a cada 100 ela ultrapassa R$ 43,5 mi. A chance de perder mais de R$ 30 milhões é de 94%. Esses números vêm de 100.000 anos simulados a partir dos dados de 2023–2025 das 24 unidades.

**2. O pacote de controles de R$ 8 milhões por ano compensa?** **Sim, com folga.** O pacote leva a cobertura de patches a 95%, o treinamento a 12 h e cria um SOC em todas as unidades. Com isso, a perda esperada cai para **R$ 9,3 mi**: uma redução de **R$ 25,6 mi por ano**, ou **retorno de 220%** sobre o custo. A cauda também encolhe: o ano ruim (VaR 95%) passa de R$ 40,7 mi para R$ 12,3 mi. Em nenhum dos anos simulados o pacote somado ao seu custo saiu mais caro do que não fazer nada. O pacote continuaria valendo a pena até um custo de cerca de **R$ 26 mi por ano**. O maior ganho vem do SOC: ele reduz o número de ataques, a chance de cada ataque virar perda e o tempo até a detecção, que encarece cada perda em cerca de 2% por hora.

**3. Quão confiáveis são esses números?** A recomendação é robusta: mesmo variando a gravidade das perdas em ±20% e a frequência de ataques em ±10%, o benefício líquido fica entre R$ 13,7 mi e R$ 23,3 mi por ano. Os valores exatos, porém, têm limites que a diretoria deve conhecer:

* **A cauda está subestimada.** Comparado com o processo real que gerou os dados, o modelo acerta a perda média (diferença de 2%), mas subestima a variação de um ano para outro em cerca de 12% e a perda dos anos extremos (VaR 99% e CVaR) em cerca de 2% a 3%. VaR e CVaR devem ser tratados como pisos, com margem de segurança.
* **O passado pode não se repetir.** A tendência de alta vem de apenas três anos e foi inflada pela campanha de ataques de abril de 2025. Novas campanhas, novos tipos de ataque ou mudanças de comportamento dos atacantes alteram o quadro.
* **O efeito dos controles foi estimado, não observado.** Nenhuma unidade tem hoje os três controles no nível proposto; o efeito é extrapolado dos modelos. O efeito do SOC no tempo de detecção supõe que o novo SOC funcione como os atuais.
* **Eventos catastróficos raros** (um "cisne negro" acima de tudo o que já foi visto) não estão nos dados e não podem ser previstos por eles.

**Recomendação:** aprovar o pacote, priorizando a implantação do SOC nas 16 unidades que não o têm. O modelo deve ser revisto a cada trimestre com os novos dados, e a perda real de 2026 comparada com a faixa prevista (backtesting).
