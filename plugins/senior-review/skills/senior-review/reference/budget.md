# Mesure du plafond de fan-out

**Plafond de fan-out : 5 agents par tour, mesuré et non estimé.** Sur 66 runs du journal, le rendement s'effondre au-delà :

| agents/tour | runs | confirmés/run | tokens/run | tokens par finding |
|---|---|---|---|---|
| 1 | 22 | 1,5 | 85 k | 55 k |
| 2-3 | 17 | 4,1 | 278 k | 68 k |
| **4-5** | 15 | **9,3** | 553 k | **59 k** |
| 6-8 | 5 | 12,6 | 919 k | 73 k |
| 9+ | 7 | 12,7 | 1 384 k | 109 k |

Passer de 6-8 à 9+ coûte **+50 % de tokens pour +0,1 finding par tour**. La zone 4-5 est le meilleur rapport. Donc : **au plus 5 agents par tour**, refuteurs compris ; s'il en faut davantage, c'est un tour de plus, pas un tour plus large, et un tour de delta trouve à 55 k le finding contre 109 k pour un dixième agent. Dimensionner sur le **volume du diff** et non sur l'enjeu ressenti : environ un reviewer par 150 LOC non générées, plancher 2, plafond 5.
