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
    'w': (0xD6, 0xCE, 0xC6, 255),  # white fur shade (cooler)
    'B': (0x8B, 0x7A, 0x66, 255),  # tabby base: grey-brown taupe (h32 s27 v55)
    'b': (0x3B, 0x2C, 0x24, 255),  # tabby stripe: near-black warm (v23, 20 points under the shadow)
    'L': (0xB4, 0xA1, 0x80, 255),  # tabby light: warmer, yellower (h38 v71)
    'G': (0x9C, 0xB6, 0x4E, 255),  # eye: hazel green (h75)
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
    'd': (0x66, 0x52, 0x4A, 255),  # tabby shadow: cooler, greyer (h17 s27 v40)
    'l': (0xCB, 0xB9, 0x9A, 255),  # tabby highlight (cards only)
    'x': (0xB9, 0xB0, 0xA8, 255),  # white deep shade (chin / under-jaw)
    'e': (0xC3, 0xD3, 0x7A, 255),  # eye light (cards only)
    'q': (0xF5, 0xC6, 0xD0, 255),  # pink light (inner ear, nose highlight)
    '9': (0x2A, 0x1F, 0x1A, 255),  # deep shadow line (folds), darker than the stripe
    '1': (0xB3, 0xD4, 0xF2, 255),  # plush blue light
    '2': (0x86, 0xB6, 0xE6, 255),  # plush blue base
    '5': (0x2B, 0x3A, 0x67, 255),  # samurai haori indigo (2.16.0)
    '6': (0x1C, 0x26, 0x48, 255),  # haori indigo shadow / folds
    '7': (0x3E, 0x51, 0x90, 255),  # haori indigo light
    '4': (0x3A, 0x3A, 0x44, 255),  # hakama charcoal
    '0': (0x26, 0x26, 0x2E, 255),  # hakama charcoal shadow
    '8': (0xB3, 0x20, 0x2A, 255),  # obi and hachimaki crimson (shade: 'r')
    '3': (0x5C, 0x8E, 0xC2, 255),  # plush blue dark
    'f': (0x4A, 0x86, 0xB0, 255),  # bath water dark
    # 2.20.0 shrine stall: Daifuku is a ginger cat and Kinsuke a ginger-and-white koi.  No existing
    # ramp is orange (the tabby is a grey-brown taupe), so ginger needs its own three tones.
    'k': (0xEF, 0xAC, 0x5E, 255),  # ginger light: warmer, yellower (h35 v94)
    'i': (0xC9, 0x76, 0x2E, 255),  # ginger base (h27 v79)
    'n': (0x8A, 0x45, 0x20, 255),  # ginger shadow: cooler, redder (h21 v54)
    # 2.20 shrine stall redesign (2026-09-18): the torii is the largest red mass and needs three tones
    # for its 3/4 read (lit left column of each post, top face of the nuki).  16 value points above 'R',
    # hue-shifted warmer, so it reads as sunlit lacquer rather than orange.
    't': (0xF0, 0x68, 0x48, 255),  # torii vermilion light (shade ramp: t > R > r)
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


class DroppedPixels(ValueError):
    """A transform pushed drawn pixels off the canvas (the ear-clipping bug class)."""


def pad(rows, w, h, dx=0, dy=0, allow_drop=False):
    """Place rows on a w x h transparent canvas, offset by (dx, dy). Raises DroppedPixels if a
    drawn pixel would fall outside the canvas, unless allow_drop=True (sinking into a pit, etc.)."""
    canvas = [['.'] * w for _ in range(h)]
    dropped = 0
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == '.':
                continue
            X, Y = x + dx, y + dy
            if 0 <= X < w and 0 <= Y < h:
                canvas[Y][X] = ch
            else:
                dropped += 1
    if dropped and not allow_drop:
        raise DroppedPixels(f'pad: {dropped} drawn pixel(s) fell off the {w}x{h} canvas at offset ({dx},{dy})')
    return [''.join(r) for r in canvas]


def shift(rows, dx=0, dy=0, allow_drop=False):
    h = len(rows); w = max(len(r) for r in rows)
    return pad(rows, w, h, dx, dy, allow_drop=allow_drop)


def flip_h(rows):
    return [r[::-1] for r in rows]


def flip_v(rows):
    return rows[::-1]


def overlay(base, top, dx=0, dy=0, allow_drop=False):
    """Draw non-transparent pixels of top onto base at offset. Raises DroppedPixels if part of
    top falls outside base (a part placed off the canvas), unless allow_drop=True."""
    h = len(base); w = max(len(r) for r in base)
    canvas = [list(r.ljust(w, '.')) for r in base]
    dropped = 0
    for y, row in enumerate(top):
        for x, ch in enumerate(row):
            if ch == '.':
                continue
            X, Y = x + dx, y + dy
            if 0 <= X < w and 0 <= Y < h:
                canvas[Y][X] = ch
            else:
                dropped += 1
    if dropped and not allow_drop:
        raise DroppedPixels(f'overlay: {dropped} pixel(s) of the part fell off the {w}x{h} canvas at ({dx},{dy})')
    return [''.join(r) for r in canvas]


def overlay_clip(base, top, dx=0, dy=0):
    """overlay() that clips silently: for item/VFX/card art where parts may leave the canvas."""
    return overlay(base, top, dx, dy, allow_drop=True)


def pad_clip(rows, w, h, dx=0, dy=0):
    return pad(rows, w, h, dx, dy, allow_drop=True)


def shift_clip(rows, dx=0, dy=0):
    return shift(rows, dx, dy, allow_drop=True)


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


def _content_rows(rows):
    ys = [y for y, r in enumerate(rows) if any(ch != '.' for ch in r)]
    return (ys[0], ys[-1]) if ys else (None, None)


def squash(rows, factor_h):
    """Vertically squash the drawn content toward its bottom row (nearest-neighbour, sampled from the
    bottom so the bottom row - the feet outline - is always kept and never moves)."""
    top, bottom = _content_rows(rows)
    if top is None:
        return rows
    n = bottom - top + 1
    nh = max(1, round(n * factor_h))
    w = max(len(r) for r in rows)
    out = ['.' * w] * len(rows)
    for y in range(nh):
        src = bottom - int((nh - 1 - y) / factor_h)
        out[bottom - (nh - 1 - y)] = rows[max(top, src)]
    return out


def scale_down(rows, factor, anchor='bottom'):
    """Shrink the drawn content on both axes (nearest-neighbour). anchor='bottom' keeps the bottom row
    and the horizontal centre; 'center' keeps the centre of the content box."""
    top, bottom = _content_rows(rows)
    if top is None:
        return rows
    w = max(len(r) for r in rows)
    xs = [x for r in rows for x, ch in enumerate(r) if ch != '.']
    left, right = min(xs), max(xs)
    n, m = bottom - top + 1, right - left + 1
    nh, nw = max(1, round(n * factor)), max(1, round(m * factor))
    out = [['.'] * w for _ in rows]
    cx = (left + right) // 2
    x0 = cx - nw // 2
    y0 = bottom - nh + 1 if anchor == 'bottom' else (top + bottom) // 2 - nh // 2
    for y in range(nh):
        sy = bottom - int((nh - 1 - y) / factor)
        sy = max(top, sy)
        for x in range(nw):
            sx = left + min(m - 1, int(x / factor))
            ch = rows[sy][sx] if sx < len(rows[sy]) else '.'
            X, Y = x0 + x, y0 + y
            if 0 <= X < w and 0 <= Y < len(rows):
                out[Y][X] = ch
    return [''.join(r) for r in out]


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


def strip_outline(rows):
    """Body frames ship WITHOUT an outline: Enter the Gungeon draws a 1-px black outline around the
    player sprite (and hands) at runtime (SpriteOutlineManager in PlayerController.Start). A baked
    outline would double it. 'o' becomes transparent; interior 'o' lines render black in game."""
    return [''.join('.' if ch == 'o' else ch for ch in r) for r in rows]


def outline_img(im, color=(0, 0, 0, 255), threshold=12):
    """Preview-only: add a 1-px 4-neighbour outline around opaque pixels, like the game does."""
    im = im.convert('RGBA')
    w, h = im.size
    src = im.load()
    out = Image.new('RGBA', (w + 2, h + 2), (0, 0, 0, 0))
    dst = out.load()
    for y in range(h):
        for x in range(w):
            if src[x, y][3] > threshold:
                dst[x + 1, y + 1] = src[x, y]
    for y in range(h + 2):
        for x in range(w + 2):
            if dst[x, y][3] > threshold:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w + 2 and 0 <= ny < h + 2 and dst[nx, ny][3] > threshold and dst[nx, ny] != color:
                    dst[x, y] = color
                    break
    return out
