"""Tiny pixel-art toolkit: ASCII maps -> PIL images, plus transforms and previews.

Every sprite in the mod is defined as a list of equal-length strings where each
character is a palette key. '.' is transparent. This keeps the art reproducible
and diff-able; run make_art.py to regenerate every PNG.
"""
from PIL import Image
import os

PALETTE = {
    '.': None,
    'o': (0x1E, 0x16, 0x14, 255),  # outline
    'W': (0xFA, 0xF6, 0xEE, 255),  # white fur
    'w': (0xD8, 0xD0, 0xC4, 255),  # white fur shade
    'B': (0x8E, 0x71, 0x50, 255),  # tabby base
    'b': (0x5A, 0x40, 0x28, 255),  # tabby dark stripe
    'L': (0xB3, 0x94, 0x73, 255),  # tabby light
    'G': (0x7D, 0xB4, 0x47, 255),  # eye green
    'g': (0x1B, 0x2A, 0x1B, 255),  # pupil
    'P': (0xE8, 0xA0, 0xB0, 255),  # pink nose / ear
    'p': (0xD4, 0x6A, 0x7A, 255),  # tongue / dark pink
    'R': (0xC8, 0x2B, 0x2B, 255),  # sack red
    'r': (0x8A, 0x1C, 0x1C, 255),  # sack red dark
    'Y': (0xE9, 0xC4, 0x5A, 255),  # kibble tan / gold
    'y': (0xB0, 0x86, 0x3A, 255),  # kibble dark
    'S': (0xB8, 0xBC, 0xC4, 255),  # can silver
    's': (0x7A, 0x80, 0x8A, 255),  # can silver dark
    'K': (0xF2, 0xF2, 0xF2, 255),  # highlight white
    'M': (0x9A, 0x6A, 0x4A, 255),  # meat / wet food
    'm': (0x6E, 0x44, 0x2C, 255),  # wet food dark
    'H': (0xFF, 0x5C, 0x8A, 255),  # heart pink
    'h': (0xC4, 0x2C, 0x5C, 255),  # heart dark
    'T': (0x00, 0x00, 0x00, 0),    # explicit transparent (alias)
    'D': (0x6E, 0x6A, 0x86, 190),  # ghost dark (translucent)
    'C': (0xA8, 0xA4, 0xC0, 190),  # ghost mid
    'c': (0xE6, 0xE4, 0xF4, 190),  # ghost light
    'X': (0x3C, 0x2E, 0x22, 255),  # bg brown (cards)
    'Q': (0x25, 0x1C, 0x14, 255),  # bg brown dark (cards)
    'E': (0xEE, 0xDD, 0xB0, 255),  # parchment light
    'V': (0x6B, 0x3F, 0x8F, 255),  # Royal Canin purple label
    'v': (0x4A, 0x28, 0x66, 255),  # purple dark
    'Z': (0x74, 0x76, 0x80, 255),  # grey cat on the bag
    'z': (0x4C, 0x4E, 0x58, 255),  # grey cat dark
    'A': (0xF3, 0xDF, 0x8E, 255),  # gold highlight (can lid)
    'a': (0xC9, 0xA8, 0x4C, 255),  # gold shade
    'N': (0xE0, 0xE2, 0xE6, 255),  # bag silver-white edge
    'I': (0xF6, 0xC8, 0xD4, 255),  # can label pink (light)
    'J': (0x5E, 0x4C, 0x3C, 255),  # wet tabby base
    'j': (0x35, 0x28, 0x1E, 255),  # wet tabby dark
    'U': (0xD6, 0xDC, 0xE6, 255),  # wet white (blue-grey)
    'u': (0xA9, 0xB2, 0xC0, 255),  # wet white shade
    'F': (0x7F, 0xB4, 0xD8, 255),  # bath water
    'd': (0x6E, 0x52, 0x38, 255),  # tabby shadow (hue-shifted toward red)
    'l': (0xCD, 0xB2, 0x8E, 255),  # tabby highlight
    'x': (0xBF, 0xB2, 0xA2, 255),  # white deep shade (chin / under-jaw)
    'e': (0xA9, 0xD6, 0x62, 255),  # eye light green
    'q': (0xF5, 0xC6, 0xD0, 255),  # pink light (inner ear, nose highlight)
    '9': (0x3A, 0x2A, 0x20, 255),  # deep shadow line (folds)
    '1': (0xB3, 0xD4, 0xF2, 255),  # plush blue light
    '2': (0x86, 0xB6, 0xE6, 255),  # plush blue base
    '3': (0x5C, 0x8E, 0xC2, 255),  # plush blue dark
    'f': (0x4A, 0x86, 0xB0, 255),  # bath water dark
}


def img_from_rows(rows, palette=PALETTE):
    w = max(len(r) for r in rows)
    h = len(rows)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    px = im.load()
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            col = palette.get(ch)
            if col is None:
                if ch not in palette and ch != '.':
                    raise KeyError(f'unknown palette key {ch!r} at ({x},{y})')
                continue
            px[x, y] = col
    return im


def rows_from_img(im, palette=PALETTE):
    inv = {v: k for k, v in palette.items() if v is not None}
    im = im.convert('RGBA')
    px = im.load()
    out = []
    for y in range(im.height):
        out.append(''.join('.' if px[x, y][3] == 0 else inv.get(px[x, y], '?') for x in range(im.width)))
    return out


def pad(rows, w, h, dx=0, dy=0):
    """Place rows on a w x h transparent canvas, offset by (dx, dy)."""
    rw = max(len(r) for r in rows)
    canvas = [['.'] * w for _ in range(h)]
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            X, Y = x + dx, y + dy
            if ch != '.' and 0 <= X < w and 0 <= Y < h:
                canvas[Y][X] = ch
    return [''.join(r) for r in canvas]


def shift(rows, dx=0, dy=0):
    h = len(rows); w = max(len(r) for r in rows)
    return pad(rows, w, h, dx, dy)


def flip_h(rows):
    return [r[::-1] for r in rows]


def flip_v(rows):
    return rows[::-1]


def overlay(base, top, dx=0, dy=0):
    """Draw non-transparent pixels of top onto base at offset."""
    h = len(base); w = max(len(r) for r in base)
    canvas = [list(r.ljust(w, '.')) for r in base]
    for y, row in enumerate(top):
        for x, ch in enumerate(row):
            X, Y = x + dx, y + dy
            if ch != '.' and 0 <= X < w and 0 <= Y < h:
                canvas[Y][X] = ch
    return [''.join(r) for r in canvas]


def erase(base, top, dx=0, dy=0):
    """Make base transparent wherever top is non-transparent."""
    h = len(base); w = max(len(r) for r in base)
    canvas = [list(r.ljust(w, '.')) for r in base]
    for y, row in enumerate(top):
        for x, ch in enumerate(row):
            X, Y = x + dx, y + dy
            if ch != '.' and 0 <= X < w and 0 <= Y < h:
                canvas[Y][X] = '.'
    return [''.join(r) for r in canvas]


def recolor(rows, mapping):
    return [''.join(mapping.get(ch, ch) for ch in r) for r in rows]


def squash(rows, factor_h):
    """Vertically squash sprite toward its bottom (nearest-neighbour row resample)."""
    h = len(rows)
    nh = max(1, round(h * factor_h))
    out = []
    for y in range(nh):
        src = min(h - 1, int(y / factor_h))
        out.append(rows[src])
    return pad(out, max(len(r) for r in rows), h, 0, h - nh)


def scale_down(rows, factor, anchor='bottom'):
    """Shrink the whole sprite (both axes) and keep it bottom-centred on the same canvas."""
    im = img_from_rows(rows)
    bbox = im.getbbox()
    if not bbox:
        return rows
    crop = im.crop(bbox)
    nw, nh = max(1, round(crop.width * factor)), max(1, round(crop.height * factor))
    small = crop.resize((nw, nh), Image.NEAREST)
    out = Image.new('RGBA', im.size, (0, 0, 0, 0))
    cx = (bbox[0] + bbox[2]) // 2
    x = cx - nw // 2
    y = bbox[3] - nh if anchor == 'bottom' else (bbox[1] + bbox[3]) // 2 - nh // 2
    out.paste(small, (x, y))
    return rows_from_img(out)


def rotate(rows, angle):
    """Rotate about centre in 90-degree steps (nearest), keeping canvas size."""
    im = img_from_rows(rows)
    im = im.rotate(angle, resample=Image.NEAREST, expand=False)
    return rows_from_img(im)


def rotate_free(rows, angle):
    im = img_from_rows(rows)
    im = im.rotate(angle, resample=Image.NEAREST, expand=False, center=(im.width / 2, im.height / 2))
    return rows_from_img(im)


def save(rows, path, scale=1):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im = img_from_rows(rows)
    if scale != 1:
        im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    im.save(path)
    return im


def sheet(frame_lists, path, scale=6, gap=2, bg=(70, 70, 90, 255)):
    """Contact sheet: each entry of frame_lists is a list of row-lists (one row per animation)."""
    ims = [[img_from_rows(f) for f in row] for row in frame_lists]
    W = max(sum(i.width * scale + gap for i in row) for row in ims)
    H = sum(max(i.height for i in row) * scale + gap for row in ims)
    out = Image.new('RGBA', (W, H), bg)
    y = 0
    for row in ims:
        x = 0
        rh = max(i.height for i in row) * scale
        for i in row:
            out.paste(i.resize((i.width * scale, i.height * scale), Image.NEAREST), (x, y))
            x += i.width * scale + gap
        y += rh + gap
    os.makedirs(os.path.dirname(path), exist_ok=True)
    out.save(path)
    return out


def check_rect(rows):
    w = len(rows[0])
    for i, r in enumerate(rows):
        assert len(r) == w, f'row {i} has width {len(r)} != {w}: {r!r}'
    return rows


def shade(rows, protect='GgPpe', bottom_x_from=0.6):
    """Rim-shading pass: shadow tone on pixels whose bottom or right neighbour is outline/transparent,
    highlight tone on tabby pixels whose top or left neighbour is outline/transparent.
    Pixels next to eyes/nose (protect) are left alone. Bottom white rim in the lower part of the
    sprite uses the deep shade ('x'), elsewhere the light shade ('w')."""
    h = len(rows); w = max(len(r) for r in rows)
    g = [list(r.ljust(w, '.')) for r in rows]
    out = [row[:] for row in g]

    def at(x, y):
        return g[y][x] if 0 <= x < w and 0 <= y < h else '.'

    def edge(ch):
        return ch in 'o.'

    for y in range(h):
        for x in range(w):
            ch = g[y][x]
            if ch not in 'BWL':
                continue
            if any(at(x + dx, y + dy) in protect for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                continue
            below, right, above, left = at(x, y + 1), at(x + 1, y), at(x, y - 1), at(x - 1, y)
            if ch == 'B':
                if edge(below) or edge(right):
                    out[y][x] = 'd'
                elif edge(above) or edge(left):
                    out[y][x] = 'L'
            elif ch == 'L':
                if edge(below) or edge(right):
                    out[y][x] = 'd'
            elif ch == 'W':
                if edge(below):
                    out[y][x] = 'x' if y >= h * bottom_x_from else 'w'
                elif edge(right):
                    out[y][x] = 'w'
    return [''.join(r) for r in out]
