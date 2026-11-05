#!/usr/bin/env python3
"""Build one self-contained install ZIP from an explicit tracked-file allowlist."""
import hashlib
import json
from pathlib import Path
import zipfile
from check_privacy import audit_files, tracked_files

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/visual-skills'
REQUIRED = {
    'SKILL.md', 'LICENSE', 'THIRD_PARTY.md', 'agents/openai.yaml',
    'references/enhancement.md', 'references/plan.md', 'references/review.md', 'references/style.md',
    'scripts/bootstrap.py', 'scripts/collage.py', 'scripts/replay.py', 'scripts/run.py', 'scripts/vision.swift',
    'assets/fonts/NotoSansSC[wght].ttf', 'assets/fonts/BebasNeue-Regular.ttf',
    'assets/fonts/notosanssc-OFL.txt', 'assets/fonts/bebasneue-OFL.txt', 'assets/fonts/manifest.json',
}


def package(destination=None):
    files = [p for p in tracked_files(ROOT) if p.is_relative_to(SKILL) and p.relative_to(SKILL).as_posix() in REQUIRED]
    found = {p.relative_to(SKILL).as_posix() for p in files}
    if found != REQUIRED:
        raise ValueError('Missing tracked skill files: ' + ', '.join(sorted(REQUIRED - found)))
    findings = audit_files(files, ROOT)
    if findings:
        raise ValueError('Publication scan blocked package: ' + '; '.join(f'{name}: {reason}' for name, reason in findings))
    destination = Path(destination) if destination else ROOT / 'dist'
    destination.mkdir(parents=True, exist_ok=True)
    out = destination / 'visual-skills-0.1.0-experimental.zip'
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for file in sorted(files):
            # Fixed metadata avoids embedding local timestamps, owners or permissions.
            info = zipfile.ZipInfo('visual-skills/' + file.relative_to(SKILL).as_posix(), (2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, file.read_bytes())
    with zipfile.ZipFile(out) as archive:
        assert archive.testzip() is None
    checksum = {out.name: hashlib.sha256(out.read_bytes()).hexdigest()}
    (destination / 'SHA256SUMS.json').write_text(json.dumps(checksum, indent=2) + '\n')
    print(f'{out.name}: {len(files)} files, {out.stat().st_size} bytes. No developer/source bundle.')
    return out


if __name__ == '__main__':
    package()
