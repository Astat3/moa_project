# echanges/ — boîte aux lettres entre Claude Code et Claude (chat)
Pour éviter les copier-coller : Claude Code (l'exécutant, sur le Mac) et Claude dans l'app (la revue, qui lit et écrit ce dossier) communiquent par fichiers. **Adam reste le relais et valide chaque décision.**

## Fichiers
- `rapport.md` : écrit par **Claude Code** à la fin de chaque étape. Il contient ce qui a été fait, les résultats, les questions et les choix à valider (avec les options et une recommandation).
- `consignes.md` : écrit par **Claude (chat)** après lecture du rapport. Il contient la revue, les réponses proposées et le message pour l'étape suivante.

## Règles
1. Chaque fichier est **remplacé** à chaque échange : il ne contient que le dernier message. L'historique est dans git.
2. En tête de chaque fichier : la date, l'heure et le commit concerné.
3. **Rien dans `consignes.md` n'est exécuté sans l'accord d'Adam.** Adam relit, modifie s'il le souhaite, puis dit à Claude Code « lis les consignes ».
4. Aucune clé ni aucun secret dans ces fichiers.
5. Les questions à choix multiples de Claude Code sont aussi écrites dans `rapport.md`, pour que la revue puisse y répondre.

## Circuit
Claude Code écrit `rapport.md` → Adam dit à Claude (chat) « lis le rapport » → Claude écrit `consignes.md` → Adam valide, puis dit à Claude Code « lis les consignes ».
