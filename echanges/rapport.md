# Rapport — 28/10/2026, 15 h 08 · après le commit 02df689
Rapport de Claude Code : résultats de l'évaluation humaine, des alertes G5 et de la liste de défauts harmonisée, reportés dans les six fichiers.

## Résultats
**Évaluation humaine** (`20261028-095239`, 15 affirmations, un seul juge, pas de kappa). Le calcul est fait par un script ponctuel ; `eval/evaluer.py` n'est pas modifié.

| | SOUTENU | PARTIEL | NON_SOUTENU |
|---|---|---|---|
| Après harmonisation | **5 (33 %)** | **10 (67 %)** | **0** |
| Avant (valeurs initiales tracées) | 4 (27 %) | 8 (53 %) | 3 (20 %) |

| Section | SOUTENU | PARTIEL | NON_SOUTENU |
|---|---|---|---|
| contexte (2) | 1 | 1 | 0 |
| technique (2) | 2 | 0 | 0 |
| ethique (1) | 0 | 1 | 0 |
| social_economique (2) | 0 | 2 | 0 |
| parcours_soins (2) | 0 | 2 | 0 |
| autres (4) | 2 | 2 | 0 |
| conclusion (2) | 0 | 2 | 0 |

- Aucune affirmation n'a été tirée dans enjeux_fda ni dans reglementaire.
- Les sections ethique, social_economique, parcours_soins et conclusion n'ont que des PARTIEL (7 sur 7).

**G5** : 6 vraies alertes sur 8 (5 sur 8 avant harmonisation).

**Défauts de référence** (je les ai recomptés dans le tableau) :
- 17 défauts de fond confirmés sur 30, dont 8 de gravité haute (A1, A3, A7, A14, A21, A22, A25, A29) ;
- 21 défauts confirmés en tout.

**Relecteur** :
- 1 défaut repéré sur 21, et 0 sur les 17 défauts de fond ;
- par type : 0 sur 8 sur-affirmations, 0 sur 6 affirmations non soutenues, 0 sur 2 liens inventés, 0 sur 1 contre-argument ;
- 1 sur 19 parmi les défauts couverts par sa grille.

## Où c'est reporté
- **`pipeline.md`** :
  - au § 3, les résultats de l'évaluation humaine (avec le tableau par section), de G5 et du relecteur ;
  - au § 5, la limite, mot pour mot, dans une nouvelle ligne, ainsi que les 2 fausses alertes de G5 et le passage de 15 à 17 défauts.
- **CLAUDE.md** : une décision du 28/10 au § 5, puis le § 6 et la ligne 6 du § 8.
- **`implémentation.md`** : la critique (relecteur, G5, évaluation humaine, harmonisation) et le journal.
- **`oral.md`**, **`presentation.md`** et **`point_28-10.md`** : les chiffres, la limite, et les tâches faites retirées des listes « reste à faire ».

## Ajouts faits sans consigne explicite (à relire)
- **`presentation.md`, § 1 (texte à dire)** :
  - une phrase sur l'évaluation humaine : « sur quinze phrases tirées au hasard, notre juge n'en trouve que cinq entièrement soutenues… » ;
  - la limite de l'harmonisation, ajoutée au paragraphe « Les limites ».
- **Réponse à « Comment savez-vous que vos défauts de référence sont justes ? »**, dans `oral.md` et `presentation.md` : elle mentionne maintenant que A7 et A21 ont été changés après coup, sur proposition d'une IA.
- **`point_28-10.md`** :
  - total ramené à 15 à 19 h ;
  - partie A ramenée à environ 2 h restantes ;
  - « Ordre conseillé » mis à jour.

## À signaler, en attente de ton accord
1. **Contradiction sur A9.** La section « Harmonisation » de `defauts_reference_…` dit : « Le problème ajouté sur A9 **reste classé vrai défaut** a posteriori, hors score ». Or ta position finale du 28/10 est « fausse alerte ».
   - Je n'ai pas modifié cette ligne. Partout ailleurs, j'ai gardé « fausse alerte ».
   - **(a) Recommandé** : remplacer « vrai défaut » par « fausse alerte (position finale du 28/10) » dans cette ligne.
   - (b) Si ta position a changé, dis-le-moi : je mettrai à jour les 6 fichiers.
2. **Le résultat de l'appariement est périmé** dans le même fichier. Ma section affiche encore « **Résultat : 1 défaut confirmé repéré sur 19** ». Recommandé : ajouter « (recalculé le 28/10 : 1 sur 21, voir Harmonisation) ».
3. **`pipeline.md` § 3** (déjà signalé) : sous le titre « un seul juge, pas de kappa », deux puces parlent encore de « 2 membres du groupe » et du « kappa de Cohen ». Recommandé : les barrer ou les supprimer.

## Ma proposition G5 : comparaison
Le groupe a jugé les alertes G5, je peux donc montrer ma proposition (commit `71f917c`). Elle comptait **4 vraies alertes sur 8**.

| Alerte | Mon jugement (`71f917c`) | Jugement initial d'Adam | Jugement final d'Adam |
|---|---|---|---|
| G5-1 contexte § 3 | fausse | vraie | fausse |
| G5-2 contexte § 4 | fausse | vraie | vraie |
| G5-3 enjeux_fda § 4 | vraie | fausse | vraie |
| G5-4 ethique § 1 | vraie | vraie | vraie |
| G5-5 reglementaire § 1 | fausse | fausse | fausse |
| G5-6 reglementaire § 2 | vraie | fausse | vraie |
| G5-7 autres § 3 | fausse | vraie | vraie |
| G5-8 conclusion § 3 | vraie | vraie | vraie |

- **Accord avec moi** : 3 sur 8 avant l'harmonisation, 6 sur 8 après.
- **Les 3 changements vont tous dans le sens de ma proposition.** Ils ont été proposés par Claude (chat), et non par moi ; le fichier précise que ma proposition « n'a pas servi de base ». Les deux propositions viennent pourtant de la même famille de modèles.
- **Désaccords restants** : G5-2 et G5-7 (« a démontré » une sensibilité ou une spécificité). Je les avais classés comme simple compte rendu.
- **Même tendance pour la liste de défauts**, écrite par moi : A7 et A21 passent de « rejeté » à « confirmé ».
- Ces faits appuient la limite que tu as ajoutée (indépendance du jugement réduite). Je ne les ai écrits **dans aucun fichier du dépôt**. Je te propose d'ajouter une phrase à la ligne du § 5, par exemple : « les changements rapprochent les jugements des propositions de l'IA (G5 : accord de 3/8 à 6/8) ». À toi de décider.

## Reste à faire pour le groupe
1. Vérifier les 22 références de la baseline (`outputs/references_baseline.csv`).
2. Vérifier l'alerte G4 (« 510 », « 21 », « 870.2380 ») et le cas QXO / SFR (D07, p. 8).
3. Faire les captures des workflows.
4. Donner le point de vue du groupe sur la conclusion.
5. Rédiger le rapport et préparer l'oral.

Pas d'export n8n : aucun workflow n'a changé, et le pipeline est gelé.
