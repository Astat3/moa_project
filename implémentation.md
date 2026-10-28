# Implémentation — journal des étapes
Trace écrite de la construction du pipeline. Elle sert de matière première pour le **rapport** (partie « Méthodologie et difficultés ») et pour l'**oral**.

> Pour chaque étape, noter : **objectif · ce qu'on a fait · nœuds n8n utilisés · difficulté rencontrée · solution · capture d'écran à garder**.
> Les captures d'écran vont dans `captures/NN-nom.png`, pour le rapport et les slides.

---

## Vue d'ensemble
> **Plan v2 minimale du 21/10/2026** : voir `pipeline.md` (consignes → pipeline en § 0, limites et pistes v2 en § 5). Les sections « Étape 4 » à « Étape 8 » plus bas décrivent encore la v1 et ne valent que pour l'historique.

| # | Étape | Livrable | Temps estimé (avec Claude) | Difficulté /10 |
|---|---|---|---|---|
| 0 | Cadrage : position, choix des LLM, critères d'inclusion | Décisions notées dans `CLAUDE.md` | 2 h | 2 |
| 1 | Environnement local (Docker, n8n, Qdrant, LLM) | `docker-compose.yml` fonctionnel | 2–4 h | 3 |
| 2 | Corpus de test figé à 4 documents (D06, D07, D09, D12) | `corpus/` + `meta.json` | fait | 3 |
| 3 | Ingestion RAG (WF00) | Collection Qdrant (187 chunks, `chunk_id`) | fait | 5 |
| 4 | `10-argumentaire` : rédaction + garde-fous G1/G2/G4 (signalement, sans correction) + assemblage | `argumentaire_<run_id>.md` + `verif_<run_id>.json` | 3,5 h | 5 |
| 5 | Garde-fous : intégrés à l'étape 4 (G3, juge Claude, supprimé le 21/10) | — | — | — |
| 6 | Relecteur : 1 appel, rapport de relecture sans correction (dans `10-argumentaire`) | `relecture_<run_id>.json` | 0,5 h | 3 |
| 7 | Assemblage : intégré à l'étape 4 | — | — | — |
| 8 | Baseline (`50-baseline`) + évaluation (script + évaluation humaine) | `metriques.csv` + kappa | 2,5 h | 4 |
| 9 | Rapport écrit + graphical abstract | `Ecrit_….pdf` | 5–6 h | 4 |
| 10 | Oral : slides + répétition | `Oral_….pdf` | 3–4 h | 3 |
| | **Reste à faire (au 21/10)** | | **≈ 15–17 h** | **Global : 4/10** |

---

## Étape 0 — Cadrage
- [x] Position : POUR
- [x] Option B : corpus choisi par le groupe (pas de recherche PubMed automatisée)
- [x] LLM : API Gemini de Google (décision du 2026-09-30, remplace Mistral dont le plan Free ne permet pas d'activer de clé API)
- [x] Critères de sélection du corpus : voir `corpus.md`
- [ ] Corpus « obligatoire » ajouté à la main : 510(k) summary de la FDA, recommandations ESH/AHA sur le *cuffless*, ISO 81060-2, IEEE 1708, règlement (UE) 2017/745 (MDR), RGPD, HIPAA

**Notes :**

## Étape 1 — Environnement local
- Docker et Docker Compose
- n8n self-hosted (volume persistant, clés API dans les *credentials* n8n, jamais en clair dans les workflows exportés)
- Qdrant (vector store)
- Optionnel : Ollama (LLM local + modèle d'embeddings)
- Exporter régulièrement les workflows en JSON et les versionner avec git (reproductibilité)

**Notes :**
- **Machine** : MacBook Apple M3, 16 Go, macOS 26.6. Conteneurs gérés par Podman 5.8.2 (VM `applehv` de 4 CPU et 2 Go) avec `podman-compose`.
- **Fichiers** : `docker-compose.yml` (n8n `2.41.4` + Qdrant `v1.19.1`, volumes nommés `n8n_data` et `qdrant_data`, ports limités à 127.0.0.1), `.env` (clé `N8N_ENCRYPTION_KEY`, gitignoré), `.env.example`, `n8n/workflows/` (exports JSON).
- **Choix** : n8n utilise SQLite (pas de Postgres). Pas d'Ollama, le LLM passant par une API (Mistral au départ, Gemini depuis le 30/09/2026). Variables `GENERIC_TIMEZONE` et `TZ` à Europe/Paris, `N8N_DIAGNOSTICS_ENABLED=false`.
- **Vérifications (30/09/2026)** :
  - Depuis le Mac : `healthz` de n8n renvoie `ok` ; `readyz` de Qdrant renvoie « all shards are ready ».
  - Depuis le conteneur n8n : Qdrant (`http://qdrant:6333`) répond 200 ; `api.mistral.ai` répond 401 sans clé, ce qui prouve que le réseau sortant fonctionne ; PubMed esearch et Europe PMC répondent 200.
  - Le dossier `n8n/workflows/` est accessible en écriture.
  - Persistance : une collection de test a survécu à `down` puis `up`, et la clé n8n a été relue sans erreur.
- **Clé d'API Qdrant (30/09/2026)** : `QDRANT_API_KEY` a été générée avec `openssl rand -hex 32` et écrite directement dans `.env`, sans être affichée. Le conteneur la reçoit par `QDRANT__SERVICE__API_KEY=${QDRANT_API_KEY}` dans `docker-compose.yml`, et `.env.example` a été complété. Vérifications :
  - `/collections` renvoie 401 sans clé ou avec une mauvaise clé, depuis le Mac comme depuis le conteneur n8n ;
  - avec la clé (en-tête `api-key`), la réponse est 200 ;
  - `/readyz` reste accessible sans clé (200) ;
  - n8n est de nouveau `ok` après la recréation.
- **Difficultés et solutions** :
  - Recréer qdrant seul (`up -d --force-recreate --no-deps qdrant`) échoue, car podman-compose transforme le `depends_on` en dépendance dure entre conteneurs : n8n bloque la suppression de qdrant. Solution : `podman compose down` puis `up -d`, ce qui conserve les volumes. Par précaution, la sortie de ces commandes a été filtrée pour masquer les secrets.
  - Le registre `docker.n8n.io` a renvoyé `toomanyrequests` (quota des téléchargements anonymes). Solution : prendre la même image sur Docker Hub (`docker.io/n8nio/n8n`).
  - La clé de chiffrement s'est affichée en clair pendant le contrôle de `podman compose config`. Solution : clé régénérée avant le premier démarrage de n8n, sans conséquence. **Leçon** : ne jamais afficher la sortie de `compose config` quand un `.env` contient des secrets.
  - La VM Podman s'est arrêtée après une interruption. Solution : toujours vérifier `podman machine list` avant `compose up`.
  - Au démarrage, n8n signale que le mode interne des *task runners* est déprécié. C'est sans effet pour l'instant : à surveiller lors des mises à jour.
- **À faire (par l'utilisateur)** : créer le compte propriétaire sur http://localhost:5678, puis les credentials « Google Gemini(PaLM) API » (clé Google AI Studio, host `https://generativelanguage.googleapis.com`) et « Qdrant API » (URL `http://qdrant:6333`, avec la clé `QDRANT_API_KEY` de `.env`, obligatoire depuis le 30/09/2026).
- **Test de fumée Gemini** : *Manual Trigger* → *Basic LLM Chain* avec *Google Gemini Chat Model*, prompt « Réponds uniquement OK ». Si « OK » revient, n8n, la clé et l'API fonctionnent. Capture : `captures/01-test-gemini.png`.
- **Captures à garder** : `captures/01-podman-ps.png` (conteneurs actifs) et `captures/01-n8n-credentials.png` (credentials validés).

> Le détail technique de chaque workflow (nœuds, prompts, schémas JSON) est dans `pipeline.md`. Ici, on consigne ce qui a été fait, les difficultés et les solutions.

## Étape 2 — Constitution du corpus
- Corpus v0 (20 documents, 5 versants, dont 7 « contre » à réfuter) dans `corpus.md`
- [ ] Validation par l'équipe
- [ ] Récupération des PDF en texte intégral dans `corpus/` (via la BU pour les documents payants)
- [ ] `corpus/meta.json` : source unique de vérité pour la bibliographie
- [ ] Combler les trous (médico-économie, statut CE, faux positifs et surdiagnostic)

**Notes :**
- **Corpus de test (30/09/2026)** : D06 (Apple, *validation paper*), D07 (FDA K250507) et D09 (Elgendi 2019) sont téléchargés dans `corpus/`. `corpus/meta.json` a été créé pour ces 3 documents, avec les champs `annee` et `type_source` en plus du schéma de `pipeline.md`. Les références ont été vérifiées sur les PDF. Les rôles et versants sont à valider par le groupe.
- D12 (AHA 2025, *cuffless*, PMC13335599) est bloqué au téléchargement automatique : Europe PMC et ahajournals renvoient 403, et PMC affiche une vérification anti-robot. Il faut le télécharger à la main.
- **17/10/2026** : rôles et versants de `meta.json` validés par le groupe. Les PDF ne sont plus versionnés (`corpus/*.pdf` dans `.gitignore` : droits et taille), `meta.json` l'est toujours.
- **D12 ajouté (17/10/2026)** : nouvel essai automatique, toujours 403 (l'article n'est pas dans le sous-ensemble Open Access de PMC). PDF déposé à la main (manuscrit auteur PMC, 19 pages), renommé `aha_cuffless_2025.pdf`. Rôle contre, versant technique. Référence relevée sur le PDF. **Écart à trancher** : la consigne de citation de l'AHA donne *Hypertension* 2026;83:876–886, l'en-tête PMC donne 83(3):e00254 (retenu).

## Étape 3 — Ingestion RAG (WF00)
- PDF → extraction → nettoyage → chunks (≈ 1 000 caractères, chevauchement de 150, à justifier) → `gemini-embedding-001` (dimension à fixer, identique dans la collection Qdrant) → Qdrant `moa_corpus`
- Métadonnées par chunk : `chunk_id`, `doc_id`, `versant`, `role`, `page`
- Contrôle : nombre de chunks par document ; alerte si le texte extrait fait moins de 500 caractères (PDF scanné)

**Notes :**
- **Première version (30/09/2026)**, `n8n/workflows/00-ingestion.json` :
  - lecture de `meta.json` → *Split Out* (un item par document) → *Read Files from Disk* → *Extract from File* (PDF, `joinPages: false`) → Code (un item par page, avec les métadonnées) → *Loop Over Items* (lots de 6 pages) → *Qdrant Vector Store* (insertion, collection `moa_corpus`), avec *Default Data Loader* (JSON), *Recursive Character Text Splitter* (1 000 / 150) et *Embeddings Google Gemini* (`gemini-embedding-001`) → *Wait* 60 s → lot suivant ;
  - pas encore de nettoyage du texte ni de `chunk_id`.
- **Montage** : `./corpus` → `/home/node/corpus` en lecture seule, avec `N8N_RESTRICT_FILE_ACCESS_TO=/home/node/corpus`. Sans cette variable, n8n 2.x limite les nœuds de fichiers à `~/.n8n-files` (valeur par défaut lue dans le code de n8n 2.41.4).
- **Résultat** : 40 pages et 153 chunks (D06 : 23, D07 : 47, D09 : 83), en 434 s. Les chunks font entre 65 et 1 000 caractères (876 en moyenne). Métadonnées par chunk : `doc_id`, `fichier`, `page`, `annee`, `type_source`, `versant` (liste), `role`. La collection a été créée automatiquement : 3 072 dimensions, distance cosinus.
- **Difficultés et solutions** :
  - **Quota Gemini gratuit** : le 1er essai (tous les chunks d'un coup) a échoué. Un diagnostic via un nœud HTTP, qui utilise le credential n8n sans exposer la clé, a donné : 429 `RESOURCE_EXHAUSTED`, quota `EmbedContentRequestsPerMinutePerUserPerProjectPerModel-FreeTier` = **100 par minute**. **Chaque texte d'un lot `batchEmbedContents` compte pour une requête.** Solution : lots de 6 pages (≈ 60 chunks au plus), puis une pause de 60 s. Le quota journalier reste à relever dans Google AI Studio.
  - **Défaillance silencieuse de LangChain** (`@langchain/google-genai` 2.1.24) : les lots d'embeddings partent en parallèle, et un lot en erreur est remplacé par des vecteurs **vides**, sans exception. Seule la validation de Qdrant (422 : *dense vector must not be empty*) a arrêté l'insertion. À citer dans le rapport comme argument pour les contrôles automatiques.
  - Le nœud *Embeddings Google Gemini* n'expose ni la dimension (3 072 par défaut, alors que la notice du nœud annonce 768) ni le *task type* (requête ou document).
  - `n8n execute` en CLI démarre son propre *task broker* sur le port 5679, déjà pris par n8n. Solution : `podman exec -e N8N_RUNNERS_BROKER_PORT=5690 moa_n8n_1 n8n execute --id=…`.
  - En mode binaire « Load All Input Data », le *Default Data Loader* recharge **tous** les fichiers entrants pour chaque item, ce qui aurait créé des doublons. Ce mode a été écarté.
- **Test de retrieval** (`n8n/workflows/test-retrieval.json`, top 5, question en français) : les 5 chunks viennent tous de D09. 2 sur 5 sont des morceaux de bibliographie, et les scores sont très resserrés (0,730–0,737). Pistes : retirer les sections de références au nettoyage, et ajouter D12 (AHA), le document le plus pertinent pour cette question.
- **Nettoyage avant découpage (17/10/2026)** : nouveau nœud Code « Nettoyage du texte », entre *Extract from File* et « Un item par page ». Les règles sont décrites dans `pipeline.md` (WF00). Le code a été testé hors de n8n avant toute ingestion, pour ne pas consommer de quota, sur le texte extrait par la même fonction pdf.js que n8n (`parseText` de `binary.js`).

  | Doc | Caractères avant → après | Bibliographie retirée | Appels supprimés | Césures recollées |
  |---|---|---|---|---|
  | D06 | 18 158 → 17 387 | 757 (notes de fin, p. 12) | 4 | 0 |
  | D07 | 35 398 → 35 384 | 0 | 0 | 0 |
  | D09 | 66 870 → 46 840 | 19 308 (p. 9 à 11) | 172 | 18 |
  | D12 | 61 347 → 46 073 | 15 006 (p. 13 à 16) | 58 | 0 |
- **Difficultés et solutions (17/10/2026)** :
  - pdf.js place chaque exposant sur sa propre ligne : les appels de référence (`\n52 \n`) ressemblent aux indices et aux exposants d'unités (`kg/m\n2`, `K\n1`). Solution : un chiffre seul qui suit un symbole court est recollé, les autres sont supprimés.
  - Recoller toutes les césures abîmait les mots composés : les 10 « césures » de D07 étaient en fait des mots composés ou des URL (`machine-learning`, `over-the`). Solution : on ne recolle que si le mot entier existe ailleurs dans le document. Il reste 6 mots coupés dans D09 (`visualiza-tion`…), sans gravité.
  - D06 n'a pas de titre « References » (notes de fin). Solution : règle de densité des marqueurs bibliographiques sur les pages finales.
  - Dans le manuscrit PMC de D12, la figure et les tableaux 1-2 sont placés **après** les références. Solution : la coupe s'arrête au premier « Table » ou « Figure ». Sans cela, le tableau 2 (considérations de mise en œuvre : éthique, réglementaire, coût) était perdu.
  - La sortie de `n8n execute` recopie tous les vecteurs (21 Mo) et a été tronquée. Solution : contrôler le résultat dans Qdrant, pas dans cette sortie.
- **Réingestion (17/10/2026)** : collection supprimée puis recréée. 53 pages non vides, **187 chunks** (D06 = 22, D07 = 47, D09 = 59 au lieu de 83, D12 = 59), 3 072 dimensions, aucun vecteur vide, environ 10 min. Plus aucun chunk de bibliographie : les 2 chunks de D09 p. 4 qui contiennent plusieurs « et al. » forment le tableau 1 des études, conservé volontairement.
- **Test de retrieval n° 2 (17/10/2026)** : même question qu'au 30/09, en français et en anglais (« How reliable are cuffless blood pressure measurement devices? »), top 5. La pertinence a été jugée par Claude et reste **à valider par le groupe**.

  | | 30/09 : FR, 3 docs, sans nettoyage | 17/10 : FR | 17/10 : EN |
  |---|---|---|---|
  | Pertinents / partiels / bruit | 1 / 2 / 2 | 5 / 0 / 0 | 4 / 1 / 0 |
  | Bibliographie dans le top 5 | 2 | 0 | 0 |
  | Documents représentés | D09 seul | D12 seul | D12 seul |
  | Scores | 0,730–0,737 | 0,762–0,784 | 0,775–0,802 |

  - Critère fixé **avant** le test : aucun chunk de bibliographie, au moins 3 pertinents sur 5, D12 présent. Il est rempli, donc l'appel direct de l'API d'embeddings avec `task_type` (étape c) n'est pas nécessaire pour l'instant.
  - **Attribution prudente** : la question porte exactement sur le sujet de D12, donc le gain vient surtout de l'ajout de D12. L'effet du nettoyage se vérifie dans la collection (plus de bibliographie) plutôt que dans ce test. La requête anglaise relève les scores d'environ 0,02 et garde les mêmes chunks en tête : l'effet est faible mais cohérent avec un corpus en anglais.
  - **Nouvelle limite** : le top 5 vient d'un seul document. D06 (performances annoncées par Apple) n'apparaît pas. Pour WF10, il faudra plusieurs requêtes par section ou une contrainte de diversité (plafond par document, MMR) : à décider.
- **`chunk_id` (17/10/2026)** : `<doc_id>-<8 premiers caractères du SHA-1 du texte du chunk>` (ex. `D12-4794f2ff`), stable d'une réingestion à l'autre. Comme le critère (c) n'était pas déclenché, pas de réingestion : le `chunk_id` a été ajouté aux 187 points existants par `set_payload` (sans appel à Gemini), avec un index `keyword` sur `metadata.chunk_id`.
  - Nœuds ajoutés **en fin de boucle de WF00** : *HTTP Request* (`scroll` des points sans `chunk_id`) → *Split Out* → *Crypto* (SHA-1) → Code (opérations `set_payload`) → *HTTP Request* (`points/batch`, un seul appel) → *HTTP Request* (index). Le credential Qdrant est réutilisé dans les nœuds HTTP (en-tête `api-key`).
  - Pour l'appliquer aux points existants, ces mêmes nœuds ont été exécutés via une variante temporaire de WF00 (même ID, « Lancer » branché directement sur l'étape), puis le vrai WF00 a été réimporté. Résultat : 187 points, 187 `chunk_id` uniques, 0 doublon. Le SHA-1, recalculé indépendamment en Python, correspond pour les 187 points, et les autres métadonnées sont intactes. Au second passage, il n'y a plus aucun point à traiter : l'étape est idempotente.
  - `test-retrieval` affiche désormais le `chunk_id`. Relancé : mêmes chunks, même ordre, mêmes scores qu'avant l'ajout.
  - **Difficulté** : un sous-workflow aurait évité de dupliquer la logique, mais n8n 2.x n'appelle que la version **publiée** d'un sous-workflow quand l'exécution vient de la CLI (mode `cli`), alors que l'interface utilise le brouillon (code de `workflow-execute-additional-data.js`). Solution : nœuds intégrés à WF00. L'appel en fin de boucle sera vérifié à la prochaine ingestion complète ; en cas d'échec, l'étape peut être rejouée seule, puisqu'elle est idempotente.
- **Export des workflows** : `sh n8n/exporter.sh`. L'export `--backup` nommait les fichiers par ID (doublons), exportait aussi les workflows hors pipeline et contenait le nom et l'e-mail du propriétaire n8n (bloc `shared`). Vérification sur les 4 commits existants : aucun fichier ne contient ce nom ni cet e-mail. Seules les métadonnées git des commits (auteur) contiennent l'e-mail.

## Étape 4 — Rédaction (WF10)
- Un appel par section, top-k ≈ 8 plus un filtre `role = contre` pour forcer les contre-arguments
- **Règle : aucune affirmation sans `chunk_id` cité**, sortie JSON structurée, `[INFORMATION NON DISPONIBLE DANS LE CORPUS]` si l'information manque

**Notes :**
- **Stratégie de récupération (décision du 17/10/2026)** : 2 ou 3 requêtes anglaises fixes par section (top-k 15 chacune), plus une requête forcée sur `role = contre` ; fusion et dédoublonnage par `chunk_id`, plafond de 2 chunks par document, 10 chunks au plus. Pas de MMR : un plafond codé dans un nœud Code est déterministe et s'explique en une phrase. Motif : au test du 17/10, le top 5 venait d'un seul document.
- **`prompts/sections.json` (v1)** : les 9 sections de la structure imposée, avec pour chacune sa consigne, ses requêtes anglaises (2 ou 3 angles, tirés des versants de `corpus.md`), sa requête « contre » et les paramètres de récupération. La conclusion n'a pas de requête : elle est rédigée à partir des sections. Ce fichier ira en annexe du rapport.
- Proposition à valider : les 2 meilleurs chunks de la requête « contre » sont garantis dans la sélection (2 places sur 10).
- À faire avant de construire WF10 : monter `./prompts` dans le conteneur n8n (lecture seule) et l'ajouter à `N8N_RESTRICT_FILE_ACCESS_TO`.

**Notes v2 (21/10/2026)** :
- **Étape 0, test de fumée** (workflow `test-gemini`) : liste des modèles par l'API, puis un appel « Réponds uniquement OK » par modèle. `gemini-3.8-flash` (et l'alias `gemini-flash-latest`) répond OK. `gemini-3.1-pro` (et `gemini-pro-latest`) : 429 avec un quota à 0 sur le plan gratuit. `gemini-2.5-pro` : « no longer available to new users ». Modèle retenu : `gemini-3.8-flash`.
  - RPM non mesuré : un test en rafale aurait consommé RPM+1 requêtes d'un quota journalier inconnu. Il est à lire dans AI Studio avant l'étape 2. Les erreurs 429 de Gemini donnent la métrique et la limite dépassées (détail `QuotaFailure`).
  - Sécurité : le credential Gemini passe la clé en paramètre d'URL. Les appels HTTP sont en mode « ne jamais lever d'erreur » (aucun objet d'erreur contenant la requête), et chaque sortie est contrôlée (`AIza`, `key=`) avant d'être lue.
- **Étape 1, `10-argumentaire` sur la section « technique »** : Lire les fichiers (`sections.json`, `redacteur_v1.md`, `meta.json`) → Préparer la section (3 requêtes + 1 « contre ») → Recherche Qdrant (top 15, filtre `role = contre` par expression pour la 4e requête) → Sélection des chunks → Prompt du rédacteur → Rédacteur (HTTP, mode JSON avec schéma) → Garde-fous G1 G2 G4 → Assemblage et fichiers → Écrire dans `outputs/`. 12 nœuds, pas encore de boucle (une seule section).
  - Exécution `20261021-165636` : 51 chunks candidats → **8 retenus** (2 par document, plafond atteint pour les 4 ; les 2 chunks « contre » de D12 garantis). Rédacteur : 2 783 tokens en entrée, 991 en sortie, 3 690 de réflexion ; **34 s** au total. 4 paragraphes, tous cités, **0 signalé** par G1, G2 ou G4. Bibliographie : 4 références générées depuis `meta.json`.
  - **Relecture humaine des chunks cités (Claude, à confirmer par le groupe)** : les chiffres sont fidèles, mais il y a des distorsions que G1, G2 et G4 ne peuvent pas voir :
    - § 1 : « principes physiologiques solides » (la source dit « generally accepted… partially expressed ») ; l'erreur de ±9,82 / ±3,88 mmHg d'une seule étude (Radha et al. 2018) devient « ces méthodes ont démontré » ; la réserve de la source (« only three subjects ») est omise ;
    - § 3 : « pour répondre à ces exigences méthodologiques » invente un lien logique, et même chronologique, entre la déclaration de l'AHA (déc. 2025) et l'étude d'Apple (autorisée en sept. 2025) ; « viabilité d'un suivi sur le long terme » n'est pas dans les sources (étude de 30 jours) ;
    - § 4 : « outil de repérage robuste et rigoureusement validé » enfreint la règle 7 du prompt ; la sensibilité de 41,2 % (la majorité des HTA non détectées) n'est pas discutée ;
    - § 2 présente les objections de l'AHA sans y répondre dans le même paragraphe (règle 6 partiellement suivie).
  - Ce sont des exemples pour la critique des résultats : « tout est vert » ne veut pas dire « tout est juste ». D'où le relecteur (étape 3) et l'évaluation humaine.

**Notes du 26/10/2026** :
- Validations : appel HTTP direct du rédacteur, montages `prompts/` et `outputs/`, `redacteur_v1` gardé jusqu'au bout (ses défauts servent à la critique). Quotas relevés par le groupe dans AI Studio (`pipeline.md` § 1) : `gemini-3.8-flash` à **20 appels par jour**, d'où un paramètre listant les sections à générer et l'interdiction de lancer une exécution complète sans accord.
- **Contrôle de `moa_corpus`, sans ingestion** : 187 points (D06 22, D07 47, D09 59, D12 59), 187 `chunk_id` distincts, aucun point sans `chunk_id`, index `keyword` présent.
- **309 requêtes d'embeddings affichées par AI Studio le 26/10, RPM saturé** : n8n n'a rien exécuté depuis le 21/10. La table des exécutions (rétention de 14 jours) et le journal d'événements ne montrent aucun lancement depuis cette date. Consommation du pipeline : 17/10 = 191 (ingestion de 187 chunks + 4 requêtes de test) ; 21/10 = 4 ; 26/10 = 0. Le 30/09 en revanche : deux ingestions de 153 chunks (la première sans lots, quota par minute dépassé), plus un diagnostic et une requête de test, soit environ 309. Hypothèse : le graphique affiche le pic d'une période, pas la journée. À confirmer par le groupe ; sinon la clé est utilisée ailleurs.
- Incident : `10-argumentaire` a été archivé dans l'interface le 26/10 à 19 h 50, pendant la suppression de `zz-diag-gemini` (erreur de manipulation, confirmée par le groupe). Réimporté (donc désarchivé) avec G5.
- **G5** testé hors ligne : « prouvé », « prouve », « prouvent », « toujours », « aucun risque » sont signalés ; « éprouvée », « approuvé », « improuvable » ne le sont pas. Limites : « pas toujours » (formule prudente) est signalé, et « outil robuste et rigoureusement validé » (21/10) passe. Aucun des 4 paragraphes du 21/10 n'aurait été signalé.
- **Étape 2a, structure** (19 nœuds) : Paramètres → Lire → Préparer les sections → *Loop* (une section à la fois) : Requêtes → Qdrant → Sélection → Prompt → Rédacteur → Garde-fous G1 G2 G4 G5 → IF « Conclusion ? » → *Wait* 15 s → *Loop*. En sortie de boucle : IF « Conclusion demandée ? » → Chunks déjà cités → mêmes nœuds Prompt, Rédacteur et Garde-fous → Assemblage. Conclusion branchée après la boucle, choix du groupe.
- **Test de la tuyauterie sans appel de chat** : variante de même ID avec un rédacteur simulé (nœud Code), sorties préfixées `test_` puis supprimées. Boucle, pauses, conclusion, G5 et assemblage vérifiés pour 7 requêtes d'embeddings et aucun appel de chat. Ensuite, réimport du vrai workflow.
- **Essai 1** (20 h 12) : le délai de 180 s est dépassé sur « éthique », ce qui arrête l'exécution. n8n masque la clé dans l'erreur (`**hidden**`). Délai porté à 600 s. Le mode « continuer après erreur » est écarté : il renvoie l'objet d'erreur brut, non masqué.
- **Essai 2, exécution `20261026-201619`** (éthique, réglementaire, conclusion), 421 s :
  - **éthique** : HTTP **503** (« high demand ») en 1,1 s ;
  - **réglementaire** : HTTP 200 en **381,7 s** (2 415 tokens en entrée, 548 en sortie, 5 944 de réflexion) ;
  - **conclusion** : **503** en 5,4 s.

  G1 signale les deux échecs et l'exécution va jusqu'au bout. C'est le comportement prévu, et un exemple réel pour le rapport.
- Sélection : éthique 44 candidats → 8 retenus (2 par document) ; réglementaire 46 → 7 (un seul chunk de D06). Les 2 mêmes chunks « contre » de D12 (p. 13 et p. 19, tableau 2) sont garantis dans les deux sections.
- **Section réglementaire** : 5 paragraphes. 2 sont rédigés et cités (D07, D12). Les 3 autres sont des `[INFORMATION NON DISPONIBLE DANS LE CORPUS]` pour HIPAA, CE/MDR et RGPD, ce qui est attendu avec 4 documents. G2, G4 et G5 ne signalent aucun paragraphe.
- **Relecture des chunks cités (Claude, à confirmer par le groupe)** :
  - § 1 : « garantissant ainsi un usage approprié » n'est pas soutenu. C'est aussi une formulation absolue, que G5 ne repère pas.
  - § 1 : « code produit QXO » est fidèle au chunk (tableau 1, p. 8), mais la correction administrative du 12/09 l'a remplacé par SFR (`corpus.md` n° 7). Être fidèle au chunk ne garantit pas l'exactitude.
  - § 2 : « l'autorisation de HTNF répond à ces exigences » invente un lien entre la déclaration de l'AHA (déc. 2025) et l'autorisation FDA (sept. 2025). C'est le même défaut que le 21/10. Les exigences de l'AHA sur la confidentialité et la propriété des données ne sont d'ailleurs traitées dans aucun extrait de D07.
  - § 2 : « proscrit les algorithmes adaptatifs » durcit « does not include provisions for », et « validation stricte garantissant » durcit « such that the modified device remains as safe and effective ».
- `version_modele` manquait dans `runs.jsonl` quand la première section échoue : corrigé (première version renvoyée).
- Quota du 26/10 : au plus 4 appels de chat sur 20 (1 délai dépassé + 3). On ne sait pas si les 503 sont décomptés.

**Soir du 26/10 : étape 3 préparée, rien n'est lancé**
- **G5 élargi** (décision du groupe) :
  - les 28 cas d'essai passent, hors ligne ;
  - sur les sorties réelles, 6 paragraphes sur 9 sont signalés, tous à raison : « solides » et « démontré » (21/10 § 1), « démontrant la viabilité » (§ 3), « robuste », « rigoureusement » (§ 4), « garantissant » (26/10 §§ 1 et 2) ;
  - aucun faux positif sur ces textes ;
  - « pas toujours » n'est pas signalé ;
  - correction en cours de test : « sans aucun risque » était pris pour une forme niée, à cause de « sans ». « Aucun risque » est maintenant signalé dans tous les cas.
- **Relances** : « Retry On Fail » ne convenait pas. Le code du moteur montre que l'attente est plafonnée à `Math.min(5000, …)`, et que la relance ne se déclenche que sur une erreur levée ou un champ `error`. Un 503 reçu en « ne jamais lever d'erreur » n'est donc pas relancé, et les tentatives ne sont pas tracées. Le groupe a choisi une relance explicite : IF 429/5xx → *Wait* 60 s → copie du nœud HTTP. Elle s'applique aux sections, à la conclusion et au relecteur. Un délai dépassé n'est pas relancé : il est signalé par G1.
- **Test des objets d'erreur** (workflow temporaire de même ID que `test-gemini`, exécution non sauvegardée, aucun appel de chat) :
  - en « continuer après erreur », l'erreur ne contient que le message et la cause, pour un 404 avec la clé en paramètre, un délai dépassé, et un 400 avec une clé factice en en-tête ;
  - aucune occurrence de `AIza` dans la sortie ;
  - le code de n8n ne garde de la requête que l'URL (sans les paramètres), la méthode, le corps et les en-têtes, et le nœud HTTP ne renvoie ensuite que le message et la cause.

  **Correction** : la phrase écrite plus tôt dans `pipeline.md` (« continuer après erreur » exposerait la clé) n'avait pas été vérifiée. Elle était fausse et a été remplacée.
- **Clé en en-tête `x-goog-api-key`** (question du groupe, non codée) : c'est faisable, avec un credential *Header Auth* saisi par l'utilisateur et le nœud HTTP en « generic credential ». Mais ce n'est plus utile pour « continuer après erreur ». Inconvénients : un second credential qui contient la même clé, car le nœud d'embeddings garde le sien. Avantage : la clé ne passe plus dans l'URL, ce qui compte pour les journaux d'un proxy éventuel.
- **Relecteur** :
  - prompt `prompts/relecteur_v1.md` ;
  - 11 nœuds ajoutés, 30 au total ;
  - la ligne de `runs.jsonl` est écrite après le relecteur, avec les tentatives par section ;
  - tous les chemins ont été testés avec un rédacteur et un relecteur simulés : technique 200 ; éthique 503 puis 200 ; réglementaire délai dépassé, signalé par G1 sans arrêt ; relecteur 503 puis 200 ;
  - `runs.jsonl` donne 7 appels de chat, conformément au plan ;
  - sorties `test_` supprimées.
- Un seul `10-argumentaire` dans n8n (`MoaWf10Argumentaire`, non archivé) ; aucun workflow actif.
- **Défauts de référence à revérifier sur les sorties du 27/10**, avant de lire la relecture :
  - technique (21/10) : principes « solides » ; résultat d'une seule étude généralisé ; réserve « only three subjects » omise ; lien inventé AHA → étude d'Apple ; « suivi sur le long terme » non soutenu ; « robuste et rigoureusement validé » ; sensibilité de 41,2 % non discutée ; objections de l'AHA sans réponse ;
  - réglementaire (26/10) : « garantissant ainsi un usage approprié » ; « l'autorisation répond à ces exigences » (lien inventé) ; « proscrit » et « validation stricte garantissant » durcissent la source ; « QXO » périmé, que le relecteur ne peut pas voir.

**Essai du 27/10 (feu vert d'Adam à 9 h)** : la règle d'arrêt s'est déclenchée deux fois, et aucune sortie n'a été écrite.
- **Essai 1** (lancé à 9 h 05) :
  - le premier appel (technique) reçoit un 503, puis réussit à la relance ;
  - arrêt `delai` avec « 41 145 s » affichées ;
  - cause : l'horloge de la VM Podman, figée pendant la veille du Mac, avait 40 837 s de retard (11 h 20). `chronyd` l'a recalée à 9 h 09 min 59 s, en plein appel (journal : « System clock wrong by 40836.9 seconds », puis « stepped ») ;
  - durée réelle du premier appel : environ 308 s, donc l'arrêt était justifié ;
  - le `run_id` 20261026-214455 est faux : la ligne de `runs.jsonl` est laissée telle quelle et documentée ici.
- **Correctif de procédure** : avant chaque exécution, contrôler l'écart d'horloge entre l'hôte et le conteneur, et forcer le recalage au-delà de 5 s (`podman machine ssh 'sudo chronyc makestep'`, testé : « 200 OK »). Voir `pipeline.md` § 4.
- **Essai 2** (lancé à 9 h 13, écart d'horloge de 0 s) : le premier appel réussit du premier coup, mais en **241 s**, d'où un arrêt `delai`. C'est une relance dans l'heure, conforme à la règle. Comme le seuil validé est de 180 s, je n'ai pas relancé une troisième fois : décision demandée à Adam.
- **API lente** : avec le même prompt (2 783 tokens en entrée, environ 4 300 en sortie et en réflexion), le premier appel a pris 34 s le 21/10, contre 241 à 308 s le 27/10, soit environ 18 tokens par seconde contre 150. Le 26/10, il y avait aussi eu des 503 et un appel de 6 min 22 s.
- Quota du 27/10 : 3 appels de chat consommés, dont un 503.
- **Les deux sections « technique » rédigées puis non écrites** (extrait dans `outputs/brouillons_arretes_20261027.json`) :
  - les 8 mêmes chunks que le 21/10, puisque la récupération est déterministe ;
  - le lien inventé AHA → étude d'Apple **revient dans les deux** : « Pour répondre à ces enjeux de validation… » et « Pour pallier ces limites méthodologiques… ». Il est donc présent dans 4 sorties sur 4 ;
  - « sur le long terme » revient aussi, pour une étude de 30 jours ;
  - G5 signale « démontré », « garantissant » et « garantit ».
- La comparaison avec le relecteur n'a pas pu se faire : il n'y a eu ni argumentaire ni relecture.

**Exécution complète candidate `20261027-093507`** (consignes de 9 h 30 ; seuil de 420 s) :
- **Déroulé** :
  - premier lancement à 9 h 26 : arrêt `delai` à 422 s (503, puis relance en 406 s) ;
  - relancement à 9 h 35 : **terminé en 47 min**, statut `termine`.
- **Appels** : 14 appels de chat (10 appels et 4 relances), 28 requêtes d'embeddings.
- **Latence** : de 142 à 494 s par appel réussi.
- **Baseline `20261027-102233`** : 293 s, 9 sections sur 9, 27 paragraphes, 22 références.
- **Quota du jour épuisé** : 20 appels.
- **Critère « sans défaut technique » non rempli** :
  - éthique et parcours de soins sont en échec G1 (503 aux deux tentatives) ;
  - la section « enjeux FDA » contient 91 caractères nuls : Gemini a renvoyé `\u0000e9` au lieu de « é » dans son JSON (`finishReason: STOP`). G4 signale les « nombres » qui en résultent ;
  - la conclusion est entièrement écrite sans accents.
- **Liste de défauts de référence** (`outputs/defauts_reference_20261027-093507.md`), écrite sans ouvrir la relecture :
  - 30 défauts de fond, dont 11 de gravité haute et 4 liens inventés entre l'AHA et Apple ou la FDA (A3, A9, A18, A25) ;
  - 4 défauts de structure et de forme ;
  - 2 défauts invisibles depuis les extraits (QXO, deux fois).
  
  Elle est en attente de validation par un membre du groupe.
- **Garde-fous** :
  - G5 signale 5 paragraphes, chacun avec un vrai défaut. Il fait aussi une fausse alerte (« sans lien prouve ») et manque « demontre », écrit sans accent ;
  - G4 n'a repéré que la corruption de l'encodage.

**Correctifs du 27/10 avant le gel** (consignes de 10 h 45, tous testés par simulation, sans appel de chat) :
- **Décodage** :
  - un caractère NUL suivi de 2 chiffres hexadécimaux est remplacé par le caractère correspondant, juste après `JSON.parse` et avant G1 à G5 ;
  - G1 signale tout NUL restant ;
  - le même décodage s'applique à la réponse du relecteur ;
  - la baseline du 27/10 ne présente pas le défaut, donc rien à changer dans `eval/evaluer.py`.
- **G1** : alerte quand une section rédigée (200 caractères au moins hors marqueur) ne contient aucun caractère accentué.
- **G5** : la comparaison ignore les accents (`normalize('NFD')`, marques retirées), et les lignes `TERMES` et `NEGATION` sont inchangées. 34 cas d'essai passent.
  - Sur l'exécution 1, G5 voit maintenant « demontre » (A30).
  - Il signale aussi « demontrent » dans « les résultats démontrent une spécificité de 92,3 % » : probable fausse alerte.
- **Relances** :
  - jusqu'à 2, après 60 s puis 120 s, avec un budget de 18 appels de chat par exécution ;
  - compteurs de l'exécution dans `$execution.customData`, testé en CLI au préalable ;
  - **les 120 s sont faites de deux attentes de 60 s** : le code du nœud *Wait* (lignes 506 à 518) met l'exécution en attente dans la base au-delà de 65 s, ce qui casserait la CLI ;
  - 40 nœuds au total.
- **Simulation** :
  - contexte : 3 décodages et un NUL restant signalé ;
  - enjeux FDA : 503, 503, puis 200 (3 tentatives) ;
  - technique : sans accents, d'où une alerte G1 et G5 sur « demontre » ;
  - éthique : 503 trois fois ;
  - conclusion et relecteur : relance refusée faute de budget (budget de test : 9) ;
  - `runs.jsonl` : 10 appels, tentatives, refus et 3 décodages.
- **Baseline officielle** : `20261027-102233`. **Exécution 1, non officielle** : `20261027-093507`, support de la comparaison avec le relecteur.
- **Gel** le 27/10 au soir.

## Étape 5 — Garde-fous (WF20)
- G1 structure · G2 citations ∈ chunks récupérés · G3 fidélité (juge Claude Haiku) · G4 chiffres présents dans la source
- Régénération si échec, 2 itérations au maximum

**Notes :**

## Étape 6 — Agent examinateur (WF30)
- Grille : conformité à la consigne, contre-arguments du corpus non traités, sur-affirmations, équilibre, cohérence, conclusion
- Il produit une liste de problèmes, **pas une réécriture**, puis le rédacteur fait une passe de correction. On garde les versions avant et après

**Notes :**

## Étape 7 — Assemblage (WF40)
- Les `chunk_id` deviennent des numéros [n] ; la bibliographie est générée depuis `meta.json`, **jamais par le LLM**
- Conversion en PDF avec Pandoc

**Notes :**

## Étape 8 — Baseline et évaluation qualité (WF50/60)
Méthodes à citer dans le rapport (références à vérifier et à compléter) :
- RAGAS : *faithfulness*, *answer relevance*, *context precision* (Es et al., 2023)
- FActScore : décomposition en faits atomiques (Min et al., 2023)
- LLM-as-a-judge, avec ses biais connus (Zheng et al., 2023)
- Chain-of-Verification (Dhuliawala et al., 2023) ; SelfCheckGPT (Manakul et al., 2023)
- Cadre d'évaluation humaine des LLM en santé : QUEST (Tam et al., 2024)
- Études sur les références hallucinées par les LLM (à rechercher)

Protocole :
- **Baseline** : même modèle Gemini que le rédacteur, même consigne, sans RAG ni garde-fous
- Métriques : % d'affirmations soutenues, % de références existantes et correctes, % de chiffres retrouvés, couverture des sections, contre-arguments traités, problèmes relevés par l'examinateur, tokens, coût et durée
- Double évaluation humaine en aveugle sur un échantillon d'affirmations, avec kappa

**Résultats :**

## Étape 9 — Rapport écrit
- [ ] Graphical abstract (figure d'ouverture)
- [ ] Description du pipeline et de la méthodologie
- [ ] Contrôle qualité (méthodes citées)
- [ ] Critique des résultats. Matière déjà relevée :
  - « tout est vert » ne veut pas dire « tout est juste » : 0 paragraphe signalé le 21/10, malgré des distorsions relevées à la relecture ;
  - **fidélité ≠ exactitude** : « code produit QXO » (26/10) est fidèle au chunk de D07, mais périmé, car le corpus contient la version d'avant la correction administrative du 12/09 (SFR) ;
  - lien inventé AHA (déc. 2025) → Apple ou FDA (sept. 2025) : **observé par Claude dans toutes les sorties, non validé par le groupe** ; dans l'exécution 1, A3 et A25 confirmés, A9 et A18 rejetés à l'aveugle, puis A9 reclassé vrai défaut après la sortie du relecteur ;
  - **relecteur** (exécution 1, liste de défauts validée à l'aveugle) : **1 défaut confirmé repéré sur 19, 0 sur 15 sur le fond** (seul B1, les sections vides). Son seul problème de fond porte sur le passage de A9 : classé vrai défaut par Adam, après avoir vu la sortie du relecteur (validation à l'aveugle et score inchangés). Le relecteur n'est pas modifié : pipeline gelé ;
  - G5 version 1 (règle 7 seule) ne repérait aucun défaut réel. La liste élargie a été construite à partir de ces mêmes défauts : ses résultats sur le 21/10 et le 26/10 relèvent du surajustement. Seuls ceux de l'exécution finale comptent, et la liste est gelée depuis le 26/10 ;
  - la liste de défauts de référence qui sert à évaluer le relecteur est écrite par un LLM (Claude), puis validée par le groupe : à dire explicitement ;
  - la baseline a reçu **les mêmes règles** que le rédacteur, sauf celles qui dépendent du corpus, y compris l'interdiction d'inventer des références : à préciser dans la description de la baseline ;
  - une affirmation (une phrase) est jugée par rapport aux chunks de son paragraphe, et non de sa phrase : une phrase peut être jugée soutenue grâce à un chunk cité pour une autre phrase ;
  - l'API saturée (503, appel de 6 min 22 s) est une limite pratique d'un service gratuit
- [ ] Annexe : argumentaire généré + critères de sélection du corpus et équations de recherche manuelles + prompts

## Étape 10 — Oral (10 min + 10 min de questions)

| Temps | Slide | Contenu |
|---|---|---|
| 0:00–1:00 | 1 | Titre + problématique clinique en une phrase |
| 1:00–2:00 | 2 | Contexte : HTA, dépistage, autorisation FDA |
| 2:00–3:30 | 3 | **Graphical abstract du pipeline** |
| 3:30–5:00 | 4–5 | Architecture n8n : capture du workflow, choix techniques |
| 5:00–6:30 | 6 | Garde-fous et agent de relecture (exemple concret d'une hallucination détectée) |
| 6:30–8:00 | 7 | Résultats du contrôle qualité : pipeline vs baseline |
| 8:00–9:00 | 8 | Ce que l'IA a conclu, et ce qu'on en pense |
| 9:00–10:00 | 9 | Limites et leçons pour un usage raisonné de l'IA |

**Points de méthode à raconter** (exemples concrets et vérifiables) :
- **Critère fixé avant de regarder les résultats** (17/10) : pour décider s'il fallait l'étape (c) (`task_type`), le critère a été écrit *avant* de lancer le test (aucune bibliographie, au moins 3 chunks pertinents sur 5, D12 présent). On évite ainsi d'ajuster le critère aux résultats (biais de l'analyse *a posteriori*).
- **Le piège des tableaux de D12** : dans le manuscrit PMC, la figure et les tableaux 1-2 sont placés après les références. Une règle naïve (« tout couper après References ») supprimait le tableau 2, qui porte justement sur l'éthique, le réglementaire et le coût. D'où une coupe qui s'arrête au premier « Table » ou « Figure ». Leçon : inspecter le texte extrait document par document avant d'ingérer.
- **Défaillance silencieuse de LangChain** (30/09) : un lot d'embeddings en erreur est remplacé par des vecteurs vides, sans exception. Seule la validation de Qdrant l'a bloqué. C'est un argument pour les contrôles automatiques.
- **Attribution prudente** : la hausse de 1/5 à 5/5 chunks pertinents vient surtout de l'ajout de D12, pas du nettoyage ni de la requête en anglais (environ +0,02 de score).

**Questions probables à préparer** : fonctionnement du PPG et pourquoi le *cuffless* reste débattu · différence entre 510(k) et De Novo et marquage CE · biais de LLM-as-a-judge · pourquoi ce choix de modèle · reproductibilité · RGPD et envoi de données à une API.

---

## Journal chronologique
| Date | Ce qui a été fait | Difficulté | Solution | Capture |
|---|---|---|---|---|
| 2026-09-30 | Lecture des consignes, création de `CLAUDE.md` et `implémentation.md` | — | — | — |
| 2026-09-30 | Choix du LLM : API Mistral | Pas de clé API au départ, un modèle local jugé trop faible pour la rédaction | Clés Mistral (argument RGPD) | — |
| 2026-09-30 | Option B retenue (corpus choisi par le groupe) ; corpus v0 et spec `pipeline.md` rédigés | Un seul article ne couvrait pas tous les versants imposés | Corpus de 15–20 documents + RAG | — |
| 2026-09-30 | Étape 1 : stack n8n 2.41.4 + Qdrant 1.19.1 sous Podman, vérifiée (santé, réseau, persistance) | Quota de téléchargement sur `docker.n8n.io` ; clé de chiffrement affichée pendant un contrôle | Image prise sur Docker Hub ; clé régénérée avant le premier démarrage | à faire : `01-podman-ps.png` |
| 2026-09-30 | Passage de Mistral à l'API Gemini (Google) | Plan Free de Mistral Studio : impossible d'activer une clé API sans plan payant | Clé Google AI Studio, credential n8n « Google Gemini(PaLM) API », embeddings `gemini-embedding-001` ; argument RGPD reformulé (conditions EEE : pas d'entraînement sur les prompts) | à faire : `01-test-gemini.png` |
| 2026-09-30 | Clé d'API sur Qdrant (`QDRANT_API_KEY` dans `.env`, `QDRANT__SERVICE__API_KEY` dans le compose) : 401 sans clé, 200 avec | Impossible de recréer qdrant seul, à cause de la dépendance dure créée par podman-compose | `down` puis `up -d` (volumes conservés) | — |
| 2026-09-30 | Corpus de test (D06, D07, D09) + `meta.json` ; workflows `00-ingestion` (153 chunks dans `moa_corpus`) et `test-retrieval` | Quota Gemini gratuit de 100 embeddings par minute ; LangChain renvoie des vecteurs vides sans erreur ; conflit de port avec `n8n execute` ; D12 bloqué par l'anti-robot de PMC | Lots de 6 pages + pause de 60 s ; Qdrant rejette les vecteurs vides ; `N8N_RUNNERS_BROKER_PORT=5690` ; D12 à télécharger à la main | à faire : capture du workflow d'ingestion |
| 2026-10-17 | PDF du corpus sortis de git + commit ; corrections (`corpus.md` n° 7, credential Qdrant) ; `${QDRANT_API_KEY:?…}` ; D12 ajouté ; WF00 : nettoyage avant découpage ; `test-retrieval` en FR et en EN ; réingestion (187 chunks) ; retrieval : 5/5 pertinents en FR, 4 + 1 partiel en EN, plus de bibliographie (contre 2/5 au 30/09) | D12 toujours en 403 ; exposants pdf.js confondus avec les indices ; mots composés pris pour des césures ; tableaux de D12 après les références ; l'export n8n contient le nom et l'e-mail du propriétaire | PDF déposé à la main ; recollage selon le contexte (symbole court, vocabulaire du document) ; coupe arrêtée au premier tableau ou à la première figure ; export ciblé des 2 workflows, sans le bloc `shared` | à faire : capture de WF00 avec le nœud de nettoyage |
| 2026-10-17 | `chunk_id` (SHA-1 du texte) ajouté aux 187 points par `set_payload` + index, et intégré en fin de WF00 ; `prompts/sections.json` (requêtes anglaises fixes, 9 sections) ; stratégie de récupération de WF10 (multi-requêtes, plafond de 2 par document, requête « contre ») ; référence D12 confirmée par Crossref ; export par `n8n/exporter.sh` | Sous-workflow inutilisable depuis la CLI sans publication ; l'export `--backup` exposait le nom et l'e-mail | Nœuds intégrés à WF00, testés via une variante temporaire (même ID) ; export ciblé sans bloc `shared`, avec arrêt s'il reste un e-mail | à faire : capture de WF00 (nettoyage + `chunk_id`) |
| 2026-10-21 | Plan v2 « rapide » : corpus figé à 4 documents, juge Claude supprimé, 2 workflows + script d'évaluation (`pipeline.md` réécrit, v1 dans git `28e7b16`) | Délai serré (date limite probable 02/11) | Périmètre réduit, sections pauvres assumées comme résultat du garde-fou | — |
| 2026-10-21 | Consignes exactes du sujet 2 intégrées (`CLAUDE.md` § 2) ; plan v2 minimale : RAG + garde-fous en signalement seul + relecteur sans correction + baseline + évaluation humaine ; liste des limites et pistes v2 (`pipeline.md` § 5) | Délai serré | Ne garder que ce que les consignes exigent | — |
| 2026-10-21 | Étape 0 : test de fumée Gemini (`test-gemini`) → `gemini-3.8-flash` retenu (Pro fermé au plan gratuit). Étape 1 : `10-argumentaire` sur la section « technique » de bout en bout, premier Markdown (`outputs/argumentaire_20261021-165636.md`), 0 paragraphe signalé ; `./prompts` et `./outputs` montés dans n8n ; prompt `redacteur_v1.md` | RPM inconnu (test en rafale risqué) ; clé Gemini en paramètre d'URL ; distorsions qualitatives invisibles pour G1, G2 et G4 | RPM à lire dans AI Studio ; appels HTTP sans erreur levée + contrôle des sorties ; relecteur et évaluation humaine pour la fidélité | à faire : capture de `10-argumentaire` |
| 2026-10-26 | Reprise : validations du 21/10 (HTTP direct, `redacteur_v1` gardé) ; quotas Gemini dans `pipeline.md` (chat : 5 RPM, 20 RPD) ; contrôle de `moa_corpus` (187 points, 0 doublon) ; relecteur option A (spec) ; **G5** formulations absolues ; `CLAUDE.md` § 4 en v2 ; exécution finale planifiée un jour de quota entier | 309 requêtes d'embeddings affichées alors que n8n n'a rien exécuté depuis le 21/10 ; `10-argumentaire` archivé par erreur | Hypothèse du pic du 30/09, à vérifier dans AI Studio ; workflow réimporté | — |
| 2026-10-26 | Étape 2a : `10-argumentaire` avec boucle sur les sections (*Wait* 15 s), conclusion après la boucle, paramètre des sections en tête, G5 ; tuyauterie testée avec un rédacteur simulé ; essai éthique + réglementaire + conclusion (`outputs/argumentaire_20261026-201619.md`) : réglementaire rédigé (2 paragraphes cités + 3 `[INFORMATION NON DISPONIBLE]`), éthique et conclusion en 503 | API Gemini saturée (« high demand ») : premier appel au-delà de 180 s, un appel réussi en 6 min 22 s ; « continuer après erreur » exposerait la clé ; nouveau lien inventé entre AHA et FDA, invisible pour G1 à G5 | Délai porté à 600 s ; les 503 sont signalés par G1 sans arrêt ; relance d'éthique et de la conclusion à prévoir ; défaut gardé pour la critique | à faire : capture de `10-argumentaire` (boucle) |
| 2026-10-26 | Étape 3 préparée (rien lancé) : relecteur option A (`relecteur_v1.md`, grille + 2 critères) ; relance unique sur 429/5xx (*Wait* 60 s) pour les sections, la conclusion et le relecteur ; délai dépassé signalé par G1 ; G5 élargi (négations, « certain » affirmatif) ; tentatives dans `runs.jsonl` ; paramètres réglés pour le 27/10 (technique, éthique, réglementaire, conclusion + relecteur = 5 appels) | « Retry On Fail » inadapté (5 s au plus, pas de relance sur un 503 en « ne jamais lever d'erreur ») ; affirmation non vérifiée sur la fuite de clé dans les erreurs | Relance explicite dans le graphe ; test des objets d'erreur : pas de clé, affirmation corrigée ; tous les chemins testés avec des appels simulés | à faire : capture de `10-argumentaire` (relances + relecteur) |
| 2026-10-26 | Consignes de la revue (points 0 à 2) : boîte aux lettres `echanges/` (`CLAUDE.md` § 9) ; en-tête `x-goog-api-key` non retenu ; G5 gelé et évalué seulement sur l'exécution finale (surajustement, `pipeline.md` § 3 et § 5) ; protocole corrigé : défauts de référence écrits par Claude puis validés par le groupe avant l'appariement ; échéance du pipeline le 28/10 | La relecture « manuelle » de référence était celle d'un LLM ; G5 testé sur les sorties qui ont servi à le construire | Validation humaine défaut par défaut ; liste de G5 gelée | — |
| 2026-10-26 | Étape 4 : `50-baseline` (11 nœuds) et `prompts/baseline_v1.md`. Un appel Gemini en mode JSON (sections, paragraphes, références numérotées), même relance unique que le pipeline ; sorties `baseline_<run_id>.md` (références « non vérifiées »), `baseline_<run_id>.json` et une ligne de `runs.jsonl`. Testé avec un appel simulé (503 puis relance, section inattendue, sections absentes) | Comparaison équitable avec le pipeline | Mêmes règles que `redacteur_v1` hors corpus, interdiction d'inventer des références, même schéma JSON | à faire : capture de `50-baseline` |
| 2026-10-26 | Étape 5 : `eval/evaluer.py` (`metriques` : `metriques.csv`, 15 affirmations tirées avec le `run_id` pour graine dans deux copies `eval_humaine_juge1/2.csv`, `references_baseline.csv` ; `kappa` : kappa de Cohen + matrice de confusion). `verif` garde désormais le texte des chunks récupérés. Testé sur les sorties du 21/10 et du 26/10 et sur une exécution simulée (pipeline + baseline) ; kappa vérifié à la main (0,516) | Les jugements ne doivent jamais être écrasés ; l'indépendance des deux évaluateurs ; anciens `verif` sans texte des chunks | Fichiers à remplir créés une seule fois ; une copie par évaluateur ; texte signalé comme absent pour les anciennes exécutions | — |
| 2026-10-26 | Consignes de 21 h 15 : choix de la baseline et de l'évaluation validés ; limite « affirmation jugée par rapport aux chunks de son paragraphe » (§ 5) ; **règle d'arrêt dans `10-argumentaire`** (paramètres `arret_premier_appel` et `seuil_premier_appel_s` = 180, premier appel seulement, ligne `statut: arrete` dans `runs.jsonl`, puis *Stop and Error* ; 34 nœuds). Testée par simulation, sans appel de chat : échec après relance → arrêt ; premier appel lent → arrêt ; deuxième appel lent → exécution complète (`statut: termine`) | `n8n execute` n'affiche rien avant la fin ; durée négative dans la variante de test (attente de relance raccourcie à 2 s alors que 60 s sont déduites) | Règle dans le workflow plutôt qu'une surveillance à la main ; déduction de 60 s documentée comme liée à l'attente réelle | — |
| 2026-10-27 | Essai du point 3 (technique, éthique, réglementaire, conclusion, relecteur) : **deux arrêts par la règle du premier appel**. Essai 1 : 503 puis relance réussie, durée réelle d'environ 308 s, mais 41 145 s affichées à cause d'un saut d'horloge de la VM. Essai 2 : 241 s. Aucune sortie, 3 appels de chat consommés. Extrait des deux sections rédigées dans `outputs/brouillons_arretes_20261027.json` | Horloge de la VM Podman figée pendant la veille du Mac (11 h 20 de retard), recalée en pleine exécution ; API Gemini environ 8 fois plus lente que le 21/10 | Contrôle d'horloge avant chaque exécution (`chronyc makestep`) ; arrêt après la relance prévue par la règle, décision sur le seuil demandée à Adam ; le lien inventé AHA → Apple revient dans 4 sorties sur 4 | — |
| 2026-10-27 | Consignes de 9 h 30 : **seuil de la règle d'arrêt porté à 420 s** (essai et exécution finale) ; l'essai devient une **exécution complète candidate** (9 sections dont la conclusion, relecteur, puis baseline : 11 appels). Paramètres réglés sur les 9 sections | Latence de 4 à 5 min observée le 27/10 (34 s le 21/10, même prompt) : le seuil de 180 s arrêtait des appels réussis | Seuil relevé, l'arrêt sur échec après relance est conservé ; contrôle d'horloge systématique avant chaque lancement | — |
| 2026-10-27 | Exécution complète candidate, lancement de 9 h 26 : **arrêt `delai` à 422 s** (seuil de 420 s). Premier appel (contexte) : 503 en 16 s, puis relance réussie en 406 s. La mesure additionne les deux tentatives, sans l'attente de relance : la relance seule serait passée. Délai de la baseline porté à 1 200 s (décision d'Adam, débit d'environ 10 à 18 tokens/s). Nouvel essai lancé dans l'heure, avec la baseline enchaînée | API très lente et instable (503 au premier essai, 2 fois sur 3 ce matin) ; 5 appels de chat consommés à 9 h 34 | Réessai prévu par la règle ; le quota de demain reste intact pour le filet de sécurité ; question sur la mesure (inclure ou non l'essai échoué) posée à Adam | — |
| 2026-10-27 | Exécution complète candidate `20261027-093507` (47 min, 14 appels) et baseline `20261027-102233` (9 sections sur 9, 22 références) ; liste de défauts de référence écrite sans ouvrir la relecture (30 de fond + 4 de forme + 2 invisibles depuis les extraits) | 2 sections en échec G1 (503 après relance) ; caractères nuls dans « enjeux FDA » (`\u0000e9` renvoyé par Gemini) ; conclusion sans accents ; quota du jour épuisé | Exécution non éligible comme officielle (critère technique) ; correctifs proposés à Adam (réparation de l'encodage, détection de l'absence d'accents, seconde relance, réutilisation de la baseline) ; validation de la liste par le groupe avant l'appariement | — |
| 2026-10-27 | Correctifs avant le gel : décodage des caractères NUL, alertes G1 (NUL restant, texte sans accents), G5 insensible aux accents (liste inchangée), jusqu'à 2 relances (60 s puis 2 × 60 s) avec un budget de 18 appels ; baseline du 27/10 officielle ; **gel** | Un *Wait* de plus de 65 s met l'exécution en attente dans la base et casserait la CLI ; besoin d'un compteur d'appels sur toute l'exécution | Deux attentes de 60 s ; `$execution.customData`, testé en CLI ; tous les chemins testés par simulation | à faire : capture de `10-argumentaire` gelé |
| 2026-10-27 | Liste de défauts de référence validée par Adam (15 de fond confirmés sur 30, 4 de forme sur 4, C1 et C2 rejetés), puis appariement avec `relecture_20261027-093507.json` : **1 défaut confirmé repéré sur 19** (B1, sections vides), 0 sur 15 de fond. Le seul problème de fond du relecteur porte sur A9, rejeté : à trier par un humain | Protocole de `pipeline.md` § 3 ; relecture ouverte après la validation |
| 2026-10-27 | Décisions sur l'appariement : ligne du § 5 sur le lien AHA → Apple/FDA reformulée (observé par Claude, non validé ; A25 confirmé, A9 et A18 rejetés), même mise à jour dans la critique et la synthèse de la liste ; résultat 1/19 (0/15 sur le fond) ajouté à la critique ; relecteur inchangé | Pipeline gelé |
| 2026-10-27 | Tri du problème ajouté par le relecteur (passage de A9) : **fausse alerte**, classé par Adam après avoir vu la sortie du relecteur ; score officiel inchangé, 1/19 | Protocole de `pipeline.md` § 3 |
| 2026-10-28 | **Exécution finale officielle `20261028-095239`** (lancée à 9 h 52 après resynchronisation de l'horloge de la VM, retard de 13 h 26 ; 59 min ; 11 appels de chat dont 1 relance, budget 18) : 9 sections sur 9, 34 paragraphes dont 3 `[INFORMATION NON DISPONIBLE]`, 8 signalés (G5 : 8, G4 : 1), aucun G1, aucun décodage. **Relecteur en échec : délai de 600 s atteint**, pas de relance (règle du 26/10 : un délai dépassé n'est pas relancé). Métriques avec la baseline `20261027-102233` ; fichiers d'évaluation humaine créés | Conclusion en 586 s : l'API reste très lente |
| 2026-10-28 | Tri de A9 remplacé par **vrai défaut** (Adam, après la sortie du relecteur ; score officiel inchangé, 1/19) ; § 5 et critique reformulés selon Adam (lien AHA → Apple/FDA « observé par Claude dans toutes les sorties, non validé par le groupe ») ; `oral.md` ajouté, puis complété avec les résultats de l'exécution finale ; procédure de resynchronisation de l'horloge dans CLAUDE.md | Consignes d'Adam du 28/10 |
