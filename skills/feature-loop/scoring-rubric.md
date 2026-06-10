# Scoring Rubric — Feature Loop (V8)

Référentiel pour noter une feature sur 0-10 par axe. Chargé par l'agent **reviewer** (≠ auteur du code, ≠ auteur des tests) avant d'évaluer. Reviewer = Sonnet par défaut, Opus si complexe/sensible (cf. SKILL.md §4.6).

> **Voir aussi la section « V8 — Ajouts » en fin de fichier** : anti-biais du juge (sources), champs JSON `confidence`/`adversarial_test`, packs d'axes conditionnels (sécurité/OWASP, user-facing UX/UI/i18n/SEO/CTA), et red-check. Les axes ci-dessous (standards + front + sécu/perf/observabilité) restent la base.

## Règles globales de notation

- **Preuve obligatoire** : tout score < 10 doit citer `file:line — raison concise`. Aucune critique vague.
- **Sois exigeant** : si tu vois quelque chose à dire, note ≤ 8 et explique. Ne mets pas 9 par défaut.
- **Compare au précédent** : si itération N>1, score relatif à l'amélioration depuis itération précédente.
- **Score 0** auto-déclenché si une métrique objective critique échoue (build, typecheck).
- **Un seul ordre d'évaluation** : lis le code → consulte les métriques → regarde les screenshots → note. Ne note pas avant d'avoir tout vu.

## Format de réponse (JSON strict)

```json
{
  "scope": "backend|frontend|fullstack",
  "scores": {
    "<axe>": {
      "value": 8,
      "evidence": "src/foo.ts:42-58 — fonction parseInput claire ; src/bar.ts:120 — variable `d` peu explicite"
    }
  },
  "criticals": [
    {
      "axis": "sécurité",
      "issue": "Injection SQL via paramètre `id` non sanitisé",
      "file": "src/api/user.ts:34",
      "fix_approach": "Utiliser query parameterized via le client ORM existant",
      "adversarial_test": "GET /api/user?id=1 OR 1=1 → ne doit PAS retourner toutes les lignes"
    }
  ],
  "majors": [{ "axis": "...", "issue": "...", "file": "...", "fix_approach": "...", "adversarial_test": "..." }],
  "minors": [{ "axis": "...", "issue": "...", "file": "...", "fix_approach": "..." }],
  "summary": "1-2 phrases : qu'est-ce qui est bon, qu'est-ce qui bloque",
  "regression_from_previous": ["axe1", "axe2"],
  "notes_for_implementer": "2-4 conseils de direction pour le prochain tour : patterns du projet ratés, contexte manquant, pièges. PAS de code, juste l'orientation."
}
```

`regression_from_previous` est vide si pas de régression ou si itération 1.

`notes_for_implementer` est lu par le Sonnet du tour suivant. Exemples :
- "Tu as oublié de regarder `src/lib/forms.ts` qui a un pattern Form établi — réutilise-le au lieu d'inventer"
- "Les états loading/empty/error sont gérés via un composant `<DataState>` existant dans `src/ui/` — utilise-le"
- "Le projet a un système de toast pour le feedback, pas d'alert() — voir `src/ui/toast.ts`"

## Règles de citation des preuves (anti-hallucination)

CHAQUE `evidence` et chaque `file` dans criticals/majors/minors DOIT pointer sur :
- Un fichier qui existe RÉELLEMENT dans le worktree (vérifié post-review)
- Une ligne (ou plage) dans les bornes du fichier
- Pour les critiques : une ligne qui est dans le diff de l'itération (pas du legacy)

Le skill VÉRIFIE ces refs après la review. Si > 30% sont invalides, la review est relancée. Donc : si tu n'es pas sûr du file:line exact, mieux vaut être imprécis que d'inventer — utilise `<file>` sans ligne, ou `<file>:?` avec point d'interrogation.

---

## Axes — Backend / Logique générale

### Lisibilité
| Score | Critères |
|---|---|
| 10 | Noms explicites partout, fonctions courtes (<30 lignes), pas de magic numbers, intentions claires sans commentaires superflus |
| 8 | Globalement clair, quelques zones perfectibles (un commentaire manquant sur logique non triviale) |
| 6 | Compréhensible mais demande de l'effort, noms ambigus ponctuels |
| 4 | Nécessite de relire plusieurs fois, abréviations cryptiques, fonctions trop longues |
| 2 | Très difficile à suivre |
| 0 | Illisible |

Anti-patterns à pénaliser : `data`, `info`, `temp`, `tmp`, `i`/`j` hors itérateur de boucle, fonctions > 80 lignes, nesting > 4 niveaux, commentaires qui paraphrasent le code.

### Robustesse
| Score | Critères |
|---|---|
| 10 | Tous edge cases gérés, erreurs typées + wrappées avec contexte, pas de panic possible, tests couvrent failure paths |
| 8 | Edge cases principaux couverts, erreurs propagées correctement |
| 6 | Happy path solide, quelques edge cases non gérés |
| 4 | Erreurs ignorées ou mal propagées, hypothèses non vérifiées |
| 0 | Build/lint/typecheck/tests échouent (auto-fail) |

Checklist : `try/catch` sans contexte, `unwrap()`/`!` sans justification, parsing sans validation, `any` injustifié (TS), `panic` sur erreur normale (Go), promises non-`await`/non-catchées.

### Modularité
| Score | Critères |
|---|---|
| 10 | SRP respecté, dépendances inversées (DI), composants testables isolément, frontières claires |
| 8 | Structure claire, séparation logique propre |
| 6 | Modules un peu trop gros mais OK |
| 4 | Couplage fort, side effects partout |
| 0 | Monolithique non testable |

Vérifier : un composant ne dépend pas directement d'un store global s'il pourrait recevoir via prop ; les fonctions pures sont séparées des fonctions à side effect.

### Simplicité
| Score | Critères |
|---|---|
| 10 | Aussi simple que possible, pas d'abstraction prématurée, code direct |
| 8 | 1-2 abstractions justifiées |
| 6 | Quelques sur-abstractions |
| 4 | Architecture lourde pour un besoin simple |
| 0 | Sur-ingénierie massive |

Red flags : struct juste pour grouper des fonctions, interface à 1 implémentation, factory pour 1 type, abstraction "au cas où".

### YAGNI
| Score | Critères |
|---|---|
| 10 | 0 feature non demandée, 0 paramètre optionnel inutilisé, 0 hook pour l'avenir |
| 8 | 1-2 extensions minimes justifiables |
| 6 | Quelques options "au cas où" |
| 4 | Nombreuses features non demandées |
| 0 | Refonte massive non demandée |

### Tests
| Score | Critères |
|---|---|
| 10 | Couverture complète (happy + edge + erreurs + e2e si front), tests rapides, lisibles, indépendants |
| 8 | Happy path + principaux edge cases + tests d'erreur |
| 6 | Tests présents mais incomplets (manque erreurs ou edge cases) |
| 4 | Tests symboliques (assert true, expect.anything) |
| 2 | Aucun test alors que framework existe dans le projet |
| 0 | Aucun test alors qu'il en faut absolument |

Vérifier : tests indépendants (pas d'ordre), pas de mock excessif, assertions précises (pas `toBeTruthy()` sur ce qui pourrait être strict), structure AAA lisible (Arrange/Act/Assert séparés, une action par test), équilibrage pyramidal (unitaires nombreux, intégration ciblée, e2e rares — pénaliser un e2e qui duplique un unitaire), non-déterminisme doublé (horloge/réseau/aléa injectés, pas de sleep ni de flaky masqué).

**Principe anti-sur-ingénierie sur cet axe** (très important — appris d'un run réel où viser le "test idéal" a fait dériver vers du parser custom inutile) :

> **Test minimum viable du vrai bug** > test idéal théorique.
>
> Avant de marquer un test comme insuffisant, demande-toi : ce test attrape-t-il **concrètement** le bug qu'on veut empêcher ? Si oui, c'est suffisant — note ≥ 8.
>
> Le coût d'un test (lignes, complexité, maintenance) doit être proportionnel au risque qu'il couvre. Un test simple qui attrape 95% des cas vaut mieux qu'un test sophistiqué qui attrape 99% au prix de 5× plus de code et de fragilité.
>
> Un méta-test (test qui réimplémente l'algorithme qu'il teste, ou qui teste un private en duplication de l'API) = faux confort, à pénaliser explicitement comme **anti-pattern** (axe simplicité/YAGNI/tests tous descendent).

### Sécurité (si activé)
| Score | Critères |
|---|---|
| 10 | Inputs validés au boundary, pas de string concat SQL/shell, secrets pas en clair, auth/authz appliquée, CSRF/XSS prévenus |
| 8 | Sécurité globalement OK, quelques validations manquantes côté défense en profondeur |
| 6 | Risques mineurs identifiés (logs verbeux, error leaks) |
| 4 | Vulnérabilités exploitables (injection, IDOR) |
| 0 | Injection / secret leak évident |

Checklist OWASP minimum : injection (SQL, command, prompt), auth broken, sensitive data exposure, XXE, broken access control, security misconfig, XSS, deserialization, vulnerable deps, insufficient logging.

### Performance (si activé)
| Score | Critères |
|---|---|
| 10 | Pas de N+1, requêtes paginées/indexées, pas de re-render inutile, bundle size optimisé |
| 8 | Performance correcte, quelques optimisations possibles |
| 6 | Risque de lenteur sur gros volumes |
| 4 | N+1 ou requêtes lourdes évidentes |
| 0 | Inutilisable à l'échelle |

Front : `useMemo`/`useCallback` quand justifié, pas de re-render cascading, lazy loading, image optim. Back : index DB, batching, pagination, cache cohérent.

### Observabilité (si activé)
| Score | Critères |
|---|---|
| 10 | Logs structurés contextuels, métriques pertinentes, erreurs trackées, niveaux de log adaptés |
| 8 | Logging utile sur chemins critiques |
| 6 | Logs présents mais pauvres en contexte |
| 4 | `console.log` ou logs non structurés |
| 0 | Aucune visibilité |

---

## Axes — Frontend (en plus de lisibilité/robustesse/etc.)

### UX/UI
| Score | Critères |
|---|---|
| 10 | Hiérarchie visuelle claire, feedback sur toutes actions, états (loading/empty/error/disabled) gérés, copy concise et utile |
| 8 | UX solide, quelques détails manquants (1 état non géré, micro-friction) |
| 6 | Fonctionnel mais peu polished |
| 4 | Friction utilisateur évidente (pas de feedback, états manquants) |
| 0 | Inutilisable |

Vérifier sur screenshots : alignement, espacement consistant, hiérarchie typographique (h1>h2>body), états visibles. Sur le code : présence des états loading/empty/error.

### Contraste (WCAG)
| Score | Critères |
|---|---|
| 10 | WCAG AAA partout (7:1 texte normal, 4.5:1 large) |
| 8 | WCAG AA partout (4.5:1 normal, 3:1 large) |
| 6 | AA sur l'essentiel, manques sur texte secondaire ou états disabled |
| 4 | Sous AA sur du texte important |
| 0 | Texte illisible |

Vérifier sur screenshots — estimer le ratio à l'œil sur les textes principaux. Pénaliser le gris-sur-gris pour le texte body.

### Aéré (espacement)
| Score | Critères |
|---|---|
| 10 | Grille cohérente, padding/margin suit un système (4/8/16/24/32), respirations entre sections, densité adaptée au contexte |
| 8 | Espacement cohérent, quelques densités à revoir |
| 6 | Un peu serré ou un peu vide ponctuellement |
| 4 | Étouffant ou désorganisé |
| 0 | Illisible visuellement |

### Responsive
| Score | Critères |
|---|---|
| 10 | Parfait sur mobile (375px), tablet (768px), desktop (1440px+), pas de scroll horizontal, breakpoints justifiés, touch targets ≥ 44px |
| 8 | Fonctionne sur tous viewports, quelques détails à mobile (texte un peu serré, bouton un peu petit) |
| 6 | Un viewport moins bien traité |
| 4 | Casse sur mobile (overflow, illisible) |
| 0 | Utilisable seulement sur desktop |

**Vérifier sur les 3 screenshots multi-viewports.** C'est l'axe le plus visuel — ne note pas sans avoir vu les images.

### Doc utilisateur
| Score | Critères |
|---|---|
| 10 | Labels clairs, placeholders utiles, tooltips où nécessaire, messages d'erreur actionnables ("Format invalide" → "L'email doit contenir @"), empty states informatifs |
| 8 | Majoritairement clair |
| 6 | Quelques labels ambigus, erreurs génériques |
| 4 | Messages d'erreur peu utiles, pas de guidance |
| 0 | Aucune guidance, formulaires nus |

### Accessibilité (si activé)
| Score | Critères |
|---|---|
| 10 | ARIA correct (uniquement quand HTML sémantique insuffisant), navigation clavier complète, focus visible et logique, alt sur images informatives, alt="" sur décoratives, semantic HTML, labels associés aux inputs |
| 8 | ARIA essentiel + clavier OK + focus visible |
| 6 | Semantic HTML mais ARIA manquant pour widgets custom |
| 4 | Navigation clavier cassée ou focus invisible |
| 0 | Non utilisable au clavier ou screen reader |

Checklist : `<button>` vs `<div onClick>`, `<label htmlFor>` vs placeholder seul, `aria-live` pour notifications dynamiques, `aria-expanded` sur disclosures, `role="dialog"` + focus trap pour modals, skip link en haut de page.

---

## Heuristiques anti-biais pour le reviewer

- **Si tout est à 9-10 du premier coup** : tu es probablement indulgent. Re-regarde les axes à 9-10 avec un œil critique.
- **Si rien n'est en critical mais le code est de qualité moyenne** : tu sous-classifies. Un endpoint sans validation d'input est critical (sécurité), pas major.
- **Si tu utilises "globalement", "majoritairement", "plutôt"** : sois plus précis. Cite l'exception, n'enrobe pas.
- **Si tu hésites entre N et N+1** : prends N (le plus bas). Force l'amélioration.
- **Si l'agent précédent a déjà fixé une critique et tu en trouves une nouvelle similaire** : note que c'est récurrent, ça vaut souvent un major même si individuellement minor.

## DA paranoid — patterns à chercher (calibration par exemples observés)

Quand le devil's advocate est activé (mode paranoid sur keywords sensibles), il doit chercher activement les patterns qui **échappent à une review classique** parce qu'ils nécessitent de raisonner sur des interactions entre composants, pas sur le diff seul. Voici des **exemples concrets** observés sur des runs réels, à utiliser comme calibration :

### Patterns d'interaction multi-scope

- **EAV cross-scope leak** : un calcul/insert sur scope A (ex: questionnaire annexe) qui pollue scope B (questionnaire main) parce que la clé scope est `NULL` au lieu d'être fixée. Réflexe DA : pour chaque insert/update EAV ou similaire, **vérifier le scope est explicite**, pas implicite.
- **Race TOCTOU silencieuse** : check d'autorisation/état au début, traitement long (parsing, validations), flush à la fin sans re-check. Réflexe DA : entre `denyAccessUnlessGranted` (ou équivalent) et `em->flush()`/`commit`, regarder si un acteur concurrent peut **changer l'invariant** vérifié initialement.

### Patterns d'identifiant/nommage

- **Bypass voter/policy via shadowing de nom** : un user peut nommer une entité utilisateur (CALC, variable, label) avec un nom **réservé** au système (ex: `rec_status`, `admin`, `is_active`). Le code legacy fait `if name == 'admin'` sans whitelist explicite des sources légitimes. Réflexe DA : **toute logique basée sur un nom user-fourni** doit avoir une whitelist de sources système OU rejeter les noms réservés à la création.
- **Token clair leaké via debug/log/audit** : un token sensible (reset password, API key, session) qui se retrouve dumpé par `var_dump`/`__toString`/Sentry/profiler/audit Loggable. Réflexe DA : pour tout objet portant un secret, **vérifier `__debugInfo()` ou équivalent** qui le masque, ET vérifier que les listeners Loggable/audit ne le persistent pas en clair.

### Patterns de sécurité standards (à ne pas oublier)

- **Énumération par timing** : `if (user_exists) { hash_password } else { return null }` → différence de latence ~50ms signale l'existence de l'user. Réflexe : `usleep` aligné dans la branche null OU queue async normalisant.
- **Énumération par status HTTP** : `404 si user inconnu / 200 si email envoyé` → leak. Réflexe : status neutre uniforme.
- **CSRF absent sur form mutateur** : `POST` sans token CSRF = vulnérable. Réflexe : présence systématique du token, validation effective côté serveur (pas juste champ caché).
- **Rate limiter sans bucket sain** : `rate_limit_by(email)` sans skip si email vide → tous les requests sans email collapsent sur bucket `''` = DoS sur ce bucket.
- **Validation d'input partielle** : validation au form (Symfony Form) sans validation en service direct (programmatic call) → bypass via API/cmd interne.

### Patterns de robustesse cross-platform

- **DDL atomique PG vs auto-commit MariaDB** : `ALTER TABLE` transactionnel sur PG mais auto-commit sur MariaDB → fenêtre où la contrainte n'existe plus en prod MariaDB.
- **UK partial (`WHERE col IS NULL`) PG vs MariaDB** : MariaDB < 8.0 ne supporte pas les UK partial → asymétrie : ce qui est exclu de l'UK en PG est bloquant en MariaDB (ex: soft-deleted avec email réutilisé). Réflexe : si la migration utilise un UK partial, **documenter l'asymétrie** ou compenser applicativement.
- **DDL bi-platform** : `instanceof PostgreSQLPlatform` → sinon code PG-only échoue silencieusement sur MariaDB (ou inversement).

### Patterns d'atomicité

- **Atomicité changePassword + audit log** : si l'un flush et l'autre échoue, état incohérent. Réflexe : `wrapInTransaction` englobant les 2.
- **Nested transactions Doctrine** : `wrapInTransaction` imbriqué = savepoints automatiques. Si l'inner rollback, l'outer décide. Vérifier que les rollback se propagent correctement.

**Règle d'or DA** : si tu trouves un major sur un de ces patterns, c'est probablement un **vrai bug en prod**, pas un faux positif. Si tu n'en trouves aucun sur du code paranoid (auth/payment/etc.), tu as probablement raté quelque chose — re-passe en mode adversaire.

---

# V8 — Ajouts (lire en complément des axes ci-dessus)

## Anti-biais du juge (fondé sur la recherche LLM-as-judge)

Le reviewer est un agent DISTINCT de l'auteur du code et des tests (self-preference bias prouvé : un modèle qui se juge se surnote, discrimination ~52 % = quasi-hasard — Zheng 2023, Panickssery 2024). En plus, respecter :

- **Anti-verbosity** : ne JAMAIS récompenser la longueur. Plus court à valeur égale = meilleur. La sur-ingénierie est un défaut (axe Simplicité/YAGNI), pas une qualité. (Les juges LLM sur-notent les réponses longues — Zheng 2023.)
- **Anti-leniency / adversarial** : lister D'ABORD tout ce qui cloche, PUIS noter. Chercher le pire cas crédible, pas confirmer que « ça marche » (leniency/sycophancy bias).
- **CoT avant la note** : raisonner axe par axe (constat + file:line) avant de poser le chiffre (G-Eval : améliore l'accord avec l'humain).
- **En cas d'hésitation entre N et N+1 → prendre N** (le plus bas). Et baisser la `confidence` (ci-dessous) plutôt que bluffer.
- **Preuves vérifiées** : tout score < 10 cite un `file:line` réel ; > 30 % de refs invalides → review rejouée (anti-hallucination, déjà en place).

## Champs JSON ajoutés

En plus du format existant, chaque axe porte une **confiance**, et chaque finding un **test adversarial** :

```json
"axes": {
  "robustesse": {
    "value": 7,
    "confidence": 0.55,                         // 0-1 ; < 0.7 sur un axe décisif → 2e juge, < 0.4 → panel (SKILL §4.6c)
    "evidence": "src/bar.ts:88 — guard absent sur entrée vide",
    "issues": [{
      "severity": "major",
      "file": "src/bar.ts", "line": 88,
      "fix_approach": "minimal: 1 guard + 1 test sur l'entrée vide (~8 lignes)",
      "adversarial_test": "appeler foo('') → doit lever ValidationError, pas retourner null"
    }]
  }
},
"borderline_axes": ["robustesse"],   // axes dans [seuil−1 ; seuil+0.5] (seuil = --threshold, défaut 8) → candidats escalade
"needs_escalation": true             // vrai si borderline / confiance < 0.7 sur axe décisif / scope sensible sous seuil
```

- `confidence` : honnêteté du juge sur sa propre certitude. Confiance basse n'est PAS pénalisée — elle route vers un 2ᵉ juge/panel (SKILL §4.6c), c'est le but.
- `adversarial_test` : le test qui DÉMONTRE le finding. Sur scope sensible, le reviewer l'écrit réellement (XSS, entrée limite, contournement d'autorisation) — il est ajouté à la suite (pattern fresh-eyes d'outil-factory).
- `needs_escalation` : le skill déclenche l'escalade (panel) si vrai. Un axe **sécurité/auth/données sous le seuil ne se vote jamais à la hausse**.

## Pack d'axes « user-facing » (activer si la feature produit une UI/contenu vu par un utilisateur final)

N'activer que les axes pertinents — une route API n'en active aucun. Barèmes repris/adaptés d'outil-factory. (Les axes front UX/UI, contraste, aéré, responsive, doc-utilisateur, a11y sont déjà décrits plus haut ; ce pack ajoute la dimension produit.)

### i18n (si projet multilingue)
- 10 : 100 % traduit, persistance langue, placeholders/title dynamiques, traductions idiomatiques (pas du mot-à-mot)
- 8 : complet, localStorage, toutes les fonctions ; 6 : oublis (placeholders, libellés dynamiques) ; 4 : partiel ; 0 : hardcodé une langue

### Copywriting / wording (si la feature porte du texte utilisateur)
- 10 : orienté bénéfice, ton juste, verbes d'action, chaque mot pèse
- 8 : accrocheur ; 6 : correct mais générique/technique ; 4 : froid ; 0 : illisible

### SEO technique (si page web publique)
- 10 : title/meta/canonical/OG/Twitter/JSON-LD (WebApplication + FAQPage si pertinent) + contenu utile + H1-H2 propres
- 8 : tout sauf contenu un peu faible ; 6 : meta+OG+canonical de base ; 0 : juste un `<title>`

### CTA / conversion (UNIQUEMENT si la page a un objectif de conversion — rare en interne)
- 10 : CTA contextuel adapté au résultat + micro-copy rassurant + restart ; 6 : CTA générique ; 0 : aucun

> **« valeur vs concurrence »** : axe disponible seulement sur demande explicite (produit public comparable à des concurrents identifiés). Jamais d'office.

## Red-check (rappel — détail dans SKILL.md §4.5b)

Les tests marqués **critiques** par l'agent de tests (logique métier clé, sécurité) doivent passer le red-check : muter la ligne protégée → le test DOIT rougir → restaurer. Un test resté vert sur la version cassée est vacant → l'axe Tests plafonne à 6 et le test est renvoyé en réécriture. (76 % des tests LLM ratent ce critère fail-to-pass — TDD-Bench.)

## Sources (pour calibration du juge)
- Zheng et al. 2023 (MT-Bench) — position/verbosity/self-enhancement bias. · Panickssery et al. 2024 — les LLM reconnaissent et favorisent leur propre sortie. · Verga et al. 2024 (PoLL) — panel de petits juges > un gros juge, 7-8× moins cher. · Liu et al. 2023 (G-Eval) — CoT avant la note. · Huang et al. ICLR 2024 — l'auto-correction sans signal externe dégrade. · TDD-Bench Verified 2024 — fail-to-pass des tests LLM.
