# recap.md — Dossier complet pour le rendu du projet MOA (Sujet 2)
Document de passation pour le groupe. Il contient **tout ce qu'il faut savoir pour rédiger le rapport, préparer l'oral et envoyer le rendu**, sans avoir suivi le développement.
État au **29/10/2026** : pipeline terminé et gelé ; restent quelques vérifications, le rapport écrit et l'oral.

**Légende** : ✅ fait · ⏳ à faire par le groupe · ⚠ point de vigilance (erreur à éviter ou fait à vérifier).

---

## Sommaire
0. L'essentiel en 15 lignes
1. La consigne (ce qui est exigé)
2. Où trouver quoi dans le dossier
3. Le projet expliqué simplement
4. Le pipeline en détail (paramètres compris)
5. Chronologie et décisions
6. Difficultés rencontrées et solutions
7. Le contrôle qualité (protocoles + littérature à citer)
8. Tous les résultats chiffrés
9. Les exemples concrets à montrer (vérifiés)
10. Les limites
11. Les pistes d'amélioration (v2)
12. Plan détaillé du rapport écrit (3 à 4 pages + annexe)
13. Plan détaillé de l'oral (10 min) et questions probables
14. Ce qui reste à faire : liste de tâches avec mode d'emploi
15. Pièges à éviter
16. Glossaire
17. Annexe technique : relancer le pipeline (à ne faire qu'en cas de besoin)

---

## 0. L'essentiel en 15 lignes
- **Sujet 2 (technique)**, position **POUR** l'autorisation par la FDA de la notification d'hypertension de l'Apple Watch.
- On a construit un **pipeline RAG orchestré en local avec n8n** : 4 documents → 187 extraits dans une base vectorielle (Qdrant) → pour chacune des 9 sections imposées, recherche des extraits pertinents → rédaction par un LLM (Gemini) qui **cite obligatoirement les extraits** → **garde-fous automatiques** → **agent relecteur** → comparaison avec une **baseline** (le même LLM sans corpus).
- Garde-fou principal : **le LLM n'écrit jamais une référence**, c'est le code qui génère la bibliographie → **référence inventée impossible**.
- **Exécution finale officielle** : `20261028-095239` (28/10). 9/9 sections, 31/31 paragraphes cités, 59 min, 11 appels.
- **3 résultats clés** :
  1. Sans corpus, le LLM n'avoue jamais qu'il ne sait pas : « information non disponible » **3 fois** pour le pipeline, **0** pour la baseline (pourtant même règle dans son prompt).
  2. « Tout est vert ≠ tout est juste » : évaluation humaine de 15 affirmations → **5 SOUTENU, 10 PARTIEL, 0 NON_SOUTENU** ; défaut typique = **formulation plus forte que la source**. Sur une exécution précédente, **17 défauts de fond** confirmés, invisibles pour les garde-fous.
  3. L'IA qui relit l'IA ne voit presque rien : relecteur **1 défaut repéré sur 21**, **0 sur 17** défauts de fond.
- ⏳ **Reste à faire** : vérifier les 22 références de la baseline (≈ 1 h), vérifier les références de littérature citées dans le rapport, figure de synthèse, captures n8n, rapport écrit, slides, répétition, envoi.
- ⚠ **Date limite** : le PDF dit **« avant le 02/11/2025 »** pour un projet 26/27 → très probablement **02/11/2026 (lundi)**. **À confirmer avec l'enseignant.**

---

## 1. La consigne (ce qui est exigé)
### 1.1 Rendu
- **Deux PDF**, **un seul envoi par groupe**, à **rosy.tsopra@aphp.fr** et **benjamin.pariente@aphp.fr** :
  - `Ecrit_Nom1_Nom2_NomX.pdf` (rapport écrit) ;
  - `Oral_Nom1_Nom2_NomX.pdf` (support de la présentation).
- Échéance : « avant le 02/11/2025 » dans le PDF (⚠ voir § 0), « selon les modalités énoncées en cours ».
- Rapport : **3 à 4 pages** (indication donnée au groupe ; ⚠ demander si l'annexe et la bibliographie comptent).
- Le non-respect des consignes et l'absence en cours font perdre des points. Le projet devait être **validé par l'enseignant** (⚠ vérifier que c'est fait).

### 1.2 Oral
- **10 min de présentation + 10 min de questions**, sur le projet **et/ou sur les cours**.
- Date fixée par l'administration. **Absence = non-validation du module.**
- La qualité de l'oral et de l'écrit compte dans la note.

### 1.3 Ce que demande le Sujet 2
- Principe : un pipeline IA qui rédige l'argumentaire (pour ou contre), **avec la structure complète attendue et les références**.
- Objectifs : utiliser des **techniques d'optimisation** de l'IA et **évaluer leur efficacité** ; garder un **esprit critique** ; comprendre les **limites d'utilisation en pratique**.
- À faire : (1) un pipeline **de la revue de la littérature jusqu'au rapport structuré** ; (2) des **éléments de contrôle qualité** ; (3) une **critique des résultats**.
- Exemples cités par la consigne : multi-agents (2 LLM + superviseur) ; **système RAG** (notre choix) ; autres optimisations (structuration, synthèse, **vérification de références**).
- Objectifs pédagogiques communs : exposer un problème clinique ; objet connecté de santé ; évaluation d'un dispositif (valeur clinique, réglementaire, équité, éthique, données) ; lecture critique ; **usage raisonné et critique de l'IA générative** ; recherche documentaire, travail d'équipe, oral.
- ⚠ Les enseignants **vérifient au hasard que les sources soutiennent ce qu'on avance** : chaque référence citée doit avoir été vérifiée.

### 1.4 Structure imposée du rapport
- **3.1 Figure de synthèse** du pipeline (style *graphical abstract*), qui ouvre le rapport.
- **3.2 Description du pipeline et de la méthodologie** : techniques d'optimisation, garde-fous, difficultés et solutions.
- **3.3 Description du contrôle qualité**, appuyée sur des **méthodes de la littérature (sources citées)**.
- **3.4 Critique des résultats** : ce qui fonctionne, ce qui échoue, limites d'utilisation en pratique.
- **3.5 Annexe** : l'**argumentaire généré par l'IA**, avec la structure : contexte et problématique clinique ; enjeux de l'autorisation FDA ; arguments par versants (technique/scientifique, éthique, social/économique, réglementaire, parcours de soins, autres) ; conclusion avec parti pris clair. Tout autre élément utile peut être ajouté.

---

## 2. Où trouver quoi dans le dossier `MOA/`
| Fichier / dossier | Contenu | Utile pour |
|---|---|---|
| `Projet_MOA_2627_v4_vf.pdf` | La consigne officielle | Tout |
| **`recap.md`** (ce fichier) | Dossier complet de passation | Tout |
| `plan_rapport.md` | Plan du rapport écrit, partie par partie | Rapport |
| `presentation.md` | Texte de l'oral prêt à dire + dossier complet | Oral |
| `oral.md` | Support de préparation de l'oral | Oral |
| `point_28-10.md` | Point d'étape du 28/10 et temps de travail restant | Organisation |
| `pipeline.md` | Spécification technique ; **§ 5 = toutes les limites** | Rapport 3.2, 3.4 |
| `CLAUDE.md` | Mémoire du projet : décisions datées, état | Rapport 3.2 |
| `implémentation.md` | Journal détaillé des étapes, difficultés, solutions | Rapport 3.2 |
| `tech.md` | Explications : RAG, chunks, embeddings, Qdrant, PubMed | Oral (questions) |
| `corpus.md` | Corpus identifié (20 docs) + **critères de sélection** | Rapport 3.2, annexe |
| `corpus/meta.json` | Métadonnées des 4 documents (source de la bibliographie) | Annexe |
| `corpus/*.pdf` | Les 4 PDF (non versionnés dans git) | Vérifications |
| `prompts/redacteur_v1.md`, `relecteur_v1.md`, `baseline_v1.md`, `sections.json` | Les prompts et requêtes de recherche | Annexe |
| `n8n/workflows/*.json` | Workflows exportés (`00-ingestion`, `10-argumentaire`, `50-baseline`) | Captures, reproductibilité |
| `eval/evaluer.py` | Script de métriques et d'évaluation humaine | Rapport 3.3 |
| **`outputs/argumentaire_20261028-095239.md`** | **Argumentaire officiel (annexe obligatoire)** | Annexe |
| `outputs/verif_20261028-095239.json` | Détail des garde-fous de l'exécution finale | Rapport 3.4 |
| `outputs/relecture_20261028-095239.json` | Relecteur de l'exécution finale (échec : délai) | Rapport 3.4 |
| **`outputs/baseline_20261027-102233.md`** | **Baseline officielle** (22 références à vérifier) | Rapport 3.4 |
| `outputs/metriques.csv` | Tableau pipeline contre baseline | Rapport 3.4 |
| `outputs/eval_humaine_juge1.csv` | Les 15 affirmations jugées (avec commentaires) | Rapport 3.3, 3.4, annexe |
| `outputs/g5_jugements_20261028-095239.md` | Les 8 alertes G5 jugées | Rapport 3.4 |
| `outputs/references_baseline.csv` | ⏳ **À remplir** : vérification des 22 références | Rapport 3.4 |
| `outputs/defauts_reference_20261027-093507.md` | Liste des défauts de l'exécution 1, validation, appariement avec le relecteur | Rapport 3.3, 3.4 |
| `outputs/argumentaire_20261027-093507.md` + `relecture_…` | Exécution 1 (non officielle) | Rapport 3.4 |
| `outputs/runs.jsonl` | Journal machine de chaque exécution (modèle, appels, tokens, durées) | Rapport 3.2 |
| `echanges/` | Échanges entre Claude Code et Claude (rapports, consignes) | Historique |

---

## 3. Le projet expliqué simplement
**Le problème clinique.** L'HTA est l'un des principaux facteurs de risque cardiovasculaire modifiables, très sous-diagnostiquée (environ la moitié des hypertendus l'ignorent, d'après le livre blanc d'Apple). Mesure de référence : cabinet, automesure, MAPA sur 24 h. En septembre 2025, la FDA a autorisé (510(k)) une fonction de l'Apple Watch qui **analyse passivement le signal optique (PPG) pendant 30 jours** et **notifie** l'utilisateur s'il présente des signes évocateurs d'HTA. Elle **ne mesure pas la pression** et **ne pose pas de diagnostic**.

**Ce qu'on devait faire.** Un pipeline d'IA qui écrit un argumentaire structuré et sourcé (nous : POUR), avec contrôle qualité et critique des résultats.

**Ce qu'on a fait.** Plutôt que de laisser le LLM écrire de mémoire (risque d'hallucinations et de fausses références), on l'oblige à écrire **à partir d'un corpus choisi** (RAG) et à **citer l'extrait** derrière chaque affirmation. Puis on contrôle :
- automatiquement (structure, citations, chiffres, mots trop forts) ;
- par un second LLM (relecteur) ;
- par un humain (évaluation de 15 affirmations tirées au hasard) ;
- par comparaison avec le même LLM sans corpus (baseline).

**Ce qu'on a appris.** Le RAG supprime les références inventées et rend le LLM honnête sur ce qu'il ignore. Mais il ne garantit pas la fidélité fine : le LLM **durcit** les sources, **généralise**, **invente des liens** entre documents. Les contrôles automatiques ne le voient pas, et un LLM relecteur du même modèle non plus. **Seule la relecture humaine le voit.**

---

## 4. Le pipeline en détail
### 4.1 Outils et environnement
- **n8n 2.41.4** auto-hébergé (orchestration visuelle, base SQLite) + **Qdrant 1.19.1** (base vectorielle), lancés avec **Podman** (fichier `docker-compose.yml`) sur un MacBook M3.
- Ports ouverts **sur la machine locale uniquement** (127.0.0.1), télémétrie de n8n coupée, clé API sur Qdrant, clés uniquement dans les *credentials* n8n (jamais dans le code).
- **LLM** : API **Gemini** de Google, offre gratuite. Rédaction, relecture, baseline : **`gemini-3.8-flash`**. Embeddings : **`gemini-embedding-001`** (3 072 dimensions).
- Évaluation : script Python `eval/evaluer.py` (bibliothèque standard seulement).
- Code et documentation produits **avec l'aide d'un assistant IA** (Claude / Claude Code) ; décisions et validations prises par le groupe (⚠ à déclarer dans le rapport).

### 4.2 Corpus (4 documents, figé)
| Id | Document | Rôle | Extraits |
|---|---|---|---|
| D06 | Apple Inc. *Hypertension Notification Feature on Apple Watch* [validation paper]. Septembre 2025 | pour | 22 |
| D07 | FDA. 510(k) **K250507**, *Hypertension Notification Feature (HTNF)*, Apple Inc. Lettre d'équivalence substantielle du 11/09/2025 (correction administrative du 12/09/2025) + 510(k) Summary. 21 CFR 870.2380 | contexte (réglementaire) | 47 |
| D09 | Elgendi M et al. *The use of photoplethysmography for assessing hypertension.* npj Digit Med. 2019;2:60. doi:10.1038/s41746-019-0136-7 | contexte (technique) | 59 |
| D12 | Cohen JB et al. *Cuffless devices for the measurement of blood pressure: a scientific statement from the American Heart Association.* Hypertension. 2026;83(3):e00254. doi:10.1161/HYP.0000000000000254 (mis en ligne le **11/12/2025**) | contre | 59 |
- **Critères de sélection** (`corpus.md`) : couvrir les versants imposés ; priorité aux sources primaires (documents réglementaires, étude de validation, déclarations de sociétés savantes) ; présence de sources contradictoires ; texte intégral accessible.
- 20 documents avaient été identifiés (`corpus.md` : NCD-RisC Lancet 2021, OMS 2023, ESH 2023, HAS, ESH cuffless 2022/2023, Apple Heart Study NEJM 2019, MDR, RGPD, HIPAA…) ; le corpus a été **réduit à 4 le 21/10** faute de temps (limite).
- Les métadonnées (`meta.json`) sont la **source unique de la bibliographie**.

### 4.3 Ingestion (`00-ingestion`)
- Lecture des PDF **page par page** → **nettoyage avant découpage** :
  - bibliographie coupée (en gardant les tableaux placés après les références dans le manuscrit PMC de D12) ;
  - appels de référence supprimés ; césures recollées seulement si le mot existe ailleurs.
- Découpage **récursif, 1 000 caractères, chevauchement 150**, page par page (un extrait ne chevauche jamais deux pages).
- Embeddings `gemini-embedding-001` (3 072 dimensions, distance cosinus), par **lots de 6 pages + 60 s d'attente** (quota de 100 embeddings/min).
- Identifiant stable par extrait : `chunk_id = <doc_id>-<8 premiers caractères du SHA-1 du texte>` (ex. `D12-4794f2ff`).
- Résultat : **187 extraits** dans la collection `moa_corpus`.

### 4.4 Recherche des extraits (dans `10-argumentaire`) — optimisation n° 1
- Pour chaque section : **2 à 3 requêtes fixes en anglais** (langue du corpus ; fichier `prompts/sections.json`), **top 15** par requête.
- **1 requête filtrée `role = contre`** : ses **2 meilleurs extraits sont garantis** (forcer la discussion des objections).
- Fusion, **dédoublonnage** par `chunk_id`, **plafond de 2 extraits par document**, **10 extraits au plus** ; pas de MMR (un plafond codé est déterministe et plus simple à expliquer).
- Pourquoi : au test du 30/09, 2 extraits sur 5 étaient de la bibliographie et 1 seul était pertinent ; au test du 17/10, le top 5 venait d'un seul document (D12) et l'étude d'Apple n'apparaissait pas. Après corrections : 5/5 pertinents.
- ⚠ Attribution honnête : le gain de 1/5 à 5/5 vient surtout de **l'ajout de D12**, pas du nettoyage ni de la langue des requêtes.

### 4.5 Rédaction — optimisation n° 2 (prompt + format)
- **Un appel par section** pour les 8 sections, puis **la conclusion après la boucle**, à partir des sections déjà rédigées (sans nouvelle recherche).
- Prompt versionné **`redacteur_v1.md`**, 8 règles :
  1. uniquement les extraits fournis, aucune connaissance extérieure ;
  2. chaque affirmation factuelle justifiée par au moins un `chunk_id` ;
  3. pas d'identifiant dans le texte ;
  4. chiffres repris exactement ;
  5. `[INFORMATION NON DISPONIBLE DANS LE CORPUS]` si un point n'est pas couvert ;
  6. défendre la position, mais **présenter puis réfuter** les objections « contre » ;
  7. **pas de formulation absolue** (« prouve », « toujours », « aucun risque ») ni de causalité non démontrée ;
  8. 3 à 6 paragraphes de 60 à 150 mots.
- Réponse **imposée en JSON avec schéma** (`responseMimeType` + `responseSchema`), appel **HTTP direct** à l'API (pas le nœud LangChain), pour une sortie garantie et des erreurs visibles.

### 4.6 Garde-fous (un nœud Code, sans coût) — signalent ⚠, ne corrigent pas
| Garde-fou | Ce qu'il vérifie |
|---|---|
| **Références par construction** | Le LLM ne cite que des `chunk_id` ; l'assemblage les remplace par [n, p. X] et **génère la bibliographie depuis `meta.json`** |
| **G1 Structure** | JSON valide, champs présents, au moins un paragraphe ; échecs d'appel ; caractères NUL restants ; section en français **sans aucun accent** |
| **G2 Citations** | Chaque `chunk_id` cité fait partie des extraits récupérés ; paragraphe sans citation = alerte |
| **G4 Chiffres** | Chaque nombre ou pourcentage du paragraphe figure dans un extrait qu'il cite |
| **G5 Formulations absolues** | Liste de mots (prouve, toujours, aucun risque, robuste, rigoureusement, solide(s), démontré, incontestable, garanti/garantissant, certain/certainement), formes niées exclues, comparaison **sans accents** ; **liste gelée le 26/10** |
- Avant les garde-fous : **décodage** des caractères corrompus renvoyés par Gemini (`\u0000e9` → « é »).
- Choix assumé : **signaler sans corriger** (simplicité, transparence ; la boucle de correction est une piste v2).
- ⚠ Il n'y a **pas de G3** : le juge de fidélité (Claude Haiku) prévu au départ a été retiré le 21/10 (délai).

### 4.7 Agent relecteur
- **Un seul appel** Gemini (`relecteur_v1.md`). Il reçoit : l'argumentaire, la consigne, **le texte des extraits cités** et **l'année de chaque document** (« option A »).
- Grille de 7 critères : structure ; contre-arguments non traités ; sur-affirmations ; affirmations non soutenues par les extraits cités ; **liens et chronologie entre sources** ; équilibre ; conclusion.
- Il renvoie une **liste de problèmes** (section, gravité haute/moyenne/basse, problème), **sans réécrire**.

### 4.8 Baseline (`50-baseline`)
- **Un seul appel**, même modèle, même consigne et même structure, position POUR, **sans corpus** (`baseline_v1.md`).
- Mêmes règles que le rédacteur hors corpus, dont : citer ses sources, **« n'en invente aucune »**, `[INFORMATION NON DISPONIBLE]` si pas d'information fiable.
- Baseline officielle : **`20261027-102233`** (27/10) : 9/9 sections, **22 références**.

### 4.9 Robustesse, quotas, traçabilité
- Quotas de l'offre gratuite (relevés le 26/10) : chat **5 requêtes/min, 250 000 tokens/min, 20 requêtes/jour** ; embeddings 100/min, 1 000/jour. Remise à zéro à minuit heure du Pacifique.
- *Wait* de 15 s entre deux appels ; **budget de 18 appels de chat** par exécution.
- **Relances explicites** sur erreur 429/5xx : 2 au plus (60 s, puis 120 s) ; pas de relance après un délai dépassé (600 s ; 1 200 s pour la baseline).
- **Règle d'arrêt** : si le premier appel échoue après relance ou dépasse 420 s, l'exécution s'arrête et l'écrit dans `runs.jsonl`.
- Traçabilité : `runs.jsonl` (modèle, versions de prompts, appels, tentatives, tokens, durées) ; prompts et workflows versionnés dans git ; **gel du pipeline le 27/10** (commit `8bde9d6`) avant l'exécution finale.
- Chaque appel consomme environ 2 000 à 2 800 tokens d'entrée, 700 à 1 000 de sortie, et **2 500 à 3 700 tokens de « réflexion »** du modèle (ce qui explique en partie la lenteur).

---

## 5. Chronologie et décisions
| Date | Étape | À retenir |
|---|---|---|
| 30/09 | Cadrage | Sujet 2, position POUR, **option B** (corpus choisi + RAG, pas de recherche PubMed automatisée) |
| 30/09 | Environnement | n8n + Qdrant sous Podman, local, clés protégées |
| 30/09 | LLM | **Mistral abandonné** (offre gratuite sans clé API) → **Gemini** ; argument RGPD reformulé |
| 30/09 | 1re ingestion + test de recherche | 1/5 extrait pertinent, 2/5 de bibliographie ; quota de 100 embeddings/min ; LangChain renvoie des vecteurs vides **sans erreur** (bloqué par Qdrant) |
| 17/10 | Corpus et recherche | Ajout de D12 (AHA), nettoyage avant découpage, requêtes en anglais, `chunk_id`, stratégie multi-requêtes + plafond + « contre » forcé → 187 extraits, 5/5 pertinents |
| 21/10 | **Plan v2 minimale** | Corpus figé à 4 docs, juge de fidélité (G3) retiré, pas de boucle de correction ; tout est listé en limites |
| 21/10 | 1re section rédigée (technique) | 0 alerte, mais 4 distorsions à la relecture (relecture de Claude, non validée par le groupe) |
| 26/10 | Quotas, G5, relecteur option A, relances, baseline, script d'évaluation | Protocole corrigé : liste de défauts écrite par une IA **validée par un humain avant** de voir le relecteur |
| 27/10 | Exécution 1 (non officielle) + baseline officielle | 2 sections vides (503), caractères corrompus, conclusion sans accents ; liste de 36 défauts validée ; relecteur comparé |
| 27/10 | Correctifs puis **gel** | Décodage, alertes G1, G5 sans accents, 2 relances + budget |
| 28/10 | **Exécution finale officielle** `20261028-095239` | 9/9 sections ; relecteur en échec (délai) ; métriques |
| 28/10 | Évaluation humaine, alertes G5, harmonisation | 1 seul juge, pas de kappa ; harmonisation a posteriori tracée |
| 28/10 | **Implémentation arrêtée** | Tout ce qui n'est pas fait = limites |

---

## 6. Difficultés rencontrées et solutions
| Difficulté | Solution |
|---|---|
| Pas de clé API dans l'offre gratuite de Mistral | Passage à Gemini (Google AI Studio) |
| Quota de 20 appels de chat par jour | Essais sur 1–2 sections (paramètre), budget d'appels, aucune exécution complète sans accord, exécution finale planifiée |
| API très lente (34 s par appel le 21/10 → 2 à 10 min les 27–28/10) et erreurs 503 | Délais longs, relances explicites, règle d'arrêt, exécutions le matin |
| « Retry On Fail » de n8n inadapté (attente plafonnée à 5 s, pas de relance si le nœud ne lève pas d'erreur) | Relance codée explicitement dans le workflow, visible sur le schéma |
| *Wait* > 65 s met l'exécution en pause en base (casse le lancement en ligne de commande) | 120 s obtenues par 2 × 60 s |
| Bibliographie dans les extraits | Nettoyage avant découpage |
| Tableaux de D12 placés après les références (manuscrit PMC) | Coupe arrêtée au premier « Table »/« Figure » |
| Recherche dominée par un document | Plafond de 2 par document + extrait « contre » forcé |
| Quota d'embeddings 100/min ; échecs silencieux (vecteurs vides) | Lots + attente ; validation par Qdrant |
| Caractères corrompus renvoyés par Gemini (`\u0000e9`), conclusion sans accents | Décodage avant les garde-fous, alerte G1, G5 insensible aux accents |
| Horloge de la machine virtuelle figée pendant la veille du Mac (jusqu'à 13 h 26 de retard) | Contrôle et resynchronisation (redémarrage de chronyd) avant chaque exécution |
| G5 construit sur les sorties qu'il évalue (surajustement) | Liste gelée le 26/10, évaluée seulement sur l'exécution finale |
| Liste de défauts écrite par une IA | Validation humaine à l'aveugle avant l'appariement |
| Délai serré | Périmètre réduit (« v2 minimale »), simplifications listées en limites |

---

## 7. Le contrôle qualité
### 7.1 Architecture à 5 niveaux
1. **Par construction** : bibliographie générée par le code.
2. **Automatique, déterministe** : G1, G2, G4, G5.
3. **Par un LLM** : agent relecteur (« LLM-as-a-judge »).
4. **Humain** : évaluation de 15 affirmations ; validation d'une liste de défauts ; jugement des alertes G5 ; ⏳ vérification des références de la baseline.
5. **Comparatif** : pipeline contre baseline.

### 7.2 Protocoles
- **Métriques automatiques** (`metriques.csv`) : sections présentes ; paragraphes cités ; « information non disponible » ; paragraphes ⚠ ; problèmes du relecteur ; appels, durée.
- **Évaluation humaine de la fidélité** (exécution finale) :
  - 15 affirmations (phrases de 6 mots ou plus) **tirées au hasard** parmi les 115 phrases citées (graine = `run_id`, tirage reproductible) ;
  - chacune jugée **contre les extraits cités par son paragraphe** : `SOUTENU` (les extraits le disent) / `PARTIEL` (en partie, ou **formulé plus fort que la source**) / `NON_SOUTENU` (absent ou contredit) ;
  - **un seul juge** (Adam), donc **pas de kappa** (décision du 28/10).
- **Évaluation du relecteur** (exécution 1, `20261027-093507`) :
  1. liste de défauts écrite par Claude **sans ouvrir la sortie du relecteur** (typologie : 1 structure, 2 contre-argument non traité, 3 sur-affirmation, 4 non soutenu par les extraits cités, 5 lien/chronologie inventés, 6 équilibre, 7 conclusion) ;
  2. **validation de chaque ligne par un membre du groupe, à l'aveugle** ;
  3. appariement : un défaut confirmé est « repéré » si le relecteur cite le même passage avec un problème de même nature.
- **Évaluation de G5** : chaque alerte de l'exécution finale jugée vraie ou fausse (précision).
- ⏳ **Baseline** : chaque référence vérifiée (existe ? auteurs, année, revue, DOI corrects ?).

### 7.3 Littérature à citer (⚠ vérifier chaque référence avant de la citer)
| Référence | À quoi elle sert dans le rapport |
|---|---|
| Lewis P, Perez E, Piktus A, et al. *Retrieval-augmented generation for knowledge-intensive NLP tasks.* NeurIPS 2020 | Justifier le RAG |
| Walters WH, Wilder EI. *Fabrication and errors in the bibliographic citations generated by ChatGPT.* Sci Rep. 2023 | Les LLM inventent des références → bibliographie générée par le code, vérification de la baseline |
| Bhattacharyya M, et al. *High rates of fabricated and inaccurate references in ChatGPT-generated medical content.* Cureus. 2023 | Idem, en médecine |
| Es S, James J, Espinosa-Anke L, Schockaert S. *RAGAS: Automated evaluation of retrieval augmented generation.* EACL 2024 (demo) ; arXiv 2023 | Notion de **fidélité** (*faithfulness*) → nos jugements SOUTENU/PARTIEL/NON_SOUTENU |
| Min S, Krishna K, Lyu X, et al. *FActScore: Fine-grained atomic evaluation of factual precision in long form text generation.* EMNLP 2023 | Évaluation par faits atomiques → notre évaluation par phrase en est une version simplifiée |
| Zheng L, Chiang WL, Sheng Y, et al. *Judging LLM-as-a-judge with MT-Bench and Chatbot Arena.* NeurIPS 2023 | LLM comme évaluateur et ses biais → le relecteur |
| Panickssery A, Bowman SR, Feng S. *LLM evaluators recognize and favor their own generations.* NeurIPS 2024 | Biais d'auto-préférence → relecteur du même modèle |
| Huang J, Chen X, Mishra S, et al. *Large language models cannot self-correct reasoning yet.* ICLR 2024 | Cohérent avec l'échec du relecteur |
| Manakul P, Liusie A, Gales MJF. *SelfCheckGPT.* EMNLP 2023 ; Dhuliawala S, et al. *Chain-of-Verification reduces hallucination in LLMs.* Findings ACL 2024 | Méthodes alternatives non mises en œuvre (pistes) |
| Tam TYC, et al. *A framework for human evaluation of large language models in healthcare derived from literature review* (QUEST). npj Digit Med. 2024 | Justifier l'évaluation humaine en santé |
| Cohen J. *A coefficient of agreement for nominal scales.* Educ Psychol Meas. 1960 | Kappa (prévu, non réalisé) |

---

## 8. Tous les résultats chiffrés
### 8.1 Exécution finale officielle `20261028-095239` (28/10) contre baseline `20261027-102233` (27/10)
| Métrique | Pipeline | Baseline |
|---|---|---|
| Sections imposées | **9 / 9** | 9 / 9 |
| Références | 4 documents, **exactes par construction** | 22 écrites par le LLM, ⏳ à vérifier |
| Paragraphes avec au moins une citation | **31 / 31** | 27 / 27 |
| `[INFORMATION NON DISPONIBLE]` | **3 / 34** (HIPAA, CE/MDR, RGPD) | **0 / 27** (même règle dans son prompt) |
| Paragraphes signalés ⚠ | 8 / 34 (G5 : 8, G4 : 1 ; G1, G2 : 0) | sans objet |
| Relecteur | **échec** (délai de 600 s dépassé) | sans objet |
| Appels de chat, durée | 11 (1 relance), 59 min | 1, 5 min |
| Taille | ≈ 4 200 mots | ≈ 2 500 mots |
- Lancement 9 h 52 (et non 8 h : horloge de la VM à resynchroniser). Durée des appels : de 91 s à 586 s par section ; « social/économique » : un 503 puis une relance réussie.
- Aucune section vide, aucun caractère corrompu.

### 8.2 Évaluation humaine (exécution finale, 15 affirmations, 1 juge)
- **5 SOUTENU (33 %), 10 PARTIEL (67 %), 0 NON_SOUTENU.** (Avant harmonisation : 4 / 8 / 3.)
- Par section : contexte 1 S / 1 P ; technique 2 S / 0 P ; éthique 0 / 1 ; social-économique 0 / 2 ; parcours de soins 0 / 2 ; autres 2 / 2 ; conclusion 0 / 2. Aucune affirmation tirée dans « enjeux FDA » ni « réglementaire ».
| N° | Section | Jugement | Pourquoi (résumé) |
|---|---|---|---|
| 1 | contexte | PARTIEL | « prépondérante », « enjeu majeur de santé publique » plus forts que « major source », « critical risk factor » |
| 2 | contexte | SOUTENU | Quasi littéral (D12 : confort, suivi passif continu, accessibilité) |
| 3 | technique | SOUTENU | Paramètres PPG exacts (nuance « partially » jugée acceptable, comme A5) |
| 4 | technique | SOUTENU | Chiffres et IC identiques (41,2 % ; 53,7 %) |
| 5 | éthique | PARTIEL | Fidèle à Apple (« on par »), mais le tableau FDA (RR 1,42 [0,86-2,35]) montre « non significatif », pas « équivalent » |
| 6 | social-éco | PARTIEL | Futur de l'AHA (« will allow ») passé au présent, réserve « major limitations… » omise |
| 7 | social-éco | PARTIEL | Pas de commentaire du juge (piste : « large diffusion » est une affirmation d'Apple sur elle-même, sans chiffre) ⏳ à expliciter |
| 8 | parcours | PARTIEL | 1re moitié soutenue mais renforcée ; 2de moitié absente des extraits cités |
| 9 | parcours | PARTIEL | Pas de commentaire du juge (piste : « critères d'évaluation cliniques » pour « clinical outcomes ») ⏳ à expliciter |
| 10 | autres | PARTIEL | Même cas que 1 |
| 11 | autres | SOUTENU | Recommandation AHA/ACC 2025 fidèle (« fiabilité » omise) |
| 12 | autres | PARTIEL | « promising » retenu, « yet challenging » et les réserves omis |
| 13 | autres | SOUTENU | Architecture montre/iPhone, conditionnel respecté |
| 14 | conclusion | PARTIEL | Pas de commentaire du juge (piste : « au moins 30 jours » pour « just 30 days », « pronostic » pour « longevity ») ⏳ à expliciter |
| 15 | conclusion | PARTIEL | Raisons de la déclaration scientifique AHA attribuées aux recommandations 2025 |
- Détail et commentaires : `outputs/eval_humaine_juge1.csv`. ⏳ Les affirmations 7, 9 et 14 n'ont pas de commentaire : le juge doit ajouter une ligne de justification (le jury peut demander pourquoi).

### 8.3 Alertes G5 (exécution finale)
- **6 vraies alertes sur 8** (5 sur 8 avant harmonisation). Les 2 fausses : une négation non détectée (« n'a pas encore été corrélé à des résultats cliniques **démontrés** ») et le vocabulaire réglementaire du 510(k) (« a **démontré** son équivalence substantielle »). Rappel (sur-affirmations sans mot de la liste) non mesuré.
- Détail : `outputs/g5_jugements_20261028-095239.md`.

### 8.4 Exécution 1 `20261027-093507` (27/10, non officielle) : liste de défauts et relecteur
- 47 min, 14 appels (4 relances) ; 2 sections vides (503), 91 caractères corrompus, conclusion sans accents.
- **Liste de défauts** : 30 de fond proposés par Claude → **17 confirmés** par le groupe (A1, A3, A6, A7, A10, A11, A14, A15, A16, A20, A21, A22, A23, A24, A25, A29, A30), dont **8 de gravité haute** (A1, A3, A7, A14, A21, A22, A25, A29) ; 4 de forme sur 4 (B1–B4) ; C1, C2 (code QXO) rejetés (⚠ voir § 9.5).
  - Par type (confirmés) : 8 sur-affirmations, 6 non soutenus par les extraits cités, 2 liens inventés entre sources, 1 contre-argument non traité.
  - Avant harmonisation : 15 confirmés (A7 et A21 étaient rejetés).
- **Relecteur** : 3 problèmes signalés → **1 défaut confirmé repéré sur 21** (B1, sections vides), **0 sur 17 défauts de fond**. Son seul problème de fond porte sur A9 (lien AHA 2026 → étude Apple 2025), que le validateur avait rejeté à l'aveugle ; tri a posteriori : **fausse alerte** (position finale d'Adam). (Avant harmonisation : 1 sur 19.)
- Garde-fous sur l'exécution 1 : G5 signalait 5 paragraphes (tous avec un défaut de la liste) + 1 fausse alerte ; il ne voyait pas « demontre » (sans accent) ; G4 n'a vu que la corruption des caractères.

### 8.5 Essais antérieurs
- 21/10 (section technique seule) : 0 alerte des garde-fous, mais 4 distorsions repérées par Claude (une étude présentée comme générale, réserve « only three subjects » omise, « suivi sur le long terme » pour 30 jours, lien inventé AHA → Apple). ⚠ Non validé par le groupe.
- 26/10 (réglementaire) : même lien inventé AHA → FDA ; « proscrit » durcit « ne prévoit pas ».

---

## 9. Les exemples concrets à montrer (vérifiés)
1. **Le LLM seul ne dit jamais « je ne sais pas »** : pipeline 3 « information non disponible » (HIPAA, CE/MDR, RGPD absents du corpus) ; baseline 0, et elle produit quand même des paragraphes et 22 références sur ces points.
2. **Durcissement de la source** : « can be **partially** expressed » (Elgendi) → « **reflète** » ; « **could** improve » (Apple) → « **démontre** son potentiel » ; « **will allow** […] However, major limitations must be addressed » (AHA) → « ces outils **contribuent** à surmonter » (réserve supprimée) ; une sensibilité de 41 % → « **garantit** un ciblage pertinent ».
3. **Lien inventé entre sources** (A25, confirmé à l'aveugle) : « les critiques […] ne s'appliquent pas aux données probantes fournies pour cette notification » : aucun extrait ne l'établit ; l'AHA vise explicitement les appareils autorisés par la FDA (« despite FDA clearance »). Variante A3 : arguments du livre blanc d'Apple attribués à la FDA.
4. **⚠ Contradiction avec la source, causée par le découpage** (exécution finale, conclusion § 3) — *vérifié par Claude dans les PDF, à confirmer par le groupe* :
   - Le texte affirme : « les analyses en sous-groupes ne montrent **aucune différence** cliniquement significative selon **l'âge**, le sexe, la race ou le phototype ».
   - Apple (p. 9) et la FDA (510(k) Summary, p. 8–9) disent : « **Lower sensitivity** and higher specificity were observed in those with **younger age (<60)** and lower BMI (<30). Importantly, comparisons of **sex, race, and skin tone** suggested no clinically meaningful difference ». Tableau FDA : âge < 60 vs ≥ 60, rapport de sensibilité **0,69 [0,55 ; 0,85]** (significatif).
   - Cause : l'extrait cité (D06-fd4b1853) **commence au milieu de la phrase** (« …tone suggested no clinically meaningful difference ») ; la phrase sur l'âge est dans l'extrait précédent, non récupéré. Le LLM a généralisé à l'âge. **Exemple parfait des limites du découpage.**
5. **⚠ Code produit QXO / SFR** — *vérifié par Claude dans le PDF D07, à confirmer par le groupe* :
   - Le pipeline écrit « code produit **QXO** » pour la fonction d'Apple (exécution 1 et exécution finale, réglementaire § 1 ; conclusion de l'exécution 1).
   - D07 : lettre du 11/09/2025 (p. 2) : *Product Code: QXO* ; **correction administrative du 12/09/2025** (p. 1) : *Product Code: SFR*, « FDA has created a new product code to better categorize your device ». Tableau du 510(k) Summary (p. 8) : **HTNF = SFR**, **Viz HCM (prédicat) = QXO**.
   - Donc « QXO » est **le code du prédicat et de la lettre initiale**, pas le code actuel de la fonction. Cause probable : l'extraction du tableau PDF a mélangé les colonnes (l'extrait contient les deux codes dans le désordre).
   - ⚠ C1 et C2 (ce défaut, dans la liste de l'exécution 1) avaient été **rejetés** à la validation. Au vu de cette vérification, le groupe peut décider de les reconsidérer (tracé comme une décision a posteriori), ou présenter l'exemple seulement comme une erreur repérée après coup.
6. **Erreur de citation sans erreur de fait** (G4, exécution finale, réglementaire § 1) : « 510(k) » et « 21 CFR 870.2380 » sont exacts mais absents de l'extrait cité → G4 a raison de signaler.
7. **L'IA qui relit l'IA** : 1 sur 21, 0 sur 17 de fond, malgré l'accès aux extraits et aux années des documents.
8. **Un problème d'infrastructure** : Gemini renvoie « \u0000e9 » au lieu de « é » ; G4 y voyait des nombres ; corrigé par un décodage.
9. **La conclusion de l'IA** : « l'autorisation de la FDA apparaît **pleinement fondée** et bénéfique » — parti pris clair (exigé), mais très affirmatif vu une sensibilité de 41 % (⏳ avis du groupe).
10. **VPP et prévalence** (utile en questions) : la FDA indique une VPP de **70,9 %** pour une prévalence de **31,4 %** (celle de l'étude). Dans une population où la prévalence de l'HTA non diagnostiquée est plus basse, la VPP baisse fortement (ex. calcul : prévalence 10 % → VPP ≈ 37 % avec Se 41,2 % et Sp 92,3 %) : plus de fausses alertes en vie réelle.

---

## 10. Les limites (à reprendre en 3.4 ; détail : `pipeline.md` § 5)
**Corpus et recherche**
- 4 documents seulement, choisis à la main : revue non exhaustive, biais de sélection ; sections éthique, socio-économique et réglementaire pauvres ; un seul document « contre ».
- Le pipeline ne va pas « de la revue de la littérature » au sens d'une recherche automatisée (exigence de la consigne remplie seulement par une revue ciblée manuelle).
- Corpus figé dans une version donnée ; source intéressée (livre blanc d'Apple) pour des chiffres épidémiologiques (pas d'OMS ni de NCD-RisC dans le corpus).
- Découpage fixe : une phrase coupée change de sens (exemple de l'âge) ; extraction de tableaux PDF peu fiable (exemple QXO/SFR).
- `task_type` des embeddings non utilisé, pas de reranking.

**Contrôle qualité**
- Pas de juge de fidélité indépendant (G3 retiré).
- Relecteur de la même famille de modèle que le rédacteur ; un seul appel sur tout l'argumentaire (~15 000 tokens) → délai dépassé sur l'exécution finale.
- G5 = liste de mots : contexte ignoré, fausses alertes, rappel non mesuré, **liste construite sur les sorties qu'elle évalue** (surajustement).
- Les défauts sont signalés, pas corrigés.
- Une phrase est jugée par rapport aux extraits de **son paragraphe** (citations par paragraphe) : surestime la fidélité.

**Évaluation**
- Une seule exécution officielle (LLM non déterministe, variabilité non mesurée).
- Évaluation humaine sur 15 affirmations, **un seul juge, pas de kappa**.
- Liste de défauts de référence écrite par une IA, validée par **un seul membre**, avec un **jugement volontairement indulgent** (borne basse).
- **Jugements humains harmonisés a posteriori sur proposition d'une IA** (règles fixées à l'avance, valeurs initiales tracées) : les 5 changements proposés vont tous dans le sens des propositions initiales de Claude Code (accord sur G5 passé de 3/8 à 6/8 ; A7 et A21) → **indépendance du jugement réduite**.
- ⏳ Références de la baseline encore à vérifier.

**Modèle et infrastructure**
- Offre gratuite : 20 appels/jour, latence très variable, erreurs 503 ; modèle Flash seulement (Pro fermé à l'offre gratuite).
- API américaine : le texte du corpus (publications, **aucune donnée patient**) part chez Google ; pour les utilisateurs de l'EEE, les conditions de l'offre payante s'appliquent aussi au quota gratuit (pas d'utilisation des requêtes pour améliorer les modèles — Gemini API Additional Terms, ⚠ à citer/vérifier). Inacceptable tel quel pour des données de santé.

---

## 11. Les pistes d'amélioration (v2)
- Recherche PubMed / Europe PMC automatisée + tri des résumés par deux LLM + arbitre (exemple « multi-agents » de la consigne) + **diagramme PRISMA**.
- Corpus complet (~20 documents de `corpus.md`), versions corrigées des documents, version dans les métadonnées.
- Juge de fidélité d'une **autre famille de modèle** ; relecteur d'un autre fournisseur ; relecture section par section.
- Boucle de correction bornée (2 itérations) avec comparaison avant/après.
- Citations **par phrase** ; décomposition en faits atomiques (FActScore) ; métriques RAGAS.
- Plusieurs exécutions (3 à 5) pour mesurer la stabilité.
- Évaluation par **deux cliniciens** avec kappa, grille écrite à l'avance.
- Modèle local (Ollama) ou fournisseur européen sous contrat pour des données sensibles ; modèle Pro (offre payante).
- Découpage respectant les phrases et les tableaux (extraction de tableaux dédiée).

---

## 12. Plan détaillé du rapport écrit (3 à 4 pages + annexe)
*Version complète : `plan_rapport.md`.*

**En-tête** : titre, noms, date, « Sujet 2 », position POUR. Vocabulaire : « autorisation 510(k) » (*clearance*), pas « approbation » ni « validation » (expliquer une fois : équivalence substantielle à un prédicat, Viz HCM, réglementation 21 CFR 870.2380).

**3.1 Figure de synthèse (≈ ½ page)**
- Corpus (4 docs + rôles) → ingestion (nettoyage, 1 000/150, embeddings, Qdrant 187) → boucle par section (recherche multi-requêtes + « contre » forcé + plafond → rédacteur Gemini JSON → garde-fous G1 G2 G4 G5 ⚠) → conclusion → assemblage (bibliographie par le code) → relecteur ; baseline en parallèle ; évaluation (métriques, humain, liste de défauts).
- Codes visuels : couleur par nature (LLM / code / humain / données), frontière « local / API externe », points d'intervention humaine, 3–4 chiffres clés.
- Outils : draw.io, Figma, PowerPoint ou Keynote (Claude peut aussi produire un premier jet en SVG).

**3.2 Pipeline et méthodologie (≈ 1¼ page)** — reprendre §§ 4 et 6 de ce document :
- cadre et outils ; corpus et critères ; ingestion (avec la justification par le test du 30/09) ;
- **optimisation 1** : la recherche (avec la justification par le test du 17/10) ;
- **optimisation 2** : prompt à règles + JSON imposé + extrait « contre » forcé ;
- garde-fous (le principal : bibliographie par le code) ; relecteur ; baseline ;
- robustesse et traçabilité (quotas, relances, règle d'arrêt, gel) ;
- tableau « difficultés → solutions » (5–7 lignes) ;
- déclaration de l'usage d'un assistant IA pour le code.

**3.3 Contrôle qualité (≈ ¾ page)** — reprendre § 7 : les 5 niveaux, les protocoles, et les références de littérature (chacune reliée à une méthode du projet). ⚠ Vérifier chaque référence.

**3.4 Critique des résultats (≈ 1 page)** — reprendre §§ 8, 9, 10 :
- ce qui fonctionne (9/9, 31/31, 0 référence inventée possible, 3 contre 0, contre-arguments présents, G4/G5 utiles, robustesse) ;
- ce qui échoue (5/10/0 ; 17 défauts de fond ; liens inventés ; contradiction « âge » ; QXO/SFR ; relecteur 1/21 ; limites de G5 ; ⏳ références de la baseline) ;
- limites d'utilisation (aide à la rédaction, pas un auteur ; relecture humaine experte indispensable ; RGPD ; coût en temps) ;
- limites de notre propre évaluation (1 juge, indulgence, harmonisation par une IA) ;
- pistes v2 en 3 lignes ;
- l'avis du groupe sur la conclusion de l'IA (⏳).

**3.5 Annexe**
- **Obligatoire** : `outputs/argumentaire_20261028-095239.md` en entier, dans l'ordre de la consigne (nos 9 sections y correspondent exactement : contexte ; enjeux FDA ; technique ; éthique ; social/économique ; réglementaire ; parcours de soins ; autres ; conclusion). Expliquer en tête : les marques ⚠ = paragraphes signalés par les garde-fous ; les renvois [n, p. X] = document n, page X ; 3 « information non disponible » ; bibliographie générée par le code.
- Utile si place : tableau du corpus + critères ; prompts (`redacteur_v1`, `relecteur_v1`, `baseline_v1`, requêtes de `sections.json`) ; métriques ; les 15 affirmations jugées ; synthèse des défauts et de l'appariement ; alertes G5 ; références de la baseline vérifiées ; captures n8n ; déclaration d'usage de l'IA.

**Conseils de rédaction**
- Chaque choix = **un problème observé → une décision → un effet mesuré**.
- Donner **les chiffres finaux** (après harmonisation) et mentionner une fois les chiffres initiaux.
- Ne présenter comme « validé » que ce qui a été validé par le groupe ; sinon écrire « observé par Claude, non validé ».
- Conversion : écrire en Markdown ou dans un traitement de texte ; PDF via Pandoc (`pandoc rapport.md -o Ecrit_….pdf`) ou export direct.

---

## 13. Plan détaillé de l'oral (10 min) et questions probables
*Texte complet prêt à dire : `presentation.md` § 1 ; support : `oral.md`.*
| Temps | Slide | Contenu |
|---|---|---|
| 0:00–1:00 | 1 | Titre ; problématique en une phrase : « Un LLM peut-il écrire un argumentaire médical sourcé et fiable ? » ; position POUR |
| 1:00–2:00 | 2 | Contexte : HTA sous-diagnostiquée ; la fonction Apple (PPG, 30 jours, notification, ne mesure pas la PA) ; autorisation 510(k) de sept. 2025 ; réserves de l'AHA |
| 2:00–3:30 | 3 | **Graphical abstract** du pipeline |
| 3:30–5:00 | 4–5 | Choix techniques : RAG, Qdrant, recherche (multi-requêtes, « contre » forcé, plafond), prompt à règles, JSON ; capture n8n ; difficultés (Mistral → Gemini, quotas, 503) |
| 5:00–6:30 | 6 | Garde-fous + relecteur ; **un exemple concret** (âge ou durcissement de la source) |
| 6:30–8:00 | 7 | Résultats : tableau pipeline/baseline ; 3 contre 0 ; 5/10/0 ; relecteur 1/21 |
| 8:00–9:00 | 8 | Ce que l'IA conclut (« pleinement fondée ») et ce que le groupe en pense |
| 9:00–10:00 | 9 | Limites et leçons pour un usage raisonné de l'IA : l'IA aide, l'humain vérifie |

**Questions probables sur le projet** (réponses détaillées : `presentation.md` § 11)
- Pourquoi un RAG ? → traçabilité, références impossibles à inventer ; la baseline montre le LLM seul.
- Pourquoi Qdrant ? → persistance, filtre par métadonnées, local, intégré à n8n (pas un choix de performance : 187 extraits).
- Pourquoi 1 000 caractères ? → citations précises, contrôle des chiffres strict ; non optimisé (limite) ; l'exemple « âge » montre le revers.
- Pourquoi signaler sans corriger ? → transparence, simplicité ; correction = v2.
- Pourquoi le relecteur échoue ? → même modèle (auto-préférence), entrée corrompue, prompt long ; Huang et al. 2024.
- Vos défauts de référence sont-ils fiables ? → écrits par une IA, validés à l'aveugle par un humain ; indulgence et harmonisation déclarées.
- Pourquoi pas de kappa ? → un seul juge faute de temps ; script prêt.
- RGPD avec une API américaine ? → aucune donnée patient ; conditions EEE ; en clinique : modèle local ou fournisseur européen.
- Pourquoi avoir changé de fournisseur ? → contrainte d'accès.
- Reproductibilité ? → versions figées, prompts et workflows versionnés, `runs.jsonl` ; mais LLM non déterministe et une seule exécution.
- Le pipeline « va-t-il de la revue de la littérature » ? → revue ciblée manuelle (option B) ; la recherche automatisée est une piste v2 (limite assumée).

**Questions probables sur les cours** (à réviser)
- **Objet connecté / dispositif médical** : différence bien-être / DM ; logiciel DM (SaMD).
- **Réglementaire US** : 510(k) (équivalence substantielle à un prédicat) / De Novo (nouveau type, risque faible à modéré, sans prédicat) / PMA (classe III) ; classes I–III ; OTC vs prescription ; PCCP (plan de modifications prédéterminé, section 3308 de la FDORA 2022). HIPAA : couvre les *covered entities* (soignants, assureurs) et leurs sous-traitants, en général **pas** une app grand public.
- **Réglementaire UE** : règlement (UE) 2017/745 (MDR), classes I, IIa, IIb, III, marquage CE par organisme notifié, règle 11 pour les logiciels ; RGPD : données de santé = catégorie particulière (art. 9), consentement, minimisation, DPIA. (⚠ statut CE de la fonction Apple non vérifié, absent du corpus.)
- **Évaluation diagnostique** : Se, Sp, VPP, VPN ; **VPP dépend de la prévalence** (cf. § 9, point 10) ; faux positifs → anxiété, consultations inutiles ; faux négatifs → fausse réassurance (« l'absence de notification n'exclut pas une HTA »).
- **Mesure de la PA** : cabinet, automesure, MAPA 24 h (référence) ; seuils (AHA 2017 : ≥ 130/80 ; ESH : ≥ 140/90 au cabinet).
- **PPG / cuffless** : PPG = variations de **volume** sanguin (pas de pression) ; estimation de la PA par forme d'onde, PTT, ML ; calibration (brassard ou démographique), dérive ; validation : ISO 81060-2 (dispositifs à brassard), IEEE 1708, protocoles ESH cuffless ; biais selon la couleur de peau.
- **Équité et éthique** : biais du PPG, fracture numérique (coût de la montre), surdiagnostic, autonomie, bienfaisance/non-malfaisance.
- **IA générative** : hallucinations, références inventées, RAG, embeddings, prompt engineering (rôle, règles, format, exemples), température, tokens, fenêtre de contexte, agents et multi-agents, LLM-as-a-judge et ses biais, évaluation humaine.

---

## 14. Ce qui reste à faire : liste de tâches avec mode d'emploi
| # | Tâche | Qui | Temps | Mode d'emploi |
|---|---|---|---|---|
| 1 | **Confirmer la date limite** et le format (pages, annexe) | 1 membre | 5 min | Mail aux enseignants |
| 2 | **Vérifier les 22 références de la baseline** | 1–2 membres | 1 h – 1 h 30 | Voir 14.1 ; remplir `outputs/references_baseline.csv` |
| 3 | Vérifier les références de littérature du § 7.3 | 1 membre | 30–45 min | Google Scholar / éditeur : auteurs, titre, revue, année |
| 4 | Confirmer les exemples « âge » et « QXO/SFR » (§ 9.4, 9.5) ; décider pour C1/C2 | 1 membre | 15 min | PDF Apple p. 9 ; PDF D07 p. 1, 2, 8, 13 |
| 5 | Captures d'écran des workflows (`00-ingestion`, `10-argumentaire`, `50-baseline`) | 1 membre | 15 min | Ouvrir n8n (http://localhost:5678) sur le Mac d'Adam ; ou importer les JSON de `n8n/workflows/` dans un n8n |
| 6 | **Figure de synthèse** | 1 membre | 1 h – 1 h 30 | § 12, 3.1 |
| 7 | **Rapport écrit** 3.2 à 3.4 | 2 membres | 5–7 h | § 12 + `plan_rapport.md` |
| 8 | Annexe (argumentaire + éléments utiles) | 1 membre | 1 h | Copier `argumentaire_20261028-095239.md`, mise en forme |
| 9 | Avis du groupe sur la conclusion de l'IA | tous | 15 min | § 9, point 9 |
| 10 | Relecture croisée + PDF `Ecrit_…` | 1 membre | 1 h | Vérifier chiffres finaux, vocabulaire (§ 15) |
| 11 | **Slides** + PDF `Oral_…` | 1–2 membres | 2 h 30 – 3 h | § 13 |
| 12 | Préparer questions (projet + cours) | tous | 1 h 30 – 2 h | § 13 |
| 13 | Répétition chronométrée | tous | 1 h | 10 min pile |
| 14 | Remplir les noms (CLAUDE.md, noms de fichiers) et **envoyer** (un seul envoi) | 1 membre | 10 min | § 1.1 |
**Total ≈ 16 à 20 h**, soit 5 à 7 h par personne à trois.

### 14.1 Vérification des références de la baseline (tâche 2)
Pour chaque ligne de `outputs/references_baseline.csv` (séparateur `;`) :
1. Ouvrir le DOI (`https://doi.org/<DOI>`) ou chercher le titre exact dans PubMed / Google Scholar.
2. Colonne **`existe`** : `OUI` si un document avec ce titre (ou presque) existe ; `NON` sinon.
3. Colonne **`correcte`** : `OUI` si auteurs, titre, revue, année (et DOI) sont justes ; `PARTIEL` si le document existe mais avec une erreur (mauvais titre, mauvaise revue, mauvais DOI, mauvaise année…) ; `NON` s'il n'existe pas.
4. **`commentaire`** : l'écart constaté (ex. « titre réel : … », « DOI renvoie à un autre article »).
5. Ne pas juger le contenu des paragraphes, seulement la référence.
6. Résultat à rapporter : « X références inventées et Y inexactes sur 22 ».

Les 22 références (DOI à cliquer) :
1. NCD-RisC, Lancet 2021 — 10.1016/S0140-6736(21)01330-1
2. Whelton PK et al., guideline 2017 ACC/AHA, JACC 2018 — 10.1016/j.jacc.2017.11.006
3. Stergiou GS et al., ESH 2021 mesure de la PA, J Hypertens 2021 — 10.1097/HJH.0000000000002843
4. Ding EY, Marcus GM, McManus DD, Nat Rev Cardiol 2020 — 10.1038/s41569-020-0402-9
5. FDA, *Policy for Device Software Functions and Mobile Medical Applications*, 2022 — URL fda.gov
6. Shuren J, Patel B, Gottlieb S, JAMA 2018;320(4):337-338 — 10.1001/jama.2018.8832
7. Kario K, *Management of Hypertension in the Digital Health Era*, Circulation 2020 — 10.1161/CIRCULATIONAHA.120.048744
8. Allen J, *Photoplethysmography and its application…*, Physiol Meas 2007 — 10.1088/0967-3334/28/3/R01
9. Elgendi M et al., npj Digit Med 2019 — 10.1038/s41746-019-0136-7
10. IEEE Std 1708-2014 — 10.1109/IEEESTD.2014.6909892
11. Stergiou GS et al., AAMI/ESH/ISO, Hypertension 2018 — 10.1161/HYPERTENSIONAHA.117.10237
12. Mancia G et al., ESH 2023, J Hypertens 2023 — 10.1097/HJH.0000000000003480
13. Vayena E et al., Perspect Biol Med 2018 — 10.1353/pbm.2018.0031
14. Beauchamp TL, Childress JF, *Principles of Biomedical Ethics*, 8e éd., OUP 2019 (livre)
15. Topol EJ, Nat Med 2019 — 10.1038/s41591-018-0300-7
16. Gaziano TA et al., Health Affairs 2010 — 10.1377/hlthaff.2010.0988
17. Moran AE et al., NEJM 2015 — 10.1056/NEJMsa1406751
18. IMDRF, *SaMD: Clinical Evaluation*, 2017 — imdrf.org
19. Règlement (UE) 2017/745 (MDR), JO L 117
20. Cohen IG, Mello MM, *HIPAA and Protecting Health Information in the 21st Century*, JAMA 2018 — 10.1001/jama.2018.5630
21. Règlement (UE) 2016/679 (RGPD), JO L 119
22. Perez MV et al., Apple Heart Study, NEJM 2019 — 10.1056/NEJMoa1901183

---

## 15. Pièges à éviter
- ⚠ **Vocabulaire** : « autorisation 510(k) » et non « approbation » ou « validation » ; « notification » et non « mesure » ou « diagnostic ».
- ⚠ **Chiffres** : utiliser les chiffres **après harmonisation** (17 défauts, 1/21, 5/10/0, G5 6/8) et le dire une fois.
- ⚠ **A9** : position finale = **fausse alerte** (le lien AHA → Apple d'A9 a été rejeté à l'aveugle). Exemple de lien inventé à utiliser : **A25** (confirmé à l'aveugle).
- ⚠ Ne pas dire « défaut systématique dans toutes les sorties » comme un résultat validé : c'est une **observation de Claude, non validée** (validés : A3, A25).
- ⚠ Exemples « âge » et « QXO/SFR » : vérifiés par Claude dans les PDF → **à confirmer par un membre** avant de les présenter comme établis.
- ⚠ Distinguer **exécution 1** (27/10, liste de défauts, relecteur) et **exécution finale** (28/10, évaluation humaine, G5, métriques).
- ⚠ Ne citer **aucune référence non vérifiée** (contrôles aléatoires).
- ⚠ D12 : publication 2026 (vol. 83), **mise en ligne le 11/12/2025** — postérieure à l'autorisation (11/09/2025).
- ⚠ Ne plus parler de Mistral ni de Claude Haiku comme éléments du pipeline final (abandonnés).
- ⚠ Déclarer l'usage d'un assistant IA pour le développement (objectif pédagogique « usage raisonné de l'IA »).
- ⚠ Ne pas relancer le pipeline (gelé ; quota ; les résultats officiels sont ceux du 28/10).

---

## 16. Glossaire
- **RAG** : génération augmentée par la recherche ; le LLM rédige à partir de passages récupérés dans un corpus.
- **Extrait / chunk** : morceau de document (ici 1 000 caractères) ; **chevauchement** : texte commun entre deux extraits voisins.
- **Embedding** : vecteur de nombres qui représente le sens d'un texte ; proximité mesurée par la similarité cosinus.
- **Qdrant** : base de données vectorielle ; chaque extrait = vecteur + texte + métadonnées.
- **n8n** : outil d'automatisation par workflows visuels (nœuds reliés).
- **Garde-fou** : contrôle automatique d'une sortie du LLM.
- **Baseline** : référence de comparaison (ici le LLM seul, sans corpus).
- **LLM-as-a-judge** : utiliser un LLM pour évaluer la sortie d'un LLM.
- **Fidélité** (*faithfulness*) : la sortie dit-elle ce que disent ses sources ?
- **Kappa de Cohen** : accord entre deux évaluateurs corrigé du hasard.
- **510(k)** : autorisation FDA par équivalence substantielle à un dispositif déjà autorisé (prédicat).
- **PCCP** : plan de contrôle des modifications prédéterminé, autorisé par la FDA, qui encadre les mises à jour d'un algorithme.
- **PPG** : photopléthysmographie, mesure optique des variations de volume sanguin.
- **Cuffless** : mesure (ou estimation) de la PA sans brassard.
- **HTNF** : *Hypertension Notification Feature*, la fonction d'Apple.

---

## 17. Annexe technique : relancer le pipeline (seulement si nécessaire)
⚠ Le pipeline est **gelé** et les résultats officiels sont ceux du 28/10. Ne relancer que pour une démonstration ou des captures.
- Prérequis : le Mac d'Adam (ou une machine avec Podman/Docker), le dépôt, un `.env` créé depuis `.env.example` (`N8N_ENCRYPTION_KEY`, `QDRANT_API_KEY`), les credentials n8n (Gemini, Qdrant), les 4 PDF dans `corpus/`.
- Démarrage : `podman machine start` puis `podman compose up -d` → n8n sur http://localhost:5678, Qdrant sur http://localhost:6333/dashboard.
- Avant toute exécution : vérifier l'horloge de la VM (resynchroniser si besoin, procédure dans `CLAUDE.md`).
- Un appel de chat = 1 sur 20 du quota journalier ; une exécution complète ≈ 11 appels et ≈ 1 h.
