# Plan du rapport écrit (3 à 4 pages + annexe)
Contenu à mettre dans chaque partie imposée par la consigne. ⏳ = résultat encore attendu. ⚠ = à vérifier avant d'écrire.

## Format et en-tête
- Fichier : `Ecrit_Nom1_Nom2_NomX.pdf`, un seul envoi par groupe (rosy.tsopra@aphp.fr, benjamin.pariente@aphp.fr).
- En-tête : titre, noms du groupe, date, « Sujet 2 – pipeline technique », position défendue : **POUR**.
- Budget : 3.1 ≈ ½ page · 3.2 ≈ 1¼ page · 3.3 ≈ ¾ page · 3.4 ≈ 1 page → ≈ 3½ pages. ⚠ Demander si la bibliographie du rapport et l'annexe comptent dans les 4 pages.
- Vocabulaire : écrire « autorisation 510(k) » (*clearance*), pas « approbation » ni « validation » ; expliquer une fois que c'est une équivalence substantielle à un prédicat (Viz HCM).

## 3.1 Figure de synthèse (graphical abstract, ≈ ½ page)
- Entrée : corpus de 4 documents avec leur rôle : D06 Apple (pour), D07 FDA 510(k) K250507 (contexte réglementaire), D09 Elgendi 2019 (contexte technique), D12 AHA 2026 (contre).
- Ingestion : nettoyage → découpage (1 000 caractères, chevauchement 150) → embeddings Gemini → Qdrant (187 extraits).
- Boucle par section : recherche (plusieurs requêtes + extrait « contre » forcé + plafond par document) → rédacteur Gemini (cite des identifiants d'extraits) → garde-fous G1, G2, G4, G5 (⚠ signalé, pas corrigé).
- Conclusion → assemblage (bibliographie générée par le code) → relecteur Gemini (liste de problèmes).
- À côté : baseline (même modèle, sans corpus) → évaluation (métriques, évaluation humaine, liste de défauts).
- Codes visuels : une couleur par nature d'étape (LLM / code déterministe / humain / données) ; une frontière « local / API externe » (lien avec le RGPD) ; les points d'intervention humaine (choix du corpus, validation, évaluation).
- 3 ou 4 chiffres clés en marge : 9/9 sections, 31/31 paragraphes cités, « info non disponible » 3 contre 0, relecteur 1 défaut repéré sur 21.
- Légende de 2 lignes sous la figure.

## 3.2 Pipeline et méthodologie d'implémentation (≈ 1¼ page)
**Cadre et outils**
- Objectif : argumentaire structuré et sourcé POUR l'autorisation FDA de la notification d'hypertension de l'Apple Watch.
- Option retenue : corpus choisi par le groupe + RAG (exemple « Système RAG » de la consigne), plutôt qu'une recherche PubMed automatisée.
- Outils : n8n 2.41.4 auto-hébergé, Qdrant 1.19.1, conteneurs Podman, API Gemini (`gemini-3.8-flash` pour la rédaction, `gemini-embedding-001` pour les embeddings), script Python d'évaluation. Exécution locale, ports limités à la machine, versions figées.

**Corpus**
- 4 documents, critères de sélection : couvrir les versants imposés, sources primaires (dossier FDA, étude d'Apple), une revue technique, au moins une source « contre » de société savante.
- `meta.json` = source unique des métadonnées et de la bibliographie.
- Critères et équations de recherche manuelles → annexe.

**Ingestion**
- Extraction page par page, nettoyage avant découpage (bibliographie, appels de référence, césures). Pourquoi : au 1er test, 2 extraits sur 5 étaient de la bibliographie.
- Découpage récursif 1 000 caractères / 150 de chevauchement. Pourquoi : citations précises, contrôle des chiffres plus strict.
- Embeddings de 3 072 dimensions, distance cosinus ; identifiant stable `chunk_id` (empreinte du texte) ; 187 extraits (D06 22, D07 47, D09 59, D12 59).

**Recherche (technique d'optimisation n° 1)**
- 2 à 3 requêtes fixes en anglais par section (la langue du corpus), top 15 chacune.
- Une requête filtrée « contre » dont les 2 meilleurs extraits sont garantis.
- Fusion, dédoublonnage, **plafond de 2 extraits par document**, 10 extraits au plus.
- Pourquoi : au test du 17/10, le top 5 venait d'un seul document, et l'étude d'Apple n'apparaissait pas.

**Rédaction (technique d'optimisation n° 2 : prompt et format)**
- Un appel par section (8 sections), puis la conclusion à partir des sections.
- Prompt versionné (`redacteur_v1`) : citer un extrait pour toute affirmation factuelle, aucune connaissance extérieure, écrire « [INFORMATION NON DISPONIBLE DANS LE CORPUS] » si l'information manque, présenter puis réfuter les objections, pas de formulation absolue.
- Réponse imposée en JSON (schéma), appel HTTP direct.

**Garde-fous**
- Principal : **le LLM n'écrit jamais une référence**. Il cite des identifiants d'extraits, et le code génère la bibliographie : une référence inventée est impossible par construction.
- G1 structure (JSON, sections, échecs d'appel, caractères corrompus, texte sans accents) ; G2 chaque citation fait partie des extraits récupérés ; G4 chaque nombre figure dans un extrait cité ; G5 formulations absolues (liste de mots, formes niées exclues, insensible aux accents, liste gelée le 26/10).
- Choix : **signaler (⚠) sans corriger**, pour la simplicité et la transparence (une boucle de correction est une piste v2).

**Agent relecteur et baseline**
- Relecteur : un appel Gemini, reçoit l'argumentaire, la consigne, le texte des extraits cités et l'année de chaque document ; grille de 7 critères ; renvoie une liste de problèmes, sans réécrire.
- Baseline : même modèle, même consigne et mêmes règles (dont « n'invente aucune référence »), sans corpus.

**Robustesse et traçabilité**
- Quotas gratuits (20 appels par jour, 5 par minute) : attente de 15 s entre deux appels, budget de 18 appels par exécution, relances explicites sur erreur 429/5xx (60 s puis 120 s), règle d'arrêt sur le premier appel.
- Traçabilité : `runs.jsonl` (modèle, prompts, appels, durées), prompts et workflows versionnés dans git, **gel du pipeline** avant l'exécution finale du 28/10.

**Difficultés et solutions** (petit tableau)
- Pas de clé API gratuite chez Mistral → Gemini (argument RGPD reformulé).
- API lente (de 34 s à près de 10 min par appel) et erreurs 503 → relances, budget, règle d'arrêt, exécutions planifiées.
- « Retry On Fail » de n8n inadapté (attente plafonnée à 5 s) → relance codée explicitement.
- Bibliographie dans les extraits → nettoyage ; un document dominant la recherche → plafond + extrait « contre » forcé.
- Quota d'embeddings (100 par minute) → ingestion par lots avec attente.
- Caractères corrompus renvoyés par Gemini, texte sans accents → décodage avant les garde-fous, alertes G1.
- Délai serré → périmètre réduit (« v2 minimale ») : juge de fidélité et boucle de correction retirés, listés comme limites.

**Usage de l'IA dans la conception** (à déclarer, en 2 lignes)
- Le code et une partie de la documentation ont été produits avec un assistant IA (Claude / Claude Code) ; décisions et validations prises par le groupe.

## 3.3 Contrôle qualité, avec méthodes de la littérature citées (≈ ¾ page)
**Architecture du contrôle, à 5 niveaux**
1. Par construction : références générées par le code.
2. Automatique et déterministe : garde-fous G1, G2, G4, G5.
3. Par un LLM : agent relecteur (approche « LLM-as-a-judge »).
4. Humain : évaluation d'affirmations et validation d'une liste de défauts.
5. Comparatif : pipeline contre baseline.

**Protocoles**
- Métriques automatiques (`metriques.csv`) : sections présentes, paragraphes cités, « information non disponible », paragraphes signalés, appels et durée.
- Évaluation humaine de la fidélité : 15 affirmations tirées au hasard (graine = identifiant de l'exécution) parmi les 115 phrases de l'exécution finale, chacune jugée contre les extraits cités par son paragraphe : SOUTENU / PARTIEL (en partie, ou formulée plus fort que la source) / NON_SOUTENU. Un seul juge (pas de kappa).
- Évaluation du relecteur (exécution 1) : liste de défauts écrite par un LLM selon une typologie de 7 types, **validée à l'aveugle** par un membre du groupe avant d'ouvrir la sortie du relecteur, puis appariement.
- Évaluation de G5 : chaque alerte jugée vraie ou fausse (précision).
- Baseline : chaque référence vérifiée (existe-t-elle ? auteurs, année, revue, DOI corrects ?).

**Références à citer, en reliant chaque méthode à la vôtre** (⚠ vérifier chacune avant de la citer : contrôles au hasard)
- Lewis et al., 2020 (NeurIPS) : RAG → justification de l'architecture.
- Walters & Wilder, 2023 (*Scientific Reports*) ; Bhattacharyya et al., 2023 (*Cureus*) : références fabriquées par les LLM → justification de la bibliographie générée par le code et de la vérification des références de la baseline.
- Es et al., RAGAS (2023 ; EACL 2024) : la « fidélité » (*faithfulness*) comme critère → votre jugement SOUTENU / PARTIEL / NON_SOUTENU.
- Min et al., FActScore (EMNLP 2023) : décomposition en faits atomiques → votre évaluation par phrase en est une version simplifiée.
- Zheng et al., 2023 (NeurIPS) : LLM-as-a-judge et ses biais ; Panickssery et al., 2024 (NeurIPS) : un LLM favorise ses propres productions → justifie la prudence sur le relecteur du même modèle.
- Huang et al., 2024 (ICLR), *Large Language Models Cannot Self-Correct Reasoning Yet* → cohérent avec l'échec du relecteur.
- Manakul et al., SelfCheckGPT (EMNLP 2023) ; Dhuliawala et al., Chain-of-Verification (2023) → alternatives non mises en œuvre (pistes).
- Tam et al., 2024 (*npj Digital Medicine*), cadre QUEST d'évaluation humaine des LLM en santé → justifie l'évaluation humaine.
- Cohen, 1960 : kappa → prévu mais non réalisé (un seul juge).

## 3.4 Critique des résultats (≈ 1 page)
**Ce qui fonctionne**
- Exécution finale : **9 sections sur 9**, **31/31 paragraphes cités**, références exactes par construction, aucune référence inventée possible.
- **Honnêteté sur l'ignorance** : 3 « information non disponible » (HIPAA, CE/MDR, RGPD) ; la baseline n'en écrit **aucune**, malgré la même règle.
- Contre-arguments présents dans chaque section, grâce à l'extrait « contre » forcé.
- Garde-fous déterministes utiles sur la forme : G4 a repéré les caractères corrompus ; G5 : **6 vraies alertes sur 8**.
- Robustesse : exécution finale sans section vide malgré l'API instable ; traçabilité complète.

**Ce qui échoue**
- **Fidélité fine** : évaluation humaine **5 SOUTENU, 10 PARTIEL, 0 NON_SOUTENU** sur 15 → un tiers seulement pleinement fidèle. Défaut typique : **formulation plus forte que la source**, avec exemples (« partially expressed » → « reflète » ; « could improve » → « démontre » ; un futur conditionnel de l'AHA → un présent ; la réserve « however, major limitations… » omise).
- **Exécution 1** : **17 défauts de fond confirmés sur 30** proposés (sur-affirmations, affirmations non soutenues par l'extrait cité, liens inventés entre sources), tous invisibles pour les garde-fous → « tout est vert ≠ tout est juste ».
- **Liens inventés entre sources** : exemple A25 (« les critiques de l'AHA ne s'appliquent pas aux données de cette notification »), aucun extrait ne l'établit.
- **Relecteur** : **1 défaut repéré sur 21**, **0 sur 17** défauts de fond (exécution 1) ; délai dépassé sur l'exécution finale. Hypothèses : même famille de modèle que le rédacteur (biais d'auto-préférence), entrée en partie corrompue, prompt très long.
- G5 : liste de mots, fausses alertes (négation, vocabulaire du 510(k)), rappel non mesuré, liste construite sur les sorties qu'elle évalue (surajustement).
- ⚠ Exemple possible, à vérifier dans les extraits cités : la conclusion affirme « aucune différence selon l'âge », alors que le tableau de la FDA donne une sensibilité significativement plus basse avant 60 ans (rapport 0,69 [0,55 ; 0,85]).
- ⏳ Baseline : X références inexistantes ou inexactes sur 22.
- Coût : 11 appels et 59 min pour le pipeline, contre 1 appel et 5 min pour la baseline.

**Limites d'utilisation en pratique**
- Corpus de 4 documents : revue non exhaustive, biais de sélection, sections pauvres, source intéressée (livre blanc d'Apple) pour des chiffres épidémiologiques.
- LLM non déterministe, une seule exécution officielle.
- Dépendance à une API gratuite (quotas, latence, erreurs), modèle Flash seulement.
- RGPD : envoi du texte à une API hors UE, acceptable pour des publications, pas pour des données patients.
- **L'outil reste une aide à la rédaction** : chaque affirmation doit être relue par un humain compétent ; le contrôle par une IA du même modèle ne suffit pas.
- Limites de l'évaluation : un seul juge, sans kappa ; validation volontairement indulgente ; liste de défauts écrite par une IA ; **harmonisation a posteriori sur proposition d'une IA, qui a rapproché les jugements humains de ceux de l'IA** (accord sur G5 passé de 3/8 à 6/8) ; petits échantillons.

**Pistes d'amélioration (v2)**
- Recherche PubMed automatisée + tri par deux LLM + diagramme PRISMA ; corpus complet (~20 documents).
- Juge de fidélité d'une autre famille de modèle ; relecteur d'un autre fournisseur ; boucle de correction bornée.
- Citations par phrase ; plusieurs exécutions ; évaluation par deux cliniciens avec kappa.

**Regard du groupe sur la conclusion de l'IA** ⏳
- L'IA conclut POUR avec assurance : le groupe est-il d'accord, au vu d'une sensibilité de 41 % et des réserves de l'AHA ?

## 3.5 Annexe
- **Obligatoire** : l'argumentaire de l'exécution finale (`20261028-095239`), dans l'ordre de la consigne : contexte et problématique clinique ; enjeux de l'autorisation FDA ; versants technique/scientifique, éthique, social/économique, réglementaire, parcours de soins, autres ; conclusion avec parti pris. Garder les marques ⚠ et le préciser en tête, signaler les 3 « information non disponible », joindre la bibliographie générée.
- Utile, si la place le permet :
  - tableau du corpus (références, rôle, critères de sélection, équations de recherche manuelles) ;
  - prompts (`redacteur_v1`, `relecteur_v1`, `baseline_v1`, requêtes de `sections.json`) ;
  - tableau des métriques pipeline contre baseline ;
  - les 15 affirmations avec leur jugement ;
  - synthèse de la liste de défauts et de l'appariement avec le relecteur ;
  - les 8 alertes G5 jugées ;
  - références de la baseline vérifiées ;
  - captures des workflows n8n ;
  - déclaration d'usage de l'IA.

## À régler avant de rédiger
- ⏳ Vérifier les 22 références de la baseline.
- ⚠ Vérifier les références de la littérature citées en 3.3.
- ⚠ Vérifier l'exemple « âge » (extraits cités par la conclusion § 3).
- ⚠ Ne pas utiliser l'exemple QXO/SFR sans avoir vérifié la page 8 du PDF D07.
- Confirmer : date limite, et si l'annexe et la bibliographie comptent dans les 4 pages.
