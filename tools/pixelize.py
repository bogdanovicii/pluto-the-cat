"""Turn generated reference images into sprite-sized pixel art.

Pipeline per object: flood-fill the white background to transparent from the corners, find the
separate objects on the sheet (gaps in the column/row projections), crop one, fit it into the target
canvas keeping aspect, downscale with a box filter, quantize to a small palette, optionally snap every
colour to the mod palette (tools/pixel.py) and redraw a 1-px dark outline around the silhouette.
"""
import os
from PIL import Image, ImageDraw
from pixel import PALETTE

OUTLINE = PALETTE['o'][:3]


def strip_background(im, tol=28):
    """Flood-fill near-white background to transparent, starting from the four corners."""
    im = im.convert('RGBA')
    w, h = im.size
    px = im.load()
    seen = bytearray(w * h)
    stack = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    while stack:
        x, y = stack.pop()
        if x < 0 or y < 0 or x >= w or y >= h or seen[y * w + x]:
            continue
        r, g, b, a = px[x, y]
        if a == 0 or (255 - r) > tol or (255 - g) > tol or (255 - b) > tol:
            continue
        seen[y * w + x] = 1
        px[x, y] = (0, 0, 0, 0)
        stack.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
    return im


def objects(im, min_gap=14, min_size=20):
    """Bounding boxes of separate opaque objects, left-to-right (uses column gaps, then row gaps)."""
    im = im.convert('RGBA')
    w, h = im.size
    alpha = im.split()[3]
    cols = [any(alpha.getpixel((x, y)) > 8 for y in range(0, h, 2)) for x in range(w)]
    boxes = []
    x = 0
    while x < w:
        if not cols[x]:
            x += 1; continue
        x0 = x
        gap = 0
        while x < w and gap < min_gap:
            gap = gap + 1 if not cols[x] else 0
            x += 1
        x1 = x - gap
        sub = alpha.crop((x0, 0, x1, h))
        bbox = sub.getbbox()
        if bbox and (x1 - x0) >= min_size and (bbox[3] - bbox[1]) >= min_size:
            boxes.append((x0 + bbox[0], bbox[1], x0 + bbox[2], bbox[3]))
    return boxes


def grid(im, cols, rows):
    """Equal cells of a grid sheet (e.g. a 2x2 portrait sheet)."""
    w, h = im.size
    cw, ch = w // cols, h // rows
    return [(c * cw, r * ch, (c + 1) * cw, (r + 1) * ch) for r in range(rows) for c in range(cols)]


def nearest_palette(rgb):
    best, bd = None, 1e9
    for k, v in PALETTE.items():
        if v is None or v[3] < 255:
            continue
        d = (v[0] - rgb[0]) ** 2 + (v[1] - rgb[1]) ** 2 + (v[2] - rgb[2]) ** 2
        if d < bd:
            best, bd = v[:3], d
    return best


def pixelize(im, box, size, colors=14, snap=False, outline=True, pad=0, fill_canvas=False):
    """Crop `box` from an RGBA image and render it as size=(w,h) pixel art."""
    crop = im.crop(box)
    tw, th = size
    if fill_canvas:
        fitted = crop.resize((tw, th), Image.BOX)
    else:
        # fit inside the canvas keeping aspect, centred at the bottom
        scale = min((tw - 2 * pad) / crop.width, (th - 2 * pad) / crop.height)
        nw, nh = max(1, round(crop.width * scale)), max(1, round(crop.height * scale))
        small = crop.resize((nw, nh), Image.BOX)
        fitted = Image.new('RGBA', (tw, th), (0, 0, 0, 0))
        fitted.paste(small, ((tw - nw) // 2, th - pad - nh))
    # quantize the opaque pixels
    rgb = fitted.convert('RGB').quantize(colors=colors, method=Image.MEDIANCUT).convert('RGB')
    out = Image.new('RGBA', (tw, th), (0, 0, 0, 0))
    src = fitted.load(); q = rgb.load(); o = out.load()
    for y in range(th):
        for x in range(tw):
            a = src[x, y][3]
            if a < 96:
                continue
            c = q[x, y]
            if snap:
                c = nearest_palette(c)
            o[x, y] = (c[0], c[1], c[2], 255)
    if outline:
        edge = []
        for y in range(th):
            for x in range(tw):
                if o[x, y][3] == 0:
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if nx < 0 or ny < 0 or nx >= tw or ny >= th or o[nx, ny][3] == 0:
                        edge.append((x, y)); break
        for x, y in edge:
            o[x, y] = OUTLINE + (255,)
    return out


def upscale(im, s):
    return im.resize((im.width * s, im.height * s), Image.NEAREST)
