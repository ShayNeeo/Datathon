#!/usr/bin/env python3
"""Fallback bulk annotator: add a small top-right label to every PNG under
output/figures_living so team writers can quickly identify figures.
"""
import os
import math
from PIL import Image, ImageDraw, ImageFont

REPO = '/home/shayneeo/Downloads/Datathon'
FIG_DIR = os.path.join(REPO, 'output', 'figures_living')


def get_font(sz):
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", sz)
    except Exception:
        return ImageFont.load_default()


def annotate(path):
    try:
        img = Image.open(path).convert('RGBA')
        w, h = img.size
        diag = int(math.hypot(w, h))
        font_size = max(9, min(22, diag // 220))
        font = get_font(font_size)
        draw = ImageDraw.Draw(img, 'RGBA')

        text = os.path.relpath(path, FIG_DIR)
        padding = max(6, font_size // 2)

        # measure text
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]

        x = w - tw - padding - 8
        y = padding + 8

        # draw semi-opaque box with thin outline
        bg = (255, 255, 255, 230)
        outline = (60, 60, 60, 200)
        draw.rectangle([x - padding, y - padding, x + tw + padding, y + th + padding], fill=bg, outline=outline, width=1)
        draw.text((x, y), text, fill=(30, 30, 30, 255), font=font)

        img.save(path)
        return True
    except Exception as e:
        print(f"Error annotating {path}: {e}")
        return False


if __name__ == '__main__':
    total = 0
    done = 0
    for root, dirs, files in os.walk(FIG_DIR):
        for f in files:
            if f.lower().endswith('.png'):
                total += 1
                p = os.path.join(root, f)
                if annotate(p):
                    done += 1
    print(f"Annotated {done}/{total} PNGs")
