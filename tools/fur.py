"""Frame-following fur layers for the Puffed Up passive.

For each body frame, a fur layer is generated on a larger canvas: spikes grow outward from every
silhouette edge pixel along the local outward direction. Four variants per frame:
  0 short (1 px), 1 medium (2 px), 2 long (3 px), 3 long with jitter (2-3 px, shifted pattern).
The runtime overlay swaps between them (bristle up -> shiver -> settle) while following the
player's current clip and frame, so the fur hugs Pluto's own outline in every direction.

Canvas: body 24x20 placed at (MARGIN_X, MARGIN_TOP) on a 32x24 canvas (no bottom margin: fur does
not stand under the feet). Both the body sprite and the fur sprite use a lower-centre anchor, so the
fur lines up when placed at the body sprite's position.
"""
import math
import character_anims as A

MARGIN_X, MARGIN_TOP = 4, 4
FUR_W, FUR_H = A.W + 2 * MARGIN_X, A.H + MARGIN_TOP

WHITE = set('WwxKq')
TABBY = set('BbdLlU')      # U/J wet keys are recoloured later; treat as fur
DARK = set('J j'.split())


def _hash(x, y, v):
    return (x * 73856093 ^ y * 19349663 ^ v * 83492791) & 0xffff


def fur_layer(rows, variant):
    h = len(rows); w = max(len(r) for r in rows)
    body = [list(r.ljust(w, '.')) for r in rows]
    out = [['.'] * FUR_W for _ in range(FUR_H)]

    def solid(x, y):
        return 0 <= x < w and 0 <= y < h and body[y][x] != '.'

    length_for = {0: 1, 1: 2, 2: 3, 3: 3}[variant]
    for y in range(h):
        for x in range(w):
            ch = body[y][x]
            if ch == '.':
                continue
            # outward normal: sum of directions toward empty neighbours (8-connected)
            nx = ny = 0
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)):
                if not solid(x + dx, y + dy):
                    nx += dx; ny += dy
            if nx == 0 and ny == 0:
                continue                                    # interior pixel
            norm = math.hypot(nx, ny)
            ux, uy = nx / norm, ny / norm
            if uy > 0.75:
                continue                                    # no fur standing under the feet / belly
            # sparser, staggered spikes: every other edge pixel, pattern shifted by variant
            hv = _hash(x, y, variant)
            if (x + y + (1 if variant == 3 else 0)) % 2:
                continue
            length = length_for
            if variant == 3:
                length = 2 + (hv % 2)
            # colour follows the fur underneath: white areas -> white spikes, tabby -> tabby spikes
            fur_ch, tip_ch = ('W', 'w') if ch in WHITE else ('B', 'b')
            if ch == 'o':
                # outline pixel: look one step inward for the fur colour
                ix, iy = int(round(x - ux)), int(round(y - uy))
                inner = body[iy][ix] if 0 <= ix < w and 0 <= iy < h else 'B'
                fur_ch, tip_ch = ('W', 'w') if inner in WHITE else ('B', 'b')
            for k in range(1, length + 1):
                px = int(round(x + ux * k)) + MARGIN_X
                py = int(round(y + uy * k)) + MARGIN_TOP
                bx, by = px - MARGIN_X, py - MARGIN_TOP
                if solid(bx, by):
                    continue                                # never draw over the body
                if 0 <= px < FUR_W and 0 <= py < FUR_H and out[py][px] == '.':
                    out[py][px] = tip_ch if k == length else fur_ch
    return [''.join(r) for r in out]


# Clips that get fur (everything Pluto can be doing while standing/moving; not death, pits, ghosts).
FUR_CLIPS = [
    'idle', 'idle_forward', 'idle_backward', 'idle_bw',
    'run_right', 'run_right_bw', 'run_down', 'run_up',
    'dodge', 'dodge_bw', 'dodge_left', 'dodge_left_bw',
    'item_get', 'chest_recover', 'pet', 'doorway', 'spit_out', 'spinfall', 'timefall',
    'jetpack_down', 'jetpack_right', 'jetpack_right_bw', 'jetpack_up',
    'slide_right', 'slide_up', 'slide_down',
    'tablekick_down', 'tablekick_right', 'tablekick_up',
]


def all_fur():
    """{clip: [[variant0, variant1, variant2, variant3] per frame]}"""
    result = {}
    for clip in FUR_CLIPS:
        frames = A.CLIPS.get(clip)
        if not frames:
            continue
        result[clip] = [[fur_layer(f, v) for v in range(4)] for f in frames]
    return result
