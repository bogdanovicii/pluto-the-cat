"""Shrine Stall v2 art (2026-09-18), shipped by tools/make_art.py since the user approved it "as shown".

Redrawn to .superpowers/sdd/2026-09-18-shrine-stall-redesign/art-spec.md in ETG 3/4 view:
every solid shows a top face (lightest tone) over a front face (base tone), light from the
top-left, right ends and undersides in the shadow tone, no side faces.  User decisions: D1 no
dressing (noren, maneki, stone lantern, koi banner are gone), D2 the slot plaque is an ema,
D3 the big stall with the goods on the counter, D4 the new key 't'.

Daifuku is unchanged and stays in art_shrine_stall.py.  This module owns ``PROPS['torii']``
136x56, ``PROPS['stall']`` 104x23, ``KINSUKE_CLIPS`` 4 x 12x14 and ``BLUEPRINT`` 14x16.  Breach
props keep their drawn ``o`` outline (nothing adds one at runtime).  The anchor columns below are
the contract with PlutoTheCat/src/ShrineStall.cs (art-spec section 5 / 6).
"""
from pixel import PALETTE, check_rect as R, overlay, pad, flip_h
from art_shrine_stall import LANTERN

# 't' (vermilion light) now lives in tools/pixel.py PALETTE.  The alias keeps the candidate render
# script (docs/art-preview/candidates-2026-09-18/render.py) working unchanged.
PALETTE_V2 = PALETTE


def _blank(w, h):
    rows = [['.'] * w for _ in range(h)]

    def put(x, y, s):
        for i, ch in enumerate(s):
            if ch != '.':
                rows[y][x + i] = ch

    return rows, put


# ------------------------------------------------------------------------ counter
STALL_W, STALL_H = 104, 23
SLOT_MAT_COLS = (5, 24, 43)      # crimson display mats, 14 wide, for slots A, B, C
SLOT_ANCHOR_COLS = (12, 31, 50)  # bottom-centre of each slot's item, on the bottom edge of row 6
KINSUKE_ANCHOR_COL = 94          # bowl bottom-centre, on the bottom edge of row 5
DAIFUKU_ANCHOR_COL = 73


def _stall():
    """104x23: a 9-row top face (back outline, 6 rows of L, 2-row l front strip) over a 14-row
    front face (m seam, M planks, m kick, bottom outline).  Daifuku's shadow darkens the back
    row where he stands; each slot has a crimson mat, the bowl a small shadow."""
    rows, put = _blank(STALL_W, STALL_H)
    inner = STALL_W - 2
    put(1, 0, 'o' * inner)                          # back edge of the top face
    put(0, 1, 'o' + 'L' * 57 + 'M' * 30 + 'L' * 15 + 'o')   # cols 58-87 = Daifuku's shadow
    for y in range(2, 7):
        put(0, y, 'o' + 'L' * inner + 'o')
    for y in (7, 8):
        put(0, y, 'o' + 'l' * inner + 'o')          # front strip catches the top-left light
    put(0, 9, 'o' + 'm' * inner + 'o')              # seam between top and front face
    for y in range(10, 20):
        put(0, y, 'o' + 'M' * 99 + 'mmm' + 'o')     # planks, right end in shadow
        for x in (26, 52, 78):
            put(x, y, 'm')
    for y in (20, 21):
        put(0, y, 'o' + 'm' * inner + 'o')          # kick board: occlusion where it meets the floor
    put(1, 22, 'o' * inner)
    for mx in SLOT_MAT_COLS:
        for y in (3, 4, 5):
            put(mx, y, '8' * 14)
        put(mx, 6, 'r' * 14)                        # the mat's front edge is its shadow
    for y in (5, 6):
        put(89, y, 'M' * 10)                        # bowl contact shadow
    return R([''.join(r) for r in rows])


STALL = _stall()


# -------------------------------------------------------------------------- torii
TORII_W, TORII_H = 136, 56
POSTS = (8, 122)            # left column of each 7-wide post
LANTERN_COLS = (20, 110)


def _torii():
    """136x56 vermilion torii in 3/4 view: upswept charcoal kasagi (stone top face, charcoal
    front, dark underside), red shimaki, centre gakuzuka, nuki with a lit top face, two round
    posts (lit left column, shaded right) on stone kamebara bases, a lantern under each end."""
    rows, put = _blank(TORII_W, TORII_H)
    # kasagi: upswept tips, then the roof beam
    put(0, 0, 'oooo'); put(132, 0, 'oooo')
    put(0, 1, 'osssoooo'); put(128, 1, 'oooossso')
    put(0, 2, 'o' + 's' * 7 + 'o' * 120 + 's' * 7 + 'o')
    for y in (3, 4):
        put(0, y, 'o' + 's' * 134 + 'o')            # top face
    for y in (5, 6, 7):
        put(0, y, 'o' + '4' * 132 + '00' + 'o')     # front, right end in shadow
    put(0, 8, 'o' + '0' * 134 + 'o')                # underside
    # shimaki: red band, outlined, with the overhang of the kasagi closed underneath
    put(0, 9, 'o' * 6 + 'R' * 122 + 'rr' + 'o' * 6)
    put(5, 10, 'o' + 'R' * 122 + 'rr' + 'o')
    put(5, 11, 'o' + 'r' * 124 + 'o')
    put(5, 12, 'o' * 126)
    # gakuzuka: centre strut, shaded where the shimaki overhangs it
    put(66, 12, 'orrro')
    for y in range(13, 17):
        put(66, y, 'otRro')
    # posts (drawn before the nuki so the nuki passes in front of them)
    for px in POSTS:
        put(px, 12, 'orrrrro')                      # shadow under the shimaki
        for y in range(13, 52):
            put(px, y, 'otRRRro')
        put(px - 1, 52, 'o' + 'K' * 7 + 'o')        # kamebara: lit top face
        put(px - 1, 53, 'o' + 'S' * 6 + 's' + 'o')
        put(px - 1, 54, 'o' + 's' * 7 + 'o')
        put(px - 1, 55, 'o' * 9)
    # nuki: tie beam with a lit top face, over the posts and under the strut
    put(2, 16, 'o' * 132)
    put(67, 16, 'tRr')                              # the strut runs into the nuki
    put(2, 17, 'o' + 't' * 130 + 'o')
    for y in (18, 19, 20):
        put(2, y, 'o' + 'R' * 128 + 'rr' + 'o')
    put(2, 21, 'o' + 'r' * 130 + 'o')
    put(2, 22, 'o' * 132)
    for px in POSTS:
        put(px + 1, 16, 'tRRRr')                    # the post continues above the beam
        put(px + 1, 22, 'rrrrr')                    # and below it, in the beam's shadow
    # paper lanterns hung from the nuki on a one-pixel cord
    for lx in LANTERN_COLS:
        put(lx + 3, 23, 'o')
        for dy, line in enumerate(LANTERN):
            put(lx, 24 + dy, line)
    return R([''.join(r) for r in rows])


TORII = _torii()

PROPS = {'torii': TORII, 'stall': STALL}


# ------------------------------------------------------------------------ Kinsuke
KINSUKE_W, KINSUKE_H = 12, 14

# The glass is neutral grey now (rim N, walls S, right wall shaded s, glint K); only the
# lower two thirds hold water, so the blue shrinks to ~44 px and the bowl stops dominating.
BOWL = R([
    '............',
    '............',
    '............',
    '..oooooooo..',
    '.oNssssssNo.',
    'oNNNNNNNNNNo',
    'oK11111111so',
    'oKFFFFFFFFso',
    'oSFFFFFFFFso',
    'oSFFFFFFFFso',
    '.oSffffffso.',
    '.oSffffffso.',
    '..ooSSssoo..',
    '...oooooo...',
])

# 6x3 koi, head right: a white forked tail, a ginger body lit on the back and shaded on the
# belly, the snout one pixel longer than the back.  White is kept to the tail only (a white
# saddle made the 6-px fish read as a bone once flipped).  The fork notch leaves up to two
# single water pixels; review_art counts them as strays - they are the tail shape, keep them.
KOI_RIGHT = R([
    'W.kkk.',
    'WWkkkk',
    'W.iii.',
])
KOI_LEFT = R(flip_h(KOI_RIGHT))

BUBBLE = R([
    '.o.',
    'oKo',
    '.o.',
])


SURFACING = R(['K'])    # a bubble breaking the surface, seen against the dark far wall


def _kinsuke(koi, kx, ky, bubble=None):
    rows = overlay(BOWL, koi, kx, ky)
    if bubble is not None:
        part, bx, by = bubble
        rows = overlay(rows, part, bx, by)
    return R(rows)


# 6 fps: the koi blows a bubble and sinks a pixel as it surfaces (frame 2), turns while the
# bubble floats up clear of the rim on the right (frame 3, cols 9-11 so it only meets the rim
# diagonally), and rises back.  The drift is vertical: the water is 8 px wide and the koi 6, so
# a sideways drift would press the fish against the glass and trap single water pixels.
KINSUKE_IDLE = [
    _kinsuke(KOI_RIGHT, 3, 7),
    _kinsuke(KOI_RIGHT, 3, 8, (SURFACING, 8, 4)),
    _kinsuke(KOI_LEFT, 3, 8, (BUBBLE, 9, 0)),
    _kinsuke(KOI_LEFT, 3, 7),
]

KINSUKE_CLIPS = {'kinsuke_idle': KINSUKE_IDLE}


# ------------------------------------------------------------------------ ema plaque
# The item slot display: a pale-wood ema (pentagon votive plaque) with a dark wood roof band,
# a crimson cord knot at the apex and a crimson paw print painted on the face.  It stands on
# a slot mat, so its bottom row is a flat outline.
BLUEPRINT = R([
    '.....o88o.....',
    '....o88rro....',
    '.....oooo.....',
    '....ommmmo....',
    '...ommllmmo...',
    '..ommllLLmmo..',
    '.ommllLLLLmmo.',
    'ommllLLLLLLmmo',
    'omlLL8LL8LLLMo',
    'omlL8LLLL8LLMo',
    'omlLLL88LLLLMo',
    'omlLL8888LLLMo',
    'omlLL8888LLLMo',
    'omlLLLLLLLLLMo',
    'ommMMMMMMMMmmo',
    'oooooooooooooo',
])
