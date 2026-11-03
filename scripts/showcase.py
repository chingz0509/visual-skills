#!/usr/bin/env python3
"""Present three actual skill outputs without changing their artwork."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FONT = ROOT / 'skills/photo-paper-collage/assets/fonts/BebasNeue-Regular.ttf'


def main():
    canvas = Image.new('RGB', (1800, 1050), '#eeeae2')
    draw = ImageDraw.Draw(canvas)
    def label(x, y, text, size, color='#252c28'):
        draw.text((x, y), text, font=ImageFont.truetype(str(FONT), size), fill=color)
    label(60, 35, 'PHOTO / PAPER / POSSIBILITIES', 70)
    label(1410, 62, 'VISUAL STYLE SKILLS', 34)
    draw.line((60, 135, 1740, 135), fill='#b7b8ad', width=2)
    cases = [('person-easy', '01 / PORTRAIT'), ('product-easy', '02 / OBJECT'),
             ('landscape-hard', '03 / LANDSCAPE')]
    for i, (case, caption) in enumerate(cases):
        x = 60 + i * 570
        # All are complete, unretouched final renders from the frozen benchmark.
        with Image.open(ROOT / 'examples' / case / 'attempt-0/final.png') as source:
            poster = source.convert('RGB').resize((540, 720), Image.Resampling.LANCZOS)
        canvas.paste(poster, (x, 175))
        label(x, 916, caption, 32)
    draw.line((60, 976, 1740, 976), fill='#b7b8ad', width=2)
    label(60, 995, 'REAL SKILL OUTPUTS / EXPERIMENTAL EDITION', 24, '#596056')
    label(1380, 995, 'KEEP THE PHOTO. MAKE A POSTER.', 24, '#596056')
    out = ROOT / 'examples/showcase.jpg'
    canvas.save(out, quality=94, subsampling=0)
    print(out)


if __name__ == '__main__':
    main()
