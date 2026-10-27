# Rapport — 27/10/2026, 9 h 18 · après le commit 4dd38f8
Rapport de Claude Code sur le point 3 des consignes (essai du 27/10).

## En bref
- **La règle d'arrêt s'est déclenchée deux fois**, à chaque fois parce que le premier appel était trop lent. Il n'y a donc **aucune sortie**, et la comparaison avec le relecteur n'a pas pu se faire.
- La règle a joué son rôle : chaque arrêt a coûté 1 ou 2 appels au lieu de 5 à 10, et a laissé une ligne `statut: arrete` dans `runs.jsonl`.
- **Quota du jour** : 3 appels de chat consommés sur 20, dont un 503.
- **Incident découvert : l'horloge de la VM Podman.** Il faut la contrôler avant chaque exécution, et surtout avant l'exécution finale de demain matin.
- **Décision à prendre : le seuil de la règle d'arrêt** (section « Choix à valider »).

## Les deux essais

| Essai | Premier appel (technique) | Durée réelle | Résultat |
|---|---|---|---|
| 1 (9 h 05) | 503, puis relance réussie | **≈ 308 s** (41 145 s affichées, voir ci-dessous) | arrêt `delai`, 2 appels |
| 2 (9 h 13), relance dans l'heure | réussi du premier coup | **241 s** | arrêt `delai`, 1 appel |

- **L'API est lente** : avec le même prompt (2 783 tokens en entrée, environ 4 300 en sortie et en réflexion), le premier appel avait pris 34 s le 21/10. Aujourd'hui il prend de 241 à 308 s, soit environ 8 fois plus lent. Le 26/10 au soir, il y avait déjà eu des 503 et un appel de 6 min 22 s : la lenteur dure depuis au moins 13 h.
- Après les deux arrêts, je n'ai pas relancé une troisième fois. La règle prévoit une relance dans l'heure, ce qui a été fait. Relancer encore, ou changer le seuil de 180 s validé, demande ton accord.

## Incident : horloge de la VM Podman
- **Constat** :
  - l'essai 1 affichait 41 145 s et un `run_id` daté du 26/10 à 21 h 44, alors qu'il a tourné le 27/10 de 9 h 05 à 9 h 11 ;
  - le journal de `chronyd` dans la VM indique « System clock wrong by 40836.9 seconds », puis « stepped » à 9 h 09 min 59 s ;
  - l'horloge de la VM s'est figée pendant la veille du Mac (11 h 20 de retard), puis a été recalée en plein appel.
- **Conséquence** : la durée et le `run_id` de l'essai 1 sont faux, mais l'arrêt était justifié (≈ 308 s, au-dessus du seuil). La ligne de `runs.jsonl` est laissée telle quelle et documentée dans `implémentation.md`.
- **Correctif de procédure**, dans `pipeline.md` § 4 et `CLAUDE.md` § 6 : avant chaque exécution, je mesure l'écart d'horloge entre l'hôte et le conteneur. S'il dépasse 5 s, je lance `podman machine ssh 'sudo chronyc makestep'` (testé : « 200 OK »). Pour l'essai 2, l'écart était de 0 s. **C'est indispensable demain matin**, après une nuit de veille.

## Ce qu'apprennent quand même les deux sections rédigées
Les sections « technique » ont été rédigées, mais pas écrites par le workflow. Je les ai extraites dans `outputs/brouillons_arretes_20261027.json` :
- **Les 8 mêmes chunks que le 21/10** : la récupération est déterministe, seule la rédaction varie.
- **Le lien inventé entre l'AHA et Apple revient dans les deux** : « Pour répondre à ces enjeux de validation, la fonctionnalité d'Apple a fait l'objet d'une étude… » et « Pour pallier ces limites méthodologiques, le protocole de validation clinique… ». Il est donc présent dans **4 sorties sur 4** (21/10, 26/10, 27/10 deux fois). La ligne correspondante du § 5 de `pipeline.md` est mise à jour.
- « Sur le long terme » revient aussi, pour une étude de 30 jours.
- G5 signale « démontré », « garantissant » et « garantit ».

Ce ne sont pas des sorties officielles : je les cite comme matière pour la critique (variabilité, défaut systématique), pas comme résultats.

## Choix à valider : que faire de la règle d'arrêt ?
La règle doit éviter de dépenser le quota sur une API défaillante. Or un appel lent mais réussi ne gaspille pas de quota : il prend seulement du temps. Ce sont les 503 qui gaspillent des appels.

- **A. Relever le seuil à 420 s (7 min) et relancer l'essai aujourd'hui (recommandé).**
  - On garde l'arrêt en cas d'échec après relance. Les appels réussis observés ont duré 241, 305 et 382 s.
  - Durée estimée de l'essai : 25 à 35 min (5 appels de 4 à 6 min, plus les pauses). Quota : 3 + 5 à 10 = 13 au plus sur 20.
  - Le même seuil servirait pour l'exécution finale de demain, qui durerait environ 1 h pour 11 appels.
- **B. Garder 180 s et réessayer plus tard** (en début d'après-midi ou ce soir). La lenteur dure depuis au moins 13 h, et chaque essai arrêté coûte 1 ou 2 appels. Si l'API reste lente, on n'aura pas d'essai avant l'exécution finale.
- **C. Supprimer le critère de durée** et ne garder que l'arrêt sur échec. Le délai de 600 s par appel reste la seule borne. C'est plus simple, mais on ne sait plus quand l'API est anormalement lente.

Avec A ou C, je relance l'essai dès ton accord, toujours après le contrôle d'horloge. Puis j'applique le protocole de comparaison : ma liste de défauts sans ouvrir la relecture, la validation par le groupe ce soir, et l'appariement.
