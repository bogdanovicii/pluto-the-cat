"""Katana fire clip as a real swing (2.16.1): the approved idle katana rotated around the grip, top to bottom,
with a steel-white smear behind the blade, like vanilla Blasphemy's swing.
Run from the repo root: python3 reference/gemini/katana/swing.py  -> reference/gemini/katana/build/swing/

Rotation is RotSprite-style so the pixels stay the approved ones: 8x nearest upscale, nearest rotation about the
grip, then each 8x8 cell takes its majority colour (no new colours, hard alpha).
The fire canvas is FIRE_W x FIRE_H with the grip at FIRE_HAND (from the bottom-left); KatanaGun.cs shifts the fire
sprite definitions by (FIRE_HAND - IDLE_HAND) / 16 so the grip stays in Pluto's paw.
"""
import math
import os
from collections import Counter
from PIL import Image, ImageDraw

SRC = 'reference/art/katana/pluto_katana_idle_001.png'
OUT = 'reference/gemini/katana/build/swing'
IDLE_HAND = (6, 13)               # grip pixel in the idle frame, from the bottom-left (make_art.py)
FIRE_W, FIRE_H = 43, 80
FIRE_HAND = (6, 40)
Z = 8

# (blade angle in degrees, positive = up when facing right; smear (from, to) or None)
FRAMES = [(75, None), (35, (80, 35)), (-15, (75, -15)), (-60, (35, -60)), (-80, (-10, -80)),
          (-65, None), (-35, None), (-10, None)]

RIM, FILL, TAIL = (0xf8, 0xf8, 0xf8, 255), (0xc8, 0xf0, 0xf0, 255), (0x60, 0xe8, 0xe0, 255)


def rotate(idle, angle):
    """Idle katana rotated by `angle` about the grip, on the fire canvas."""
    w, h = idle.size
    hx, hy = IDLE_HAND[0], h - 1 - IDLE_HAND[1]              # top-left pixel coordinates of the grip
    fx, fy = FIRE_HAND[0], FIRE_H - 1 - FIRE_HAND[1]
    big = Image.new('RGBA', (FIRE_W * Z, FIRE_H * Z), (0, 0, 0, 0))
    up = idle.resize((w * Z, h * Z), Image.NEAREST)
    big.paste(up, ((fx - hx) * Z, (fy - hy) * Z))
    cx, cy = fx * Z + Z / 2, fy * Z + Z / 2
    big = big.rotate(angle, resample=Image.NEAREST, center=(cx, cy))
    out = Image.new('RGBA', (FIRE_W, FIRE_H), (0, 0, 0, 0))
    bp, op = big.load(), out.load()
    for y in range(FIRE_H):
        for x in range(FIRE_W):
            cell = Counter(bp[x * Z + i, y * Z + j] for j in range(1, Z - 1) for i in range(1, Z - 1))
            opaque = [(c, n) for c, n in cell.items() if c[3] == 255]
            n_opaque = sum(n for _, n in opaque)
            if n_opaque * 2 >= sum(cell.values()):
                op[x, y] = max(opaque, key=lambda t: t[1])[0]
    return out


def smear(a0, a1):
    """Crescent band between two blade angles: pale cyan fill, white outer rim, cyan tail at the start angle."""
    img = Image.new('RGBA', (FIRE_W, FIRE_H), (0, 0, 0, 0))
    px = img.load()
    fx, fy = FIRE_HAND[0], FIRE_H - 1 - FIRE_HAND[1]
    lo, hi = min(a0, a1), max(a0, a1)
    for y in range(FIRE_H):
        for x in range(FIRE_W):
            dx, dy = x - fx, fy - y
            r = math.hypot(dx, dy)
            a = math.degrees(math.atan2(dy, dx))
            if not (lo <= a <= hi):
                continue
            t = (a - a1) / (a0 - a1)                      # 0 at the blade, 1 at the start of the swing
            inner = 28 + 6 * t                            # thin crescent: 7 px at the blade, 1-2 px at the tail
            if inner <= r <= 35.5:
                px[x, y] = RIM if r >= 34.2 else (TAIL if t > 0.75 else FILL)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    idle = Image.open(SRC).convert('RGBA')
    frames = []
    for i, (angle, sm) in enumerate(FRAMES, 1):
        f = Image.new('RGBA', (FIRE_W, FIRE_H), (0, 0, 0, 0))
        if sm:
            f.alpha_composite(smear(*sm))
        f.alpha_composite(rotate(idle, angle))
        f.save(f'{OUT}/pluto_katana_fire_{i:03d}.png')
        frames.append(f)
    S, PAD = 6, 2
    sheet = Image.new('RGBA', ((FIRE_W + PAD) * len(frames) * S, FIRE_H * S), (60, 58, 70, 255))
    d = ImageDraw.Draw(sheet)
    for i, f in enumerate(frames):
        x0 = i * (FIRE_W + PAD) * S
        sheet.alpha_composite(f.resize((FIRE_W * S, FIRE_H * S), Image.NEAREST), (x0, 0))
        hx, hy = x0 + FIRE_HAND[0] * S, (FIRE_H - 1 - FIRE_HAND[1]) * S
        d.rectangle([hx, hy, hx + S - 1, hy + S - 1], outline=(255, 60, 60, 255))
    sheet.save(f'{OUT}/sheet.png')
    bg = [Image.new('RGBA', (FIRE_W, FIRE_H), (74, 72, 88, 255)) for _ in frames]
    anim = []
    for b, f in zip(bg, frames + []):
        b.alpha_composite(f)
        anim.append(b.resize((FIRE_W * S, FIRE_H * S), Image.NEAREST))
    idle_bg = Image.new('RGBA', (FIRE_W, FIRE_H), (74, 72, 88, 255))
    idle_bg.alpha_composite(rotate(idle, 0))
    anim.append(idle_bg.resize((FIRE_W * S, FIRE_H * S), Image.NEAREST))
    anim[0].save(f'{OUT}/swing.png', save_all=True, append_images=anim[1:], duration=[50] * 8 + [400], loop=0)
    print('frames', len(frames), 'canvas', (FIRE_W, FIRE_H), 'grip', FIRE_HAND)


if __name__ == '__main__':
    main()
