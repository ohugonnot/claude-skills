<!--
Format de citation du dossier. RÈGLE ABSOLUE : chaque référence doit avoir été
vérifiée via un résolveur (DOI/arXiv/HAL). Les champs sont RECOPIÉS depuis la
réponse de l'API, jamais rédigés de mémoire.
Voir le protocole anti-hallucination de bibliographie pour la procédure complète.
-->

## Bibliographie

Format (numéroté, cité inline dans le corps par [n]) :

```
[n] Auteur1, Auteur2, … (Année). « Titre exact ». Revue / Conférence / Éditeur, volume(numéro), pages. DOI : https://doi.org/<doi>
```

### Procédure de constitution du socle de références

Ne réutilisez aucune référence sans la re-résoudre. Pour chaque entrée candidate :
1. Résoudre le DOI / l'identifiant arXiv / HAL et **recopier** titre, auteurs, année, venue depuis la réponse.
2. Marquer le statut de vérification (voir ci-dessous).
3. Pour une source web sans DOI (page d'auteur, document de référence technique) : citer l'URL exacte vérifiée par récupération directe, et la présenter comme référence technique fondatrice (pas académique peer-reviewed).
4. Références réglementaires (textes sectoriels applicables, articles du CGI dont art. 244 quater B) : citer le texte officiel et son URL Légifrance / EUR-Lex, vérifiée.

### Marquage du statut de vérification
Pendant la rédaction, préfixer chaque entrée :
- `[VÉRIFIÉ ✓ <source>]` — DOI/arXiv/HAL résolu, métadonnées recopiées.
- `[À VÉRIFIER]` — candidat non encore résolu → **ne pas laisser dans le dossier final**.
- `[NON TROUVÉ]` — n'a résolu sur aucun index → **supprimer** (suspicion d'invention).

Aucune entrée `[À VÉRIFIER]` ou `[NON TROUVÉ]` ne doit subsister dans le dossier remis.
