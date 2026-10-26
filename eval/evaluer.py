#!/usr/bin/env python3
"""Évaluation du pipeline et de la baseline (pipeline.md, section 3). Bibliothèque standard seulement.

  python3 eval/evaluer.py metriques <run_id du pipeline> [<run_id de la baseline>] [--dossier outputs]
      Écrit metriques.csv et, s'ils n'existent pas encore, les fichiers à remplir à la main :
      eval_humaine_juge1.csv et eval_humaine_juge2.csv (15 affirmations tirées au hasard, une copie par évaluateur)
      et references_baseline.csv (références de la baseline, à vérifier une par une). Ils ne sont jamais écrasés.

  python3 eval/evaluer.py kappa <eval_humaine_juge1.csv> <eval_humaine_juge2.csv>
      Kappa de Cohen entre les deux évaluateurs (SOUTENU, PARTIEL, NON_SOUTENU), écrit aussi dans kappa.txt.

Les CSV sont au format tableur français : séparateur « ; », UTF-8 avec BOM.
"""
import argparse
import csv
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
MARQUEUR = '[INFORMATION NON DISPONIBLE'  # commun au pipeline (« … DANS LE CORPUS] ») et à la baseline (« …] »)
JUGEMENTS = ['SOUTENU', 'PARTIEL', 'NON_SOUTENU']
N_AFFIRMATIONS = 15


def lire_json(chemin):
    return json.loads(chemin.read_text(encoding='utf-8'))


def ligne_runs(dossier, run_id, workflow):
    """Dernière ligne de runs.jsonl pour cette exécution, ou None."""
    lignes = [json.loads(l) for l in (dossier / 'runs.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]
    lignes = [l for l in lignes if l['run_id'] == run_id and l['workflow'] == workflow]
    return lignes[-1] if lignes else None


def ecrire_csv(chemin, entetes, lignes, ecraser):
    if chemin.exists() and not ecraser:
        print(f'  {chemin.name} existe déjà : non écrasé (il contient peut-être des jugements).')
        return
    with chemin.open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(entetes)
        w.writerows(lignes)
    print(f'  écrit : {chemin}')


def ratio(n, total):
    return f'{n} / {total}' if total else '0 / 0'


def appels(run):
    """« 5 (dont 1 relance), 11 embeddings, 342 s » à partir d'une ligne de runs.jsonl."""
    if not run:
        return 'ligne absente de runs.jsonl'
    relances = sum(n - 1 for n in run.get('tentatives', {}).values())
    return (f"{run['appels']['chat']} appel(s) de chat (dont {relances} relance(s)), "
            f"{run['appels']['embeddings']} requête(s) d'embeddings, {run['duree_s']} s")


def mesures_pipeline(dossier, run_id, imposees):
    verif = lire_json(dossier / f'verif_{run_id}.json')
    sections = verif['sections']
    paragraphes = [p for s in sections for p in s['paragraphes']]
    factuels = [p for p in paragraphes if MARQUEUR not in p['texte']]
    signales = lambda g: sum(any(a.startswith(g) for a in p['alertes']) for p in paragraphes)
    documents = {c.split('-')[0] for p in paragraphes for c in p['citations']}
    chemin_relecture = dossier / f'relecture_{run_id}.json'
    if chemin_relecture.exists():
        r = lire_json(chemin_relecture)
        relecteur = (f"échec : {r['erreur']}" if r['erreur'] else
                     f"{len(r['problemes'])} (haute {r['par_gravite']['haute']}, moyenne {r['par_gravite']['moyenne']}, basse {r['par_gravite']['basse']})")
    else:
        relecteur = 'pas de relecture pour cette exécution'
    return {
        'sections': f"{ratio(sum(1 for s in sections if s['paragraphes'] and not s['g1']), len(imposees))}"
                    f" (demandées : {len(sections)} ; en échec G1 : {sum(1 for s in sections if s['g1'])})",
        'references': f'100 % par construction ({len(documents)} document(s) cité(s), bibliographie générée depuis meta.json)',
        'citations': f"{ratio(sum(1 for p in factuels if p['citations']), len(factuels))} paragraphes hors {MARQUEUR}]",
        'signales': f"{ratio(sum(1 for p in paragraphes if p['alertes']), len(paragraphes))}"
                    f" (G2 : {signales('G2')}, G4 : {signales('G4')}, G5 : {signales('G5')})",
        'marqueur': ratio(len(paragraphes) - len(factuels), len(paragraphes)),
        'relecteur': relecteur,
        'appels': appels(ligne_runs(dossier, run_id, '10-argumentaire')),
    }, verif


def mesures_baseline(dossier, run_id, imposees):
    brut = lire_json(dossier / f'baseline_{run_id}.json')
    sortie = brut['sortie'] or {'sections': [], 'references': []}
    recues = {s['id']: s for s in sortie['sections']}
    demandees = brut['sections_demandees']
    paragraphes = [p for i in demandees for p in recues.get(i, {}).get('paragraphes', [])]
    factuels = [p for p in paragraphes if MARQUEUR not in p['texte']]
    listees = {r['numero'] for r in sortie['references']}
    citees = {n for p in paragraphes for n in p['references']}
    return {
        'sections': f"{ratio(sum(1 for i in demandees if recues.get(i, {}).get('paragraphes')), len(imposees))}"
                    f" (demandées : {len(demandees)}" + (f" ; échec : {brut['erreur']}" if brut['erreur'] else '') + ')',
        'references': f"{len(listees)} référence(s) listée(s), à vérifier une par une (references_baseline.csv) ;"
                      f" renvois sans référence listée : {len(citees - listees)} ; références jamais citées : {len(listees - citees)}",
        'citations': f"{ratio(sum(1 for p in factuels if p['references']), len(factuels))} paragraphes hors {MARQUEUR}]",
        'signales': 'non applicable (pas de garde-fous)',
        'marqueur': ratio(len(paragraphes) - len(factuels), len(paragraphes)),
        'relecteur': 'non applicable',
        'appels': appels(ligne_runs(dossier, run_id, '50-baseline')),
    }, brut, recues


def phrases(texte):
    """Découpe un paragraphe en phrases ; garde celles d'au moins 6 mots."""
    morceaux = re.split(r'(?<=[.!?])\s+(?=[A-ZÀ-ÖØ-Ý«"])', texte.strip())
    return [m for m in morceaux if len(m.split()) >= 6]


def echantillon(verif, run_id):
    """Affirmations = phrases des paragraphes qui citent au moins un chunk récupéré (hors marqueur), tirées au hasard."""
    population = []
    for s in verif['sections']:
        chunks = {c['chunk_id']: c for c in s['chunks_recuperes']}
        for p in s['paragraphes']:
            cites = [chunks[i] for i in p['citations'] if i in chunks]
            if MARQUEUR in p['texte'] or not cites:
                continue
            for phrase in phrases(p['texte']):
                population.append((s['id'], phrase, cites))
    tirage = sorted(random.Random(run_id).sample(range(len(population)), min(N_AFFIRMATIONS, len(population))))
    lignes = []
    for k, i in enumerate(tirage, 1):
        section, phrase, cites = population[i]
        textes = '\n---\n'.join(
            f"[{c['chunk_id']} · p. {c['page']}]\n" + c.get('texte', "(texte non conservé dans ce fichier verif : exécution antérieure au 26/10 au soir)")
            for c in cites)
        lignes.append([k, section, phrase, ', '.join(c['chunk_id'] for c in cites), textes, '', ''])
    return lignes, len(population)


def commande_metriques(args):
    dossier = Path(args.dossier)
    imposees = [s['id'] for s in lire_json(RACINE / 'prompts' / 'sections.json')['sections']]
    pipeline, verif = mesures_pipeline(dossier, args.pipeline, imposees)
    baseline, brut, recues = mesures_baseline(dossier, args.baseline, imposees) if args.baseline else ({}, None, None)
    libelles = [
        ('sections', 'Sections imposées présentes', 'auto'),
        ('references', 'Références existantes et correctes', 'manuel (baseline)'),
        ('citations', 'Paragraphes avec au moins une citation', 'auto'),
        ('signales', 'Paragraphes signalés ⚠ (G2 / G4 / G5)', 'auto'),
        ('marqueur', 'Paragraphes [INFORMATION NON DISPONIBLE]', 'auto'),
        ('relecteur', 'Problèmes relevés par le relecteur, par gravité', 'auto'),
        ('appels', "Nombre d'appels, durée", 'auto'),
    ]
    print(f'Pipeline {args.pipeline}' + (f' · baseline {args.baseline}' if args.baseline else ''))
    lignes = [[libelle, pipeline[cle], baseline.get(cle, 'pas de baseline'), mode] for cle, libelle, mode in libelles]
    for l in lignes:
        print(f'  {l[0]} : {l[1]} | {l[2]}')
    ecrire_csv(dossier / 'metriques.csv', [f'Métrique (pipeline {args.pipeline}, baseline {args.baseline or "—"})', 'Pipeline', 'Baseline', 'Mode'], lignes, ecraser=True)

    ech, population = echantillon(verif, args.pipeline)
    print(f'  évaluation humaine : {len(ech)} affirmation(s) tirée(s) sur {population} (graine : {args.pipeline})')
    entetes = ['id', 'section', 'affirmation', 'chunks_cites', 'textes_des_chunks', 'jugement (SOUTENU / PARTIEL / NON_SOUTENU)', 'commentaire']
    for juge in (1, 2):
        ecrire_csv(dossier / f'eval_humaine_juge{juge}.csv', entetes, ech, ecraser=False)

    if brut:
        sections_de = {}
        for i, s in recues.items():
            for p in s['paragraphes']:
                for n in p['references']:
                    sections_de.setdefault(n, set()).add(i)
        refs = [[r['numero'], r['reference'], ', '.join(sorted(sections_de.get(r['numero'], []))), '', '', '']
                for r in (brut['sortie'] or {}).get('references', [])]
        ecrire_csv(dossier / 'references_baseline.csv',
                   ['numero', 'reference', 'citee_dans', 'existe (OUI / NON)', 'correcte (OUI / PARTIEL / NON)', 'commentaire'], refs, ecraser=False)


def lire_jugements(chemin):
    with Path(chemin).open(encoding='utf-8-sig', newline='') as f:
        lignes = list(csv.reader(f, delimiter=';'))[1:]
    jugements = {}
    for l in lignes:
        valeur = l[5].strip().upper().replace(' ', '_').replace('-', '_')
        if valeur not in JUGEMENTS:
            sys.exit(f'{chemin}, affirmation {l[0]} : jugement « {l[5]} » invalide (attendu : {", ".join(JUGEMENTS)})')
        jugements[l[0]] = valeur
    return jugements


def commande_kappa(args):
    j1, j2 = lire_jugements(args.juge1), lire_jugements(args.juge2)
    if j1.keys() != j2.keys():
        sys.exit('Les deux fichiers ne portent pas sur les mêmes affirmations.')
    paires = [(j1[k], j2[k]) for k in j1]
    n = len(paires)
    po = sum(a == b for a, b in paires) / n
    m1, m2 = Counter(a for a, _ in paires), Counter(b for _, b in paires)
    pe = sum(m1[c] * m2[c] for c in JUGEMENTS) / n ** 2
    kappa = (po - pe) / (1 - pe) if pe < 1 else float('nan')
    fr = lambda x, chiffres: f'{x:.{chiffres}f}'.replace('.', ',')  # notation française
    sortie = [
        f'Affirmations : {n}',
        f'Accord observé : {fr(100 * po, 1)} % · accord attendu par hasard : {fr(100 * pe, 1)} %',
        f'Kappa de Cohen : {fr(kappa, 3)}' if pe < 1 else 'Kappa de Cohen : indéfini (un seul jugement utilisé par les deux évaluateurs)',
        'Répartition (évaluateur 1 / évaluateur 2) : ' + ' · '.join(f'{c} {m1[c]} / {m2[c]}' for c in JUGEMENTS),
        'Matrice de confusion (lignes : évaluateur 1, colonnes : évaluateur 2) :',
        '  ' + ' '.join(f'{c:>12}' for c in JUGEMENTS),
        *[f'  {a:<12}' + ' '.join(f'{sum(1 for x, y in paires if x == a and y == b):>12}' for b in JUGEMENTS) for a in JUGEMENTS],
    ]
    print('\n'.join(sortie))
    (Path(args.juge1).parent / 'kappa.txt').write_text('\n'.join(sortie) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sous = parser.add_subparsers(dest='commande', required=True)
    m = sous.add_parser('metriques', help='métriques automatiques et fichiers à remplir')
    m.add_argument('pipeline', help='run_id de 10-argumentaire')
    m.add_argument('baseline', nargs='?', help='run_id de 50-baseline')
    m.add_argument('--dossier', default=str(RACINE / 'outputs'), help='dossier des sorties (défaut : outputs/)')
    k = sous.add_parser('kappa', help='kappa de Cohen entre deux évaluateurs')
    k.add_argument('juge1')
    k.add_argument('juge2')
    args = parser.parse_args()
    {'metriques': commande_metriques, 'kappa': commande_kappa}[args.commande](args)


if __name__ == '__main__':
    main()
