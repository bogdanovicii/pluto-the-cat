"""Additional poses: dodge ball, crouch/land/hit/kneel (composed from parts), tip-over, lying dead,
tails, breach-idle props. Pose canvas 18 x 22 (feet fill on row 20, outline row 21) unless noted."""
from pixel import check_rect as R, pad, overlay
import poses as P

# ---------------------------------------------------------------- dodge roll ball (16 x 16)
# Ears at the top, face on the white belly, tail wrapped around the bottom-left with its rings,
# the head spot near the ear line, so the 90-degree rotations read as a real tumble.
BALL = R([
"..oo.......oo...",
".oBBo.....oBBo..",
".oBPBoooooBPBo..",
"..oBBBBWBBBBo...",
".oBbBBBWBBBBBo..",
"oBBBBBBBBBBBBBo.",
"oBBBGgBWWBGgBBBo",
"oBbBBWWWWWWWBBbo",
"oBBBWWWWPWWWWBBo",
"oBBBBWWWpWWWWBBo",
"oBBBBBWWWWWBBBBo",
".oBbBBBBBBBBbBo.",
"obBBBBBBBBBBBBo.",
"obbobBBbBBBBbBo.",
"oBBoobbBBBBoo...",
".ooo.oooooo.....",
])

# ---------------------------------------------------------------- low body (crouch / land / kneel): 4 rows + 3 leg rows
BODY_SIDE_LOW = R([
"...oBBBBWWWWWWWBBo",  # 15 wider, lower
"..oBbBBBWWWWWWWBBo",  # 16
"..oBBbBBBWWwwwwBBo",  # 17
"...oBBBBwwwwwwBBo.",  # 18
])
LEGS_SPLAYED = R([
"....oWWWo..oWWWo..",  # 19
"....owwwo..owwwo..",  # 20
".....ooo....ooo...",  # 21
])
BLANK = ['.' * P.W]


def low_pose(head_dy, eye_kind='open', mouth=False):
    """Head pushed down by head_dy rows over the low body: crouch (3), land (2), kneel (3, eyes shut)."""
    head = P.eyes(P.HEAD_SIDE, P.EYES_SIDE, eye_kind)
    if mouth:
        head = P.mouth_open(head, 11, 11)
    rows = BLANK * head_dy + list(head)                   # rows 0 .. head_dy+11
    rows = rows[:15] if len(rows) > 15 else rows + BLANK * (15 - len(rows))
    rows = rows + list(BODY_SIDE_LOW) + list(LEGS_SPLAYED)
    # the mouth row of the head (row head_dy+11) may be cut by the body: re-overlay the head so the
    # chin sits on the shoulders
    rows = R(rows)
    rows = overlay(rows, head, 0, head_dy)
    return R(rows)


CROUCH = low_pose(3)                      # wind-up before the roll
LAND = low_pose(2)                        # landing squash after the roll
KNEEL = low_pose(3, 'shut')               # knees buckle (death)
KNEEL_LOW = low_pose(4, 'shut')           # ... and sag one more pixel

# Hit: eyes shut, mouth open, knocked back (drawn facing right, the game mirrors).
HIT = P.stack(P.mouth_open(P.eyes(P.HEAD_SIDE, P.EYES_SIDE, 'shut'), 11, 11), P.BODY_SIDE, P.LEGS_SIDE)

# Tipping over: head down toward the floor, rump up.
TIP = R([
"..................",
"..................",
"..................",
"..................",
"..................",
"..................",
"..................",
"..................",
"..................",
"..................",
"........ooooo.....",
"..ooo.ooBBBBBoo...",
"..oBBoBBBBBBBBBo..",
"oBBBBBBBBWWWBBBBo.",
"oBBbBBBBBBBBBBBBo.",
".oBBBBBBbbBBbbBBo.",
".oBBBBBWWWWWWWWWo.",
"..oBBWWWWWWPPWWWo.",
"..oBBWWWWWWpWWWo..",
"...oBBWWWWWWWWo...",
"....oooWWoWWoo....",
".......oo.oo......",
])

# Final: flat on his side, X eyes, tongue out. Body starts at x=5 so the flat tail shows on the left.
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
"..................",
"..................",
"..................",
"...........oooooo.",
"..........oBBBBBBo",
".....oooooBBbBBBBo",
"....oBBbBBBBBBb9Bo",
"...oBBBBBBBBBBB9bo",
"...oBbBBBWWWWWWWWo",
"...oBBBBWWWWWWWPWo",
"....oBBBWWWWWWWpWo",
"....oooWWoWWoWWoo.",
"......oo..oo..oo..",
])

# ---------------------------------------------------------------- the tail (raccoon-ringed, dark tip)
# Drawn BEHIND the body (body overlaid on top), base tucked in at the rump. Bands alternate the
# base tone and the near-black stripe tone (2 rows each) so the rings survive at 1x.
TAIL_A = R([          # raised, tip curling forward (idle)
"..ooo...",
".obbbo..",
".obbbo..",
"oBBBo...",
"oBBBo...",
"obbbo...",
"obbbo...",
".oBBBo..",
"..oBBBBo",
"...obbBo",
"....oooo",
])
TAIL_B = R([          # sway: tip one pixel over
"...ooo..",
"..obbbo.",
".obbbo..",
"oBBBo...",
"oBBBo...",
"obbbo...",
"obbbo...",
".oBBBo..",
"..oBBBBo",
"...obbBo",
"....oooo",
])
TAIL_RUN_A = R([      # streaming back while running, tip up
"oooo.......",
"obbbo......",
"obbbBoo....",
".oBBBBBoo..",
"..oobbbBBoo",
"....oobbBBo",
"......oooBo",
".........oo",
])
TAIL_RUN_B = R([      # streaming back, tip level
"...........",
".oooo......",
"obbbboo....",
"obbbBBBoo..",
".ooBbbbBBoo",
"...oobbbBBo",
"......oooBo",
".........oo",
])
# Lying dead: tail stretched out flat on the floor to the left, rings visible, dark tip.
TAIL_FLAT = R([
"ooooooooooo",
"obbbBBbbBBo",
"ooooooooooo",
])


# ---------------------------------------------------------------- breach idles
# Cat loaf: paws tucked, body low, tail wrapped around the front. The breathing frame moves the
# head down one row over the loaf (a squash), never the loaf itself (it sits on the floor).
LOAF_BODY = R([
".ooBbBBBBWWWWWBBBo",   # 18
"obBBBbBBBBBBBBBBBo",   # 19
"oBBboBBBBWWWWBBBBo",   # 20  the tail wraps around the front (rings)
".oo.oooooooooooooo",   # 21
])


def loaf(head_dy):
    head = P.eyes(P.HEAD_SIDE, P.EYES_SIDE, 'happy')
    rows = pad(head, P.W, P.H, 0, head_dy)
    return R(overlay(rows, LOAF_BODY, 0, 18))


LOAF = loaf(6)
LOAF_DOWN = loaf(7)

# Grooming: raised paw (5x4), overlaid near the cheek.
GROOM_PAW = R([
".ooo.",
"oWWWo",
"oWWWo",
".ooo.",
])

# Bowl for the "knock it off the table" idle (10 x 6) and the ledge (12 x 3).
BOWL = R([
"..oooooo..",
".oYyYYyYo.",
"oSSSSSSSSo",
".oSsSSsSo.",
"..oossoo..",
"...oooo...",
])
LEDGE = R([
"oooooooooooo",
"oXXXXXXXXXXo",
"oooooooooooo",
])
