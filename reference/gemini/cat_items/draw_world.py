"""In-world sprites for the 2.17 cat items (projectiles, the placed post, VFX), hand-drawn as row strings in the
icons' palette. Writes approved art to reference/art/cat_items/ (make_art.py copies it into Resources).
Run from the repo root: python3 reference/gemini/cat_items/draw_world.py"""
import math
import os
import sys
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from draw_items import PAL, render as _render16  # noqa: E402

OUT = 'reference/art/cat_items'


def render(rows):
    h, w = len(rows), len(rows[0])
    assert all(len(r) == w for r in rows), [len(r) for r in rows]
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    for y, row in enumerate(rows):
        for x, k in enumerate(row):
            if k != '.':
                im.putpixel((x, y), tuple(int(PAL[k][i:i + 2], 16) for i in (0, 2, 4)) + (255,))
    return im


# Ball of Yarn projectile: two tumble frames (the second is the first turned a quarter, light kept top-left).
YARN_BALL = [
    '...oooo...',
    '.ooqqPPoo.',
    '.oqqPPPpo.',
    'oqPPppPPpo',
    'oPppPPPppo',
    'oPPPPppPpo',
    'oPpppPPppo',
    '.oPPPPppo.',
    '..oppppoo.',
    '...oooo...',
]
YARN_BALL_2 = [
    '...oooo...',
    '.ooqqPPoo.',
    '.oqPppPPo.',
    'oqPPPPppPo',
    'oPPppPPPpo',
    'oPpPPPpppo',
    'oPPPpppPpo',
    '.oppPPPpo.',
    '..oppppoo.',
    '...oooo...',
]

HAIRBALL_ITEM = [
    '....o..o....',
    '.....oo.....',
    '...oooooo...',
    '..oLLBBBBo..',
    '.oLWLBddBBo.',
    '.oLLBBBBddo.',
    'ooLBddBBBdoo',
    '.oBBBBddBdo.',
    '.oddBBBBddo.',
    '..oddBdddo..',
    '...oooooo...',
    '............',
]

# The post Pluto places: taller than the icon, pom-pom on a string, two claw marks on the rope.
POST = [
    '...oooooooooo...',
    '..oVVVVVVVVVVo..',
    '..ovvvvvvvvvvoo.',
    '....ooSSSSoo..b.',
    '.....oSSSSo...b.',
    '.....osssso...b.',
    '.....oSSSSo..oqo',
    '.....oSSSSo.oqqo',
    '.....osssso.oPPo',
    '.....oSSSSo..oo.',
    '.....oSSSSo.....',
    '.....osssso.....',
    '.....oSwSSo.....',
    '.....oSwSSo.....',
    '.....osssso.....',
    '.....oSSSwo.....',
    '.....oSSSwo.....',
    '.....osssso.....',
    '...oooSSSSooo...',
    '..oVVVVVVVVVVo..',
    '..oVVVVVVVVVVo..',
    '..oVVVVVVVVVvo..',
    '..ovvvvvvvvvvo..',
    '...oooooooooo...',
]


def ring_frames():
    """Jingle: a gold ring that widens and breaks up, with a bright inner edge."""
    frames = []
    for radius, dashed in ((4, False), (7, False), (10, False), (11, True)):
        im = Image.new('RGBA', (24, 24), (0, 0, 0, 0))
        for y in range(24):
            for x in range(24):
                d = math.hypot(x + 0.5 - 12, y + 0.5 - 12)
                if radius - 2 <= d < radius:
                    if dashed and (int(math.degrees(math.atan2(y - 12, x - 12)) + 180) // 30) % 2:
                        continue
                    key = 'h' if d < radius - 1 else 'Y'
                    im.putpixel((x, y), tuple(int(PAL[key][i:i + 2], 16) for i in (0, 2, 4)) + (255,))
        frames.append(im)
    return frames


LEAF = ['...oo...', '..oGGo..', '.oGGGGo.', 'oGGGGgo.', '.ogggo..', '..ooo...']
LEAF_SMALL = ['.oo.', 'oGGo', 'oggo', '.oo.']


def leaf_frames():
    """Catnip: a little leaf drifting up out of Pluto's fur and shrinking away."""
    frames = []
    for y, rows in ((6, LEAF), (4, LEAF), (2, LEAF), (1, LEAF_SMALL)):
        im = Image.new('RGBA', (12, 12), (0, 0, 0, 0))
        leaf = render(rows)
        im.paste(leaf, ((12 - leaf.width) // 2 + (1 if y == 5 else 0), y), leaf)
        frames.append(im)
    return frames


def main():
    os.makedirs(OUT, exist_ok=True)
    render(YARN_BALL).save(f'{OUT}/pluto_yarn_ball_001.png')
    render(YARN_BALL_2).save(f'{OUT}/pluto_yarn_ball_002.png')
    render(HAIRBALL_ITEM).save(f'{OUT}/pluto_hairball_item_001.png')
    render(POST).save(f'{OUT}/scratching_post_placed.png')
    for i, im in enumerate(ring_frames(), 1):
        im.save(f'{OUT}/jingle_{i:03d}.png')
    for i, im in enumerate(leaf_frames(), 1):
        im.save(f'{OUT}/catnip_{i:03d}.png')
    print('world sprites written to', OUT)


if __name__ == '__main__':
    main()
