# Pièges connus — book-distill (par thème)

Lu en Phase 0. Règles durables uniquement, dédoublonnées contre SKILL.md. Tenir ce fichier sous ~150 lignes : consolider à dépassement (voir SKILL.md § Auto-amélioration).

## Identifier l'édition (toujours par le contenu)

- Croiser **deux marqueurs internes** : features couvertes (lambdas = post-2014 pour un livre Java), dédicace et blagues d'édition, chapitres connus pour avoir changé. Nom de fichier, CreationDate et page copyright mentent sur les rips.
- « 6th ER » = 6e *Early Release*, pas 6e édition (lire la revision history en page copyright).
- « Draft » en page de titre = manuscrit : pagination non fiable, citer par chapitre.
- Un folio plausible peut être la pagination du rip : croiser folio et nombre de pages attendu avant de citer par page.

## Extraire et cartographier

- `pdfinfo` donne le vrai nombre de pages (`file` peut dire n'importe quoi).
- **Offset pages livre ↔ PDF** : à trouver dès la Phase 1 ; il peut VARIER à l'intérieur d'un même PDF → seule la lecture du numéro imprimé fait foi pour les citations.
- Mapper les chapitres d'un rip : `grep -P "^\fChapter \d+$"` (pdftotext colle un `\f` aux en-têtes ; vérifier avec `od -c` avant de conclure que la structure est absente) ; sinon chercher la première occurrence de phrases-titres distinctives. Une table des matières multi-colonnes s'extrait en bouillie : scanner le corps, pas la TOC.
- Pagination désordonnée : extraire le texte séquentiel complet, trouver les frontières par `grep -n`, découper par `sed -n 'A,Bp'` en fichiers donnés aux agents. Plus fiable que les pages PDF.
- EPUB : `unzip` + strip des balises = texte propre, frontières de chapitres gratuites, parfois des pépites (un « TODO » oublié dans l'epub publié).

## Vérifier les citations (le grep ment)

- **Tout passe par `scripts/check-claim.py`** (normalise césures, apostrophes typographiques, ligatures, soft hyphens, sauts de page) AVANT d'accuser. Cause n°1 de faux FAIL : l'apostrophe U+2019. En pratique, la quasi-totalité des « citations introuvables » d'agents sérieux sous contrat s'avèrent réelles.
- Artefacts rencontrés en vrai : glyphes **Th/fi supprimés** (« ere are » = « There are ») → tester des fragments sans mots à Th/fi ; pollution d'interface entrelacée au milieu des phrases ; en-têtes de page qui coupent les citations (et donnent la page imprimée gratuitement) ; guillemets fermants rendus `''` ; `\f` au milieu d'une citation.
- **Recoller la phrase EXACTE du texte, jamais la reformulation d'un agent** (la paraphrase fidèle sur le fond mais fausse au mot existe). **Recompter soi-même toute énumération** d'agent.

## Distiller : où est la valeur

- La phrase-thèse de l'AUTEUR bat la thèse populaire du livre. La chercher activement : préface, conclusion, dernière page.
- Mines à pépites : la préface d'une 2e édition (ce qui a changé et pourquoi), la préface d'un tiers connu, les aveux de l'auteur, les annexes-résumés.
- Par type de livre : **catalogue** → le tri EST le travail ; **manuel pour débutants** → transcrire la pédagogie, pas un tuto ; **cookbook** → les modèles mentaux transversaux ; **livre à thèse unique répétée** → l'assumer dans les contrepoints plutôt que gonfler la diversité.
- Chercher l'actualité éditoriale AVANT d'écrire l'avis (tout livre > 5 ans : nouvelle édition ? thèse contestée ? techno citée disparue ?).
