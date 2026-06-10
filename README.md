# claude-skills

Skills personnels pour [Claude Code](https://claude.com/claude-code).

## Skills

| Skill | Rôle |
|---|---|
| [`feature-loop`](skills/feature-loop) | Implémentation de feature autonome, itérative et quality-gated (orchestrateur-workers + evaluator-optimizer : le code est toujours relu par un agent qui ne l'a pas écrit, gate objectif build/lint/tests avant toute revue LLM). |
| [`senior-review`](skills/senior-review) | Revue de code niveau senior — reviewers aveugles spécialisés par dimension (correctness/sécurité/design/tests), findings vérifiés (receipts grep/exec/test), panel adversarial sur les cas critiques. |
| [`issue-mr`](skills/issue-mr) | Crée issue + branche + MR/PR à partir d'une description (GitLab `glab` / GitHub `gh`, auto-détecté). Modes scaffold / isoler / analyse. |
| [`vide-contexte`](skills/vide-contexte) | Avant `/clear` : extrait les insights non-déductibles de la conversation (décisions, gotchas, préférences) et les persiste en fichiers mémoire — dédup contre l'index, format aligné sur le harnais — puis confirme et rend la main. |

## Installation

Cloner puis copier dans le dossier skills de Claude Code :

```bash
git clone https://github.com/ohugonnot/claude-skills.git /tmp/claude-skills
cp -r /tmp/claude-skills/skills/* ~/.claude/skills/
```

Ou en symlink pour rester synchronisé avec le repo :

```bash
git clone https://github.com/ohugonnot/claude-skills.git ~/claude-skills
for s in feature-loop senior-review issue-mr vide-contexte; do
  ln -s ~/claude-skills/skills/$s ~/.claude/skills/$s
done
```

Les skills sont alors invocables via `/feature-loop`, `/senior-review`, `/issue-mr`, `/vide-contexte`.

## Notes

- Chaque skill garde son `CHANGELOG.md` et son `lessons.md` (leçons distillées run après run).
- L'historique `.archive/` (versions antérieures) n'est volontairement pas publié.
