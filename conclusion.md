# Conclusion de la session du 30/09/2026
Trace de la session : ce qui a été fait, les résultats des tests, et ce qu'il reste à faire.
Le détail technique est consigné dans `implémentation.md` (étapes 1, 2 et 3, et journal chronologique).

---

## 1. En bref
- Qdrant est protégé par une clé d'API.
- Un corpus de test de 3 PDF est ingéré dans Qdrant : **153 chunks** dans la collection `moa_corpus`.
- Les deux workflows n8n tournent de bout en bout : `00-ingestion` et `test-retrieval`.
- **La qualité du retrieval est encore faible** : sur 5 chunks, 1 est pertinent, 2 le sont en partie et 2 sont du bruit (bibliographie).
- Principale contrainte découverte : le **quota gratuit de Gemini, 100 embeddings par minute**.

---

## 2. Ce qui a été fait

### 2.1 Clé d'API Qdrant
- `QDRANT_API_KEY` a été générée (`openssl rand -hex 32`) et écrite directement dans `.env`, sans jamais être affichée.
- `.env.example` a été complété (variable sans valeur).
- `docker-compose.yml` : ajout de `QDRANT__SERVICE__API_KEY=${QDRANT_API_KEY}` dans le service `qdrant`.

### 2.2 Corpus de test
| doc_id | Fichier | Document | Rôle | Versant |
|---|---|---|---|---|
| D06 | `apple_validation_2025.pdf` | Apple, *Hypertension Notification Feature on Apple Watch*, validation paper, sept. 2025 | pour | technique, fda |
| D07 | `fda_K250507.pdf` | FDA, 510(k) K250507, lettre du 11/09/2025 (corrigée le 12/09/2025) + 510(k) Summary | contexte | reglementaire, fda |
| D09 | `elgendi_2019_npjdm.pdf` | Elgendi M et al. *The use of photoplethysmography for assessing hypertension.* npj Digit Med 2019;2:60 | contexte | technique |

- `corpus/meta.json` reprend le schéma de `pipeline.md`, avec deux champs en plus : `annee` et `type_source`.
- Les références ont été vérifiées sur les PDF eux-mêmes.
- D12 (AHA 2025, *cuffless*) n'a pas pu être téléchargé automatiquement (voir 4.1).

### 2.3 Montage du corpus dans n8n
- `docker-compose.yml`, service `n8n` :
  - volume `./corpus:/home/node/corpus:ro` ;
  - variable `N8N_RESTRICT_FILE_ACCESS_TO=/home/node/corpus`, car n8n 2.x limite par défaut les nœuds de fichiers à `~/.n8n-files`.

### 2.4 Workflows n8n (dans `n8n/workflows/`, importés via la CLI)
**`00-ingestion.json`** (ID `MoaWf00Ingestion`)
- Enchaînement : lecture de `meta.json` → un item par document → lecture du PDF → texte page par page → un item par page (avec les métadonnées) → lots de 6 pages → Qdrant (insertion) → pause de 60 s → lot suivant.
- Le nœud Qdrant est alimenté par trois sous-nœuds :
  - *Default Data Loader* ;
  - *Recursive Character Text Splitter* (**1 000 caractères, chevauchement de 150**, paramètres à évaluer plus tard) ;
  - *Embeddings Google Gemini* (`gemini-embedding-001`).
- Métadonnées par chunk : `doc_id`, `fichier`, `page`, `annee`, `type_source`, `versant`, `role`.

**`test-retrieval.json`** (ID `MoaTestRetrieval`)
- Une question fixe → même modèle d'embeddings → Qdrant, top 5 → affichage du rang, du score, du `doc_id`, de la page, des métadonnées et du texte.

---

## 3. Résultats des tests

### 3.1 Clé d'API Qdrant
| Requête | Résultat |
|---|---|
| `/collections` sans clé | **401** ✅ |
| `/collections` avec une mauvaise clé | **401** ✅ |
| `/collections` avec la bonne clé | **200** ✅ |
| Depuis le conteneur n8n, sans clé | **401** ✅ |
| `/readyz` sans clé | 200 (sonde de santé, reste ouverte) |

### 3.2 Premier essai d'ingestion : ❌ échec
- Qdrant a renvoyé l'erreur **422** : *dense vector must not be empty*. Les 100 premiers vecteurs étaient vides.
- **Cause, confirmée dans le code de LangChain** (`@langchain/google-genai` 2.1.24) : les lots d'embeddings partent en parallèle, et un lot en erreur est remplacé **silencieusement** par des vecteurs vides. Seule la validation de Qdrant a empêché l'insertion de données corrompues.

### 3.3 Diagnostic du quota Gemini
- Un workflow temporaire a appelé `batchEmbedContents` via le credential n8n, sans que la clé soit jamais lue ni affichée.
- Réponse : **429 `RESOURCE_EXHAUSTED`**.
  - Quota : `EmbedContentRequestsPerMinutePerUserPerProjectPerModel-FreeTier`.
  - Valeur : **100 par minute**.
- **Chaque texte d'un lot compte comme une requête.** Ce n'est pas écrit dans l'erreur, c'est déduit : quelques appels de 100 textes ont suffi à épuiser la minute.
- Le **quota journalier** reste inconnu (voir 4.2).

### 3.4 Ingestion par lots : ✅ succès
| Mesure | Valeur |
|---|---|
| Pages traitées | 40 |
| Chunks insérés | **153** : D06 = 23, D07 = 47, D09 = 83 |
| Durée | 434 s (7 lots + pauses) |
| Taille des chunks | 65 à 1 000 caractères, 876 en moyenne |
| Collection `moa_corpus` | 3 072 dimensions, distance cosinus |
| Types des métadonnées | conservés : `versant` en liste, `page` et `annee` en entiers |

### 3.5 Test de retrieval
Question : *« Quelle est la fiabilité des dispositifs de mesure de pression artérielle sans brassard ? »*

| Rang | Score | Source | Contenu | Pertinence |
|---|---|---|---|---|
| 1 | 0,7370 | D09 p. 10 | Bibliographie (réf. 41 à 45) | ❌ bruit |
| 2 | 0,7370 | D09 p. 5 | Applis smartphone ; « no clinical study validates the use of this product » ; Wang et al. ±6,7 mmHg | 🟡 partielle |
| 3 | 0,7365 | D09 p. 4 | Retrait de l'appli Instant Blood Pressure + tableau 1 mal extrait | 🟡 partielle |
| 4 | 0,7308 | D09 p. 10 | Bibliographie (réf. 37 à 41) | ❌ bruit |
| 5 | 0,7304 | D09 p. 6 | Petits effectifs, sujets sains, « difficult to confidently understand the accuracy » | ✅ pertinente |

**Bilan : 1 chunk pertinent, 2 partiels, 2 de bruit.** Tous viennent du même document, avec des scores très resserrés.

Causes probables :
- les bibliographies sont indexées, et leurs titres contiennent « cuff-less blood pressure » ;
- D12 (AHA), le document le plus pertinent pour cette question, manque ;
- la question est en français et le corpus en anglais ;
- le nœud Gemini ne permet pas de préciser s'il s'agit d'une requête ou d'un document (le *task type*).

---

## 4. Ce que tu dois faire

### 4.1 Actions
- [ ] **Télécharger D12 à la main** : Cohen JB et al., *Cuffless Devices for the Measurement of Blood Pressure: A Scientific Statement From the AHA*, Hypertension, 2026;83(3):e00254, DOI 10.1161/HYP.0000000000000254 (PMC13335599).
  - Le téléchargement automatique est bloqué : 403 sur Europe PMC et sur ahajournals, vérification anti-robot sur PMC.
  - L'enregistrer sous `corpus/aha_cuffless_2025.pdf`. Claude l'ajoutera ensuite à `meta.json` et relancera l'ingestion.
- [ ] **Relever les quotas Gemini dans Google AI Studio**, surtout le quota **journalier**. Il décide si le corpus complet (15 à 20 documents) peut être ingéré en une journée. À reporter dans `pipeline.md`.
- [ ] **Supprimer le workflow `zz-diag-gemini (temporaire, à supprimer)`** dans l'interface n8n (la CLI n'a pas de commande de suppression).
- [ ] **Faire une capture du workflow `00-ingestion`** pour le rapport et l'oral.
- [ ] **Commiter** quand tu le souhaites : rien n'a été commité pendant cette session.

### 4.2 Décisions à prendre
- [ ] **Nettoyage du texte avant découpage** : retirer les bibliographies, les numéros d'appel de référence et les césures, puis relancer le test. C'est l'amélioration la plus rentable.
- [ ] **Valider les rôles et versants** de `meta.json` : D06 `pour` ; D07 `contexte` ; D09 `contexte`.
- [ ] **Corriger `corpus.md`, ligne n° 7 ?**
  - Le texte parle d'une nouvelle classification « Hypertension Machine Learning-Based Notification Software ».
  - Le PDF de la FDA indique la réglementation **existante** 21 CFR 870.2380 (« Cardiovascular Machine Learning-Based Notification Software »), avec la création d'un **code produit** (QXO puis SFR).
- [ ] **Corriger `implémentation.md`, ligne 64 ?** Elle dit de créer le credential Qdrant « sans clé », alors que la clé est maintenant obligatoire.
- [ ] **Mettre à jour `pipeline.md` ?** Nouveau déroulé de WF00 (page par page, lots, pause) et quota Gemini.
- [ ] **Mettre à jour `CLAUDE.md` ?**
  - Section 6 : dimension des embeddings = 3 072 (non réglable dans le nœud), quota de 100 par minute.
  - Section 8 : avancement des étapes 2 et 3.
- [ ] **Protéger la clé Qdrant contre l'oubli ?** Passer à `${QDRANT_API_KEY:?…}` dans `docker-compose.yml`, comme pour `N8N_ENCRYPTION_KEY` : Docker refuserait alors de démarrer si la clé manque, au lieu de lancer Qdrant sans protection.
- [ ] **Versionner les PDF de `corpus/` dans git ?** Le PDF d'Apple pèse 15 Mo, et les droits de diffusion sont à vérifier.
- [ ] **Tester la question en anglais**, pour mesurer l'effet d'une recherche français → anglais.

---

## 5. Commandes utiles
```bash
# Importer un workflow après modification du JSON
podman exec moa_n8n_1 n8n import:workflow --input=/home/node/workflows/00-ingestion.json

# Exécuter un workflow en CLI (le port 5690 évite le conflit avec le n8n déjà lancé)
podman exec -e N8N_RUNNERS_BROKER_PORT=5690 moa_n8n_1 n8n execute --id=MoaWf00Ingestion
podman exec -e N8N_RUNNERS_BROKER_PORT=5690 moa_n8n_1 n8n execute --id=MoaTestRetrieval

# Supprimer la collection avant une nouvelle ingestion : l'ingestion n'est pas idempotente, sinon les chunks sont en double
Q=$(sed -n 's/^QDRANT_API_KEY=//p' .env); curl -s -X DELETE -H "api-key: $Q" http://127.0.0.1:6333/collections/moa_corpus

# Copier la clé Qdrant dans le presse-papiers sans l'afficher (credential n8n, tableau de bord)
sed -n 's/^QDRANT_API_KEY=//p' .env | pbcopy
```

---

## 6. Fichiers créés ou modifiés
| Fichier | Modification |
|---|---|
| `.env` | + `QDRANT_API_KEY` (non versionné) |
| `.env.example` | + `QDRANT_API_KEY=` |
| `docker-compose.yml` | clé API Qdrant ; montage `./corpus` et `N8N_RESTRICT_FILE_ACCESS_TO` pour n8n |
| `corpus/` | 3 PDF + `meta.json` |
| `n8n/workflows/00-ingestion.json` | nouveau |
| `n8n/workflows/test-retrieval.json` | nouveau |
| `implémentation.md` | notes des étapes 1, 2 et 3 + 3 lignes du journal |
| `conclusion.md` | ce fichier |

## Sources
- Apple. Hypertension Notification Feature on Apple Watch, sept. 2025 : https://www.apple.com/health/pdf/Hypertension_Notifications_Validation_Paper_September_2025.pdf
- FDA. 510(k) K250507 : https://www.accessdata.fda.gov/cdrh_docs/pdf25/K250507.pdf
- Elgendi M et al. npj Digit Med 2019;2:60 : https://www.nature.com/articles/s41746-019-0136-7
- Cohen JB et al. AHA Scientific Statement, cuffless : https://www.ahajournals.org/doi/10.1161/HYP.0000000000000254
