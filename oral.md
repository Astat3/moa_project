# oral.md — Étapes, choix et limites, pour la présentation orale
Support de préparation de l'oral (10 min + 10 min de questions). Chaque point renvoie au fichier où se trouve le détail.

> Rôle des fichiers : `CLAUDE.md` (décisions datées) · `pipeline.md` (spécification, § 5 = toutes les limites) · `implémentation.md` (journal) · `tech.md` (notions : chunks, embeddings, Qdrant) · `outputs/` (résultats).
> ⏳ = à compléter après l'exécution finale du 28/10 et l'évaluation humaine.

---

## 1. Le pipeline en une phrase
Un pipeline **RAG orchestré en local avec n8n** qui rédige un argumentaire **POUR** l'autorisation FDA de la notification d'hypertension de l'Apple Watch, **à partir d'un corpus de 4 documents choisis par le groupe**, et dont **chaque affirmation cite un extrait du corpus**. Des **garde-fous automatiques** et un **agent relecteur** signalent les défauts, et le tout est **comparé à une baseline** (le même LLM, sans corpus).

**Schéma (graphical abstract)**
```
Corpus (4 PDF + meta.json)
  → 00-ingestion : nettoyage → découpage (1 000 car., chevauchement 150) → embeddings Gemini → Qdrant (187 chunks)
  → 10-argumentaire : pour chaque section
        recherche Qdrant (2-3 requêtes + 1 requête « contre » forcée, 2 chunks max par document, 10 au plus)
        → rédacteur Gemini (JSON, cite des chunk_id)
        → garde-fous G1 G2 G4 G5 (signalent ⚠, ne corrigent pas)
     → conclusion → assemblage (bibliographie générée par le code) → relecteur Gemini (liste de problèmes)
  → 50-baseline : même modèle, mêmes règles, sans corpus
  → eval/evaluer.py : métriques + évaluation humaine (1 juge, pas de kappa)
```

---

## 2. Les étapes de construction (chronologie)
| Date | Étape | Ce qu'il faut en retenir à l'oral |
|---|---|---|
| 30/09 | Cadrage, stack locale (n8n + Qdrant sous Podman), choix du LLM | Position **POUR**. Option B : corpus choisi à la main plutôt qu'une recherche PubMed automatisée. **Mistral abandonné** (pas de clé API en offre gratuite), **passage à Gemini** |
| 30/09 → 17/10 | Ingestion et recherche | 1er test : 2 chunks sur 5 étaient de la **bibliographie** → nettoyage avant découpage. Top 5 venant d'un seul document → **plusieurs requêtes + plafond par document + requête « contre » forcée** |
| 21/10 | **Plan v2 minimale** + 1re section rédigée | Le délai impose de simplifier : corpus figé à 4 documents, juge de fidélité (G3) supprimé, pas de correction automatique. Tout ce qui est retiré est listé comme limite. 1re section : **0 alerte des garde-fous, mais 4 distorsions** relevées en relisant (« tout est vert ≠ tout est juste ») |
| 26/10 | Relecteur, G5, relances, baseline, script d'évaluation | Relecteur qui **reçoit les sources** (option A). G5 contre les formulations absolues. Relance explicite sur les erreurs 503. Baseline avec **les mêmes règles** que le rédacteur |
| 27/10 | Exécution complète candidate + validation humaine + comparaison avec le relecteur | API très lente (4 à 5 min par appel au lieu de 34 s) et instable (503) → 2 sections vides, caractères corrompus. Liste de défauts écrite par Claude, **validée par un membre du groupe** à l'aveugle, puis comparée au relecteur : **1 défaut repéré sur 19** |
| 27/10 | Correctifs, puis **gel** du pipeline | Décodage des caractères corrompus, alertes « texte sans accents », G5 insensible aux accents, 2 relances avec un budget d'appels |
| 28/10 | Exécution finale officielle (`20261028-095239`) | Horloge de la VM en retard de 13 h 26 après la veille du Mac : resynchronisée avant le lancement. 59 min, 11 appels (1 relance après un 503), **9 sections sur 9**, aucun caractère corrompu. **Relecteur en échec** : délai de 600 s dépassé, donc pas de relance (règle fixée le 26/10) |

---

## 3. Les choix et leur justification
| Choix | Pourquoi | Ce qu'on a écarté |
|---|---|---|
| **n8n en local** (Podman), ports limités à la machine, télémétrie coupée | Orchestration visuelle et montrable ; données sur la machine | Solutions cloud |
| **RAG sur un corpus choisi** (4 documents : Apple D06 « pour », FDA K250507 D07 et Elgendi 2019 D09 « contexte », AHA 2026 D12 « contre ») | La consigne propose l'exemple « RAG à partir d'un corpus d'articles » ; chaque phrase devient traçable | Recherche PubMed automatisée + tri par LLM (piste v2) |
| **Qdrant** | Persistance, filtrage par métadonnées (`role = contre`), exécution locale, nœud natif n8n | Simple Vector Store de n8n (vidé à chaque redémarrage) |
| **Chunks de 1 000 caractères, chevauchement 150**, découpage récursif page par page | Chunks courts = citation précise et contrôle des chiffres (G4) plus strict | Chunks plus longs (moins précis) |
| **Gemini** (`gemini-3.8-flash`, embeddings `gemini-embedding-001`) | Seule offre gratuite utilisable (Mistral : pas de clé API gratuite ; modèles Pro fermés au gratuit) | Modèle local (Ollama), jugé trop faible pour la rédaction |
| **Le LLM n'écrit jamais une référence** : il cite des `chunk_id`, la bibliographie est générée par le code depuis `meta.json` | Une référence inventée devient **impossible par construction** : c'est le garde-fou principal | Laisser le LLM citer ses sources |
| **Garde-fous qui signalent sans corriger** : G1 structure, G2 citations, G4 chiffres, G5 formulations absolues | Simple, lisible, et chaque défaut reste visible pour la critique | Boucle de régénération (piste v2) |
| **Relecteur qui reçoit les sources** (texte des chunks cités + année des documents) | Sans les sources, il ne peut pas voir un ajout non sourcé ni une chronologie impossible | Relecteur « à l'aveugle » |
| **Baseline avec les mêmes règles** (dont l'interdiction d'inventer des références) | Comparaison équitable : si elle invente malgré la consigne, le résultat est plus fort | Baseline sans consigne |
| **Liste de défauts écrite par Claude, validée par un humain avant de voir le relecteur** | Sinon on mesure l'accord entre deux IA, pas la détection de vrais défauts | Liste établie et validée par des IA |
| **Appels HTTP directs à Gemini** (JSON avec schéma), relances explicites, règle d'arrêt si le premier appel échoue | Sorties JSON garanties, erreurs visibles, pas de relances cachées ; quota de 20 appels par jour | Nœud « Gemini Chat Model » et « Retry On Fail » de n8n (attente plafonnée à 5 s) |
| **Gel du pipeline** avant l'exécution finale | Les résultats présentés correspondent à une version fixe et documentée | Ajustements de dernière minute |

---

## 4. Les résultats (exécution 1 du 27/10 ; exécution finale du 28/10)
- **Exécution 1** (`20261027-093507`, non officielle) : 47 min, 14 appels (dont 4 relances). 2 sections vides (erreurs 503), une section aux accents corrompus, une conclusion sans accents.
- **Baseline officielle** (`20261027-102233`) : 9 sections sur 9, 22 références. ⏳ Vérification de chaque référence (existe ? correcte ?).
- **Liste de défauts de référence** : 30 défauts de fond proposés par Claude, **15 confirmés** par le groupe (validation indulgente, voir les limites), 4 défauts de forme sur 4.
- **Relecteur** : 3 problèmes signalés → **1 défaut confirmé repéré sur 19**, **0 sur 15 défauts de fond**. Son seul problème de fond porte sur un passage (A9) que le validateur avait rejeté à l'aveugle ; trié après sa sortie : **fausse alerte** (position finale, 28/10). Score officiel : 1 sur 19.
- **Exécution finale** (`20261028-095239`, officielle) : 59 min, 11 appels de chat (dont 1 relance). **9 sections sur 9**, 34 paragraphes, dont 3 `[INFORMATION NON DISPONIBLE]` (HIPAA, marquage CE / MDR, RGPD : absents du corpus). Les 31 autres citent tous au moins un extrait.
  - **Garde-fous** : 8 paragraphes signalés sur 34 (G5 : 8, G4 : 1 ; G1 et G2 : 0). Aucun caractère corrompu.
  - **Relecteur en échec** : l'appel a dépassé le délai de 600 s (la conclusion avait déjà pris 586 s). Un délai dépassé n'est pas relancé (règle fixée le 26/10). Le relecteur n'est donc évalué que sur l'exécution 1.
- **Pipeline contre baseline** (`outputs/metriques.csv`) :

  | Métrique | Pipeline (28/10) | Baseline (27/10) |
  |---|---|---|
  | Sections imposées présentes | 9 / 9 | 9 / 9 |
  | Références | 4 documents, exactes par construction | 22 références écrites par le LLM, ⏳ à vérifier une par une |
  | Paragraphes avec au moins une citation | 31 / 31 | 27 / 27 |
  | `[INFORMATION NON DISPONIBLE]` | 3 / 34 | 0 / 27 (même règle dans son prompt, jamais employée) |
  | Paragraphes signalés ⚠ | 8 / 34 | sans objet (pas de garde-fous) |
  | Appels de chat, durée | 11 appels, 59 min | 1 appel, 5 min |

- **Contraste `[INFORMATION NON DISPONIBLE]` : pipeline 3, baseline 0.** Le pipeline déclare 3 manques (HIPAA, marquage CE / MDR, RGPD : absents du corpus). La baseline a la même règle dans son prompt, mais ne l'emploie jamais : elle traite ces trois points de mémoire, avec des références ⏳ à vérifier.
- ⏳ Évaluation humaine de 15 affirmations par un seul juge (pas de kappa : décision du 28/10, notée en limite).

---

## 5. Exemples concrets à montrer (un par message clé)
1. **« Tout est vert ≠ tout est juste »** (21/10) : 0 alerte des garde-fous, mais 4 distorsions à la relecture (une étude présentée comme générale, une réserve « only three subjects » omise, « suivi sur le long terme » pour 30 jours). Relecture faite par Claude, non validée par le groupe : à présenter comme tel.
2. **L'IA qui relit l'IA ne voit presque rien** : 1 défaut repéré sur 19, 0 défaut de fond, malgré l'accès aux sources. Hypothèses : même famille de modèle que le rédacteur, texte en partie corrompu.
3. **Lien inventé entre sources** (A25, conclusion de l'exécution 1, confirmé à l'aveugle) : « les critiques pointant les limites de performance […] ou l'inadequation des protocoles de laboratoire ne s'appliquent pas aux donnees probantes fournies pour cette notification » (texte écrit sans accents par le modèle). Aucun extrait n'établit que les critiques de l'AHA ne s'appliquent pas, et l'étude d'Apple évalue une classification sur 30 jours, pas le suivi des variations de pression. Observé par Claude dans toutes les sorties ; validation humaine : A3 et A25 confirmés (A3 : variante livre blanc d'Apple → FDA), A9 et A18 rejetés à l'aveugle ; le problème du relecteur sur A9, trié après sa sortie, est classé fausse alerte. Les garde-fous ne le détectent pas, et le relecteur ne repère ni A3 ni A25.
4. **La sur-affirmation** : « could improve » (Apple) devient « démontre son potentiel » ; « partially expressed » devient « permet de capter » ; une sensibilité de 41 % devient « garantit un ciblage pertinent ».
5. **Fidélité ≠ exactitude** (code produit QXO / SFR) : ⚠ **à vérifier avant de l'utiliser.** C1 et C2 ont été rejetés à la validation, et le chunk de D07 contient les deux codes (colonnes du tableau mélangées à l'extraction). Ouvrir le PDF D07, p. 8, et la correction administrative citée dans `corpus.md`.
6. **Un problème d'infrastructure, pas de contenu** : Gemini a renvoyé « \u0000e9 » au lieu de « é » ; repéré par G4 (qui y voyait des nombres), puis réparé par un décodage avant les garde-fous.

---

## 6. Les limites (détail complet : `pipeline.md` § 5)
**Corpus et recherche**
- 4 documents seulement, choisis à la main : revue non exhaustive, biais de sélection, sections éthique / socio-économique / réglementaire pauvres, un seul document « contre ».
- Corpus figé dans une version donnée : un fait fidèle à l'extrait peut être périmé.
- Une partie des chiffres épidémiologiques vient du livre blanc d'Apple (source intéressée), faute de source OMS dans le corpus.

**Contrôle qualité**
- Pas de juge de fidélité (G3 retiré faute de temps) : ajouts non sourcés et liens inventés repérés seulement par le relecteur et l'humain, et le relecteur n'en repère aucun parmi les défauts confirmés.
- Relecteur de la même famille de modèle que le rédacteur (risque de complaisance).
- G5 = une liste de mots : il ignore le contexte, a des faux positifs, et a été **construit sur les sorties qu'il a ensuite évaluées** (surajustement ; liste gelée le 26/10).
- Les garde-fous signalent sans corriger : l'argumentaire final contient ses défauts, marqués ⚠.

**Évaluation**
- **Validation de la liste de défauts faite par un seul membre, avec un jugement volontairement indulgent** sur les cas limites, faute de temps (objectif : un pipeline fonctionnel, pas parfait) → la liste confirmée est une borne basse des défauts réels.
- Liste de référence d'abord écrite par un LLM.
- Une seule exécution officielle : variabilité non mesurée. Évaluation humaine sur 15 affirmations seulement, par un seul juge : pas de kappa, la fiabilité du jugement n'est pas mesurée.
- Une phrase est jugée par rapport aux chunks de son paragraphe, ce qui surestime la fidélité.

**Modèle et infrastructure**
- Offre gratuite : 20 appels par jour, latence très variable (34 s le 21/10, de 2 à 8 min le 27/10 ; le 28/10, de 23 s à 10 min, relecteur au-delà de 10 min), erreurs 503 → sections vides possibles.
- Modèle Flash seulement (Pro fermé à l'offre gratuite).
- API américaine : le texte du corpus (publications, aucune donnée patient) part chez Google. Pour les utilisateurs de l'EEE, les conditions de l'offre payante s'appliquent aussi au quota gratuit (pas d'entraînement sur les requêtes).

---

## 7. Questions probables et éléments de réponse
| Question | Réponse courte |
|---|---|
| Pourquoi un RAG plutôt qu'un LLM seul ? | Traçabilité : chaque phrase renvoie à un extrait, les références ne peuvent pas être inventées. La baseline montre ce que fait le LLM seul. |
| Pourquoi Qdrant ? | Persistance, filtre par métadonnées (requête « contre » forcée), local, intégré à n8n. Pas un choix de performance : 187 chunks. |
| Comment avez-vous choisi la taille des chunks ? | 1 000 caractères : citation précise, contrôle des chiffres plus strict. Non optimisé par une mesure (limite). |
| Pourquoi les garde-fous ne corrigent-ils pas ? | Simplicité et transparence : on montre les défauts au lieu de les masquer. La correction automatique est une piste v2. |
| Pourquoi le relecteur échoue-t-il ? | Même modèle que le rédacteur, texte en partie corrompu, une seule exécution. C'est un résultat en soi : un contrôle par IA ne remplace pas la relecture humaine. Sur l'exécution finale, il n'a même pas abouti : délai de 10 min dépassé (API saturée), sans relance, et l'échec est compté comme un résultat. |
| Comment savez-vous que vos défauts de référence sont justes ? | Écrits par un LLM, puis validés un par un par un membre du groupe, à l'aveugle (sans voir le relecteur). Validation indulgente, assumée comme limite. |
| Et le RGPD avec une API américaine ? | Aucune donnée patient ; conditions EEE de l'API Gemini ; le reste tourne en local. Une version clinique demanderait un modèle local ou un fournisseur européen sous contrat. |
| Pourquoi avoir changé de fournisseur ? | Contrainte d'accès (offre gratuite de Mistral sans clé API), avec un impact assumé sur l'argument RGPD. |
| Différence entre une autorisation 510(k) et une « validation » ? | 510(k) = autorisation par équivalence substantielle à un dispositif existant (ici le prédicat Viz HCM), pas une approbation. Le rédacteur emploie parfois « validé » à tort. |
| Votre IA conclut POUR : qu'en pensez-vous ? | ⏳ À préparer avec le groupe après l'exécution finale. |

---

## 8. Chiffres à connaître
- Corpus : 4 documents, **187 chunks** (D06 22, D07 47, D09 59, D12 59).
- Étude d'Apple (D06, D07) : 2 229 inclus, 1 863 analysables ; sensibilité **41,2 %** (53,7 % au stade 2) ; spécificité **92,3 %** (95,3 % chez les normotendus) ; 30 jours de port.
- Quotas gratuits : **20 appels de chat par jour**, 5 par minute.
- Exécution 1 : 47 min, 14 appels ; défauts : **15 de fond confirmés sur 30** ; relecteur : **1 sur 19**.
- Exécution finale : 59 min, 11 appels ; 9 sections sur 9 ; 34 paragraphes, dont 8 signalés et 3 `[INFORMATION NON DISPONIBLE]` ; relecteur en échec (délai de 600 s). Baseline : 22 références, 1 appel, 5 min.
- ⏳ Résultats de l'évaluation humaine (1 juge, sans kappa).

---

## 9. Reste à faire pour l'oral
- Exécution finale et métriques : faites le 28/10.
- ⏳ Évaluation humaine (1 juge : `outputs/eval_humaine_juge1.csv` ; pas de kappa), vérification des références de la baseline (`outputs/references_baseline.csv`).
- ⏳ Vérifier le cas QXO / SFR dans le PDF D07 (p. 8) avant de s'en servir.
- ⏳ Captures : `00-ingestion`, `10-argumentaire`, `50-baseline`.
- ⏳ Point de vue du groupe sur la conclusion de l'IA.
