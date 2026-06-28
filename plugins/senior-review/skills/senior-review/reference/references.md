# Senior-review — Sources (traçabilité)

Regroupe les sources citées en abrégé dans le SKILL.md, avec ce qu'elles fondent. À lire seulement pour vérifier/approfondir un fondement.

## LLM-as-judge & biais (fondent reviewer ≠ auteur, blind review, CoT avant verdict)
- **Panickssery 2024** (arXiv:2404.13076) — self-preference bias : un modèle qui juge sa propre sortie se surnote → reviewers en contexte vierge, jamais le prompt d'implémentation.
- **Wataoka 2024** (arXiv:2410.21819) — confirmation du biais d'auto-préférence.
- **Zheng / MT-Bench 2023** (arXiv:2306.05685) — biais de position, de verbosité, d'auto-complaisance → ordre inversé chez les refuteurs, anti-verbosity.
- **G-Eval / Liu 2023** (arXiv:2303.16634) — raisonner (CoT) avant de poser la note améliore l'accord avec l'humain.

## Panels / débat (fondent le refute-panel ciblé, pas un débat généralisé)
- **Verga / PoLL 2024** (arXiv:2404.18796) — panel de juges variés > juge unique.
- **Du 2023** (arXiv:2305.14325) — multiagent debate.
- **« Stop Overvaluing Multi-Agent Debate »** (arXiv:2502.08788) — le débat généralisé est surévalué → réfutation ciblée sur critical/incertain seulement.

## Auto-correction (fonde le gate objectif externe, pas de revue-de-la-revue en boucle)
- **Huang ICLR 2024** (arXiv:2310.01798) — l'auto-correction sans oracle externe dégrade.
- **Self-Refine** (arXiv:2303.17651), **Reflexion** — le raffinement ne marche qu'avec un signal externe (tests).

## Détection de bugs / grounding (fondent le gate de vérification « receipts »)
- **CriticGPT** (OpenAI 2024) — critique entraînée à trouver des bugs ; les humains+critique > humains seuls.
- **Agentless** (arXiv:2407.01489) — localisation simple + vérification > agents complexes.
- **« Verify Before You Fix »** (arXiv:2604.10800) — execution-grounding rejette ~60 % des faux positifs.
- **« Are LLMs Reliable Code Reviewers? »** (arXiv:2603.00539) — overcorrection systématique : les LLMs sur-flaguent.
- **arXiv:2505.20206** — sans la description du problème (ticket/PR), la revue LLM perd sensiblement en précision → spec-alignment + ticket-aware.

## Mutation / tests (fondent le red-check bidirectionnel de l'Étape 4)
- **TDD-Bench Verified** (arXiv:2412.02883) — critère fail-to-pass : la plupart des tests LLM ne rougissent pas sur code cassé.
- **Mutation @ Meta** (arXiv:2501.12862) — mutation-guided comme preuve qu'un test protège un comportement.

## Faux positifs / calibration (fondent signal > recall, cap nits)
- **iCodeReviewer** (arXiv:2510.12186) — mixture-of-prompts, routage des dimensions pertinentes.
- **LLM4PFA / Tencent** (arXiv:2601.18844) — filtrage agentique des faux positifs.
- **Datadog** — FP-filtering en production.

## Outils de référence (ce que chacun a apporté à l'architecture)
- **CodeRabbit** — codegraph + learnings persistants + verification agent.
- **Greptile** — graphe multi-hop ; bench : diff seul ~44 % de catch-rate vs ~82 % avec contexte cross-fichiers → context-first.
- **Cursor BugBot** — passes parallèles + majority vote → agentic.
- **GitHub Copilot code review** — agentic + silence intentionnel (~29 % de revues silencieuses assumées).
- **Qodo** — agents par dimension. **Snyk DeepCode** — symbolic+neural. **Atlassian Rovo** — judge + classifier.

## Pratiques d'ingénierie
- **Google eng-practices** (looking-for / standard / comments / navigate) — seuil de greenlight : le changement améliore la base, pas « est parfait ».
- **SmartBear/Cisco** — le taux de détection chute avec la taille du diff (87 % ≤100 LOC vs 28 % >1000 LOC, Propel) → découpage ≤ 300-400 LOC.
- **Cloudflare / G-Research** — prompt patterns ; « telling an LLM what not to do is where the value is » → what-NOT-to-flag.
- **WirelessCar 2025** (étude d'adoption d'outils de revue IA) — le bruit / les faux positifs minent l'adoption → signal > recall.
