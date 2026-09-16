"""2.19.0 Cat Set item/effect art and Coco's Matching Cones clips.

The three 16x16 icons copy the approved cat_items_2 c1 silhouettes.  Effects
copy the c2 paper/shard/puddle ideas at gameplay size.  Coco starts from every
plain frame on the knight counterpart canvas, then receives a pale-blue shell
and front neck rim.  The exporter strips ``o`` so the AIActor can add its normal
runtime outline.
"""
from pixel import check_rect as R, pad
import art_v4 as V4


# ------------------------------------------------------------------ item icons
TOILET_PAPER_ICON = R([
    '....oooooo......',
    '...oWWWWWwo.....',
    '..oWWWWWWxoo....',
    '.oWWWWooooWWo...',
    'oWWWWoSsoWWWwo..',
    'oWWWWoSsoWWWwo..',
    '.oWWWWooooWWo...',
    '..oWWWWWWWWwo...',
    '...ooWWWWWwo....',
    '....oWWWWwo.....',
    '...oWWWWwo......',
    '..oWWWWwo.......',
    '..oWWWwo........',
    '...oooo.........',
    '................',
    '................',
])

CONE_OF_SHAME_ICON = R([
    '..oooooooooooo..',
    '.o111111111111o.',
    'o11FFFFFFFFFF11o',
    '.o1FFFFFFFFFF1o.',
    '..o1FFFFFFFF1o..',
    '...o1FFFFFF1o...',
    '....o1sFFs1o....',
    '.....o1FF1o.....',
    '......o11o......',
    '.....oSSSSo.....',
    '....oSsSSsSo....',
    '.....oSssSo.....',
    '......oooo......',
    '................',
    '................',
    '................',
])

COFFEE_MUG_ICON = R([
    '.............M..',
    '...........M..M.',
    '............MMm.',
    '..........ooM...',
    '.....oooooMMmo..',
    '....oWWMMMMMmo..',
    '...oWWWWRRRWWo..',
    '..oWWWWWRRRWWo..',
    '..oWWWWWWRWWwo..',
    '...oWWWWWWWwooo.',
    '....oWWWWWwoWoWo',
    '.....oWWWwwoWWWo',
    '......owwwwoWoo.',
    '.......ooooo.oo.',
    '................',
    '................',
])

ICONS = {
    'toilet_paper_roll_icon': TOILET_PAPER_ICON,
    'cone_of_shame_icon': CONE_OF_SHAME_ICON,
    'coffee_mug_icon': COFFEE_MUG_ICON,
}


# --------------------------------------------------------------- world effects
STREAMER = R([
    'oooooooooooo',
    'oWWWWWWWWWWo',
    'oWwwWWwwWWWo',
    'oWWWWWWWWWWo',
    'oWWwwWWwwWWo',
    'oooooooooooo',
])

PAPER_BITS = R([
    '.oo.....',
    'oWWo....',
    '.owo.oo.',
    '..o.oWWo',
    '.....owo',
    '.oo.....',
    'oWwo....',
    '.oo.....',
])

CONFETTI = R([
    '.RR.......YY',
    '.R.........Y',
    '....11......',
    '.....1...HH.',
    '.WW......H..',
    '..W..PP.....',
    '.....P....FF',
    '.YY........F',
    '..Y..RR.....',
    '......R..11.',
    '.PP.......1.',
    '..P.........',
])

SHARD_1 = R([
    '..oo...',
    '.oWWo..',
    'oWWWwo.',
    'oWWwo..',
    '.owo...',
    '..o....',
    '.......',
])
SHARD_2 = R([
    '...o...',
    '..oWo..',
    '.oWWwo.',
    'oWWWwwo',
    '.ooooo.',
    '.......',
    '.......',
])
SHARD_3 = R([
    '.oooo..',
    'oWwwWo.',
    '.oWWo..',
    '..oWo..',
    '..oWo..',
    '...oo..',
    '.......',
])
SHARD_HEART = R([
    'oo...oo',
    'oWoooWo',
    '.oRrRo.',
    '..oRo..',
    '...o...',
    '.......',
    '.......',
])

COFFEE_PUDDLE = R([
    '...oooooo...',
    '.ooMMMMmmoo.',
    'oMMMMMMMMmmo',
    'oMMMLMMMMmmo',
    'oMMMMMMMLmmo',
    '.ommmmmmmmo.',
    '..oooooooo..',
    '............',
])

EFFECTS = {
    'toilet_paper_streamer_001': STREAMER,
    'toilet_paper_bits_001': PAPER_BITS,
    'toilet_paper_confetti_001': CONFETTI,
    'coffee_shard_001': SHARD_1,
    'coffee_shard_002': SHARD_2,
    'coffee_shard_003': SHARD_3,
    'coffee_shard_004': SHARD_HEART,
    'coffee_puddle_001': COFFEE_PUDDLE,
}


# --------------------------------------------------------- Coco Matching Cones
# Solid blue tones suggest translucent plastic while retaining hard alpha.
CONE = R([
    'ooooooooooooooooo',
    'o111111111111111o',
    '.o1FFFFFFFFFFF1o.',
    '.o1FFFFFFFFFFF1o.',
    '..o1FFFFFFFFF1o..',
    '..o1FFFFFFFFF1o..',
    '...o1FFFFFFF1o...',
    '...o1FFFFFFF1o...',
    '....o1FFFFF1o....',
    '....o1FFFFF1o....',
    '.....o1FFF1o.....',
    '.....o1FFF1o.....',
    '......o1F1o......',
    '......ooooo......',
])
CONE_DOWN = R([
    '..oooooo',
    '.o11111o',
    'o11FFFFo',
    'o1FFFfo.',
    '.offfo..',
    '..ooo...',
])


def _behind(base, top, dx, dy):
    """Place the rear shell around (not over) the plain Coco pixels."""
    canvas = [list(row) for row in base]
    for y, row in enumerate(top):
        for x, ch in enumerate(row):
            X, Y = x + dx, y + dy
            if ch != '.' and 0 <= X < len(canvas[0]) and 0 <= Y < len(canvas) and canvas[Y][X] == '.':
                canvas[Y][X] = ch
    return [''.join(row) for row in canvas]


def _worn(frame):
    # Knight canvas is four rows taller than the plain clip.  Follow each
    # frame's actual head so the cone rises with hops and settles with squashes.
    canvas = pad(frame, V4.KNIGHT_W, V4.KNIGHT_H, 0, V4.KNIGHT_H - V4.COCO_H)
    top = min(y for y, row in enumerate(canvas) if any(ch != '.' for ch in row))
    cone_y = min(max(0, top - 3), V4.KNIGHT_H - len(CONE))
    return _behind(canvas, CONE, 0, cone_y)


COCO_CONE_IDLE = [_worn(f) for f in V4.COCO_IDLE]
COCO_CONE_MOVE = [_worn(f) for f in V4.COCO_MOVE]
COCO_CONE_PET = [_worn(f) for f in V4.COCO_PET]
COCO_CONE_BLOCK = [_worn(f) for f in V4.COCO_BLOCK]
# The cone slips beside Coco when knocked out, on the exact 24x16 knight KO
# canvas.  The plain KO pixels remain byte-for-byte unchanged.
COCO_CONE_KO = [_behind(pad(f, 24, 16, 0, 0), CONE_DOWN, 15, 9) for f in V4.COCO_KO]

CONE_CLIPS = {
    'idle': COCO_CONE_IDLE,
    'move': COCO_CONE_MOVE,
    'pet': COCO_CONE_PET,
    'block': COCO_CONE_BLOCK,
    'ko': COCO_CONE_KO,
}
