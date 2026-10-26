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
- **Traçabilité minimale** : une ligne par exécution dans `outputs/runs.jsonl` (run_id, horodatage, modèle, versions des prompts, nombre d'appels de chat et d'embeddings, **tentatives par section et pour le relecteur**, durée). La ligne est écrite à la fin, après le relecteur.
- **Quotas Gemini du plan gratuit**, relevés le 26/10/2026 sur https://ai.dev/rate-limit. Remise à zéro quotidienne à minuit, heure du Pacifique : 8 h à Paris jusqu'au 01/11 inclus, 9 h à partir du 02/11 (fin de l'heure d'été américaine).

  | Modèle | Requêtes / min (RPM) | Tokens / min (TPM) | Requêtes / jour (RPD) |
  |---|---|---|---|
  | `gemini-3.8-flash` (rédacteur, relecteur, baseline) | 5 | 250 000 | **20** |
  | `gemini-embedding-001` (ingestion, requêtes de recherche) | 100 | 30 000 | 1 000 |

  - *Wait* de **15 s** entre deux appels de chat (60 s / 5 RPM = 12 s, plus une marge).
  - Une exécution complète de `10-argumentaire` fait **10 appels de chat** (8 sections, conclusion, relecteur) et 28 requêtes d'embeddings. Avec la baseline : **11 appels de chat**, plus de la moitié du quota du jour. Chaque appel peut être relancé une fois (429 ou 5xx), donc 22 au pire.
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

**B. Rédacteur** (Gemini, prompt `redacteur_v1.md`). Il reçoit la section, la consigne, la position POUR et les chunks avec leur `chunk_id`. Appel par un nœud **HTTP Request** direct à `generateContent` (credential Gemini de n8n), modèle **`gemini-3.8-flash`**, en **mode JSON avec schéma** (`responseMimeType` + `responseSchema`) ; réponse complète conservée même en cas d'erreur HTTP (« ne jamais lever d'erreur »). Délai maximal de **600 s** par appel (180 s au départ, dépassé le 26/10).
- **Relance unique** (décision du 26/10/2026) : IF « Relancer le rédacteur ? » (HTTP 429 ou 5xx) → *Wait* 60 s → « Rédacteur (2e tentative) » (copie du nœud HTTP) → garde-fous. Un second échec est signalé par G1. Le nombre de tentatives (1 ou 2) va dans `verif` et `runs.jsonl`. Le « Retry On Fail » de n8n ne convenait pas : attente plafonnée à 5 s par le moteur, pas de relance sur un 503 reçu en mode « ne jamais lever d'erreur », tentatives invisibles.
- **Délai dépassé** : pas de relance, car après 600 s l'API est saturée. Le nœud est en « continuer après erreur », donc l'erreur est signalée par G1 sans arrêter l'exécution. Ce mode est sans risque : un test du 26/10 montre que l'objet d'erreur ne contient que le message et la cause, ni l'URL, ni les paramètres, ni les en-têtes. La clé n'y figure pas.

Il renvoie :
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
| **G5 Formulations absolues** | liste de mots, élargie le 26/10 au-delà de la règle 7 de `redacteur_v1.md`. Termes signalés :<br>• « prouve » et « démontre » (et leurs formes) ;<br>• « toujours », « aucun risque » ;<br>• « robuste », « rigoureusement », « solide(s) », « incontestable » ;<br>• « garanti » (et ses formes) ;<br>• « certainement », et « certain » en emploi affirmatif (« est certain »), pas comme quantificateur (« certains patients »).<br>Les formes niées (« pas toujours », « non prouvé », « n'a pas été démontré ») ne sont pas signalées |

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
- **affirmations non soutenues par les chunks cités** (ajout du 26/10) ;
- **liens et chronologie entre sources, d'après les années des documents** (ajout du 26/10) ;
- équilibre entre versants ;
- clarté de la conclusion.

Il renvoie une **liste de problèmes** en JSON (`{section, gravite: haute|moyenne|basse, probleme}`), **sans réécriture ni correction automatique**. Sortie : `relecture_<run_id>.json`.
- Nœuds : Écrire dans `outputs/` → *Wait* 15 s → Prompt du relecteur → Relecteur (HTTP, mode JSON avec schéma) → même relance unique que le rédacteur (429 ou 5xx, *Wait* 60 s, « Relecteur (2e tentative) ») → Relecture et traces (`relecture_<run_id>.json` + ligne de `runs.jsonl`).
- Les extraits lui sont donnés avec le même renvoi `[n, p. X]` que dans le Markdown, avec le document et son année.
- Le prompt définit la gravité :
  - haute : affirmation non soutenue, lien inventé, erreur ;
  - moyenne : sur-affirmation, contre-argument non traité ;
  - basse : structure, équilibre, clarté.
- Le prompt demande de citer entre guillemets le passage en cause.

**Assemblage** (nœud Code, avant le relecteur) :
- les sections sont mises dans l'ordre de la consigne ;
- les `chunk_id` deviennent des numéros [n] ;
- la bibliographie est générée depuis `meta.json`.

Sortie : `outputs/argumentaire_<run_id>.md` et `verif_<run_id>.json`, écrits avant le relecteur ; la ligne de `runs.jsonl` est écrite après lui. La conversion en PDF se fait avec Pandoc, hors n8n.

### WF50 — `50-baseline`
Un seul appel Gemini, même modèle, même consigne, même structure, position POUR, prompt `baseline_v1.md`, **sans RAG ni garde-fous**. On lui demande de **citer ses sources**, pour pouvoir compter les références inventées. Sortie : `outputs/baseline_<run_id>.md`.

Mise en œuvre (26/10/2026) :
- **Chaîne** : Paramètres → lecture de `sections.json` et `baseline_v1.md` → Prompt → HTTP `generateContent` → même relance unique que le pipeline (429 ou 5xx, *Wait* 60 s) → Assemblage → fichiers.
- **Paramètres** : modèle, et sections à générer. Par défaut les 9 sections, à aligner sur l'exécution de `10-argumentaire` comparée.
- **Mode JSON avec schéma**, comme le rédacteur : `sections` → `paragraphes` `{texte, references: [n]}`, plus une liste `references` `{numero, reference}`.
- **Prompt** : il reprend les règles de `redacteur_v1` qui ne dépendent pas du corpus (chiffres exacts, `[INFORMATION NON DISPONIBLE]`, contre-arguments, pas de formulation absolue, 3 à 6 paragraphes de 60 à 150 mots). Il interdit d'inventer des références, comme `redacteur_v1` interdit d'inventer des `chunk_id`.
- **Sorties** :
  - `baseline_<run_id>.md`, avec les références marquées « non vérifiées » ;
  - `baseline_<run_id>.json`, la sortie brute, pour `eval/evaluer.py` ;
  - une ligne dans `runs.jsonl`.
- Testé avec un appel simulé (503 puis relance).

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

**G5 n'est évalué que sur l'exécution finale.** Sa liste de termes a été construite à partir des défauts du 21/10 et du 26/10, puis testée sur ces mêmes sorties. Son score sur ces sorties (« 6 paragraphes sur 9, sans faux positif ») ne mesure donc pas sa performance : c'est du surajustement. **La liste est gelée depuis le 26/10.**

**Relecteur contre liste de défauts de référence** (pour le rapport : « X défauts confirmés repérés par le relecteur sur Y » ; protocole corrigé le 26/10) :
1. Claude relit les nouvelles sorties **avant** d'ouvrir `relecture_<run_id>.json`. Il écrit sa liste de défauts dans `outputs/defauts_reference_<run_id>.md`, avec pour chaque défaut l'affirmation, le chunk cité, le défaut et son type dans la grille. Il part des défauts déjà relevés (technique le 21/10, réglementaire le 26/10), à revérifier sur le nouveau texte.
2. **Un membre du groupe valide chaque défaut** (confirmé ou rejeté), sans avoir vu la sortie du relecteur.
3. Ensuite seulement, l'appariement. Un défaut confirmé est « repéré » si le relecteur cite le même passage avec un problème de même nature. Résultat : **X défauts confirmés repérés sur Y**. Les problèmes que le relecteur ajoute sont triés **par un humain** en vrais défauts et fausses alertes.
- Le cas QXO/SFR est compté à part : il est invisible depuis les extraits.
- À écrire dans le rapport : la liste de référence a été produite avec l'aide d'un LLM (Claude), puis validée par le groupe. Sans cette validation, la comparaison ne mesurerait que l'accord entre deux LLM, pas la détection de défauts réels. Une seule exécution : pas de valeur statistique.

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

**Prochaine exécution, le 27/10 après 8 h, avec l'accord du groupe** : technique, éthique, réglementaire et conclusion (4 appels), puis le relecteur (1 appel). Cela fait 5 appels de chat, 10 au plus avec les relances, et 11 requêtes d'embeddings. Les paramètres sont déjà réglés dans `10-argumentaire`.
- **Règle d'arrêt** : si le premier appel dépasse 3 minutes, ou renvoie un 503 malgré la relance, on arrête et on réessaie dans l'heure.
- Ensuite : comparaison avec le relecteur selon le protocole corrigé (section 3) ; la validation par le groupe peut se faire le 27/10 au soir.
- Derniers correctifs éventuels, **sans toucher à la liste de G5**. Tout correctif de prompt passe par une validation d'Adam.

**Échéance : pipeline prêt le 28/10 après-midi.**

**Exécution finale officielle** (après les étapes 3 et 4 déboguées sur 1 ou 2 sections) : toutes les sections, puis le relecteur, puis la baseline, **le même jour**, un jour où le quota de chat est entier (aucun essai ce jour-là avant l'exécution), après la remise à zéro de 8 h (9 h à partir du 02/11). Elle consomme 11 appels sur 20 sans relance. Avec les relances automatiques (une par appel au plus), le pire cas dépasse le quota : si plus de 9 relances sont nécessaires, il faut arrêter et reporter l'exécution. Elle n'est lancée qu'avec l'accord du groupe. Ses fichiers sont ceux du rapport.
- Prévue le **28/10 après 8 h**, avec la même règle d'arrêt.
- Suivie de `eval/evaluer.py` sur cette exécution.
- Ensuite, **gel** : plus aucune modification des prompts, de G5 ni des workflows.

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
| Une seule relance (429 ou 5xx), aucune après un délai dépassé | En cas de saturation durable de l'API (26/10 : 503 et un appel de 6 min 22 s), la section n'est pas rédigée ; elle est signalée par G1 | Relances espacées sur plusieurs minutes, ou offre payante |
| Détection des formulations absolues (G5) par une liste de mots, avec une négation simple (« pas », « non », « ne », « jamais »…) | Le contexte est ignoré. Faux positifs possibles (« un argument solide »). Sur-affirmations sans mot de la liste non repérées (« atteste », « répond à ces exigences ») | Repérage par le relecteur, ou classifieur de sur-affirmations |
| Liste de G5 construite à partir des défauts du 21/10 et du 26/10, puis testée sur ces mêmes sorties | **Surajustement** : « 6 paragraphes sur 9, sans faux positif » ne mesure pas la performance de G5. Seuls ses résultats sur l'exécution finale comptent, et la liste est gelée depuis le 26/10 | Construire la liste sur un jeu de développement, puis l'évaluer sur un jeu de test distinct, annoté à la main |
| Liste de défauts de référence écrite par un LLM (Claude), pour évaluer le relecteur | Sans validation humaine, on ne mesurerait que l'accord entre deux LLM. Chaque défaut est donc validé par un membre du groupe avant l'appariement ; l'échantillon reste petit (une exécution) | Annotation indépendante par deux cliniciens, avant toute sortie du relecteur |
| Corpus figé dans une version donnée de chaque document | **Fidélité ≠ exactitude** : « code produit QXO » (26/10) est fidèle au chunk de D07, mais périmé (remplacé par SFR dans la correction administrative du 12/09, absente du corpus). Ni les garde-fous ni le relecteur, qui ne voient que les extraits, ne peuvent le repérer | Ingérer les versions corrigées ; vérification humaine des faits réglementaires ; version du document dans les métadonnées |
| Pas de contrôle automatique des liens entre sources | **Défaut systématique** : le lien inventé AHA (déclaration de déc. 2025) → FDA (autorisation de sept. 2025) revient d'une exécution à l'autre (« pour répondre à ces exigences », 21/10 ; « l'autorisation répond à ces exigences », 26/10) | Années des documents données au rédacteur et règle explicite dans le prompt (`redacteur_v2`) ; repérage par le relecteur (option A) |
| Boucle de régénération après garde-fous et correction après relecture | Les défauts sont signalés, pas corrigés | Boucle bornée (2 itérations) + comparaison avant / après |
| Relecteur de la même famille de modèle que le rédacteur | Risque de complaisance | Relecteur d'un autre fournisseur |
| Une seule exécution | Variabilité des sorties non mesurée | 3 à 5 exécutions, stabilité des citations et des conclusions |
| `task_type` des embeddings Gemini non utilisé, pas de MMR | Retrieval perfectible (compensé par plusieurs requêtes et un plafond par document) | Appel direct de l'API avec `RETRIEVAL_QUERY` / `RETRIEVAL_DOCUMENT`, reranking |
| Évaluation humaine sur 15 affirmations | Faible puissance statistique | Échantillon plus large, évaluateurs externes (cliniciens) |
| Modèle Pro non utilisé : `gemini-3.1-pro` est fermé au plan gratuit (quota à 0, test du 21/10/2026) | Rédaction et relecture par un modèle Flash (`gemini-3.8-flash`) | Modèle Pro (offre payante), à comparer sur les mêmes sections |
| API externe (Gemini) pour le LLM et les embeddings | Envoi du texte du corpus (publications, pas de données patients) à un fournisseur hors UE | Modèle local (Ollama) ou fournisseur européen sous contrat |
