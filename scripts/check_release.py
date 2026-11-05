#!/usr/bin/env python3
"""Check release evidence and required files without fabricating visual judgments."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    required = [
        'README.md', 'README.en.md', 'LICENSE', 'THIRD_PARTY.md',
        'CONTRIBUTING.md', 'CHANGELOG.md', 'docs/PUBLISHING.md',
        'skills/photo-paper-collage/SKILL.md',
        'skills/photo-paper-collage/assets/fonts/notosanssc-OFL.txt',
        'skills/photo-paper-collage/assets/fonts/bebasneue-OFL.txt',
    ]
    for name in required:
        if not (ROOT / name).is_file():
            raise SystemExit('Missing release file: ' + name)
    manifest = ROOT / 'benchmark/manifest.json'
    expected = (ROOT / 'benchmark/manifest.sha256').read_text().split()[0]
    if hashlib.sha256(manifest.read_bytes()).hexdigest() != expected:
        raise SystemExit('Frozen manifest was changed')
    items = json.loads(manifest.read_text())['items']
    results = json.loads((ROOT / 'benchmark/results.json').read_text())['results']
    if len(items) != 10 or {i['id'] for i in items} != {i['id'] for i in results}:
        raise SystemExit('Fixed dataset and published results disagree')
    attempts = 0
    for item in items:
        folder = ROOT / 'examples' / item['id']
        state = json.loads((folder / 'state.json').read_text())
        for attempt in state['attempts']:
            attempts += 1
            bundle = folder / attempt['bundle']
            # Failures remain visible; do not require every attempt to pass.
            if not (bundle / 'final.png').exists() and not (bundle / 'error.json').exists():
                raise SystemExit('Missing attempt output or error: ' + str(bundle))
            if attempt['status'] in ('passed', 'rejected'):
                for name in ('plan.json', 'checks.json', 'visual-review.json'):
                    if not (bundle / name).exists():
                        raise SystemExit('Missing review evidence: ' + str(bundle / name))
    print(f'Release materials checked: {len(items)} fixed cases, {attempts} published attempts.')
    print('This checks evidence presence, not aesthetics or human acceptance.')


if __name__ == '__main__':
    main()
