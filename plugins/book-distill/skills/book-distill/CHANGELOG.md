# Changelog — book-distill

## 1.2.0 — 2026-10-27

Leçons d'une série de onze fiches de livres techniques (skill privé `fiche-livre`), mesurées avant d'être promues :

- **Tri avant lecture complète** (Phase 0, `templates/agent-tri.md`) : 60 000 caractères lus (carte, introduction, conclusion, deux chapitres cœur), verdict LIRE EN ENTIER / FICHE COURTE / PASSER. Sur la série, le tri prévoyait la note finale à un point près.
- **Note = moyenne des sous-critères**, la question de Sivers devient un contrôle (écart > 1,5 signalé dans l'avis).
- **Juge aveugle** (Phase 4, `reference/bareme-notation.md`) : un sous-agent note sans jamais voir la note du rédacteur, preuve d'abord, échelle ancrée sur des livres déjà notés, comparaison dans les deux ordres. Mesuré : écart 0,95 pour un relecteur ancré contre 0,4 à l'aveugle.
- **Réconciliation à 1,0** sur la note (bruit du juge mesuré : 0,33 en moyenne, 0,8 au plus) ; entre 0,7 et 1,0, moyenner deux passages. Les corrections du demandeur sont consignées et deviennent des ancres.
- **Écriture** : fil directeur (thèse en une phrase, familles d'idées annoncées, liaisons), phrases simples (25 mots, deux relatifs, définitions hors des phrases qui raisonnent), titres-affirmations qui nomment leur objet, exemples « de mon cru » marqués et publics seulement ; une règle nouvelle se relance sur toute la fiche, un ajout de relecture repasse la chasse aux redites. Tirées des corrections humaines d'une fiche.
- **Vérification** : `scripts/check-sources.py` (chapitres cités ⊆ chapitres déclarés lus) et passe « lecteur novice » avant la relecture finale.
- **Modèles** : économique pour lire, vérifier et juger ; fort pour la seule prose finale (A/B : voix meilleure, exactitude égale, ~3 500 tokens de sortie). Briefs de sous-agents autonomes et bornés à la grille.
- `reference/science.md` § Noter : sources (ancrage du juge, biais de position, échelles ancrées, jurys) et mesures maison.

## 1.1.1 — 2026-06-28

- Corrige des citations imprécises / mal attribuées (audit fact-check des références).

## 1.1.0 — 2026-06-16

Renforcement pédagogique « non-résumé », tiré d'une fiche CQRS/Event Sourcing réussie (cf. fiche-livre) :

- **Audience par défaut « le nouveau qui rejoint l'équipe »** pour les livres denses en jargon (patterns, archi, domaine) + règle absolue « définir avant d'utiliser » (un terme employé doit avoir été défini dans une phrase antérieure) ajoutées au point 7 de la Phase 5.
- **Radar par idée** (Phase 6b-bis) : chaque idée distillée notée sur quatre axes (Clarté / Exemples / Pédagogie / Concision), seuil 8/10, boucle de réécriture par idée. Porte pédagogique au grain de l'idée, distincte de la note /10 du livre et du score /100 de la fiche. La 6c boucle aussi tant qu'une idée reste sous 8.

## 1.0.0 — 2026-06-11

Extraction portable du moteur de distillation du skill privé `fiche-livre` (web-developpeur.com, ~30 livres traités), recalibrée sur trois recherches dédiées :

- **Science cognitive de la synthèse** : macro-règles de Kintsch & van Dijk, marqueur d'expertise de Brown & Day, verdicts de Dunlosky et al. 2013, signaling (Schneider 2018), retrieval (Adesope 2017), self-explanation (Bisra 2018), given-new (Clark & Haviland 1977).
- **Anti-hallucination LLM** : verbatim-first (Anthropic), lost-in-the-middle, claims atomiques (FActScore), vérification découplée (CoVe), hallucination extrinsèque (Maynez 2020), contrôle de couverture (SummHay).
- **Authoring de skills (état de l'art juin 2026)** : progressive disclosure à un niveau, scripts exécutés via `${CLAUDE_SKILL_DIR}`, le pourquoi plutôt que les MUST, degrés de liberté calibrés.

Contenu : pipeline en 7 phases avec gates (cartographie Adler A/B/C → notes verbatim-first → distillation thématique → jugement post-compréhension avec contrepoints → écriture pédagogique → boucle de vérification ≥ 85/100), `templates/fiche.md`, `templates/agent-lecteur.md` (contrat fan-out anti-invention), `scripts/check-claim.py` (vérification de claims tolérante aux artefacts de rip), `reference/science.md` (la base de preuves sourcée de chaque règle), `lessons.md` (pièges distillés de ~30 livres réels).
