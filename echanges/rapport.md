# Rapport — 27/10/2026, 10 h 50 · après le commit 8bde9d6
Rapport de Claude Code sur les consignes de 10 h 45 (correctifs avant le gel).

## En bref
- Les points 1 à 3 sont **codés et testés par simulation, sans aucun appel de chat**. Le point 4 (baseline) et le point 5 (exécution 1) sont consignés. **Le pipeline est gelé** au commit `8bde9d6`.
- **Point d'attention** : les 120 s d'attente avant la 3e tentative sont faites de **deux attentes de 60 s**. Le code du nœud *Wait* de n8n (lignes 506 à 518) met l'exécution en attente dans la base au-delà de 65 s, ce qui casserait une exécution lancée en CLI. La durée totale est bien de 120 s.
- **Demain, 28/10 à 8 h pile, avec ton feu vert** : contrôle de l'horloge, puis exécution finale. Baseline : celle du 27/10.
- **En attente du groupe** : valider `outputs/defauts_reference_20261027-093507.md`, sans ouvrir la relecture, avant l'appariement sur l'exécution 1.

## 1. Décodage de l'encodage
**Où** : juste après `JSON.parse` de la réponse de Gemini, **avant** G1 à G5. G4 et G5 travaillent donc sur le texte réparé.

**Ce qui est fait** :
- Un caractère NUL suivi de 2 chiffres hexadécimaux est remplacé par le caractère correspondant (`\u0000e9` → « é »).
- Le motif est strict : **tout autre NUL est laissé tel quel et signalé par G1**.
- Le nombre de remplacements va dans `verif` et `runs.jsonl`. Le même décodage s'applique à la réponse du relecteur.

**Présentation dans `pipeline.md`** : c'est un *décodage*, pas une correction de contenu. Il rétablit le texte voulu par le modèle et ne contredit donc pas le principe « les garde-fous signalent sans corriger ».

**Baseline du 27/10** : aucun caractère NUL et des accents dans les 9 sections. `eval/evaluer.py` n'a donc pas besoin de la réparer.

## 2. Texte sans accents et G5
- **G1** signale une section rédigée (200 caractères au moins hors marqueur) qui ne contient aucun caractère accentué.
- **G5** compare désormais **sans tenir compte des accents**, en normalisant le texte et la liste. Les lignes de la liste gelée (`TERMES`, `NEGATION`) sont inchangées, au caractère près. C'est noté au § 5, avec sa cause : la conclusion du 27/10.
- Les 34 cas d'essai passent. Sur l'exécution 1, G5 voit maintenant « demontre » (A30).
- Il ajoute aussi une **fausse alerte probable** : « les résultats démontrent une spécificité de 92,3 % » (conclusion § 3), qui est un simple compte rendu. Je l'ai notée au § 5.
- Pas de changement de prompt.

## 3. Relances avec budget
- Jusqu'à **2 relances** par appel, après 60 s puis 120 s, sur HTTP 429 ou 5xx seulement. Un délai dépassé n'est toujours pas relancé.
- **Budget** : une relance n'est tentée que si le total des appels de chat de l'exécution reste ≤ 18. Ce budget est réglé dans le nœud Paramètres. Au-delà, l'échec est signalé par G1, avec la mention « budget atteint ».
- `runs.jsonl` contient le budget, les relances refusées et les tentatives par section.
- Le mécanisme s'applique aux sections, à la conclusion et au relecteur. Les compteurs de l'exécution sont gardés dans `$execution.customData` ; j'ai d'abord vérifié qu'il fonctionne en CLI.
- La règle d'arrêt déduit désormais les attentes de relance : 60 s pour 2 tentatives, 180 s pour 3.

**Simulation** (budget de test de 9, attentes ramenées à 1 s) :

| Section | Scénario | Obtenu |
|---|---|---|
| contexte | accents corrompus, plus un NUL non décodable | 3 caractères décodés ; G1 « caractère NUL non décodable » |
| enjeux_fda | 503, 503, puis 200 | 3 tentatives, section rédigée ; seconde attente exécutée |
| technique | texte sans accents avec « demontre » | G1 « sans aucun caractère accentué » ; G5 « demontre » |
| ethique | 503 trois fois | G1 après 3 tentatives |
| conclusion | 503 | relance refusée (budget atteint), G1 avec mention du budget |
| relecteur | 503 | relance refusée (budget), erreur consignée dans `relecture` |

`runs.jsonl` : 10 appels de chat, tentatives `{1, 3, 1, 3, 1, relecteur 1}`, relances refusées `[conclusion, relecteur]`, 3 décodages. Les sorties de test ont été supprimées et le vrai workflow réinstallé (40 nœuds, budget 18, 9 sections, seuil de 420 s).

## 4 et 5. Baseline et exécution 1
- **Baseline officielle : `baseline_20261027-102233`**, notée dans `pipeline.md` : même modèle, mêmes règles, délai de 1 200 s, produite le 27/10.
- **Exécution 1 (non officielle) : `20261027-093507`**, gardée avec ses défauts techniques. Elle sert à la comparaison avec le relecteur, et à montrer que le lien inventé AHA → Apple/FDA revient d'une exécution à l'autre.

## Demain, 28/10 à 8 h pile (avec ton feu vert)
1. Contrôle de l'horloge (`chronyc makestep` si l'écart dépasse 5 s).
2. `10-argumentaire` : 9 sections dont la conclusion, puis le relecteur, soit 10 appels plus les relances, dans la limite de 18. À la vitesse du 27/10, compter entre 50 min et 1 h 15.
3. `eval/evaluer.py metriques <run> 20261027-102233`. J'attendrai pour l'évaluation humaine : elle se fait en deux copies, une par évaluateur.
4. Export, commit, rapport ici, avec la liste de ce qui reste à faire au groupe.

## En attente du groupe
- Valider la liste de défauts de référence de l'exécution 1 (colonne « Validation »), sans ouvrir la relecture. Ensuite seulement, je ferai l'appariement : « X défauts confirmés repérés sur Y ».
