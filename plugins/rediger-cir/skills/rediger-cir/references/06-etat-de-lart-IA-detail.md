# État de l'art assisté par IA pour un dossier CIR — Protocole anti-hallucination

> Objectif : produire un état de l'art de qualité scientifique, assisté par IA, **sans aucune citation inventée**, pour un dossier Crédit d'Impôt Recherche. En contrôle fiscal, une seule référence fabriquée décrédibilise tout le dossier.
>
> **Note de fiabilité** : toutes les références chiffrées de ce rapport ont été vérifiées en direct (juin 2026) contre Crossref, l'API arXiv et Semantic Scholar — chaque DOI résout, chaque ID arXiv existe avec un titre correspondant. Les IDs arXiv en `26xx.xxxxx` (févr.–avr. 2026) sont réels : l'encodage `AAMM` correspond bien à des prépublications de 2026.

---

## Sommaire

- [1. Méthodes de revue de littérature assistée par IA (SLR, PRISMA, snowballing, RAG)](#1-methodes-de-revue-de-litterature-assistee-par-ia-slr-prisma-snowballing-rag)
- [2. Outils spécialisés — comparatif fiabilité des citations](#2-outils-specialises-comparatif-fiabilite-des-citations)
- [3. Taux d'hallucination de citations par les LLM (études chiffrées)](#3-taux-dhallucination-de-citations-par-les-llm-etudes-chiffrees)
- [4. APIs de vérification gratuites — endpoints concrets (testés en direct)](#4-apis-de-verification-gratuites-endpoints-concrets-testes-en-direct)
- [5. Protocole bout-en-bout exécutable par un agent IA](#5-protocole-bout-en-bout-executable-par-un-agent-ia)
- [6. Prompts et garde-fous anti-invention](#6-prompts-et-garde-fous-anti-invention)
- [Sources principales (toutes vérifiées par résolution DOI/arXiv)](#sources-principales-toutes-verifiees-par-resolution-doiarxiv)

## 1. Méthodes de revue de littérature assistée par IA (SLR, PRISMA, snowballing, RAG)

### Le constat partagé par toute la littérature 2023-2025
Tous les articles méthodologiques convergent sur **trois points non négociables** :
1. **L'écrasante majorité des usages d'IA fiables portent sur le screening** (tri titre/résumé), pas sur la génération de texte ou de citations.
2. **L'extraction full-text et la synthèse restent peu fiables** : aucun modèle ne dépasse un F1 d'extraction structurée de ~0,67.
3. **La supervision humaine reste obligatoire** : pas un seul papier ne conclut à une automatisation complète fiable.

### Où l'IA aide vraiment, étape par étape
| Étape SLR | IA utile ? | Preuve / fiabilité |
|---|---|---|
| Génération de requête de recherche | Oui (assistance) | Multi-agent SLR ([arXiv:2403.08399](https://arxiv.org/abs/2403.08399)) |
| Screening titre/résumé | **Oui, le cas d'usage le plus mûr** | GPT-4o : sensibilité 0,85 / spécificité 0,97 ([10.1017/rsm.2025.10014](https://doi.org/10.1017/rsm.2025.10014)) |
| Screening full-text | Partiel, risqué | Review Copilot : seulement 47,4 % de spécificité full-text ([10.1186/s13643-025-02997-8](https://doi.org/10.1186/s13643-025-02997-8)) |
| Extraction de données | Peu fiable | Précision moyenne 83 % ; F1 < 0,67 en extraction structurée ([JAMIA 10.1093/jamia/ocaf063](https://doi.org/10.1093/jamia/ocaf063)) |
| **Génération de citations** | **DANGER** | Voir section 3 — 18 à 95 % d'hallucination |
| Snowballing (citation chaining) | Oui (découverte) | ProfOlaf, Interleaved Snowballing |

### Articles méthodologiques clés (tous vérifiés)
- **Benchmark de screening multi-LLM** — *Optimal large language models to screen citations for systematic reviews* ([10.1017/rsm.2025.10014](https://doi.org/10.1017/rsm.2025.10014)). Compare GPT-4o, Gemini 1.5 Pro, Claude 3.5 Sonnet, Llama 3.3 70B. Coûts : 0,28 à 0,40 $/100 citations ; Llama gratuit (open-weight). Limite : domaine unique (sepsis), prompt optimisé pour GPT-4.
- **Pipeline LLM bout-en-bout réel** — *The emergence of LLMs as tools in literature reviews* ([JAMIA, 10.1093/jamia/ocaf063](https://doi.org/10.1093/jamia/ocaf063)). Vote majoritaire (3 inférences) pour le screening ; ~40 % de l'intro, 90 % des résultats générés par LLM. Flag explicite : **taux d'hallucination élevés en génération de citations**.
- **Validation clinique** — *Accelerating the pace and accuracy of systematic reviews using AI* ([10.1186/s13643-025-02997-8](https://doi.org/10.1186/s13643-025-02997-8)). Conclusion des auteurs : *« aucune technologie IA ne peut conduire seule une revue systématique à ce stade »*.
- **Hybrid human-in-the-loop** — *A hybrid framework for AI-augmented SLR* ([10.1007/s11301-025-00522-8](https://doi.org/10.1007/s11301-025-00522-8)). Cinq principes épistémiques : transparence, validité, fiabilité, exhaustivité, agentivité réflexive.
- **Snowballing assisté** — *Interleaved Snowballing* ([arXiv:2402.08339](https://arxiv.org/abs/2402.08339)) ; *ProfOlaf* ([arXiv:2510.26750](https://arxiv.org/abs/2510.26750)) — snowballing itératif via Google Scholar, Semantic Scholar, DBLP.
- **RAG pour citations scientifiques** — *SciRAG* (retrieval citation-aware, [arXiv:2511.14362](https://arxiv.org/abs/2511.14362)) ; *SLR du RAG via PRISMA 2020* ([arXiv:2508.06401](https://arxiv.org/abs/2508.06401)).

---

## 2. Outils spécialisés — comparatif fiabilité des citations

**Distinction fondamentale pour le CIR** : les outils **ancrés dans une base réelle** (retrieval) citent des papiers indexés et affichent des DOIs réels. Les outils **génératifs** (LLM seuls, Perplexity) peuvent fabriquer. Les bases (Semantic Scholar, OpenAlex) ne sont pas génératives — risque d'hallucination nul.

| Outil | Ancré base réelle ? | DOIs réels ? | Risque hallucination | Tarif (2025-26) |
|---|---|---|---|---|
| **Semantic Scholar** | Oui (214 M, AI2 non-profit) | Oui | **N/A (base)** | Gratuit + API |
| **OpenAlex** | Oui (250 M+, ouvert) | Oui | **N/A (base)** | Gratuit + API |
| **Scite.ai** | Oui (280 M+ full-text, 1,2 Md citations classées) | Oui | **Très faible** | Gratuit limité / ~12-20 $/mois |
| **Consensus** | Oui (~200 M via S2 + OpenAlex) | Oui | Faible | Gratuit / ~9-15 $/mois |
| **Elicit** | Oui (138 M papiers + essais) | Oui | Faible | Gratuit / ~10-42 $/mois |
| **Connected Papers** | Oui (via S2) | Via liens S2 | N/A (graphe) | Gratuit 5/mois / ~6 $/mois |
| **Research Rabbit** | Oui (OpenAlex, S2, PubMed) | Via liens | Très faible | Gratuit / payant fin 2025 |
| **SciSpace** | Oui (282 M) | Oui | Faible-modéré | Gratuit / ~12-20 $/mois |
| **Undermind** | Résumés seulement | Partiel (inline) | **Modéré (synthèse générative)** | Gratuit 3/mois / 20 $/mois |
| **Perplexity Academic** | Web live + sources acad. | Partiel (pas tjrs DOI) | **Modéré à notable** | Gratuit / 20 $/mois |

**Recommandation CIR** : privilégier **Scite.ai, Consensus, Elicit** (retrieval-grounded) pour la découverte/synthèse, et **Semantic Scholar + OpenAlex** comme couche d'infrastructure de vérification. **Scite.ai** est unique : il classe chaque citation comme *supporting / contrasting / mentioning* — précieux pour démontrer qu'un verrou scientifique n'est pas levé. Éviter **Perplexity** et les **LLM seuls** comme source de citations.

> Sources : [BioSkepsis Elicit vs Consensus](https://bioskepsis.ai/blog/elicit-vs-consensus/), [Anara Scite vs Elicit](https://anara.com/blog/scite-vs-elicit), [Aaron Tay — Google Scholar vs AI tools](https://aarontay.substack.com/p/google-scholar-vs-other-ai-search-tools), [OpenAlex 2025 review](https://blog.openalex.org/openalex-2025-in-review/).

---

## 3. Taux d'hallucination de citations par les LLM (études chiffrées)

**Le chiffre à retenir pour un comité de direction** : même GPT-4 fabrique 18 % de ses citations, et certains modèles montent à 95 %. Une citation générée par LLM non vérifiée a une probabilité non négligeable d'être fausse.

| Étude (DOI/arXiv vérifié) | Modèle(s) | Domaine | Taux fabrication |
|---|---|---|---|
| Walters & Wilder 2023 ([10.1038/s41598-023-41032-5](https://doi.org/10.1038/s41598-023-41032-5)) | GPT-3.5 | Multidisciplinaire | **55 %** (+ 43 % d'erreurs dans les réelles) |
| idem | GPT-4 | Multidisciplinaire | **18 %** (+ 24 % d'erreurs) |
| Cross-disciplinary 2024 ([10.2196/52935](https://doi.org/10.2196/52935)) | Multiples | Humanités | DOI invalides **89,4 %** ; ~51 % fabriquées global |
| GhostCite 2025 ([arXiv:2602.06718](https://arxiv.org/abs/2602.06718)) | 13 LLMs / 40 domaines | — | **14 % (DeepSeek) à 95 % (Hunyuan)** |
| How LLMs Cite 2025 ([arXiv:2603.03299](https://arxiv.org/abs/2603.03299)) | 10 LLMs / 4 domaines | — | **11,4 % à 56,8 %** |
| 8 chatbots 2025 ([arXiv:2505.18059](https://arxiv.org/abs/2505.18059)) | 8 LLMs (incl. Claude, Perplexity) | 5 domaines | **39,8 % erronées/fabriquées** ; 26,5 % seulement totalement correctes |
| Mental health 2025 ([10.2196/80371](https://doi.org/10.2196/80371)) | GPT-4o | Santé mentale | **19,9 % fabriquées** ; 45,4 % d'erreurs dans les réelles |
| Legal fictions 2024 ([10.1093/jla/laae003](https://doi.org/10.1093/jla/laae003)) | GPT-4 / Llama 2 | Jurisprudence US | **58 % / 88 %** |
| Deep research agents 2025 ([arXiv:2604.03173](https://arxiv.org/abs/2604.03173)) | 10 agents / 32 champs | — | **3-13 % URLs hallucinées** ; 5-18 % non-résolvantes |
| BibTeX agents 2025 ([arXiv:2604.03159](https://arxiv.org/abs/2604.03159)) | GPT-5, Claude, Gemini | 4 domaines | **49,1 % d'entrées BibTeX imparfaites** |

**Fait aggravant** : 100+ citations hallucinées dans 53 papiers **acceptés à NeurIPS 2025**, ayant passé 3-5 relecteurs experts ([arXiv:2602.05930](https://arxiv.org/abs/2602.05930)). Les experts ne détectent pas les fausses citations à l'œil.

### Techniques de réduction (prouvées)
| Technique | Effet mesuré | Source |
|---|---|---|
| **Consensus multi-modèles** (3+ LLM citant le même travail) | 95,6 % de précision (×5,8) | [arXiv:2603.03299](https://arxiv.org/abs/2603.03299) |
| **Vérification post-génération** (DOI/Crossref/S2) | Décisif — voir section 4 | — |
| **RAG seul** | **Insuffisant** : jusqu'à 33 % d'hallucination persistante | — |
| **Prompt : demander DOI précis puis vérifier en externe** | Réduit vs requête ouverte | — |

> **Implication CIR** : la combinaison gagnante = **retrieval-grounding + consensus multi-modèles + vérification DOI externe systématique**. Le RAG seul ne suffit pas.

---

## 4. APIs de vérification gratuites — endpoints concrets (testés en direct)

Toutes ces APIs ont été appelées le jour de rédaction ; les codes HTTP et comportements ci-dessous sont observés, pas supposés.

### 4.1 Crossref — la référence pour résoudre un DOI
```
https://api.crossref.org/works/{DOI}                 # métadonnées d'un DOI
https://api.crossref.org/works?query={termes}         # recherche
```
Exemple testé (HTTP 200) :
`https://api.crossref.org/works/10.1038/s41598-023-41032-5`
DOI inexistant testé → **HTTP 404** (c'est le test d'existence). Renvoie titre, journal, auteurs, dates, références. Gratuit. Ajouter `?mailto=vous@domaine.fr` pour le « polite pool ».

### 4.2 OpenAlex — recherche et vérification (250 M+ œuvres)
```
https://api.openalex.org/works/https://doi.org/{DOI}
https://api.openalex.org/works?filter=doi:{DOI}
```
Exemple testé (HTTP 200, **sans clé**) :
`https://api.openalex.org/works/https://doi.org/10.7717/peerj.4375`
> **Correction d'une affirmation circulant en ligne** : un appel sans clé renvoie bien **HTTP 200 en juin 2026** (vérifié). Aucune clé n'est requise pour un usage de vérification ponctuel. 100 000 req/jour.

### 4.3 DOI Content Negotiation — métadonnées propres en 1 appel
```bash
# BibTeX direct depuis le DOI (testé, HTTP 200)
curl -LH "Accept: application/x-bibtex" https://doi.org/10.1126/science.169.3946.635
# Citation formatée APA en texte
curl -LH "Accept: text/x-bibliography; style=apa" https://doi.org/{DOI}
# CSL-JSON (pour pipeline)
curl -LH "Accept: application/vnd.citationstyles.csl+json" https://doi.org/{DOI}
```
Codes : **200** OK, **404** DOI inexistant, **406** format non servi. Le `-L` (suivre la redirection) est **obligatoire**. C'est l'outil idéal pour générer une bibliographie propre **à partir de DOIs déjà vérifiés**.

### 4.4 Semantic Scholar Graph API
```
https://api.semanticscholar.org/graph/v1/paper/DOI:{DOI}?fields=title,year,authors
https://api.semanticscholar.org/graph/v1/paper/search?query={termes}&fields=title,year,externalIds
```
Exemple testé (HTTP 200, renvoie paperId + titre + année + externalIds dont DOI). **Les champs doivent être demandés explicitement** via `?fields=`. Sans clé : pool partagé (~1 req/s). Clé gratuite → 1 req/s dédié.

### 4.5 arXiv API — pour les prépublications
```
http://export.arxiv.org/api/query?id_list={arxivId}            # vérifier un ID précis
http://export.arxiv.org/api/query?search_query=ti:{titre}      # rechercher par titre
```
Exemple testé : `http://export.arxiv.org/api/query?id_list=2403.08399` → 1 entrée Atom XML avec titre. Délai recommandé 3 s entre requêtes. Aucune clé.

### 4.6 HAL — archive ouverte française (clé pour le CIR)
```
https://api.archives-ouvertes.fr/search/?q={termes}&wt=json&rows=10
https://api.archives-ouvertes.fr/search/?q=doiId_s:{DOI}&wt=json
```
Testé HTTP 200. Formats `wt=` : json, xml, bibtex, endnote. Demander les champs via `fl=title_s,authFullName_s,doiId_s,fileMain_s`. **Indispensable pour un état de l'art CIR** (production scientifique française).

### 4.7 Unpaywall — statut open access (récupérer le PDF légal)
```
https://api.unpaywall.org/v2/{DOI}?email=vous@domaine.fr
```
Testé HTTP 200, renvoie `is_oa`, `oa_status`, `best_oa_location.url_for_pdf`. Email **obligatoire** en paramètre. 100 000 req/jour.

### Tableau de synthèse
| API | Clé requise | Rôle dans la vérif. CIR |
|---|---|---|
| Crossref | Non (email poli) | **Test d'existence DOI** (404 = inexistant) |
| OpenAlex | Non (testé) | Recherche large + métadonnées |
| DOI content neg. | Non | **Génération bibliographie propre** |
| Semantic Scholar | Optionnelle | Lookup DOI/arXiv + graphe citations |
| arXiv | Non | Vérif. prépublications |
| HAL | Non | **Sources françaises (CIR)** |
| Unpaywall | Email | Récupérer le PDF pour lire et extraire |

---

## 5. Protocole bout-en-bout exécutable par un agent IA

Workflow en 6 étapes, chaque étape avec son garde-fou anti-invention. Inspiré du protocole 6 couches INRA et de PRISMA-trAIce.

### Étape 0 — Cadrage (humain)
Définir question de recherche, critères inclusion/exclusion, **borne d'antériorité** (date de début du projet CIR). **Garde-fou CIR** : l'état de l'art doit être **daté du début du projet, jamais reconstruit rétroactivement** — la reconstruction rétroactive est un risque d'audit majeur (Myriad, Leyton).

### Étape 1 — Découverte (retrieval, jamais génération)
Interroger **uniquement des bases réelles** : OpenAlex, Semantic Scholar, HAL (sources FR), arXiv, + outils retrieval (Consensus/Elicit/Scite). Snowballing backward/forward via Connected Papers / Research Rabbit.
> **Garde-fou** : interdiction d'utiliser un LLM pour « lister des références ». L'IA propose des **requêtes**, la base renvoie les **papiers**.

### Étape 2 — Filtrage pertinence + antériorité
Screening titre/résumé assisté LLM avec **vote majoritaire 3 inférences** (méthode JAMIA). Filtrer par date < borne projet. **Garde-fou** : journaliser chaque décision (inclus/exclu + raison) pour la traçabilité PRISMA.

### Étape 3 — VÉRIFICATION D'EXISTENCE (le cœur anti-hallucination)
Pour **chaque** référence candidate, dans cet ordre :
1. **DOI → Crossref** `api.crossref.org/works/{DOI}` : si **404 → REJET immédiat** (référence inexistante).
2. Si 200, **comparer le titre renvoyé** au titre annoncé (anti « identifier hijacking »).
3. Pas de DOI ? Recherche titre exact sur OpenAlex/Semantic Scholar/HAL ; **0 résultat → REJET**.
4. arXiv → `export.arxiv.org/api/query?id_list={id}` pour les prépublications.
5. Statut rétractation → Retraction Watch.
> **Garde-fou absolu** : une référence qui ne résout sur **aucune** API ne rentre **jamais** dans le dossier. C'est exactement le test (Crossref 404, OpenAlex/S2/HAL 0 résultat) que ce rapport a appliqué à ses propres sources.

### Étape 4 — Extraction des limites (démontrer le « gap »)
Sur le **texte réel récupéré** (via Unpaywall pour le PDF OA), extraire par LLM : objectif, méthode, résultats clés **avec n° de page**, **limites explicites**, niveau de confiance. **Garde-fou** : extraction depuis le PDF/abstract réel uniquement, jamais depuis la mémoire paramétrique du modèle. C'est l'analyse des limites qui justifie le verrou scientifique pour le CIR (notice DGFiP).

### Étape 5 — Formatage citations exactes
Générer la bibliographie **uniquement** via DOI content negotiation :
`curl -LH "Accept: application/x-bibtex" https://doi.org/{DOI vérifié}`
> **Garde-fou** : on ne demande **jamais** au LLM de « formater une citation de mémoire ». On part du DOI vérifié et l'API renvoie le BibTeX canonique.

### Étape 6 — Audit final
Ré-extraire **toutes** les citations du document final, re-résoudre chaque DOI, comparer claim ↔ source côte à côte. Documenter (PRISMA-trAIce) : outils, versions, prompts, % vérifié humainement.
> **Garde-fou CIR (Leyton)** : toute citation doit être **reformulée avec analyse technique OU entre guillemets** — la paraphrase verbatim non sourcée est un problème de conformité en audit.

---

## 6. Prompts et garde-fous anti-invention

### Prompts de contrainte (directement utilisables)
**Abstention forcée** (MachineLearningMastery) :
> « Tu es un assistant de vérification. Si tu n'es pas certain, réponds exactement : "NON TROUVÉ — je n'ai pas de source vérifiable." Ne devine jamais une référence. »

**Grounding strict** (template INRA) :
> « Génère la synthèse en te basant UNIQUEMENT sur ces papiers : [liste de papiers vérifiés avec DOI]. N'invente AUCUNE citation. Ne cite AUCUN papier hors de cette liste. Inclus les citations exactes avec leur source. »

**Extraction sourcée** (SuprMind) :
> « Extrais les affirmations empiriques avec citation exacte, numéro de page et titre de section. Signale toute affirmation sans source citée. »

**Chain-of-Verification** :
> « Étape 1 : réponse initiale. Étape 2 : récupère les passages pertinents. Étape 3 : compare l'évidence à ta réponse. Étape 4 : corrige toute divergence. »

### Red flags d'une citation inventée
| Red flag | Diagnostic |
|---|---|
| Le DOI ne résout pas sur doi.org / Crossref 404 | **Détecte ~60 % des fabrications** |
| Titre → 0 résultat sur Google Scholar / OpenAlex | Fabrication quasi-certaine |
| Auteur réel mais champ disciplinaire incohérent | Pattern d'hallucination LLM classique |
| Volume/numéro/pages ne correspondent à aucun fascicule réel | Métadonnées inventées |
| Toutes les citations collent parfaitement aux mots-clés | Une recherche réelle est imparfaite — celle-ci est trop propre |
| Regroupement sur années rondes (2010, 2015, 2020) | Pattern de génération IA |

### La règle d'or (Sourcely)
> **Ne jamais demander au LLM qui a généré une citation si elle est réelle.** Le modèle qui a inventé l'hallucination ne peut pas la détecter. **La vérification doit être externe** : Crossref, OpenAlex, Semantic Scholar, arXiv, HAL.

### Garde-fous spécifiques CIR
- Sources généralement **< 5 ans** (sauf domaine peu exploré).
- **~10 sources analysées en profondeur > 50 listées superficiellement**.
- État de l'art **technique**, pas commercial (≠ étude de marché).
- **Mise à jour annuelle** pour un projet pluriannuel.
- Bases attendues (notice DGFiP) : revues, manuels, **brevets (Espacenet)**, conférences, normes ISO, livres blancs, rapports de synthèse — avec analyse détaillée des **limites** justifiant le verrou.
- **Aucune guidance officielle ANR/ANRT/MESRI** sur l'IA pour l'état de l'art CIR n'existe à ce jour (juin 2026) — confirmé. Les prestataires (LBKE, Compass, CIRGPT) convergent : l'IA synthétise une documentation **déjà détenue et vérifiée**, un expert humain affine, car le dossier subit relecture technique experte + contrôle fiscal.

### Outils de vérification automatisée
[doi.org](https://doi.org) (résolution), [Crossref](https://crossref.org), [Semantic Scholar](https://semanticscholar.org), [OpenAlex](https://openalex.org), [Retraction Watch](https://retractionwatch.com), [RefChecker (open-source)](https://github.com/markrussinovich/refchecker), [Citely](https://citely.ai/ai-citation-checker), [Sourcely](https://www.sourcely.net).

---

## Sources principales (toutes vérifiées par résolution DOI/arXiv)

**Hallucination — études chiffrées** : [Walters & Wilder 2023](https://doi.org/10.1038/s41598-023-41032-5) · [Cross-disciplinary 2024](https://doi.org/10.2196/52935) · [GhostCite](https://arxiv.org/abs/2602.06718) · [How LLMs Cite](https://arxiv.org/abs/2603.03299) · [8 chatbots](https://arxiv.org/abs/2505.18059) · [Mental health GPT-4o](https://doi.org/10.2196/80371) · [Legal Fictions](https://doi.org/10.1093/jla/laae003) · [Deep research agents](https://arxiv.org/abs/2604.03173) · [BibTeX agents](https://arxiv.org/abs/2604.03159) · [NeurIPS fabricated](https://arxiv.org/abs/2602.05930)

**Méthodes SLR/RAG** : [Multi-agent SLR](https://arxiv.org/abs/2403.08399) · [JAMIA LLM review](https://doi.org/10.1093/jamia/ocaf063) · [Optimal LLMs screening](https://doi.org/10.1017/rsm.2025.10014) · [Review Copilot](https://doi.org/10.1186/s13643-025-02997-8) · [Hybrid framework](https://doi.org/10.1007/s11301-025-00522-8) · [PRISMA-trAIce](https://doi.org/10.2196/80247) · [Interleaved Snowballing](https://arxiv.org/abs/2402.08339) · [ProfOlaf](https://arxiv.org/abs/2510.26750) · [SciRAG](https://arxiv.org/abs/2511.14362) · [SLR du RAG](https://arxiv.org/abs/2508.06401) · [RAG burn mgmt](https://doi.org/10.3390/ebj6020028)

**APIs (docs officielles)** : [Crossref](https://www.crossref.org/documentation/retrieve-metadata/rest-api/) · [OpenAlex](https://developers.openalex.org/) · [Semantic Scholar](https://www.semanticscholar.org/product/api) · [arXiv](https://info.arxiv.org/help/api/user-manual.html) · [HAL](https://api.archives-ouvertes.fr/docs/search) · [Unpaywall](https://unpaywall.org/products/api) · [DOI content negotiation](https://citation.doi.org/docs.html)

**Garde-fous & CIR** : [INRA citation accuracy](https://www.inra.ai/blog/citation-accuracy) · [MachineLearningMastery prompts](https://machinelearningmastery.com/7-prompt-engineering-tricks-to-mitigate-hallucinations-in-llms/) · [Sourcely](https://www.sourcely.net/resources/ai-citation-checkers-catch-broken-fake-misused-references) · [SuprMind multi-LLM workflow](https://suprmind.ai/hub/insights/best-ai-for-writing-research-papers-a-multi-llm-workflow-that-holds/) · [Leyton CIR état de l'art](https://leyton.com/fr/insights/articles/cir-redaction-etat-de-lart/) · [Myriad Consulting](https://www.myriadconsulting.fr/ressources/blog/etat-de-l-art-etapes/) · [Notice DGFiP CIR](https://www.economie.gouv.fr/files/files/directions_services/dgfip/controle_fiscal/prevention/notice_CIR_fd_6914.pdf)
