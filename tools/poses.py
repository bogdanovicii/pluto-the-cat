"""Hand-drawn key poses for Pluto (18 x 20 canvas). Side poses face RIGHT; the game mirrors for left.

Palette keys: see pixel.PALETTE. '.' transparent, o outline, W/w white fur, B/b/L tabby, G/g eye, P/p pink.
"""
from pixel import check_rect as R

W, H = 18, 20

# ---------------------------------------------------------------- side (facing right)
IDLE_SIDE = R([
"......oo.....oo...",  # 0  ear tips
".....oBBo...oBBo..",  # 1
".....oBPBoooBPBo..",  # 2  pink inner ears
"....oBBBBWWBBBBBo.",  # 3
"...oBBbBWWWWBBbBBo",  # 4  cap with stripes
"...oBBBBBBBBBBBBBo",  # 5  blaze starts
"...oBBBBBWWWWBBBBo",  # 6
"...oBBWWGgWWWWGgBo",  # 7  eyes, tabby cheeks outside
"...oBWWWGgWWWWGgWo",  # 8
"...oWWWWWWWPPWWWWo",  # 9  nose
"....oWWWWWWpWWWWo.",  # 10 mouth
"....oBBBWWWWWWBBo.",  # 11 shoulders
"...oBbBBWWWWWWWBo.",  # 12
"...oBBBBWWWWWWWBo.",  # 13 tail joins
"...obBBBWWWWWWWBo.",  # 14
"...oBBBBBWwWWWBBo.",  # 15
"....oBBBwWWWwBBo..",  # 16
".....oWWo...oWWo..",  # 17 legs
".....owwo...owwo..",  # 18
"......oo.....oo...",  # 19
])

# body only (rows 0-16) and legs (rows 17-19) so runs can re-pose the legs
SIDE_BODY = IDLE_SIDE[:17] + ['.' * W] * 3
SIDE_LEG = R([  # single leg, 4 x 3
"oWWo",
"owwo",
".oo.",
])
SIDE_LEG_LONG = R([  # stretched leg for the stride
"oWWo",
"oWWo",
"owwo",
".oo.",
])

# ---------------------------------------------------------------- front (facing camera)
IDLE_FRONT = R([
"....oo......oo....",
"...oBBo....oBBo...",
"...oBPBooooBPBo...",
"..oBBBBWWWWBBBBo..",
".oBBbBBWWWWBBbBBo.",
".oBBBBBBBBBBBBBBo.",
".oBBBBBWWWWBBBBBo.",
".oBBWWgGWWWWGgWBo.",
".oBWWWgGWWWWGgWWo.",
".oWWWWWWWPPWWWWWo.",
"..oWWWWWWpWWWWWo..",
"..oBBBWWWWWWWBBBo.",
".oBBBWWWWWWWWWBBBo",
".oBBWWWWWWWWWWWBBo",
".oBBWWWWWWWWWWWBBo",
".oBBBWWWWWwWWWBBBo",
"..oBBwWWWWWWwWBBo.",
"...oWWo.....oWWo..",
"...owwo.....owwo..",
"....oo.......oo...",
])
FRONT_BODY = IDLE_FRONT[:17] + ['.' * W] * 3

# ---------------------------------------------------------------- back (facing away)
IDLE_BACK = R([
"....oo......oo....",
"...oBBo....oBBo...",
"...oBBBooooBBBo...",
"..oBBBBWWWWBBBBo..",
".oBBbBBWWWWBBbBBo.",
".oBBBbBBWWBBbBBBo.",
".oBBBBbBBBBbBBBBo.",
".oBBBBBbBBbBBBBBo.",
".oBBBBBBbbBBBBBBo.",
".oLBBBBBBBBBBBBLo.",
"..oBBBBBBBBBBBBo..",
"..oBBBbBBBBbBBBo..",
".oBBBBBbBBbBBBBBo.",
".oBBbBBBbbBBBbBBo.",
".oBBBBBBBBBBBBBBo.",
".oBBBbBBBBBBbBBo..",
"..oBBBBBBBBBBBo...",
"...oWWo.....oWWo..",
"...owwo.....owwo..",
"....oo.......oo...",
])
BACK_BODY = IDLE_BACK[:17] + ['.' * W] * 3

# ---------------------------------------------------------------- dodge ball (16 x 16, centred)
BALL = R([
"......oooo......",
"....ooBBBBoo....",
"...oBBbBBBBBo...",
"..oBBBBBBbBBBo..",
".oBbBBBWWWBBBBo.",
".oBBBBWWWWWBBBo.",
"oBBBBWWgWgWWBBBo",
"oBbBBWWWWWWWBbBo",
"oBBBBWWWPWWWBBBo",
"oBBBBBWWWWWBBBBo",
".oBBBBBWWWBbBBo.",
".oBbBBBBBBBBBBo.",
"..oBBBBBBbBBBo..",
"...oBBbBBBBBo...",
"....ooBBBBoo....",
"......oooo......",
])

# ---------------------------------------------------------------- paws up (item get / thumbs up), front
PAWS_UP = R([
"....oo......oo....",
"...oBBo....oBBo...",
"...oBPBooooBPBo...",
"..oBBBBWWWWBBBBo..",
".oBBbBBWWWWBBbBBo.",
".oBBBBBBBBBBBBBBo.",
".oBBBBBWWWWBBBBBo.",
"ooBBWWgGWWWWGgWBoo",
"WoBWWWgGWWWWGgWWoW",
"WoWWWWWWWPPWWWWWoW",
"ooWWWWWWWpWWWWWWoo",
"BoBBBWWWWWWWWBBBoB",
"BoBBWWWWWWWWWWBBoB",
"oBBBWWWWWWWWWWWBBo",
".oBBWWWWWWWWWWWBo.",
".oBBBWWWWWwWWWBBo.",
"..oBBwWWWWWWwBBo..",
"...oWWo.....oWWo..",
"...owwo.....owwo..",
"....oo.......oo...",
])

# ---------------------------------------------------------------- lying dead (side)
LYING = R([
"..................",
"..................",
"..................",
"..................",
"..................",
"..................",
"..................",
"..................",
"..................",
"...........oo.oo..",
"..........oBBoBBo.",
"....oooooooBBBBBBo",
"..ooBBbBBBBBBBBBBo",
".oBBBBBBBBBBoWoWBo",
"oBbBBBWWWWWWWWWWWo",
"oBBBBWWWWWWWWPWWWo",
".oBBBWWWWWWWWWWWo.",
"..oooWWoWWoWWoWo..",
"....ooooooooooo...",
"..................",
])

# ---------------------------------------------------------------- 4x4 paw for the gun hand
HAND = R([
".oo.",
"oWWo",
"oWWo",
".oo.",
])

# Diagonal running legs (vanilla Gungeoneers stretch the legs into 2px strokes on contact frames).
LEG_FWD = R([  # hip at top-left, foot a little ahead (short trot stride)
"oWWo.",
".oWWo",
".owwo",
"..oo.",
])
LEG_BACK = R([  # hip at top-right, foot a little behind
".oWWo",
"oWWo.",
"owwo.",
".oo..",
])
LEG_TUCK = R([  # airborne: short tucked leg
"oWWo",
".oo.",
])

# Arm extended toward the gun for the "_hand" / "_twohands" body variants (the game draws the paw itself).
ARM_SIDE = R([  # extends to the right from the shoulder
"oBBBo",
"oBBBo",
".ooo.",
])
ARM_FRONT_R = R([  # front view: right arm out to the side
"oBBo",
"oBBo",
".oo.",
])
