#!/usr/bin/env python3
"""Photo-preserving collage compositor. No generation API, uploads, or synthetic subject RGB."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, __version__ as PIL_VERSION

SKILL = Path(__file__).resolve().parents[1]
W, H = 1200, 1600
PALETTES = {
    'lagoon': {'bg': '#128b9a', 'paper': '#f3e9d3', 'accent': '#e94932', 'second': '#f5c64b', 'ink': '#24251f'},
    'lilac': {'bg': '#b6a0d5', 'paper': '#f0e8d7', 'accent': '#f35024', 'second': '#ded453', 'ink': '#272321'},
    'archive': {'bg': '#eee3ca', 'paper': '#f8f0dd', 'accent': '#df4a2d', 'second': '#d8aa28', 'ink': '#272923'},
    'forest': {'bg': '#263d35', 'paper': '#eee6d4', 'accent': '#e0b93d', 'second': '#c4aa92', 'ink': '#25352d'},
}
REVIEW_KEYS = ['subject_fidelity', 'edge_integrity', 'text_correct', 'style_coherent', 'composition_usable']


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def rgb(value):
    return tuple(bytes.fromhex(value.lstrip('#')))


def font(size, latin=False, heavy=False):
    path = SKILL / 'assets/fonts' / ('BebasNeue-Regular.ttf' if latin else 'NotoSansSC[wght].ttf')
    f = ImageFont.truetype(str(path), int(size))
    if not latin:
        f.set_variation_by_axes([850 if heavy else 450])
    return f


def texture(size, color, seed, strength=2.2):
    rng = np.random.default_rng(seed)
    width, height = size
    noise = rng.normal(0, strength, (height, width, 1))
    base = np.array(rgb(color), dtype=np.float32).reshape(1, 1, 3)
    arr = np.clip(base + noise, 0, 255).astype('uint8')
    return Image.fromarray(arr).convert('RGBA')


def torn_paper(size, color, seed, grid=False, ruled=False):
    width, height = size
    im = texture(size, color, seed)
    rng = np.random.default_rng(seed)
    edge = min(10, width // 30, height // 20)
    pts = [(x, int(rng.integers(1, max(edge, 2)))) for x in range(0, width, 9)]
    pts += [(width - int(rng.integers(1, max(edge, 2))), y) for y in range(0, height, 9)]
    pts += [(x, height - int(rng.integers(1, max(edge, 2)))) for x in range(width - 1, -1, -9)]
    pts += [(int(rng.integers(1, max(edge, 2))), y) for y in range(height - 1, -1, -9)]
    alpha = Image.new('L', size); ImageDraw.Draw(alpha).polygon(pts, fill=255)
    d = ImageDraw.Draw(im)
    if grid:
        for x in range(25, width, 35): d.line((x, 0, x, height), fill=(91, 108, 109, 28), width=1)
        for y in range(25, height, 35): d.line((0, y, width, y), fill=(91, 108, 109, 28), width=1)
    if ruled:
        for y in range(30, height, 27): d.line((10, y, width - 10, y), fill=(80, 75, 60, 35), width=1)
    im.putalpha(alpha)
    return im


def text_bitmap(text, size, color, latin=False, heavy=False):
    f = font(size, latin, heavy)
    box = f.getbbox(text)
    width, height = max(1, box[2] - box[0]), max(1, box[3] - box[1])
    im = Image.new('RGBA', (width + 8, height + 12))
    ImageDraw.Draw(im).text((4 - box[0], 6 - box[1]), text, font=f, fill=color)
    return im


def fit_text(text, max_w, max_h, color, latin=False, heavy=False, max_size=155, min_size=24):
    for size in range(max_size, min_size - 1, -1):
        im = text_bitmap(text, size, color, latin, heavy)
        if im.width <= max_w and im.height <= max_h:
            return im, size
    raise ValueError('Text does not fit at readable size; split into more lines or choose another layout. Original text was not changed.')


class Canvas:
    def __init__(self, dest, palette, seed):
        self.dest = dest
        self.assets = dest / 'assets'; self.assets.mkdir()
        self.image = Image.new('RGBA', (W, H))
        self.layers = []
        self.checks = []
        self.photo_boxes = []
        self.text_boxes = []
        self.palette, self.seed = palette, seed
        self.add(texture((W, H), palette['bg'], seed), (W // 2, H // 2), 'background')

    def add(self, im, center, role, angle=0, shadow=False, protected=False):
        if angle:
            im = im.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
        x, y = round(center[0] - im.width / 2), round(center[1] - im.height / 2)
        if protected:
            self.checks.append({'name': role + '_inside_canvas', 'pass': x >= 0 and y >= 0 and x + im.width <= W and y + im.height <= H})
        if shadow:
            shade = Image.new('RGBA', (im.width + 30, im.height + 30))
            alpha = Image.new('L', shade.size); alpha.paste(im.getchannel('A'), (15, 15))
            alpha = alpha.filter(ImageFilter.GaussianBlur(5)).point(lambda p: int(p * .16))
            shade.putalpha(alpha)
            self.add(shade, (center[0] + 3, center[1] + 7), role + '_shadow')
        filename = f'{len(self.layers):02d}-{role}.png'
        im.save(self.assets / filename)
        self.layers.append({'file': 'assets/' + filename, 'x': x, 'y': y, 'role': role, 'size': list(im.size)})
        self.image.alpha_composite(im, (x, y))
        box = (x, y, x + im.width, y + im.height)
        if role == 'photo': self.photo_boxes.append(box)
        if role.startswith('text_'): self.text_boxes.append(box)
        return box

    def paper(self, size, center, color, role='paper', angle=0, grid=False, ruled=False):
        return self.add(torn_paper(size, color, self.seed + len(self.layers), grid, ruled), center, role, angle, True)

    def text(self, text, center, max_w, max_h, color, latin=False, heavy=False, angle=0, max_size=150, role='text_title'):
        im, size = fit_text(text, max_w, max_h, color, latin, heavy, max_size)
        box = self.add(im, center, role, angle, protected=True)
        self.checks.append({'name': role + '_readable_size', 'pass': size >= 24, 'font_size': size, 'text': text})
        return box

    def star(self, center, radius, color, points=8):
        im = Image.new('RGBA', (radius * 2 + 4, radius * 2 + 4)); d = ImageDraw.Draw(im)
        pts=[]
        for i in range(points * 2):
            a = math.pi * i / points
            r = radius * (1 if i % 2 == 0 else .32)
            pts.append((radius + 2 + r * math.cos(a), radius + 2 + r * math.sin(a)))
        d.polygon(pts, fill=color)
        self.add(im, center, 'star')

    def tape(self, center, angle):
        im = torn_paper((175, 48), '#d7c9a3', self.seed + len(self.layers))
        im.putalpha(im.getchannel('A').point(lambda p: int(p * .75)))
        self.add(im, center, 'tape', angle)


def validate_plan(plan):
    required = ['category', 'title', 'subtitle', 'palette', 'layout', 'photo_mode', 'seed', 'design_reason']
    for key in required:
        if key not in plan: raise ValueError('Missing plan key: ' + key)
    if plan['category'] not in ['person', 'group', 'product', 'pet', 'landscape']: raise ValueError('Unsupported category')
    if plan['layout'] not in ['cutout', 'editorial', 'landscape', 'simple']: raise ValueError('Unsupported layout')
    if plan['photo_mode'] not in ['cutout', 'whole']: raise ValueError('Unsupported photo_mode')
    if plan['palette'] not in PALETTES: raise ValueError('Unsupported palette')
    if type(plan['seed']) is not int: raise ValueError('seed must be an integer')
    if not isinstance(plan['subtitle'], str): raise ValueError('subtitle must be a string')
    if not isinstance(plan['title'], list) or not plan['title'] or any(not isinstance(t, str) or not t.strip() for t in plan['title']): raise ValueError('title must contain nonempty lines')
    if len(plan['title']) > 3: raise ValueError('At most three title lines; use a larger layout for longer formal copy')
    if plan['category'] in ['group', 'landscape'] and plan['photo_mode'] != 'whole': raise ValueError('Groups and landscapes must stay whole')
    if plan['layout'] == 'cutout' and plan['photo_mode'] != 'cutout': raise ValueError('cutout layout requires cutout photo')
    if plan.get('tone', 'color') not in ['color', 'mono']: raise ValueError('tone must be color or mono')
    if plan.get('formal_copy') is not None:
        visible = ''.join(plan['title']) + plan['subtitle']
        for phrase in plan['formal_copy']:
            if phrase not in visible: raise ValueError('Formal copy missing or rewritten: ' + phrase)


def prepare_photo(source, dest, plan):
    original = ImageOps.exif_transpose(Image.open(source)).convert('RGB')
    original.save(dest / 'source-normalized.png')
    write_json(dest / 'source.json', {'original_filename': source.name, 'sha256': digest(source), 'normalized_sha256': digest(dest / 'source-normalized.png'), 'size': list(original.size)})
    shutil.copyfile(source, dest / ('source-original' + source.suffix.lower()))
    photo = original.convert('RGBA')
    mask_info = {'requested': plan['photo_mode'], 'used': 'whole', 'warning': None}
    if plan['photo_mode'] == 'cutout':
        tool = os.environ.get('VISUAL_SKILLS_VISION')
        if not tool or not Path(tool).is_file():
            raise RuntimeError('Local segmentation unavailable. Keep this failed attempt; use a whole-photo layout in the repair attempt.')
        maskfile = dest / 'mask.png'
        result = subprocess.run([tool, 'mask', str(dest / 'source-normalized.png'), str(maskfile)], capture_output=True, text=True, timeout=120)
        if result.returncode: raise RuntimeError('Local segmentation failed: ' + result.stderr[:500])
        mask = Image.open(maskfile).convert('L')
        if mask.size != original.size: raise RuntimeError('Mask size differs from original')
        coverage = np.asarray(mask).mean() / 255
        if not .015 < coverage < .98: raise RuntimeError('Mask coverage is implausible; retain original photo in next attempt')
        photo.putalpha(mask)
        mask_info = {'requested': 'cutout', 'used': 'cutout', 'coverage': float(coverage), 'engine': 'Apple Vision local foreground instances', 'warning': 'Mask completeness requires side-by-side visual review; coverage is not a fidelity proof.'}
    if plan.get('tone', 'color') == 'mono':
        toned = ImageOps.grayscale(photo).convert('RGBA'); toned.putalpha(photo.getchannel('A')); photo = toned
    photo.save(dest / 'photo-prepared.png')
    # The RGB preparation is restricted to identity or grayscale conversion. Mask affects alpha only.
    expected = original if plan.get('tone', 'color') == 'color' else ImageOps.grayscale(original).convert('RGB')
    unchanged_rgb = np.array_equal(np.asarray(photo.convert('RGB')), np.asarray(expected))
    write_json(dest / 'photo-processing.json', {'mask': mask_info, 'tone': plan.get('tone', 'color'), 'rgb_matches_allowed_transform': bool(unchanged_rgb), 'generative_subject_edit': False})
    return photo, mask_info, unchanged_rgb


def place_photo(c, photo, area, angle=0, cutout=False):
    cx, cy, bw, bh = area
    if cutout:
        box = photo.getchannel('A').getbbox()
        if not box: raise ValueError('Empty subject mask')
        photo = photo.crop(box)
    # Reserve space for expanded rotation and the paper border; never crop photograph to fill.
    radians = abs(angle) * math.pi / 180
    sw, sh = photo.size
    scale = min((bw - 52) / (sw * math.cos(radians) + sh * math.sin(radians)), (bh - 52) / (sh * math.cos(radians) + sw * math.sin(radians)))
    target = (max(1, round(sw * scale)), max(1, round(sh * scale)))
    resized = photo.resize(target, Image.Resampling.LANCZOS)
    pad = 23
    mounted = Image.new('RGBA', (target[0]+pad*2, target[1]+pad*2))
    if cutout:
        a = Image.new('L', mounted.size); a.paste(resized.getchannel('A'), (pad, pad))
        a = a.filter(ImageFilter.MaxFilter(35))
        paper = texture(mounted.size, c.palette['paper'], c.seed + 201)
        paper.putalpha(a); mounted.alpha_composite(paper)
    else:
        mounted = torn_paper(mounted.size, c.palette['paper'], c.seed + 201)
    mounted.alpha_composite(resized, (pad, pad))
    c.add(mounted, (cx,cy), 'photo', angle, True, protected=True)
    return target


def add_engraving(c, center, scale=1):
    """Original procedural botanical marks, never extracted from reference posters."""
    im=Image.new('RGBA',(260,380));d=ImageDraw.Draw(im);ink=rgb(c.palette['ink'])+(170,)
    d.line((135,365,127,195,145,30),fill=ink,width=3)
    for j in range(6):
        y=70+j*45; side=-1 if j%2 else 1
        tip=(135+side*105,y-35)
        d.line((132,y+30,*tip),fill=ink,width=2)
        for k in range(15):
            t=k/15
            x=132+(tip[0]-132)*t; yy=y+30+(tip[1]-y-30)*t
            length=23*math.sin(t*math.pi)
            d.line((x,yy,x+side*length,yy-15),fill=ink,width=1)
            d.line((x,yy,x-side*length*.4,yy+13),fill=ink,width=1)
    if scale!=1: im=im.resize((int(im.width*scale),int(im.height*scale)),Image.Resampling.LANCZOS)
    c.add(im,center,'botanical')


def draw_title(c, plan, top=115, max_height=280, strip=False):
    lines=plan['title']; line_h=min(142,max_height/len(lines)); p=c.palette
    for i,line in enumerate(lines):
        center=(590+(12 if i%2 else -12),top+line_h*(i+.5))
        if strip:
            im,size=fit_text(line,1010,line_h-22,p['ink'],heavy=True,max_size=int(line_h))
            paper=torn_paper((im.width+38,im.height+26),p['paper'],c.seed+50+i)
            c.add(paper,center,'headline_paper',angle=(-2 if i%2==0 else 1.5),shadow=True)
            c.add(im,center,'text_title',angle=(-2 if i%2==0 else 1.5),protected=True)
            c.checks.append({'name':'title_readable_size','pass':size>=24,'font_size':size,'text':line})
        else:
            c.text(line,center,1050,line_h-8,p['ink'] if plan['palette']=='archive' else p['paper'],heavy=True,max_size=int(line_h))


def compose(dest, plan, photo):
    p=PALETTES[plan['palette']];seed=plan['seed']; c=Canvas(dest,p,seed)
    layout=plan['layout']
    # Small quiet folio; creative text is explicitly part of the Agent's plan.
    label=plan.get('eyebrow','PAPER / MOMENTS')
    c.text(label,(240,56),350,38,p['ink'] if plan['palette']=='archive' else p['paper'],latin=True,max_size=33,role='text_eyebrow')
    c.text(plan.get('edition','A MOMENT, KEPT'),(963,56),350,38,p['ink'] if plan['palette']=='archive' else p['paper'],latin=True,max_size=28,role='text_edition')
    if layout == 'cutout':
        draw_title(c,plan,112,260,strip=True)
        c.paper((700,795),(589,865),p['paper'],'backing_grid',angle=7,grid=True)
        c.paper((730,660),(622,941),p['accent'],'backing_color',angle=-7)
        c.text(plan.get('motif','KEEP / THE MOMENT'),(587,584),600,140,p['ink'],latin=True,max_size=118,angle=7,role='text_motif')
        add_engraving(c,(155,1135),.9)
        c.star((1037,671),63,p['second'],7)
        place_photo(c,photo,(608,892,905,945),angle=-2,cutout=True)
        # Subtitle is below the subject, never laid across a face or product.
        c.paper((1030,123),(600,1430),p['second'],'caption_strip',angle=2)
        c.text(plan['subtitle'],(600,1430),950,75,p['ink'],heavy=True,max_size=52,angle=2,role='text_subtitle')
        c.star((105,550),40,p['paper'],6)
    elif layout == 'editorial':
        draw_title(c,plan,105,260)
        c.paper((1040,720),(605,875),p['accent'],'backing_color',angle=6)
        c.paper((1050,800),(575,883),p['paper'],'backing_grid',angle=-4,grid=True)
        c.text(plan.get('motif','TOGETHER / IN FRAME'),(586,461),1030,155,p['second'],latin=True,max_size=143,angle=0,role='text_motif')
        place_photo(c,photo,(600,905,1070,740),angle=3,cutout=False)
        c.tape((250,545),-19);c.tape((971,1232),-16)
        c.paper((950,120),(600,1400),p['paper'],'caption_strip',angle=-2)
        c.text(plan['subtitle'],(600,1400),875,70,p['ink'],heavy=True,max_size=50,angle=-2,role='text_subtitle')
    elif layout == 'landscape':
        draw_title(c,plan,105,260)
        c.paper((995,950),(601,920),p['second'],'backing_color',angle=5)
        c.paper((1010,935),(590,915),p['paper'],'backing_grid',angle=-3,grid=True)
        place_photo(c,photo,(600,918,1050,975),angle=0,cutout=False)
        c.tape((229,487),-18); c.tape((986,1260),18)
        c.paper((940,115),(600,1450),p['paper'],'caption_strip',angle=1)
        c.text(plan['subtitle'],(600,1450),865,66,p['ink'],heavy=True,max_size=49,angle=1,role='text_subtitle')
    elif layout == 'simple':
        draw_title(c,plan,110,260)
        c.paper((1060,910),(600,910),p['second'],'backing_color',angle=0)
        place_photo(c,photo,(600,910,1050,900),angle=0,cutout=False)
        c.text(plan['subtitle'],(600,1450),1050,100,p['ink'] if plan['palette']=='archive' else p['paper'],heavy=True,max_size=48,role='text_subtitle')
    # A restrained press impression affects the whole sheet consistently, without obscuring details.
    rng=np.random.default_rng(seed+10001)
    noise=rng.normal(0,1,(H,W))
    grain=np.zeros((H,W,4),dtype=np.uint8)
    grain[:,:,:3]=np.where(noise[:,:,None]>0,255,0)
    grain[:,:,3]=np.minimum(np.abs(noise)*4,13).astype('uint8')
    c.add(Image.fromarray(grain),(W//2,H//2),'print_grain')
    c.image.convert('RGB').save(dest/'final.png')
    return c


def make_bundle(source, plan, dest):
    dest.mkdir(parents=True, exist_ok=False)
    validate_plan(plan)
    write_json(dest/'plan.json',plan)
    photo,mask,unchanged=prepare_photo(source,dest,plan)
    c=compose(dest,plan,photo)
    fonts=dest/'fonts';shutil.copytree(SKILL/'assets/fonts',fonts)
    # Save exact compositor and replay helper so the result survives later skill updates.
    shutil.copyfile(Path(__file__),dest/'renderer.py')
    shutil.copyfile(SKILL/'scripts/replay.py',dest/'replay.py')
    with Image.open(dest/'final.png') as final_image:
        valid_dimensions = final_image.size == (1200,1600)
    hard=c.checks + [
        {'name':'source_rgb_matches_allowed_transform','pass':bool(unchanged)},
        {'name':'source_not_regenerated','pass':True,'evidence':'Local RGB source -> optional grayscale -> alpha mask -> similarity transforms only'},
        {'name':'group_landscape_whole','pass':plan['category'] not in ['group','landscape'] or plan['photo_mode']=='whole'},
        {'name':'png_3_4','pass':valid_dimensions},
    ]
    files={str(p.relative_to(dest)):digest(p) for p in dest.rglob('*') if p.is_file()}
    record={'version':1,'canvas':[W,H],'layers':c.layers,'files':files,'runtime':{'python':platform.python_version(),'pillow':PIL_VERSION,'numpy':np.__version__,'platform':platform.platform()},'mask':mask,'photo_boxes':c.photo_boxes,'text_boxes':c.text_boxes,'requires_visual_review':REVIEW_KEYS}
    write_json(dest/'record.json',record)
    write_json(dest/'checks.json',{'all_hard_checks_pass':all(x['pass'] for x in hard),'checks':hard,'limitations':['Mask completeness, semantic correctness, readable rendered glyphs, aesthetics and subject occlusion require Agent visual review.','Source RGB checks establish allowed processing, not complete preservation of the alpha-masked subject.']})
    tool=os.environ.get('VISUAL_SKILLS_VISION')
    if tool:
        try:
            subprocess.run([tool,'ocr',str(dest/'final.png'),str(dest/'ocr.json')],check=True,capture_output=True,timeout=60)
        except (subprocess.CalledProcessError,subprocess.TimeoutExpired):
            write_json(dest/'ocr.json',{'available':False,'note':'Read rendered text visually.'})
    return {'hard_pass':all(x['pass'] for x in hard),'bundle':str(dest)}


def render(args):
    root=Path(args.output).resolve()
    source=Path(args.input).resolve()
    if not source.is_file():raise ValueError('Input photo not found')
    plan=read_json(args.plan);validate_plan(plan)
    if root.exists() and any(root.iterdir()):raise ValueError('Output directory must be new or empty; prior runs are immutable')
    root.mkdir(parents=True,exist_ok=True)
    # Keep source at the run root to ensure later attempts always return to the original photograph.
    original=root/('original'+source.suffix.lower());shutil.copyfile(source,original)
    state={'version':1,'created_at':datetime.now(timezone.utc).isoformat(),'source':original.name,'source_sha256':digest(original),'category':plan['category'],'attempts':[],'status':'needs_review','human_acceptance':'pending'}
    perform_attempt(root,state,plan)


def perform_attempt(root,state,plan):
    n=len(state['attempts'])
    if n>2:raise ValueError('Repair budget exhausted; start a separately labeled development run for changed code')
    if n==2:
        plan=dict(plan,layout='simple',photo_mode='whole')
    elif plan['layout']=='simple':
        raise ValueError('Simple fallback is reserved for attempt 2')
    source=root/state['source']
    if digest(source)!=state['source_sha256']:raise ValueError('Original photo changed since first attempt')
    if plan['category']!=state['category']:raise ValueError('Category cannot change during repair')
    dest=root/f'attempt-{n}'
    attempt={'index':n,'layout':plan['layout'],'photo_mode':plan['photo_mode'],'bundle':dest.name,'status':'needs_review'}
    try:
        result=make_bundle(source,plan,dest)
        attempt['hard_pass']=result['hard_pass']
    except Exception as error:
        attempt['status']='error';attempt['error']=str(error)
        dest.mkdir(exist_ok=True);write_json(dest/'error.json',{'message':str(error)})
    state['attempts'].append(attempt)
    state['status']='failed' if n==2 and attempt['status']=='error' else ('needs_repair' if attempt['status']=='error' else 'needs_review')
    write_json(root/'state.json',state)
    print(json.dumps({'run':str(root),'attempt':attempt,'status':state['status']},ensure_ascii=False,indent=2))


def repair(args):
    root=Path(args.run).resolve();state=read_json(root/'state.json')
    if state['status']!='needs_repair':raise ValueError('Repair requires a rejected/error attempt; inspect and record review first')
    plan=read_json(args.plan)
    previous_path=root/state['attempts'][-1]['bundle']/'plan.json'
    previous=read_json(previous_path)
    if plan.get('formal_copy')!=previous.get('formal_copy'):raise ValueError('Formal copy cannot change during repair')
    perform_attempt(root,state,plan)


def review(args):
    root=Path(args.run).resolve();state=read_json(root/'state.json')
    if state['status']!='needs_review':raise ValueError('Run does not have an unreviewed rendered attempt')
    data=read_json(args.review)
    for key in REVIEW_KEYS:
        if type(data.get(key)) is not bool:raise ValueError('Review must explicitly provide boolean '+key)
    if not isinstance(data.get('notes'),str) or not data['notes'].strip():raise ValueError('Visual review needs concrete notes')
    if not data.get('reviewer'):raise ValueError('Review must name the reviewer')
    attempt=state['attempts'][-1];dest=root/attempt['bundle']
    passed=bool(attempt['hard_pass']) and all(data[k] for k in REVIEW_KEYS)
    write_json(dest/'visual-review.json',data)
    attempt['status']='passed' if passed else 'rejected'
    if passed:
        state['status']='simple_pass' if attempt['index']==2 else 'complex_pass'
        shutil.copyfile(dest/'final.png',root/'final.png')
        state['accepted_bundle']=attempt['bundle']
    else:
        state['status']='failed' if attempt['index']==2 else 'needs_repair'
    write_json(root/'state.json',state)
    print(json.dumps({'run':str(root),'status':state['status'],'human_acceptance':state['human_acceptance']},ensure_ascii=False))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('render');p.add_argument('--input',required=True);p.add_argument('--plan',required=True);p.add_argument('--output',required=True);p.set_defaults(func=render)
    p=sub.add_parser('repair');p.add_argument('--run',required=True);p.add_argument('--plan',required=True);p.set_defaults(func=repair)
    p=sub.add_parser('review');p.add_argument('--run',required=True);p.add_argument('--review',required=True);p.set_defaults(func=review)
    args=parser.parse_args()
    try:args.func(args)
    except (ValueError,OSError,KeyError,json.JSONDecodeError) as error:
        print(str(error),file=sys.stderr);return 1
    return 0

if __name__=='__main__':raise SystemExit(main())
