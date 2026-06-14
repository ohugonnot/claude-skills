# Changelog — book-distill

## 1.0.0 — 2026-06-11

Extraction portable du moteur de distillation du skill privé `fiche-livre` (web-developpeur.com, ~30 livres traités), recalibrée sur trois recherches dédiées :

- **Science cognitive de la synthèse** : macro-règles de Kintsch & van Dijk, marqueur d'expertise de Brown & Day, verdicts de Dunlosky et al. 2013, signaling (Schneider 2018), retrieval (Adesope 2017), self-explanation (Bisra 2018), given-new (Clark & Haviland 1977).
- **Anti-hallucination LLM** : verbatim-first (Anthropic), lost-in-the-middle, claims atomiques (FActScore), vérification découplée (CoVe), hallucination extrinsèque (Maynez 2020), contrôle de couverture (SummHay).
- **Authoring de skills (état de l'art juin 2026)** : progressive disclosure à un niveau, scripts exécutés via `${CLAUDE_SKILL_DIR}`, le pourquoi plutôt que les MUST, degrés de liberté calibrés.

Contenu : pipeline en 7 phases avec gates (cartographie Adler A/B/C → notes verbatim-first → distillation thématique → jugement post-compréhension avec contrepoints → écriture pédagogique → boucle de vérification ≥ 85/100), `templates/fiche.md`, `templates/agent-lecteur.md` (contrat fan-out anti-invention), `scripts/check-claim.py` (vérification de claims tolérante aux artefacts de rip), `reference/science.md` (la base de preuves sourcée de chaque règle), `lessons.md` (pièges distillés de ~30 livres réels).
