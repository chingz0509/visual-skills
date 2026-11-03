#!/usr/bin/env python3
"""Recompose saved raster layers without segmentation, fonts, network, or generation calls."""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image


def replay(bundle, output):
    bundle=Path(bundle).resolve();output=Path(output).resolve()
    record=json.loads((bundle/'record.json').read_text())
    if output==bundle/'final.png':raise ValueError('Replay into a different path to preserve the recorded original')
    for name,expected in record['files'].items():
        path=(bundle/name).resolve()
        if not path.is_relative_to(bundle):raise ValueError('Asset outside bundle')
        if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:raise ValueError('Asset hash mismatch: '+name)
    im=Image.new('RGBA',tuple(record['canvas']))
    for layer in record['layers']:
        path=(bundle/layer['file']).resolve()
        if not path.is_relative_to(bundle):raise ValueError('Layer outside bundle')
        im.alpha_composite(Image.open(path).convert('RGBA'),(layer['x'],layer['y']))
    im=im.convert('RGB');output.parent.mkdir(parents=True,exist_ok=True);im.save(output)
    reference=Image.open(bundle/'final.png').convert('RGB')
    same=im.size==reference.size and im.tobytes()==reference.tobytes()
    print(json.dumps({'output':str(output),'pixel_identical':same}))
    if not same:raise ValueError('Replay differs from saved composition')
    return same


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('bundle');p.add_argument('--output',required=True)
    a=p.parse_args();replay(a.bundle,a.output)
