# Pack spécialiste — Architecture CQRS / Event Sourcing

Pack d'**architecture** (indépendant du langage — se COMBINE avec un pack langage, ex. stack-golang.md). Chargé à l'Étape 2bis si l'archi est détectée (event store, dossiers commands/events/projections, `apply`/`when` sur agrégats). Sources : Greg Young, Fowler, Azure Architecture Center, event-driven.io (Dudycz), microservices.io.

## 1. Invariants IMPL

**Commandes**
- Une commande = **un seul agrégat** par transaction (frontière de cohérence). Cross-agrégat → saga, jamais un handler qui charge deux streams.
- Le handler décide sur l'état reconstruit de **l'agrégat**, JAMAIS sur une projection (elle peut être en retard — décision sur état périmé).
- Idempotence : dédup par command id (retry réseau = pas de double effet). Distinguer **rejet** (règle métier violée → AUCUN event, erreur métier) d'**échec** (technique → retry possible).

**Events**
- **Immuables, à jamais** : on ne corrige pas un event, on émet un **compensating event**. Le schéma évolue par tolérance de lecture / versioning / upcasting — jamais par réécriture du store.
- Nommés au **passé** (`OrderPlaced`) : un event au présent/impératif est une commande déguisée.
- Capturer l'**intention** (« 2 places réservées par X ») pas le delta d'état (« remaining=42 »). `FirstNameChanged`/`LastNameChanged` séparés = **property sourcing**, anti-pattern nommé.
- Ordre garanti par numéro de séquence du stream ; l'append porte l'**expected version** (optimistic concurrency) — conflit de version → recharger, ré-évaluer, ré-essayer (et distinguer conflit technique de conflit MÉTIER : deux events intercalés ne conflictent pas forcément).

**Rejouabilité — le cœur**
- `apply`/`when` = **mutation d'état PURE** : zéro I/O, zéro horloge (`time.Now()`), zéro random, zéro envoi. L'agrégat se reconstruit de ses events SEULS.
- **LE piège LLM n°1 de cette archi** : un side effect (email, webhook, commande) dans `apply` — fonctionne au premier passage, **rejoué à chaque replay/rebuild**. Les side effects vivent dans des reactors/subscribers post-persistance.
- Tout l'aléatoire/temporel se fige DANS l'event au moment de l'émission (l'event porte le timestamp, l'id généré…), jamais recalculé à l'apply.

**Projections**
- Éventuellement cohérentes : pas de lire-sa-propre-écriture garanti — l'UX doit l'assumer (retour optimiste, polling, ou lecture du write model pour la confirmation immédiate).
- **Idempotentes** (livraison at-least-once) : upsert par event id ou checkpoint de position — un event rejoué ne double ni ligne ni compteur.
- Reconstructibles from scratch (donnée dérivée, jetable) ; checkpoint/offset persisté par consommateur (reprise après crash, catch-up vs live).

**Sagas**
- Pas de rollback distribué : **compensation** (nouvel event inverse, l'audit trail reste complet). Chaque étape compensatoire est elle-même idempotente. **Timeouts modélisés** (sinon saga bloquée à vie dans un état intermédiaire).

## 2. Invariants TESTS

- Le pattern canonique : **Given [events] / When (commande) / Then [events attendus | rejet]** — pur, sans DB ni queue, insensible aux refactorings internes de l'agrégat.
- **Test de rejouabilité** : `Replay(events)` exécuté N fois = même état (toute divergence = impureté dans apply).
- **Test d'idempotence de projection** : appliquer le même event 2× → état identique.
- Red-check adapté : muter `apply` (ignorer un champ, inverser une condition) → l'état reconstruit DOIT diverger ; muter le handler de projection → le test d'idempotence ou d'état doit rougir.
- Tester la concurrence : deux commandes sur le même stream, expected version → l'une des deux est rejetée/retryée.

## 3. Checklist REVIEW

- **Side effect dans apply ?** (grep emails/HTTP/publish dans les méthodes apply/when) — le finding le plus rentable de l'archi.
- **Query qui écrit ?** (méthode `Get*`/handler de lecture qui émet/incrémente) — violation CQS à la source.
- Handler de commande qui lit une projection pour décider ? (cf. §1)
- Event muté/édité, champ retiré d'un event existant, désérialisation stricte qui cassera sur les vieux events ? (compatibilité de relecture)
- Read model enrichi pour servir le write model (ou l'inverse) = couplage des deux modèles — ils évoluent indépendamment.
- Nouvelle projection : a-t-elle son checkpoint ? son rebuild ? Un event ajouté : tous les consommateurs le tolèrent-ils (au pire en l'ignorant) ?

## 4. Gate objectif

Le gate générique du langage s'applique ; spécifiquement : suite Given/When/Then complète sur les agrégats touchés + test de rejouabilité + test d'idempotence de projection au vert. Si l'event store a un linter de schéma/compat (registry), l'inclure.

## 5. Anti-hallucination LLM × CQRS/ES

1. **Side effect dans apply** (cf. §1) — le réflexe « c'est là qu'on traite l'event » est faux.
2. **Event traité comme commande** (un service reçoit `OrderShipped` et « l'exécute ») — un event est un fait, on ne peut pas le rejeter.
3. **CRUD déguisé** : events `XUpdated` avec le DTO complet, agrégat anémique, projections = miroir des tables — c'est du CRUD coûteux, pas de l'ES ; flaguer en design.
4. **Décision sur projection** (fraîcheur non garantie) au lieu du stream.
5. **Oubli de l'expected version** sur l'append (last-writer-wins silencieux sous concurrence).
