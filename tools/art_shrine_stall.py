"""2.20.0 Shrine Stall art: Daifuku, Kinsuke and the stall dressing.

Copied by hand from the approved concept in reference/gemini/shrine_stall/ into
row-strings on the mod palette.  Daifuku and Kinsuke are Breach NPCs, not
``AIActor``s, so nothing adds a runtime outline: unlike the Coco clips these keep
their drawn ``o`` outline and the exporter must not strip it.

Exports ``DAIFUKU_CLIPS`` (idle, talk), ``KINSUKE_CLIPS`` (idle), ``PROPS``
(torii, stall) and ``BLUEPRINT``; ``tools/make_art.py`` writes them into
PlutoTheCat/Resources/Shop/ under the exact names ShrineStall.cs loads.
"""
from pixel import check_rect as R, overlay, pad, flip_h


DAIFUKU_W, DAIFUKU_H = 26, 32


# ---------------------------------------------------------------------- Daifuku
# The head sits on its own 19x17 grid (canvas offset (3, 1)) so the idle breath
# can move it over a still body, the way tools/poses.py composes Pluto.
HEAD = R([
    '..oo...........oo..',
    '.okko.........oiio.',
    '.okPo.........oPio.',
    'okkP' + 'o' * 11 + 'Piio',
    'o' + 'k' * 10 + 'i' * 7 + 'o',
    'o' + 'k' * 10 + 'i' * 7 + 'o',
    'o' + 'k' * 9 + 'i' * 8 + 'o',
    'okk' + 'oooo' + 'kkiii' + 'oooo' + 'ii' + 'o',
    'okk' + 'GggG' + 'kkiii' + 'GggG' + 'ii' + 'o',
    'okk' + 'nnnn' + 'kkiii' + 'nnnn' + 'ii' + 'o',
    'o' + 'kknn' + 'wWWPPPWWw' + 'iiii' + 'o',
    'o' + 'knnn' + 'WWWWpWWWw' + 'iiii' + 'o',
    'o' + 'knnn' + 'WWWoWoWWw' + 'niii' + 'o',
    'o' + 'knnn' + 'wWWWWWWWw' + 'niii' + 'o',
    '.o' + 'nniwwwwwwwiiinn' + 'o.',
    '..o' + 'nniiwwwwwiinn' + 'o..',
    '...' + 'o' * 13 + '...',
])

EYE_SHUT = R([
    'oooo',
    'bbbb',
])

# Talk: only the jaw rows change, so the deadpan half-lidded eyes hold while
# Daifuku sets up the joke.
MOUTH_OPEN = R([
    'WWWoooWWw',
    'WWopppoWw',
    'wWWoooWWw',
])
MOUTH_WIDE = R([
    'WWoooooWw',
    'WopppppoW',
    'wWoooooWw',
])

# The body is a 24x15 grid at canvas offset (1, 17): a wide indigo haori with a
# crimson obi, white chest fur in the lapel V and both paws on the counter.
BODY = R([
    '...o' + '5' * 16 + 'o...',
    '..o' + '5' * 18 + 'o..',
    '.o6' + '5' * 4 + '7' + 'W' * 8 + '7' + '5' * 4 + '6o.',
    'o66' + '5' * 5 + '7' + 'W' * 6 + '7' + '5' * 5 + '66o',
    'o66' + '5' * 6 + '7' + 'W' * 4 + '7' + '5' * 6 + '66o',
    'o66' + '5' * 7 + '7' + 'W' * 2 + '7' + '5' * 7 + '66o',
    'o66' + '5' * 8 + '77' + '5' * 8 + '66o',
    'o66' + '5' * 18 + '66o',
    'o6' + '8' * 20 + '6o',
    'o6' + '8' + 'r' * 18 + '8' + '6o',
    'o66' + '5' * 18 + '66o',
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
HEAD_TALK_A = _head((MOUTH_OPEN, 5, 11))
HEAD_TALK_B = _head((MOUTH_WIDE, 5, 11))


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

# Talk at 8 fps: shut - open - wide - open, the jaw dropping over the same breath.
DAIFUKU_TALK = [
    _daifuku(0),
    _daifuku(0, head=HEAD_TALK_A),
    _daifuku(1, head=HEAD_TALK_B),
    _daifuku(0, head=HEAD_TALK_A),
]

DAIFUKU_CLIPS = {'daifuku_idle': DAIFUKU_IDLE, 'daifuku_talk': DAIFUKU_TALK}


# ---------------------------------------------------------------------- Kinsuke
KINSUKE_W, KINSUKE_H = 22, 20

# The bowl is fixed and only the koi and his bubbles move, so the glass reads as
# glass instead of wobbling along with the fish.
BOWL = R([
    '.....oooooooo.....',
    '...ooNNNNNNNNoo...',
    '..oNNFFFFFFFFNNo..',
    '.oNFFFFFFFFFFFFNo.',
    'oNFFFFFFFFFFFFFFNo',
    'oNFFFFFFFFFFFFFFNo',
    'oNFFFFFFFFFFFFFFNo',
    'oNFFFFFFFFFFFFFFNo',
    'oNfFFFFFFFFFFFFfNo',
    'oNffFFFFFFFFFFffNo',
    '.oNffffffffffffNo.',
    '..oNffffffffffNo..',
    '...ooNffffffNoo...',
    '.....oooooooo.....',
])

# Kohaku koi: a white forked tail at the back, a ginger body with a white saddle
# patch and a dark eye near the pointed head, so the silhouette reads as a fish.
KOI_RIGHT = R([
    'oWo..kkkk.',
    'oWWokkkkkk',
    'oWWWkWokki',
    'oWWokkiiii',
    'oWo...iii.',
])
KOI_LEFT = R(flip_h(KOI_RIGHT))
KOI_TURN = R([
    'oWo...kkk.',
    'oWWo.kkkkk',
    'oWWWkkWoki',
    'oWWo.kiiii',
    'oWo....ii.',
])

BUBBLE = R([
    '.o.',
    'oKo',
    '.o.',
])


def _kinsuke(koi, kx, ky, bx=None, by=None):
    rows = overlay(pad(BOWL, KINSUKE_W, KINSUKE_H, 2, 5), koi, kx, ky)
    if bx is not None:
        rows = overlay(rows, BUBBLE, bx, by)
    return R(rows)


# Idle at 6 fps: a lazy circuit of the bowl with a bubble on the way up - Kinsuke
# is always just about to say something.
KINSUKE_IDLE = [
    _kinsuke(KOI_RIGHT, 5, 11),
    _kinsuke(KOI_TURN, 4, 10, 14, 12),
    _kinsuke(KOI_LEFT, 5, 10, 15, 10),
    _kinsuke(KOI_TURN, 6, 11),
]

KINSUKE_CLIPS = {'kinsuke_idle': KINSUKE_IDLE}


# ------------------------------------------------------------------------ props
def _blank(w, h):
    rows = [['.'] * w for _ in range(h)]

    def put(x, y, s):
        for i, ch in enumerate(s):
            if ch != '.':
                rows[y][x + i] = ch

    return rows, put


LANTERN = R([
    '..ooo..',
    '.oRRRo.',
    'oRYYYRo',
    'oRYKYRo',
    'oRYYYRo',
    '.oRRRo.',
    '..ooo..',
])

KOI_BANNER = R([
    '.oooooo.....',
    'oRWRRRRoo.oo',
    'oRoRRRRRRoRo',
    'oRWRRRRoo.oo',
    '.oooooo.....',
])
KOI_BANNER_BLUE = R([
    '.oooooo.....',
    'o2W2222oo.oo',
    'o2o222222o2o',
    'o2W2222oo.oo',
    '.oooooo.....',
])


def _torii():
    """78x48: the vermilion gate, a paper lantern under each half of the nuki and
    the koi banner pole standing clear of the right pillar."""
    rows, put = _blank(78, 48)
    # kasagi: a dark tiled lintel whose ends step up, over a shadowed underside
    put(0, 0, 'o' * 4); put(56, 0, 'o' * 4)
    put(0, 1, '4' * 4 + 'o' * 4); put(52, 1, 'o' * 4 + '4' * 4)
    put(0, 2, '4' * 8 + 'o' * 4); put(48, 2, 'o' * 4 + '4' * 8)
    put(0, 3, '4' * 12 + 'o' * 36 + '4' * 12)
    put(0, 4, '4' * 60)
    put(0, 5, '0' * 60)
    put(0, 6, 'o' * 60)
    # shimaki: the red band under the roof
    put(3, 7, 'o' + 'R' * 52 + 'o')
    put(3, 8, 'o' + 'R' * 52 + 'o')
    put(3, 9, 'o' + 'r' * 52 + 'o')
    put(3, 10, 'o' * 54)
    # gakuzuka: the short centre post between the two lintels
    for y in range(11, 20):
        put(27, y, 'oRRrro')
    # nuki: the second lintel
    put(7, 20, 'o' * 46)
    put(7, 21, 'o' + 'R' * 44 + 'o')
    put(7, 22, 'o' + 'R' * 44 + 'o')
    put(7, 23, 'o' + 'r' * 44 + 'o')
    put(7, 24, 'o' * 46)
    # pillars on stone bases
    for y in range(11, 44):
        put(12, y, 'oRRRrro')
        put(41, y, 'oRRRrro')
    for y in range(44, 47):
        put(11, y, 'oSSSSSSso')
        put(40, y, 'oSSSSSSso')
    put(11, 47, 'o' * 9)
    put(40, 47, 'o' * 9)
    # paper lanterns hung from the nuki
    for lx in (20, 33):
        put(lx + 3, 25, 'o')
        for dy, line in enumerate(LANTERN):
            put(lx, 26 + dy, line)
    # koi banner pole, outside the gate so it never hides a pillar
    put(61, 6, 'oAAo')
    for y in range(7, 47):
        put(62, y, 'oNo')
    put(61, 47, 'ooooo')
    for dy, line in enumerate(KOI_BANNER):
        put(65, 12 + dy, line)
    for dy, line in enumerate(KOI_BANNER_BLUE):
        put(65, 21 + dy, line)
    return R([''.join(r) for r in rows])


TORII = _torii()

MANEKI = R([
    '.o...o...',
    'oWo.oWo..',
    'oWWoWWWo.',
    'oWoWWoWo.',
    'oWWWPWWWo',
    '.oWWWWWo.',
    '.oRRRRRo.',
    'oWoAAAoWo',
    'oWWWWWWWo',
    '.ooooooo.',
])

STONE_LANTERN = R([
    '....oo....',
    '...oKKo...',
    '..oooooo..',
    '.oSSSSSSo.',
    'oSSSSSSSSo',
    'osssssssso',
    '.oooooooo.',
    '.oSSSSSSo.',
    '.oSKKKKSo.',
    '.oSKKKKSo.',
    '.oSssssSo.',
    '.oooooooo.',
    '...oSSo...',
    '...oSSo...',
    '.oSSSSSSo.',
    '.oooooooo.',
])


SCROLL = R([
    'oooooooo',
    'oEEEEEEo',
    'oEEMMEEo',
    'oEMMMMEo',
    'oEEMMEEo',
    'oEMEEMEo',
    'oEEEEEEo',
    'oooooooo',
])


def _stall():
    """48x36: the noren curtain on its rod, the dark stall interior with its shelf
    and shop scroll, the maneki-neko on the wooden counter, and a stone lantern."""
    rows, put = _blank(48, 36)
    put(11, 0, 'o' * 37)
    put(11, 1, 'o' + 'M' * 35 + 'o')
    put(11, 2, 'o' * 37)
    for y in range(3, 12):
        put(11, y, 'o' + ('7' if y < 5 else '5') * 35 + 'o')
    for y in range(6, 12):          # the four panels the curtain is slit into
        for x in (20, 29, 38):
            put(x, y, '6')
    put(11, 12, 'o' * 37)
    for y in range(13, 23):         # the dark stall interior behind the counter
        put(12, y, 'Q' * 35)
    put(12, 17, 'X' * 35)           # a shelf line, so the interior is not a flat slab
    for dy, line in enumerate(SCROLL):
        put(36, 14 + dy, line)
    for dy, line in enumerate(MANEKI):
        put(14, 13 + dy, line)
    put(11, 23, 'o' * 37)           # counter top
    put(11, 24, 'o' + 'L' * 35 + 'o')
    put(11, 25, 'o' + 'M' * 35 + 'o')
    put(11, 26, 'o' * 37)
    for y in range(27, 35):         # plank front
        put(12, y, 'o' + 'M' * 33 + 'mo')
    for y in range(27, 35):
        for x in (21, 30, 39):
            put(x, y, 'm')
    put(12, 35, 'o' * 36)
    for dy, line in enumerate(STONE_LANTERN):
        put(0, 20 + dy, line)
    return R([''.join(r) for r in rows])


STALL = _stall()

PROPS = {'torii': TORII, 'stall': STALL}


# The blueprint is the hanging kanban Alexandria places by the stock: a wooden
# board on a rope, with three price tags under it for the three item slots.
BLUEPRINT = R([
    '.........oo...........',
    '........o..o..........',
    '.......o....o.........',
    '......o......o........',
    '.....o........o.......',
    '.oooooooooooooooooooo.',
    'oLLLLLLLLLLLLLLLLLLLLo',
    'oLM' + 'M' * 16 + 'MLo',
    'oLM' + '...EE..EE..EE...'.replace('.', 'M') + 'MLo',
    'oLM' + '...EE..EE..EE...'.replace('.', 'M') + 'MLo',
    'oLM' + 'M' * 16 + 'MLo',
    'oLM' + '.....EEEEEE.....'.replace('.', 'M') + 'MLo',
    'oLM' + '....EEEEEEEE....'.replace('.', 'M') + 'MLo',
    'oLM' + '....EEEEEEEE....'.replace('.', 'M') + 'MLo',
    'oLM' + '.....EEEEEE.....'.replace('.', 'M') + 'MLo',
    'oLM' + 'M' * 16 + 'MLo',
    'oLLLLLLLLLLLLLLLLLLLLo',
    '.oooooooooooooooooooo.',
    '...oo.....oo.....oo...',
    '..oYYo...oYYo...oYYo..',
    '..oYyo...oYyo...oYyo..',
    '...oo.....oo.....oo...',
])
