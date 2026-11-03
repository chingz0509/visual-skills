#!/usr/bin/env python3
"""Package a self-contained skill and a source project, excluding private/runtime artifacts."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist';DIST.mkdir(exist_ok=True)
SKILL=ROOT/'skills/photo-paper-collage'

def archive(path,files,base,prefix):
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for file in files:
   if file.is_file() and '__pycache__' not in file.parts and file.suffix!='.pyc' and file.name!='.DS_Store':
    z.write(file,str(Path(prefix)/file.relative_to(base)))
 with zipfile.ZipFile(path) as z:
  assert z.testzip() is None
 print(path.name,path.stat().st_size,'bytes')

archive(DIST/'photo-paper-collage-0.1.0-experimental.zip',sorted(SKILL.rglob('*')),SKILL,'photo-paper-collage')
files=[]
for p in sorted(ROOT.rglob('*')):
 rel=p.relative_to(ROOT)
 if not rel.parts or rel.parts[0] in ['dist','.git']:continue
 if rel.parts[:2] in [('benchmark','inputs'),('benchmark','runs')]:continue
 if rel.as_posix()=='benchmark/input-contact-sheet.jpg':continue
 if p.name.startswith('.env'):continue
 files.append(p)
archive(DIST/'visual-style-skills-0.1.0-experimental.zip',files,ROOT,'visual-style-skills')
manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in DIST.glob('*.zip')}
(DIST/'SHA256SUMS.json').write_text(json.dumps(manifest,indent=2)+'\n')
