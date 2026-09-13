"""Art lint for the body clips (run from make_art; also: python3 tools/lint_art.py).

Checks encode the rules from docs/research/03a and 03b:
  size       every frame is W x H
  border     the outer ring of the canvas holds only transparency or outline (the game draws the outline
             1 px outside the fill, so fill must never touch the canvas edge)
  ground     grounded frames keep the feet fill on GROUND; airborne frames are declared per clip
  colours    at most MAX_KEYS palette keys per frame (excluding '.' and 'o')
  holds      identical consecutive frames are declared holds, not accidents
  palette    every key exists (img_from_rows raises otherwise)
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
    'pet': {1}, 'slide_right': ALL, 'slide_up': ALL, 'slide_down': ALL, 'chest_recover': set(),
}
# clips where repeated frames are intentional holds
HOLDS = {'death', 'death_shot', 'item_get', 'chest_recover', 'select_choose', 'knock', 'loaf', 'pet', 'slide_right',
         'slide_up', 'slide_down', 'stretch', 'ghost_sneeze_left', 'ghost_sneeze_right', 'timefall', 'spinfall',
         'dodge', 'dodge_bw', 'dodge_left', 'dodge_left_bw', 'death_coop', 'tablekick_right', 'jetpack_down',
         'jetpack_right', 'jetpack_right_bw', 'jetpack_up', 'doorway', 'idle', 'idle_forward', 'idle_backward', 'idle_bw',
         'select_idle', 'groom'}


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
            seen = f
    return errors, warnings


def main():
    import character_anims as A
    e1, w1 = lint(A.CLIPS, A.W, A.H, A.GROUND)
    e2, w2 = lint(A.BREACH_IDLES, A.W, A.H, A.GROUND, label='breach/')
    errors, warnings = e1 + e2, w1 + w2
    for w in warnings:
        print('warn ', w)
    for e in errors:
        print('ERROR', e)
    n = sum(len(v) for v in A.CLIPS.values() if v) + sum(len(v) for v in A.BREACH_IDLES.values())
    print(f'lint: {n} frames, {len(errors)} error(s), {len(warnings)} warning(s)')
    return len(errors)


if __name__ == '__main__':
    sys.exit(1 if main() else 0)
