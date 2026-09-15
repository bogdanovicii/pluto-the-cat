"""Art lint for the body clips (run from make_art; also: python3 tools/lint_art.py).

Checks encode the rules from docs/research/03a and 03b:
  size       every frame is W x H
  border     the outer ring of the canvas holds only transparency or outline (the game draws the outline
             1 px outside the fill, so fill must never touch the canvas edge)
  ground     grounded frames keep the feet fill on GROUND; airborne frames are declared per clip
  colours    at most MAX_KEYS palette keys per frame (excluding '.' and 'o')
  holds      identical consecutive frames are declared holds, not accidents
  palette    every key exists (img_from_rows raises otherwise)
  orphans    a drawn pixel with no drawn 8-neighbour (stray pixel) -> warning
  flicker    after aligning consecutive frames by their content box, a single-pixel difference -> warning
Errors fail the build; warnings are printed.
"""
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

MAX_KEYS = 14
# clips whose content legitimately leaves the canvas (sinking into a pit, tumbling)
EDGE_OK = {'pitfall', 'pitfall_down', 'pitfall_return', 'spit_out'}
ALL = 'all'

# frames whose feet are legitimately off the ground (index sets) or ALL
AIRBORNE = {
    'run_right': {1, 2, 4, 5}, 'run_right_bw': {1, 2, 4, 5}, 'run_down': {1, 2, 4, 5}, 'run_up': {1, 2, 4, 5},
    'dodge': {1, 2, 3, 4, 5, 6}, 'dodge_bw': {1, 2, 3, 4, 5, 6}, 'dodge_left': {1, 2, 3, 4, 5, 6}, 'dodge_left_bw': {1, 2, 3, 4, 5, 6},
    'doorway': {1, 2, 4}, 'tablekick_right': set(), 'tablekick_down': {1}, 'tablekick_up': {1},
    'pitfall': ALL, 'pitfall_down': ALL, 'pitfall_return': ALL, 'spinfall': ALL, 'timefall': ALL, 'spit_out': ALL,
    'jetpack_down': ALL, 'jetpack_right': ALL, 'jetpack_right_bw': ALL, 'jetpack_up': ALL,
    'ghost_idle_back': ALL, 'ghost_idle_back_left': ALL, 'ghost_idle_back_right': ALL, 'ghost_idle_front': ALL,
    'ghost_idle_left': ALL, 'ghost_idle_right': ALL, 'ghost_sneeze_left': ALL, 'ghost_sneeze_right': ALL,
    'death_coop': ALL, 'death': {5}, 'death_shot': {4}, 'item_get': {1}, 'select_choose': {1}, 'stretch': ALL,
    'coco_move': {1, 2, 3}, 'coco_block': {2}, 'coco_knight_move': {1, 2, 3}, 'coco_knight_block': {2},
    'yasupen_move': {1, 3}, 'yasupen_pet': {3}, 'yasupen_cheer': {1},   # 2.18.0 Yasupen hop frames (shifted up 1 px)
    'pet': {1}, 'slide_right': ALL, 'slide_up': ALL, 'slide_down': ALL, 'chest_recover': set(),
}
# clips where repeated frames are intentional holds
# max changed-pixel fraction between consecutive frames (looping clips only)
HOLDS = {'death', 'death_shot', 'item_get', 'chest_recover', 'select_choose', 'knock', 'loaf', 'pet', 'slide_right',
         'slide_up', 'slide_down', 'stretch', 'ghost_sneeze_left', 'ghost_sneeze_right', 'timefall', 'spinfall',
         'dodge', 'dodge_bw', 'dodge_left', 'dodge_left_bw', 'death_coop', 'tablekick_right', 'jetpack_down',
         'jetpack_right', 'jetpack_right_bw', 'jetpack_up', 'doorway', 'idle', 'idle_forward', 'idle_backward', 'idle_bw',
         'select_idle', 'groom', 'coco_idle', 'coco_knight_idle', 'yasupen_idle'}


def bbox(f):
    ys = [y for y, r in enumerate(f) if any(ch != '.' for ch in r)]
    xs = [x for r in f for x, ch in enumerate(r) if ch != '.']
    return (min(xs), min(ys)) if ys else (0, 0)


def aligned_diff(a, b, W, H):
    (ax, ay), (bx, by) = bbox(a), bbox(b)
    dx, dy = bx - ax, by - ay
    n = 0
    for y in range(H):
        for x in range(W):
            pa = a[y - dy][x - dx] if 0 <= y - dy < H and 0 <= x - dx < W else '.'
            if pa != b[y][x]:
                n += 1
    return n


def base_clip(name):
    for suf in ('_twohands', '_hand'):
        if name.endswith(suf):
            return name[:-len(suf)]
    return name


def lint(clips, W, H, ground, label=''):
    errors, warnings = [], []
    for name, frames in clips.items():
        if not frames:
            continue
        base = base_clip(name)
        air = AIRBORNE.get(base, set())
        seen = None
        for i, f in enumerate(frames):
            tag = f'{label}{name}[{i}]'
            if len(f) != H or any(len(r) != W for r in f):
                errors.append(f'{tag}: size {len(f[0])}x{len(f)} != {W}x{H}')
                continue
            fill_rows = [y for y, r in enumerate(f) if any(ch not in '.o' for ch in r)]
            # border: fill must not touch the canvas edge (outline margin)
            edge = any(ch not in '.o' for ch in f[0]) or any(ch not in '.o' for ch in f[-1]) \
                or any(r[0] not in '.o' or r[-1] not in '.o' for r in f)
            if edge and base not in EDGE_OK:
                errors.append(f'{tag}: fill touches the canvas edge (no room for the runtime outline)')
            if fill_rows and air != ALL and i not in air and fill_rows[-1] != ground:
                errors.append(f'{tag}: feet fill row {fill_rows[-1]} != ground {ground} on a grounded frame')
            keys = {ch for r in f for ch in r if ch not in '.o'}
            if len(keys) > MAX_KEYS:
                warnings.append(f'{tag}: {len(keys)} colours > {MAX_KEYS}: {"".join(sorted(keys))}')
            if seen is not None and f == seen and base not in HOLDS:
                warnings.append(f'{tag}: identical to the previous frame (declare a hold or draw a key)')
            if seen is not None:
                # stray-pixel flicker: after aligning the two frames by their content boxes, a change of
                # exactly one pixel is a pixel blinking on and off, not an animation key (a 2-px ear flick is fine)
                changed = aligned_diff(seen, f, W, H)
                if changed == 1:
                    warnings.append(f'{tag}: a single pixel differs from the previous frame after alignment (stray flicker?)')
            for y in range(H):
                for x in range(W):
                    if f[y][x] in '.o':
                        continue
                    if not any(0 <= x + dx < W and 0 <= y + dy < H and f[y + dy][x + dx] != '.'
                               for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy):
                        warnings.append(f'{tag}: orphan pixel {f[y][x]!r} at ({x},{y})')
            seen = f
    return errors, warnings


def main():
    import character_anims as A
    e1, w1 = lint(A.CLIPS, A.W, A.H, A.GROUND)
    e2, w2 = lint(A.BREACH_IDLES, A.W, A.H, A.GROUND, label='breach/')
    import art_v4 as V4   # Coco companion clips (bottom 'o' row at H-1, fill ground at H-2)
    plain = {'coco_idle': V4.COCO_IDLE, 'coco_move': V4.COCO_MOVE, 'coco_pet': V4.COCO_PET, 'coco_block': V4.COCO_BLOCK}
    e4, w4 = lint(plain, V4.COCO_W, V4.COCO_H, V4.COCO_H - 2, label='companion/')
    knight = {'coco_knight_idle': V4.COCO_KNIGHT_IDLE, 'coco_knight_move': V4.COCO_KNIGHT_MOVE,
              'coco_knight_pet': V4.COCO_KNIGHT_PET, 'coco_knight_block': V4.COCO_KNIGHT_BLOCK}
    e3, w3 = lint(knight, V4.KNIGHT_W, V4.KNIGHT_H, V4.KNIGHT_H - 2, label='companion/')
    import art_yasupen as PEN
    pen = {'yasupen_idle': PEN.PEN_IDLE, 'yasupen_move': PEN.PEN_MOVE, 'yasupen_pet': PEN.PEN_PET, 'yasupen_cheer': PEN.PEN_CHEER}
    e5, w5 = lint(pen, PEN.PEN_W, PEN.PEN_H, PEN.PEN_H - 2, label='companion/')
    errors, warnings = e1 + e2 + e3 + e4 + e5, w1 + w2 + w3 + w4 + w5
    for w in warnings:
        print('warn ', w)
    for e in errors:
        print('ERROR', e)
    n = sum(len(v) for v in A.CLIPS.values() if v) + sum(len(v) for v in A.BREACH_IDLES.values())
    print(f'lint: {n} frames, {len(errors)} error(s), {len(warnings)} warning(s)')
    return len(errors)


if __name__ == '__main__':
    sys.exit(1 if main() else 0)
