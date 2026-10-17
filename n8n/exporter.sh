#!/bin/sh
# Export des workflows du pipeline (noms « NN-… » ou « test-… ») vers n8n/workflows/<nom>.json,
# sans le bloc « shared » (nom et e-mail du propriétaire n8n). Usage : sh n8n/exporter.sh
set -eu
cd "$(dirname "$0")/.."
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"; podman exec moa_n8n_1 rm -rf /tmp/export' EXIT
podman exec moa_n8n_1 n8n export:workflow --backup --output=/tmp/export/ >/dev/null 2>&1
podman cp moa_n8n_1:/tmp/export/. "$tmp"
python3 - "$tmp" <<'EOF'
import glob, json, re, sys
for f in sorted(glob.glob(sys.argv[1] + '/*.json')):
    w = json.load(open(f))
    if not re.match(r'(\d\d|test)-', w['name']):
        continue
    w.pop('shared', None)
    s = json.dumps(w, ensure_ascii=False, indent=2)
    if re.search(r'[\w.+-]+@[\w-]+\.[a-z]{2,}', s):
        sys.exit(f"Adresse e-mail trouvée dans {w['name']} : export interrompu")
    open(f"n8n/workflows/{w['name']}.json", 'w').write(s + '\n')
    print('exporté :', w['name'])
EOF
