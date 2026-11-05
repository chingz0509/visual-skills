#!/usr/bin/env python3
"""Run the frozen benchmark without overwriting prior runs or inventing visual verdicts."""
import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser();p.add_argument('--run',required=True);p.add_argument('--workers',type=int,default=2);a=p.parse_args()
    manifest=ROOT/'benchmark/manifest.json'
    expected=(ROOT/'benchmark/manifest.sha256').read_text().split()[0]
    assert hashlib.sha256(manifest.read_bytes()).hexdigest()==expected,'Frozen manifest was changed'
    items=json.loads(manifest.read_text())['items']
    for item in items:
        file=ROOT/'benchmark'/item['file']
        assert hashlib.sha256(file.read_bytes()).hexdigest()==item['sha256'],item['id']+' source changed'
    output=ROOT/'benchmark/runs'/a.run
    if output.exists():raise SystemExit('Use a new run name; never replace previous attempts')
    output.mkdir(parents=True)
    def render(item):
        cmd=[sys.executable,str(ROOT/'skills/visual-skills/scripts/run.py'),'render','--input',str(ROOT/'benchmark'/item['file']),'--plan',str(ROOT/'benchmark/plans'/(item['id']+'.json')),'--output',str(output/item['id'])]
        result=subprocess.run(cmd,capture_output=True,text=True)
        return item['id'],result.returncode,result.stdout,result.stderr
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
        for key,code,stdout,stderr in pool.map(render,items):
            print(key,code,stdout.strip(),stderr.strip(),flush=True)
    (output/'run-info.json').write_text(json.dumps({'purpose':'development evaluation on fixed dataset; not held-out generalization','manifest_sha256':expected,'visual_review':'pending','human_acceptance':'pending'},indent=2)+'\n')

if __name__=='__main__':main()
