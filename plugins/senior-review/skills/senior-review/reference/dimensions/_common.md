# Brief commun des relecteurs

Chaque agent **raisonne avant de noter** et rend, par finding : `{ severity: blocking|important|nit|suggestion, file, line, confidence: high|med|low, reasoning, finding, fix_concret, verification_plan }`. On lui donne explicitement la section **« ce qu'on NE flague PAS »** (voir plus bas). Prompt « senior 10+ ans **— en mode spécialiste, expert de la stack détectée (Étape 1) : adopte cette persona et vérifie en priorité les invariants/pièges de l'archi** —, terse, evidence-based ; ne récompense pas la longueur ; en cas d'hésitation, baisse la confiance ; en cas de doute version/API, une recherche web ciblée est permise (cite la source, re-vérifie contre le repo) ».

## Rubrique des dimensions (ancres — ce qu'un senior regarde, par priorité)

Bloquant-potentiel d'abord :
1. **Spec coverage** — couvre tout le ticket ? (pas seulement correct). Si le ticket chiffre une gêne, recompter ce chiffre sur le parcours livré ; « comme l'existant » ne répond pas à un ticket qui reproche l'existant.
2. **Design** — interactions cohérentes, abstraction au bon endroit, pas d'over-engineering (« résous le problème d'aujourd'hui, pas celui spéculé pour demain » — Google) ; et avant tout, **la capacité n'existe-t-elle pas déjà** : une surface publique neuve se justifie par une commande, pas par un plan
3. **Correctness** — logique, cas limites, concurrence/races ; **data-shape** : rejouer le chemin sur ZÉRO entité, UNE, PLUSIEURS du même groupe (multi-items même clé), doublons — les bugs de count/jointure/dédup sont invisibles au mono-entité happy-path
4. **Security** — entrées validées, authz, secrets/PII, injection, fail-closed
5. **Robustesse** — ce qui PANIQUE au lieu de rendre une erreur, et où la panique atterrit ; une garantie prêtée à une donnée d'un autre système est une hypothèse jusqu'à mesure
6. **Tests** — présents, rougissent si le code casse, cas d'erreur
7. **Error handling** — wrap `%w`, pas de panic sur erreur normale
Non-bloquant (nit/suggestion) :
8. **Perf** — N+1, allocations (sans micro-opt prématurée) · 9. **Complexity** · 10. **Naming** · 11. **Comments** (pourquoi non-évident) · 12. **Docs** (si comportement public change)
