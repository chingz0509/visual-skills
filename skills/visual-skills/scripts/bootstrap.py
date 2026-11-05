#!/usr/bin/env python3
"""Find a usable Python or prepare an isolated environment; never modify global packages."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys

SKILL = Path(__file__).resolve().parents[1]
CACHE = Path(os.environ.get('VISUAL_SKILLS_CACHE', Path.home() / '.cache' / 'visual-skills'))

def probe(executable):
    try:
        p = subprocess.run([str(executable), '-c', 'import PIL,numpy; print(PIL.__version__)'], capture_output=True, text=True, timeout=15)
        return p.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False

def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    candidates = [sys.executable]
    if os.environ.get('VISUAL_SKILLS_PYTHON'):
        candidates.insert(0, os.environ['VISUAL_SKILLS_PYTHON'])
    candidates += [CACHE / 'venv' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')]
    runtime = Path.home() / '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3'
    candidates += [runtime]
    python = next((str(p) for p in candidates if Path(p).is_file() and probe(p)), None)
    if not python:
        venv = CACHE / 'venv'
        subprocess.run([sys.executable, '-m', 'venv', str(venv)], check=True)
        python = str(venv / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python'))
        subprocess.run([python, '-m', 'pip', 'install', 'Pillow==11.3.0', 'numpy==2.0.2'], check=True)
    vision = None
    note = 'Whole-photo composition available; local foreground segmentation unavailable.'
    if platform.system() == 'Darwin' and int(platform.mac_ver()[0].split('.')[0]) >= 14 and shutil.which('xcrun'):
        source = SKILL / 'scripts/vision.swift'
        tag = hashlib.sha256(source.read_bytes()).hexdigest()[:12]
        binary = CACHE / ('vision-' + tag)
        if not binary.exists():
            try:
                subprocess.run(['xcrun', 'swiftc', '-O', str(source), '-o', str(binary)], check=True, timeout=180, capture_output=True)
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                binary = None
        if binary and binary.exists():
            vision = str(binary)
            note = 'Apple Vision local segmentation and OCR available; no image-generation API used.'
    result = {'python': python, 'vision': vision, 'skill': str(SKILL), 'note': note}
    (CACHE / 'runtime.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
