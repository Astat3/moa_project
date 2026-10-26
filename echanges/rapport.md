# Rapport — 26/10/2026, 21 h 07 · après le commit 98ed986
Rapport de Claude Code sur les consignes du 26/10 (points 0, 1, 2 et partie « Ce soir » du point 3).

## En bref
- Fait : points 0 à 2, étape 4 (`50-baseline`) et étape 5 (`eval/evaluer.py`).
- **Aucun appel de chat ce soir** : tout a été testé avec des appels simulés. Environ 25 requêtes d'embeddings ont été consommées, sur 1 000 par jour.
- Commits :
  - `f0cc5d5` : points 0 à 2 ;
  - `bbe11f9` : étape 4 ;
  - `98ed986` : étape 5 ;
  - un dernier commit pour ce rapport et `CLAUDE.md` § 8.
- Rien n'est poussé. Rien n'est lancé avant ton feu vert demain après 8 h.
- **Une question à trancher avant l'essai de demain** : comment appliquer la règle d'arrêt (dernière section).

## Points 0 à 2
- **Boîte aux lettres** : la convention est au § 9 de `CLAUDE.md`. `echanges/README.md` et `consignes.md` sont versionnés.
- **En-tête `x-goog-api-key`** : non retenu, question fermée au § 6 avec la raison.
- **2a, G5** : la liste est gelée depuis le 26/10.
  - Le surajustement est expliqué au § 3 de `pipeline.md`, avec une ligne au § 5.
  - La phrase « il en repère 7 » de la critique des résultats a été corrigée dans le même sens.
- **2b, protocole corrigé** (`pipeline.md` § 3) :
  1. ma liste de défauts dans `outputs/defauts_reference_<run_id>.md` ;
  2. validation de chaque défaut par un membre du groupe, sans voir la sortie du relecteur ;
  3. appariement ;
  4. tri humain des problèmes ajoutés par le relecteur.

  La limite « liste produite avec l'aide d'un LLM, puis validée par le groupe » est au § 5.

## Étape 4 : `50-baseline` (11 nœuds) et `prompts/baseline_v1.md`
**Chaîne** : Paramètres (les 9 sections par défaut) → prompt → un appel `generateContent` → assemblage.

**Sorties** :
- `baseline_<run_id>.md`, avec les références marquées « non vérifiées » ;
- `baseline_<run_id>.json`, la sortie brute, pour l'évaluation ;
- une ligne dans `runs.jsonl`.

**Test simulé** : un 503, puis une relance après 60 s, puis un succès. Le Markdown signale les sections absentes, et une section hors liste est repérée.

**Choix faits, à valider** (tous réversibles) :
1. **Même relance unique que le pipeline** (429 ou 5xx, 60 s). Sans elle, un 503 le 28/10 ferait perdre la baseline.
2. **Mode JSON avec schéma** : sections → paragraphes `{texte, references: [n]}`, plus une liste `references`. C'est la même contrainte de format que pour le rédacteur, et elle permet de compter automatiquement.
3. **Le prompt interdit d'inventer des références**, comme `redacteur_v1` interdit d'inventer des `chunk_id`. La comparaison est plus équitable : si la baseline en invente malgré la consigne, le résultat n'en est que plus fort.
4. **Mêmes règles que `redacteur_v1`, sauf celles qui dépendent du corpus** :
   - chiffres exacts ;
   - `[INFORMATION NON DISPONIBLE]` ;
   - objections présentées puis réfutées ;
   - pas de formulation absolue ;
   - 3 à 6 paragraphes de 60 à 150 mots.

## Étape 5 : `eval/evaluer.py` (bibliothèque standard de Python seulement)
**Métriques** : `python3 eval/evaluer.py metriques <run pipeline> [<run baseline>]`.
- Écrit `metriques.csv`, avec les 7 métriques du § 3.
- Crée une seule fois, **sans jamais les écraser**, les fichiers à remplir à la main :
  - `eval_humaine_juge1.csv` et `eval_humaine_juge2.csv` ;
  - `references_baseline.csv` (pour chaque référence : existe, correcte, commentaire).

**Kappa** : `python3 eval/evaluer.py kappa <juge1.csv> <juge2.csv>`. Donne l'accord observé, le kappa et la matrice de confusion, aussi écrits dans `kappa.txt`.

**Tests** :
- sur les sorties du 21/10 (15 affirmations sur 16) et du 26/10 (2 sections en échec G1 bien comptées) ;
- sur une exécution simulée : pipeline + relecteur + baseline, une relance comptée de chaque côté ;
- **kappa vérifié sur un exemple calculé à la main** (accord 70 %, hasard 38 %, κ = 0,516) ;
- un jugement invalide est refusé.

**Choix faits, à valider** :
1. **Affirmation = une phrase** (6 mots au moins) d'un paragraphe qui cite au moins un chunk. Elle est jugée par rapport aux chunks cités par **son paragraphe**, puisque les citations sont données par paragraphe et non par phrase. Tirage reproductible, avec le `run_id` pour graine.
2. **Deux fichiers, un par évaluateur**, au lieu d'un seul `eval_humaine.csv`. Ainsi, chaque évaluateur juge sans voir les réponses de l'autre.
3. **Définition des jugements** :
   - `SOUTENU` : appuyée par les extraits ;
   - `PARTIEL` : en partie seulement, **ou formulée plus fort que la source** ;
   - `NON_SOUTENU` : absente ou contredite.
4. **`verif_<run_id>.json` garde désormais le texte des chunks** (une ligne de l'assemblage de `10-argumentaire` modifiée). C'est nécessaire pour l'évaluation humaine. Les sorties du 21/10 et du 26/10 n'ont pas ce texte, et le CSV le signale.

À savoir : les alertes ne sont pas recalculées. L'exécution du 21/10, antérieure à G5, affiche donc « G5 : 0 ».

## Question à trancher avant l'essai : comment appliquer la règle d'arrêt ?
« Si le premier appel dépasse 3 min ou renvoie un 503 malgré la relance, on arrête. » Le problème : `n8n execute` n'affiche rien avant la fin de l'exécution, donc je ne vois pas quand le premier appel se termine.

- **A. Règle dans le workflow (recommandé).** Le nœud des garde-fous mesure le premier appel de l'exécution, à partir d'un horodatage posé par le prompt, sans compter l'attente de relance. Si l'appel dépasse 3 min, ou s'il échoue après la relance, le nœud lève une erreur et l'exécution s'arrête sans fichier. Environ 6 lignes, testables ce soir ou demain par simulation, sans appel de chat. Avantage : la règle est déterministe et documentée dans le pipeline. Elle servira aussi le 28/10.
- **B. Surveillance à la main** à partir des journaux de débogage de n8n (lignes « Running node … finished »), puis arrêt du processus. Aucune modification du workflow. Mais le journal de débogage peut contenir des détails de requête, ce qui oblige à le filtrer, et l'arrêt est moins net.
- **C. Pas d'arrêt automatique** : on attend la fin (600 s au plus par appel) et on juge après coup. Le plus simple, mais un essai lent consomme quand même ses 5 appels.

## Plan de demain, 27/10 après 8 h (avec ton feu vert)
1. Essai : technique, éthique, réglementaire, conclusion, puis relecteur. Cela fait 5 appels, 10 au plus avec les relances. Les paramètres sont réglés.
2. Règle d'arrêt selon ta réponse ci-dessus.
3. Ma liste de défauts dans `outputs/defauts_reference_<run_id>.md`, écrite **sans ouvrir** `relecture_<run_id>.json`. Le résumé d'exécution n'affichera pas son contenu.
4. Validation de la liste par un membre du groupe (mardi soir), puis appariement : « X défauts confirmés repérés sur Y ».
5. Correctifs éventuels, sans toucher à G5. Les prompts ne changent qu'avec ton accord. Rapport ici.

## Reste à faire du côté du groupe
- Mardi soir : valider la liste de défauts de référence.
- Après l'exécution finale du 28/10 :
  - évaluation humaine par 2 membres (`eval_humaine_juge1.csv` et `eval_humaine_juge2.csv`, environ 45 min) ;
  - vérification des références de la baseline (`references_baseline.csv`).
- Captures de `00-ingestion`, `10-argumentaire` et `50-baseline` pour le rapport.
- Facultatif : supprimer les brouillons « MOA » et « My workflow » dans n8n.
- Toujours ouvert : adresse *noreply* de GitHub pour les commits.
