# Défauts de référence — exécution `20261027-093507`
Liste établie par Claude (Claude Code) le 27/10/2026, **avant toute ouverture de `relecture_20261027-093507.json`**. Protocole : `pipeline.md` § 3.

- **Sources relues** : `argumentaire_20261027-093507.md` et le texte des chunks cités, tiré de `verif_20261027-093507.json`. Le jugement ne s'appuie que sur les extraits cités, comme pour le relecteur.
- **Types** : numéros de la grille du relecteur.
  1. structure ;
  2. contre-argument non traité ;
  3. sur-affirmation ;
  4. affirmation non soutenue par les chunks cités ;
  5. lien ou chronologie inventés entre sources ;
  6. équilibre ;
  7. conclusion.
- **Gravité proposée**, même échelle que le relecteur :
  - haute : non soutenu, lien inventé, erreur ;
  - moyenne : sur-affirmation, contre-argument non traité ;
  - basse : structure, équilibre, forme.
- **À remplir par un membre du groupe, sans avoir vu la sortie du relecteur** : colonne « Validation », avec `confirmé` ou `rejeté` (et un commentaire si besoin).

## A. Défauts de fond (30)

| N° | Section § | Affirmation (extrait) | Chunk(s) cité(s) | Défaut | Type | Gravité | Validation |
|---|---|---|---|---|---|---|---|
| A1 | contexte § 4 | « la fonction de notification d'hypertension sur Apple Watch ne prétend pas guider directement une thérapeutique » | D06-75f56bef, D06-a3309247, D07-c40316f9 | Aucun chunk cité ne décrit l'usage prévu. Ce sont D07 p. 7 et p. 9, non cités ici, qui le font | 4 | haute | confirmé |
| A2 | contexte § 4 | « Ce profil permet d'alerter utilement l'utilisateur sans générer un excès de faux positifs » | D07-c40316f9 | Aucun extrait n'évalue les faux positifs. La sensibilité de 41,2 % (la majorité des hypertensions non détectées) est donnée sans être discutée | 3 | moyenne | rejeté |
| A3 | enjeux_fda § 2 | « L'approbation par la FDA répond à l'enjeu de promouvoir la sensibilisation […]. Cette démarche vise à améliorer les taux de diagnostic » | D06-a7001751, D06-a3309247 | Le texte attribue à la FDA les arguments du livre blanc d'Apple (« specifically promotes awareness », « could improve diagnosis rates »). Le conditionnel devient un objectif | 5 | haute | confirmé |
| A4 | enjeux_fda § 4 | « confortant un rôle d'alerte complémentaire sans risque de substitution thérapeutique » | D07-b23884cb | « Sans risque » est une formulation absolue. La source dit seulement que l'outil n'est pas destiné à remplacer le diagnostic | 3 | moyenne | rejeté |
| A5 | technique § 1 | « L'analyse de la morphologie de l'onde […] permet de capter l'état physiologique des vaisseaux sanguins périphériques » | D09-393736c2 | La source dit « generally accepted […] can be **partially** expressed » | 3 | moyenne | rejeté |
| A6 | technique § 1 | « des réseaux de neurones […] ont atteint une erreur de ±9,82 mmHg […] et de ±3,88 mmHg » | D09-6db02069 | Le résultat d'une seule étude (Radha et al., 2018) est présenté comme général | 3 | moyenne | confirmé |
| A7 | technique § 2 | « la fonction autorisée par la FDA ne prétend pas remplacer la mesure conventionnelle ni afficher une pression continue instantanée » | D07-8c402bbb, D07-c40316f9, D06-172c7316 | Non soutenu par les chunks cités (l'usage prévu figure dans D07 p. 7, non cité) | 4 | haute | confirmé *(harmonisé le 28/10 ; initialement : rejeté)* |
| A8 | technique § 2 | « avec une comparaison rigoureuse à un tensiomètre à domicile autorisé par la FDA » | D07-c40316f9 | « Rigoureuse » n'est pas dans la source, qui dit seulement « as reference » | 3 | moyenne | rejeté |
| A9 | technique § 3 | « Pour répondre à ces exigences méthodologiques, l'évaluation clinique pivotale de la montre s'est déroulée de façon décentralisée sur 30 jours » | D12-cbb338ee, D07-8c402bbb, D07-c40316f9, D06-172c7316 | **Lien inventé** : l'étude d'Apple répondrait à la déclaration de l'AHA (2026, en ligne en déc. 2025), qui lui est postérieure (autorisation en sept. 2025) | 5 | haute | rejeté |
| A10 | technique § 3 | « permettant de valider l'efficacité de l'algorithme sur une durée prolongée et en vie réelle » | D06-172c7316, D07-c40316f9 | 30 jours deviennent une « durée prolongée ». L'étude mesure des performances (sensibilité, spécificité), pas une efficacité | 3 | moyenne | confirmé |
| A11 | technique § 4 | « Les résultats de l'étude clinique pivotale confirment la pertinence technique de l'outil au regard des consensus médicaux » | D07-c40316f9, D06-8dcda495, D07-8c402bbb | Jugement non soutenu : les extraits disent que les critères principaux ont été atteints. Le seul consensus du corpus sur le sans-brassard (AHA) est critique | 3 | moyenne | confirmé |
| A12 | technique § 4 | « réduisant drastiquement le risque d'alertes intempestives » | D06-8dcda495 | « Drastiquement » n'est pas soutenu | 3 | moyenne | rejeté |
| A13 | technique § 4 | « garantissant un repérage accru des profils nécessitant une prise en charge médicale prioritaire » | D06-8dcda495 | Sur-affirmation : une sensibilité de 41,2 % (53,7 % au stade 2) laisse la majorité des cas non détectés, ce qui n'est pas discuté | 3 | moyenne | rejeté |
| A14 | social_economique § 2 | « cet outil optimise l'investissement matériel consenti par l'utilisateur tout en élargissant les perspectives d'évaluation dans les communautés sous-dotées » | D06-a3309247, D06-a7001751, D12-62520587 | Non soutenu. L'objection de l'AHA (coût-efficacité « speculative ») n'est pas réfutée par les extraits | 4 | haute | confirmé |
| A15 | social_economique § 3 | « Néanmoins, la puissance de traitement des technologies portables et de l'informatique en nuage s'est considérablement accrue » | D09-396688b9, D12-5aedfb38 | Réponse hors sujet : l'objection porte sur l'absence de protocoles de validation standardisés, et la réponse sur la puissance de calcul (D09, 2019) | 2 | moyenne | confirmé |
| A16 | reglementaire § 1 | « repose sur un cadre réglementaire strict et clairement délimité » | D07-bccd84c8 | « Strict » n'est pas soutenu | 3 | moyenne | confirmé |
| A17 | reglementaire § 1 | « excluant tout ajustement thérapeutique direct non supervisé » | D07-bccd84c8 | Extrapolation de « for further diagnostic follow-up » | 3 | moyenne | rejeté |
| A18 | reglementaire § 2 | « Ce défi est directement pris en charge par le plan de contrôle des modifications prédéterminé (PCCP) » | D07-885a1648, D12-e54005ae | **Lien inventé** : la demande de transparence de l'AHA (déc. 2025) porte sur les entrées et la logique des algorithmes. Elle est présentée comme prise en charge par le PCCP (sept. 2025), qui encadre les modifications | 5 | haute | rejeté |
| A19 | reglementaire § 2 | « Ce dispositif réglementaire exclut tout algorithme adaptatif apprenant en continu » | D07-885a1648 | La source dit « does not include provisions for » | 3 | moyenne | rejeté |
| A20 | reglementaire § 2 | « une procédure formelle […] garantit la communication transparente des modifications […], assurant que le logiciel demeure aussi sûr et efficace » | D07-885a1648 | « Garantit » et « assurant » durcissent « a procedure has been established […] such that the modified device remains as safe and effective » | 3 | moyenne | confirmé |
| A21 | autres § 3 | « l'outil validé par la FDA ne prétend pas se substituer aux mesures conventionnelles pour poser un diagnostic formel ou guider directement le traitement » | D12-557c6126, D12-4794f2ff, D09-9f5b7b12, D06-a3309247, D06-75f56bef | Non soutenu par les chunks cités (usage prévu dans D07, non cité). « Validé » est employé pour une autorisation 510(k) | 4 | haute | confirmé *(harmonisé le 28/10 ; initialement : rejeté)* |
| A22 | conclusion § 1 | « demeure asymptomatique chez pres de la moitie d'entre eux » | D06-75f56bef | **Déformation** : la source dit « about half […] remain **unaware** of it » (ignorent leur état), pas asymptomatiques | 4 | haute | confirmé |
| A23 | conclusion § 1 | « represente une avancee majeure […] L'approbation reglementaire apparait donc pleinement justifiee » | D06-75f56bef, D06-a3309247, D07-b23884cb, D07-e5fd860e | Jugements non soutenus (« majeure », « pleinement ») | 3 | moyenne | confirmé |
| A24 | conclusion § 2 | « l'autorisation FDA circonscrit rigoureusement l'indication […] ecartant ainsi le risque d'une decision therapeutique autonome ou hasardeuse » | D07-b23884cb, D07-e5fd860e | Sur-affirmations : l'usage prévu n'écarte pas un risque, il le limite par l'étiquetage | 3 | moyenne | confirmé |
| A25 | conclusion § 3 | « les critiques pointant les limites de performance […] ou l'inadequation des protocoles de laboratoire ne s'appliquent pas aux donnees probantes fournies pour cette notification » | D12-1e0588da, D12-cbb338ee, D06-172c7316, D07-c40316f9 | **Lien inventé** : aucun extrait n'établit que les critiques de l'AHA ne s'appliquent pas. L'étude d'Apple évalue une classification sur 30 jours, pas le suivi des variations de pression | 5 | haute | confirmé |
| A26 | conclusion § 3 | « prevenant un afflux anxiogene de faux positifs » | D06-8dcda495, D07-c40316f9 | L'anxiété et l'« afflux » ne figurent dans aucun extrait | 4 | haute | rejeté |
| A27 | conclusion § 3 | « Sa sensibilite globale de 41,2 % […] garantit un ciblage pertinent des profils les plus severes » | D06-8dcda495, D07-c40316f9 | Sur-affirmation qui présente une faible sensibilité comme un atout | 3 | moyenne | rejeté |
| A28 | conclusion § 4 | « l'autorisation de la FDA offre un cadre de securite robuste, notamment grace a un plan de controle des modifications predetermine interdisant les algorithmes adaptatifs » | D07-885a1648 | « Robuste » et « interdisant » durcissent « does not include provisions for » | 3 | moyenne | rejeté |
| A29 | conclusion § 4 | « deja portee au quotidien par des millions de personnes » | D06-a3309247 | « Des millions » n'est pas dans la source (« so many people ») | 4 | haute | confirmé |
| A30 | conclusion § 4 | « cette fonctionnalite demontre son potentiel […] loin de constituer un substitut non eprouve, elle s'affirme comme une sentinelle opportuniste et precieuse » | D06-a3309247 | La source dit « could improve ». « Démontre », « s'affirme » et « précieuse » ne sont pas soutenus | 3 | moyenne | confirmé |

## B. Défauts de structure et de forme (4)

| N° | Section | Défaut | Cause | Type | Gravité | Validation |
|---|---|---|---|---|---|---|
| B1 | ethique, parcours_soins | Sections vides (signalées par G1) | 503 aux deux tentatives (API saturée) | 1 | basse | confirmé |
| B2 | enjeux_fda | 91 caractères corrompus (« fonctionnalit e9 ») ; les alertes G4 de la section en découlent (« nombres » 7, 0, 8, 9, 4) | Gemini a renvoyé `\u0000e9` au lieu de « é » dans sa réponse JSON | forme | basse | confirmé |
| B3 | conclusion | Texte entièrement sans accents | Sortie du modèle | forme | basse | confirmé |
| B4 | contexte § 4, technique § 4, autres §§ 1-2, conclusion § 3 | Redondance : les mêmes chiffres de l'étude d'Apple (2 229 / 1 863 participants, 92,3 %, 41,2 %…) et le même contexte épidémiologique reviennent dans 4 sections | Rédaction section par section | 6 | basse | confirmé |

## C. Défauts invisibles depuis les extraits (comptés à part)

| N° | Section § | Affirmation | Chunk | Défaut | Validation |
|---|---|---|---|---|---|
| C1 | reglementaire § 1 | « code produit QXO » | D07-bccd84c8 | Fidèle au chunk, mais périmé : SFR depuis la correction administrative du 12/09/2025, absente du corpus (`corpus.md` n° 7) | rejeté |
| C2 | conclusion § 2 | « (code produit QXO) » | D07-bccd84c8 | Idem | rejeté |

## Validation humaine (27/10/2026)
- Validation de chaque ligne par **Adam** (membre du groupe), le 27/10/2026, **sans avoir ouvert** `relecture_20261027-093507.json`. Matériel utilisé : la phrase dans son paragraphe et le texte brut des chunks cités, présentés par Claude (chat) **sans verdict**.
- **Résultat** : 15 défauts de fond confirmés sur 30 (A1, A3, A6, A10, A11, A14, A15, A16, A20, A22, A23, A24, A25, A29, A30), 4/4 défauts de forme confirmés, C1 et C2 rejetés.
- **Limite déclarée par le validateur** : jugement volontairement **indulgent** sur les cas limites, compte tenu du temps imparti (objectif : un pipeline fonctionnel, pas parfait). La liste confirmée est donc une **borne basse** des défauts réels : un cas douteux a été rejeté plutôt que confirmé.
- Les colonnes Type et Gravité n'ont pas été revues : elles restent celles proposées par Claude Code.

## Synthèse (avant validation)
- **Y proposé** : 30 défauts de fond et 4 de structure et de forme. Parmi les défauts de fond, 11 sont de gravité haute (A1, A3, A7, A9, A14, A18, A21, A22, A25, A26, A29), dont les 4 liens inventés. S'y ajoutent 2 défauts invisibles depuis les extraits.
- **Le lien inventé entre l'AHA et Apple ou la FDA** (type 5) apparaît 4 fois dans cette exécution : A3 (variante Apple → FDA), A9, A18 et A25. Avec les brouillons arrêtés, il est présent dans **toutes les sorties** depuis le 21/10. *Après validation : A3 et A25 confirmés, A9 et A18 rejetés à l'aveugle ; le problème du relecteur sur A9, trié après sa sortie, est classé fausse alerte (position finale d'Adam, 28/10) ; « toutes les sorties » repose sur les observations de Claude, non validées par le groupe.*
- **Ce que voient les garde-fous** :
  - G5 signale 5 paragraphes, et chacun contient un défaut de la liste (A13, A20, A24, A27, A28). Dans le paragraphe de A24, il signale aussi « prouve » dans « sans lien prouve », une **fausse alerte** : c'est une formule prudente, et sa négation (« sans lien ») échappe à la règle des formes niées ;
  - G5 ne voit pas « demontre » (A30), à cause de l'absence d'accents ;
  - G4 ne signale que la corruption de B2.

## Appariement avec le relecteur (27/10/2026, après la validation)
- `relecture_20261027-093507.json` a été ouvert **après** la validation humaine. Le relecteur (1 appel, 1 tentative, sans erreur) signale **3 problèmes** : 1 de gravité haute, 2 de gravité basse.
- Règle (`pipeline.md` § 3) : un défaut confirmé est repéré si le relecteur cite le même passage avec un problème de même nature. **Seuls les défauts confirmés comptent.**

| Problème signalé par le relecteur | Gravité | Défaut de la liste | Validation | Résultat |
|---|---|---|---|---|
| ethique : section absente, « appel Gemini en échec » (critère 1) | basse | B1 | confirmé | repéré |
| parcours_soins : même problème (critère 1) | basse | B1 | confirmé | repéré (même défaut) |
| technique : « Pour répondre à ces exigences méthodologiques, l'évaluation clinique pivotale […] » ; lien de cause à effet anachronique et non soutenu entre l'AHA (2026) et l'étude d'Apple (2025) (critères 4 et 5) | haute | A9 (même passage, même nature) | **rejeté** | non compté ; problème ajouté, trié : fausse alerte (position finale, 28/10) |

**Résultat : 1 défaut confirmé repéré sur 19** (B1).
- **Défauts de fond : 0 sur 15**, dont 0 sur les 6 de gravité haute (A1, A3, A14, A22, A25, A29). Par type : 0 sur 8 sur-affirmations, 0 sur 4 affirmations non soutenues, 0 sur 2 liens inventés (A3, A25), 0 sur 1 contre-argument non traité.
- **Structure et forme : 1 sur 4.** B2 (encodage) et B3 (texte sans accents) n'entrent dans aucun critère de la grille. Sur les seuls défauts couverts par la grille : 1 sur 17.
- **Problème ajouté par le relecteur, à trier par un humain** : celui de technique § 3. Il porte sur le passage de A9, avec la même nature (lien inventé, chronologie), alors que le validateur a rejeté A9 sans connaître la sortie du relecteur. Premier tri par Adam, le 27/10 : fausse alerte (réponse à une question de Claude, sans raison donnée) ; remplacé le 28/10 par « vrai défaut » (voir ci-dessous) ; **position finale d'Adam, le 28/10 : « fausse alerte », car il faut faire au plus simple.** Le score officiel reste 1 sur 19.
- **Biais possibles** :
  - le texte reçu par le relecteur contenait les 91 caractères NUL de enjeux_fda (B2) et une conclusion sans accents (B3) ;
  - le relecteur appartient à la même famille de modèles que le rédacteur ;
  - une seule exécution : pas de valeur statistique.

### Tri du problème ajouté par le relecteur (28/10/2026)
- **Problème du relecteur sur technique § 3 (passage de A9, lien anachronique AHA 2026 → étude d'Apple 2025)** : classé **vrai défaut** par Adam le 28/10/2026, **après avoir vu la sortie du relecteur**.
- Ce classement ne modifie pas la validation à l'aveugle (A9 reste « rejeté » dans le tableau) ni le **score officiel : 1 défaut confirmé repéré sur 19**.
- Bilan des problèmes ajoutés par le relecteur : 1 sur 1 jugé vrai défaut. La contradiction avec le rejet de A9 à l'aveugle illustre la **validation indulgente** déclarée en limite (`pipeline.md` § 5) : sur ce cas, le relecteur a vu un défaut que le validateur humain avait écarté.
- **Remplacé par la position finale d'Adam, le 28/10 : fausse alerte**, car il faut faire au plus simple (voir l'appariement ci-dessus).

### Harmonisation de la validation (28/10/2026)
Proposée par Claude (chat), **validée par Adam**, pour supprimer une incohérence de la validation à l'aveugle :
- **A1, A7 et A21** décrivent le même défaut (affirmation vraie, mais absente des chunks **cités** : l'usage prévu figure dans D07-b23884cb, non cité). A1 avait été confirmé, A7 et A21 rejetés. Règle appliquée aux trois : **on juge par rapport aux chunks cités** → A7 et A21 passent à **confirmé**.
- Nouveaux totaux : **17 défauts de fond confirmés sur 30** (au lieu de 15), dont **8 de gravité haute** (A1, A3, A7, A14, A21, A22, A25, A29) ; 4 de forme sur 4 ; **21 défauts confirmés au total**.
- **Appariement recalculé** : le relecteur ne repère ni A7 ni A21 → **1 défaut confirmé repéré sur 21** (au lieu de 1 sur 19), **0 sur 17** défauts de fond. Le problème ajouté sur A9 reste classé vrai défaut a posteriori, hors score.
- Les jugements initiaux restent visibles dans le tableau.

