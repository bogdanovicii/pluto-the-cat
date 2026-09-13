"""Version 2.2 art: Coco Blue companion, gravy pouch alt gun, kibble bowl pickup, fur-puff and love-burst VFX,
pop-in select card.

Palette keys added in pixel.py for this file: 1/2/3 plush blue (light/base/dark).
"""
from pixel import check_rect as R, overlay_clip as overlay, pad_clip as pad, shift_clip as shift, flip_h, scale_down, squash
from art_v3 import CROWN, blank, put, row, col

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
COCO_IDLE = [COCO_IDLE_1, COCO_IDLE_1, COCO_IDLE_2, COCO_IDLE_2]
# hop cycle: squash, stretch up, land
COCO_MOVE = [
    squash(COCO_IDLE_1, 0.85),
    shift(COCO_IDLE_1, 0, -2),
    shift(COCO_IDLE_2, 0, -3),
    shift(COCO_IDLE_1, 0, -1),
    COCO_IDLE_1,
    squash(COCO_IDLE_2, 0.9),
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
COCO_PET = [COCO_PET_1, squash(COCO_PET_1, 0.92), COCO_PET_1, shift(COCO_PET_1, 1, 0)]


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
COCO_BLOCK = [squash(COCO_BLOCK_1, 0.9), COCO_BLOCK_1, shift(COCO_BLOCK_1, 0, -1)]

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
COCO_DECOY = [squash(COCO_DECOY_1, 0.85), shift(COCO_DECOY_1, 0, -3), shift(COCO_DECOY_1, 0, -1), COCO_DECOY_1]

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
