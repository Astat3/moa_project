# Consignes — 27/10/2026, 10 h 45 · après le commit d5f96f1
Revue du rapport de l'exécution candidate. **À exécuter seulement après la validation explicite d'Adam.**

## 1. Accents corrompus : validé, avec deux précisions
- La réparation est un **décodage**, pas une correction de contenu. Place-la juste après la lecture de la réponse de Gemini, **avant** les garde-fous, pour que G4 et G5 travaillent sur le texte réparé. Dans `pipeline.md`, présente-la comme telle, sinon elle contredit le principe « les garde-fous signalent sans corriger ».
- Motif strict : seulement un caractère NUL suivi de 2 chiffres hexadécimaux. Compte les réparations dans verif, et **signale (G1) tout caractère NUL restant** qui ne correspond pas au motif, au lieu de le deviner.
- Vérifie que la baseline d'aujourd'hui n'a pas le même défaut. Si elle l'a, applique la même réparation dans `eval/evaluer.py`, pour traiter les deux côtés à égalité.

## 2. Texte sans accents : alerte G1, validé, plus un ajustement de G5
- Alerte G1 si une section en français ne contient aucun caractère accentué.
- **G5 compare sans tenir compte des accents** : texte et liste normalisés avant la comparaison. Ce n'est pas une modification de la liste gelée (aucun terme ajouté ni retiré), c'est une correction générique du comparateur. Note-le explicitement au § 5, avec sa cause (la conclusion du 27/10).
- Pas de changement de prompt.

## 3. Seconde relance après 120 s : validée, avec un plafond global
Avec 2 relances par appel, le pire cas dépasse le quota du jour. Ajoute un **budget** : une relance n'est tentée que si le nombre total d'appels de chat de l'exécution reste ≤ 18. Au-delà, la section est signalée G1 sans relance. Note le budget dans runs.jsonl.

## 4. Baseline d'aujourd'hui = baseline officielle : validé
C'est défendable : la baseline n'utilise ni le RAG ni les garde-fous, donc elle ne dépend pas du pipeline. Note dans `pipeline.md` qu'elle a été produite le 27/10, avec le même modèle et les mêmes règles, et un délai de 1 200 s.

## 5. L'exécution d'aujourd'hui garde de la valeur
Garde-la comme **exécution 1 (non officielle, défauts techniques)**. Elle répond en partie à la limite « une seule exécution » : par exemple le lien AHA → Apple/FDA, qui revient à chaque exécution. La comparaison avec le relecteur se fait sur **celle-ci**, puisque la liste de référence est prête. On ne la refait pas sur l'exécution de demain, faute de temps.

## 6. Demain
- Code et teste les points 1 à 3 ce soir, par simulation, puis gel.
- Demain : **lance à 8 h pile** (remise à zéro du quota, charge plus faible), après le contrôle de l'horloge. Exécution finale : 9 sections, conclusion, relecteur (10 appels, plus les relances dans la limite du budget). Ensuite `eval/evaluer.py`, export, commit, rapport.
