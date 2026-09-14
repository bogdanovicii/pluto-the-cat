"""Version-3 art: frame-filling shaded face card, composed Royal Canin bag (gun + Ammonomicon), shaded wet-food can.

Pixel-art craft rules applied here (the same ones vanilla Gungeon sprites follow):
- light from the top-left: highlight tone on top/left edges, shadow tone on bottom/right;
- shadows are hue-shifted (tabby shadow leans red, white shadow leans warm grey), never plain darker;
- every material gets 3 tones (highlight / base / shade) plus a dark outline;
- eyes get a light iris tone, a dark pupil and a single white glint;
- folds and seams are drawn as 1-px lines of the shade tone, not as outlines.
"""
from pixel import check_rect as R, overlay_clip as overlay, pad_clip as pad, rotate, shift_clip as shift, flip_h

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


# ---------------------------------------------------------------- gun: the Ammonomicon bag lying on its side, 32 x 18
GUN_W, GUN_H = 32, 18


def rot_cw(rows):
    """Rotate row-strings 90 degrees clockwise (exact, no resampling)."""
    return [''.join(r[x] for r in reversed(rows)) for x in range(len(rows[0]))]


def gun_bag(open_lip=True):
    """The same Royal Canin bag as the Ammonomicon page, turned on its side so the zip top points at the
    target: bottom gusset in the paw on the left, purple label with the grey cat, red band with its white
    dots, the crown, the zip seam, and the torn-open top on the right where the kibble comes out."""
    c = blank(GUN_W, GUN_H)
    c = put(c, rrect(28, 14, 'W'), 1, 2)                 # body x1..28, y2..15
    c = col(c, 2, 3, 14, 'N'); c = col(c, 3, 4, 13, 's')  # bottom gusset (grip end)
    c = row(c, 3, 4, 24, 'K')                             # top highlight
    c = row(c, 14, 4, 24, 'w')                            # bottom shade
    c = put(c, [
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
    ], 5, 4)                                              # purple label
    c = put(c, CAT_SIT, 8, 5)                             # grey cat, kept upright so it reads at 1x
    c = col(c, 16, 3, 14, 'r'); c = col(c, 17, 3, 14, 'R'); c = col(c, 18, 3, 14, 'R')  # red band
    for y in (4, 7, 10, 13):
        c = put(c, ['K'], 17, y)
    c = put(c, CROWN, 20, 7)                              # crown, upright (turned sideways it reads as a K)
    c = col(c, 25, 3, 14, 's'); c = col(c, 26, 3, 14, 'N'); c = col(c, 27, 3, 14, 'N')  # zip seam
    for y in (4, 8, 12):
        c = put(c, ['o'], 26, y)
    if open_lip:                                          # torn-open top: flap peeled up, kibble inside the mouth
        c = put(c, ['.', '.', '.', '.'], 28, 7)           # no outline across the opening
        c = put(c, ['m', 'M', 'M', 'm'], 27, 7)           # kibble showing in the mouth
        c = put(c, ['..oo', '.oNo', 'oNo.', 'No..'], 27, 3)  # flap torn back over the top edge
        c = put(c, ['o'], 28, 11)                         # lower lip
    return R(c)


GUN_IDLE = gun_bag()
_SHUT = gun_bag(open_lip=False)


def kibble_at(frame, pts):
    for x, y, ch in pts:
        frame = put(frame, [ch], x, y)
    return frame


# fire (14 fps): recoil squeeze with a burst out of the top, the burst scatters, the lip settles
GUN_FIRE = [
    kibble_at(shift(GUN_IDLE, -1, 0), [(29, 7, 'M'), (30, 9, 'm'), (29, 10, 'M'), (31, 8, 'M')]),
    kibble_at(GUN_IDLE, [(30, 6, 'm'), (31, 9, 'M'), (30, 11, 'M')]),
    kibble_at(GUN_IDLE, [(29, 9, 'M')]),
]
# reload (8 fps): the paw folds the top shut, shakes the bag, kibble tumbles back up to the opening
GUN_RELOAD = [
    shift(_SHUT, 0, 1),
    shift(_SHUT, 1, -1),
    kibble_at(shift(GUN_IDLE, 0, 1), [(26, 1, 'M'), (28, 2, 'm')]),
    GUN_IDLE,
]

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

# ---------------------------------------------------------------- active: Royal Canin Kitten tin (reference/ideas/active_item_idea.png)
# A short, wide gold tin: ring-pull lid, pink label wrapped around a white panel with the crown over the red
# band, a pink KITTEN strip and a window of gravy chunks. Items keep their drawn outline.
CAN_ICON = R([
"....oooooooooooo....",
"..ooYYYYYYYYYYYYoo..",
".oAYYaaaaaaaaaaYYao.",
".oAYaaoooooaaaaaYao.",
".oAYaoYaaaYoAAAaYao.",
".oAYaaoooooaaaaaYao.",
".oAYYaaaaaaaaaaYYao.",
".ooYYYYYYYYYYYYYYoo.",
".oqIIWWWRWRWRWWIPpo.",
".oqIIWWWWRWRWWWIPpo.",
".oqIIWWWWWWWWWWIPpo.",  # the red band is the crown's base
".oqIRRKRRKRRKRRRPpo.",
".oqIPPPPPWMmMmWIPpo.",
".oqIPPPPPWmMmMWIPpo.",
".oqIIIIIIWWWWWWIPpo.",
".oAAYYYYYYYYYYYYaao.",
"..ooaaYYYYYYYYaaoo..",
"....oooooooooooo....",
])

# Thrown: the tin tumbles end over end (16x16 frames, square so a rotation never shifts it).
_TIN_SIDE = R([
".oooooooooo.",
"oAYYYYYYYYao",
"oqIWRWRWIPpo",
"oqIRRRRRRPpo",
"oqIPWMmWIPpo",
"oqIPWmMWIPpo",
"oAYYYYYYYYao",
".oooooooooo.",
])
_TIN_LID = R([
"...oooo...",
".ooYYYYoo.",
".oYaaaaYo.",
"oYaooooaYo",
"oYaoYYoAYo",
"oYaooooaYo",
"oYaaaAAaYo",
".oYaaaaYo.",
".ooYYYYoo.",
"...oooo...",
])
_TIN_BOTTOM = R([
"...oooo...",
".ooaaaaoo.",
".oaYYYYao.",
"oaYAAYYYao",
"oaYAYYYYao",
"oaYYYYYYao",
"oaYYYYYaao",
".oaYYYYao.",
".ooaaaaoo.",
"...oooo...",
])
_side16 = pad(_TIN_SIDE, 16, 16, 2, 4)
CAN_TOSS = [_side16, pad(_TIN_LID, 16, 16, 3, 3), rotate(_side16, -180), pad(_TIN_BOTTOM, 16, 16, 3, 3)]

# Burst where the can stops (VFX, 20x20): the lid pops off, gravy splats, hearts rise.
_SPLAT_S = R([
"..oooooo..",
".oMMmMMMo.",
"oMmMMMmMMo",
".oMMMmMMo.",
"..oooooo..",
])
_SPLAT_L = R([
"....oooooooooo....",
"..ooMMMmMMMMmMMoo.",
".oMMmMMMMMmMMMMMMo",
"oMMMMMMmMMMMMmMMMo",
".oMMmMMMMMMmMMMMo.",
"..ooMMMMmMMMMMoo..",
"....oooooooooo....",
])
_LID_S = R([
".oooo.",
"oAYYao",
".oooo.",
])
_DROP = R([
"oo",
"Mm",
])
_HEART = R([".oo.oo.", "oHHoHHo", "oHHHHHo", ".oHHHo.", "..oHo..", "...o..."])


def _burst(i):
    c = blank(20, 20)
    if i == 0:
        c = put(c, _SPLAT_S, 5, 15)
        c = put(c, _TIN_SIDE, 4, 8)
        c = put(c, _LID_S, 7, 4)
    elif i == 1:
        c = put(c, _SPLAT_L, 1, 12)
        c = put(c, _LID_S, 11, 2)
        c = put(c, _DROP, 1, 9)
        c = put(c, _DROP, 17, 10)
    elif i == 2:
        c = put(c, _SPLAT_L, 1, 13)
        c = put(c, _HEART, 6, 4)
        c = put(c, _DROP, 16, 8)
    else:
        c = put(c, _SPLAT_L, 1, 13)
        c = put(c, _HEART, 4, 1)
        c = put(c, _HEART, 12, 5)
    return c


GRAVY_BURST = [_burst(i) for i in range(4)]
