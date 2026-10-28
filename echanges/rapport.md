# Rapport — 28/10/2026, 11 h 20 · après le commit 71f917c
Rapport de Claude Code : décisions d'Adam sur l'exécution finale (`20261028-095239`) et sur A9.

## Fait
- **A9, position finale : fausse alerte**, « car il faut faire au plus simple ». Elle est notée à côté de la trace des tris précédents (27/10 : fausse alerte ; 28/10 : vrai défaut), dans le tableau de l'appariement et sous ta section du 28/10, que je n'ai pas modifiée.
  - Elle est reportée dans `pipeline.md` § 5, la critique de `implémentation.md`, CLAUDE.md et `oral.md`.
  - Le score officiel reste 1/19.
- **Exécution finale gardée sans relecteur.** L'échec est compté comme un résultat, et le relecteur reste évalué sur l'exécution 1. Où c'est noté :
  - `pipeline.md` § 4 ;
  - une nouvelle limite au § 5 : un seul appel sur tout l'argumentaire, environ 15 000 tokens, pas de relance sur délai ;
  - la critique ;
  - CLAUDE.md (§ 5 et § 6).
- **A3** : la précision « variante livre blanc d'Apple → FDA » est ajoutée au § 5 et au point 3 du § 5 de `oral.md`.
- **`oral.md`** :
  - latence du 28/10 au § 6 ;
  - échec du relecteur dans la réponse « Pourquoi le relecteur échoue-t-il ? » ;
  - au § 4, le contraste `[INFORMATION NON DISPONIBLE]` : pipeline 3, baseline 0. La baseline a la même règle mais traite HIPAA, le marquage CE / MDR et le RGPD de mémoire.

## Alignements faits sans consigne explicite (à relire)
Ta position finale rendait fausses trois phrases de `oral.md`. Je les ai alignées :
- § 4 : « classé vrai défaut a posteriori… c'est le relecteur qui a vu juste » devient « trié après sa sortie : fausse alerte (position finale) » ;
- § 5, point 3 : « le relecteur l'a repéré une fois (A9) » devient « le relecteur ne repère ni A3 ni A25 » ;
- § 6 : « le relecteur n'en repère qu'un (A9…) » devient « aucun parmi les défauts confirmés ».

## Proposition G5
- Elle a été retirée de ce rapport. Elle reste dans la version précédente (commit `71f917c`) et dans ma réponse précédente dans le terminal. Je n'ai pas réécrit l'historique git.
- **Tu en as vu le résumé** : « 4 justes, 4 fausses alertes, toutes dues à “démontrer” ». Je recommande donc que les 8 alertes soient jugées par **un autre membre du groupe**, qui n'ouvre pas cette version.
- Je la ressortirai pour la comparaison une fois le jugement fait.

**Les 8 paragraphes à juger** (vrai défaut ou fausse alerte), sans proposition :

| Paragraphe | Terme(s) signalé(s) |
|---|---|
| contexte § 3 | « démontrés » |
| contexte § 4 | « démontré » |
| enjeux_fda § 4 | « garantissant » |
| ethique § 1 | « solide » |
| reglementaire § 1 | « démontré » |
| reglementaire § 2 | « rigoureusement » |
| autres § 3 | « démontré » |
| conclusion § 3 | « solides », « garantit » |

Le texte complet est dans `outputs/argumentaire_20261028-095239.md` : ce sont les paragraphes marqués ⚠.

## Question
**L'exemple du lien inventé dans `oral.md`** (§ 5, point 3) cite le passage de **A9** (« Pour répondre à ces exigences méthodologiques… »). Or A9 a été rejeté à l'aveugle, puis le problème du relecteur sur ce passage a été classé fausse alerte. L'oral illustrerait donc un défaut avec un passage que le groupe n'a pas retenu.
- **(a) Recommandé.** Remplacer la citation par celle de **A25**, confirmé à l'aveugle : « les critiques pointant les limites de performance […] ou l'inadequation des protocoles de laboratoire ne s'appliquent pas aux donnees probantes fournies pour cette notification » (conclusion du 27/10, écrite sans accents par le modèle).
- (b) Garder A9 et le présenter comme un cas limite, sur lequel l'humain et le relecteur ne s'accordent pas.
- (c) Ne rien changer.

## Reste à faire pour le groupe
1. **Évaluation humaine** : deux juges, `outputs/eval_humaine_juge1.csv` et `juge2.csv`, environ 45 min. Ensuite, `python3 eval/evaluer.py kappa outputs/eval_humaine_juge1.csv outputs/eval_humaine_juge2.csv`.
2. **Références de la baseline** : les 22 de `outputs/references_baseline.csv`.
3. **Les 8 alertes G5** ci-dessus, de préférence par un membre qui n'a pas vu ma proposition.
4. Point de vue sur la conclusion, cas QXO / SFR (D07 p. 8), captures des workflows.
