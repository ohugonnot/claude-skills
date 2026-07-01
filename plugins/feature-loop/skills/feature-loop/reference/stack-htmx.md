# Pack spécialiste — HTMX (1.x / 2.x)

Chargé à l'Étape 2bis si HTMX détecté (script htmx.org dans les templates, attributs `hx-*`). HTMX = API **basse fréquence** dans les training data → taux d'hallucination d'attributs maximal (corrélation fréquence/hallucination documentée, cf. études du pack). Sources : htmx.org/docs + /reference + migration guide + issues GitHub sourcées.

## 0. Discipline de version (avant tout)

- **Identifier 1.x vs 2.x** (le script chargé fait foi). Changements de défauts silencieux en 2.x : `selfRequestsOnly` true, `scrollBehavior` instant, **DELETE passe ses params en query string** (plus dans le body — un backend qui lit le body DELETE ne reçoit rien), `hx-sse`/`hx-ws` sortis du core (extensions).
- `hx-on` : syntaxe 2.x = `hx-on:htmx:before-request="…"` — **kebab-case OBLIGATOIRE** (le DOM lowercase les attributs : `beforeRequest` ne matchera jamais). L'ancienne syntaxe 1.x (`hx-on="event: code"`) est dépréciée et les deux ne coexistent pas sur un même élément.

## 1. Invariants IMPL

- **Attributs souvent hallucinés — n'existent PAS** : `hx-swap="replace|append|prepend"` (c'est `outerHTML`/`beforeend`/`afterbegin`), `hx-trigger="hover"` (c'est `mouseenter`), modifier `.prevent` (utiliser `hx-on:click="event.preventDefault()"`). Valeurs réelles de `hx-swap` : `innerHTML` (défaut), `outerHTML`, `afterbegin`, `beforebegin`, `beforeend`, `afterend`, `delete`, `none`, `textContent` (2.x — remplace le contenu sans parser le HTML de la réponse, utile si la réponse n'est pas censée être du HTML) (+ modifiers `swap:`/`settle:`/`scroll:`/`show:`/`focus-scroll:`).
- **Cycle de vie au swap** : tout listener attaché DIRECTEMENT à un élément swappé est perdu. JS toujours en **délégation sur `document.body`** (ou `htmx.onLoad()` pour initialiser des libs tierces sur le contenu inséré ; `hx-preserve` + id stable pour les widgets stateful). HTML injecté par du JS tiers → `htmx.process(el)`.
- **GET ne sérialise PAS le form** : seule la valeur de l'élément déclencheur part (contrairement aux non-GET qui embarquent le form parent). D'où `hx-include` — dont les sélecteurs `find`/`closest` s'évaluent depuis l'ÉLÉMENT DÉCLENCHEUR, pas depuis le porteur de l'attribut ; et qui ignore les inputs `disabled` (utiliser `readonly`).
- **4xx/5xx ne swappent PAS par défaut** (la page reste figée, event `htmx:responseError`). Pour swapper un 422 de validation : `htmx.config.responseHandling` (2.x) ou header `HX-Reswap` côté serveur.
- **Historique** : `hx-push-url` snapshotte le DOM en localStorage. Réponse fragment vs full-page → servir selon le header `HX-Request` ET poser **`Vary: HX-Request`** (sinon le cache HTTP sert un fragment nu au hard-refresh). Données sensibles → `hx-history="false"`.
- Headers de réponse utiles (réels) : `HX-Redirect`, `HX-Location`, `HX-Refresh`, `HX-Retarget`, `HX-Reswap`, `HX-Reselect` (choisit quelle portion de la réponse swapper, indépendamment de `hx-select` côté client), `HX-Trigger[-After-Swap|-After-Settle]`, `HX-Push-Url`/`HX-Replace-Url`.
- OOB swaps (`hx-swap-oob`) : matcher par id — **sans `id` sur l'élément cible, le swap est ignoré SILENCIEUSEMENT** (pas d'erreur console) ; envelopper `<tr>/<td>/<li>` dans `<template>` (sinon le parseur navigateur les corrige).
- Cross-domain légitime malgré `selfRequestsOnly` (2.x, défaut `true`) : hook `htmx:validateUrl` pour autoriser explicitement des domaines de confiance — ne pas désactiver `selfRequestsOnly` globalement pour un besoin ponctuel.

## 2. Invariants TESTS

- Deux couches : **intégration backend** (requête avec header `HX-Request: true` → asserter le FRAGMENT) pour la logique, **e2e navigateur** (Playwright) pour les flux critiques seulement (swaps réels, historique). Les e2e htmx sont flaky sur le timing (swap/settle delays) — pas de sleep, attendre des états DOM.
- **Piège : tester le fragment ≠ tester le swap.** Un fragment correct peut être swappé au mauvais endroit (`hx-target`/`hx-swap` faux) — au moins un e2e par interaction valide l'insertion réelle.
- Tester la page COMPLÈTE (sans header HX-Request) en plus du fragment : c'est elle qu'on reçoit au refresh/bookmark.
- Paramètres périmés (le piège `page` au changement de filtre) : vérifier ce que `hx-include` embarque réellement — l'absence d'un champ dans la zone incluse vaut remise à zéro côté serveur (pattern robuste).

## 3. Checklist REVIEW

- Tout `addEventListener` sur un élément situé dans une zone swappée = bug différé. Chercher les bind directs dans les scripts des templates.
- Contenu utilisateur dans un attribut `hx-on:*`, `hx-vals='js:…'`, `hx-headers='js:…'`, ou filtre `hx-trigger="click[…]"` = **XSS par eval** (ces attributs évaluent du JS). L'auto-échappement HTML du template ne suffit pas dans ces contextes. `hx-disable` est contournable (injection hors de la balise, meta htmx-config) — ne pas s'y fier seul.
- CSP : `hx-on`/filtres/`js:` exigent `unsafe-eval` — incompatibles avec une CSP stricte ; vérifier la cohérence du choix projet. `inlineScriptNonce` htmx annule la protection des nonces (il nonce TOUT script de réponse).
- Endpoint qui sert un fragment : renvoie-t-il la full-page sans `HX-Request` + `Vary: HX-Request` ?
- Erreurs serveur : l'UI a-t-elle un feedback sur `htmx:responseError`, ou l'échec est-il silencieux pour l'utilisateur ?

## 4. Gate objectif

Pas de linter HTMX : le gate = tests d'intégration sur fragments + e2e Playwright + **grep des hallucinations** (`grep -rn 'hx-swap="\(replace\|append\|prepend\)"\|hx-trigger="hover"\|hx-on="' templates/` doit être vide).

## 5. Anti-hallucination LLM × HTMX

1. **Attributs/valeurs inventés** (cf. §1) — toujours vérifiables contre htmx.org/reference ; en cas de doute, WebFetch la référence plutôt que deviner.
2. **Confusion 1.x/2.x** (syntaxe hx-on, params DELETE, extensions) — identifier la version AVANT d'écrire.
3. **Code « démo » qui bind directement les éléments** — marche au premier rendu, meurt au premier swap : le bug n'apparaît qu'en exerçant l'interaction DEUX fois (à tester ainsi).
4. **Oubli du chemin non-htmx** (hard refresh, bookmark, history restore) — chaque URL pushée doit servir une page complète.
