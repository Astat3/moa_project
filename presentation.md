# presentation.md — Tout ce qu'on a fait, et tout ce qu'on peut en dire
Projet MOA IA 26/27 · Sujet 2 · Pipeline IA d'aide à l'argumentation sur l'autorisation FDA de la notification d'hypertension de l'Apple Watch.
Version du 28/10/2026, après l'exécution finale. ⏳ = en attente du groupe.

**Mode d'emploi**
- La **partie 1** est un texte à dire, prêt à l'emploi (≈ 5 min ; pour l'oral final de 10 min, développer avec les parties suivantes).
- Les **parties 2 à 13** contiennent tout le reste : ce qui a été fait, pourquoi, les chiffres, les exemples, les limites et les réponses aux questions probables.
- Sources du détail : `pipeline.md` (spécification et § 5 des limites), `CLAUDE.md` (décisions datées), `implémentation.md` (journal), `tech.md` (notions), `outputs/` (résultats).

---

## 1. Le texte à dire (≈ 5 min)

**Le sujet.** « On devait construire un pipeline d'IA qui va de la littérature jusqu'à un argumentaire structuré et sourcé, pour ou contre l'autorisation par la FDA de la fonction de notification d'hypertension de l'Apple Watch, avec des garde-fous, un agent de relecture et un contrôle qualité. Nous avons pris la position **pour**. »

**Ce qu'on a construit.** « Notre pipeline tourne en local, orchestré avec n8n. Il part d'un corpus de quatre documents choisis par le groupe : le livre blanc d'Apple sur l'étude de validation, le dossier 510(k) de la FDA, une revue d'Elgendi sur la photopléthysmographie, et la déclaration scientifique de l'AHA de 2026 sur les tensiomètres sans brassard, qui est notre source "contre". Ces documents sont découpés en 187 extraits, vectorisés avec Gemini et stockés dans une base vectorielle, Qdrant. Pour chacune des neuf sections imposées, le pipeline va chercher les extraits pertinents, dont au moins deux extraits "contre" pour forcer la discussion des objections. Le LLM rédige la section en citant obligatoirement les identifiants des extraits. »

**Le garde-fou principal.** « Le LLM n'écrit jamais une référence bibliographique. Il cite des identifiants d'extraits, et c'est le code qui génère la bibliographie à partir d'un fichier de métadonnées. Une référence inventée est donc impossible par construction. »

**Les autres contrôles.** « Ensuite, quatre garde-fous automatiques vérifient la structure, que chaque citation correspond bien à un extrait récupéré, que chaque chiffre figure dans l'extrait cité, et l'absence de formulations absolues comme "prouvé" ou "garanti". Ils signalent les défauts sans les corriger, pour qu'ils restent visibles. Un agent relecteur reçoit l'argumentaire et les sources, et produit une liste de problèmes. Enfin, on compare le pipeline à une baseline : le même modèle, avec les mêmes règles, mais sans corpus. »

**Les résultats.** « L'exécution finale, ce matin, a produit les neuf sections sur neuf, avec 31 paragraphes qui citent tous au moins un extrait. Trois résultats nous paraissent importants.
- Premièrement : sans corpus, le LLM n'avoue jamais qu'il ne sait pas. Notre pipeline écrit trois fois "information non disponible dans le corpus", pour HIPAA, le marquage CE et le RGPD. La baseline ne le fait jamais, alors que la même règle figure dans son prompt : elle remplit.
- Deuxièmement : "tout est vert" ne veut pas dire "tout est juste". Nos garde-fous contrôlent la forme. Sur une exécution précédente, une relecture validée par un membre du groupe a confirmé dix-sept défauts de fond qu'aucun garde-fou ne voyait : des sur-affirmations, des affirmations non soutenues par l'extrait cité, et des liens inventés entre sources. Et sur l'exécution finale, sur quinze phrases tirées au hasard, notre juge n'en trouve que cinq entièrement soutenues par leurs extraits : les dix autres ne le sont qu'en partie, ou sont formulées plus fort que la source.
- Troisièmement : l'IA qui relit l'IA ne voit presque rien. Notre relecteur, du même modèle que le rédacteur, n'a repéré qu'un défaut sur vingt et un, et aucun des dix-sept défauts de fond, alors qu'il avait les sources sous les yeux. »

**Un exemple.** « Le cas le plus parlant : dans sa conclusion, le rédacteur affirme que les critiques de l'AHA sur les tensiomètres sans brassard "ne s'appliquent pas" aux données d'Apple. Aucun extrait ne dit cela : c'est un lien inventé entre deux sources. Ce type de lien entre l'AHA et Apple ou la FDA revient d'une exécution à l'autre, et aucun garde-fou automatique ne le détecte. »

**Les difficultés.** « Nous avons dû changer de fournisseur en cours de route : l'offre gratuite de Mistral ne donnait pas de clé API, donc nous sommes passés à Gemini. L'offre gratuite de Gemini limite à vingt appels par jour, avec une API très lente, jusqu'à près de dix minutes par appel, et des erreurs de saturation. Nous avons donc ajouté des relances explicites, un budget d'appels, une règle d'arrêt, et planifié les exécutions. »

**Les limites.** « Le corpus ne compte que quatre documents, donc certaines sections sont pauvres. Nous avons retiré, faute de temps, un juge de fidélité indépendant. Le relecteur est du même modèle que le rédacteur. Il n'y a qu'une exécution officielle. Et la validation humaine a été faite par un seul membre, de façon volontairement indulgente : c'est une borne basse des défauts réels. Enfin, nos jugements humains ont été harmonisés après coup, sur proposition d'une IA, selon des règles fixées à l'avance : les valeurs initiales sont tracées, mais l'indépendance du jugement est réduite. »

**Conclusion.** « Le pipeline produit un argumentaire complet, entièrement sourcé, et sans référence inventée. Mais il montre surtout que le contrôle qualité automatique ne remplace pas la relecture humaine : les défauts les plus graves, comme les liens inventés entre sources, ne sont vus que par un humain. »

---

## 2. Tout ce qu'on a fait, dans l'ordre
| Date | Ce qui a été fait | Difficulté et solution |
|---|---|---|
| 30/09 | Lecture des consignes, création de `CLAUDE.md` (mémoire du projet), `implémentation.md` (journal), `pipeline.md` (spécification) | — |
| 30/09 | Choix : **sujet 2, position POUR, option B** (corpus choisi à la main + RAG, plutôt qu'une recherche PubMed automatisée) | Un seul article ne couvrait pas les versants imposés → corpus de plusieurs documents |
| 30/09 | Environnement local : **n8n 2.41.4 + Qdrant 1.19.1** sous Podman, ports limités à la machine (127.0.0.1), télémétrie coupée, clé API sur Qdrant | Quota de téléchargement de l'image n8n → image prise sur Docker Hub ; une clé de chiffrement affichée par erreur → régénérée |
| 30/09 | **Abandon de Mistral** (offre gratuite sans clé API) → **API Gemini** (Google AI Studio) | L'argument « fournisseur européen » tombe → RGPD reformulé |
| 30/09 | Premiers workflows : `00-ingestion` et `test-retrieval` | 100 embeddings par minute au maximum → ingestion par lots + attente |
| 17/10 | Nettoyage du texte avant découpage (bibliographie, appels de référence, césures) ; ajout du document AHA (D12) ; réingestion : **187 chunks** | Au 1er test, 2 extraits sur 5 étaient de la bibliographie |
| 17/10 | Recherche améliorée : requêtes en anglais (comme le corpus), 2 à 3 requêtes par section, plafond de 2 extraits par document, requête « contre » forcée ; identifiant stable `chunk_id` pour chaque extrait | Le top 5 venait d'un seul document, et le document d'Apple n'apparaissait pas |
| 21/10 | **Plan v2 minimale** : corpus figé à 4 documents, juge de fidélité supprimé, pas de correction automatique ; tout ce qui est retiré est listé comme limite | Délai serré |
| 21/10 | Test du modèle : `gemini-3.8-flash` (les modèles Pro sont fermés à l'offre gratuite) ; **1re section rédigée** (technique) | 0 alerte des garde-fous, mais 4 distorsions relevées à la relecture |
| 26/10 | Quotas relevés : **20 appels de chat par jour**, 5 par minute ; paramètre « sections à générer » pour les essais | Aucune exécution complète sans accord |
| 26/10 | **G5** (formulations absolues), **relecteur qui reçoit les sources** (option A), relances explicites sur les erreurs 503, conclusion rédigée après la boucle | « Retry On Fail » de n8n inadapté (attente plafonnée à 5 s) → relance codée explicitement |
| 26/10 | Baseline (`50-baseline`) et script d'évaluation (`eval/evaluer.py` : métriques, tirage des affirmations, kappa), testés par simulation, sans appel | — |
| 26/10 | Protocole d'évaluation du relecteur corrigé : liste de défauts écrite par Claude, **validée par un humain avant** de voir le relecteur | Sinon on mesure l'accord entre deux IA |
| 26-27/10 | Règle d'arrêt (si le premier appel échoue ou est trop lent) ; seuil passé de 180 à 420 s | API très lente (4 à 5 min par appel au lieu de 34 s) ; horloge de la machine virtuelle décalée pendant la veille → resynchronisation avant chaque exécution |
| 27/10 | **Exécution 1** (complète, non officielle) : 47 min, 14 appels ; baseline officielle (22 références) | 2 sections vides (503), caractères corrompus renvoyés par Gemini, conclusion sans accents |
| 27/10 | Liste de 36 défauts de référence → **validée par Adam** à l'aveugle : 15 défauts de fond confirmés sur 30, 4 de forme sur 4 ; puis comparaison avec le relecteur : **1 sur 19** (17 défauts et 1 sur 21 après l'harmonisation du 28/10) | Validation volontairement indulgente, faute de temps (limite déclarée) |
| 27/10 | Correctifs, puis **gel du pipeline** : décodage des caractères corrompus, alerte « texte sans accents », G5 insensible aux accents, 2 relances avec un budget de 18 appels | — |
| 28/10 | **Exécution finale officielle** (`20261028-095239`) : 9 sections sur 9, 59 min, 11 appels ; métriques calculées | Relecteur en échec (délai de 600 s dépassé), compté comme un résultat |
| 28/10 | **Évaluation humaine** (15 affirmations, 1 juge) et **jugement des 8 alertes G5**, puis harmonisation des jugements (A7 et A21 confirmés) | Incohérences entre jugements → harmonisation sur proposition d'une IA, valeurs initiales tracées (limite déclarée) |

---

## 3. L'architecture
```
Corpus : 4 PDF + corpus/meta.json (référence, rôle pour/contre/contexte, versant, année)
  │
00-ingestion : lecture page par page → nettoyage (bibliographie, appels, césures)
  → découpage récursif (1 000 caractères, chevauchement de 150) → embeddings gemini-embedding-001 (3 072 dimensions)
  → Qdrant, collection moa_corpus (187 points) → chunk_id = doc_id + empreinte SHA-1 du texte
  │
10-argumentaire (pour chacune des 8 sections, puis la conclusion)
  A. Recherche : 2-3 requêtes anglaises fixes (top 15) + 1 requête filtrée role = contre (2 meilleurs extraits garantis)
     → fusion, dédoublonnage, 2 extraits max par document, 10 au plus
  B. Rédacteur : Gemini en appel HTTP direct, réponse JSON imposée {paragraphes, citations, contre-arguments traités}
  C. Décodage des caractères corrompus, puis garde-fous G1 G2 G4 G5 → paragraphe marqué ⚠ (pas de correction)
  D. Attente de 15 s (quota) ; relances sur erreur 429/5xx (60 s puis 120 s, budget de 18 appels)
  → Conclusion (à partir des sections, sans nouvelle recherche) → Assemblage (chunk_id → [n], bibliographie depuis meta.json)
  → Relecteur Gemini (argumentaire + consigne + texte des extraits cités + année des documents) → liste de problèmes
  │
50-baseline : un seul appel, même modèle, mêmes règles (dont « n'invente aucune référence »), sans corpus
  │
eval/evaluer.py : métriques (metriques.csv), 15 affirmations tirées au hasard, jugées par 1 juge (pas de kappa, décision du 28/10)
```

**Le corpus**
| Id | Document | Rôle | Extraits |
|---|---|---|---|
| D06 | Apple, *Hypertension Notification Feature on Apple Watch*, livre blanc de validation, septembre 2025 | pour | 22 |
| D07 | FDA, 510(k) K250507, Apple HTNF, 11/09/2025 (prédicat : Viz HCM) | contexte (réglementaire) | 47 |
| D09 | Elgendi et al., *The use of photoplethysmography for assessing hypertension*, npj Digit Med 2019 | contexte (technique) | 59 |
| D12 | Cohen et al., déclaration scientifique de l'AHA sur les tensiomètres sans brassard, *Hypertension* 2026 (en ligne le 11/12/2025) | contre | 59 |

---

## 4. Les choix et leur justification
| Choix | Pourquoi | Ce qu'on a écarté |
|---|---|---|
| n8n en local | Orchestration visuelle et montrable ; données sur la machine | Solutions cloud |
| RAG sur un corpus choisi | Exemple « RAG » de la consigne ; chaque phrase traçable | Recherche PubMed automatisée + tri par LLM (piste v2) |
| Qdrant | Persistance, filtre par métadonnées (requête « contre »), local, intégré à n8n | Simple Vector Store de n8n (vidé à chaque redémarrage) |
| Extraits de 1 000 caractères, chevauchement de 150 | Citation précise, contrôle des chiffres plus strict | Extraits longs, plus flous |
| Gemini (`gemini-3.8-flash`) | Seule offre gratuite utilisable | Mistral (pas de clé gratuite), modèle local (trop faible) |
| Bibliographie générée par le code | Référence inventée impossible | Laisser le LLM citer ses sources |
| Garde-fous qui signalent sans corriger | Simple et transparent | Boucle de régénération (piste v2) |
| Relecteur avec les sources | Sinon il ne peut voir ni un ajout non sourcé ni une chronologie impossible | Relecteur « à l'aveugle » |
| Baseline avec les mêmes règles | Comparaison équitable | Baseline sans consigne |
| Validation humaine à l'aveugle de la liste de défauts | Mesurer la détection de vrais défauts, pas l'accord entre deux IA | Validation par d'autres agents IA |
| Appels HTTP directs, relances explicites, règle d'arrêt | Réponses JSON garanties, erreurs visibles, quota protégé | Nœuds « Gemini Chat Model » et « Retry On Fail » de n8n |
| Gel du pipeline avant l'exécution finale | Résultats attachés à une version fixe | Ajustements de dernière minute |

---

## 5. Les notions techniques (si on me demande)
- **RAG** (*retrieval-augmented generation*) : le LLM rédige à partir de passages récupérés dans un corpus, au lieu de puiser dans sa mémoire d'entraînement. Avantage : traçabilité. Sans RAG, le LLM répond avec ce qu'il a appris, ce qui est invérifiable et parfois inventé.
- **Chunk (extrait)** : un morceau de document. Un embedding résume un texte en un seul vecteur ; avec un article entier, ce vecteur est une moyenne floue. Avec des extraits, chaque vecteur porte une idée précise. Le **chevauchement** évite qu'une idée coupée en deux soit perdue.
- **Embedding** : une liste de nombres (ici 3 072) qui représente le sens d'un texte. Deux textes de sens proche ont des vecteurs proches (mesure : la similarité cosinus, l'angle entre deux vecteurs). Le même modèle doit servir à l'ingestion et à la requête. **Limites** : la négation passe mal (« fiable » et « pas fiable » sont proches), les chiffres aussi (5 ou 15 mmHg), et proximité n'est pas pertinence. D'où les garde-fous.
- **Qdrant / indexation** : chaque extrait est un point (identifiant, vecteur, texte + métadonnées). Pour aller vite à grande échelle, Qdrant construit un index HNSW (un graphe de voisins en plusieurs niveaux). Avec 187 extraits, une comparaison exhaustive irait aussi vite.
- **Équation de recherche PubMed** : blocs de synonymes reliés par OR, combinés par AND ; `[Mesh]` = vocabulaire contrôlé (précision), `[tiab]` = titre et résumé (exhaustivité), `*` = troncature. Avec l'option B, les équations servent à la recherche manuelle.
- **510(k)** : autorisation de la FDA par **équivalence substantielle** à un dispositif déjà autorisé (le prédicat, ici Viz HCM). Ce n'est ni une approbation ni une « validation ».
- **Kappa de Cohen** : accord entre deux évaluateurs, corrigé de l'accord dû au hasard.

---

## 6. Le contrôle qualité
| Contrôle | Ce qu'il vérifie | Ce qu'il ne voit pas |
|---|---|---|
| **Références par construction** | Toute référence vient de `meta.json` | — |
| **G1 Structure** | JSON valide, sections présentes, caractères corrompus, texte sans accents, échecs d'appel | Le fond |
| **G2 Citations** | Chaque extrait cité fait bien partie des extraits récupérés | Si l'extrait soutient vraiment la phrase |
| **G4 Chiffres** | Chaque nombre du paragraphe figure dans un extrait cité | Un chiffre juste mais mal interprété |
| **G5 Formulations absolues** | Une liste de mots (« prouve », « garanti », « robuste », « solide »…), hors formes niées, sans tenir compte des accents | Le contexte (2 fausses alertes sur 8 sur l'exécution finale) ; les sur-affirmations sans mot de la liste |
| **Relecteur** (Gemini) | Structure, contre-arguments non traités, sur-affirmations, équilibre, conclusion, affirmations non soutenues, liens et chronologie entre sources | En pratique, presque rien (1 sur 21) |
| **Baseline** | Ce que fait le LLM seul | — |
| **Évaluation humaine** | 15 affirmations tirées au hasard, jugées SOUTENU / PARTIEL / NON_SOUTENU par **un seul juge** | Fiabilité du jugement non mesurée (pas de second juge, donc pas de kappa) ; jugements harmonisés après coup sur proposition d'une IA |
| **Liste de défauts de référence** | Écrite par Claude, validée à l'aveugle par un membre du groupe, puis comparée au relecteur | Validation indulgente, un seul validateur ; 2 rejets changés à l'harmonisation |

Méthodes de la littérature à citer dans le rapport (**références à vérifier une par une**) : RAGAS (Es et al., 2023), FActScore (Min et al., 2023), LLM-as-a-judge et ses biais (Zheng et al., 2023), Chain-of-Verification (Dhuliawala et al., 2023), SelfCheckGPT (Manakul et al., 2023), cadre QUEST d'évaluation humaine en santé (Tam et al., 2024).

---

## 7. Les résultats chiffrés
**Exécution finale officielle `20261028-095239` (28/10) contre la baseline `20261027-102233` (27/10)**
| | Pipeline | Baseline |
|---|---|---|
| Sections imposées | 9 / 9 | 9 / 9 |
| Références | 4 documents, exactes par construction | 22 écrites par le LLM, ⏳ à vérifier |
| Paragraphes cités | 31 / 31 | 27 / 27 |
| « Information non disponible » | 3 / 34 (HIPAA, CE/MDR, RGPD) | 0 / 27 (règle pourtant dans le prompt) |
| Paragraphes signalés ⚠ | 8 / 34 (G5 : 8, G4 : 1) | sans objet |
| Relecteur | échec : délai de 600 s dépassé | sans objet |
| Appels, durée | 11 appels (1 relance), 59 min | 1 appel, 5 min |

- Durée des appels : de 91 s à 586 s par section.
- **Alertes G5** (jugées par Adam, après harmonisation) : **6 vraies sur 8** (5 avant). Fausses alertes : une négation éloignée du terme, le vocabulaire du 510(k). Rappel non mesuré.
- **Évaluation humaine** (15 affirmations tirées au hasard, 1 juge, sans kappa, après harmonisation) : **5 SOUTENU (33 %), 10 PARTIEL (67 %), 0 NON_SOUTENU** (avant : 4, 8 et 3). Par section : contexte 1 S + 1 P ; technique 2 S ; ethique 1 P ; social_economique 2 P ; parcours_soins 2 P ; autres 2 S + 2 P ; conclusion 2 P ; aucune affirmation tirée dans enjeux_fda ni reglementaire.
- ⏳ L'alerte G4 (« 510 », « 21 », « 870.2380 ») est à vérifier.

**Exécution 1 `20261027-093507` (27/10, non officielle)**
- 47 min, 14 appels (4 relances) ; 2 sections vides (503), 91 caractères corrompus, conclusion sans accents.
- **Défauts de référence** : 30 de fond proposés, **17 confirmés** (A1, A3, A6, A7, A10, A11, A14, A15, A16, A20, A21, A22, A23, A24, A25, A29, A30 ; A7 et A21 ajoutés à l'harmonisation du 28/10), dont 8 de gravité haute, 4 de forme sur 4, 2 cas « invisibles depuis les extraits » rejetés.
- **Relecteur** : 3 problèmes signalés → **1 défaut confirmé repéré sur 21** (les sections vides), **0 sur 17 défauts de fond** (1 sur 19 et 0 sur 15 avant l'harmonisation). Son seul problème de fond porte sur A9 (lien AHA → Apple), rejeté à l'aveugle ; trié après la sortie du relecteur : fausse alerte (position finale).

---

## 8. Les exemples à montrer
1. **Sans corpus, le LLM n'avoue jamais qu'il ne sait pas** : 3 « information non disponible » pour le pipeline, 0 pour la baseline.
2. **« Tout est vert ≠ tout est juste »** (21/10) : 0 alerte, mais une étude unique présentée comme générale, une réserve (« only three subjects ») omise, 30 jours devenus un « suivi sur le long terme ». *Relecture de Claude, non validée par le groupe.*
3. **Le lien inventé entre sources** (A25, confirmé à l'aveugle) : « les critiques pointant les limites de performance […] ne s'appliquent pas aux donnees probantes fournies pour cette notification » (conclusion de l'exécution 1, écrite sans accents par le modèle) : aucun extrait ne l'établit. Observé par Claude dans toutes les sorties, y compris l'exécution finale (« répond directement à ces préoccupations », « dissipe ces craintes ») ; validation humaine : A3 et A25 confirmés, A9 et A18 rejetés à l'aveugle.
4. **La sur-affirmation** : « could improve » (Apple) → « démontre son potentiel » ; « partially expressed » → « permet de capter » ; une sensibilité de 41 % → « garantit un ciblage pertinent ».
5. **L'IA qui relit l'IA** : 1 défaut sur 21, alors que le relecteur a les sources.
6. **Un problème d'infrastructure** : Gemini renvoie « \u0000e9 » au lieu de « é ». G4 l'a repéré (il y voyait des nombres), puis un décodage a été ajouté avant les garde-fous.
7. ⚠ **Fidélité ≠ exactitude** (code produit QXO / SFR) : **ne pas l'utiliser sans avoir vérifié** le PDF D07, p. 8 (C1 et C2 rejetés à la validation ; l'extrait contient les deux codes).

---

## 9. Les difficultés rencontrées et leurs solutions
| Difficulté | Solution |
|---|---|
| Pas de clé API gratuite chez Mistral | Passage à Gemini |
| 20 appels par jour | Essais sur 1 ou 2 sections, budget d'appels, aucune exécution complète sans accord, exécution finale un jour de quota entier |
| API lente (34 s → jusqu'à près de 10 min par appel) et erreurs 503 | Délais longs, relances explicites (60 s puis 120 s), règle d'arrêt sur le premier appel |
| « Retry On Fail » de n8n inutilisable (attente plafonnée à 5 s) | Relance codée dans le workflow, visible sur le schéma |
| Bibliographie dans les extraits | Nettoyage avant découpage |
| Recherche dominée par un seul document | Plusieurs requêtes, plafond par document, extrait « contre » forcé |
| Caractères corrompus, texte sans accents | Décodage avant les garde-fous, alerte G1, G5 insensible aux accents |
| Horloge de la machine virtuelle figée pendant la veille | Contrôle et resynchronisation avant chaque exécution |
| G5 construit sur les sorties qu'il évalue (surajustement) | Liste gelée le 26/10, évaluée seulement sur l'exécution finale |
| Liste de référence écrite par une IA | Validation humaine à l'aveugle avant la comparaison |

---

## 10. Les limites
**Corpus** : 4 documents seulement, choisis à la main (revue non exhaustive, biais de sélection, sections éthique, socio-économique et réglementaire pauvres, un seul document « contre ») ; corpus figé dans une version donnée ; une partie des chiffres épidémiologiques vient du livre blanc d'Apple (source intéressée).

**Contrôle qualité** : pas de juge de fidélité (retiré faute de temps) ; relecteur de la même famille de modèle que le rédacteur, en échec sur l'exécution finale ; G5 = une liste de mots (contexte ignoré, 2 fausses alertes sur 8) ; les défauts sont signalés, pas corrigés.

**Évaluation** : une seule exécution officielle (variabilité non mesurée) ; évaluation humaine sur 15 affirmations **par un seul juge, donc sans kappa** (fiabilité du jugement non mesurée) ; une phrase est jugée par rapport aux extraits de son paragraphe (surestime la fidélité) ; liste de défauts écrite par une IA puis **validée par un seul membre, de façon volontairement indulgente** (borne basse des défauts réels) ; jugements humains harmonisés a posteriori sur proposition d'une IA (Claude), selon des règles fixées à l'avance, valeurs initiales tracées : indépendance du jugement réduite.

**Modèle et infrastructure** : offre gratuite (20 appels par jour, latence très variable, erreurs 503) ; modèle Flash seulement ; API américaine (le texte du corpus, des publications sans aucune donnée patient, part chez Google ; pour les utilisateurs de l'EEE, les conditions de l'offre payante s'appliquent au quota gratuit : pas d'entraînement sur les requêtes).

**Pistes v2** : recherche PubMed automatisée avec tri par deux LLM et diagramme PRISMA ; corpus complet (~20 documents) ; juge de fidélité d'une autre famille de modèle ; relecteur d'un autre fournisseur ; boucle de correction bornée ; plusieurs exécutions ; évaluation par des cliniciens.

---

## 11. Questions probables et réponses
| Question | Réponse |
|---|---|
| Pourquoi un RAG plutôt qu'un LLM seul ? | Traçabilité, références impossibles à inventer. La baseline montre ce que fait le LLM seul : elle n'avoue jamais ne pas savoir. |
| Pourquoi Qdrant ? | Persistance, filtre par métadonnées (requête « contre »), local, intégré à n8n. Pas un choix de performance : 187 extraits. |
| Pourquoi des extraits de 1 000 caractères ? | Citation précise, contrôle des chiffres plus strict. Valeur non optimisée par une mesure : c'est une limite. |
| Pourquoi les garde-fous ne corrigent-ils pas ? | Transparence et simplicité : on montre les défauts. La correction automatique est une piste v2. |
| Pourquoi le relecteur échoue-t-il ? | Même modèle que le rédacteur, texte en partie corrompu sur l'exécution 1, délai dépassé sur l'exécution finale (le prompt avec les sources est lourd). Résultat en soi : un contrôle par IA ne remplace pas la relecture humaine. |
| Comment savez-vous que vos défauts de référence sont justes ? | Écrits par un LLM, puis validés un à un par un membre du groupe, sans voir le relecteur. Validation indulgente, assumée. Deux rejets (A7, A21) changés ensuite pour appliquer la même règle qu'à A1, sur proposition d'une IA : valeurs initiales tracées. |
| Et le RGPD avec une API américaine ? | Aucune donnée patient ; conditions EEE de l'API ; le reste tourne en local. En clinique, il faudrait un modèle local ou un fournisseur européen sous contrat. |
| Pourquoi avoir changé de fournisseur ? | Contrainte d'accès, avec un impact assumé sur l'argument RGPD. |
| 510(k), De Novo, marquage CE ? | 510(k) : équivalence substantielle à un prédicat (ici Viz HCM). De Novo : nouvelle classification pour un dispositif sans prédicat. En Europe : marquage CE selon le règlement (UE) 2017/745 (MDR) ; absent de notre corpus. |
| Pourquoi le sans-brassard reste-t-il débattu ? | Selon l'AHA : calibration, mesure de variations plutôt que de valeurs absolues, protocoles de validation inadaptés, performances médiocres en conditions dynamiques. La fonction d'Apple ne mesure pas une pression : elle classe un risque sur 30 jours. |
| Que pensez-vous de la conclusion de l'IA ? | ⏳ À préparer en groupe. |
| Pourquoi pas de kappa ? | Faute de temps, un seul juge : l'accord entre évaluateurs n'est pas mesuré. C'est noté en limite ; le script de calcul du kappa est prêt pour une v2. |
| Reproductibilité ? | Versions figées, prompts versionnés, workflows exportés dans git, `runs.jsonl` (modèle, prompts, appels, durées) ; mais un LLM n'est pas déterministe, et une seule exécution officielle. |

---

## 12. Les chiffres à connaître
- **Corpus** : 4 documents, **187 extraits** (D06 22, D07 47, D09 59, D12 59).
- **Étude d'Apple** : 2 229 inclus, 1 863 analysables ; 30 jours de port ; sensibilité **41,2 %** (53,7 % au stade 2) ; spécificité **92,3 %** (95,3 % chez les normotendus).
- **Quotas gratuits** : 20 appels de chat par jour, 5 par minute.
- **Exécution finale** : 9 / 9 sections, 31 / 31 paragraphes cités, 3 « information non disponible » (baseline : 0), 8 / 34 paragraphes signalés, 11 appels, 59 min.
- **Exécution 1** : 17 défauts de fond confirmés sur 30 (8 de gravité haute) ; relecteur **1 sur 21** (0 sur 17 sur le fond).
- **Évaluation humaine** : 5 SOUTENU, 10 PARTIEL, 0 NON_SOUTENU sur 15 ; **G5** : 6 vraies alertes sur 8.

---

## 13. Ce qui reste à faire
**L'implémentation est arrêtée** (28/10, pipeline gelé) : ce qui n'a pas été réalisé est listé dans les limites (`pipeline.md` § 5). Il ne reste que des tâches d'évaluation courtes, le rapport et l'oral.
- Évaluation humaine et jugement des alertes G5 : faits le 28/10 (jugements harmonisés, valeurs initiales tracées).
- ⏳ Vérification des 22 références de la baseline (≈ 1 h à 1 h 30).
- ⏳ Vérification de l'alerte G4 et du cas QXO / SFR (≈ 15 min).
- ⏳ Captures des workflows (≈ 15 min).
- ⏳ Rapport écrit (≈ 9 à 11 h) et oral (≈ 5 à 7 h) : détail dans `point_28-10.md`.
- ⏳ Confirmer la date limite (02/11 ?) et les noms des membres.
