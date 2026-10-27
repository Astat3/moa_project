# Rapport — 27/10/2026, 10 h 35 · après le commit 3e96bd8
Rapport de Claude Code sur les consignes de 9 h 30 (exécution complète candidate).

## En bref
- **L'exécution complète est allée au bout**, mais **elle ne remplit pas le critère « sans défaut technique »**. Elle ne peut donc pas devenir l'exécution officielle : l'exécution finale de demain reste nécessaire. Trois défauts :
  - deux sections en échec G1 ;
  - un encodage corrompu dans une section ;
  - une conclusion entièrement écrite sans accents.
- La baseline est complète.
- **Le quota du jour est épuisé** : 20 appels de chat sur 20.
- **Ma liste de défauts de référence est prête**, écrite **sans ouvrir la relecture** : `outputs/defauts_reference_20261027-093507.md`. **À faire par un membre du groupe** : la valider ligne par ligne (confirmé ou rejeté), sans regarder `relecture_20261027-093507.json`. Ensuite seulement, je fais l'appariement (« X défauts confirmés repérés sur Y »).
- **4 choix à valider** pour l'exécution finale de demain (dernière section).

## Exécutions
| Exécution | Durée | Appels de chat | Résultat |
|---|---|---|---|
| 9 h 26, `20261027-092605` | 8 min | 2 | arrêt `delai` à 422 s : 503, puis relance réussie en 406 s. La mesure inclut le premier essai (16 s) |
| 9 h 35, `20261027-093507` | **47 min** | 14 (10 appels + 4 relances) | `termine` : 9 sections, conclusion, relecteur |
| 10 h 22, baseline `20261027-102233` | 5 min | 1 | 9 sections sur 9, 27 paragraphes, 22 références |

Avec les 3 appels de ce matin, cela fait **20 appels sur 20**.

**Latence** : de 142 à 494 s par appel réussi, contre 34 s le 21/10. **503** : 6 tentatives sur 16 pour l'argumentaire.

## Défauts techniques (exécution non éligible comme officielle)
1. **Éthique et parcours de soins** : 503 aux deux tentatives, sections vides, signalées par G1. C'est le comportement prévu, mais il manque deux sections imposées.
2. **Encodage dans « enjeux FDA »** : Gemini a renvoyé `\u0000e9` au lieu de « é » dans son JSON, alors qu'il a terminé normalement (`finishReason: STOP`).
   - Cela fait 91 caractères nuls, et un texte lisible mais corrompu (« fonctionnalit e9 »).
   - **G4 l'a repéré** : les « nombres » absents qu'il signale (7, 0, 8, 9, 4) viennent des codes `e7`, `e0`, `e8`, `e9`, `f4`.
   - Le défaut vient du modèle, pas de notre code (vérifié sur la réponse brute).
3. **Conclusion entièrement sans accents** (« fonctionnalite », « avancee »). C'est une sortie du modèle. Une conséquence : G5 ne voit plus « demontre ».

## Liste de défauts de référence (en attente de validation)
- **A. 30 défauts de fond**, dont 11 de gravité haute :
  - 9 affirmations non soutenues par les chunks cités, dont une déformation : « asymptomatique chez près de la moitié » pour « about half remain **unaware** » ;
  - 4 liens inventés ;
  - 16 sur-affirmations ;
  - 1 contre-argument mal traité.
- **B. 4 défauts de structure et de forme** : les deux sections vides, l'encodage, les accents, et la redondance des chiffres de l'étude d'Apple dans 4 sections.
- **C. 2 cas invisibles depuis les extraits**, comptés à part : « code produit QXO », deux fois.
- **Défaut systématique confirmé** : le lien inventé entre l'AHA et Apple ou la FDA apparaît **4 fois dans cette exécution** (A3, A9, A18, A25), et dans toutes les sorties depuis le 21/10.
- **G5** (résultat sur l'exécution évaluée, pas sur les sorties qui ont servi à le construire) :
  - 5 paragraphes signalés, chacun avec un vrai défaut ;
  - 1 fausse alerte : « sans lien prouve » ;
  - 1 défaut manqué à cause des accents : « demontre » ;
  - beaucoup de sur-affirmations hors de sa liste ne sont pas vues (« avancée majeure », « drastiquement », « strict »).

## Choix à valider pour l'exécution finale de demain (28/10 après 8 h)
1. **Encodage corrompu (`\u0000xx`)** :
   - **a. Réparation déterministe dans les garde-fous (recommandé).** La séquence nul + 2 chiffres hexadécimaux devient le caractère correspondant (`\u0000e9` → « é »). Le nombre de caractères réparés est noté dans `verif`, avec une alerte G1. C'est une correction d'encodage, pas de contenu.
   - b. Détection seule (alerte G1), sans réparation.
   - c. Rien.
2. **Texte sans accents** :
   - **a. Détection seule (recommandé)** : alerte G1 si un paragraphe de plus de 200 caractères ne contient aucune lettre accentuée. Le prompt ne change pas, conformément à la règle « `redacteur_v1` jusqu'au bout ».
   - b. Ajouter « écris avec les accents » au prompt (`redacteur_v2`). Mais c'est une modification du prompt la veille du gel.
   - c. Rien : le défaut est accepté comme une limite.
3. **503 persistants (2 sections perdues sur 10 aujourd'hui)** :
   - a. Garder une seule relance. Probabilité d'au moins une section perdue demain : environ 75 %, au taux de 503 d'aujourd'hui (37 % des tentatives).
   - **b. Seconde relance après 120 s, sur 429 ou 5xx seulement (recommandé, avec le point 4).** Environ 15 appels attendus pour l'argumentaire. La probabilité d'au moins une section perdue tombe à environ 40 %.
   - Le pire cas dépasse le quota. La règle d'arrêt sur le premier appel limite ce risque.
4. **Baseline** :
   - **a. Garder celle d'aujourd'hui (`20261027-102233`) comme baseline officielle (recommandé).** Même modèle, même prompt, 9 sections sur 9. Cela libère un appel pour les relances. Elle ne dépend pas de l'argumentaire.
   - b. La refaire demain, avec 1 appel de plus.

Si tu valides 1a, 2a et 3b, je les code et je les teste ce soir par simulation (aucun appel de chat) avant le gel.

## Prochaines étapes
1. **Groupe** : valider `outputs/defauts_reference_20261027-093507.md`, sans ouvrir la relecture.
2. **Moi** : appariement avec `relecture_20261027-093507.json`, puis « X défauts confirmés repérés sur Y » et le tri humain des problèmes ajoutés par le relecteur. Cette comparaison reste valable même si l'exécution n'est pas officielle : elle porte sur la capacité du relecteur.
3. **Demain après 8 h, avec ton feu vert** : contrôle de l'horloge, exécution finale, puis `eval/evaluer.py`, gel, export et rapport.
