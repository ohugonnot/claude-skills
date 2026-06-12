# Pack spécialiste — Go (1.21+)

Chargé à l'Étape 2bis si Go détecté (`go.mod`). Go est typé : le compilateur attrape les signatures hallucinées — **le vrai risque = les erreurs silencieuses qui compilent**. Sources : go.dev (blog/wiki/spec), 100go.co (100 Go Mistakes), golangci-lint, USENIX Security 2025 (hallucination de packages).

## 0. Discipline de version (avant tout)

- **Lire la directive `go` de `go.mod`** : la capture de variable de boucle a changé en **Go 1.22** (chaque itération = sa copie). Module `go 1.21` ou moins → ancien comportement partagé → `v := v` requis avant `go func(){}` et `tc := tc` dans les table-tests parallèles. Module 1.22+ → ces lignes sont du bruit. Ne pas deviner : lire.
- Packages : **~20 % des packages recommandés par les LLM n'existent pas** (USENIX 2025, 16 modèles) — tout nouvel import hors stdlib se vérifie (`go list -m`, pkg.go.dev) avant usage ; risque maximal sur les libs basse fréquence (SDKs, ORMs de niche).

## 1. Invariants IMPL

**Concurrence**
- Goroutine = jamais lancée sans savoir comment elle s'ARRÊTE (context, canal fermé). Les goroutines ne sont pas GC-ées.
- `defer cancel()` sur la ligne qui suit TOUT `context.WithTimeout/WithCancel/WithDeadline` (même si le timeout expire seul). `context.Background()` à la racine uniquement — jamais au milieu d'une chaîne (casse la propagation d'annulation). Pas de dépendances/valeurs métier dans `context.WithValue`.
- `wg.Add(1)` AVANT le `go func()`, jamais dedans. Pas de copie de types `sync` (Mutex, WaitGroup) après usage. `select` + `default` dans une boucle = spin 100 % CPU.
- `http.DefaultClient` n'a **aucun timeout** — toujours `http.NewRequestWithContext` + timeout, ou un client configuré.

**Slices / maps / nil**
- `append` sur une sous-slice avec capacité restante **écrase le parent** (backing array partagé) — `s[:n:n]` (3-index) pour couper la capacité. Une sous-slice retient tout le backing array (fuite) → `copy` pour détacher.
- `var m map[K]V` : lisible (zéro), **panique à l'écriture** — `make()` obligatoire. Itération de map non déterministe par design (un test qui dépend de l'ordre passe 9 fois sur 10).
- **Typed nil** : `var e *MyErr = nil; return e` dans une fonction retournant `error` → l'interface est NON-nil (`err != nil` vrai). Retourner le littéral `nil`.

**Erreurs**
- `%w` = l'erreur wrappée devient contractuelle (`errors.Is/As` la voient) ; `%v` la masque. Jamais `==` sur des erreurs potentiellement wrappées → `errors.Is`.
- Shadowing : `if v, err := f(); …` crée un `err` LOCAL — le `err` du scope parent reste intact (bug silencieux classique).
- `defer` en boucle = ressources accumulées jusqu'au retour de la FONCTION → extraire le corps en fonction. `defer` peut muter les retours nommés (intentionnel pour wrapper, accidentel sinon).

## 2. Invariants TESTS

- Table-driven (`[]struct{name string; …}` + `t.Run(tc.name, …)`), `t.Errorf` avec `got`/`want` (pas `Fatalf` qui masque les cas suivants). `tc := tc` si module < 1.22 et `t.Parallel()`.
- **`-race` au gate, avec `-count=1`** (le cache de test ne re-détecte pas les races).
- **Frontières exactes** : tester la valeur pivot, pas seulement les côtés (un test de pagination « dernière page partielle » ne distingue pas `>` de `>=` — il faut le cas dernière-page-PLEINE). Généralisable à tout seuil.
- Red-check/mutation : `gremlins` ou mutation manuelle ciblée + relance du paquet seul (`go test ./pkg/...`) — rapide grâce à la compilation incrémentale.
- Doublures : horloge injectée (pas de `time.Now()` dans la logique testée), pas de `time.Sleep` pour « attendre » une goroutine (synchroniser par canal).

## 3. Checklist REVIEW

- Chaque `go func()` : qui l'arrête ? qui collecte son erreur ? (une goroutine qui `panic` tue le process).
- Chaque `(val, err :=)` : `err` consommé ? `_` sur une erreur = à justifier explicitement. Erreur gérée DEUX fois (loggée ET retournée) = anti-pattern.
- `resp.Body` fermé (et drainé si réutilisation de connexion) après chaque appel HTTP.
- Accès concurrents : append/map partagés entre goroutines sans mutex/canal ; la review demande « quel test -race couvre ce chemin ? ».
- Pagination/offsets : cf. frontières exactes (§2) — vérifier le pivot, ET la **cohérence count↔rows** : un `COUNT`/total SQL calculé AVANT un filtre appliqué dans le mapping Go (`continue`, dédup) est gonflé — pages courtes, « suivant » actif à tort. Tracer total ET lignes jusqu'à l'UI. Granularité : un `NOT EXISTS`/`WHERE` par-ligne jointe ≠ intention par-entité (multi-items même clé).
- API tierce : la sémantique d'un champ se vérifie sur un ARTEFACT RÉEL (dump, XML, réponse), pas sur son nom — les noms mentent.

## 4. Gate objectif Go

```bash
gofmt -l .                          # sortie vide attendue
go vet ./...                        # loopclosure, lostcancel, copylocks, printf, httpresponse…
go test -race -count=1 ./...
golangci-lint run ./...             # + activer : shadow, nilerr, bodyclose, contextcheck, tparallel
govulncheck ./...                   # CVE des dépendances
```

## 5. Anti-hallucination LLM × Go

1. **Packages inventés** (~20 % — slopsquatting documenté) : vérifier l'existence de tout import non-stdlib.
2. **Patterns d'autres langages transposés** : `_` sur les erreurs (réflexe Python), exceptions simulées, getters/setters inutiles.
3. **`v := v` cargo-culté ou manquant** selon la version du module (cf. §0) — lire go.mod.
4. **Code concurrent « plausible »** qui compile et passe les tests single-thread : exiger `-race` + un test qui exerce réellement la concurrence.
5. **`%v` par défaut sur les erreurs** quand l'appelant a besoin d'`errors.Is` : choisir `%w`/`%v` consciemment (contrat d'API).
