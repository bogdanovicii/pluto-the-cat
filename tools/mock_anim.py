"""Animated in-game mock: Pluto runs through a Gungeon room firing kibble from the Royal Canin bag with
Coco Blue trailing, stops, breathes, dodge-rolls and idles again. Body frames are drawn the way the game
renders them (runtime outline), clips run at Alexandria's frame rates, and movement is per real frame
(30 fps), independent of the animation rate, as in the game.

Usage: python3 tools/mock_anim.py -> docs/art-preview/ingame-anim.gif (+ .png APNG)
"""
import os
import sys
import math
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)

from pixel import img_from_rows, strip_outline, outline_img  # noqa: E402
import character_anims as A  # noqa: E402
import ui_and_items as U  # noqa: E402
import art_v3 as V3  # noqa: E402
import art_v4 as V4  # noqa: E402
import poses as P  # noqa: E402
import preview as V  # noqa: E402

SCALE = 4
W, H = 290, 118                 # logical pixels
FPS = 30
DT = 1 / FPS


def floor_and_hud():
    im = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    for y in range(0, H, 16):
        for x in range(0, W, 16):
            shade = 46 + ((x // 16 + y // 16) % 2) * 6
            d.rectangle([x, y, x + 15, y + 15], fill=(shade, shade - 2, shade + 6, 255))
            d.line([(x, y), (x + 15, y)], fill=(38, 36, 46, 255))
            d.line([(x, y), (x, y + 15)], fill=(38, 36, 46, 255))
    d.rectangle([0, 0, W, 22], fill=(30, 26, 34, 255))                 # back wall
    d.rectangle([0, 22, W, 25], fill=(70, 62, 80, 255))                # wall lip
    for x in range(0, W, 24):
        d.rectangle([x, 4, x + 20, 18], outline=(44, 40, 52, 255))
    # HUD: face card, hearts, blanks (top-left); items + ammo (bottom-right)
    im.alpha_composite(img_from_rows(U.framed_38(V3.FACE_34)), (4, 4))
    heart = img_from_rows([".oo.oo.", "oHHoHHo", "oHHHHHo", ".oHHHo.", "..oHo..", "...o..."])
    for i in range(3):
        im.alpha_composite(heart, (46 + i * 9, 8))
    for i in range(2):
        d.ellipse([46 + i * 8, 18, 51 + i * 8, 23], fill=(230, 230, 240, 255), outline=(30, 22, 20, 255))
    slot = 26
    sx = W - slot - 4
    d.rectangle([sx, H - slot - 4, sx + slot, H - 4], fill=(28, 24, 32, 255), outline=(90, 80, 100, 255))
    im.alpha_composite(img_from_rows(V3.CAN_ICON), (sx + 3, H - slot - 1))
    for i, icon in enumerate((U.NINE_LIVES_ICON, V4.COCO_IDLE_1, V4.SQUEAKER_ICON)):
        x = sx - (i + 1) * 20
        d.rectangle([x, H - 22, x + 18, H - 4], fill=(28, 24, 32, 255), outline=(70, 62, 80, 255))
        ic = img_from_rows(icon)
        im.alpha_composite(ic, (x + 1 + (18 - ic.width) // 2, H - 21 + (16 - ic.height) // 2))
    bag = img_from_rows(V3.GUN_AMMONOMICON)
    im.alpha_composite(bag.resize((19, 26), Image.NEAREST), (W - 34, H - slot - 40))
    d.text((W - 14, H - 40), "∞", fill=(240, 235, 220, 255))
    return im


BASE = floor_and_hud()
KIBBLE = img_from_rows(U.KIBBLE)
HAND = outline_img(img_from_rows(strip_outline(P.HAND)))
BAG_IDLE = img_from_rows(V3.GUN_IDLE)
BAG_FIRE = [img_from_rows(f) for f in V3.GUN_FIRE]
HAND_PT = (7, V3.GUN_H - 5)         # PrimaryHand attach (7 px from the left, 5 from the bottom) as image coords
CASING_PT = (29, V3.GUN_H - 7)
GUN_ANCHOR = (21, 19)               # where the paw sits on Pluto's canvas (chest front, fixed to the transform)

# timeline (seconds): run+fire -> idle -> dodge -> idle
T_RUN, T_IDLE1, T_DODGE, T_IDLE2 = 1.2, 1.0, 9 / 13, 1.2
T_TOTAL = T_RUN + T_IDLE1 + T_DODGE + T_IDLE2
RUN_SPEED = 104                     # px/s (about 6.5 units/s)
ROLL_SPEED = 60


def pluto_state(t):
    """(clip, frame index, x, gun visible)"""
    x0 = 10
    if t < T_RUN:
        return 'run_right_hand', int(t * 9) % 6, x0 + RUN_SPEED * t, True
    x1 = x0 + RUN_SPEED * T_RUN
    t -= T_RUN
    if t < T_IDLE1:
        return 'idle_hand', int(t * 6) % 4, x1, True
    t -= T_IDLE1
    if t < T_DODGE:
        return 'dodge_left', min(8, int(t * 13)), x1 + ROLL_SPEED * t, False
    x2 = x1 + ROLL_SPEED * T_DODGE
    t -= T_DODGE
    return 'idle_hand', int(t * 6) % 4, x2, True


def shadow(d, x, y, w):
    d.ellipse([x, y, x + w, y + 4], fill=(22, 20, 28, 255))


FRAMES_CACHE = {}


def body(clip, i):
    key = (clip, i)
    if key not in FRAMES_CACHE:
        FRAMES_CACHE[key] = V.game_frame(A.CLIPS[clip][i])
    return FRAMES_CACHE[key]


COCO = [V.game_frame(f) for f in V4.COCO_MOVE]
COCO_IDLE = [V.game_frame(f) for f in V4.COCO_IDLE]


def render(t):
    im = BASE.copy()
    d = ImageDraw.Draw(im)
    clip, fi, px, gun = pluto_state(t)
    py = 48                                          # canvas top; feet on row 24 -> floor y 72
    # kibble in flight: volleys every 0.25 s while running, two kibbles each, flying right
    shots = []
    if t < T_RUN:
        for k in range(int(t / 0.25) + 1):
            ts = k * 0.25
            age = t - ts
            if 0 <= age < 0.6:
                sx0 = 10 + RUN_SPEED * ts + GUN_ANCHOR[0] - HAND_PT[0] + CASING_PT[0]
                sy0 = py + GUN_ANCHOR[1] - HAND_PT[1] + CASING_PT[1]
                for j, dy in enumerate((-1, 1)):
                    shots.append((sx0 + age * 180, sy0 + dy * age * 14 - 2))
    # Coco trails behind with a delay
    cx = pluto_state(max(0, t - 0.3))[2] - 30
    cy = py + 14
    shadow(d, cx + 1, cy + 12, 14)
    coco = COCO[int(t * 8) % 6] if abs(pluto_state(t)[2] - pluto_state(max(0, t - DT))[2]) > 0.1 or t < T_RUN + 0.3 else COCO_IDLE[int(t * 6) % 4]
    im.alpha_composite(coco, (int(cx) - 1, cy - 1))
    # Pluto
    shadow(d, int(px) + 4, py + 25, 18)
    fr = body(clip, fi)
    im.alpha_composite(fr, (int(px) - 1, py - 1))
    if gun:
        firing = t < T_RUN and (t % 0.25) < 0.12
        bag = BAG_FIRE[0] if firing else BAG_IDLE
        gx = int(px) + GUN_ANCHOR[0] - HAND_PT[0]
        gy = py + GUN_ANCHOR[1] - HAND_PT[1]
        im.alpha_composite(bag, (gx, gy))
        im.alpha_composite(HAND, (int(px) + GUN_ANCHOR[0] - 2, py + GUN_ANCHOR[1] - 2))
    for sx, sy in shots:
        if sx < W:
            im.alpha_composite(KIBBLE, (int(sx), int(sy)))
    return im


def main():
    out = os.path.join(ROOT, 'docs', 'art-preview')
    os.makedirs(out, exist_ok=True)
    n = int(T_TOTAL * FPS)
    frames = []
    for k in range(n):
        im = render(k * DT)
        frames.append(im.resize((W * SCALE, H * SCALE), Image.NEAREST))
    frames[0].save(os.path.join(out, 'ingame-anim.png'), save_all=True, append_images=frames[1:], duration=int(1000 / FPS), loop=0)
    pal = [f.convert('RGB').quantize(colors=128, method=Image.MEDIANCUT, dither=Image.Dither.NONE) for f in frames]
    pal[0].save(os.path.join(out, 'ingame-anim.gif'), save_all=True, append_images=pal[1:], duration=int(1000 / FPS), loop=0, optimize=False)
    render(0.55).resize((W * SCALE, H * SCALE), Image.NEAREST).save(os.path.join(out, 'ingame-anim-still.png'))
    print(f'{n} frames ->', out)


if __name__ == '__main__':
    main()
