# Consignes — 26/10/2026, 21 h · après le commit fde3378
Revue de ton rapport du 26/10 au soir. **À exécuter seulement après la validation explicite d'Adam.**

## 0. Nouvelle convention (boîte aux lettres)
Lis `echanges/README.md`. À partir de maintenant, à la fin de chaque étape, écris ton rapport dans `echanges/rapport.md` (résultats, questions, choix à valider avec options et recommandation), en plus de ta réponse dans le terminal. Ajoute cette convention au § 9 de `CLAUDE.md`.

## 1. Validations
- Relance explicite (429/5xx, une fois, 60 s, pas sur un délai dépassé) : **validée**. Bon réflexe d'avoir vérifié dans le code du moteur.
- En-tête `x-goog-api-key` : **on ne le fait pas**. Gain trop faible pour une clé stockée dans deux credentials. Ferme la question au § 6 de `CLAUDE.md`, avec la raison.
- Correction de ton erreur sur « continuer après erreur » : merci de l'avoir signalée.

## 2. Deux points de méthode, à écrire dans `pipeline.md` § 3 et § 5
**a. G5 a été calibré sur les sorties qu'il évalue.** Sa liste de termes a été construite à partir des défauts du 21/10 et du 26/10, puis testée sur ces mêmes sorties. Le « 6 sur 9, sans faux positif » n'est donc pas une mesure de sa performance : c'est du surajustement. Dans le rapport, seuls ses résultats sur l'**exécution finale** comptent, et la règle est : **plus aucune modification de la liste de G5 après aujourd'hui**. Ajoute cette limite au § 5.

**b. La « relecture manuelle » de référence est faite par toi, Claude, pas par un humain.** La comparaison avec le relecteur Gemini mesure donc l'accord entre deux LLM, pas la détection de défauts réels. Protocole corrigé pour la comparaison de demain :
1. tu relis les nouvelles sorties **avant** d'ouvrir `relecture_<run_id>.json` et tu écris ta liste de défauts dans `outputs/defauts_reference_<run_id>.md` (affirmation, chunk cité, défaut, type) ;
2. **un membre du groupe valide chaque défaut** de cette liste (confirmé / rejeté), toujours sans avoir vu la sortie du relecteur ;
3. ensuite seulement, l'appariement : « X défauts confirmés repérés par le relecteur sur Y », plus les problèmes ajoutés par le relecteur, triés en vrais défauts ou fausses alertes, par un humain.

Le cas QXO/SFR est compté à part, comme tu l'as proposé. Dans le rapport, il faudra écrire que la liste de référence a été produite avec l'aide d'un LLM puis validée par le groupe.

## 3. Échéance : le pipeline doit être prêt mercredi 28/10 après-midi
(Le rapport et l'oral viendront ensuite : l'échéance ne porte que sur le pipeline.)

**Ce soir (aucun appel de chat) :**
1. Points 0, 1 et 2 ci-dessus.
2. Étape 4 : `50-baseline` et `prompts/baseline_v1.md`, testés avec un appel simulé.
3. Étape 5 : `eval/evaluer.py` (métriques automatiques, tirage des 15 affirmations dans `outputs/eval_humaine.csv`, kappa), testé sur les sorties du 21/10 et du 26/10.

**Mardi 27/10 après 8 h, avec le feu vert d'Adam : essai (5 appels de chat)**
1. Technique, éthique, réglementaire, conclusion, puis relecteur (paramètres déjà réglés).
2. Règle d'arrêt : si le premier appel dépasse 3 minutes ou renvoie un 503 malgré la relance, on arrête et on réessaie dans l'heure.
3. Comparaison avec le relecteur selon le protocole du point 2b. La validation par le groupe peut se faire mardi soir.
4. Derniers correctifs **éventuels** du pipeline, sans toucher à la liste de G5 (point 2a). Tout correctif de prompt passe par une validation d'Adam.
5. Rapport dans `echanges/rapport.md`.

**Mercredi 28/10 après 8 h, avec le feu vert d'Adam : exécution finale officielle (quota entier)**
1. Toutes les sections, conclusion, relecteur, puis baseline (11 appels de chat ; marge de 9 pour les relances). Même règle d'arrêt.
2. `eval/evaluer.py` sur cette exécution.
3. **Gel** : plus aucune modification des prompts, de G5 ni des workflows. Les fichiers de cette exécution sont ceux du rapport.
4. Export des workflows, commit, et rapport final dans `echanges/rapport.md`. Liste ce qui reste à faire au groupe (évaluation humaine, vérification des références de la baseline).

Après chaque étape : commit, puis une ligne dans `implémentation.md`.
