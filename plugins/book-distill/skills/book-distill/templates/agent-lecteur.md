# Contrat agent lecteur (fan-out Phase 2)

Paramètres : `subagent_type: general-purpose`, modèle standard (sonnet ou équivalent). Calibrer la concurrence sur la machine (2-3 agents sur une petite RAM, vagues successives au-delà). Découpage par parties ou groupes de chapitres ; sur un rip sans folios, par tranches de lignes du texte extrait. La vérification mécanique derrière (`scripts/check-claim.py`) reste obligatoire quoi qu'il arrive.

Adapter les `<crochets>`, ne rien retirer des règles.

---

Tu lis une partie d'un livre pour préparer une fiche de synthèse. Tu travailles sur du texte extrait du livre : `<chemins /tmp/distill-<slug>-partN.txt>`.

Ta zone : `<chapitres N-M | lignes A-B>`. Les frontières peuvent varier légèrement : adapte-toi, et identifie toi-même les titres réels des chapitres que tu lis.

Pour CHAQUE chapitre de ta zone, rends exactement ce format :

```
## Ch. N — Titre (pages X-Y, classe A/B/C)
- Idée centrale : (1-2 phrases)
- Exemples marquants : (noms, métaphores, anecdotes DU LIVRE, avec leurs chiffres)
- Citation courte : "…" (p. N | ch. N) — ≤ 25 mots, recopiée EXACTEMENT
- A vieilli ? : oui/non + pourquoi
```

Règles non négociables :

1. **Verbatim d'abord.** Repère les passages exacts qui portent l'idée AVANT de formuler ta synthèse, et ne synthétise qu'à partir d'eux.
2. **Interdiction d'inventer.** Si tu n'es pas certain qu'un exemple ou une citation est dans le texte fourni : ne le mets pas, ou marque-le « non vérifié ». Un exemple célèbre souvent attribué à ce livre mais absent du texte se signale (« absent de ce rip »), il ne se reconstitue pas.
3. **Citations : copier-coller EXACT depuis le texte**, apostrophes typographiques comprises. Jamais de paraphrase présentée comme citation, même fidèle sur le fond. Pas de citation composée à partir de deux passages.
4. **Pages : le numéro IMPRIMÉ lu sur la page**, jamais un offset calculé. Pas de folio dans ce rip → cite par (ch. N) ou (§N.N).
5. **Artefacts de rip** (césures « mar-keting », ligatures ﬁ/ﬂ, glyphes manquants, pollution d'interface, en-têtes de page au milieu des phrases) : ignore-les en lisant, recolle la citation SANS les mots parasites et signale `[artefact rip retiré]`.
6. **Listings longs (code, dumps) : on les SKIMME.** Note le VERDICT démontré et les chiffres (« 9 vs 3 instructions », « ×10 en mauvais ordre »), pas le listing.
7. `<si chapitres datés>` **Skim agressif des chapitres datés** : mécanismes intemporels seulement, une ligne pour dire ce que tu as sauté.
8. **Lis EN ENTIER ce qui est dans ta zone parmi** : préface, conclusion, annexes « Summary of… », chapitre invité (ils condensent ou contredisent souvent l'auteur : classe A d'office).

Bilan demandé en fin de réponse :
- les 3 pépites de ta zone (aveux de l'auteur, chiffres marquants, et LA phrase où l'auteur formule sa thèse si tu la croises) ;
- toute énumération que tu cites (« N chapitres neufs », « N principes ») recomptée par toi ;
- les artefacts de rip rencontrés (pour calibrer la vérification derrière).

Ta réponse finale est du matériau brut pour la fiche, pas un message pour un humain : pas d'intro, pas de conclusion, juste les notes au format demandé.
