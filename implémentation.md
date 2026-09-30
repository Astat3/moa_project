# Implémentation — journal des étapes
Trace écrite de la construction du pipeline. Elle sert de matière première pour le **rapport** (partie « Méthodologie et difficultés ») et pour l'**oral**.

> Pour chaque étape, noter : **objectif · ce qu'on a fait · nœuds n8n utilisés · difficulté rencontrée · solution · capture d'écran à garder**.
> Les captures d'écran vont dans `captures/NN-nom.png`, pour le rapport et les slides.

---

## Vue d'ensemble

| # | Étape | Livrable | Temps estimé (avec Claude) | Difficulté /10 |
|---|---|---|---|---|
| 0 | Cadrage : position, choix des LLM, critères d'inclusion | Décisions notées dans `CLAUDE.md` | 2 h | 2 |
| 1 | Environnement local (Docker, n8n, Qdrant, LLM) | `docker-compose.yml` fonctionnel | 2–4 h | 3 |
| 2 | Constitution du corpus (sélection, validation par l'équipe, PDF, `meta.json`) | `corpus/` + `corpus.md` | 3–5 h | 3 |
| 3 | Ingestion RAG (WF00) | Collection Qdrant avec métadonnées | 3–5 h | 5 |
| 4 | Rédaction par section avec citations (WF10) | Brouillon de l'argumentaire | 4–6 h | 6 |
| 5 | Garde-fous G1–G4 (WF20) | Rapport de vérification automatique | 5–7 h | 7 |
| 6 | Agent examinateur (WF30) | Liste de problèmes + version corrigée | 3–4 h | 5 |
| 7 | Assemblage + bibliographie générée par le code (WF40) | `argumentaire_<run_id>.md` | 2–3 h | 3 |
| 8 | Baseline + évaluation qualité (WF50/60) | `metriques.csv` + évaluation humaine | 6–8 h | 7 |
| 9 | Rapport écrit + graphical abstract | `Ecrit_….pdf` | 6–8 h | 4 |
| 10 | Oral : slides + répétition | `Oral_….pdf` | 4–6 h | 3 |
| | **Total** | | **≈ 40–58 h** | **Global : 5,5/10** |

---

## Étape 0 — Cadrage
- [x] Position : POUR
- [x] Option B : corpus choisi par le groupe (pas de recherche PubMed automatisée)
- [x] LLM : API Mistral (décision du 2026-09-30)
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
- **Choix** : n8n utilise SQLite (pas de Postgres). Pas d'Ollama, le LLM passant par l'API Mistral. Variables `GENERIC_TIMEZONE` et `TZ` à Europe/Paris, `N8N_DIAGNOSTICS_ENABLED=false`.
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
- **À faire (par l'utilisateur)** : créer le compte propriétaire sur http://localhost:5678, puis les credentials « Mistral Cloud API » (la clé) et « Qdrant API » (URL `http://qdrant:6333`, sans clé).
- **Captures à garder** : `captures/01-podman-ps.png` (conteneurs actifs) et `captures/01-n8n-credentials.png` (credentials validés).

> Le détail technique de chaque workflow (nœuds, prompts, schémas JSON) est dans `pipeline.md`. Ici, on consigne ce qui a été fait, les difficultés et les solutions.

## Étape 2 — Constitution du corpus
- Corpus v0 (20 documents, 5 versants, dont 7 « contre » à réfuter) dans `corpus.md`
- [ ] Validation par l'équipe
- [ ] Récupération des PDF en texte intégral dans `corpus/` (via la BU pour les documents payants)
- [ ] `corpus/meta.json` : source unique de vérité pour la bibliographie
- [ ] Combler les trous (médico-économie, statut CE, faux positifs et surdiagnostic)

**Notes :**

## Étape 3 — Ingestion RAG (WF00)
- PDF → extraction → nettoyage → chunks (≈ 1 000 caractères, chevauchement de 150, à justifier) → `mistral-embed` → Qdrant `moa_corpus`
- Métadonnées par chunk : `chunk_id`, `doc_id`, `versant`, `role`, `page`
- Contrôle : nombre de chunks par document ; alerte si le texte extrait fait moins de 500 caractères (PDF scanné)

**Notes :**

## Étape 4 — Rédaction (WF10)
- Un appel par section, top-k ≈ 8 plus un filtre `role = contre` pour forcer les contre-arguments
- **Règle : aucune affirmation sans `chunk_id` cité**, sortie JSON structurée, `[INFORMATION NON DISPONIBLE DANS LE CORPUS]` si l'information manque

**Notes :**

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
- **Baseline** : même modèle Mistral, même consigne, sans RAG ni garde-fous
- Métriques : % d'affirmations soutenues, % de références existantes et correctes, % de chiffres retrouvés, couverture des sections, contre-arguments traités, problèmes relevés par l'examinateur, tokens, coût et durée
- Double évaluation humaine en aveugle sur un échantillon d'affirmations, avec kappa

**Résultats :**

## Étape 9 — Rapport écrit
- [ ] Graphical abstract (figure d'ouverture)
- [ ] Description du pipeline et de la méthodologie
- [ ] Contrôle qualité (méthodes citées)
- [ ] Critique des résultats
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

**Questions probables à préparer** : fonctionnement du PPG et pourquoi le *cuffless* reste débattu · différence entre 510(k) et De Novo et marquage CE · biais de LLM-as-a-judge · pourquoi ce choix de modèle · reproductibilité · RGPD et envoi de données à une API.

---

## Journal chronologique
| Date | Ce qui a été fait | Difficulté | Solution | Capture |
|---|---|---|---|---|
| 2026-09-30 | Lecture des consignes, création de `CLAUDE.md` et `implémentation.md` | — | — | — |
| 2026-09-30 | Choix du LLM : API Mistral | Pas de clé API au départ, un modèle local jugé trop faible pour la rédaction | Clés Mistral (argument RGPD) | — |
| 2026-09-30 | Option B retenue (corpus choisi par le groupe) ; corpus v0 et spec `pipeline.md` rédigés | Un seul article ne couvrait pas tous les versants imposés | Corpus de 15–20 documents + RAG | — |
| 2026-09-30 | Étape 1 : stack n8n 2.41.4 + Qdrant 1.19.1 sous Podman, vérifiée (santé, réseau, persistance) | Quota de téléchargement sur `docker.n8n.io` ; clé de chiffrement affichée pendant un contrôle | Image prise sur Docker Hub ; clé régénérée avant le premier démarrage | à faire : `01-podman-ps.png` |
| 2026-09-30 | Clé d'API sur Qdrant (`QDRANT_API_KEY` dans `.env`, `QDRANT__SERVICE__API_KEY` dans le compose) : 401 sans clé, 200 avec | Impossible de recréer qdrant seul, à cause de la dépendance dure créée par podman-compose | `down` puis `up -d` (volumes conservés) | — |
