"""Version-3 art: frame-filling shaded face card, composed Royal Canin bag (gun + Ammonomicon), shaded wet-food can.

Pixel-art craft rules applied here (the same ones vanilla Gungeon sprites follow):
- light from the top-left: highlight tone on top/left edges, shadow tone on bottom/right;
- shadows are hue-shifted (tabby shadow leans red, white shadow leans warm grey), never plain darker;
- every material gets 3 tones (highlight / base / shade) plus a dark outline;
- eyes get a light iris tone, a dark pupil and a single white glint;
- folds and seams are drawn as 1-px lines of the shade tone, not as outlines.
"""
from pixel import check_rect as R, overlay, pad, rotate, shift, flip_h

# ---------------------------------------------------------------- face card 34x34: cropped, zoomed head like vanilla portraits
FACE_34 = R([
"...oLBBBBo..............oBBBBBo...",
"..oLLBBqqBo............oBqqBBBBo..",
"..oLBBBqqqBo..........oBqqqBBBBo..",
".oLLBBBqqqqBo........oBqqqqBBBBdo.",
".oLBBBBBqqqBBoooooooBBqqqBBBBBBdo.",
"oLBBBBBBBqqBBBLLWWLLBBBqqBBBBBBBdo",
"oLBBBBBBBBBBBLLWWWWLLBBBBBBBBBBBdo",
"oLBBbBBBBBBBBLWWWWWWLBBBBBBBbBBBdo",
"oBBBbbBBBBBBBLLWWWWLLBBBBBBbbBBBdo",
"oBBBBbbBBBBBBBLLWWLLBBBBBBbbBBBBdo",
"oBBBBBbbBBBBBBBBBBBBBBBBBbbBBBBBdo",
"oBBBBBBbbBBBBBBBWWBBBBBBBbbBBBBBdo",
"oBBBBBBBBBBBBBBWWWWBBBBBBBBBBBBBdo",
"oBBBBBBBBBBBBBWWWWWWBBBBBBBBBBBBdo",
"oBBBBBBoooooWWWWWWWWWWoooooBBBBBdo",
"oBBBBBoeGGGGoWWWWWWWWoeGGGGoBBBBdo",
"oBBBBBoGKggGoWWWWWWWWoGKggGoBBBBdo",
"oBBBBBoGgggGoWWWWWWWWoGgggGoBBBBdo",
"oBBBBBoGGgGGoWWWWWWWWoGGgGGoBBBBdo",
"oBBBBBBoooooWWWWWWWWWWoooooBBBBBdo",
"oBBBBBBWWWWWWWWWWWWWWWWWWWWBBBBBdo",
"oBBBBWWWWWWWWWWWWWWWWWWWWWWWWBBBdo",
"oBBWWWWWWWWWWWWWPPPPWWWWWWWWWWWBdo",
"oBWWwWWWWWWWWWWPqPPpWWWWWWWWWwWWdo",
"oWWWWWWWWWWWWWWWPPppWWWWWWWWWWWWxo",
"oWWwWWWWWWWWWWWWWppWWWWWWWWWWwWWxo",
"oWWWWWWWWWWWWWWWpWWpWWWWWWWWWWWxxo",
".oWWWWWWWWWWWWWWWWWWWWWWWWWWWWxxo.",
".oWWWWWWWWWWWWWWWWWWWWWWWWWWWxxxo.",
"..oWWWWWWWWWWWWWWWWWWWWWWWWWxxxo..",
"...oWWwwwwWWWWWWWWWWWWWWWxxxxo....",
".....oWwwwwwwwwwwwwwwwwwxxxo......",
".......oowwwwwwwwwwwwwxxoo........",
".........oooooooooooooo...........",
])

# blink: eyes closed (two arcs), for the foyer idle
FACE_34_BLINK = list(FACE_34)
FACE_34_BLINK[14] = "oBBBBBBBBBBBWWWWWWWWWWBBBBBBBBBBdo"
FACE_34_BLINK[15] = "oBBBBBBBBBBBWWWWWWWWWWBBBBBBBBBBdo"
FACE_34_BLINK[16] = "oBBBBBBBBBBBWWWWWWWWWWBBBBBBBBBBdo"
FACE_34_BLINK[17] = "oBBBBBoooooBWWWWWWWWWWBoooooBBBBdo"
FACE_34_BLINK[18] = "oBBBBBBBBBBBWWWWWWWWWWBBBBBBBBBBdo"
FACE_34_BLINK[19] = "oBBBBBBBBBBBWWWWWWWWWWBBBBBBBBBBdo"
R(FACE_34_BLINK)

# hurt: flattened eyes, mouth open
FACE_34_HURT = list(FACE_34)
FACE_34_HURT[15] = "oBBBBBoooooooWWWWWWWWoooooooBBBBdo"
FACE_34_HURT[16] = "oBBBBBoGGgGGoWWWWWWWWoGGgGGoBBBBdo"
FACE_34_HURT[17] = "oBBBBBoGgggGoWWWWWWWWoGgggGoBBBBdo"
FACE_34_HURT[18] = "oBBBBBBoooooWWWWWWWWWWoooooBBBBBdo"
FACE_34_HURT[19] = "oBBBBBBBWWWWWWWWWWWWWWWWWWBBBBBBdo"
FACE_34_HURT[25] = "oWWwWWWWWWWWWWWWoppoWWWWWWWWWwWWxo"
FACE_34_HURT[26] = "oWWWWWWWWWWWWWWWoppoWWWWWWWWWWWxxo"
FACE_34_HURT[27] = ".oWWWWWWWWWWWWWWWooWWWWWWWWWWWxxo."
R(FACE_34_HURT)


# ---------------------------------------------------------------- composition helpers
def blank(w, h):
    return ['.' * w] * h


def rrect(w, h, fill='W', outline='o'):
    """Rounded rectangle w x h: 1-px outline with cut corners."""
    rows = []
    for y in range(h):
        if y == 0 or y == h - 1:
            rows.append('.' + outline * (w - 2) + '.')
        else:
            rows.append(outline + fill * (w - 2) + outline)
    return rows


def put(canvas, rows, x, y):
    return overlay(canvas, rows, x, y)


def col(canvas, x, y0, y1, ch):
    return put(canvas, [ch] * (y1 - y0 + 1), x, y0)


def row(canvas, y, x0, x1, ch):
    return put(canvas, [ch * (x1 - x0 + 1)], x0, y)


CROWN = R([  # the five-dot Royal Canin crown
"R.R.R",
".R.R.",
"RRRRR",
])
CAT_SIT = R([  # grey cat silhouette for the purple label (5x7)
".oo..",
".ZZ..",
"ZZZZ.",
".ZZZz",
".ZZZz",
".Zzz.",
".z.z.",
])
KIBBLE_PIC = R([  # small kibble pile on the bag
".mM.",
"mMMm",
])


# ---------------------------------------------------------------- gun: bag held sideways, 32 x 18, opening on the right
GUN_W, GUN_H = 32, 18


def gun_bag():
    c = blank(GUN_W, GUN_H)
    c = put(c, rrect(28, 14, 'W'), 1, 1)                 # bag body x1..28, y1..14
    c = row(c, 2, 5, 24, 'K')                             # top highlight
    c = row(c, 13, 5, 24, 'w')                            # bottom shade
    c = col(c, 24, 3, 12, 'w')                            # right-side shade
    for x in (2, 3, 4):                                   # gusset (bag bottom) silver
        c = col(c, x, 2, 13, 'N')
    c = col(c, 3, 3, 12, 's')                             # gusset fold
    c = col(c, 25, 2, 13, 'N')                            # zip strip
    c = col(c, 26, 2, 13, 'N')
    c = col(c, 27, 2, 13, 's')
    for y in (3, 5, 7, 9, 11):                            # zip teeth
        c = put(c, ['o'], 26, y)
    c = col(c, 8, 5, 10, 'w')                             # wrinkle
    c = col(c, 21, 4, 9, 'w')                             # wrinkle
    c = put(c, CROWN, 9, 3)                               # crown
    c = put(c, KIBBLE_PIC, 9, 9)                          # kibble picture under the crown
    c = col(c, 14, 2, 13, 'R')                            # red ROYAL CANIN band (vertical because the bag lies down)
    c = col(c, 15, 2, 13, 'R')
    c = col(c, 16, 2, 13, 'r')
    for y in (4, 6, 8, 10):                               # white letter hints on the band
        c = put(c, ['K'], 15, y)
    circle = R([                                          # purple label (7 x 9)
    "..vvv..",
    ".vVVVv.",
    "vVVVVVv",
    "vVVVVVv",
    "vVVVVVv",
    "vVVVVVv",
    "vVVVVVv",
    ".vVVVv.",
    "..vvv..",
    ])
    c = put(c, circle, 17, 3)
    c = put(c, CAT_SIT, 18, 4)
    return c


GUN_IDLE = gun_bag()

_BURST = blank(GUN_W, GUN_H)
_BURST = put(_BURST, ['M'], 30, 4)
_BURST = put(_BURST, ['M', 'm'], 29, 6)
_BURST = put(_BURST, ['M'], 31, 8)
_BURST = put(_BURST, ['m'], 30, 10)
GUN_FIRE = [overlay(shift(GUN_IDLE, -1, 0), _BURST), overlay(GUN_IDLE, shift(_BURST, 0, 1)), GUN_IDLE]
_POUR = blank(GUN_W, GUN_H)
_POUR = put(_POUR, ['M'], 27, 3)
_POUR = put(_POUR, ['m'], 26, 5)
GUN_RELOAD = [shift(GUN_IDLE, 0, 1), overlay(shift(GUN_IDLE, 1, 0), _POUR), overlay(shift(GUN_IDLE, 0, -1), shift(_POUR, 0, 2)), GUN_IDLE]

# ---------------------------------------------------------------- Ammonomicon page: the bag upright, 24 x 32
def ammonomicon_bag():
    W, H = 24, 32
    c = blank(W, H)
    c = put(c, rrect(22, 30, 'W'), 1, 1)
    c = row(c, 2, 2, 21, 'N'); c = row(c, 3, 2, 21, 'N'); c = row(c, 4, 3, 20, 's')   # zip top
    for x in (4, 8, 12, 16, 20):
        c = put(c, ['o'], x, 3)
    c = col(c, 2, 5, 27, 'K')                             # left highlight
    c = col(c, 21, 5, 27, 'w')                            # right shade
    c = row(c, 27, 3, 20, 'w')
    c = row(c, 28, 2, 21, 'N'); c = row(c, 29, 2, 21, 'N')  # bottom gusset
    c = row(c, 29, 3, 20, 's')
    c = put(c, CROWN, 9, 6)                               # crown
    c = row(c, 10, 3, 20, 'R'); c = row(c, 11, 3, 20, 'R'); c = row(c, 12, 3, 20, 'r')  # red band
    for x in (5, 8, 11, 14, 17):
        c = put(c, ['K'], x, 11)
    circle = R([
    "...vvvv...",
    ".vvVVVVvv.",
    ".vVVVVVVv.",
    "vVVVVVVVVv",
    "vVVVVVVVVv",
    "vVVVVVVVVv",
    "vVVVVVVVVv",
    ".vVVVVVVv.",
    ".vvVVVVvv.",
    "...vvvv...",
    ])
    c = put(c, circle, 7, 14)
    c = put(c, CAT_SIT, 9, 15)
    c = put(c, KIBBLE_PIC, 15, 25)
    c = col(c, 6, 13, 24, 'w')                            # wrinkle
    return c


GUN_AMMONOMICON = ammonomicon_bag()

# ---------------------------------------------------------------- active: Royal Canin Kitten can, 20 x 20 (can 16 x 19 centred)
def can():
    W, H = 20, 20
    c = blank(W, H)
    # lid (gold) rows 0-3
    c = put(c, R([
    "....oooooooo....",
    "..ooAAAYYYYaaoo.",
    ".oAAAYYoooYYaaao",
    ".oAAYYYoKKoYYaao",
    ".oooooooooooooo.",
    ]), 2, 0)
    # body rows 5-16: pink label, cylinder shading (highlight left, shade right)
    for y in range(5, 17):
        c = put(c, ["oqIIIIIIIIIIPPpo"], 2, y)
    # white panel with crown, red band, kitten
    for y in range(6, 15):
        c = put(c, ["KWWWWWWw"], 6, y)
    c = put(c, CROWN, 7, 6)
    c = put(c, ["RRRRRRRr"], 6, 9)
    for x in (7, 9, 11):
        c = put(c, ['K'], x, 9)
    c = put(c, R([
    ".oo.",
    "oWWo",
    "oWWo",
    "WWWW",
    ".oo.",
    ]), 8, 10)                                            # tiny white kitten
    # bottom rim (gold) rows 17-19
    c = put(c, R([
    ".oAAAYYYYYYaaao.",
    "..ooAAYYYYaaoo..",
    "....oooooooo....",
    ]), 2, 17)
    return c


CAN_ICON = can()
CAN_TOSS = [rotate(CAN_ICON, a) for a in (0, -90, -180, -270)]


def splash(stage):
    """Burst can on its side with gravy spreading; stage 0..2 adds hearts."""
    W, H = 20, 20
    c = blank(W, H)
    gravy = R([
    "....oooooooo....",
    "..ooMMMMMMMMoo..",
    ".oMMMmMMMMmMMMo.",
    "oMMMMMMMmMMMMMMo",
    "oMmMMMMMMMMMmMMo",
    ".oooMMMMMMMMooo.",
    "...oooooooooo...",
    ])
    c = put(c, gravy, 2, 12 - stage)
    lid = R([
    "..oooooo..",
    ".oAAYYYao.",
    "oAAYYoooao",
    ".oaaYYYao.",
    "..oooooo..",
    ])
    c = put(c, lid, 1, 8 - stage)
    heart = R([".oo.oo.", "oHHoHHo", "oHHHHHo", ".oHHHo.", "..oHo..", "...o..."])
    if stage >= 1:
        c = put(c, heart, 12, 3)
    if stage >= 2:
        c = put(c, heart, 3, 1)
        c = put(c, heart, 14, 0)
    return c


CAN_SPLASH = [splash(0), splash(1), splash(2)]
