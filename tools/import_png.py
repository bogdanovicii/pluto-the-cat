"""PNG -> row-strings round trip, so a frame can be touched up in LibreSprite / Pixelorama / Piskel
and pasted back into tools/*.py. Colours are snapped to the nearest palette key (exact for palette
colours; off-by-a-few tones snap to the intended key). Prints Python row-string literals.

Usage: python3 tools/import_png.py frame.png [--outline]   (--outline re-adds 'o' around the fill,
for body frames that were exported without one)
"""
import sys
from PIL import Image
from pixel import PALETTE


def nearest_key(rgba):
    if rgba[3] < 128:
        return '.'
    best, bd = '?', 1e9
    for k, v in PALETTE.items():
        if v is None or v[3] < 128:
            continue
        d = sum((v[i] - rgba[i]) ** 2 for i in range(3))
        if d < bd:
            best, bd = k, d
    return best


def rows_from_png(path, outline=False):
    im = Image.open(path).convert('RGBA')
    px = im.load()
    rows = [[nearest_key(px[x, y]) for x in range(im.width)] for y in range(im.height)]
    if outline:
        for y in range(im.height):
            for x in range(im.width):
                if rows[y][x] == '.' and any(0 <= x + dx < im.width and 0 <= y + dy < im.height and rows[y + dy][x + dx] not in '.o'
                                             for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    rows[y][x] = 'o'
    return [''.join(r) for r in rows]


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    for path in args:
        print(f'# {path}')
        print('R([')
        for r in rows_from_png(path, outline='--outline' in sys.argv):
            print(f'"{r}",')
        print('])')
