#!/usr/bin/env python3
from pathlib import Path
import argparse,json
from PIL import Image,ImageDraw,ImageFont,ImageOps
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--run',required=True);a=p.parse_args()
items=json.loads((ROOT/'benchmark/manifest.json').read_text())['items']
canvas=Image.new('RGB',(1800,1120),'#e8e3d9');d=ImageDraw.Draw(canvas)
f=ImageFont.truetype(str(ROOT/'skills/visual-skills/assets/fonts/BebasNeue-Regular.ttf'),24)
for i,item in enumerate(items):
 root=ROOT/'benchmark/runs'/a.run/item['id']
 state=json.loads((root/'state.json').read_text());n=state['attempts'][-1]['index']
 path=root/f'attempt-{n}/final.png';x=(i%5)*360;y=(i//5)*560
 d.text((x+10,y+8),item['id']+' / '+str(n),fill='#232323',font=f)
 if path.exists():
  im=Image.open(path).convert('RGB');im.thumbnail((340,470));canvas.paste(im,(x+(360-im.width)//2,y+45))
 d.text((x+10,y+520),state['status'],fill='#232323',font=f)
path=ROOT/'benchmark/runs'/a.run/'contact-sheet.jpg';canvas.save(path,quality=92)
print(path)
