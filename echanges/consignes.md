# Consignes — 27/10/2026, 9 h 30 · après le commit 02882a0
Revue du rapport de ce matin. **À exécuter seulement après la validation explicite d'Adam.**

## 1. Seuil : option A (420 s)
Tu as raison, mon seuil de 180 s était trop serré : un appel lent mais réussi ne coûte que du temps. On garde l'arrêt sur échec après relance, et le seuil passe à **420 s** pour l'essai et pour l'exécution finale. Note le changement dans `pipeline.md` et `implémentation.md`, avec la raison (latence de 4 à 5 min observée le 27/10, contre 34 s le 21/10).

## 2. Changement de plan : l'essai d'aujourd'hui devient une exécution candidate
L'API est instable et l'échéance est demain après-midi. Pour ne pas tout miser sur demain matin :
- **Lance aujourd'hui l'exécution complète** : toutes les sections, conclusion, relecteur, puis baseline (11 appels ; 3 déjà consommés, donc 14 sur 20, avec 6 de marge pour les relances).
- Si elle va au bout sans défaut technique (pas de section en échec G1, fichiers complets) **et** qu'Adam valide, **elle devient l'exécution officielle** : gel, `eval/evaluer.py`, export et commit. Demain matin ne sert alors que de filet de sécurité.
- Si elle révèle un bug à corriger, on corrige, puis on refait l'exécution finale demain après 8 h, comme prévu.
- Dans les deux cas, applique ensuite le protocole de comparaison avec le relecteur (ta liste de défauts **avant** d'ouvrir la relecture).

Contrôle de l'horloge (`chronyc makestep` si l'écart dépasse 5 s) avant de lancer : bonne trouvaille, garde-le systématique.

## 3. Pour la critique des résultats
Le lien inventé AHA → Apple à 4 sorties sur 4, y compris dans les brouillons arrêtés : c'est un défaut systématique du rédacteur, à présenter comme tel. Garde `brouillons_arretes_20261027.json` comme matière qualitative, hors métriques.

Rapport dans `echanges/rapport.md` à la fin.
