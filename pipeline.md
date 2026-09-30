# Spécification du pipeline — v1 (option B)
Contrat d'implémentation pour Claude Code. Toute divergence doit être signalée avant d'être codée.

## 0. Principes
- **Tranche verticale d'abord** : 3 documents → 1 section (technique) → garde-fous → assemblage. On n'élargit qu'une fois cette chaîne fonctionnelle de bout en bout.
- **Le LLM n'écrit jamais une référence bibliographique.** Il cite des `chunk_id`, et la bibliographie est générée par du code à partir de `corpus/meta.json`. Une référence inventée devient donc structurellement impossible : c'est le garde-fou principal, à mettre en avant à l'oral.
- **Prompts versionnés** dans `prompts/` (`redacteur_v1.md`, `examinateur_v1.md`…), jamais écrits en dur dans les nœuds. Chaque changement de prompt est consigné dans `implémentation.md`.
- **Traçabilité** : chaque exécution ajoute une ligne à `outputs/runs.jsonl` (run_id, horodatage, workflow, modèle, version de prompt, tokens, durée, résultat).
- **Limite Mistral (plan gratuit)** : environ 1 requête par seconde, à vérifier dans la console. Tous les appels passent par *Loop Over Items* (lots de 1) suivi de *Wait* 1,2 s.
- **Budget Claude** (≈ 4 $) : Claude Haiku n'est utilisé que pour le juge G3. En développement, travailler sur de petits échantillons.

## 1. Arborescence et montages
```
MOA/
  corpus/          # PDF en texte intégral (n°1 à n°20 de corpus.md) + meta.json
  prompts/         # prompts versionnés
  outputs/         # argumentaires, rapports de vérification, runs.jsonl, métriques
  n8n/workflows/   # exports JSON versionnés
```
- Monter dans le conteneur n8n : `./corpus` en lecture seule, `./prompts` en lecture seule, `./outputs` en lecture et écriture.
- ⚠️ n8n 2.x restreint l'accès des nœuds de fichiers à certains dossiers : vérifier la variable d'environnement concernée dans la documentation de la version installée.

`corpus/meta.json` (renseigné à la main, **source unique de vérité pour la bibliographie**) :
```json
[{"doc_id": "D06", "fichier": "apple_validation_2025.pdf",
  "reference": "Apple. Hypertension Notification Feature on Apple Watch — Validation paper. Sept 2025.",
  "url": "https://...", "versant": ["technique", "fda"], "role": "pour|contre|contexte"}]
```

## 2. Workflows n8n

### WF00 — Ingestion (`00-ingestion`)
Manual Trigger → lecture de `meta.json` → pour chaque document : *Read Files from Disk* → *Extract from File* (PDF) → Code (nettoyage : en-têtes, numéros de page, césures) → *Recursive Character Text Splitter* (≈ 1 000 caractères, chevauchement de 150, **à justifier dans le rapport**) → *Embeddings Mistral* (`mistral-embed`) → *Qdrant Vector Store* (insertion, collection `moa_corpus`).
- Métadonnées de chaque chunk : `chunk_id` (`D06-c012`), `doc_id`, `versant`, `role`, `page` si elle est disponible.
- Contrôle : nombre de chunks par document, et signalement de tout document dont le texte extrait fait moins de 500 caractères (PDF scanné, donc OCR nécessaire).

### WF10 — Rédaction d'une section (`10-redaction`, sous-workflow)
Entrée : `{section, consigne_section, position: "POUR"}`
1. Récupération dans Qdrant : top-k (k ≈ 8) sur la requête de la section, plus un **filtre `role = contre`** pour forcer la présence de contre-arguments.
2. LLM rédacteur : Mistral, modèle large, à vérifier dans le plan gratuit. Il reçoit les chunks avec leur `chunk_id` et doit produire une sortie structurée :
```json
{"section": "technique",
 "paragraphes": [{"texte": "...", "citations": ["D06-c012", "D09-c003"]}],
 "contre_arguments_traites": ["D12-c004"]}
```
Règles du prompt :
- toute affirmation factuelle cite au moins un `chunk_id` fourni ;
- aucune connaissance extérieure ;
- si l'information manque, écrire `[INFORMATION NON DISPONIBLE DANS LE CORPUS]` plutôt que d'inventer.
3. Sortie : JSON de la section + liste des `chunk_id` récupérés (nécessaire au garde-fou G2).

### WF20 — Garde-fous (`20-garde-fous`, sous-workflow)
| Garde-fou | Méthode | Coût |
|---|---|---|
| **G1 Structure** | Parser de sortie structurée + Code : toutes les sections imposées sont présentes, le JSON est valide | 0 |
| **G2 Citations** | Code : chaque `chunk_id` cité ∈ chunks récupérés ; paragraphe sans citation = alerte | 0 |
| **G3 Fidélité** | Claude Haiku comme juge, pour chaque paire (paragraphe, chunk cité) : `SOUTENU / PARTIEL / NON_SOUTENU` + justification courte | ≈ 0,002 $/paire |
| **G4 Chiffres** | Code : extraction par regex des nombres et pourcentages du paragraphe, et vérification de leur présence dans le texte du chunk cité | 0 |

Boucle : si G1 ou G2 échoue, ou si G3 donne plus de 20 % de `NON_SOUTENU`, retour au rédacteur avec la liste des problèmes, **2 itérations au maximum**. Le rapport de vérification est enregistré dans `outputs/verif_<run_id>.json`.

### WF30 — Agent examinateur (`30-examinateur`)
LLM Mistral, avec un modèle ou un prompt différent de celui du rédacteur. Il reçoit l'argumentaire complet, la consigne et la liste des documents `role = contre`.

Grille de relecture :
- conformité à la structure imposée ;
- contre-arguments du corpus non traités ;
- sur-affirmations (formulations absolues, causalités non démontrées) ;
- équilibre entre versants ;
- cohérence entre sections ;
- clarté de la conclusion.

Sortie : une **liste de problèmes** en JSON (`{section, gravité, problème, suggestion}`), pas une réécriture. Ensuite, une seule passe de correction par le rédacteur, suivie d'un nouveau passage de G1, G2 et G4. On conserve la version avant et la version après.

### WF40 — Assemblage (`40-assemblage`)
Fusion des sections dans l'ordre de la consigne → Markdown. Les `chunk_id` sont remplacés par des numéros de référence [n], et la bibliographie est **générée depuis `meta.json`**. Écriture dans `outputs/argumentaire_<run_id>.md`. La conversion en PDF se fait avec Pandoc, hors n8n.

### WF50 — Baseline (`50-baseline`)
Même modèle Mistral et même consigne, **mais sans RAG ni garde-fous**, en un seul prompt. Sortie : `outputs/baseline_<run_id>.md`.

### WF60 — Évaluation (`60-evaluation`)
Application de G2, G3 et G4 au pipeline et à la baseline. Pour la baseline, les références sont vérifiées à la main ou via PubMed. Sortie : `outputs/metriques.csv`

| Métrique | Pipeline | Baseline |
|---|---|---|
| % d'affirmations soutenues (G3) | | |
| % de références existantes et correctes | | |
| % de chiffres retrouvés dans la source (G4) | | |
| Couverture des sections imposées | | |
| Nombre de contre-arguments du corpus traités | | |
| Problèmes relevés par l'examinateur (par gravité) | | |
| Tokens, coût, durée | | |

À compléter par une évaluation humaine en aveugle sur un échantillon d'affirmations (2 évaluateurs du groupe, kappa de Cohen).

## 3. Ordre de construction
1. Arborescence + montages + `meta.json` pour 3 documents en accès libre (n° 6 Apple, n° 7 FDA K250507, n° 9 Elgendi)
2. WF00 sur ces 3 documents → vérification dans le tableau de bord Qdrant
3. WF10 pour la section « technique »
4. WF20 : G1, G2 et G4 (gratuits), puis G3 sur 5 paires seulement
5. WF40 → premier argumentaire partiel
6. Extension au corpus complet et à toutes les sections
7. WF30, puis WF50, puis WF60
Après chaque étape : export JSON du workflow + commit + ligne dans le journal de `implémentation.md` (avec capture d'écran si c'est utile pour l'oral).
