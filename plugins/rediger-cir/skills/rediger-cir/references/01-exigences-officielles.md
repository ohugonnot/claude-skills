# Exigences officielles du CIR

Cadre : art. 244 quater B CGI ; BOFiP BOI-BIC-RICI-10-10-* ; Guide CIR du MESR (édition annuelle) ; Manuel de Frascati (OCDE 2015). Le dossier technique n'est exigé qu'en cas de contrôle, mais doit être constitué **au fil de l'eau** — sa reconstitution a posteriori est la première cause de fragilité.

> ⚠️ La doctrine et les taux changent à chaque loi de finances. Vérifier le Guide CIR de l'année concernée avant de figer dépenses, taux et dispositifs. Les chiffres ci-dessous intègrent la **LFI 2025** ; les revalider pour les années suivantes.

## 1. Les 3 catégories d'activités éligibles

| Catégorie | Définition (Frascati) | Marqueur distinctif |
|---|---|---|
| Recherche fondamentale | Acquérir des connaissances nouvelles sur les fondements des phénomènes, sans application visée | Pas d'objectif économique défini (rare en entreprise) |
| Recherche appliquée | Connaissances nouvelles dirigées vers un but pratique déterminé | But pratique connu, **résultat incertain** |
| Développement expérimental | Travaux systématiques fondés sur la recherche/l'expérience, produisant de nouvelles connaissances techniques | **Nouveauté non négligeable + dissipation d'une incertitude** scientifique/technique |

**Ligne de partage critique (dév. expérimental vs développement courant non éligible) :** la présence d'un **élément de nouveauté combiné à une incertitude**. Sans incertitude = intégration, paramétrage, déploiement, adaptation client = hors CIR.

Pour le logiciel, 4 catégories reconnues : algorithmes innovants, méthodologies originales, application de résultats scientifiques récents, prototypes documentés et mesurables.

## 2. Les 5 critères de Frascati (cumulatifs — un manquant = inéligible)

| Critère | À démontrer | Question-test de l'administration |
|---|---|---|
| **Nouveauté** | Résultat inédit à l'échelle mondiale (pas seulement pour l'entreprise) ; absent de l'état de l'art (publications, brevets, produits) | « Cette connaissance existe-t-elle déjà, même chez un concurrent, dans un brevet, une publication ? » |
| **Créativité** | Concepts/hypothèses originaux, non simple extrapolation de l'existant | « Un ingénieur compétent aurait-il résolu ça avec la doc technique habituelle ? » |
| **Incertitude** ⭐ | Verrou précis dont la levée n'était pas garantie ; échecs intermédiaires documentés | « Si l'issue était connue d'avance, pourquoi ne pas l'avoir appliquée immédiatement ? Quel obstacle empêchait les méthodes existantes ? » |
| **Systématicité** | Travaux planifiés, structurés, consignés (plan, jalons, logs datés) | « Y a-t-il un protocole formalisé, documenté au fil de l'eau ? » |
| **Transférabilité / reproductibilité** | Résultats formalisés (rapport, brevet, méthode, prototype) reproductibles par un tiers | « Un autre chercheur pourrait-il reproduire vos travaux à partir de votre doc ? » |

⭐ **L'incertitude est le critère pivot en contrôle.** Distinguer incertitude *scientifique* (phénomène inconnu) et *technologique* (faisabilité douteuse). Un dossier qui ne décrit que des succès n'est pas crédible.

## 3. Trame officielle du dossier justificatif (format 2025, plateforme CIROCO)

**Nouveauté 2025** : format entièrement restructuré (1re refonte depuis 2018). Synthèse d'**1 page par opération**, structure en **4 sections obligatoires**, repère de **~10 pages par opération** (indicatif, pas bloquant — déborder se justifie si la preuve le commande), saisie directe sur CIROCO (champs limités en caractères, **plus d'annexes libres**). Impose concision et structure.

Plan d'ensemble :
- **A. Présentation de l'entreprise** — identité, secteur, effectif R&D, organisation de la R&D (internes/sous-traitants), contexte économique et scientifique, périmètre total des opérations déclarées.
- **B. Liste des opérations** — tableau de synthèse (nom, période, responsable scientifique, montant).
- **C. Fiche descriptive par opération — trame en 4 sections :**
  1. **Contexte et état de l'art** — domaine, problème à résoudre, état des connaissances au lancement, démonstration que la solution ne préexistait pas.
  2. **Verrous scientifiques/technologiques** — identification précise et **nommée** (pas « difficulté technique » vague) ; pour chaque verrou : nature de l'incertitude, pourquoi les méthodes existantes échouent.
  3. **Travaux réalisés et démarche** — hypothèses, protocoles, méthodes/outils, essais ; travaux aboutis **ET échoués** ; personnel, qualifications, temps affecté.
  4. **Résultats et indicateurs** — résultats (y compris négatifs), savoir-faire/publications/brevets/livrables, indicateurs mesurables, verrous levés vs résiduels.
- **D. Ressources humaines et matérielles** — tableau personnel R&D (nom, qualification, diplôme, temps en ETP et %), CV/diplômes/fiches de poste, feuilles de temps, matériels.
- **E. Tableau financier** — dépenses par catégorie, rapprochement comptabilité analytique, subventions à déduire.
- **F. Pièces annexes** — contrats + agréments des sous-traitants, grand livre R&D, livrables techniques datés.

> Le **gabarit historique** (intro / présentation société / fiche-opération / annexes — voir `03-gabarit-exemple.md`) reste compatible : il faut surtout que les 4 sections de la fiche-opération apparaissent nettement et que le tout tienne dans la limite de pages.

## 4. Dépenses éligibles (régime post-LFI 2025)

- **Taux CIR** : 30 % jusqu'à 100 M€ de dépenses/an, 5 % au-delà (50 % dans les DOM).
- **Personnel R&D** (salaires + charges) : éligible au réel.
- **Frais de fonctionnement** : **40 %** des dépenses de personnel (était 43 %).
- **Amortissements** des biens affectés R&D : éligibles.
- **Sous-traitance agréée** : éligible, plafond 10 M€/an. Le sous-traitant doit être **agréé MESR** (organismes publics dispensés). Liste : data.esr.gouv.fr. Annexe **2069-A-2-SD** obligatoire. Non-cumul (dépense comptée une seule fois — CE 05/03/2018).
- **EXCLUS depuis le 14 fév. 2025** : ⚠️ **veille technologique**, **brevets** (dépôt/maintenance/défense/dotations), **doublement jeune docteur** (supprimé). → Un poste « logiciels de veille » hérité de dossiers antérieurs ne fonde plus de dépense éligible (peut rester mentionné comme moyen, pas comme dépense CIR).

Formulaires : **2069-A-SD** (CERFA 11081, déclaration), 2069-A-2-SD (sous-traitance), 2069-A-1-SD (si > 10 M€).

## 5. Personnel et feuilles de temps

- **Chercheurs/ingénieurs** : Bac+5 / diplôme d'ingénieur **ou** compétences équivalentes acquises en entreprise.
- **Techniciens de recherche** : aucun diplôme requis (CE), mais sous contrôle des chercheurs, soutien technique indispensable.
- **Sans diplôme** : valorisable si la qualification ressort des tâches réelles → contrat + **fiche de poste détaillée** (les intitulés génériques sont rejetés — jurisprudence Kaliop/Scality).
- **Exclus** : administratif, commercial, maintenance, direction (sauf participation directe).
- **Feuilles de temps** : **toute forfaitisation est exclue** (un « 50 % R&D » annuel est présumé forfaitaire). Chaque entrée = date + description des tâches + lien à l'opération éligible. Saisie contemporaine, au fil de l'eau.

## 6. Rescrit et sécurisation

- **Rescrit CIR** (L. 80 B 3° LPF) : confirmation formelle d'éligibilité avant déclaration ; à déposer **≥ 6 mois** avant la date limite de la 2069-A-SD ; réponse sous **3 mois** ; silence = **accord tacite opposable**. Sécurise la qualification R&D (et le financier pour les PME).
- **CIR vs CII** : verrou scientifique → CIR (30 %). Produit nouveau sans verrou scientifique mais incertitude de faisabilité → **CII** (PME seulement, **20 %** depuis 2025, plafond crédit 80 k€). Non-cumul sur les mêmes dépenses.
- **CIROCO** : portail unique 2025 (rescrit CIR/JEI, agréments CIR/CII).
- **JEI** : remboursement immédiat de la créance CIR, exonérations sociales ; seuil de dépenses R&D porté à **20 %** des charges (depuis mars 2025).

## 7. Contrôle — délais et procédure

- **Délai de reprise** : 3 ans à compter du dépôt (CIR exercice N déclaré en N+1 → contrôlable jusqu'au 31/12 N+4).
- Deux temps : vérification comptable (DGFiP) puis **expertise scientifique (MESR)**, avis consultatif mais déterminant.
- **30 jours** pour répondre à une demande de justificatifs.
- Conservation des pièces : 3 ans après dépôt (idéalement plus).
- Sanctions : rappel + intérêts + pénalités jusqu'à **40 %** (mauvaise foi).
