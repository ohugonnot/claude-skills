# Changelog — rediger-cir

## 1.1.1 — 2026-08-10

- **Sommaires ajoutés aux cinq références de plus de 100 lignes** (`02`, `03`, `05`, `06`, `07`) — recommandation officielle Anthropic pour tout fichier de référence dépassant 100 lignes ; `06-etat-de-lart-IA-detail.md` en fait 250.

## 1.1.0 — 2026-08-10

- **`disable-model-invocation: true`** : skill lourd, spécifique à un domaine et lancé à la demande — exactement le cas que `skill-builder` cite pour ce flag (« a tax-dossier writer »). Il ne se déclenche plus tout seul, seulement via `/rediger-cir`, et sa description quitte le contexte du modèle.
- **Mot directeur « verrou » injecté dans la description** : il portait toute la règle d'or du corps (9 occurrences) sans jamais apparaître ni dans le nom ni dans la description.

## 1.0.0 — 2026-06-28

- Version initiale publique : méthodologie CIR généraliste — trame officielle CIROCO (4 sections), critères du Manuel de Frascati, démarche expérimentale (échecs valorisés), protocole de vérification bibliographique externe (anti-hallucination, `verify-biblio.py`), radar d'auto-notation 8 axes. Gabarits à trous et guide des figures. **Aucune donnée d'entreprise.**
