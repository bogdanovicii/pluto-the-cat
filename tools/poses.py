"""Hand-drawn key poses for Pluto on an 18 x 22 pose canvas. Side poses face RIGHT; the game mirrors for left.

Structure (v4 art pass): a pose = HEAD part (12 rows) + BODY part (7 rows) + LEGS (3 rows), stacked.
The head markings are drawn once per view and reused by every pose, so eyes, blaze and the white
head spot never drift between poses. Eye variants are applied by eyes() at known pixel positions.

Markings follow the photos: tabby mask around the eyes, white blaze between the eyes running down to
the white muzzle, a small white oval on the crown fully surrounded by tabby, forehead "M" strokes,
mackerel bars on the flank, big pink-lined ears, ringed tail (drawn in poses_extra).

Outline rule: 'o' marks the silhouette so previews and the fur generator know the edge, but body
frames are exported WITHOUT it (the game draws the black outline at runtime). Interior seams use the
darker tone of the material ('b' for tabby, 'w'/'x' for white), never 'o'.
Shading rule: no rim shading. One shadow shape per mass from a top-left light: 'dd' block on the
right of the forehead, 'w' along the bottom-right of the belly/muzzle.

Palette keys: see pixel.PALETTE. '.' transparent, o outline, W/w white fur, B/b/d/L tabby, G/g eye, P/p pink.
"""
from pixel import check_rect as R, overlay, pad

W, H = 18, 22
HEAD_ROWS, BODY_ROWS, LEG_ROWS = 12, 7, 3

# ---------------------------------------------------------------- heads (18 x 12)
HEAD_SIDE = R([
"......oo.....oo...",  # 0  ear tips
".....oBBo...oBBo..",  # 1
".....oBPPoooPPBo..",  # 2  pink inner ears face the centre
"....oBBPBBBBBPBBo.",  # 3  ear bases; crown under the bridge is tabby (the spot must not touch the bridge)
"...oBbBBBBBBBBbddo",  # 4  M outer strokes, shadow block on the right
"...oBBbBBWWWBbBddo",  # 5  white head spot (3x2 oval) inside tabby, M inner strokes
"...oBBBBBWWWBBBddo",  # 6
"...oBBBGgBBBBGgBBo",  # 7  eyes inside the tabby mask (pupil = vertical slit on the forward side)
"...oBBBGgBWWBGgBBo",  # 8  blaze starts between the eyes
"...oBBWWWWWWWWWWBo",  # 9  white cheeks / muzzle
"...oWWWWWWWPPWWWwo",  # 10 nose
"....oWWWWWWpWWWwo.",  # 11 mouth
])
# eye boxes (x, y) top-left of each 2x2 eye, per view; used by eyes()
EYES_SIDE = ((7, 7), (13, 7))

HEAD_FRONT = R([
"....oo......oo....",  # 0
"...oBBo....oBBo...",  # 1
"...oBPPoooooPPBo..",  # 2
"..oBBPBBBBBBBPBBo.",  # 3
".oBbBBBBBBBBBBbBdo",  # 4
".oBBbBBBWWWBBBbBdo",  # 5  spot
".oBBBBBBWWWBBBBBdo",  # 6
".oBBBgGBBBBBGgBBdo",  # 7  pupils inward (not wall-eyed)
".oBBBgGBWWWBGgBBdo",  # 8  blaze
".oBWWWWWWWWWWWWWBo",  # 9
".oWWWWWWWPPWWWWWwo",  # 10
"..oWWWWWWpWWWWWwo.",  # 11
])
EYES_FRONT = ((5, 7), (12, 7))

HEAD_BACK = R([
"....oo......oo....",  # 0
"...oBBo....oBBo...",  # 1
"...oBBBoooooBBBo..",  # 2  no pink from behind
"..oBBBBBBBBBBBBBo.",  # 3
".oBBBBBBBBBBBBBBdo",  # 4
".oBBbBBBWWWBBBbBdo",  # 5  the spot, seen from behind
".oBBBbBBWWWBBbBBdo",  # 6
".oBBBBbBBBBBbBBBdo",  # 7  chevron down the neck
".oBBBBBbBBBbBBBBdo",  # 8
".oBBBBBBbbbBBBBBdo",  # 9
".oBBBBBBBBBBBBBBdo",  # 10
"..oBBBBBBBBBBBBBo.",  # 11 neck
])

# ---------------------------------------------------------------- bodies (18 x 7): shoulders to belly
BODY_SIDE = R([
"....oBBBWWWWWWBBo.",  # 12 shoulders
"...oBbBBWWWWWWWBo.",  # 13 flank bar 1
"...oBbBBWWWWWWWBo.",  # 14
"...oBBbBWWWWWWWBo.",  # 15 flank bar 2
"...oBBbBBWWWWWBBo.",  # 16
"...oBBBBBWWwwwBBo.",  # 17 belly shadow (bottom-right)
"....oBddwwwwwdBo..",  # 18 underside
])
BODY_FRONT = R([
"..oBBBWWWWWWWBBBo.",  # 12
".oBBBWWWWWWWWWBBdo",  # 13
".oBbWWWWWWWWWWWbdo",  # 14 bars on both flanks
".oBbWWWWWWWWWWWbdo",  # 15
".oBBBWWWWWWWWWBBdo",  # 16
".oBBBWWWWwwwwBBBdo",  # 17
"..oBBwwwwwwwwwBBo.",  # 18
])
BODY_BACK = R([
"..oBBBBBBBBBBBBBo.",  # 12
".oBBbBBBBBBBBbBBdo",  # 13 mackerel bars down the back
".oBBBbBBBbBBbBBBdo",  # 14
".oBBBBbBbBbBBBBBdo",  # 15
".oBBBbBBBbBBbBBBdo",  # 16
".oBBbBBBBBBBBbBBdo",  # 17
"..oBBBdddddBBBBo..",  # 18
])

# ---------------------------------------------------------------- legs (18 x 3) at rest
LEGS_SIDE = R([
".....oWWo...oWWo..",  # 19
".....owwo...owwo..",  # 20
"......oo.....oo...",  # 21
])
LEGS_FRONT = R([
"...oWWo.....oWWo..",
"...owwo.....owwo..",
"....oo.......oo...",
])
LEGS_BACK = LEGS_FRONT
EMPTY_LEGS = ['.' * W] * LEG_ROWS


def stack(head, body, legs):
    """Head (12) + body (7) + legs (3) rows -> one 18x22 pose."""
    rows = list(head) + list(body) + list(legs)
    assert len(rows) == H, len(rows)
    return R(rows)


def eyes(rows, boxes, kind):
    """Rewrite the 2x2 eyes of a pose. kind: 'open' (unchanged), 'shut' (lid line), 'x' (dead),
    'wide' (startled), 'happy' (closed arcs)."""
    if kind == 'open':
        return rows
    g = [list(r) for r in rows]
    for (x, y) in boxes:
        if kind == 'shut':
            g[y][x], g[y][x + 1] = 'B', 'B'
            g[y + 1][x], g[y + 1][x + 1] = 'b', 'b'
        elif kind == 'x':
            g[y][x], g[y][x + 1] = 'b', '9'
            g[y + 1][x], g[y + 1][x + 1] = '9', 'b'
        elif kind == 'wide':
            g[y][x], g[y][x + 1] = 'G', 'G'
            g[y + 1][x], g[y + 1][x + 1] = 'g', 'g'
        elif kind == 'happy':
            g[y][x], g[y][x + 1] = 'b', 'b'
            g[y + 1][x], g[y + 1][x + 1] = 'B', 'B'
    return [''.join(r) for r in g]


def ear_flick(rows, x0, x1):
    """Tilt the ear whose tip spans columns x0..x1 on rows 0-1 by one pixel to the right (idle fidget)."""
    g = [list(r) for r in rows]
    for y in (0, 1):
        seg = g[y][x0:x1 + 1]
        g[y][x0:x1 + 1] = ['.'] + seg[:-1] if seg[-1] == '.' else seg
    return [''.join(r) for r in g]


def mouth_open(rows, x, y):
    """Small open mouth (2x1 dark pink) replacing the 1-px mouth at (x, y)."""
    g = [list(r) for r in rows]
    g[y][x - 1], g[y][x] = 'p', 'p'
    return [''.join(r) for r in g]


# ---------------------------------------------------------------- the three idle views
IDLE_SIDE = stack(HEAD_SIDE, BODY_SIDE, LEGS_SIDE)
IDLE_FRONT = stack(HEAD_FRONT, BODY_FRONT, LEGS_FRONT)
IDLE_BACK = stack(HEAD_BACK, BODY_BACK, LEGS_BACK)

# body-only versions (legs blank) so clips can re-pose the legs
SIDE_BODY = stack(HEAD_SIDE, BODY_SIDE, EMPTY_LEGS)
FRONT_BODY = stack(HEAD_FRONT, BODY_FRONT, EMPTY_LEGS)
BACK_BODY = stack(HEAD_BACK, BODY_BACK, EMPTY_LEGS)

# ---------------------------------------------------------------- leg parts (placed by the clips)
SIDE_LEG = R([  # single leg, 4 x 3 (fill 2 rows)
"oWWo",
"owwo",
".oo.",
])
SIDE_LEG_LONG = R([  # leg stretched down (pass frames): fill 3 rows
"oWWo",
"oWWo",
"owwo",
".oo.",
])
LEG_REACH = R([  # leg reaching for the ground (pass frames, body 3 px up): fill 4 rows
"oWWo",
"oWWo",
"oWWo",
"owwo",
".oo.",
])
LEG_FWD = R([  # contact: hip at top-left, foot 2 px ahead (short splayed stride, vanilla-like)
"oWWo..",
".oWWo.",
"..owwo",
"...oo.",
])
LEG_BACK = R([  # contact: hip at top-right, foot 2 px behind
"..oWWo",
".oWWo.",
"owwo..",
".oo...",
])
LEG_TUCK = R([  # airborne: short tucked leg
"oWWo",
".oo.",
])

# ---------------------------------------------------------------- paws up (item get / thumbs up), front
PAWS_UP = R([
"....oo......oo....",
"...oBBo....oBBo...",
"...oBPPoooooPPBo..",
"..oBBPBBBBBBBPBBo.",
".oBbBBBBBBBBBBbBdo",
".oBBbBBBWWWBBBbBdo",
".oBBBBBBWWWBBBBBdo",
"ooBBBgGBBBBBGgBBoo",  # paws come up beside the head (3 px wide)
"WWBBBgGBWWWBGgBBWW",
"WWBWWWWWWWWWWWWWWW",
"WWWWWWWWWPPWWWWWWW",
"owWWWWWWWpWWWWWWwo",
".owoBBWWWWWWWBBowo",
"..ooBBWWWWWWWWBBoo",
".oBBBWWWWWWWWWBBdo",
".oBbWWWWWWWWWWWbdo",
".oBBBWWWWWWWWWBBdo",
".oBBBWWWWwwwwBBBdo",
"..oBBwwwwwwwwwBBo.",
"...oWWo.....oWWo..",
"...owwo.....owwo..",
"....oo.......oo...",
])

# ---------------------------------------------------------------- 4x4 paw for the gun hand (2x2 fill + margin; the game outlines it)
HAND = R([
".oo.",
"oWWo",
"oWWo",
".oo.",
])

# Free-hand stubs for the "_hand" / "_twohands" body variants (the game draws the paw on the gun).
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


# ---------------------------------------------------------------- back-view side ("_bw": aiming up-diagonal)
# The player sees Pluto from behind at an angle: back of the head, one pink ear, no eyes, a sliver of
# muzzle and chest on the near side, more stripes on the flank.
HEAD_BW = R([
"......oo.....oo...",  # 0
".....oBBo...oBBo..",  # 1
".....oBBBoooPPBo..",  # 2  far ear shows its back, near ear shows pink
"....oBBBBBBBBPBBo.",  # 3
"...oBbBBBBBBBBbddo",  # 4
"...oBBbBBWWWBbBddo",  # 5  spot
"...oBBBBBWWWBBBddo",  # 6
"...oBBBBBBBBBBBBBo",  # 7  looking away: no eyes
"...oBBbBBbBBBBBBBo",  # 8  neck stripes
"...oBBBBBBBBBBWWBo",  # 9  a bit of cheek
"...oBBBBBBBBBWWWwo",  # 10 muzzle peeking out
"....oBBBBBBBWWWwo.",  # 11
])
BODY_BW = R([
"....oBBBBBBWWWBBo.",  # 12
"...oBbBBbBBBWWWBo.",  # 13
"...oBbBBbBBBWWWBo.",  # 14
"...oBBbBBbBBWWWBo.",  # 15
"...oBBbBBbBBBWWBo.",  # 16
"...oBBBBBBBBBwwBo.",  # 17
"....oBddBBBBwwBo..",  # 18
])
BW_BODY = stack(HEAD_BW, BODY_BW, EMPTY_LEGS)

# Free paw resting on the chest for the "_hand" (one-handed gun: the other paw is the game's hand
# sprite on the gun) and "_twohands" (no gun: both paws) body variants. A 'w' rim keeps it readable
# on the white chest.
PAW = R([
".xx.",
"xWWx",
"xWWx",
".xx.",
])


def ears_back(rows, tips=((6, 7), (13, 14))):
    """Airborne run frames: both ear tips (rows 0-1, columns x0..x1) blow back one pixel (to the left)."""
    g = [list(r) for r in rows]
    for y in (0, 1):
        for x0, x1 in tips:
            seg = g[y][x0 - 1:x1 + 2]                 # one extra column on each side
            if seg[0] == '.':
                g[y][x0 - 1:x1 + 1] = seg[1:]         # shift the tip left by one
                g[y][x1 + 1] = '.'
    return [''.join(r) for r in g]


def squashed(head, body, legs, head_dy=1):
    """Idle squash: the head sinks head_dy rows into the shoulders while the belly and feet stay put."""
    rows = pad(head, W, H, 0, head_dy)
    rows = overlay(rows, body, 0, HEAD_ROWS)
    rows = overlay(rows, legs, 0, HEAD_ROWS + BODY_ROWS)
    return R(rows)
