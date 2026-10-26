# Spécification du pipeline — v2 minimale (21/10/2026)
Contrat d'implémentation pour Claude Code. Toute divergence doit être signalée avant d'être codée.
**Règle : le plus simple possible.** Tout ce qui n'est pas indispensable aux consignes va dans la section 5 (« Limites et pistes pour une v2 »), qui alimente directement le rapport.
Les versions précédentes sont dans git (v1 : commit `28e7b16`).

## 0. Consignes du sujet 2 → ce que fait le pipeline
| Consigne | Réponse minimale |
|---|---|
| **Pipeline IA de la revue de la littérature jusqu'au rapport structuré** | Revue **ciblée manuelle** (4 documents, critères dans `corpus.md`) → ingestion (WF00) → **RAG** : extraction automatique des passages pertinents par section (exemple « Système RAG » de la consigne) → rédaction par section avec citations → assemblage d'un argumentaire structuré + bibliographie |
| **Contrôle qualité des résultats de l'IA** | (1) **Références vérifiées par construction** : le LLM cite des `chunk_id`, la bibliographie est générée par le code (exemple « vérification de références » de la consigne) ; (2) **garde-fous automatiques** G1 structure, G2 citations, G4 chiffres, G5 formulations absolues ; (3) **agent relecteur** (un appel LLM, rapport de relecture) ; (4) **évaluation humaine** sur échantillon avec kappa ; (5) **comparaison avec une baseline** (LLM seul) |
| **Critiquer les résultats** | Tableau de métriques pipeline vs baseline, exemples d'échecs (paragraphes signalés, références inventées par la baseline), limites (section 5) |

Corpus **figé à 4 documents** (D06 Apple, D07 FDA K250507, D09 Elgendi, D12 AHA), déjà ingérés (187 chunks avec `chunk_id`). **Aucune nouvelle ingestion.**

## 1. Principes
- **Le LLM n'écrit jamais une référence** : il cite des `chunk_id`, et la bibliographie vient de `corpus/meta.json`.
- **Prompts versionnés** dans `prompts/` : `redacteur_v1.md`, `relecteur_v1.md`, `baseline_v1.md`, ainsi que `sections.json` (déjà fait). Ils seront reproduits en annexe.
- **Pas de boucle** : ni régénération automatique, ni correction automatique. Les garde-fous et le relecteur **détectent et signalent**, sans corriger. C'est plus simple et plus lisible pour l'oral.
- **Traçabilité minimale** : une ligne par exécution dans `outputs/runs.jsonl` (run_id, horodatage, modèle, versions des prompts, nombre d'appels de chat et d'embeddings, durée).
- **Quotas Gemini du plan gratuit**, relevés le 26/10/2026 sur https://ai.dev/rate-limit. Remise à zéro quotidienne à minuit, heure du Pacifique : 8 h à Paris jusqu'au 01/11 inclus, 9 h à partir du 02/11 (fin de l'heure d'été américaine).

  | Modèle | Requêtes / min (RPM) | Tokens / min (TPM) | Requêtes / jour (RPD) |
  |---|---|---|---|
  | `gemini-3.8-flash` (rédacteur, relecteur, baseline) | 5 | 250 000 | **20** |
  | `gemini-embedding-001` (ingestion, requêtes de recherche) | 100 | 30 000 | 1 000 |

  - *Wait* de **15 s** entre deux appels de chat (60 s / 5 RPM = 12 s, plus une marge).
  - Une exécution complète de `10-argumentaire` fait **9 appels de chat** (8 sections + conclusion) et 28 requêtes d'embeddings. Avec le relecteur et la baseline : **11 appels de chat**, plus de la moitié du quota du jour.
  - Donc : les essais portent sur 1 ou 2 sections (paramètre en tête de `10-argumentaire`), **aucune exécution complète sans l'accord du groupe**, et l'exécution finale officielle se fait un jour où le quota est entier (section 4).
- Rédaction en **français** ; requêtes de recherche fixes en **anglais** (`sections.json`).

## 2. Workflows n8n

### WF00 — Ingestion (`00-ingestion`)
Manual Trigger → lecture de `meta.json` → *Split Out* (un item par document) → *Read Files from Disk* → *Extract from File* (PDF, texte **page par page**) → Code **Nettoyage du texte** → Code (un item par page, avec les métadonnées de `meta.json`) → *Loop Over Items* (**lots de 6 pages**) → *Qdrant Vector Store* (insertion, collection `moa_corpus`) → *Wait* **60 s** (quota d'embeddings) → lot suivant. En fin de boucle : étape **`chunk_id`** (voir ci-dessous).
- Sous-nœuds du *Qdrant Vector Store* : *Default Data Loader* (JSON) ; *Recursive Character Text Splitter* (1 000 caractères, chevauchement de 150, **à justifier dans le rapport** ; découpage page par page, donc un chunk ne chevauche jamais deux pages) ; *Embeddings Google Gemini* (`gemini-embedding-001`, **3 072 dimensions**, non réglable dans le nœud ; la collection Qdrant est créée en 3 072, distance cosinus).
- Lots de 6 pages : ≈ 60 chunks au plus par minute, sous le quota de 100 embeddings par minute. Si un lot dépasse le quota, LangChain renvoie des vecteurs vides sans erreur et c'est Qdrant qui refuse l'insertion (422).
- **Nettoyage avant découpage** (par document) :
  - **bibliographie** : coupe à partir du dernier titre « References » (ou « Bibliography ») situé dans la seconde moitié du document, jusqu'au premier tableau ou à la première figure qui suit (manuscrits PMC) ou jusqu'à la fin ; puis suppression des pages finales sans titre où les marqueurs bibliographiques (« et al. », « doi », année entre parenthèses) dépassent 3 pour 1 000 caractères (notes de fin) ;
  - **appels de référence** : lignes ne contenant qu'un numéro d'appel (pdf.js isole les exposants sur leur propre ligne) et appels entre crochets `[12]`, `[3–5]` ; un chiffre seul qui suit un symbole court est un indice ou un exposant (`kg/m2`, `K1`) et il est recollé, pas supprimé ;
  - **césures** : `mot-\nsuite` est recollé seulement si le mot entier existe ailleurs dans le document ; sinon c'est un mot composé (`machine-learning`, `non-hypertensive`) et le trait d'union est gardé ;
  - le nœud renvoie, par document, les caractères avant et après, la bibliographie retirée, le nombre d'appels supprimés et de césures recollées.
- Métadonnées de chaque chunk : `chunk_id`, `doc_id`, `fichier`, `page`, `annee`, `type_source`, `versant`, `role`.
- **`chunk_id` = `<doc_id>-<8 premiers caractères du SHA-1 du texte du chunk>`** (ex. `D12-4794f2ff`) : stable d'une réingestion à l'autre tant que le texte du chunk ne change pas. Le découpage se fait dans un sous-nœud LangChain qui ne numérote pas les chunks : le `chunk_id` est donc ajouté **après** l'insertion, sans appel à Gemini :
  HTTP Request « Points sans chunk_id » (`scroll` filtré sur `is_empty: metadata.chunk_id`, exécuté une seule fois) → *Split Out* → *Crypto* (SHA-1 du texte) → Code (une opération `set_payload` par point, avec `key: metadata`) → HTTP Request `points/batch` (un seul appel) → HTTP Request : index de payload `keyword` sur `metadata.chunk_id`.
  Étape idempotente : elle ne traite que les points sans `chunk_id`. Le Code compte les doublons (chunks au texte identique dans un même document, donc même `chunk_id`).
  ⚠️ Pas de sous-workflow : lancé par la CLI (`n8n execute`), n8n 2.x n'appelle que la version **publiée** d'un sous-workflow, alors que l'interface utilise le brouillon.
- L'ingestion n'est pas idempotente : supprimer la collection `moa_corpus` avant de réingérer, sinon les chunks sont en double.
- Contrôle : nombre de chunks par document, et signalement de tout document dont le texte extrait fait moins de 500 caractères (PDF scanné, donc OCR nécessaire).

Statut : **terminé**, à ne plus modifier sauf en cas de bug.

### WF10 — `10-argumentaire` (un seul workflow)
Manual Trigger → **Paramètres** (nœud en tête : modèle et **liste des sections à générer**, pour déboguer sur 1 ou 2 sections ; décision du 26/10/2026) → lecture de `prompts/sections.json` et de `corpus/meta.json` → *Loop Over Items* sur les sections (hors conclusion), avec pour chaque section :

**A. Récupération dans Qdrant** (paramètres dans `prompts/sections.json`, décision du 17/10/2026) :
   - **2 ou 3 requêtes par section** (angles différents), **en anglais** comme le corpus, **fixes** (pas d'appel au LLM pour les formuler) ; la rédaction reste en français ;
   - **top-k 15** par requête ;
   - **requête forcée `role = contre`** (une par section, filtre Qdrant `metadata.role = contre`, top-k 15) : ses **2 meilleurs chunks sont garantis** dans la sélection, pour que l'argumentaire traite les contre-arguments ;
   - fusion et **dédoublonnage par `chunk_id`** (score maximal conservé), puis sélection par score décroissant avec un **plafond de 2 chunks par document**, jusqu'à **10 chunks** au plus ;
   - pas de MMR : un plafond codé dans un nœud Code est déterministe et plus simple à expliquer.
   Pourquoi : au test du 17/10/2026, le top 5 venait d'un seul document (D12), et D06 (performances d'Apple) n'apparaissait pas.

**B. Rédacteur** (Gemini, prompt `redacteur_v1.md`). Il reçoit la section, la consigne, la position POUR et les chunks avec leur `chunk_id`. Appel par un nœud **HTTP Request** direct à `generateContent` (credential Gemini de n8n), modèle **`gemini-3.8-flash`**, en **mode JSON avec schéma** (`responseMimeType` + `responseSchema`) ; réponse complète conservée même en cas d'erreur HTTP (429, 5xx…), pour que G1 la signale. Délai maximal de **600 s** par appel (180 s au départ, dépassé le 26/10). Un délai dépassé **arrête l'exécution** : le mode « continuer après erreur » de n8n renverrait l'objet d'erreur brut, sans masquer la requête, donc avec la clé. Il renvoie :
```json
{"section": "technique",
 "paragraphes": [{"texte": "...", "citations": ["D06-1a2b3c4d"]}],
 "contre_arguments_traites": ["D12-9f8e7d6c"]}
```
Règles du prompt :
- toute affirmation factuelle cite au moins un `chunk_id` fourni ;
- aucune connaissance extérieure ;
- si l'information manque, écrire `[INFORMATION NON DISPONIBLE DANS LE CORPUS]`.

**C. Garde-fous** (un seul nœud Code, sans coût, **sans nouvelle tentative**) :
| Garde-fou | Contrôle |
|---|---|
| **G1 Structure** | JSON valide, champs présents, au moins un paragraphe |
| **G2 Citations** | chaque `chunk_id` cité fait partie des chunks récupérés ; un paragraphe sans citation déclenche une alerte |
| **G4 Chiffres** | chaque nombre ou pourcentage d'un paragraphe figure dans un chunk qu'il cite |
| **G5 Formulations absolues** | aucune formulation interdite par la règle 7 de `redacteur_v1.md` : « prouve » et ses formes (prouvé, prouvent…), « toujours », « aucun risque ». Simple liste de mots, sans analyse du contexte |

Un paragraphe en défaut est **conservé et marqué `⚠`** dans l'argumentaire ; le détail va dans `verif_<run_id>.json`.

**D.** *Wait* de 15 s (quota), puis section suivante.

**Conclusion** : un appel au rédacteur avec les sections déjà générées, sans nouvelle recherche, et un parti pris POUR clair. Il ne peut citer que des `chunk_id` déjà utilisés (G1 + G2).
Branchée **après la boucle** (choix du 26/10/2026) : IF « Conclusion demandée ? » → Code « Chunks déjà cités » → mêmes nœuds Prompt, Rédacteur et Garde-fous que les sections (G4 et G5 s'appliquent donc aussi) → IF « Conclusion ? » → Assemblage.
- Ses extraits sont les chunks cités par les paragraphes et les contre-arguments traités des sections.
- Les sections rédigées, avec les `chunk_id` cités par chaque paragraphe, sont ajoutées à la suite de la consigne (`{{CONSIGNE}}`), faute d'autre emplacement dans `redacteur_v1.md`, qui reste inchangé.
- Un paragraphe de section marqué `⚠` est transmis tel quel.

**Relecteur** (option A, décision du 26/10/2026) : **un seul appel** Gemini, prompt distinct `relecteur_v1.md`. Il reçoit :
- l'argumentaire assemblé ;
- la consigne ;
- le texte des chunks cités ;
- l'année de chaque document (depuis `meta.json`).

Grille :
- conformité à la structure ;
- contre-arguments non traités ;
- sur-affirmations ;
- équilibre entre versants ;
- clarté de la conclusion.

Il renvoie une **liste de problèmes** en JSON (`{section, gravite: haute|moyenne|basse, probleme}`), **sans réécriture ni correction automatique**. Sortie : `relecture_<run_id>.json`.

**Assemblage** (nœud Code, avant le relecteur) :
- les sections sont mises dans l'ordre de la consigne ;
- les `chunk_id` deviennent des numéros [n] ;
- la bibliographie est générée depuis `meta.json`.

Sortie : `outputs/argumentaire_<run_id>.md`, plus une ligne dans `runs.jsonl`. La conversion en PDF se fait avec Pandoc, hors n8n.

### WF50 — `50-baseline`
Un seul appel Gemini, même modèle, même consigne, même structure, position POUR, prompt `baseline_v1.md`, **sans RAG ni garde-fous**. On lui demande de **citer ses sources**, pour pouvoir compter les références inventées. Sortie : `outputs/baseline_<run_id>.md`.

## 3. Évaluation — script `eval/evaluer.py` (hors n8n)
Sortie : `outputs/metriques.csv`

| Métrique | Pipeline | Baseline | Mode |
|---|---|---|---|
| Sections imposées présentes | | | auto |
| Références existantes et correctes | 100 % par construction | **vérification manuelle de chaque référence** | manuel |
| Paragraphes avec au moins une citation | | | auto |
| Paragraphes signalés `⚠` (G2/G4/G5) | | non applicable | auto |
| `[INFORMATION NON DISPONIBLE]` | | | auto |
| Problèmes relevés par le relecteur, par gravité | | non applicable | auto |
| Nombre d'appels, durée | | | auto |

**Évaluation humaine** :
- le script tire au hasard **15 affirmations** du pipeline et produit `outputs/eval_humaine.csv` (affirmation, chunk cité, texte du chunk) ;
- **2 membres du groupe** les jugent indépendamment : `SOUTENU`, `PARTIEL` ou `NON_SOUTENU` ;
- le script calcule le **kappa de Cohen**. Compter environ 45 min.

## 4. Ordre de construction
| # | Étape | Estimation |
|---|---|---|
| 0 | Test de fumée du modèle de chat Gemini et relevé de son RPM | 15 min |
| 1 | `10-argumentaire` sur la **seule section « technique »** : récupération, rédacteur, G1, G2, G4, assemblage minimal, premier Markdown | 2,5 h |
| 2 | Toutes les sections + conclusion | 1 h |
| 3 | Relecteur | 0,5 h |
| 4 | `50-baseline` | 0,5 h |
| 5 | `eval/evaluer.py` + feuille d'évaluation humaine | 1 h |
| 6 | Évaluation humaine (groupe) | 0,75 h |
| | **Pipeline** | **≈ 6,5 h** |

**Exécution finale officielle** (après les étapes 3 et 4 déboguées sur 1 ou 2 sections) : toutes les sections, puis le relecteur, puis la baseline, **le même jour**, un jour où le quota de chat est entier (aucun essai ce jour-là avant l'exécution), après la remise à zéro de 8 h (9 h à partir du 02/11). Elle consomme 11 appels sur 20, ce qui laisse une marge pour une seule relance en cas d'erreur 429 ou 5xx. Elle n'est lancée qu'avec l'accord du groupe. Ses fichiers sont ceux du rapport.

Après chaque étape : `n8n/exporter.sh`, commit, et une ligne dans le journal de `implémentation.md`.

**À garder pour le rapport et l'oral** :
- une capture de `10-argumentaire` ;
- un paragraphe signalé par G2 ou G4 ;
- un problème relevé par le relecteur ;
- une référence inventée par la baseline ;
- les prompts (annexe).

## 5. Limites et pistes pour une v2
À reprendre dans la partie « Critique des résultats » du rapport. **Toute simplification décidée en cours de route doit être ajoutée ici.**

| Non fait en v1 | Conséquence (limite) | Piste v2 |
|---|---|---|
| Recherche bibliographique automatisée (équations générées par LLM, PubMed / Europe PMC, screening des abstracts) | Revue ciblée manuelle, non exhaustive, avec un biais de sélection possible | Workflow de recherche PubMed + screening par double LLM, avec arbitre (exemple « multi-agents » de la consigne) + diagramme PRISMA |
| Corpus de 4 documents (au lieu des ~20 identifiés dans `corpus.md`) | Sections éthique, socio-économique et réglementaire pauvres ; un seul document « contre » | Ingérer le corpus complet (quota d'embeddings, idempotence de l'ingestion) |
| Système multi-agents (2 rédacteurs + superviseur) | Un seul point de vue de génération | 2 rédacteurs de modèles différents + arbitre en cas de discordance |
| Juge LLM indépendant de fidélité (G3, autre famille de modèle) | Fidélité contrôlée seulement par G4 (chiffres) et par 15 affirmations notées à la main. **Pas de juge de fidélité : les ajouts non sourcés et les liens inventés entre sources ne sont repérés que par le relecteur et l'évaluation humaine** | Juge d'une autre famille de modèle (biais d'auto-préférence de LLM-as-a-judge) ; métriques RAGAS / FActScore |
| Pas de relance ni de signalement par G1 quand un appel au rédacteur dépasse le délai ou échoue au niveau réseau | Toute l'exécution s'arrête, sans fichier de sortie (26/10 : plus de 180 s pour la section « éthique ») | Relance bornée, ou mode « continuer après erreur » avec un filtrage de l'objet d'erreur |
| Détection des formulations absolues (G5) par une simple liste de mots, sans analyse du contexte | Faux positifs : « pas toujours », formule prudente, est signalée. Faux négatifs : « outil de repérage robuste et rigoureusement validé » (exécution du 21/10) passe | Repérage par le relecteur, ou classifieur de sur-affirmations |
| Boucle de régénération après garde-fous et correction après relecture | Les défauts sont signalés, pas corrigés | Boucle bornée (2 itérations) + comparaison avant / après |
| Relecteur de la même famille de modèle que le rédacteur | Risque de complaisance | Relecteur d'un autre fournisseur |
| Une seule exécution | Variabilité des sorties non mesurée | 3 à 5 exécutions, stabilité des citations et des conclusions |
| `task_type` des embeddings Gemini non utilisé, pas de MMR | Retrieval perfectible (compensé par plusieurs requêtes et un plafond par document) | Appel direct de l'API avec `RETRIEVAL_QUERY` / `RETRIEVAL_DOCUMENT`, reranking |
| Évaluation humaine sur 15 affirmations | Faible puissance statistique | Échantillon plus large, évaluateurs externes (cliniciens) |
| Modèle Pro non utilisé : `gemini-3.1-pro` est fermé au plan gratuit (quota à 0, test du 21/10/2026) | Rédaction et relecture par un modèle Flash (`gemini-3.8-flash`) | Modèle Pro (offre payante), à comparer sur les mêmes sections |
| API externe (Gemini) pour le LLM et les embeddings | Envoi du texte du corpus (publications, pas de données patients) à un fournisseur hors UE | Modèle local (Ollama) ou fournisseur européen sous contrat |
