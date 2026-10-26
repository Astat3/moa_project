# Prompt de la baseline — v1

Tu rédiges un argumentaire scientifique en français, destiné à des médecins, sur l'autorisation par la FDA de la fonction de notification d'hypertension de l'Apple Watch.

Position défendue : {{POSITION}} l'autorisation FDA.

## Structure imposée
Rédige toutes les sections suivantes, dans cet ordre (identifiant : titre. Points à couvrir) :
{{SECTIONS}}

## Règles
1. Appuie-toi sur tes connaissances : tu n'as accès à aucun document.
2. Cite tes sources. Chaque affirmation factuelle (chiffre, résultat d'étude, position d'une institution, fait réglementaire) renvoie à au moins une référence, par son numéro, dans la liste `references` de son paragraphe.
3. Donne chaque référence complète dans la liste `references` du document : auteurs, titre, revue ou éditeur, année, et DOI ou URL si tu les connais. Une même référence garde le même numéro dans tout le texte. Ne cite que des références dont tu es sûr qu'elles existent : n'en invente aucune.
4. N'écris jamais de numéro de référence dans le texte des paragraphes : les numéros vont uniquement dans `references`.
5. Reprends les chiffres exactement comme dans la source (même valeur, même unité), en notation française (virgule décimale).
6. Si tu n'as pas d'information fiable sur un point à couvrir, écris un paragraphe qui contient seulement `[INFORMATION NON DISPONIBLE]` suivi du point concerné, avec une liste `references` vide.
7. Défends la position {{POSITION}}, mais présente honnêtement les principales objections, puis réponds-y.
8. Pas de formulation absolue (« prouve », « toujours », « aucun risque ») ni de lien de causalité non démontré.
9. Entre 3 et 6 paragraphes de 60 à 150 mots par section. La conclusion prend un parti pris clair.

## Format de sortie
Uniquement du JSON :
{"sections": [{"id": "<identifiant>", "paragraphes": [{"texte": "...", "references": [1]}]}], "references": [{"numero": 1, "reference": "..."}]}
