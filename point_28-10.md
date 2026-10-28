# Point d'étape — 28/10/2026 : pipeline terminé
Ce qu'on peut présenter aujourd'hui, et le travail restant avant l'évaluation finale de la semaine prochaine.
Détail : `oral.md` (support complet), `pipeline.md` § 5 (limites), `outputs/metriques.csv` (chiffres).

---

## 1. À présenter aujourd'hui (≈ 5 min)

### Le pipeline (terminé et gelé)
Un pipeline **RAG orchestré en local avec n8n** qui rédige un argumentaire **POUR** l'autorisation FDA de la notification d'hypertension de l'Apple Watch, à partir d'un **corpus de 4 documents** (Apple, FDA K250507, Elgendi 2019, AHA 2026), avec :
- **des citations obligatoires** : chaque paragraphe cite un extrait du corpus, et la bibliographie est générée par le code (aucune référence ne peut être inventée) ;
- **des garde-fous automatiques** (structure, citations, chiffres, formulations absolues) qui signalent les défauts sans les corriger ;
- **un agent relecteur** qui reçoit le texte et les sources ;
- **une baseline** : le même LLM, avec les mêmes règles, mais sans corpus.

À montrer : la capture des workflows `00-ingestion`, `10-argumentaire` et `50-baseline` (⏳ à faire), et `outputs/argumentaire_20261028-095239.md`.

### L'exécution finale officielle (28/10, `20261028-095239`)
| | Pipeline | Baseline (LLM seul) |
|---|---|---|
| Sections imposées | **9 / 9** | 9 / 9 |
| Références | 4 documents, **exactes par construction** | 22 écrites par le LLM, ⏳ en cours de vérification |
| Paragraphes cités | 31 / 31 | 27 / 27 |
| « Information non disponible » | **3** (HIPAA, CE/MDR, RGPD : absents du corpus) | **0**, alors que la règle figure dans son prompt |
| Paragraphes signalés par les garde-fous | 8 / 34 | sans objet |
| Alertes G5 justes (jugement humain) | **6 / 8** | sans objet |
| Évaluation humaine (15 affirmations tirées au hasard, 1 juge) | **5 SOUTENU, 10 PARTIEL, 0 NON_SOUTENU** | non évaluée |
| Coût | 11 appels, 59 min | 1 appel, 5 min |

### Trois résultats à retenir
1. **Sans corpus, le LLM n'avoue jamais qu'il ne sait pas.** Le pipeline écrit « information non disponible » 3 fois, la baseline jamais, malgré la consigne.
2. **« Tout est vert » ne veut pas dire « tout est juste ».** Les garde-fous ne voient que la forme : sur l'exécution du 27/10, **17 défauts de fond** (sur-affirmations, affirmations non soutenues, liens inventés entre sources) ont été confirmés par une relecture humaine.
3. **L'IA qui relit l'IA ne voit presque rien.** Le relecteur, du même modèle que le rédacteur, repère **1 défaut sur 21** (0 sur 17 défauts de fond), malgré l'accès aux sources. Sur l'exécution finale, il a dépassé le délai de 600 s.

### Les principales difficultés (et leur solution)
- Aucune clé API gratuite chez Mistral → **passage à Gemini** (argument RGPD reformulé).
- **20 appels par jour** et une API très lente (de 34 s à près de 10 min par appel), avec des erreurs 503 → relances explicites, budget d'appels, règle d'arrêt, exécutions planifiées.
- Bibliographie mélangée aux extraits, un seul document dominant la recherche → nettoyage avant découpage, plusieurs requêtes, plafond par document, extrait « contre » forcé.
- Caractères corrompus renvoyés par Gemini → décodage avant les garde-fous.

### Les limites à annoncer d'emblée
Corpus de 4 documents ; pas de juge de fidélité ; relecteur de la même famille de modèle ; une seule exécution officielle ; validation humaine faite par un seul membre, volontairement indulgente ; jugements humains harmonisés après coup sur proposition d'une IA (Claude), selon des règles fixées à l'avance, valeurs initiales tracées : indépendance du jugement réduite.

---

## 2. Ce qui n'est pas encore fait
- Vérification des 22 références de la baseline.
- Vérification du code produit QXO / SFR (PDF D07, p. 8) et de l'alerte G4 (« 510 », « 21 », « 870.2380 »).
- Captures d'écran des workflows.
- Rapport écrit et support de l'oral.

---

## 3. Travail restant, en temps de travail

### A. Fin de l'évaluation (≈ 2 h restantes ; évaluation humaine et alertes G5 faites le 28/10)
| Tâche | Qui | Temps |
|---|---|---|
| Évaluation humaine : 15 affirmations (`eval_humaine_juge1.csv`), sans ouvrir la relecture | 1 membre | ✅ fait (28/10) |
| Vérification des 22 références de la baseline (existe ? auteurs, année, revue, DOI ?) | 1 à 2 membres | 1 h à 1 h 30 (à 2 : 45 min) |
| Jugement des 8 alertes G5 | 1 membre | ✅ fait (28/10) |
| QXO / SFR dans le PDF D07 p. 8 ; alerte G4 | 1 membre / Claude Code | 15 min |
| Captures des 3 workflows dans n8n | 1 membre | 15 min |
| Mise à jour des métriques et d'`oral.md` | Claude Code | 15 min |

### B. Rapport écrit (≈ 9 à 11 h)
Structure imposée par la consigne :
| Partie | Base existante | Temps |
|---|---|---|
| 1. Figure de synthèse (graphical abstract) | schéma de `oral.md` § 1 | 1 h à 1 h 30 |
| 2. Pipeline et méthodologie (optimisations, garde-fous, difficultés et solutions) | `oral.md` §§ 2-3, `pipeline.md`, `implémentation.md` | 2 h |
| 3. Contrôle qualité, avec des méthodes **issues de la littérature et citées** (RAGAS, FActScore, LLM-as-a-judge, évaluation humaine…) | liste dans `implémentation.md` ; **chaque référence est à vérifier** (contrôles au hasard) | 1 h 30 à 2 h |
| 4. Critique des résultats | `oral.md` §§ 4-6, `pipeline.md` § 5, résultats de l'évaluation humaine | 2 h |
| 5. Annexes : argumentaire généré, critères de sélection du corpus, prompts | fichiers existants, surtout de l'assemblage | 1 h |
| Relecture, mise en forme, PDF `Ecrit_Nom1_Nom2_NomX.pdf` | | 1 h à 1 h 30 |

### C. Oral (≈ 5 à 7 h)
| Tâche | Temps |
|---|---|
| Slides (9 diapositives, trame dans `implémentation.md` étape 10) → `Oral_Nom1_Nom2_NomX.pdf` | 2 h 30 à 3 h |
| Réponses aux questions sur le projet (`oral.md` § 7) | 1 h |
| Révision des **cours** (les 10 min de questions portent aussi sur eux) | 1 h 30 à 2 h, selon le groupe |
| Répétition chronométrée (10 min), à plusieurs | 1 h |

### D. Administratif (≈ 15 min)
- Confirmer la date limite (le PDF de consignes indique 02/11/2025 pour un projet 26/27 : sans doute le **lundi 02/11/2026**, ce qui laisse très peu de temps).
- Noms des membres dans `CLAUDE.md` et dans les noms de fichiers.
- Un seul envoi par groupe, à rosy.tsopra@aphp.fr et benjamin.pariente@aphp.fr.

### Total
**≈ 15 à 19 h de travail**, soit environ **5 à 7 h par personne à trois**. Claude peut rédiger un premier jet des parties 2, 3 et 4 du rapport à partir des fichiers existants, ce qui réduit le temps de rédaction d'environ moitié. La vérification des références de la littérature et les jugements humains restent au groupe.

### Ordre conseillé
1. **Aujourd'hui** : point d'étape ; lancer la vérification des références de la baseline (elle conditionne la critique ; l'évaluation humaine est faite).
2. **Jeudi–vendredi** : rapport, parties 1 à 3, en parallèle de la fin de l'évaluation.
3. **Week-end** : critique des résultats (partie 4), annexes, slides.
4. **Avant l'envoi** : relecture croisée, PDF, répétition.
