#!/usr/bin/env python3
"""Check publication candidates without printing sensitive matches."""
import argparse
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PATH_PATTERN = re.compile(rb'(?:/' + rb'Users/[^/\s"\x27<>]+/|/' + rb'home/[^/\s"\x27<>]+/|/' + rb'var/folders/|[A-Za-z]:\\Users\\)')
SECRET_PATTERN = re.compile(rb'(?:sk-(?:proj-)?[A-Za-z0-9_-]{24,}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)')
EMAIL_PATTERN = re.compile(rb'[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})')
FONT_FILES = {'NotoSansSC[wght].ttf', 'BebasNeue-Regular.ttf'}


def tracked_files(root=ROOT):
    names = subprocess.check_output(['git', 'ls-files', '-z'], cwd=root).decode().split('\0')
    return [root / name for name in names if name and (root / name).is_file()]


def forbidden_path(relative):
    parts = relative.parts
    lower = relative.as_posix().lower()
    return (any(p in {'.git', '.venv', '__pycache__', 'private', 'local', 'outputs', 'output'} for p in parts)
            or any(p.startswith('.env') for p in parts)
            or lower.startswith(('benchmark/inputs/', 'benchmark/runs/'))
            or relative.suffix.lower() in {'.key', '.pem', '.log', '.pyc'}
            or relative.name == '.DS_Store'
            or any(p.startswith(('cookies', 'credentials')) for p in parts))


def audit_bytes(name, data):
    findings = []
    if PATH_PATTERN.search(data):
        findings.append('personal absolute path')
    if SECRET_PATTERN.search(data):
        findings.append('credential-like value')
    # Unmodified licensed fonts contain upstream contact metadata.
    if Path(name).name not in FONT_FILES:
        if any(not m.group(1).lower().endswith(b'users.noreply.github.com') for m in EMAIL_PATTERN.finditer(data)):
            findings.append('email requires review')
    return findings


def audit_files(files, root=ROOT):
    findings = []
    for file in files:
        rel = file.relative_to(root)
        if file.is_symlink() or not file.resolve().is_relative_to(root.resolve()):
            findings.append((str(rel), 'symbolic link or external file'))
            continue
        if forbidden_path(rel):
            findings.append((str(rel), 'private/runtime filename'))
        findings.extend((str(rel), reason) for reason in audit_bytes(str(rel), file.read_bytes()))
    return findings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--history', action='store_true')
    args = parser.parse_args()
    files = tracked_files()
    findings = audit_files(files)
    if args.history:
        rows = subprocess.check_output(['git', 'rev-list', '--objects', '--all'], cwd=ROOT).decode().splitlines()
        for row in rows:
            sha, _, name = row.partition(' ')
            if subprocess.check_output(['git', 'cat-file', '-t', sha], cwd=ROOT).strip() == b'blob':
                data = subprocess.check_output(['git', 'cat-file', 'blob', sha], cwd=ROOT)
                findings.extend((name, 'history: ' + reason) for reason in audit_bytes(name, data))
        identities = subprocess.check_output(['git', 'log', '--all', '--format=%ae%n%ce'], cwd=ROOT).splitlines()
        if any(not email.lower().endswith(b'@users.noreply.github.com') for email in identities):
            findings.append(('git metadata', 'non-private commit email'))
    if findings:
        for name, reason in sorted(set(findings)):
            print(f'BLOCKED: {name}: {reason}')
        raise SystemExit(1)
    print(f'Publication scan passed: {len(files)} tracked files' + (' and all reachable history.' if args.history else '.'))
    print('Pattern checks do not establish absence of every kind of personal information.')


if __name__ == '__main__':
    main()
