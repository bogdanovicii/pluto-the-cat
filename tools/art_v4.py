"""Version 2.2 art: Coco Blue companion, gravy pouch alt gun, kibble bowl pickup, fur-puff and love-burst VFX,
pop-in select card.

Palette keys added in pixel.py for this file: 1/2/3 plush blue (light/base/dark).
"""
from pixel import check_rect as R, overlay_clip as overlay, pad_clip as pad, shift_clip as shift, flip_h, scale_down, squash
from pixel import pad as _pad_strict, shift as _shift_strict
from art_v3 import CROWN, blank, put, row, col

# Coco's clips live on a 17 x 16 canvas: 3 rows above the 13-row drawing for the 3-px hop and 1 column on the right
# for the pet wiggle. Bottom-left anchored, so the C# hitbox offsets (3,2) do not move. Strict pad/shift: before 2.15.1
# the hop frames were shifted on the bare 16 x 13 drawing and silently lost the ears and the top of the head.
COCO_W, COCO_H = 17, 16


def _room(drawing):
    return _pad_strict(drawing, COCO_W, COCO_H, 0, COCO_H - len(drawing))

# ---------------------------------------------------------------- Coco Blue: round blue plush cat, 16 x 13
# Photo: reference/photos/coco/coco_blue_1.png. Blue oval body, white belly, tiny red-lined ears, stub paws,
# embroidered face: closed happy eyes, white muzzle with a pink nose, whiskers.
COCO_IDLE_1 = R([
"..oo........oo..",
".o1Ro......oR2o.",
".o122ooooo222o..",
"o1122222222223o.",
"o12222222222233o",
"o1222o22o2222W3o",
"o122222222222W3o",
"o12o2WWWW2o22W3o",
"o1222WPqW2222W3o",
"o22222WW22222W3o",
".o32222222222Wo.",
".oo3322222233oo.",
"..oo.oooooo.oo..",
])
COCO_IDLE_2 = R([  # breathe: a touch wider
"..oo........oo..",
".o1Ro......oR2o.",
".o122ooooo222o..",
"o1122222222223o.",
"o12222222222233o",
"o1222o22o2222W3o",
"o122222222222W3o",
"o12o2WWWW2o22W3o",
"o1222WPqW2222W3o",
"o22222WW22222W3o",
"o332222222222Wo.",
".oo3322222233oo.",
"..oo.oooooo.oo..",
])
_I1, _I2 = _room(COCO_IDLE_1), _room(COCO_IDLE_2)
COCO_IDLE = [_I1, _I1, _I2, _I2]
# hop cycle: squash, stretch up, land
COCO_MOVE = [
    squash(_I1, 0.85),
    _shift_strict(_I1, 0, -2),
    _shift_strict(_I2, 0, -3),
    _shift_strict(_I1, 0, -1),
    _I1,
    squash(_I2, 0.9),
]

# ---------------------------------------------------------------- gravy pouch (Wet Pluto's alt gun), 24 x 14, opening on the right
# A Royal Canin wet-food pouch: gold-silver foil with a pink label, crown, tear notch and gravy at the spout.
GUN2_W, GUN2_H = 24, 14


def pouch():
    c = blank(GUN2_W, GUN2_H)
    c = put(c, R([
    "..oooooooooooooooooo....",
    ".oAAAAAAAAAAAAAAAAAAo...",
    "oAAYYYYYYYYYYYYYYYYYAo..",
    "oAYIIIIIIIIIIIIIIIIYao..",
    "oAYIWWWWWWWWWWWWWIIYaoo.",
    "oAYIWWWWWWWWWWWWWIIYaoM.",
    "oAYIWWWWWWWWWWWWWIIYaoMM",
    "oAYIWWWWWWWWWWWWWIIYaoM.",
    "oAYIIIIIIIIIIIIIIIIYao..",
    "oAYYYYYYYYYYYYYYYYYYao..",
    "oaaaaaaaaaaaaaaaaaaaao..",
    ".oooooooooooooooooooo...",
    "........................",
    "........................",
    ]), 0, 0)
    c = put(c, CROWN, 5, 4)
    c = put(c, ["RRRRRRRRRRRR"], 4, 7)
    for x in (6, 9, 12):
        c = put(c, ['K'], x, 7)
    c = put(c, ['s'], 21, 3)   # tear notch
    return c


GUN2_IDLE = pouch()
_SQUIRT = blank(GUN2_W, GUN2_H)
_SQUIRT = put(_SQUIRT, ['M'], 23, 4)
_SQUIRT = put(_SQUIRT, ['M'], 23, 8)
GUN2_FIRE = [overlay(shift(GUN2_IDLE, -1, 0), _SQUIRT), GUN2_IDLE]
GUN2_RELOAD = [shift(GUN2_IDLE, 0, 1), shift(GUN2_IDLE, 1, 0), GUN2_IDLE]

GRAVY = R([  # 7 x 7 glob
"..ooo..",
".oMMMo.",
"oMKMMMo",
"oMMMMmo",
"oMMMmmo",
".ommmo.",
"..ooo..",
])

# ---------------------------------------------------------------- kibble bowl pickup, 12 x 9
BOWL_PICKUP = R([
"...ooooo....",
"..oMmMMmMo..",
".oMMmMMMMMo.",
"oNNNNNNNNNNo",
".oNsNNNNsNo.",
"..oNNNNNNo..",
"...oosoo....",
"....oooo....",
"............",
])
BOWL_PICKUP_2 = shift(BOWL_PICKUP, 0, -1)

# ---------------------------------------------------------------- fur puff VFX, 4 frames 16 x 16
FUR_PUFF = [
    R([
"................",
"................",
"................",
"................",
"......W.........",
".....WBW.B......",
"....B.WWW.W.....",
".....WWBWW......",
"....W.WWW.B.....",
".....B.W.W......",
"................",
"................",
"................",
"................",
"................",
"................",
    ]),
    R([
"................",
"................",
".....W....B.....",
"...B..WW.W......",
"....WW.WW..W....",
"..W.WBWWWBW.B...",
"...WWW.W.WWW....",
"..B.WWWWWWW.W...",
"....W.WBW.W.....",
"..W..WW.WW..B...",
"...B...W...W....",
"................",
"................",
"................",
"................",
"................",
    ]),
    R([
"................",
"...W......B.....",
".B..W..W....W...",
"...W..B..W......",
".W..W.....W..B..",
"..B...W.W...W...",
".....W...B......",
"..W....W....W...",
".B..B.....B.....",
"....W..W..W..B..",
"..W.....W.......",
"...B..W....W....",
"................",
"................",
"................",
"................",
    ]),
    R([
"..W..........B..",
".....B...W......",
"W.......B....W..",
"...W........B...",
".B.....W........",
"......B....W....",
"..W.........B...",
".....W..........",
"B........W......",
"...B..W.....W...",
".W..........B...",
"......W.........",
"...B......B.....",
".W.....W........",
"................",
"................",
    ]),
]

# ---------------------------------------------------------------- love burst VFX (can splash), 4 frames 16 x 16
_H = R([".oo.oo.", "oHHoHHo", "oHHHHHo", ".oHHHo.", "..oHo..", "...o..."])
_h = R([".o.o.", "oHoHo", "oHHHo", ".oHo.", "..o.."])


def _love(stage):
    c = blank(16, 16)
    c = put(c, ["MM"], 7, 12)
    if stage == 0:
        c = put(c, _h, 5, 8)
    elif stage == 1:
        c = put(c, _H, 4, 5); c = put(c, _h, 11, 9)
    elif stage == 2:
        c = put(c, _H, 2, 2); c = put(c, _H, 9, 3); c = put(c, _h, 6, 8)
    else:
        c = put(c, _h, 1, 0); c = put(c, _h, 11, 0); c = put(c, _h, 6, 2)
    return c


LOVE_BURST = [_love(i) for i in range(4)]


# ---------------------------------------------------------------- Coco being petted: happy wiggle (eyes squeezed, cheeks up), 4 frames
COCO_PET_1 = R([
"..oo........oo..",
".o1Ro......oR2o.",
".o122ooooo222o..",
"o1122222222223o.",
"o12222222222233o",
"o122o2o2o2o22W3o",
"o1222222222223o.",
"o12qq2WWWW2qqW3o",
"o1222WPqW2222W3o",
"o22222WW22222W3o",
".o32222222222Wo.",
".oo3322222233oo.",
"..oo.oooooo.oo..",
])
_P1 = _room(COCO_PET_1)
COCO_PET = [_P1, squash(_P1, 0.92), _P1, _shift_strict(_P1, 1, 0)]


# ---------------------------------------------------------------- Coco blocking a bullet: squish flat with ">.<" eyes and a spark, 3 frames
COCO_BLOCK_1 = R([
"................",
"................",
"................",
"..oo........oo..",
".o1Ro......oR2o.",
"o1122ooooo2223o.",
"o12222222222233o",
"o12o2o2222o2oW3o",
"o122o22WWWW22W3o",
"o1222WWWPqWW2W3o",
"o22222WWWWW22W3o",
".oo3322222233oo.",
"..oo.oooooo.oo..",
])
_B1 = _room(COCO_BLOCK_1)
COCO_BLOCK = [squash(_B1, 0.9), _B1, _shift_strict(_B1, 0, -1)]

# Decoy mode: Coco with a determined face, running (used as the move clip while decoying)
COCO_DECOY_1 = R([
"..oo........oo..",
".o1Ro......oR2o.",
".o122ooooo222o..",
"o1122222222223o.",
"o12222222222233o",
"o1222oo2o2o22W3o",
"o1222o2222o22W3o",
"o12o2WWWW2o22W3o",
"o1222WPqW2222W3o",
"o22222WW22222W3o",
".o32222222222Wo.",
".oo3322222233oo.",
"..oo.oooooo.oo..",
])
_D1 = _room(COCO_DECOY_1)
COCO_DECOY = [squash(_D1, 0.85), _shift_strict(_D1, 0, -3), _shift_strict(_D1, 0, -1), _D1]

# Squeaky Toy icon 16 x 16: a little blue Coco-shaped squeaky toy with a nozzle, squeaking
SQUEAKER_ICON = R([
"...K.......K....",
"..KKK.....KKK...",
"...K.......K....",
"....oo....oo....",
"...o12o..o22o...",
"...o1222oo222o..",
"..o12222222223o.",
"..o12o22o2222Wo.",
"..o122WWW22222o.",
"..o122WPW2222Wo.",
"...o32222222Wo..",
"....oo3222oo....",
"......oSSo......",
"......osso......",
".......oo.......",
"................",
])

# Bullet-pop spark VFX for the block, 3 frames 12 x 12
def _spark(stage):
    c = blank(12, 12)
    if stage == 0:
        c = put(c, R([".K.", "KKK", ".K."]), 4, 4)
    elif stage == 1:
        c = put(c, R(["K...K", ".K.K.", "..K..", ".K.K.", "K...K"]), 3, 3)
    else:
        c = put(c, R(["K.....K", ".......", "..K.K..", ".......", "..K.K..", ".......", "K.....K"]), 2, 2)
    return c


BLOCK_SPARK = [_spark(i) for i in range(3)]


# ---------------------------------------------------------------- Coco knocked out: flat on his back, feet up, X eyes, stars (16 x 16, 2 frames)
_KO_BODY = R([
"..oo.oooooo.oo..",
".oo3322222233oo.",
".o32222222222Wo.",
"o22222WW22222W3o",
"o1222WPqW2222W3o",
"o12o2WWWW2o22W3o",
"o122o2o2o2o22W3o",
"o1222o222o222W3o",
"o122o2o2o2o22W3o",
"o1122222222223o.",
".o122ooooo222o..",
".o1Ro......oR2o.",
"..oo........oo..",
])
_STAR = R([".K.", "KKK", ".K."])
_STAR_S = R(["K"])


def _ko(stage):
    c = blank(16, 16)
    c = put(c, _KO_BODY, 0, 3)
    if stage == 0:
        c = put(c, _STAR, 2, 0); c = put(c, _STAR_S, 12, 1)
    else:
        c = put(c, _STAR_S, 3, 1); c = put(c, _STAR, 10, 0)
    return c


COCO_KO = [_ko(0), _ko(1)]


# ---------------------------------------------------------------- 2.14 Knighted: Coco Blue + Ser Junkan at Holy Knight
# Junkan bakes each armour level into its own clip set (junk_shspcg_* is the Holy Knight) and swaps clip names at
# runtime; Coco does the same. The tin kettle helmet (gold band, red plume) is drawn onto every base drawing BEFORE
# the clip's squash/shift, so it squashes and hops with him. Canvas grows to 17 x 20: 7 rows above the 13-row
# drawing leave room for the plume on the 3-px hop. Strict pad/overlay/shift: a clipped plume raises.
from pixel import overlay as _overlay_strict

KNIGHT_W, KNIGHT_H = COCO_W, 20
KNIGHT_TOP = KNIGHT_H - 13
# 9 x 8, plume swept back; the bottom row (dark gold brim edge) sits on the drawing's row 3, between the ears. Light from top-left:
# tin S -> Z -> z, gold A -> a -> y, plume R / r.
HELMET = R([
"......oo.",
".....oRRo",
"....oRro.",
"..oooroo.",
".oSSSZZzo",
"oSSZZZZzo",
"oAAAAAAao",
"yaaaaaaay",
])
# the helmet on the floor, tipped on its side with the plume flopped out (9 x 5)
HELMET_DOWN = R([
"..ooooo..",
".oSSSZzo.",
"oRoSZZZzo",
"orAAAAAao",
".ooooooo.",
])


def _knight(drawing, head_dy=0):
    c = _pad_strict(drawing, KNIGHT_W, KNIGHT_H, 0, KNIGHT_TOP)
    return _overlay_strict(c, HELMET, 3, KNIGHT_TOP - 4 + head_dy)


KNIGHT_IDLE_1 = _knight(COCO_IDLE_1)
KNIGHT_IDLE_2 = _knight(COCO_IDLE_2)
KNIGHT_PET_1 = _knight(COCO_PET_1)
KNIGHT_BLOCK_1 = _knight(COCO_BLOCK_1, head_dy=3)     # the block drawing's head sits 3 rows lower

# same timing and transforms as the plain clips
COCO_KNIGHT_IDLE = [KNIGHT_IDLE_1, KNIGHT_IDLE_1, KNIGHT_IDLE_2, KNIGHT_IDLE_2]
COCO_KNIGHT_MOVE = [
    squash(KNIGHT_IDLE_1, 0.85),
    _shift_strict(KNIGHT_IDLE_1, 0, -2),
    _shift_strict(KNIGHT_IDLE_2, 0, -3),
    _shift_strict(KNIGHT_IDLE_1, 0, -1),
    KNIGHT_IDLE_1,
    squash(KNIGHT_IDLE_2, 0.9),
]
COCO_KNIGHT_PET = [KNIGHT_PET_1, squash(KNIGHT_PET_1, 0.92), KNIGHT_PET_1, _shift_strict(KNIGHT_PET_1, 1, 0)]
COCO_KNIGHT_BLOCK = [squash(KNIGHT_BLOCK_1, 0.9), KNIGHT_BLOCK_1, _shift_strict(KNIGHT_BLOCK_1, 0, -1)]
# knocked out: the helmet came off and lies beside him (24 x 16)
COCO_KNIGHT_KO = [_overlay_strict(_pad_strict(COCO_KO[i], 24, 16, 0, 0), HELMET_DOWN, 15, 11) for i in range(2)]


# ---------------------------------------------------------------- 2.16.3 Squire: Ser Junkan's pot helmet below Holy Knight
# Vanilla Ser Junkan (Peasant to Knight Commander) wears a grey tin pot with a dark visor slit; Coco gets the same pot
# while Squire is active, and the gold plumed HELMET above from Holy Knight up. Same 17 x 20 canvas, anchor and
# transforms as the knight set, so the two swap cleanly. 8 x 7, centred so both ears stay out: dome, highlight top-left, visor slit ('9', the darkest
# shared colour), dark rim; the bottom row sits on the drawing's row 3 between the ears. Tin S -> Z -> z, glint K.
POT_HELMET = R([
"..oooo..",
".oKSSZo.",
"oKSSSZzo",
"oSSSZZzo",
"o999999o",
"oSZZZZzo",
"ozzzzzzo",
])
# knocked off: the pot on its side, opening (dark) to the left (9 x 5)
POT_HELMET_DOWN = R([
"..ooooo..",
".o9SSSZo.",
"o99SSZZzo",
".o9ZZZzo.",
"..ooooo..",
])


def _squire(drawing, head_dy=0):
    c = _pad_strict(drawing, KNIGHT_W, KNIGHT_H, 0, KNIGHT_TOP)
    return _overlay_strict(c, POT_HELMET, 4, KNIGHT_TOP - 3 + head_dy)


SQUIRE_IDLE_1 = _squire(COCO_IDLE_1)
SQUIRE_IDLE_2 = _squire(COCO_IDLE_2)
SQUIRE_PET_1 = _squire(COCO_PET_1)
SQUIRE_BLOCK_1 = _squire(COCO_BLOCK_1, head_dy=3)

COCO_SQUIRE_IDLE = [SQUIRE_IDLE_1, SQUIRE_IDLE_1, SQUIRE_IDLE_2, SQUIRE_IDLE_2]
COCO_SQUIRE_MOVE = [
    squash(SQUIRE_IDLE_1, 0.85),
    _shift_strict(SQUIRE_IDLE_1, 0, -2),
    _shift_strict(SQUIRE_IDLE_2, 0, -3),
    _shift_strict(SQUIRE_IDLE_1, 0, -1),
    SQUIRE_IDLE_1,
    squash(SQUIRE_IDLE_2, 0.9),
]
COCO_SQUIRE_PET = [SQUIRE_PET_1, squash(SQUIRE_PET_1, 0.92), SQUIRE_PET_1, _shift_strict(SQUIRE_PET_1, 1, 0)]
COCO_SQUIRE_BLOCK = [squash(SQUIRE_BLOCK_1, 0.9), SQUIRE_BLOCK_1, _shift_strict(SQUIRE_BLOCK_1, 0, -1)]
COCO_SQUIRE_KO = [_overlay_strict(_pad_strict(COCO_KO[i], 24, 16, 0, 0), POT_HELMET_DOWN, 15, 11) for i in range(2)]
