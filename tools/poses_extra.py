"""Additional hand-drawn poses: dodge-roll ball and death sequence (18 x 20 canvas / 16 x 16 ball)."""
from pixel import check_rect as R

# ---------------------------------------------------------------- dodge roll ball (16 x 16)
# Ears at the top, face on the white belly, tail wrapped around the bottom-left, so the
# 90-degree rotations read as a real tumble instead of a plain circle.
BALL = R([
"..oo.......oo...",
".oBBo.oWo.oBBo..",
".oBPBoWWWoBPBo..",
"..oBBBBWBBBBo...",
".oBbBBBBBBBBBo..",
"oBBBBWWWWWWBBBo.",
"oBBBWWoWWWoWWBBo",
"oBbBWWWWWWWWWBbo",
"oBBBWWWWPWWWWBBo",
"oBBBBWWWpWWWWBBo",
"oBBBBBWWWWWBBBBo",
".oBbBBBBBBBBbBo.",
"ooBBBBBBBBBBBBo.",
"obBoBBbBBBBbBo..",
"oBBooBBBBBBoo...",
".ooo.oooooo.....",
])

# Crouch / wind-up before the roll: leaning forward, ears back.
CROUCH = R([
"..................",
"..................",
"..................",
"..................",
"......oo.....oo...",
".....oBBo...oBBo..",
"....oBBPBoooBPBBo.",
"...oBBBBBWWBBBBBo.",
"..oBBbBBWWWWBBbBBo",
"..oBBBBBWWWWBBBBBo",
"..oBBWWoWWWWoWWBBo",
"..oBWWWWWWWWWWWWWo",
"..oWWWWWWWPPWWWWWo",
"..oBBBWWWWWWWWWBo.",
".oBbBBBWWWWWWWBBo.",
"...oBBBBWWWWWWBBo.",
"...oBBBBBWWWWWBBo.",
"....oBBBBWWWWBBo..",
"....oWWWo..oWWWo..",
".....ooo....ooo...",
])

# Landing squash after the roll.
LAND = R([
"..................",
"..................",
"..................",
"..................",
"..................",
"......oo.....oo...",
".....oBBoooooBBo..",
"....oBBPBWWWBPBBo.",
"...oBBbBWWWWBbBBBo",
"...oBBBBBBWWBBBBBo",
"...oBBBWWGgWWGgBBo",
"...oBWWWWWWWWWWWWo",
"...oWWWWWWWPPWWWWo",
"...oBBBWWWWpWWWBo.",
"..oBbBBWWWWWWWWBo.",
".oBBBBBBWWWWWWBBo.",
"...oBBBBBWWWWWBBo.",
"....oBBBWWWWWBBBo.",
"....oWWWo...oWWWo.",
".....ooo.....ooo..",
])

# ---------------------------------------------------------------- death sequence
# Hit: eyes shut, mouth open, knocked back (drawn facing right, the game mirrors).
HIT = R([
"......oo.....oo...",
".....oBBo...oBBo..",
".....oBPBoooBPBo..",
"....oBBBBWWBBBBBo.",
"...oBBbBWWWWBBbBBo",
"...oBBBBBBBBBBBBBo",
"...oBBBBBWWWWBBBBo",
"...oBBWWooWWWWooBo",
"...oBWWWWWWWWWWWWo",
"...oWWWWWWWPPWWWWo",
"....oWWWWWoppoWWo.",
"....oBBBWWWppWWBo.",
"...oBbBBWWWWWWWBo.",
"...oBBBBWWWWWWWBo.",
"...obBBBWWWWWWWBo.",
"...oBBBBBWwWWWBBo.",
"....oBBBwWWWwBBo..",
".....oWWo...oWWo..",
".....owwo...owwo..",
"......oo.....oo...",
])

# Knees buckle: lower, eyes shut.
KNEEL = R([
"..................",
"..................",
"..................",
"..................",
"......oo.....oo...",
".....oBBo...oBBo..",
".....oBPBoooBPBo..",
"....oBBBBWWBBBBBo.",
"...oBBbBWWWWBBbBBo",
"...oBBBBBBBBBBBBBo",
"...oBBWWooWWWWooBo",
"...oBWWWWWWWWWWWWo",
"...oWWWWWWWPPWWWWo",
"....oWWWWWWpWWWWo.",
"....oBBBWWWWWWBBo.",
"...oBbBBWWWWWWWBo.",
"...oBBBBWWWWWWWBo.",
"...oBBBBBWWWWWBBo.",
"....oBBBWWWWWBBo..",
".....oooo...oooo..",
])

# Tipping over: head down, about to hit the floor.
TIP = R([
"..................",
"..................",
"..................",
"..................",
"..................",
"..................",
"..................",
"..................",
"........ooooo.....",
"..ooo.ooBBooBoo...",
"..oBBoBBBWWBBBBo..",
"oBBBBBBBBWWWBBBBo.",
"oBBbBBBWWWWWWWBBo.",
".oBBBBWWooWWooWBo.",
".oBBBWWWWWWWWWWWo.",
"..oBBWWWWWWPPWWWo.",
"..oBBWWWWWWpWWWo..",
"...oBBWWWWWWWWo...",
"....oooWWoWWoo....",
".......oo.oo......",
])

# Final: flat on his side, X eyes, tongue out, tail limp.
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
"..........oooooo..",
".........oBBWWBBo.",
"....ooooooBBWWBBo.",
"..ooBBBbBBBBBBBBBo",
".oBBBBBBBBBoWoWWBo",
"oBbBBBWWWWWWoWWWWo",
"oBBBBWWWWWWoWoWPWo",
".oBBBWWWWWWWWWWpWo",
"...oooWWooWWooWWo.",
"..o...oo..oo..oo..",
"..................",
])


# ---------------------------------------------------------------- the tail (raccoon-ringed, dark tip)
# Drawn on the 24-wide canvas BEHIND the body (body is overlaid on top), so its base tucks in
# at the rump. Curves out from the rump, up, and hooks back at the tip. Four ring bands.
# TAIL_A / TAIL_B differ by the tip position for a gentle sway.
TAIL_A = R([
"..ooo...",
".obbbo..",
".obbbo..",
"oBBBo...",
"oBBBo...",
"obbbo...",
"obbbo...",
".oBBBo..",
"..obbBBo",
"...oBBBo",
"....oooo",
])
TAIL_B = R([
"...ooo..",
"..obbbo.",
".obbbo..",
"oBBBo...",
"oBBBo...",
"obbbo...",
"obbbo...",
".oBBBo..",
"..obbBBo",
"...oBBBo",
"....oooo",
])
# Lying dead: tail stretched out flat on the floor to the left, rings visible, dark tip.
TAIL_FLAT = R([
"ooooooooo..",
"obbbBBbbBBo",
"ooooooooooo",
])


# ---------------------------------------------------------------- v2 breach idles
# Cat loaf: paws tucked, body low, tail wrapped around the front. 18 x 20 canvas.
LOAF = R([
"..................",
"..................",
"..................",
"..................",
"..................",
"......oo.....oo...",
".....oBBo...oBBo..",
".....oBPBoooBPBo..",
"....oBBBBWWBBBBBo.",
"...oBBbBWWWWBBbBBo",
"...oBBBBBBBBBBBBBo",
"...oBBBBBWWWWBBBBo",
"...oBBWWGgWWWWGgBo",
"...oBWWWGgWWWWGgWo",
"...oWWWWWWWPPWWWWo",
"..ooBBWWWWWpWWWBo.",
".oBbBBBBBWWWWWBBBo",
"obBBbBBBBBBBBBBBBo",
"oBBboBBBBWWWWBBBBo",
".oo.oooooooooooooo",
])

# Grooming: paw raised to the face, two frames (paw up / paw at cheek). Side view.
GROOM_PAW = R([  # 5x4 raised paw, overlaid near the cheek
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
