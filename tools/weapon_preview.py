"""Weapon alignment inspection sheets: Pluto's body with each player weapon attached at the hand for several aims.

Usage: python3 tools/weapon_preview.py  (also run by tools/make_art.py)
Writes docs/art-preview/weapons/<weapon>-<costume>.png.

Every number comes from tools/weapon_layout.py (the source of the .jtk2d files and src/WeaponLayout.cs).
Markers: green cross = PrimaryHand grip, red cross = Casing/muzzle, orange line = aim ray from the muzzle,
yellow circle = katana swing reach (1.85 x |Casing - PrimaryHand| with the runtime Casing push),
cyan box = the body frame's drawn content box (the player's physics collider is engine-defined and not shown).

This is an approximation of the engine transform, not a capture: the gun pivots on its grip at a fixed hand
anchor on the side-view body, aims to the left mirror the body and flip the gun vertically (tk2d FlipY), and the
katana swing frames are moved down by the layout's grip offset exactly as KatanaGun.ShiftSwingFrames does.
Up/down aims in game switch to the front/back body clips and may draw the gun behind the body; verify in-game.
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)

import weapon_layout as WL  # noqa: E402

OUT = os.path.join(ROOT, 'docs', 'art-preview', 'weapons')
WC = os.path.join(ROOT, 'PlutoTheCat', 'Resources', 'SpriteRoot', 'WeaponCollection')
SCALE = 4
CELL = 150                         # logical pixels per aim cell
HAND_ANCHOR = (21, 19)             # paw position on the 24x26 side-view body canvas (image coords), as in tools/mock_anim.py
AIMS = [('right', 0), ('up-right', 45), ('down-right', -45), ('left (flipped)', 180), ('up-left', 135), ('down-left', -135)]
FLOOR = (52, 50, 58, 255)
FONT = ImageFont.load_default(size=28)
TITLE_H = 48


def bodies():
    """costume -> (idle_hand body frame image with the runtime outline, paw image)."""
    import preview as V
    from pixel import img_from_rows, strip_outline, outline_img
    import character_anims as A
    import poses as P
    normal = (V.game_frame(A.CLIPS['idle_hand'][0]), outline_img(img_from_rows(strip_outline(P.HAND))))
    import samurai
    clips, _, hand = samurai.build()
    sam = (V.game_frame(clips['idle_hand'][0]), outline_img(img_from_rows(strip_outline(hand))))
    return {'normal': normal, 'samurai': sam}


def frame_path(spec, clip):
    name = f"{spec['sprite']}_{clip}_001.png"
    if clip == 'fire' and 'swing_grip' in spec:
        name = f"{spec['sprite']}_fire_004.png"      # mid-swing, blade out
    return os.path.join(WC, name)


def place_gun(canvas, gun, grip, anchor, angle, flip):
    """Paste gun (RGBA, 1x) rotated around its grip (bottom-left pixel coords) onto canvas so the grip lands on anchor
    (canvas coords at SCALE). Inverse-maps each canvas pixel into gun space with nearest sampling."""
    big = gun.resize((gun.width * SCALE, gun.height * SCALE), Image.NEAREST)
    a = math.radians(angle)
    ca, sa = math.cos(a), math.sin(a)
    gx, gy = grip[0] * SCALE, (gun.height - grip[1]) * SCALE        # grip in the scaled image (y down)
    ax, ay = anchor
    # world (y up) offset d = (X - ax, ay - Y); gun offset v = R(-a) d; flip: v.y = -v.y; image = (gx + v.x, gy - v.y)
    fy = -1 if flip else 1
    A_ = ca
    B_ = -sa
    C_ = gx - ca * ax + sa * ay
    D_ = fy * sa
    E_ = fy * ca
    F_ = gy - fy * sa * ax - fy * ca * ay
    layer = big.transform(canvas.size, Image.AFFINE, (A_, B_, C_, D_, E_, F_), resample=Image.NEAREST)
    canvas.alpha_composite(layer)

    def to_canvas(px, py):
        vx, vy = (px - grip[0]) * SCALE, (py - grip[1]) * SCALE * fy
        return ax + ca * vx - sa * vy, ay - (sa * vx + ca * vy)
    return to_canvas


def cross(d, x, y, color, r=5):
    d.line([(x - r, y), (x + r, y)], fill=color, width=2)
    d.line([(x, y - r), (x, y + r)], fill=color, width=2)


def cell(body, paw, spec, clip, angle, label):
    im = Image.new('RGBA', (CELL * SCALE, CELL * SCALE), FLOOR)
    d = ImageDraw.Draw(im)
    left = 90 < angle % 360 < 270
    bw, bh = body.width * SCALE, body.height * SCALE
    bx, by = (CELL * SCALE - bw) // 2, (CELL * SCALE - bh) // 2 + 10 * SCALE
    b = body.resize((bw, bh), Image.NEAREST)
    hx = HAND_ANCHOR[0] + 1                               # +1: the outlined frame is 1 px larger on each side
    if left:
        b = b.transpose(Image.FLIP_LEFT_RIGHT)
        hx = body.width - 1 - hx
    im.alpha_composite(b, (bx, by))
    box = b.getbbox()
    d.rectangle([bx + box[0], by + box[1], bx + box[2] - 1, by + box[3] - 1], outline=(80, 220, 230, 255))
    anchor = (bx + hx * SCALE, by + (HAND_ANCHOR[1] + 1) * SCALE)
    gun = Image.open(frame_path(spec, clip)).convert('RGBA')
    grip = spec['swing_grip'] if (clip == 'fire' and 'swing_grip' in spec) else spec['hand']
    to_canvas = place_gun(im, gun, grip, anchor, angle, left)
    p = paw.resize((paw.width * SCALE, paw.height * SCALE), Image.NEAREST)
    im.alpha_composite(p, (int(anchor[0] - p.width / 2), int(anchor[1] - p.height / 2)))
    # the muzzle in gun space: katana fire frames are shifted, so the jtk2d Casing still sits at the idle muzzle
    mx, my = spec['muzzle']
    if clip == 'fire' and 'swing_grip' in spec:
        mx, my = mx, my + WL.swing_grip_offset(spec)
    muzzle = to_canvas(mx, my)
    a = math.radians(angle)
    d.line([muzzle, (muzzle[0] + math.cos(a) * 30 * SCALE, muzzle[1] - math.sin(a) * 30 * SCALE)], fill=(255, 150, 40, 255), width=2)
    if 'casing_reach_units' in spec:
        r = WL.swing_radius_px(spec) * SCALE
        d.ellipse([anchor[0] - r, anchor[1] - r, anchor[0] + r, anchor[1] + r], outline=(250, 220, 60, 255), width=2)
    cross(d, *anchor, (60, 230, 90, 255))
    cross(d, *muzzle, (240, 60, 60, 255))
    d.text((6, 6), f'{label}  ({clip})', fill=(240, 235, 220, 255), font=FONT)
    return im


def sheet(key, spec, body, paw):
    clips = ['idle', 'fire'] if 'swing_grip' in spec else ['idle']
    out = Image.new('RGBA', (CELL * SCALE * len(AIMS), CELL * SCALE * len(clips) + TITLE_H), (24, 22, 28, 255))
    for r, clip in enumerate(clips):
        for c, (label, angle) in enumerate(AIMS):
            out.paste(cell(body, paw, spec, clip, angle, label), (c * CELL * SCALE, TITLE_H + r * CELL * SCALE))
    d = ImageDraw.Draw(out)
    title = (f"{key} on {spec['costume']} Pluto: grip {spec['hand']} muzzle {spec['muzzle']} canvas {spec['canvas']}"
             + (f"; swing grip {spec['swing_grip']} (offset {WL.swing_grip_offset(spec)} px), reach {WL.swing_radius_px(spec) / 16:.2f} u"
                if 'swing_grip' in spec else '')
             + '  |  green=grip red=muzzle orange=aim yellow=swing reach cyan=body box (approximate engine transform)')
    d.text((8, 8), title, fill=(240, 235, 220, 255), font=FONT)
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    body_for = bodies()
    written = []
    for key, spec in WL.WEAPONS.items():
        body, paw = body_for[spec['costume']]
        path = os.path.join(OUT, f"{key}-{spec['costume']}.png")
        sheet(key, spec, body, paw).convert('RGB').save(path, optimize=True)
        written.append(path)
    return written


if __name__ == '__main__':
    for p in main():
        print(p)
