# Changelog — vide-contexte

## 1.3.0 — 2026-08-12

Issu d'un audit des 169 mémoires produites par ce skill sur un dépôt réel : le corpus était sain sur le fond, mais quatre mécaniques silencieuses le dégradaient. Chaque ajout ci-dessous trace vers un défaut mesuré.

- **Règle anti-pourrissement « le mécanisme, pas l'instantané »**, avec exemple avant/après. Douze mémoires figeaient un état de MR (« pushée », « pas encore mergée », « reste à faire ») devenu faux en quelques semaines. Le skill disait « ne pas sauvegarder l'état de la tâche en cours » sans jamais dire **quoi écrire à la place** quand l'insight porte justement sur un chantier. La règle vaut explicitement pour la `description:`, où trois occurrences envoyaient un signal faux longtemps après le merge.
- **Convention de nom de fichier, jusqu'ici jamais écrite** : `<type>_<slug>.md`, et `name` = ce nom sans son préfixe, underscores en tirets. Trois conventions coexistaient (prose accentuée, kebab, snake) sur 165 fichiers, dont 54 en prose — d'où 83 liens `[[...]]` qui ne résolvaient pas, silencieusement. C'est le défaut le plus coûteux et le plus invisible.
- **Critères de fin vérifiables** (étape 4) remplaçant la simple confirmation. Quatre mémoires étaient dépourvues de `description` — donc jamais rappelées, donc écrites pour rien. Un skill doit donner de quoi distinguer « fait » de « pas fait ».
- **Budget d'accroche pour `MEMORY.md`** (~80 caractères). « Une ligne par mémoire » se lisait comme une ligne physique : 36 lignes dépassaient 160 caractères, une atteignait 407. L'index se paie à chaque session, le corps des mémoires seulement au rappel — le volume va dans le corps.
- **Chercher la contradiction, pas seulement le doublon** : deux mémoires peuvent traiter des sujets distincts et se contredire sur un fait. Vu sur deux notes d'accès base de données qui s'opposaient sur l'emplacement d'un secret.
- **Nettoyage des liens entrants à la suppression** : retirer une mémoire sans purger les `[[liens]]` qui la visaient laisse des références mortes.
- **Vérifier ce qu'on cite avant de l'écrire** : un renommage de dossier avait invalidé des dizaines de chemins en mémoire sans qu'aucun signal ne le révèle.

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
