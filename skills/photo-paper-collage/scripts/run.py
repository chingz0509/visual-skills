#!/usr/bin/env python3
"""Agent-facing launcher. Uses only the user's own host and local runtime."""
from pathlib import Path
import json
import os
import subprocess
import sys

HERE = Path(__file__).resolve().parent
CACHE = Path(os.environ.get('VISUAL_SKILLS_CACHE', Path.home() / '.cache' / 'visual-style-skills'))

def main():
    runtime = CACHE / 'runtime.json'
    if not runtime.exists():
        subprocess.run([sys.executable, str(HERE / 'bootstrap.py')], check=True)
    info = json.loads(runtime.read_text())
    env = os.environ.copy()
    if info.get('vision'):
        env['VISUAL_SKILLS_VISION'] = info['vision']
    p = subprocess.run([info['python'], str(HERE / 'collage.py'), *sys.argv[1:]], env=env)
    raise SystemExit(p.returncode)

if __name__ == '__main__':
    main()
