#!/usr/bin/env python3
"""Fetch the frozen inputs, validating bytes instead of silently accepting changed assets."""
import hashlib,json
from pathlib import Path
import urllib.request
ROOT=Path(__file__).resolve().parents[1]
manifest=ROOT/'benchmark/manifest.json'
assert hashlib.sha256(manifest.read_bytes()).hexdigest()==(ROOT/'benchmark/manifest.sha256').read_text().split()[0]
for item in json.loads(manifest.read_text())['items']:
 path=ROOT/'benchmark'/item['file']
 if path.exists():data=path.read_bytes()
 else:
  req=urllib.request.Request(item['download_url'],headers={'User-Agent':'VisualStyleSkills/0.1'})
  with urllib.request.urlopen(req,timeout=60) as response:data=response.read()
 if hashlib.sha256(data).hexdigest()!=item['sha256']:raise SystemExit('Frozen photo bytes differ: '+item['id']+'; do not replace the benchmark')
 path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data);print('Verified '+item['id'])
