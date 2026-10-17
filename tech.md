# tech.md — Notes techniques et trace des choix
Carnet de bord des notions techniques du pipeline et des choix faits en séance avec Claude (chat). Il sert à **comprendre** le pipeline, à **justifier** les choix dans le rapport et à **préparer les questions** de l'oral.

> Rôle des fichiers : `CLAUDE.md` = mémoire du projet (décisions, état) · `pipeline.md` = contrat d'implémentation · `implémentation.md` = journal des étapes · **`tech.md` = explications et justifications**.

---

## 1. Le workflow en une ligne

**Ingestion** (une fois, puis à chaque ajout d'article)
Corpus → Extraction → Chunking → Embedding → Indexation

**Rédaction** (pour chaque section)
Requête → Embedding → Récupération → Rédaction → Garde-fous → Relecture → Correction → Assemblage

**Autour du pipeline**
Baseline → Évaluation → Rapport

---

## 2. Notions clés

### 2.1 Chunking (découpage)
- **Quoi** : couper chaque document en petits passages avant de les vectoriser.
- **Pourquoi** : un embedding résume un texte en un seul vecteur. Avec un article entier, ce vecteur devient une moyenne floue de tout l'article, et une question précise ne tombe près de rien de net. Avec des chunks, chaque vecteur porte une idée précise.
- **Bénéfices** : un contexte léger pour le LLM (les passages pertinents plutôt que des articles entiers) et une citation vérifiable (chaque affirmation pointe vers un passage précis).
- **Deux réglages** :
  - la **taille** : trop petit, le chunk perd son contexte (« l'erreur était de 8 mmHg », mais de quel appareil ?) ; trop grand, il redevient flou ;
  - le **chevauchement** : chaque chunk reprend la fin du précédent, pour qu'une idée coupée reste entière dans l'un des deux.
- **Stratégies** : taille fixe (simple, mais coupe au milieu des phrases) · **récursive** (paragraphes, puis phrases ; nœud *Recursive Character Text Splitter*) · par section d'article.
- **Choix retenu** : récursif, **1 000 caractères avec 150 de chevauchement** (voir §4).

### 2.2 Embedding (vectorisation)
- **Quoi** : transformer un texte en une liste de nombres (un vecteur) qui représente son **sens**.
- **Image** : une carte où chaque texte est placé selon ce qu'il veut dire. « Mesure de la tension sans brassard » et « cuffless blood pressure estimation » tombent au même endroit ; une recette de cuisine tombe à l'autre bout. Au lieu de 2 dimensions, il y en a des centaines ou des milliers. **Proximité géométrique = proximité de sens.**
- **Origine** : un réseau de neurones entraîné à rapprocher les textes qui vont ensemble (question et réponse, paraphrases) et à éloigner les autres. Aucune dimension ne veut dire quelque chose de lisible à elle seule : le sens est réparti sur l'ensemble.
- **Mesure de proximité** : en général la **similarité cosinus**, c'est-à-dire l'angle entre deux vecteurs.
- **Règles pratiques** :
  - le **même modèle** à l'ingestion et à la requête, sinon les deux « cartes » ne correspondent pas ; changer de modèle impose de tout réindexer ;
  - la **dimension de la collection Qdrant** doit être exactement celle du modèle, sinon l'insertion plante.
- **Modèle retenu** : `gemini-embedding-001` (texte seul ; 3 072 dimensions par défaut, 768 ou 1 536 possibles).
- **Limites, utiles pour la partie critique du rapport** :
  - **la négation passe mal** : « la montre est fiable » et « la montre n'est pas fiable » ont des vecteurs très proches ;
  - **les chiffres aussi** : « erreur de 5 mmHg » et « erreur de 15 mmHg » sont quasi indiscernables ;
  - **proximité n'est pas pertinence** : une introduction qui *mentionne* le cuffless peut sortir devant des résultats qui le *mesurent*.
  → Ces limites expliquent pourquoi le RAG seul ne suffit pas, et pourquoi les garde-fous existent (bon enchaînement pour l'oral).

### 2.3 Indexation
- **Stockage** : chaque chunk devient un **point** dans une **collection** Qdrant (`moa_corpus`), avec :
  - un identifiant ;
  - son vecteur ;
  - son **payload** : le texte du chunk et ses métadonnées (`chunk_id`, `doc_id`, `versant`, `role`, `page`).
  Le texte voyage avec le vecteur : l'agent reçoit directement le passage lisible et sa référence.
- **Index de recherche HNSW** (*Hierarchical Navigable Small World*) : un graphe de voisins organisé en niveaux, comme un réseau routier (autoroutes en haut, rues en bas). La recherche part d'en haut puis affine, et ne compare la requête qu'à une petite fraction des vecteurs. En contrepartie, elle est **approximative** et rate rarement le voisin exact.
- **Pour notre projet** : quelques milliers de chunks au plus, donc une comparaison exhaustive irait aussi vite, et Qdrant ne construit pas le graphe HNSW sous un certain seuil. HNSW vaut une phrase à l'oral si on demande comment le système passerait à l'échelle.
- Qdrant peut aussi indexer les métadonnées pour **filtrer** (ex. `role = contre`).

### 2.4 Qdrant : pourquoi et où dans le workflow
- **Rôle** : c'est la **seule mémoire documentaire** du pipeline. Les agents n'écrivent rien qui n'en vienne, ce qui rend chaque affirmation traçable jusqu'à son article.
- **Sans Qdrant**, le LLM répond avec ce qu'il a appris à l'entraînement (invérifiable, parfois inventé). **Avec Qdrant**, il répond avec le corpus choisi et contrôlé par le groupe.
- **Trois moments d'usage** :
  1. **ingestion** (écriture) : les chunks vectorisés sont insérés ;
  2. **rédaction** (lecture) : la requête de la section est vectorisée, Qdrant renvoie les k passages les plus proches, et le rédacteur n'écrit qu'à partir d'eux ;
  3. **vérification** : les garde-fous et l'examinateur relisent le chunk cité derrière chaque affirmation.
- **Pourquoi Qdrant plutôt qu'autre chose** : persistance · filtrage par métadonnées · exécution locale (les données restent sur la machine) · nœud natif dans n8n · open source et gratuit. Ce n'est **pas** un choix de performance, vu la taille du corpus. Alternatives possibles : *Simple Vector Store* de n8n (vidé à chaque redémarrage), pgvector, Chroma.

---

## 3. Recherche bibliographique : lire une équation PubMed
Exemple :
```
("Hypertension"[Mesh] OR hypertens*[tiab] OR "blood pressure"[tiab])
AND ("Wearable Electronic Devices"[Mesh] OR "Photoplethysmography"[Mesh] OR smartwatch*[tiab] OR wearable*[tiab] OR cuffless[tiab] OR cuff-less[tiab])
AND (screening[tiab] OR detection[tiab] OR validation[tiab] OR accuracy[tiab])
```
- **Logique** : trois blocs de concepts reliés par `AND` (tous obligatoires), chacun composé de synonymes reliés par `OR` (un seul suffit). Les blocs portent sur : 1) la PA ou l'HTA ; 2) l'objet connecté ou la mesure sans brassard ; 3) la performance diagnostique.
- **`[Mesh]`** : le vocabulaire contrôlé de la NLM, attribué par des indexeurs. Le terme est « explosé » par défaut, c'est-à-dire qu'il inclut ses sous-termes.
- **`[tiab]`** : le titre et le résumé. Rattrape les articles récents, pas encore indexés en MeSH.
- **`*`** : la troncature (`hypertens*` couvre hypertension, hypertensive…).
- **Guillemets** : l'expression exacte.
- **`cuffless` / `cuff-less`** : les deux graphies coexistent, et PubMed ne les considère pas comme équivalentes.
- **Principe** : MeSH pour la précision, texte libre pour l'exhaustivité.
- ⚠️ **Point signalé** : le bloc 3 risque d'exclure les études techniques qui parlent d'*estimation*, de *monitoring* ou de *measurement*. Pistes : ajouter ces termes, ou supprimer le bloc. Comparer le nombre de résultats des deux versions (chiffre utile pour le diagramme de flux).
- Avec l'option B (corpus choisi par le groupe), ces équations servent à la recherche **manuelle** et doivent être justifiées en annexe.

---

## 4. Choix techniques de la séance du 30/09/2026

| Sujet | Choix | Justification |
|---|---|---|
| **LLM** | API **Gemini** (Google AI Studio) à la place de Mistral | Le plan Free de Mistral Studio ne permet pas d'activer de clé API sans passer à un plan payant. Clé Google gratuite disponible |
| **Juge G3** | Claude Haiku (inchangé) | Un juge d'une autre famille que le rédacteur limite le biais d'auto-préférence |
| **Embeddings** | `gemini-embedding-001` | Texte seul, compatible avec le nœud n8n. La dimension de la collection Qdrant doit être identique |
| **Métadonnées du corpus** | `corpus/meta.json` (et non un CSV) | Source unique de la bibliographie (garde-fou principal) ; contient `reference`, `role` et `doc_id` ; gère plusieurs versants par document. Ajouter un contrôle de validité du JSON en tête de WF00 |
| **Chunking** | Récursif, **1 000 caractères / 150** | Des chunks courts rendent G3 (fidélité) et G4 (chiffres) plus stricts : moins de texte, donc moins de « soutien » vague ou de chiffre trouvé par hasard. Citation plus précise. Le chevauchement et les métadonnées compensent la perte de contexte |
| **Chunking, expérience prévue** | Comparer 1 000 et ≈ 3 200 caractères | Mesurer la pertinence des chunks récupérés et le taux de `NON_SOUTENU` : un paramètre justifié par une mesure |
| **Documents de la première tranche** | n°6 Apple + n°7 FDA K250507 + n°9 Elgendi + n°12 AHA 2025 | Tous les rôles sont couverts (pour, contexte réglementaire, contexte technique, contre), ce qui permet de tester le filtre `role = contre`. Signaler tout document qui ne serait pas en accès libre au lieu de le remplacer |
| **Conversion OCR PDF → Markdown** | Reportée | On construit d'abord le cœur du pipeline. La collection Qdrant de test est **jetable** : elle sera vidée et réingérée quand la conversion arrivera |

### RGPD : l'argument change
- Google est un fournisseur américain : l'argument « fournisseur européen » ne tient plus.
- Pour les utilisateurs de l'EEE, les conditions des services **payants** s'appliquent aussi au quota gratuit de l'API Gemini : les prompts et réponses **ne servent pas** à améliorer les modèles (Gemini API Additional Terms of Service, à citer).
- Le corpus ne contient que des publications : **aucune donnée patient**.
- Autres mesures à citer : ports ouverts sur 127.0.0.1 seulement, télémétrie n8n désactivée, clés uniquement dans les credentials n8n.

---

## 5. Mise en place : pas-à-pas réalisés ou à faire

### 5.1 Connecter Qdrant à n8n
1. Vérifier que Qdrant tourne : http://localhost:6333/dashboard.
2. Clé API Qdrant : `QDRANT_API_KEY` générée dans `.env` (jamais affichée), transmise au conteneur par `QDRANT__SERVICE__API_KEY`. Vérifié : 401 sans clé, 200 avec.
3. Dans n8n : **Credentials → Qdrant API**, avec pour URL **`http://qdrant:6333`** (et non `localhost`, qui désigne le conteneur n8n lui-même) et la valeur de `QDRANT_API_KEY` comme clé.
4. Nœud **Qdrant Vector Store** : mode *Insert* pour l'ingestion, *Retrieve* (ou *tool* d'agent) pour la rédaction. Même nom de collection et même nœud d'embeddings des deux côtés.

**Dépannage**
- *Connection refused* : l'URL est sur `localhost`, ou les conteneurs ne sont pas dans le même compose.
- *Unauthorized* : la clé ne correspond pas, ou le conteneur n'a pas été redémarré.
- *Erreur de dimension* : la collection a été créée avec une autre taille de vecteur. La supprimer et la laisser se recréer.

### 5.2 Connecter Gemini à n8n
1. **Credentials → Google Gemini(PaLM) API** : host `https://generativelanguage.googleapis.com`, clé collée par l'utilisateur (jamais dans `.env`, un terminal ou une conversation).
2. Test de fumée : *Manual Trigger* → *Basic LLM Chain* + *Google Gemini Chat Model*, avec le prompt « Réponds uniquement OK ». Capture `captures/01-test-gemini.png`.
3. Relever dans AI Studio les **quotas gratuits** (par minute **et par jour**, par modèle) et les reporter dans `pipeline.md`.

### 5.3 Partager le dépôt avec le groupe
1. Avant tout push : `git status`, où **`.env` ne doit pas apparaître**, et `git check-ignore .env`, qui doit répondre `.env`.
2. Sur GitHub, créer un dépôt **privé** sans rien cocher, ou lancer `gh repo create moa-pipeline --private --source=. --push`.
3. Sinon : `git add .` → `git commit` → `git branch -M main` → `git remote add origin <url>` → `git push -u origin main`.
4. Inviter les membres : **Settings → Collaborators**.
5. Chaque membre recrée son `.env` depuis `.env.example`, recrée ses credentials n8n (ils ne sont jamais exportés) et importe les workflows JSON de `n8n/workflows/`.

### 5.4 Constitution du corpus : repères
- Cible : **15 à 25 documents**, répartis par versant. Garder des sources « contre » : les citer puis les réfuter rend l'argumentaire plus solide.
- Normes payantes (ISO 81060-2, IEEE 1708) : des articles qui les décrivent suffisent.
- Extraction brute des PDF : colonnes mélangées, en-têtes et bibliographie dans les chunks. D'où la conversion en Markdown prévue plus tard (Mistral OCR n'est plus disponible : à revoir, ex. Europe PMC pour les textes en libre accès, ou une autre solution d'OCR).

---

## 6. Points signalés, en attente de décision
- [ ] `implémentation.md`, tâche « à faire » de l'étape 1 : le credential Qdrant y est décrit « sans clé », ce qui n'est plus vrai depuis l'ajout de `QDRANT_API_KEY`.
- [ ] `CLAUDE.md` : la question du « double screening », et le mot *screening* dans la décision sur la répartition des LLM, datent d'avant l'option B (plus de screening par LLM). À supprimer ?

---

## 7. Questions d'oral à préparer (côté technique)
- Pourquoi un RAG plutôt qu'un LLM seul ? → traçabilité, corpus contrôlé, comparaison avec la baseline.
- Pourquoi Qdrant ? → persistance, filtrage par métadonnées, exécution locale, intégration n8n.
- Comment avez-vous choisi la taille des chunks ? → lien avec G3 et G4, puis l'expérience 1 000 vs 3 200.
- Quelles sont les limites des embeddings ? → négation, chiffres, proximité ≠ pertinence, d'où les garde-fous.
- Pourquoi un juge d'une autre famille de modèles ? → biais d'auto-préférence (LLM-as-a-judge).
- Et le RGPD, avec une API américaine ? → conditions EEE, aucune donnée patient, exécution locale du reste.
- Pourquoi avoir changé de fournisseur de LLM ? → contrainte d'accès (plan gratuit Mistral), et impact sur l'argument RGPD.
