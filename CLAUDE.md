# CLAUDE.md — Mémoire du projet
Projet 26/27 · MOA IA & Systèmes d'aide à la décision clinique · **Sujet 2 (technique)**

> Ce fichier est la mémoire du projet. Il doit être relu au début de chaque session et mis à jour à la fin.
> Le détail chronologique des étapes se trouve dans `implémentation.md`.

---

## 1. Le sujet en une phrase
Construire un **pipeline IA (orchestré en local avec n8n)** qui va de la revue de la littérature jusqu'à la génération d'un **argumentaire structuré et sourcé (pour OU contre)** sur l'autorisation FDA de l'Apple Watch comme outil de dépistage de l'HTA. Le pipeline doit intégrer des **garde-fous**, un **agent de relecture** et un **contrôle qualité fondé sur la littérature**. Il faut ensuite **critiquer les résultats**.

## 2. Livrables et contraintes (d'après le PDF de consignes)
| Élément | Détail |
|---|---|
| Destinataires | rosy.tsopra@aphp.fr · benjamin.pariente@aphp.fr |
| Date limite | **02/11/2025 dans le PDF** ⚠️ Le projet porte l'intitulé 26/27 : il s'agit probablement de **02/11/2026**. **À confirmer avec l'enseignant.** |
| Fichier 1 | `Ecrit_Nom1_Nom2_NomX.pdf` (rapport écrit) |
| Fichier 2 | `Oral_Nom1_Nom2_NomX.pdf` (support de l'oral) |
| Oral | 10 min de présentation + 10 min de questions (sur le projet **et** sur les cours) |
| Soumission | Un seul envoi par groupe |
| Évaluation | Rapport, oral et présence active en cours. Le non-respect des consignes fait perdre des points |

### Structure imposée du rapport (Sujet 2)
1. **Figure de synthèse du pipeline** (façon *graphical abstract*). Elle ouvre le rapport.
2. **Description du pipeline et de la méthodologie** : techniques d'optimisation, garde-fous, difficultés rencontrées et solutions.
3. **Description du contrôle qualité** : méthodes **issues de la littérature, citées**.
4. **Critique des résultats** : ce qui marche, ce qui échoue, limites en pratique.
5. **Annexe** : l'argumentaire généré par l'IA, avec la structure suivante :
   - Contexte et problématique clinique (HTA, santé publique, modalités de mesure et limites, problématique du dépistage par un objet grand public)
   - Enjeux de l'approbation FDA (pourquoi, et dans quel contexte)
   - Arguments par versant :
     - Technique / scientifique : PPG, fiabilité du *cuffless*, reconstruction de la PA à partir du signal PPG, consensus et sociétés savantes, standards de validation
     - Éthique
     - Social / économique
     - Réglementaire : FDA, HIPAA, marquage CE / MDR, RGPD
     - Intégration dans le parcours de soins
     - Autres
   - Conclusion avec un **parti pris clair**

## 3. Informations du groupe
- Membres : **à compléter**
- Position : **POUR** l'autorisation FDA (décision du groupe, 2026-09-30)
- Validation du groupe par l'enseignant : **à faire / fait ?**
- Date de l'oral : **à compléter** (fixée par l'administration)

## 4. Architecture cible (v1, option B — détail dans `pipeline.md`)
```
[Corpus choisi par le groupe : 15–20 PDF + meta.json]   (corpus.md)
      │
 WF00 Ingestion : PDF → chunks → embeddings Gemini (`gemini-embedding-001`) → Qdrant (chunk_id, doc_id, versant, rôle)
      │
 WF10 Rédaction par section (Gemini) : citations obligatoires par chunk_id, contre-arguments forcés
      │
 WF20 Garde-fous : G1 structure · G2 citations · G3 fidélité (juge Claude Haiku) · G4 chiffres  ──► régénération (2 fois max)
      │
 WF30 Agent examinateur (Gemini) : liste de problèmes → 1 passe de correction
      │
 WF40 Assemblage : Markdown + bibliographie générée par le code depuis meta.json → Pandoc → PDF
      │
 WF50 Baseline (Gemini seul, sans RAG)  ──►  WF60 Évaluation : métriques pipeline vs baseline + évaluation humaine (kappa)
```

### Stack technique pressentie
- **n8n self-hosted 2.41.4** (base SQLite) + **Qdrant 1.19.1**, définis dans `docker-compose.yml` et lancés avec **Podman** (fichier compatible Docker)
  - Démarrage : `podman machine start` puis `podman compose up -d` · n8n : http://localhost:5678 · Qdrant : http://localhost:6333/dashboard
  - Depuis n8n, Qdrant est joignable à `http://qdrant:6333`. La clé `N8N_ENCRYPTION_KEY` est dans `.env` (gitignoré, modèle dans `.env.example`) et **ne doit jamais changer**.
  - Export des workflows (à versionner) : `podman exec moa_n8n_1 n8n export:workflow --backup --output=/home/node/workflows/`, ce qui les écrit dans `n8n/workflows/`
- **Vector store** : Qdrant
- **LLM** : **API Gemini de Google** (clé créée dans Google AI Studio, plan gratuit). Remplace Mistral depuis le 2026-09-30 (voir section 5).
  - Credential n8n : **« Google Gemini(PaLM) API »**, host `https://generativelanguage.googleapis.com`. La clé est saisie **uniquement** dans ce credential, par l'utilisateur : jamais dans `.env`, un workflow exporté, un terminal ou une conversation. Claude Code ne la lit jamais.
  - Génération : nœud *Google Gemini Chat Model*. Les ID de modèles disponibles et les **quotas du plan gratuit** (requêtes par minute et par jour, par modèle) se lisent dans Google AI Studio : ne pas les supposer, les reporter dans `pipeline.md`.
  - Embeddings : nœud *Embeddings Google Gemini*, modèle **`gemini-embedding-001`** (texte seul ; 3 072 dimensions par défaut, 768 ou 1 536 possibles). **La dimension de la collection Qdrant doit être exactement celle produite par le nœud.** Changer de modèle d'embeddings (ex. `gemini-embedding-2`) impose de tout réindexer : espaces vectoriels incompatibles.
  - **Argument RGPD à reformuler pour l'oral** : Google est un fournisseur américain, l'argument « fournisseur européen » tombe. En revanche, pour les utilisateurs de l'EEE, les conditions des services payants s'appliquent aussi au quota gratuit : les prompts et réponses ne servent pas à améliorer les modèles (Gemini API Additional Terms of Service, à citer). Le corpus ne contient que des publications, aucune donnée patient.
  - Ollama reste optionnel.
- **Claude (API Anthropic)** : une clé avec **environ 4 $ de crédit restant**, utilisable pour des tests. Même règle : clé saisie uniquement dans les *credentials* n8n.
- **Sources** : corpus choisi par le groupe (`corpus.md`, PDF dans `corpus/`, métadonnées dans `corpus/meta.json`). PubMed et Europe PMC ne servent qu'à la recherche manuelle et à la vérification des références de la baseline
- **Export** : Pandoc (Markdown vers PDF)

## 5. Décisions prises
| Date | Décision | Raison |
|---|---|---|
| 2026-09-30 | Sujet 2 uniquement, orchestration n8n en local | Choix du groupe |
| 2026-09-30 | **Option B** : corpus de 15–20 documents choisi par le groupe, puis RAG → agent rédacteur → garde-fous → agent examinateur → rapport. Pas de recherche PubMed automatisée | Conforme à l'exemple RAG de la consigne (« à partir d'un corpus d'articles »), difficulté réduite, plus de temps pour le contrôle qualité. Critères de sélection et équations de recherche manuelles à justifier en annexe. Corpus dans `corpus.md` |
| 2026-09-30 | LLM via API Mistral (plutôt qu'un modèle local) — **remplacé le jour même par l'API Gemini, voir plus bas** | Meilleure qualité de rédaction qu'un modèle local + argument RGPD |
| 2026-09-30 | Répartition des LLM : **Gemini (gratuit, initialement Mistral) pour le volume** (screening, rédaction, relecture) et **Claude Haiku uniquement comme juge** claim ↔ source (étape 6) | Budget Claude d'environ 4 $, soit ≈ 0,30 $ par passe de 150 affirmations. Un juge d'une autre famille de modèles limite le biais d'auto-préférence (LLM-as-a-judge, Zheng et al. 2023, à sourcer). En développement : tests sur 10–20 abstracts, et limite de dépense fixée dans la console Anthropic |
| 2026-09-30 | Fichier mémoire renommé `CLAUDE.md` | Chargement automatique par Claude Code |
| 2026-09-30 | Conteneurs lancés avec Podman plutôt que Docker Desktop | Podman déjà installé, Docker absent. Le `docker-compose.yml` reste utilisable tel quel avec Docker |
| 2026-09-30 | Stack réduite à n8n + Qdrant (pas de Postgres ni d'Ollama), versions figées | LLM via API, donc Ollama inutile ; SQLite suffit pour n8n ; versions figées pour la reproductibilité |
| 2026-09-30 | Ports ouverts sur 127.0.0.1 seulement ; télémétrie n8n désactivée ; fuseau horaire Europe/Paris | Pas d'exposition sur le réseau local ; argument RGPD ; horodatage cohérent des exécutions |
| 2026-09-30 | **Abandon de Mistral au profit de l'API Gemini (Google)** : génération via *Google Gemini Chat Model*, embeddings `gemini-embedding-001` | Le plan Free de Mistral Studio ne permet pas d'activer de clé API sans passer à un plan payant. Clé Google AI Studio gratuite disponible. Le juge G3 reste Claude Haiku : toujours une famille de modèles différente du rédacteur |

## 6. Questions ouvertes / à trancher
- [x] Position : POUR
- [x] Offre Mistral : le plan Free ne permet pas d'activer de clé API → passage à l'API Gemini
- [ ] Quotas du plan gratuit Gemini (requêtes/minute et /jour, par modèle, embeddings compris) : à relever dans Google AI Studio et à reporter dans `pipeline.md`
- [ ] Modèles Gemini retenus pour le rédacteur, l'examinateur et la baseline (baseline = même modèle que le rédacteur)
- [ ] Dimension des embeddings : 3 072 (défaut) ou 768 (plus léger, suffisant pour ce corpus) ? Vérifier que le nœud n8n expose ce réglage
- [ ] Double screening : deux modèles Gemini différents (ex. un grand et un petit) ou le même modèle avec deux prompts ?
- [ ] Comment accéder aux textes intégraux payants (accès via la BU / ajout manuel des PDF) ?
- [ ] Date limite réelle (2025 ou 2026) ?
- [ ] VM Podman limitée à 2 Go (partagée avec un autre projet) ; n8n occupe environ 690 Mo au repos. La passer à 4 Go si les grosses exécutions saturent (`podman machine stop && podman machine set --memory 4096 && podman machine start`)
- [ ] Désactiver aussi la télémétrie de Qdrant (`QDRANT__TELEMETRY_DISABLED=true`), par cohérence avec n8n ?
- [ ] Ollama 0.35.0 est installé via brew mais inutilisé : le garder (baseline locale ?) ou le retirer (`brew uninstall ollama`) ?

## 7. Faits à sourcer (ne pas utiliser sans source vérifiée)
- Autorisation FDA de type 510(k) pour la fonction « Hypertension Notifications » (septembre 2025). Vérifier sur le 510(k) summary.
- Fonctionnement : analyse passive du signal PPG sur environ 30 jours, **sans afficher de valeur tensionnelle**, avec une simple notification de « signes évocateurs ». Vérifier.
- Performances annoncées (sensibilité, spécificité) et population de validation. Vérifier.
- Restrictions d'usage (âge, grossesse, HTA déjà diagnostiquée). Vérifier.
- Position des sociétés savantes sur le *cuffless* (ESH, AHA…) et standards de validation (ISO 81060-2, IEEE 1708). Vérifier.
- Disponibilité et statut CE en Europe. Vérifier.

## 8. État d'avancement
| Étape | Statut |
|---|---|
| 0. Cadrage | ✅ position POUR, LLM Gemini + juge Claude, option B |
| 1. Environnement local | 🟡 stack opérationnelle et vérifiée. Reste : créer le compte n8n et les credentials Google Gemini + Qdrant, puis test de fumée Gemini |
| 2. Constitution du corpus | 🟡 v0 dans `corpus.md`, à valider avec l'équipe ; PDF à récupérer |
| 3. Ingestion (WF00) | ⚪ |
| 4. Rédaction (WF10) | ⚪ |
| 5. Garde-fous (WF20) | ⚪ |
| 6. Agent examinateur (WF30) | ⚪ |
| 7. Assemblage (WF40) | ⚪ |
| 8. Baseline + évaluation (WF50/60) | ⚪ |
| 9. Rapport écrit | ⚪ |
| 10. Oral | ⚪ |

## 9. Conventions de travail avec Claude
- Répondre en français, de façon directe et concrète.
- **Aucune correction silencieuse** : signaler toute erreur (de fond, de lien, de structure) et attendre l'accord avant de corriger.
- Ne pas signaler comme défauts les états transitoires du chantier.
- Toute affirmation factuelle intégrée au rapport doit avoir une source vérifiée (les sources sont contrôlées au hasard par les enseignants).
- Mettre à jour les sections 5, 6 et 8 à la fin de chaque session, et consigner l'étape dans `implémentation.md`.
