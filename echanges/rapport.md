# Rapport — 28/10/2026, 10 h 56 · après le commit 551f85f
Rapport de Claude Code : exécution finale officielle, métriques, puis consignes d'Adam du 28/10.

## En bref
- **Exécution finale `20261028-095239`, terminée sans erreur** :
  - lancée à 9 h 52 et non à 8 h, après resynchronisation de l'horloge ;
  - durée de 59 min, 11 appels de chat dont 1 relance ;
  - **9 sections sur 9**, aucun caractère corrompu, aucune alerte G1.
- **Le relecteur a échoué** : l'appel a atteint le délai de 600 s. Selon la règle du 26/10, un délai dépassé n'est pas relancé. **Décision attendue (Q1).**
- Ce qui est fait :
  - métriques calculées avec la baseline `20261027-102233` ;
  - export des workflows (aucun changement) et commit `a3de789` ;
  - consignes du 28/10 appliquées (commits `94e60eb` et `551f85f`).

## 1. Horloge
La VM retardait de **13 h 26**. `chronyc makestep` n'a eu aucun effet, car chrony n'avait plus de source utilisable après un saut aussi grand. J'ai redémarré chronyd et attendu la synchronisation : l'écart est revenu à 0 s. La procédure est maintenant dans CLAUDE.md (§ 6).

## 2. Exécution finale
| Section | Tentatives | Durée de l'appel | Paragraphes | Signalés | Garde-fous |
|---|---|---|---|---|---|
| contexte | 1 | 340 s | 4 | 2 | G5 |
| enjeux_fda | 1 | 292 s | 4 | 1 | G5 |
| technique | 1 | 240 s | 4 | 0 | — |
| ethique | 1 | 227 s | 3 | 1 | G5 |
| social_economique | 2 | 503 en 23 s, puis 362 s | 3 | 0 | — |
| reglementaire | 1 | 305 s | 5, dont 3 `[INFORMATION NON DISPONIBLE]` (HIPAA, CE / MDR, RGPD) | 2 | G4, G5 |
| parcours_soins | 1 | 281 s | 3 | 0 | — |
| autres | 1 | 91 s | 4 | 1 | G5 |
| conclusion | 1 | 586 s | 4 | 1 | G5 |
| relecteur | 1 | **600 s, délai dépassé** | — | — | — |

### Pipeline contre baseline (`outputs/metriques.csv`)
| Métrique | Pipeline | Baseline |
|---|---|---|
| Sections imposées présentes | 9 / 9 | 9 / 9 |
| Références | 4 documents, exactes par construction | 22, à vérifier |
| Paragraphes cités | 31 / 31 | 27 / 27 |
| `[INFORMATION NON DISPONIBLE]` | 3 / 34 | 0 / 27 (la règle figure dans son prompt) |
| Paragraphes signalés | 8 / 34 (G5 : 8, G4 : 1) | sans objet |
| Appels, durée | 11, 3 554 s | 1, 293 s |

Les fichiers de l'évaluation humaine sont créés : `eval_humaine_juge1.csv`, `eval_humaine_juge2.csv` (15 affirmations tirées sur 115) et `references_baseline.csv`.

### Alertes G5 : proposition de Claude, à valider par un membre du groupe
G5 n'est évalué que sur cette exécution. Il faut donc juger chaque alerte. Voici ma proposition :

| Paragraphe | Terme | Proposition |
|---|---|---|
| contexte § 3 | « n'a pas encore été corrélé à des résultats cliniques **démontrés** » | fausse alerte : formule prudente, la négation est trop loin du terme |
| contexte § 4 | « le dispositif a **démontré** une sensibilité globale de 41,2 % » | fausse alerte : simple compte rendu d'un résultat |
| enjeux_fda § 4 | « **garantissant** ainsi un positionnement adapté » | vraie sur-affirmation |
| ethique § 1 | « justification éthique **solide** » | vraie sur-affirmation |
| reglementaire § 1 | « a **démontré** son équivalence substantielle » | fausse alerte : vocabulaire réglementaire du 510(k) |
| reglementaire § 2 | « restreint **rigoureusement** la finalité » | vraie sur-affirmation |
| autres § 3 | « L'étude a **démontré** une spécificité globale de 92,3 % » | fausse alerte : compte rendu |
| conclusion § 3 | « données cliniques **solides** », « **garantit** un verrouillage strict » | vraies sur-affirmations |

Si ces propositions sont validées : **4 paragraphes bien signalés sur 8**. Les 4 fausses alertes viennent toutes de « démontrer » employé pour rendre compte d'un résultat ; c'est la limite déjà notée au § 5.

**G4** (réglementaire § 1) : « 510 », « 21 » et « 870.2380 » sont absents du chunk cité. Ils figurent dans la bibliographie, que le code génère. Il faut vérifier s'ils se trouvent dans un autre chunk de D07.

### Observations de Claude sur le texte (non validées)
- **Lien AHA → FDA**, toujours présent. Le § 5 reste donc exact, au sens de « observé par Claude » :
  - « le cadre validé par la FDA **répond directement à ces préoccupations** » (réglementaire § 2) ;
  - « le cadre rigoureux de l'autorisation de la FDA **dissipe ces craintes** » (conclusion § 2) ;
  - forme plus faible : « Pour apporter les preuves de fiabilité requises » (technique § 4, juste après le paragraphe sur l'AHA).
- **Technique § 2** : la phrase « ce qui justifie leur rôle d'outil de repérage et de notification » est attribuée à l'AHA. Le chunk cité dit-il cela ? À vérifier.
- **Code produit QXO**, avec le « prédicat Viz HCM », revient en réglementaire § 1.

## 3. Consignes du 28/10
- **A9 = vrai défaut**, comme tu l'as noté. Hier, à ma question, tu avais répondu « fausse alerte ». J'ai donc aligné mes mentions de « fausse alerte » sur « vrai défaut » : tableau et tri de l'appariement, implémentation.md et CLAUDE.md. J'ai gardé la trace du premier tri. Le score officiel reste 1/19.
- **§ 5** : ta formulation est reprise mot pour mot, et alignée dans la critique de implémentation.md et dans la synthèse de la liste de défauts. La critique contenait déjà le résultat 1/19 (0/15 sur le fond) depuis hier ; je n'ai mis à jour que la mention de A9.
- **oral.md** : commité avec le fichier des défauts (`94e60eb`), puis complété (`551f85f`).
  - Sections remplies : la ligne du 28/10 au § 2, l'exécution finale et le tableau comparatif au § 4, les chiffres au § 8, la liste du § 9.
  - Laissés en ⏳ : évaluation humaine, kappa, références de la baseline, point de vue sur la conclusion, QXO / SFR et captures.
- **CLAUDE.md** : procédure de l'horloge ajoutée, et sections 6 et 8 mises à jour.

## 4. Questions

### Q1. Le relecteur de l'exécution finale
- **(a) Recommandé.** On garde l'exécution telle quelle. Le relecteur n'est évalué que sur l'exécution 1 (1/19), comme prévu. Son échec par dépassement de délai devient un résultat de plus pour la critique : avec l'offre gratuite, un contrôle de 15 000 tokens n'aboutit pas toujours. Coût nul, aucun changement de code.
- (b) Relancer **le relecteur seul** aujourd'hui, sur l'argumentaire final. Il reste environ 9 appels sur 20. Il faudrait un workflow temporaire qui reconstruit son entrée depuis `verif`, donc du nouveau code après le gel, à valider. Et le délai peut de nouveau être dépassé : la conclusion a déjà pris 586 s.
- (c) Augmenter le délai et tout relancer : impossible, à cause du quota et du gel.

### Q2. A3 dans la ligne du § 5
La ligne parle du lien inventé **AHA → Apple ou FDA**. Or A3 est l'autre variante : le livre blanc d'Apple attribué à la FDA.
- **(a) Recommandé.** Ajouter « (A3 : variante livre blanc d'Apple → FDA) », au § 5 et au point 3 du § 5 de `oral.md`.
- (b) Laisser tel quel.

### Q3. Compléments possibles de `oral.md` (sections sans ⏳, non modifiées)
- § 6, latence : ajouter « 28/10 : de 23 s à 10 min, relecteur au-delà de 10 min ».
- § 7, « Pourquoi le relecteur échoue-t-il ? » : ajouter le dépassement de délai de l'exécution finale.

## 5. Reste à faire pour le groupe
1. **Évaluation humaine** : deux membres, sans se concerter, remplissent `outputs/eval_humaine_juge1.csv` et `juge2.csv`. Compter environ 45 min. Ensuite, `python3 eval/evaluer.py kappa outputs/eval_humaine_juge1.csv outputs/eval_humaine_juge2.csv`.
2. **Références de la baseline** : vérifier les 22 références dans `outputs/references_baseline.csv` (existe ? correcte ?), avec PubMed ou Europe PMC.
3. **G5** : valider ou corriger les 8 propositions ci-dessus.
4. **Point de vue du groupe** sur la conclusion de l'IA, cas QXO / SFR (D07 p. 8), captures des workflows.
