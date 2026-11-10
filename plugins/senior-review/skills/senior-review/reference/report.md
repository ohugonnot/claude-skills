# Étape 6 — Format du rapport

Rapport structuré, concis, **commente le code jamais l'auteur**, chaque finding avec `file:line` + raison + fix concret + confiance (+ preuve de vérif si critique) :

```markdown
# Revue — <cible> (<N fichiers, M LOC>)

## Spec-coverage
<Le diff fait-il ce que le ticket #<id> demande ? — Oui / Partiel (gaps listés) / Hors-sujet>
<Scope creep éventuel : modifs hors ticket>
<Décisions non spécifiées : choix de l'implémentation que le ticket ne précisait pas, ou "aucune">

## 🔴 Bloquants (N)   <vrais merge-blockers — sinon "aucun">
1. <constat> — `file.go:42` (confiance: haute) — preuve: <vérif> — fix: <concret>

## 🟡 Importants (N)
…

## 🔵 Mineurs / suggestions (N inline, +K en plus non listés)
…

## 👍 Bien vu (≤2)
…

## Verdict
<approve | request-changes | needs-discussion> — <1 phrase>
Métriques: lint <…> · typecheck <…> · tests <…/…> · SAST <…> · coût: <N agents, ~M tokens>
```
