# Pack spécialiste — JavaScript navigateur (vanilla, ES2020+)

Chargé à l'Étape 2bis si du JS front sans framework est touché (scripts inline de templates serveur, modules ES, pas de React/Vue). JS = API haute fréquence (peu d'hallucinations de méthodes) mais **champion des erreurs silencieuses** : pas de compilateur, le code « plausible » casse en edge case sans bruit (Willison : « le vrai risque, ce sont les erreurs qu'aucun interpréteur n'attrape »). Sources : MDN, CodeHalu (arXiv 2405.00253), retours sourcés.

## 1. Invariants IMPL

**Async — la première source d'erreurs silencieuses**
- `await` dans `forEach` **ne marche pas** (le callback async est abandonné) → `for…of` (séquentiel) ou `Promise.all(arr.map(…))` (parallèle).
- `fetch` ne rejette QUE sur erreur réseau : **un 404/500 résout normalement** — toujours vérifier `response.ok` avant `.json()` (le pattern LLM `fetch(u).then(r => r.json())` parse le body d'erreur comme un succès).
- Toute promesse a un propriétaire : un `await` sans try/catch ni un `.catch()` = rejet non géré (UI dans un état indéfini, crash en Node 15+).
- Réponses out-of-order (recherche en tapant, double-clic) : `AbortController` pour annuler la requête précédente, ou comparaison d'un id de requête monotone avant d'appliquer le résultat.
- `Promise.all` = fail-fast ; tâches indépendantes dont on veut les résultats partiels → `allSettled`.

**Unicode / locale (sur tout site francophone)**
- Comparaison/recherche accent-insensible : **normaliser des DEUX côtés** — `s.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase()`. « é » composé ≠ « é » décomposé pour `===`, et un lowercase fait côté serveur (PHP `strtolower` non-Unicode) ne matche pas `toLowerCase()` JS.
- Tri français : `Intl.Collator('fr', {sensitivity:'base'})` (le `.sort()` par défaut trie par octets — accents à la fin). Instancier le Collator UNE fois.
- `.length` compte les code units, pas les caractères (émojis, décomposés) — `Intl.Segmenter` si ça compte.

**Types / DOM / état**
- `===` partout ; seule exception idiomatique : `x == null` (couvre null+undefined). `Number.isNaN()` (pas le global). `parseInt(s, 10)`.
- `dataset.*` retourne TOUJOURS une string (`el.dataset.active === true` est toujours faux) — convertir explicitement.
- `innerHTML` + donnée utilisateur = XSS → `textContent`/`createElement` ; partie dynamique d'un sélecteur → `CSS.escape()`.
- Listeners : **délégation sur un ancêtre stable** pour tout élément susceptible d'être recréé (re-render, swap HTMX) ; jamais de listener anonyme qu'on devra retirer.
- `{...obj}` = clone SHALLOW (le nested reste partagé) ; `const` n'immobilise que la liaison ; un module ES = singleton (son état racine est partagé entre tous les importeurs).
- Dates : mois **0-indexés**, overflow silencieux (`new Date(2024, 12, 1)` = janv. 2025), parsing fiable = ISO 8601 uniquement. Flottants : pas d'argent en float (centimes entiers) ; `toFixed` arrondit sur la représentation binaire (`(1.015).toFixed(2)` → "1.01").

## 2. Invariants TESTS

- Frontière unitaire/e2e : logique pure (parsing, formatage, calcul) extraite en module → testable en Node ; tout ce qui touche au rendu réel, events, CSS → **Playwright** (JSDOM n'a pas ~20 % des Web APIs : `transitionend` jamais émis, custom properties non résolues — un vert JSDOM peut être cassé en navigateur).
- JS inline de templates serveur : extraire la logique en fonctions/modules testables ; le résidu inline se teste via Playwright (`page.evaluate` + assertions DOM), jamais en comparant la string du script.
- Red-check : un test DOM peut être vert parce que le sélecteur ne matche RIEN (silencieux) — muter la logique et vérifier que le test rougit ; asserter aussi que l'élément ciblé EXISTE avant d'asserter son état.
- Cas de test accents/Unicode systématiques sur toute fonction de recherche/tri/comparaison (« É », « œ », chaîne décomposée).

## 3. Checklist REVIEW

- Chaque `fetch` : `response.ok` vérifié ? erreur réseau gérée ? résultat appliqué après un await peut-il être périmé (race UI) ?
- Chaque `addEventListener` : l'élément peut-il être recréé (l'écouteur meurt) ? le listener est-il retirable si besoin ?
- Toute comparaison/recherche de chaînes : Unicode-safe des deux côtés ? (le mismatch serveur-lowercase / client-toLowerCase est un bug réel vécu)
- Donnée utilisateur → `innerHTML`/attribut JS-évalué ? (XSS)
- Variable affectée sans déclaration (global implicite hors strict mode) ; mutation d'un objet partagé via spread shallow.
- Code async « démo » : que se passe-t-il au double-clic ? pendant le vol de la requête ? si elle échoue ?

## 4. Gate objectif

Si outillé : `eslint` (avec `eqeqeq`, `no-undef`, `no-floating-promises` si dispo via TS-eslint), `tsc --checkJs` si jsconfig. Sinon (JS inline de templates serveur) : la CI e2e est le gate + grep ciblés (`== ` vs `===`, `innerHTML =`, `forEach(async`).

## 5. Anti-hallucination LLM × JS

1. **Le code plausible** : bonnes variables, bons commentaires, faux en edge case (CodeHalu : « syntaxically correct, semantically plausible, fails ») — c'est la review + les cas limites qui l'attrapent, pas la lecture.
2. **`fetch` sans `response.ok`** — quasi systématique en génération naïve.
3. **`forEach(async …)`** — pattern généré très fréquemment, jamais correct.
4. **Conversions implicites** (`+x`, `==`, dataset non converti) héritées d'exemples de training laxistes.
5. **Globals implicites** (oubli de `let/const` dans un script non-module) — vert en démo, collision en prod.
