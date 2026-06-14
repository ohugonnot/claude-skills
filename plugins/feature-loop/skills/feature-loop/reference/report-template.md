# Feature-loop — Template du rapport markdown final

Lu à l'étape §5.4 (SKILL.md), une fois par run, pour écrire `$WORK/.feature-loop/feature-loop-report.md`. Toutes les sections ci-dessous sont obligatoires (mettre "aucun" plutôt que d'omettre une section).

```markdown
# Feature Loop Report — <feature slug>

**Date** : <ISO>
**Durée totale** : <Xmin>
**Statut** : <SUCCESS | MAX_ITERATIONS | ABORTED>
**Itérations** : N (dont X rollbacks, Y plan-revisions)
**Mode paranoid** : <on/off> (<auto-triggered-by ou manual>)

## Feature demandée

> <description>

## Radar final

<radar ASCII + delta vs iter 1>

## Timeline des itérations

| # | Décision | Scores moyens | Critical fixes | Notes_ack | Durée |
|---|---|---|---|---|---|
| 1 | continue | 7.2 | 2 fixed | n/a | 4min |
| 2 | rollback | 6.8 | 1 fixed, 1 regressed | 3/3 | 3min |
| 2 (retry) | continue | 7.5 | 1 fixed | 3/3 | 3min |
| 3 | success | 8.4 | 0 | 2/2 | 4min |

## Critical / Major fixés au fil des itérations

- ✅ [iter 1, sécurité] SQL injection sur `/api/users/:id` → corrigé via prisma query
- ✅ [iter 2, a11y] Missing aria-label sur icon-only button → corrigé
- ✅ [iter 3, UX] Empty state manquant sur tableau filtré → ajouté

## Critical / Major restants (si MAX_ITERATIONS)

- ⚠️ [major, performance] N+1 sur listing → fix proposé : eager-load relations

## Ajouts non demandés (scope creep léger, justifiés)

Lister les éléments AJOUTÉS qui n'étaient PAS explicitement demandés dans la description initiale, avec justification. Seuil : tout ajout > 20 LOC ou > 1 nouvelle option/feature flag/cache/abstraction.

- ➕ `chrome.storage.local.userCardCache` (+45 LOC, prospect.js) — justification : sans cache, chaque scan refetch 4 endpoints × N prospects = quota API LBC.
- ➕ Opt-in `profile.enrichUserCard` (background.js) — justification : enrichissement coûteux, désactivé par défaut évite friction utilisateur.

Si rien d'ajouté hors scope : section vide ou "aucun".

L'user voit explicitement ces ajouts et peut demander leur retrait avant merge.

## Fichiers modifiés

- `src/api/users.ts` (+45 -3)
- `src/components/UserList.tsx` (+80)
- `tests/users.test.ts` (+120)
- `tests/e2e/user-flow.spec.ts` (+35)

## Métriques finales

- Build : ✓
- Lint : 0 erreurs, 2 warnings
- Typecheck : ✓
- Tests : 28/28 ✓ (3 nouveaux)
- Coverage feature : ~92%
- Lint plugins : a11y 0, security 0, hooks 0

## Conflits avec main

<liste ou "aucun">

## Recommandations

- Merger en squash (commits de boucle = bruit)
- Vérifier manuellement <zone X> avant push (mention si zone sensible touchée)

## Espace de travail

Mode : `<in-place | worktree>` — branche `<branch>` (base `<run_base_sha court>`)
Path : `<repo root | worktree path>`
```

Rappels (détail dans SKILL.md) :
- Mode `no_auto_commit` : ajouter la section **« Commit à exécuter manuellement »** (§5.1bis Mode 2) et formuler la mergeabilité « sous réserve du commit user ».
- Smoke LIVE partiellement bloqué (auth/creds) : le rapport liste explicitement ce qui a été vérifié live vs ce qui reste à confirmer côté user (§5.1b.5).
