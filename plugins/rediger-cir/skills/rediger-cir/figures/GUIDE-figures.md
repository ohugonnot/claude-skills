# Guide des figures CIR

Un bon dossier compte en général 8-12 figures. Les figures portent une part de la démonstration (axe 8 du radar) : elles prouvent visuellement la complexité maîtrisée et la démarche. Une figure non légendée ou non sourcée ne compte pas.

## Principe : SVG éditable
Produire les schémas en **SVG** (texte, versionnable, éditable, rendu net à toute échelle, convertible PNG pour le `.docx`). Adapter des templates existants plutôt que partir de zéro.

Conversion SVG→PNG pour Word : `cairosvg fig.svg -o fig.png`. Sinon `rsvg-convert -o fig.png fig.svg` ou `inkscape fig.svg --export-type=png`.

## Conventions visuelles
- **Identité** : choisir une couleur d'accent cohérente avec la charte de [ENTREPRISE] et s'y tenir sur toutes les figures.
- **Code couleur thématique** : attribuer une couleur stable par type d'objet du domaine (ex. états, actions, alertes/incertitudes) et garder ce code constant d'une figure à l'autre.
- **Sous-traitant** : distinguer visuellement (encadré dédié) un éventuel sous-traitant agréé des équipes internes.
- **Chaque figure** : numéro (« Figure N »), titre, et **mention de source** en dessous (« Source : [ENTREPRISE] » ou la source externe exacte). Une figure reprise d'une publication doit créditer la publication vérifiée.

## Types de figures attendus dans un CIR (générique)

| Figure | Type | Rôle dans la démonstration |
|---|---|---|
| Rappel technique du domaine | Schéma de principe | Rendre le [VERROU] intelligible pour un évaluateur non-spécialiste |
| Figure(s) de l'état de l'art | Histogramme / courbe de complexité | Ancrer visuellement les données chiffrées d'une publication (preuve bibliographique) |
| Organigramme R&D | Hiérarchie | Qualifications de l'équipe (axe 6) |
| Architecture de la solution | Schéma d'architecture | Cœur de la contribution de l'année |
| Frise des prototypes | Timeline + verdict | Démarche itérative, échecs valorisés (axe 4) |
| Courbe de dégradation mesurée | Courbe | Preuve chiffrée de la limite atteinte (axe 5) |
| Diagramme du domaine | Schéma de flux | Complexité maîtrisée des objets métier |
| Tableau de benchmarks comparés | Tableau | Prototypes × (mesures, verdict) — axe 5 |

### Figures bibliographiques dans l'état de l'art (convention)
Quand une publication donne des données chiffrées clés, une figure schématique de 1-2 panneaux suffit à les ancrer visuellement. Règles :
- Valeurs **mesurées par la publication** : tracées avec valeur exacte et label.
- Valeurs **intermédiaires non publiées** : tracées en schématique, légendées « schématique d'après [auteur] » ou note de bas de figure.
- Code couleur clair : une teinte = valeur basse/référence, une teinte = valeur haute/problème.
- Source obligatoire dans la légende Word (`{custom-style="Image Caption"}`).

## Règle anti-invention pour les figures
Une figure qui affiche des données (courbe, tableau) engage autant qu'une phrase. Ne jamais tracer une courbe sur des chiffres supposés : soit les chiffres sont mesurés et archivés, soit la figure est qualifiée « illustrative / schématique » explicitement.

> ⚠️ Avant publication, confirmer toute donnée chiffrée par des **benchmarks réels datés** (preuve infabricable, axe 5). Ne pas inventer de chiffres pour une figure.
