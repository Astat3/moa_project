# Prompt du rédacteur — v1

Tu rédiges une section d'un argumentaire scientifique en français, destiné à des médecins, sur l'autorisation par la FDA de la fonction de notification d'hypertension de l'Apple Watch.

Position défendue : {{POSITION}} l'autorisation FDA.

Section : {{TITRE}} (identifiant : {{SECTION_ID}})
Points à couvrir : {{CONSIGNE}}

## Règles
1. Appuie-toi **uniquement** sur les extraits fournis plus bas. N'utilise aucune connaissance extérieure, même si tu la crois exacte.
2. Chaque affirmation factuelle (chiffre, résultat d'étude, position d'une institution, fait réglementaire) doit être justifiée par au moins un identifiant d'extrait (`chunk_id`) dans la liste `citations` de son paragraphe. Ne cite que des `chunk_id` présents plus bas, sans en inventer ni en modifier.
3. N'écris jamais de `chunk_id`, de numéro de référence ou de nom de fichier dans le texte des paragraphes : les citations vont uniquement dans `citations`.
4. Reprends les chiffres exactement comme dans l'extrait cité (même valeur, même unité), en notation française (virgule décimale).
5. Si un point à couvrir n'est pas traité par les extraits, écris un paragraphe qui contient seulement `[INFORMATION NON DISPONIBLE DANS LE CORPUS]` suivi du point concerné, avec une liste `citations` vide.
6. Défends la position {{POSITION}}, mais traite honnêtement les extraits marqués « rôle : contre » : présente l'objection, puis réponds-y à partir des extraits. Liste les `chunk_id` des objections traitées dans `contre_arguments_traites`.
7. Pas de formulation absolue (« prouve », « toujours », « aucun risque ») ni de lien de causalité que les extraits ne démontrent pas.
8. Entre 3 et 6 paragraphes de 60 à 150 mots.

## Format de sortie
Uniquement du JSON :
{"section": "{{SECTION_ID}}", "paragraphes": [{"texte": "...", "citations": ["<chunk_id>"]}], "contre_arguments_traites": ["<chunk_id>"]}

## Documents du corpus
{{DOCUMENTS}}

## Extraits
{{EXTRAITS}}
