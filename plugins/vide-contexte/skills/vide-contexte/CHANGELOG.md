# Changelog — vide-contexte

## 1.2.0 — 2026-08-10

- **La description mène par l'action** : le nom annonce « vide » alors que le skill ne vide jamais rien (« Ne lance pas /clear lui-même ») — le mot directeur contredisait le comportement. La description ouvre maintenant sur « Persists… — nothing is cleared by this skill, only saved », et le titre devient « Persister le contexte avant de le vider ». Nom du skill inchangé : il colle aux formulations réelles de l'utilisateur, le casser coûterait plus que le gain.
- **Désambiguïsation ajoutée** face à `branch-wrap-up`, qui exécute lui aussi une passe de capture de connaissances.

## 1.1.0 — 2026-06-11

- Format des fichiers mémoire aligné sur le harnais réel : `name` en slug kebab, `metadata.type`, `description` = clé de rappel.
- Étape de **déduplication** explicite : lire `MEMORY.md` avant d'écrire, mettre à jour plutôt que dupliquer ; corriger ou supprimer une mémoire devenue fausse est légitime.
- Résolution du chemin mémoire robuste : system-reminder du harnais d'abord, sinon encodage du cwd documenté (`/` → `-`).
- Format de la ligne d'index `MEMORY.md` précisé (`- [Titre](fichier.md) — accroche`) ; liens `[[slug]]` entre mémoires connexes ; dates relatives converties en absolues.
- Confirmation enrichie : mises à jour listées séparément, sortie `/clear` ou `/compact`, et consigne « un faux souvenir coûte plus cher qu'une absence ».

## 1.0.0

- Version initiale : workflow 3 étapes (extraire → persister → confirmer), critères oui/non, non-objectifs.
