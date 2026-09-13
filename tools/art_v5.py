"""Version 2.3 art: Puffed Up (angry) passive: fur halo frames, anger marks VFX, item icon."""
import math
from pixel import check_rect as R
from art_v3 import blank, put

# ---------------------------------------------------------------- fur halo: a 36 x 36 ring of bristling tufts drawn BEHIND the player,
# the body itself is scaled up in code; two frames shimmer.
def halo(phase):
    W = H = 36
    grid = [['.'] * W for _ in range(H)]
    cx, cy = 17.5, 18.5
    tufts = 26
    for i in range(tufts):
        a = 2 * math.pi * (i + phase * 0.5) / tufts
        # elliptical ring slightly taller than wide, like a puffed-up cat silhouette
        rx, ry = 13.5, 15.5
        length = 3 if i % 2 == 0 else 2
        for k in range(length):
            x = int(round(cx + math.cos(a) * (rx + k)))
            y = int(round(cy + math.sin(a) * (ry + k)))
            if 0 <= x < W and 0 <= y < H:
                grid[y][x] = ('B' if k < length - 1 else 'b') if i % 3 else ('W' if k < length - 1 else 'w')
        # outline pixel at the tip
        x = int(round(cx + math.cos(a) * (rx + length)))
        y = int(round(cy + math.sin(a) * (ry + length)))
        if 0 <= x < W and 0 <= y < H:
            grid[y][x] = 'o'
    return [''.join(r) for r in grid]


FUR_HALO = [halo(0), halo(1)]

# ---------------------------------------------------------------- anger marks VFX (the comic "vein" cross), 4 frames 12 x 12
def marks(stage):
    c = blank(12, 12)
    mark = R([
"R..R",
".RR.",
".RR.",
"R..R",
    ])
    positions = [(4, 4), (2, 3), (6, 2), (4, 1)][stage]
    c = put(c, mark, *positions)
    if stage >= 2:
        c = put(c, mark, 1 if stage == 2 else 7, 7)
    return c


ANGER_MARKS = [marks(i) for i in range(4)]

# ---------------------------------------------------------------- Puffed Up item icon 16 x 16: angry bristling cat face
PUFFED_ICON = R([
"o..o.oo.oo.o..o.",
".oBBo.BB.oBBo...",
"o.BPBBBBBBBPB.o.",
".oBBBBWWBBBBBo..",
"oBBBBBBBBBBBBBo.",
".oBBWWWWWWWWBo.o",
"oBBWoWWWWWWoWBBo",
".oBWWoWWWWoWWBo.",
"o.oWWWWPPWWWWo.o",
".oBWWWWppWWWWBo.",
"o.oBWWWWWWWWBo..",
".o.oBBWWWWBBo.o.",
"..o.oooooooo.o..",
".o..o......o..o.",
"................",
"................",
])
