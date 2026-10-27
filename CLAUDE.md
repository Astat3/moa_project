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

### Consignes du sujet 2 (texte de l'enseignant, transmis le 21/10/2026)
Il est demandé :
- d'implémenter un **pipeline IA allant de la revue de la littérature jusqu'à la génération d'un rapport structuré** ;
- de mettre en place des **éléments de contrôle qualité** des résultats de l'IA ;
- de **critiquer les résultats** obtenus par ce pipeline.
Ces éléments devront être exposés dans le rapport soumis.

Exemples de pipeline possibles (au choix, non cumulatifs) :
- **multi-agents** : deux LLM font chacun la revue, et un troisième « superviseur » arbitre en cas de discordance ;
- **RAG** : extraction automatique, à partir d'un corpus d'articles, des passages ou arguments pertinents pour le débat ;
- **autres optimisations** : structuration des arguments, synthèse comparée, vérification de références…

→ **Choix du groupe : RAG + vérification de références par construction** (voir `pipeline.md`, section 0, pour la correspondance consigne → pipeline).

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

## 4. Architecture cible (v2 minimale, option B — détail dans `pipeline.md`)
```
[Corpus figé : 4 PDF (D06, D07, D09, D12) + meta.json]   (corpus.md)
      │
 WF00 Ingestion (terminé) : PDF → nettoyage → chunks → embeddings Gemini (`gemini-embedding-001`) → Qdrant (chunk_id, doc_id, versant, rôle)
      │
 10-argumentaire : Paramètres (sections à générer) → pour chaque section (Loop + Wait 15 s) :
      récupération multi-requêtes (sections.json) → rédacteur Gemini (HTTP, JSON) → garde-fous G1 G2 G4 G5 (signalement ⚠, sans correction)
   → conclusion → assemblage : Markdown + bibliographie générée par le code depuis meta.json
   → relecteur Gemini : liste de problèmes, sans correction
      │
 50-baseline (Gemini seul, sans RAG)  ──►  eval/evaluer.py : métriques pipeline vs baseline + évaluation humaine (kappa)
      │
 Pandoc → PDF (hors n8n)
```

### Stack technique pressentie
- **n8n self-hosted 2.41.4** (base SQLite) + **Qdrant 1.19.1**, définis dans `docker-compose.yml` et lancés avec **Podman** (fichier compatible Docker)
  - Démarrage : `podman machine start` puis `podman compose up -d` · n8n : http://localhost:5678 · Qdrant : http://localhost:6333/dashboard
  - Depuis n8n, Qdrant est joignable à `http://qdrant:6333`. La clé `N8N_ENCRYPTION_KEY` est dans `.env` (gitignoré, modèle dans `.env.example`) et **ne doit jamais changer**.
  - Export des workflows (à versionner) : `sh n8n/exporter.sh`. Il exporte les workflows dont le nom commence par `NN-` ou `test-` vers `n8n/workflows/<nom>.json`, **sans le bloc `shared`** (nom et e-mail du propriétaire n8n), et s'interrompt s'il reste une adresse e-mail. Ne pas utiliser `export:workflow --backup` directement : fichiers nommés par ID (doublons), tous les workflows, nom et e-mail inclus
- **Vector store** : Qdrant
- **LLM** : **API Gemini de Google** (clé créée dans Google AI Studio, plan gratuit). Remplace Mistral depuis le 2026-09-30 (voir section 5).
  - Credential n8n : **« Google Gemini(PaLM) API »**, host `https://generativelanguage.googleapis.com`. La clé est saisie **uniquement** dans ce credential, par l'utilisateur : jamais dans `.env`, un workflow exporté, un terminal ou une conversation. Claude Code ne la lit jamais.
  - Génération : nœud **HTTP Request** direct vers `generateContent` (credential Gemini de n8n, mode JSON avec schéma), modèle **`gemini-3.8-flash`** (choisi le 21/10, validé le 26/10). Quotas du plan gratuit (relevés le 26/10 sur https://ai.dev/rate-limit, détail dans `pipeline.md` § 1) : **5 RPM, 250 000 TPM, 20 RPD**, remise à zéro à minuit heure du Pacifique.
  - Embeddings : nœud *Embeddings Google Gemini*, modèle **`gemini-embedding-001`** (texte seul ; 3 072 dimensions par défaut, 768 ou 1 536 possibles ; quotas : 100 RPM, 30 000 TPM, 1 000 RPD). **La dimension de la collection Qdrant doit être exactement celle produite par le nœud.** Changer de modèle d'embeddings (ex. `gemini-embedding-2`) impose de tout réindexer : espaces vectoriels incompatibles.
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
| 2026-10-17 | PDF du corpus non versionnés (`corpus/*.pdf` dans `.gitignore`) ; `meta.json` reste versionné | Droits de diffusion et taille (PDF d'Apple : 15 Mo) |
| 2026-10-17 | Rôles de `meta.json` validés (D06 pour, D07 et D09 contexte) ; **D12 (AHA, *cuffless*) ajouté : rôle contre, versant technique** | Décision du groupe |
| 2026-10-17 | WF00 : **nettoyage avant découpage** (bibliographie, appels de référence, césures) | Au test du 30/09, 2 chunks sur 5 étaient de la bibliographie |
| 2026-10-17 | **Requêtes de recherche en anglais** (corpus en anglais), rédaction en français | Écart de langue entre requête et corpus. L'appel direct de l'API d'embeddings avec `task_type` n'est prévu que si nettoyage + anglais ne suffisent pas |
| 2026-10-17 | `docker-compose.yml` : `${QDRANT_API_KEY:?…}` | Refuser de démarrer plutôt que lancer Qdrant sans clé |
| 2026-10-17 | Étape (c) (`task_type` via HTTP Request) **non mise en œuvre** | Critère fixé avant le test rempli : aucune bibliographie, au moins 3 pertinents sur 5, D12 présent |
| 2026-10-17 | **Récupération de WF10** : 2 ou 3 requêtes anglaises fixes par section (top-k 15), requête forcée `role = contre`, fusion et dédoublonnage par `chunk_id`, plafond de 2 chunks par document, 8 à 10 chunks retenus ; pas de MMR. Requêtes dans `prompts/sections.json` (annexe du rapport) | Au test du 17/10, le top 5 venait d'un seul document. Un plafond codé est déterministe et simple à expliquer à l'oral |
| 2026-10-17 | **`chunk_id` = `<doc_id>-<8 premiers caractères du SHA-1 du texte>`**, ajouté après insertion par `set_payload` (sans appel Gemini) + index `keyword` ; même étape en fin de WF00 | Stable d'une réingestion à l'autre ; évite une réingestion |
| 2026-10-17 | Export des workflows par `n8n/exporter.sh` (sans nom ni e-mail) | `--backup` produisait des doublons et exposait le nom et l'e-mail du propriétaire |
| 2026-10-17 | Référence D12 : *Hypertension* 2026;83(3):e00254 + DOI, mise en ligne le 11/12/2025 | Confirmé par Crossref (vol. 83, n° 3, mars 2026, sans pagination) |
| 2026-10-21 | **Plan v2 « rapide »** (`pipeline.md`) : corpus figé à 4 documents (D06, D07, D09, D12) ; **juge Claude supprimé** (plus de G3) ; 2 workflows (`10-argumentaire`, `50-baseline`) + script d'évaluation ; 1 correction max par section, 1 passe d'examinateur | Délai serré (date limite probable 02/11). Fidélité contrôlée par G4 + évaluation humaine. Sections pauvres assumées et présentées comme un résultat du garde-fou |
| 2026-10-21 | **Plan v2 minimale** : pas de boucle de régénération ni de correction automatique (les garde-fous et le relecteur signalent seulement), pas d'examinateur sur la baseline ; tout ce qui est écarté est listé dans `pipeline.md` § 5 « Limites et pistes pour une v2 » | Consignes exactes reçues : un pipeline RAG + contrôle qualité + critique suffit. Le plus simple possible, vu le délai |
| 2026-10-21 | **Modèle de chat : `gemini-3.8-flash`** (nom exact, pas l'alias `gemini-flash-latest`) | Test de fumée : seul modèle récent ouvert au plan gratuit ; `gemini-3.1-pro` a un quota à 0, `gemini-2.5-pro` n'est plus proposé |
| 2026-10-21 | Rédacteur appelé par **HTTP Request** direct (`generateContent`, mode JSON avec schéma), au lieu du nœud *Google Gemini Chat Model* | Sortie JSON garantie, erreurs (429…) visibles, pas de relances cachées de LangChain |
| 2026-10-21 | `./prompts` (lecture seule) et `./outputs` montés dans n8n ; `N8N_RESTRICT_FILE_ACCESS_TO` étendu (séparateur `;`) | Prompts versionnés lus par le workflow, sorties écrites dans le dépôt |
| 2026-10-26 | Appel HTTP direct du rédacteur **validé** ; montages `prompts/` et `outputs/` validés | Voir le 21/10 |
| 2026-10-26 | **`redacteur_v1` gardé jusqu'au bout**, sauf décision contraire | Ses défauts du 21/10 servent de matière à la critique des résultats |
| 2026-10-26 | Quotas relevés (chat : 5 RPM, 250 000 TPM, 20 RPD ; embeddings : 100 RPM, 30 000 TPM, 1 000 RPD). *Wait* de 15 s entre deux appels de chat ; paramètre en tête de `10-argumentaire` listant les sections à générer ; nombre d'appels de chat dans `runs.jsonl` ; **jamais d'exécution complète sans accord** ; exécution finale officielle (sections, relecteur, baseline) un jour où le quota est entier | 11 appels de chat pour l'exécution finale, sur 20 par jour |
| 2026-10-26 | **Relecteur, option A** : un seul appel ; il reçoit l'argumentaire, la consigne, le texte des chunks cités et l'année de chaque document (`meta.json`) | Permettre au relecteur de repérer les ajouts non sourcés et les liens inventés entre sources (aucun juge de fidélité) |
| 2026-10-26 | **G5** ajouté aux garde-fous : formulations absolues interdites par la règle 7 de `redacteur_v1` (« prouve » et ses formes, « toujours », « aucun risque »), marquage ⚠ | Contrôle automatique, sans coût, d'une règle du prompt |
| 2026-10-26 | Étape 2a : conclusion **après la boucle**, sans *Wait* avant elle (la boucle attend déjà 15 s) ; délai du rédacteur de 600 s ; archivage de `10-argumentaire` = erreur de manipulation | Choix du groupe |
| 2026-10-26 | **G5 élargi** :<br>• termes ajoutés : robuste, rigoureusement, solide(s), démontré, incontestable, garanti/garantissant, certainement ;<br>• formes niées non signalées ;<br>• « certain » seulement en emploi affirmatif ;<br>• testé hors ligne | La version initiale ne repérait aucun des défauts réels. **Liste gelée le 26/10** : construite sur les sorties qu'elle évalue (surajustement), seuls ses résultats sur l'exécution finale comptent |
| 2026-10-26 | **Relance unique explicite** (429 ou 5xx → *Wait* 60 s → copie du nœud HTTP) pour les sections, la conclusion et le relecteur. Délai dépassé : pas de relance, signalement G1 (nœud en « continuer après erreur »). Tentatives dans `verif` et `runs.jsonl`. « Retry On Fail » écarté | Le moteur de n8n plafonne l'attente à 5 s, ne relance pas un 503 reçu en « ne jamais lever d'erreur », et ne trace pas les tentatives. Test du 26/10 : l'objet d'erreur de « continuer après erreur » ne contient pas la clé |
| 2026-10-26 | **Grille du relecteur** : + « affirmations non soutenues par les chunks cités », + « liens et chronologie entre sources (années des documents) » ; prompt `relecteur_v1.md` | Exploiter les entrées de l'option A |
| 2026-10-26 | **Boîte aux lettres `echanges/`** (rapport de Claude Code, consignes de la revue) ; en-tête `x-goog-api-key` non retenu ; **protocole corrigé** de comparaison avec le relecteur : liste de défauts de référence écrite par Claude, puis validée défaut par défaut par un membre du groupe avant l'appariement | La liste de Claude seule ne mesurerait que l'accord entre deux LLM |
| 2026-10-26 | Choix de la baseline (relance, mode JSON, interdiction d'inventer des références, mêmes règles que le rédacteur hors corpus) et de l'évaluation (phrase = affirmation, deux fichiers d'évaluateurs, définition de `PARTIEL`, texte des chunks dans `verif`) **validés** | Consignes de 21 h 15 |
| 2026-10-26 | **Règle d'arrêt dans le workflow** (option A) : paramètres `arret_premier_appel` (activée) et `seuil_premier_appel_s` (180) ; premier appel seulement ; ligne `statut: arrete` dans `runs.jsonl`, puis *Stop and Error* | `n8n execute` n'affiche rien avant la fin ; un arrêt doit rester visible ; une lenteur passagère plus tard ne doit pas faire perdre l'exécution finale |
| 2026-10-26 | **Échéance : pipeline prêt le 28/10 après-midi.** Essai le 27/10, exécution finale officielle le 28/10, puis gel des prompts, de G5 et des workflows | Le rapport et l'oral viennent ensuite |

## 6. Questions ouvertes / à trancher
- [x] Position : POUR
- [x] Offre Mistral : le plan Free ne permet pas d'activer de clé API → passage à l'API Gemini
- [x] Quotas du plan gratuit Gemini : relevés le 26/10 dans AI Studio et reportés dans `pipeline.md` § 1
- [ ] Le 26/10, AI Studio affichait 309 requêtes d'embeddings et un RPM saturé, alors que n8n n'a rien exécuté depuis le 21/10 (historique et journal d'événements). Hypothèse : le graphique montre le pic d'une période, celui du 30/09 (deux ingestions de 153 chunks, dont une sans lots). À vérifier : la période choisie dans le graphique. Sinon, la clé sert ailleurs et il faut la renouveler
- [x] Modèle Gemini du rédacteur, du relecteur et de la baseline : `gemini-3.8-flash` (21/10)
- [x] **RPM, RPD et TPM de `gemini-3.8-flash`** : 5 RPM, 250 000 TPM, 20 RPD (26/10)
- [x] Dimension des embeddings : **3 072**, imposée (le nœud n8n n'expose pas ce réglage) ; collection `moa_corpus` en 3 072, distance cosinus
- [x] `chunk_id` : SHA-1 du texte, ajouté aux 187 points par `set_payload` + index (17/10)
- [x] Diversité du retrieval pour WF10 : plusieurs requêtes + plafond par document (17/10, voir section 5)
- [x] Commande d'export : remplacée par `sh n8n/exporter.sh` (17/10)
- [x] Référence de D12 : 83(3):e00254, confirmé par Crossref (17/10)
- [ ] **Essai du 27/10 après 8 h, avec le feu vert d'Adam** :
  - technique + éthique + réglementaire + conclusion + relecteur, soit 5 appels de chat (10 au plus avec les relances) ; paramètres déjà réglés ;
  - règle d'arrêt : si le premier appel dépasse 3 min ou échoue malgré la relance, on arrête et on réessaie dans l'heure. Elle est appliquée automatiquement par le workflow et testée par simulation le 26/10 ;
  - ensuite, comparaison avec le relecteur selon le protocole corrigé (`pipeline.md` § 3).
  - **27/10, 9 h 05 et 9 h 13 : deux arrêts** (premier appel en 308 s, puis en 241 s ; API lente). Décision attendue : seuil, nouvel essai ou report (voir `echanges/rapport.md`)
- [ ] **Avant chaque exécution, contrôler l'horloge de la VM Podman** (écart avec l'hôte > 5 s → `podman machine ssh 'sudo chronyc makestep'`). Le 27/10, son retard de 11 h 20 après la veille du Mac a faussé `run_id` et durées
- [ ] **Exécution finale officielle le 28/10 après 8 h, avec le feu vert d'Adam** : toutes les sections, la conclusion, le relecteur et la baseline (11 appels), puis `eval/evaluer.py`, puis **gel**. Échéance : pipeline prêt le 28/10 après-midi
- [x] Grille du relecteur : 2 critères ajoutés (26/10)
- [x] Clé Gemini en en-tête `x-goog-api-key` : **non retenu** (26/10). Gain trop faible pour une clé stockée dans deux credentials ; « continuer après erreur » ne l'expose pas de toute façon (test du 26/10)
- [ ] Workflows « MOA » et « My workflow » (brouillons du 30/09) à supprimer dans l'interface n8n ?
- [ ] Requête forcée `role = contre` : 2 chunks garantis sur 10 au plus (proposition de Claude, dans `prompts/sections.json`), à valider
- [ ] Les commits contiennent l'e-mail de l'auteur (configuration git `user.email`). Passer à l'adresse *noreply* de GitHub pour les prochains commits ?
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
| 0. Cadrage | ✅ position POUR, LLM Gemini (juge Claude abandonné le 21/10), option B, plan v2 « rapide » |
| 1. Environnement local | ✅ stack opérationnelle ; test de fumée Gemini réussi le 21/10 (`gemini-3.8-flash`, workflow `test-gemini`) ; `prompts/` et `outputs/` montés |
| 2. Constitution du corpus | ✅ figé à 4 documents (D06, D07, D09, D12), plan v2 |
| 3. Ingestion (WF00) | ✅ lots de 6 pages + nettoyage (bibliographie, appels, césures) + `chunk_id` (SHA-1, index) ; 187 chunks ; retrieval validé le 17/10 (5/5 pertinents, plus de bibliographie). L'appel de l'étape `chunk_id` en fin de boucle sera vérifié à la prochaine ingestion complète |
| 4. Workflow `10-argumentaire` (rédaction + G1/G2/G4/G5 + assemblage + relecteur) | 🟡 étape 1 faite le 21/10 : section « technique » de bout en bout, 34 s, 0 paragraphe signalé. **Étape 2a (26/10)** : boucle sur les sections (*Wait* 15 s), conclusion après la boucle, paramètre des sections, G5, délai de 600 s. Essai éthique + réglementaire + conclusion : réglementaire rédigé, éthique et conclusion en 503 (API saturée, signalés par G1). **Étape 3 prête (26/10 au soir, non exécutée)** : relecteur option A, relance unique sur 429/5xx, G5 élargi ; tous les chemins testés avec un rédacteur et un relecteur simulés. Reste : exécution du 27/10 avec accord, puis comparaison avec la relecture humaine ; exécution complète seulement avec accord |
| 5. Baseline (`50-baseline`) | 🟡 prête le 26/10 (prompt `baseline_v1.md`, mode JSON, relance unique), testée avec un appel simulé ; à exécuter le 28/10 dans l'exécution finale |
| 6. Évaluation (`eval/evaluer.py` + évaluation humaine) | 🟡 script prêt le 26/10 (métriques, 15 affirmations dans `eval_humaine_juge1/2.csv`, `references_baseline.csv`, kappa vérifié à la main), testé sur les sorties du 21/10 et du 26/10. Reste : exécution sur la sortie finale, évaluation humaine (2 membres), vérification des références de la baseline |
| 7. Rapport écrit | ⚪ |
| 8. Oral | ⚪ |

## 9. Conventions de travail avec Claude
- Répondre en français, de façon directe et concrète.
- **Aucune correction silencieuse** : signaler toute erreur (de fond, de lien, de structure) et attendre l'accord avant de corriger.
- **Divergence avec la spec** (`pipeline.md`) : la signaler **et attendre l'accord** avant de la coder ; la signaler en la codant ne suffit pas (rappel du 26/10).
- **Boîte aux lettres `echanges/`** (règles dans `echanges/README.md`) : à la fin de chaque étape, écrire le rapport dans `echanges/rapport.md`, en plus de la réponse dans le terminal. Le rapport contient les résultats, les questions et les choix à valider, avec les options et une recommandation. Le fichier est remplacé à chaque fois, avec en tête la date, l'heure et le commit. `echanges/consignes.md` n'est exécuté qu'après l'accord explicite d'Adam. Aucune clé dans ces fichiers.
- **Quota Gemini** (20 appels de chat par jour) : ne jamais lancer d'exécution complète de `10-argumentaire`, ni l'exécution finale (relecteur, baseline), sans l'accord de l'utilisateur. Les essais se font sur 1 ou 2 sections.
- Ne pas signaler comme défauts les états transitoires du chantier.
- Toute affirmation factuelle intégrée au rapport doit avoir une source vérifiée (les sources sont contrôlées au hasard par les enseignants).
- Mettre à jour les sections 5, 6 et 8 à la fin de chaque session, et consigner l'étape dans `implémentation.md`.
