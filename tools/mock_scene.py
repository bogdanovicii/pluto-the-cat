"""Compose an in-game style mock-up from the real sprites (floor, Pluto + gun, Coco, Wet Pluto, Puffed Up, HUD).
Usage: python3 tools/mock_scene.py  -> docs/art-preview/ingame-mock.png
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)

from pixel import img_from_rows, recolor, PALETTE, strip_outline, outline_img  # noqa: E402
import character_anims as A  # noqa: E402
import ui_and_items as U  # noqa: E402
import art_v3 as V3  # noqa: E402
import art_v4 as V4  # noqa: E402
import art_v5 as V5  # noqa: E402
import poses as P  # noqa: E402
import fur as FUR  # noqa: E402

SCALE = 5
W, H = 300, 170                      # logical pixels
im = Image.new('RGBA', (W, H), (0, 0, 0, 255))
d = ImageDraw.Draw(im)

# ---------------------------------------------------------------- floor: Gungeon-style stone tiles with grout, darker band at the top (wall)
for y in range(0, H, 16):
    for x in range(0, W, 16):
        shade = 46 + ((x // 16 + y // 16) % 2) * 6
        d.rectangle([x, y, x + 15, y + 15], fill=(shade, shade - 2, shade + 6, 255))
        d.line([(x, y), (x + 15, y)], fill=(38, 36, 46, 255))
        d.line([(x, y), (x, y + 15)], fill=(38, 36, 46, 255))
d.rectangle([0, 0, W, 22], fill=(30, 26, 34, 255))                 # back wall
d.rectangle([0, 22, W, 25], fill=(70, 62, 80, 255))                # wall lip
for x in range(0, W, 24):                                          # wall bricks
    d.rectangle([x, 4, x + 20, 18], outline=(44, 40, 52, 255))


def paste(rows, x, y, scale=1.0, mirror=False, body=False):
    """body=True: a player body frame -> outline stripped and re-added the way the game renders it
    (the outline image is 1 px larger on every side, so it is placed at x-1, y-1)."""
    sp = img_from_rows(rows)
    if body:
        sp = outline_img(img_from_rows(strip_outline(rows)))
        x, y = x - 1, y - 1
    if mirror:
        sp = sp.transpose(Image.FLIP_LEFT_RIGHT)
    if scale != 1.0:
        sp = sp.resize((max(1, round(sp.width * scale)), max(1, round(sp.height * scale))), Image.NEAREST)
    im.alpha_composite(sp, (int(x), int(y)))
    return sp


def shadow(x, y, w):
    d.ellipse([x, y, x + w, y + 4], fill=(22, 20, 28, 255))


# ---------------------------------------------------------------- 1. Pluto with the Royal Canin bag, kibble flying, Coco behind
px, py = 60, 64                       # frames are 26 tall: feet fill on row 24
shadow(px + 4, py + 25, 18)
paste(A.IDLE_SIDE[0], px, py, body=True)
# bag: PrimaryHand attach is (7, 5) px from the sprite's bottom-left; Pluto's paw sits at about (px+21, py+13)
gx, gy = px + 21 - 7, py + 19 - (V3.GUN_H - 5)
paste(V3.GUN_FIRE[0], gx, gy)
paste(P.HAND, px + 19, py + 17, body=True)
for i, (kx, ky) in enumerate(((gx + 34, gy + 6), (gx + 46, gy + 5), (gx + 58, gy + 7), (gx + 68, gy + 11))):
    paste(U.KIBBLE, kx, ky)
# Coco Blue trailing behind, with a crumb
shadow(px - 26, py + 25, 14)
paste(V4.COCO_MOVE[1], px - 28, py + 14, body=True)
paste(U.CRUMB, px - 10, py + 26)

# ---------------------------------------------------------------- 2. Wet Pluto with the gravy pouch beside the bathtub
wx, wy = 150, 60
paste(U.BATHTUB, wx - 40, wy - 2)
shadow(wx + 4, wy + 25, 18)
paste(A.ALT_CLIPS['idle'][0], wx, wy, body=True)
paste(V4.GUN2_FIRE[0], wx + 21 - 4, wy + 19 - (V4.GUN2_H - 4))
paste(recolor(P.HAND, A.WET_MAP), wx + 19, wy + 17, body=True)
for gxx, gyy in ((wx + 46, wy + 14), (wx + 58, wy + 16)):
    paste(V4.GRAVY, gxx, gyy)

# ---------------------------------------------------------------- 3. Puffed Up Pluto: halo behind, body scaled 1.25, anger marks above
ax, ay = 228, 56
shadow(ax + 4, ay + 25, 18)
paste(FUR.fur_layer(A.CLIPS['idle'][0], 2), ax - FUR.MARGIN_X, ay - FUR.MARGIN_TOP)
paste(A.CLIPS['idle'][0], ax, ay, body=True)
paste(V5.ANGER_MARKS[2], ax + 12, ay - 8)
paste(V4.FUR_PUFF[1], ax - 8, ay + 8)

# ---------------------------------------------------------------- 4. Wet Food Can thrown + splash with hearts, kibble bowl
cx, cy = 118, 122
paste(V3.CAN_TOSS[1], cx - 30, cy - 18)
paste(V3.GRAVY_BURST[2], cx, cy)
paste(V4.LOVE_BURST[2], cx + 18, cy - 10)
paste(V4.BOWL_PICKUP, cx + 44, cy + 8)
# a running Pluto heading for the bowl
shadow(cx + 70, cy + 19, 18)
paste(A.RUN_SIDE[0], cx + 66, cy - 6, body=True)

# ---------------------------------------------------------------- HUD: face card + hearts (top-left), items + ammo (bottom-right)
paste(U.framed_38(V3.FACE_34), 4, 4)
heart = img_from_rows([".oo.oo.", "oHHoHHo", "oHHHHHo", ".oHHHo.", "..oHo..", "...o..."])
for i in range(3):
    im.alpha_composite(heart, (46 + i * 9, 8))
# blanks
for i in range(2):
    d.ellipse([46 + i * 8, 18, 51 + i * 8, 23], fill=(230, 230, 240, 255), outline=(30, 22, 20, 255))
# item slots bottom-right: active (can) + passives (nine lives, coco, puffed up)
slot = 26
sx = W - slot - 4
d.rectangle([sx, H - slot - 4, sx + slot, H - 4], fill=(28, 24, 32, 255), outline=(90, 80, 100, 255))
paste(V3.CAN_ICON, sx + 3, H - slot - 1)
for i, icon in enumerate((U.NINE_LIVES_ICON, V4.COCO_IDLE_1, V5.PUFFED_ICON)):
    x = sx - (i + 1) * 20
    d.rectangle([x, H - 22, x + 18, H - 4], fill=(28, 24, 32, 255), outline=(70, 62, 80, 255))
    paste(icon, x + 1, H - 21)
# ammo readout: the bag icon + infinite sign
paste(V3.GUN_AMMONOMICON, W - 34, H - slot - 40, scale=0.8)
d.text((W - 16, H - 40), "∞", fill=(240, 235, 220, 255))
# Nine Lives banner (as the notification bar would show it)
d.rectangle([98, 4, 202, 20], fill=(70, 36, 92, 255), outline=(150, 110, 180, 255))
paste(U.NINE_LIVES_ICON, 101, 4)
try:
    font = ImageFont.load_default(size=8)
except TypeError:
    font = ImageFont.load_default()
d.text((120, 5), "NINE LIVES", fill=(245, 235, 255, 255), font=font)
d.text((120, 12), "Eighth life.", fill=(210, 190, 230, 255), font=font)

out = im.resize((W * SCALE, H * SCALE), Image.NEAREST)
os.makedirs(os.path.join(ROOT, 'docs', 'art-preview'), exist_ok=True)
path = os.path.join(ROOT, 'docs', 'art-preview', 'ingame-mock.png')
out.save(path)
print(path, out.size)
