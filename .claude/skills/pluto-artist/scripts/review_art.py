#!/usr/bin/env python3
"""Automated review of a finished art PNG, plus a review sheet to look at.

usage:
  review_art.py art.png [--kind bosscard|winpic|icon|item|sprite] [--scale K] [--max-colours N] [--allow-stray N]
                [--mock screenshot.png --mock-rect x0,y0,x1,y1] [--out review.png]

FAIL checks (exit 1): semi-transparent pixels; more colours than allowed; stray single pixels (at art-pixel
level); broken integer scaling (a KxK block that is not one colour); target rules from references/targets.md
(boss card: 427x240, <= 30 % opaque, nothing in the top-left name area, art inside the left 45 %).
WARN checks: silhouette edge without a dark outline; very low contrast between the two most used colours.
The sheet shows the art at 1x on dark and light grounds, a 4x zoom of its busiest area, and the in-game mock
(the art composited over a screenshot crop resized to the art's canvas) when --mock is given.
"""
import argparse
import sys
from collections import Counter
from PIL import Image, ImageDraw

LIMITS = {'bosscard': 40, 'winpic': 40, 'icon': 40, 'item': 16, 'sprite': 14}


def lum(c):
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('art')
    ap.add_argument('--kind', default='item')
    ap.add_argument('--scale', type=int, default=0, help='art pixel size in output pixels (0 = detect)')
    ap.add_argument('--max-colours', type=int)
    ap.add_argument('--mock')
    ap.add_argument('--mock-rect')
    ap.add_argument('--out')
    ap.add_argument('--allow-stray', type=int, default=0,
                    help='intentional single-pixel details (paw toes, glints) to allow; name them in the review verdict')
    a = ap.parse_args()

    im = Image.open(a.art).convert('RGBA')
    W, H = im.size
    px = im.load()
    fails, warns = [], []

    alphas = Counter(px[x, y][3] for y in range(H) for x in range(W))
    semi = sum(n for v, n in alphas.items() if 0 < v < 255)
    if semi:
        fails.append(f'{semi} semi-transparent pixels (alpha must be 0 or 255)')
    opaque = [(x, y) for y in range(H) for x in range(W) if px[x, y][3] == 255]
    share = len(opaque) / (W * H)
    colours = Counter(px[x, y][:3] for x, y in opaque)
    limit = a.max_colours or LIMITS.get(a.kind, 32)
    if len(colours) > limit:
        fails.append(f'{len(colours)} colours > {limit}')

    # integer scale: detect the largest K where every KxK block is uniform
    def uniform(k):
        for by in range(0, H - H % k, k):
            for bx in range(0, W - W % k, k):
                c = px[bx, by]
                for y in range(by, by + k):
                    for x in range(bx, bx + k):
                        if px[x, y] != c:
                            return False
        return True
    k = a.scale
    if k == 0:
        k = next((kk for kk in (8, 6, 5, 4, 3, 2) if uniform(kk)), 1)
    elif k > 1 and not uniform(k):
        fails.append(f'not a clean {k}x integer scale (some {k}x{k} block has two colours)')

    # stray pixels at art-pixel level
    small = im.resize((W // k, H // k), Image.NEAREST) if k > 1 else im
    sp = small.load(); sw, sh = small.size
    stray = 0
    for y in range(sh):
        for x in range(sw):
            c = sp[x, y]
            if c[3] == 0:
                continue
            nb = [sp[x + dx, y + dy] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 0 <= x + dx < sw and 0 <= y + dy < sh]
            if nb and all(n != c for n in nb) and all(n[3] == 255 for n in nb):
                stray += 1
    if stray > max(2, len(opaque) // (k * k) // 400) + a.allow_stray:
        fails.append(f'{stray} stray single pixels (art-pixel level)')
    elif stray:
        warns.append(f'{stray} stray single pixels - check eyes/highlights are intentional')

    # outline: share of silhouette edge pixels that are dark
    edge = dark = 0
    for x, y in opaque:
        if any(not (0 <= x + dx < W and 0 <= y + dy < H) or px[x + dx, y + dy][3] == 0 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            edge += 1
            if lum(px[x, y]) < 60:
                dark += 1
    if edge and dark / edge < 0.7 and a.kind in ('bosscard', 'item', 'icon'):
        warns.append(f'only {100 * dark / edge:.0f}% of the silhouette edge is dark outline')

    if a.kind == 'bosscard':
        if (W, H) != (427, 240):
            fails.append(f'boss card must be 427x240, got {W}x{H}')
        if share > 0.30:
            fails.append(f'boss card {share:.0%} opaque (> 30 %): it would cover the boss art')
        name_area = sum(1 for x, y in opaque if x < 190 and y < 90)
        if name_area:
            fails.append(f'{name_area} opaque pixels in the top-left name area (x<190, y<90)')
        right = sum(1 for x, y in opaque if x > 0.45 * W)
        if right:
            fails.append(f'{right} opaque pixels right of x={int(0.45 * W)} (boss art side)')

    print(f'{a.art}: {W}x{H} scale={k} colours={len(colours)} opaque={share:.1%} stray={stray}')
    for f in fails:
        print('FAIL', f)
    for w in warns:
        print('warn', w)
    print('verdict:', 'FAIL' if fails else 'automated checks pass - now review against references/rubric.md')

    if a.out:
        tiles = []
        for ground in ((32, 26, 40, 255), (228, 224, 214, 255)):
            t = Image.new('RGBA', (W, H), ground); t.alpha_composite(im); tiles.append(t)
        if opaque:
            xs = [p[0] for p in opaque]; ys = [p[1] for p in opaque]
            cx, cy = sum(xs) // len(xs), sum(ys) // len(ys)
            zw, zh = min(W, 96), min(H, 64)
            box = (max(0, cx - zw // 2), max(0, cy - zh // 2))
            z = Image.new('RGBA', (zw, zh), (32, 26, 40, 255))
            z.alpha_composite(im.crop((box[0], box[1], box[0] + zw, box[1] + zh)))
            tiles.append(z.resize((zw * 4, zh * 4), Image.NEAREST))
        if a.mock:
            shot = Image.open(a.mock).convert('RGBA')
            if a.mock_rect:
                shot = shot.crop(tuple(int(v) for v in a.mock_rect.split(',')))
            m = shot.resize((W, H), Image.LANCZOS); m.alpha_composite(im)
            tiles.append(m.resize((W * 3, H * 3), Image.NEAREST))
        sheet_w = max(t.width for t in tiles) + 20
        sheet = Image.new('RGBA', (sheet_w, sum(t.height + 30 for t in tiles) + 10), (70, 66, 80, 255))
        d = ImageDraw.Draw(sheet); y = 10
        labels = ['1x on dark', '1x on light', '4x zoom (busiest area)', 'in-game mock (3x)']
        for t, label in zip(tiles, labels):
            d.text((10, y), label, fill=(240, 240, 240, 255)); y += 16
            sheet.alpha_composite(t, (10, y)); y += t.height + 14
        sheet.save(a.out)
        print('review sheet:', a.out)
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
