#!/usr/bin/env python3
"""Copy a generated illustration faithfully into pixel-perfect game art.

usage:
  pixelize.py in.png --grid WxH --out out.png
      [--crop x0,y0,x1,y1]        fractions (0-1) or pixels of the source to keep, before gridding
      [--bg auto|none|RRGGBB] [--bg-tol 40]   remove a flat background by flood fill from the borders
      [--colors N | --palette file.txt]       build an N-colour palette, or snap to hex colours (one per line)
      [--keep RRGGBB --keep ...]   accent colours always added to the palette (small areas like eyes, labels
                                   get merged away by median cut otherwise)
      [--outline RRGGBB]           add a 1-art-pixel outline outside the silhouette where it is missing
      [--despeckle]                replace single stray pixels with their neighbours' majority (default on)
      [--scale K]                  integer upscale of the art
      [--canvas WxH --place X,Y]   paste onto a transparent canvas (negative X/Y bleed off the edge)

Steps: crop -> background mask -> palette -> each grid cell takes the MAJORITY palette colour of its source
pixels (hard edges, no averaging) -> cell is transparent when most of it is background -> despeckle -> outline
-> integer scale -> place. Alpha is only 0 or 255. Prints the colour count and opaque share.
"""
import argparse
import sys
from collections import Counter, deque
from PIL import Image


def parse_pair(s, sep='x', cast=int):
    a, b = s.lower().split(sep)
    return cast(a), cast(b)


def hexrgb(h):
    h = h.strip().lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def crop(im, spec):
    vals = [float(v) for v in spec.split(',')]
    if all(0 <= v <= 1 for v in vals):
        vals = [vals[0] * im.width, vals[1] * im.height, vals[2] * im.width, vals[3] * im.height]
    return im.crop(tuple(int(round(v)) for v in vals))


def bg_mask(im, mode, tol):
    """True where the pixel is background (flood fill from the border through similar colours)."""
    w, h = im.size
    px = im.load()
    if mode == 'none':
        return [[px[x, y][3] < 128 for x in range(w)] for y in range(h)]
    if mode == 'auto':
        corners = [px[0, 0], px[w - 1, 0], px[0, h - 1], px[w - 1, h - 1]]
        ref = Counter(c[:3] for c in corners).most_common(1)[0][0]
    else:
        ref = hexrgb(mode)
    t2 = tol * tol
    close = lambda c: c[3] < 128 or sum((c[i] - ref[i]) ** 2 for i in range(3)) <= t2
    seen = [[False] * w for _ in range(h)]
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if close(px[x, y]) and not seen[y][x]:
                seen[y][x] = True; q.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            if close(px[x, y]) and not seen[y][x]:
                seen[y][x] = True; q.append((x, y))
    while q:
        x, y = q.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < w and 0 <= ny < h and not seen[ny][nx] and close(px[nx, ny]):
                seen[ny][nx] = True; q.append((nx, ny))
    return seen


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('--grid', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--crop')
    ap.add_argument('--bg', default='auto')
    ap.add_argument('--bg-tol', type=int, default=40)
    ap.add_argument('--colors', type=int, default=24)
    ap.add_argument('--palette')
    ap.add_argument('--keep', action='append', default=[], help='accent hex colour to keep in the palette')
    ap.add_argument('--outline')
    ap.add_argument('--no-despeckle', action='store_true')
    ap.add_argument('--scale', type=int, default=1)
    ap.add_argument('--canvas')
    ap.add_argument('--place', default='0,0')
    a = ap.parse_args()

    im = Image.open(a.src).convert('RGBA')
    if a.crop:
        im = crop(im, a.crop)
    gw, gh = parse_pair(a.grid)
    # work at a bounded resolution so the per-cell vote stays fast (>= 6 source px per cell)
    step = max(1, min(im.width // (gw * 6), im.height // (gh * 6)))
    if step > 1:
        im = im.resize((im.width // step, im.height // step), Image.BOX)
    bg = bg_mask(im, a.bg, a.bg_tol)

    rgb = Image.new('RGB', im.size, (0, 0, 0))
    rgb.paste(im.convert('RGB'))
    if a.palette:
        cols = [hexrgb(l) for l in open(a.palette) if l.strip() and not l.startswith('#!')]
        pal_img = Image.new('P', (1, 1))
        cols += [hexrgb(h) for h in a.keep]
        flat = [v for c in cols for v in c]
        pal_img.putpalette(flat + [0] * (768 - len(flat)))
        q = rgb.quantize(palette=pal_img, dither=Image.Dither.NONE)
    else:
        fg = [rgb.getpixel((x, y)) for y in range(im.height) for x in range(im.width) if not bg[y][x]]
        sample = Image.new('RGB', (len(fg), 1)); sample.putdata(fg)
        pal_img = sample.quantize(colors=a.colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
        if a.keep:
            base = pal_img.getpalette()[:a.colors * 3]
            flat = base + [v for h in a.keep for v in hexrgb(h)]
            pal_img = Image.new('P', (1, 1))
            pal_img.putpalette(flat + [0] * (768 - len(flat)))
        q = rgb.quantize(palette=pal_img, dither=Image.Dither.NONE)
    pal = q.getpalette()
    qpx = q.load()

    cw, ch = im.width / gw, im.height / gh
    grid = [[None] * gw for _ in range(gh)]
    for gy in range(gh):
        for gx in range(gw):
            x0, x1 = int(gx * cw), max(int(gx * cw) + 1, int((gx + 1) * cw))
            y0, y1 = int(gy * ch), max(int(gy * ch) + 1, int((gy + 1) * ch))
            votes, bgn, n = Counter(), 0, 0
            for y in range(y0, min(y1, im.height)):
                for x in range(x0, min(x1, im.width)):
                    n += 1
                    if bg[y][x]:
                        bgn += 1
                    else:
                        votes[qpx[x, y]] += 1
            if n and bgn * 2 < n and votes:
                i = votes.most_common(1)[0][0]
                grid[gy][gx] = tuple(pal[i * 3:i * 3 + 3])

    if not a.no_despeckle:
        for _ in range(2):
            changed = 0
            for gy in range(gh):
                for gx in range(gw):
                    c = grid[gy][gx]
                    nb = [grid[gy + dy][gx + dx] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                          if 0 <= gx + dx < gw and 0 <= gy + dy < gh]
                    if nb and all(v != c for v in nb):
                        top = Counter(nb).most_common(1)[0][0]
                        grid[gy][gx] = top; changed += 1
            if not changed:
                break

    if a.outline:
        oc = hexrgb(a.outline)
        add = []
        for gy in range(gh):
            for gx in range(gw):
                if grid[gy][gx] is None and any(
                        0 <= gx + dx < gw and 0 <= gy + dy < gh and grid[gy + dy][gx + dx] not in (None, oc)
                        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    add.append((gx, gy))
        for gx, gy in add:
            grid[gy][gx] = oc

    art = Image.new('RGBA', (gw, gh), (0, 0, 0, 0))
    for gy in range(gh):
        for gx in range(gw):
            if grid[gy][gx] is not None:
                art.putpixel((gx, gy), grid[gy][gx] + (255,))
    if a.scale > 1:
        art = art.resize((gw * a.scale, gh * a.scale), Image.NEAREST)
    if a.canvas:
        cw_, ch_ = parse_pair(a.canvas)
        px_, py_ = parse_pair(a.place, ',')
        canvas = Image.new('RGBA', (cw_, ch_), (0, 0, 0, 0))
        canvas.paste(art, (px_, py_), art)
        art = canvas
    art.save(a.out)
    alpha = art.getchannel('A').tobytes()
    colours = {c for c, al in zip(art.convert('RGB').getdata(), alpha) if al}
    print(f'wrote {a.out} {art.size} colours={len(colours)} opaque={100 * sum(1 for v in alpha if v) / len(alpha):.1f}%')
    return 0


if __name__ == '__main__':
    sys.exit(main())
