"""Shrine Stall art that did not change in the 2026-09-18 redesign: Daifuku and the paper lantern.

Copied by hand from the approved concept in reference/gemini/shrine_stall/ into
row-strings on the mod palette.  Daifuku and Kinsuke are Breach NPCs, not
``AIActor``s, so nothing adds a runtime outline: unlike the Coco clips these keep
their drawn ``o`` outline and the exporter must not strip it.

Exports ``DAIFUKU_CLIPS`` (idle, talk) and ``LANTERN``.  The redesigned torii, counter,
Kinsuke's bowl and the ema slot plaque live in ``art_shrine_stall_v2.py`` (which hangs this
LANTERN from its torii); ``tools/make_art.py`` writes both into PlutoTheCat/Resources/Shop/
under the exact names ShrineStall.cs loads.  The 2.20.0 torii, noren stall, maneki-neko,
stone lantern, koi banners and kanban blueprint were retired by that redesign (user decision
D1) and are in git history if they ever return as separate props.
"""
from pixel import check_rect as R, overlay, pad


DAIFUKU_W, DAIFUKU_H = 26, 32


# ---------------------------------------------------------------------- Daifuku
# The head sits on its own 19x17 grid (canvas offset (3, 1)) so the idle breath
# can move it over a still body, the way tools/poses.py composes Pluto.
#
# Face anatomy, fixed for every frame: the cream muzzle (cols 5-13) and the pink
# nose (P at rows 10, p at row 11, both centred on col 9) are the anchor and never
# move.  The light/shadow split in the ginger steps one pixel per row from col 12
# down to col 9, so the face is lit from the top-left instead of being two flat
# halves.  Only the three jaw pixels under the nose animate; see MOUTH_* below.
HEAD = R([
    '..oo...........oo..',
    '.okko.........oiio.',
    '.okPo.........oPio.',
    'okkP' + 'o' * 11 + 'Piio',
    'o' + 'k' * 11 + 'i' * 6 + 'o',
    'o' + 'k' * 10 + 'i' * 7 + 'o',
    'o' + 'k' * 9 + 'i' * 8 + 'o',
    'okk' + 'oooo' + 'kkiii' + 'oooo' + 'ii' + 'o',
    'okk' + 'GggG' + 'kkiii' + 'GggG' + 'ii' + 'o',
    'okk' + 'nnnn' + 'kkiii' + 'nnnn' + 'ii' + 'o',
    'o' + 'kknn' + 'wWWPPPWWw' + 'iiii' + 'o',
    'o' + 'knnn' + 'WWWWpWWWw' + 'iiii' + 'o',
    'o' + 'knnn' + 'WWWWwWWWw' + 'niii' + 'o',
    'o' + 'knnn' + 'wWWowoWWw' + 'niii' + 'o',
    '.o' + 'nniwwwwwwwiiinn' + 'o.',
    '..o' + 'nniiwwwwwiinn' + 'o..',
    '...' + 'o' * 13 + '...',
])

EYE_SHUT = R([
    'oooo',
    'bbbb',
])

# Talk: the muzzle and the nose are identical in every frame - only a jaw the width
# of the nose (cols 8-10) opens under it, so the deadpan half-lidded eyes and the
# whole face hold while Daifuku sets up the joke.  Both patches sit at (8, 13).
#   closed  two dark corners with a shaded dip between them (the cat omega, and the
#           philtrum above it is a shade rather than a dark line, so the mouth never
#           stacks into a blob under the nose)
#   slit    the corners join into a 3-px line, the chin under it takes a shade
#   wide    the line lifts into a 3x2 cavity with one pink tongue pixel inside it,
#           and the chin below drops into deep shade so it reads as a jaw, not a hole
MOUTH_SLIT = R([
    'ooo',
    'wxw',
])
MOUTH_WIDE = R([
    'ooo',
    'opo',
    'xxx',
])

# The body is a 24x15 grid at canvas offset (1, 17): a wide indigo haori with a
# crimson obi, white chest fur in the lapel V and both paws on the counter.
#   row 1        shadow the head casts on the shoulders (exactly the 13 columns the
#                head outline covers, so the breath frames deepen it instead of
#                flickering it away)
#   cols 6 / 17  sleeve seams in the indigo shadow tone, rows 3-7, so the wide haori
#                sleeves separate from the torso instead of one flat slab
#   cols 13-14   the right chest panel in the white shade, and the left collar edge
#                carried on past the V's point down to the obi: the garment now
#                overlaps and wraps instead of reading as a jumper's neckline
#   cols 14-17   the obi knot - dark crimson edges on the lit band, lit centre on the
#                shaded band, and a two-pixel tail hanging below the belt
BODY = R([
    '...o' + '5' * 16 + 'o...',
    '..o' + '55' + '6' * 13 + '555' + 'o..',
    '.o6' + '5' * 4 + '7' + 'W' * 6 + 'ww' + '7' + '5' * 4 + '6o.',
    'o66' + '555' + '6' + '5' + '7' + 'W' * 4 + 'ww' + '7' + '5' + '6' + '555' + '66o',
    'o66' + '555' + '6' + '55' + '7' + 'WW' + 'ww' + '7' + '55' + '6' + '555' + '66o',
    'o66' + '555' + '6' + '555' + '7' + 'W' + 'w' + '7' + '555' + '6' + '555' + '66o',
    'o66' + '555' + '6' + '5555' + '77' + '5555' + '6' + '555' + '66o',
    'o66' + '555' + '6' + '5' * 5 + '77' + '555' + '6' + '555' + '66o',
    'o6' + '8' * 12 + 'r88r' + '8' * 4 + '6o',
    'o6' + '8' + 'r' * 12 + '88' + 'r' * 4 + '8' + '6o',
    'o66' + '5' * 12 + 'rr' + '5' * 4 + '66o',
    'o6' + 'WW' + '5' * 16 + 'WW' + '6o',
    'o6' + 'WW' + '5' * 16 + 'WW' + '6o',
    'o6' + 'ww' + '6' * 16 + 'ww' + '6o',
    'o' * 24,
])


def _head(*parts):
    rows = HEAD
    for part, dx, dy in parts:
        rows = overlay(rows, part, dx, dy)
    return R(rows)


HEAD_BLINK = _head((EYE_SHUT, 3, 7), (EYE_SHUT, 12, 7))
HEAD_TALK_A = _head((MOUTH_SLIT, 8, 13))
HEAD_TALK_B = _head((MOUTH_WIDE, 8, 13))


def _daifuku(head_dy=0, head=None):
    frame = pad(BODY, DAIFUKU_W, DAIFUKU_H, 1, 17)
    return R(overlay(frame, head or HEAD, 3, 1 + head_dy))


# Idle at 6 fps: a slow two-beat breath with a blink on the settled frame.  Nothing
# else moves - Daifuku is unbothered, and the stillness is the joke.
DAIFUKU_IDLE = [
    _daifuku(0),
    _daifuku(1),
    _daifuku(1, head=HEAD_BLINK),
    _daifuku(0),
]

# Talk at 8 fps: closed - slit - wide - slit, the jaw opening and shutting under a
# nose and muzzle that never move.  The wide frame also takes the breath's 1-px head
# drop, so the whole jaw reads as falling rather than a hole appearing in the face.
DAIFUKU_TALK = [
    _daifuku(0),
    _daifuku(0, head=HEAD_TALK_A),
    _daifuku(1, head=HEAD_TALK_B),
    _daifuku(0, head=HEAD_TALK_A),
]

DAIFUKU_CLIPS = {'daifuku_idle': DAIFUKU_IDLE, 'daifuku_talk': DAIFUKU_TALK}


# ------------------------------------------------------------------------ props
# A paper lantern (7x7), hung from each end of the torii nuki.
LANTERN = R([
    '..ooo..',
    '.oRRRo.',
    'oRYYYRo',
    'oRYKYRo',
    'oRYYYRo',
    '.oRRRo.',
    '..ooo..',
])
