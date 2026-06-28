# Feature-loop — Sources académiques et techniques

Regroupe les sources citées en abrégé dans SKILL.md et scoring-rubric.md, avec ce qu'elles fondent dans le skill. À lire seulement si on veut vérifier/approfondir un fondement.

## Patterns d'orchestration (Anthropic)
- **Anthropic — *Building Effective Agents*** : patterns orchestrator-workers et evaluator-optimizer ; l'évaluateur doit être distinct du générateur quand les critères sont clairs et mesurables (notre radar).
- **Anthropic — *How we built our multi-agent research system*** : un lead Opus + workers Sonnet surpasse un Opus seul de ~90 % sur tâches complexes ; un système multi-agents consomme ≈ 15× les tokens d'un chat → proportionner l'effort à l'enjeu.

## LLM-as-judge (fondent la séparation des rôles + l'anti-biais du juge)
- **Zheng et al. 2023 (MT-Bench / Chatbot Arena)** : biais de position, de verbosité, d'auto-complaisance (Claude-v1 se surnote de +25 %) → review en aveugle, anti-verbosity, ordre inversé au 2ᵉ juge.
- **Panickssery et al. 2024** : les LLM reconnaissent et favorisent leur propre sortie → writer ≠ tester ≠ reviewer, auto-review interdite.
- **Verga et al. 2024 (PoLL — Panel of LLM judges)** : un panel de juges variés bat un juge unique et coûte 7-8× moins qu'un gros juge — MAIS cette économie vaut pour des *petits* juges ; notre panel mixte (1 fort + 2 Sonnet) vise la réduction du biais de position, pas l'économie (outillage mono-famille Claude : diversité de famille indisponible, la préférer via MCP si dispo).
- **Liu et al. 2023 (G-Eval)** : raisonner (CoT) AVANT de poser la note améliore l'accord avec l'humain → « constat + file:line avant chaque note ».

## Raffinement itératif (fondent max 3 iters + best-version + gate objectif)
- **Madaan et al. 2023 (Self-Refine)** : les gains plafonnent après 2-3 itérations ; une itération peut régresser → garder la MEILLEURE version, pas la dernière.
- **Shinn et al. 2023 (Reflexion)** : le raffinement ne gagne que parce que les *tests* fournissent le signal externe.
- **Huang et al. ICLR 2024** : l'auto-correction LLM sans oracle externe DÉGRADE souvent → aucune itération SUCCESS sur la seule auto-critique ; gate objectif (build/lint/tests) obligatoire avant tout juge.

## Tests générés par LLM (fondent le red-check + tests-depuis-la-spec)
- **TDD-Bench Verified 2024** : 76 % des tests générés par LLM échouent le critère "fail-to-pass" (ils ne rougissent pas sur le code cassé) → red-check par mutation sur les tests critiques.
- **Meta — mutation-guided test generation** : la mutation ciblée comme preuve qu'un test protège réellement un comportement.
