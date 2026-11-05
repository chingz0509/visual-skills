#!/usr/bin/env python3
"""Install the selected self-contained skill without overwriting existing user files."""
import argparse
from pathlib import Path
import os
import shutil
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--destination',default=str(Path(os.environ.get('CODEX_HOME',Path.home()/'.codex'))/'skills'))
 p.add_argument('--prepare',action='store_true',help='Prepare dependencies after copying')
 a=p.parse_args();source=ROOT/'skills/visual-skills';dest=Path(a.destination).expanduser().resolve()/source.name
 if dest.exists():raise SystemExit('An installation already exists; not overwritten: '+str(dest))
 dest.parent.mkdir(parents=True,exist_ok=True)
 shutil.copytree(source,dest,ignore=shutil.ignore_patterns('__pycache__','*.pyc','.DS_Store'))
 print('Installed: '+str(dest))
 if a.prepare:subprocess.run([sys.executable,str(dest/'scripts/bootstrap.py')],check=True)
if __name__=='__main__':main()
