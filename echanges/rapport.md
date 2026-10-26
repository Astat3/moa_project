# Rapport — 26/10/2026, 21 h 14 · après le commit f7afe71
Rapport de Claude Code sur les consignes de 21 h 15.

## En bref
- Ton message parlait des points 0, 1, 2 et de la partie « Ce soir » du point 3. Les nouvelles consignes n'ont que trois points : 1 (choix validés), 2 (règle d'arrêt) et 3 (demain). J'ai donc **exécuté les points 1 et 2 ce soir**, et le point 3 attend ton feu vert demain après 8 h.
- **Aucun appel de chat** ce soir : tout a été testé par simulation, avec 19 requêtes d'embeddings.
- Commit `f7afe71`, plus celui de ce rapport. Rien n'est poussé.
- **Aucune question bloquante** pour demain.

## 1. Choix validés
- Les choix de la baseline et de l'évaluation sont notés dans `CLAUDE.md` § 5.
- Limite ajoutée à `pipeline.md` § 5 : « affirmation jugée par rapport aux chunks de son paragraphe, et non de sa phrase ». Une phrase peut être jugée soutenue grâce à un chunk cité pour une autre phrase, ce qui surestime la fidélité. Piste : des citations par phrase, ou FActScore.
- Pour la rédaction du rapport final, deux points sont notés dans `implémentation.md` (étape 9, critique des résultats) :
  - la baseline a reçu **les mêmes règles** que le rédacteur, sauf celles qui dépendent du corpus ;
  - la limite sur la phrase et son paragraphe.

## 2. Règle d'arrêt (option A, avec les trois ajustements)
**Paramètres**, dans le nœud Paramètres de `10-argumentaire` :
- `arret_premier_appel: true` ;
- `seuil_premier_appel_s: 180`.

Elle est donc activée pour l'essai de demain et pour l'exécution finale.

**Premier appel seulement.** Les garde-fous le vérifient à leur première exécution. Il y a arrêt si l'appel échoue malgré la relance (`echec`) ou s'il dure plus que le seuil (`delai`). La durée est mesurée depuis le prompt, en retirant les 60 s d'attente de la relance.

**Traçabilité.** En cas d'arrêt, une ligne est écrite dans `runs.jsonl` avec :
- `statut: arrete`, la raison et le détail ;
- les sections demandées et celles traitées ;
- les appels consommés (chat et embeddings) ;
- la durée de l'appel et la durée totale.

Ensuite, un nœud *Stop and Error* termine l'exécution. Une exécution complète porte désormais `statut: termine`.

**Tests par simulation** (trois variantes de même ID, aucun appel de chat, sorties supprimées) :

| Cas | Attendu | Obtenu |
|---|---|---|
| (a) premier appel en 503, puis 503 à la relance | arrêt `echec` | arrêt `echec`, ligne `arrete` avec 2 appels de chat et 4 d'embeddings ; aucun autre fichier |
| (b) premier appel de 3 s, seuil de 2 s | arrêt `delai` | arrêt `delai` (« 3 s, seuil : 2 s ») |
| (c) premier appel rapide, deuxième de 3 s, seuil de 2 s | pas d'arrêt | exécution complète, 5 appels, `statut: termine` |

**Défaut propre au test** : en (a), la durée affichée est de −58 s. La variante de test n'attend que 2 s avant la relance, alors que le calcul retire 60 s. Le vrai workflow attend bien 60 s, donc le calcul y est juste. C'est noté dans `pipeline.md` : la déduction n'est valable que tant que l'attente reste à 60 s.

## 3. Demain, 27/10 après 8 h (après ton feu vert)
Plan validé, inchangé :
1. Essai : technique, éthique, réglementaire, conclusion, puis relecteur. Cela fait 5 appels, 10 au plus. Les paramètres et la règle d'arrêt sont réglés.
2. Si la règle d'arrêt se déclenche, on réessaie dans l'heure.
3. Ma liste de défauts dans `outputs/defauts_reference_<run_id>.md`, écrite sans ouvrir `relecture_<run_id>.json`.
4. Validation de la liste par un membre du groupe (mardi soir), puis appariement : « X défauts confirmés repérés sur Y ».
5. Correctifs éventuels, sans toucher à G5. Les prompts ne changent qu'avec l'accord d'Adam. Rapport ici.

## Reste à faire du côté du groupe
Inchangé par rapport au rapport de 21 h 07 :
- valider la liste de défauts de référence mardi soir ;
- après le 28/10 : évaluation humaine par 2 membres, et vérification des références de la baseline ;
- captures des workflows pour le rapport ;
- facultatif : supprimer les brouillons « MOA » et « My workflow » dans n8n ;
- toujours ouvert : adresse *noreply* de GitHub pour les commits.
