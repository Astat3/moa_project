# Consignes — 26/10/2026, 21 h 15 · après le commit 9dfb7fb
Revue du rapport de 21 h 07. **À exécuter seulement après la validation explicite d'Adam.**

## 1. Choix validés
- **Baseline** : les 4 choix sont validés. L'interdiction d'inventer des références rend la comparaison plus équitable, et le résultat plus fort si la baseline en invente quand même. Dans le rapport, il faudra préciser que la baseline a reçu **les mêmes règles** que le rédacteur, sauf celles qui dépendent du corpus.
- **Évaluation** : les 4 choix sont validés : une phrase par affirmation, deux fichiers séparés, définition de `PARTIEL`, texte des chunks dans verif. Ajoute au § 5 la limite « affirmation jugée par rapport aux chunks de son paragraphe, et non de sa phrase : une phrase peut être jugée soutenue grâce à un chunk cité pour une autre phrase ».

## 2. Règle d'arrêt : option A, avec trois ajustements
1. **Paramétrable** dans le nœud Paramètres : `arret_premier_appel` (oui/non) et `seuil_premier_appel_s` (180). Activée pour l'essai de demain et pour l'exécution finale.
2. **Traçabilité** : en cas d'arrêt, écris quand même une ligne dans `runs.jsonl`, avec le statut `arrete`, la raison (délai ou échec après relance), la durée et le nombre d'appels consommés. Un arrêt ne doit pas être invisible.
3. La règle ne porte **que sur le premier appel**. Ensuite, un appel lent mais réussi continue normalement : on ne veut pas perdre l'exécution finale à la 6e section pour une lenteur passagère.

Teste-la par simulation ce soir ou demain avant 8 h, sans appel de chat.

## 3. Demain, 27/10 après 8 h
Le plan de ton rapport est validé tel quel (points 1 à 5), dès qu'Adam donne le feu vert.
