"""Derive every Alexandria CharacterAPI animation clip for Pluto from the key poses.

Returns {clip_folder: [rows, rows, ...]}. Folders whose value is None get a
cc_sprite_placeholder.png (Alexandria then falls back to the base clip).
"""
from pixel import shift, overlay, erase, flip_h, recolor, squash, rotate, pad, check_rect, scale_down, shade
import poses as P
import poses_extra as X

W, H = 24, P.H          # 18-wide poses sit at x=3 on a 24-wide canvas; the margins hold the tail
BODY_DX = 3
EMPTY = ['.' * W] * H


def with_legs(body, legs):
    """legs: list of (rows, dx, dy) placed on the body canvas (x already in 22-wide coords)."""
    out = body
    for rows, dx, dy in legs:
        out = overlay(out, rows, dx, dy)
    return out


def with_tail(pose18, kind='side', sway=0):
    """Widen an 18x20 pose to 22x20 and draw the ringed tail behind it.
    side/front: tail curls up on the left (behind the body); back: on the right; none: no tail."""
    body = pad(pose18, W, H, BODY_DX, 0)
    if kind == 'none':
        return body
    tail = X.TAIL_B if sway else X.TAIL_A
    if kind == 'back':
        canvas = pad(flip_h(tail), W, H, 16, 7)
    elif kind == 'lying':
        canvas = pad(X.TAIL_FLAT, W, H, 0, 15)
    else:
        canvas = pad(tail, W, H, 0, 7)
    return overlay(canvas, body)


# ---------------------------------------------------------------- idle (breathing: 4 frames)
def breathe(body18, kind, legs, bobs=(0, 0, 1, 0)):
    """Body bobs down by 1px on frame 3, legs stay planted, tail tip sways on frames 3-4."""
    out = []
    for i, b in enumerate(bobs):
        bd = with_tail(shift(body18, 0, b), kind, sway=(i >= 2))
        out.append(with_legs(bd, legs))
    return out


SIDE_LEGS = [(P.SIDE_LEG, 5 + BODY_DX, 17), (P.SIDE_LEG, 12 + BODY_DX, 17)]
FRONT_LEGS = [(P.SIDE_LEG, 3 + BODY_DX, 17), (P.SIDE_LEG, 12 + BODY_DX, 17)]
BACK_LEGS = FRONT_LEGS

IDLE_SIDE = breathe(P.SIDE_BODY, 'side', SIDE_LEGS)
IDLE_FRONT = breathe(P.FRONT_BODY, 'front', FRONT_LEGS)
IDLE_BACK = breathe(P.BACK_BODY, 'back', BACK_LEGS)


# ---------------------------------------------------------------- run cycles (6 frames)
def lean(body18, dx=1, upto=11):
    """Lean the head and shoulders forward by dx pixels (rows 0..upto)."""
    return [r if i > upto else (('.' * dx) + r)[:len(r)] if dx > 0 else r for i, r in enumerate(body18)]


def run_side(body18):
    """Vanilla-style hop cycle: contact (legs stretched wide) -> airborne (+2px, legs tucked) -> pass,
    then the same with the other leg leading. Body leans forward; tail streams and sways."""
    body = lean(body18)
    hipB, hipF, hy = 5 + BODY_DX, 12 + BODY_DX, 17
    keys = [
        (0,  [(P.LEG_BACK, hipB - 1, hy - 1), (P.LEG_FWD, hipF, hy - 1)]),        # contact, right leg forward
        (-2, [(P.LEG_TUCK, hipB, hy), (P.LEG_TUCK, hipF, hy)]),                    # airborne
        (-1, [(P.SIDE_LEG, hipB + 1, hy), (P.SIDE_LEG_LONG, hipF - 1, hy - 1)]),   # pass
        (0,  [(P.LEG_FWD, hipB, hy - 1), (P.LEG_BACK, hipF - 1, hy - 1)]),        # contact, left leg forward
        (-2, [(P.LEG_TUCK, hipB, hy), (P.LEG_TUCK, hipF, hy)]),                    # airborne
        (-1, [(P.SIDE_LEG_LONG, hipB, hy - 1), (P.SIDE_LEG, hipF - 1, hy)]),       # pass
    ]
    out = []
    for i, (dy, legs) in enumerate(keys):
        bd = with_tail(shift(body, 0, dy), 'side', sway=(i % 2))
        out.append(with_legs(bd, [(rows, x, y + dy) for rows, x, y in legs]))
    return out


def run_front(body18, kind):
    """Front/back hop: a leg kicks out to the side on contact, both tuck when airborne."""
    hipL, hipR, hy = 3 + BODY_DX, 12 + BODY_DX, 17
    keys = [
        (0,  [(P.LEG_BACK, hipL - 1, hy - 1), (P.SIDE_LEG, hipR, hy)]),       # left leg steps out
        (-2, [(P.LEG_TUCK, hipL, hy), (P.LEG_TUCK, hipR, hy)]),               # airborne
        (-1, [(P.SIDE_LEG, hipL, hy), (P.SIDE_LEG, hipR, hy)]),               # pass
        (0,  [(P.SIDE_LEG, hipL, hy), (P.LEG_FWD, hipR, hy - 1)]),            # right leg steps out
        (-2, [(P.LEG_TUCK, hipL, hy), (P.LEG_TUCK, hipR, hy)]),               # airborne
        (-1, [(P.SIDE_LEG, hipL, hy), (P.SIDE_LEG, hipR, hy)]),               # pass
    ]
    out = []
    for i, (dy, legs) in enumerate(keys):
        bd = with_tail(shift(body18, 0, dy), kind, sway=(i % 2))
        out.append(with_legs(bd, [(rows, x, y + dy) for rows, x, y in legs]))
    return out


RUN_SIDE = run_side(P.SIDE_BODY)
RUN_FRONT = run_front(P.FRONT_BODY, 'front')
RUN_BACK = run_front(P.BACK_BODY, 'back')


# ---------------------------------------------------------------- dodge roll (9 frames)
def dodge(body_frames):
    """Wind-up crouch, four crisp 90-degree tumbles (ears + tail make the spin readable),
    a second half-turn while travelling, landing squash, back to idle."""
    idle = body_frames[0]
    ball = pad(X.BALL, W, H, 4, 4)
    balls = [rotate(ball, a) for a in (0, -90, -180, -270)]
    crouch = with_tail(X.CROUCH, 'side')
    land = with_tail(X.LAND, 'side', sway=1)
    return [crouch, balls[0], balls[1], balls[2], balls[3], shift(balls[0], 0, -1), balls[1], land, idle]


DODGE = dodge(IDLE_SIDE)
DODGE_FRONT = dodge(IDLE_FRONT)


# ---------------------------------------------------------------- death (8) / death_shot (6)
def death(idle):
    """Hit (mouth open, knocked back), wobble, knees buckle, tip over, flat on his side."""
    hit = with_tail(X.HIT, 'side')
    kneel = with_tail(X.KNEEL, 'side', sway=1)
    tip = with_tail(X.TIP, 'side', sway=1)
    lying = with_tail(X.LYING, 'lying')
    return [shift(hit, 1, 0), shift(hit, -1, 0), kneel, shift(kneel, 0, 1), tip,
            shift(lying, 0, -1), lying, lying]


DEATH = death(IDLE_SIDE[0])
DEATH_SHOT = [shift(with_tail(X.HIT, 'side'), 2, 0), shift(with_tail(X.HIT, 'side'), -2, 0),
              with_tail(X.KNEEL, 'side', sway=1), with_tail(X.TIP, 'side', sway=1),
              shift(with_tail(X.LYING, 'lying'), 0, -1), with_tail(X.LYING, 'lying')]


# ---------------------------------------------------------------- pitfall (5) / pitfall_down (5) / return (8)
def pitfall(idle):
    out = []
    for i, f in enumerate((0.9, 0.75, 0.6, 0.45, 0.3)):
        fr = scale_down(idle, f)
        fr = shift(fr, 0, i + 1)
        out.append(fr)
    return out


PITFALL = pitfall(IDLE_SIDE[0])
PITFALL_DOWN = pitfall(IDLE_FRONT[0])
PITFALL_RETURN = [shift(scale_down(IDLE_FRONT[0], f), 0, d) for f, d in
                  ((0.3, 5), (0.45, 4), (0.6, 3), (0.75, 2), (0.9, 1), (1.0, 0), (1.0, -1), (1.0, 0))]


# ---------------------------------------------------------------- item get (9) / chest recover (7) / select choose
PAWS = with_legs(with_tail(P.PAWS_UP, 'front'), FRONT_LEGS)
PAWS_BOB = with_legs(with_tail(shift(P.PAWS_UP, 0, -1), 'front', sway=1), FRONT_LEGS)
ITEM_GET = [IDLE_FRONT[0], squash(IDLE_FRONT[0], 0.9), PAWS_BOB, PAWS, PAWS, PAWS, PAWS, PAWS_BOB, PAWS]
CHEST_RECOVER = [IDLE_FRONT[0], PAWS_BOB, PAWS, PAWS, PAWS, PAWS_BOB, IDLE_FRONT[0]]
SELECT_CHOOSE = [IDLE_SIDE[0], squash(IDLE_SIDE[0], 0.9), PAWS_BOB, PAWS, PAWS, PAWS]


# ---------------------------------------------------------------- spin (spinfall 6, timefall 8, spit_out 6)
SPIN = [IDLE_FRONT[0], IDLE_SIDE[0], IDLE_BACK[0], flip_h(IDLE_SIDE[0]), IDLE_FRONT[0], IDLE_SIDE[0]]
TIMEFALL = [IDLE_FRONT[0], IDLE_SIDE[0], IDLE_BACK[0], flip_h(IDLE_SIDE[0]),
            squash(IDLE_FRONT[0], 0.9), squash(IDLE_SIDE[0], 0.9), squash(IDLE_BACK[0], 0.9), squash(flip_h(IDLE_SIDE[0]), 0.9)]
SPIT_OUT = [rotate(IDLE_FRONT[0], a) for a in (0, -90, -180, -270)] + [IDLE_FRONT[0], IDLE_FRONT[1]]
DOORWAY = RUN_BACK[:5]


# ---------------------------------------------------------------- ghost (recolour + float)
GHOST_MAP = {'W': 'c', 'w': 'c', 'x': 'c', 'B': 'C', 'b': 'D', 'd': 'D', 'L': 'c', 'l': 'c', 'P': 'c', 'p': 'C', 'G': 'c', 'g': 'D'}


def ghost(frames):
    return [shift(recolor(frames[i % len(frames)], GHOST_MAP), 0, d) for i, d in enumerate((0, -1, 0))]


GHOST_FRONT = ghost(IDLE_FRONT)
GHOST_BACK = ghost(IDLE_BACK)
GHOST_SIDE = ghost(IDLE_SIDE)
GHOST_SNEEZE = [recolor(f, GHOST_MAP) for f in (squash(IDLE_SIDE[0], 0.9), shift(IDLE_SIDE[0], 1, 0), shift(IDLE_SIDE[0], -1, 1), IDLE_SIDE[0])]


# ---------------------------------------------------------------- jetpack (2), pet (2), slide (1), tablekick
JET_SIDE = [shift(IDLE_SIDE[0], 0, -1), IDLE_SIDE[0]]
JET_FRONT = [shift(IDLE_FRONT[0], 0, -1), IDLE_FRONT[0]]
JET_BACK = [shift(IDLE_BACK[0], 0, -1), IDLE_BACK[0]]
PET = [IDLE_SIDE[0], squash(IDLE_SIDE[0], 0.92)]
SLIDE_SIDE = [squash(IDLE_SIDE[0], 0.6)]
SLIDE_UP = [squash(IDLE_BACK[0], 0.6)]
SLIDE_DOWN = [squash(IDLE_FRONT[0], 0.6)]
KICK_SIDE = [RUN_SIDE[0], RUN_SIDE[3], RUN_SIDE[0], IDLE_SIDE[0]]
KICK_FRONT = [RUN_FRONT[0], RUN_FRONT[2]]
KICK_BACK = [RUN_BACK[0], RUN_BACK[2]]


# ---------------------------------------------------------------- the full clip table
CLIPS = {
    'chest_recover': CHEST_RECOVER,
    'death': DEATH,
    'death_coop': None,
    'death_shot': DEATH_SHOT,
    'dodge': DODGE,
    'dodge_bw': DODGE,
    'dodge_left': DODGE_FRONT,
    'dodge_left_bw': DODGE_FRONT,
    'doorway': DOORWAY,
    'ghost_idle_back': GHOST_BACK,
    'ghost_idle_back_left': GHOST_BACK,
    'ghost_idle_back_right': GHOST_BACK,
    'ghost_idle_front': GHOST_FRONT,
    'ghost_idle_left': GHOST_SIDE,
    'ghost_idle_right': GHOST_SIDE,
    'ghost_sneeze_left': GHOST_SNEEZE,
    'ghost_sneeze_right': GHOST_SNEEZE,
    'idle': IDLE_SIDE,
    'idle_backward': IDLE_BACK,
    'idle_backward_hand': None,
    'idle_backward_twohands': None,
    'idle_bw': IDLE_SIDE,
    'idle_bw_twohands': None,
    'idle_forward': IDLE_FRONT,
    'idle_forward_hand': None,
    'idle_forward_twohands': None,
    'idle_hand': None,
    'idle_twohands': None,
    'item_get': ITEM_GET,
    'jetpack_down': JET_FRONT,
    'jetpack_down_hand': None,
    'jetpack_right': JET_SIDE,
    'jetpack_right_bw': JET_SIDE,
    'jetpack_right_hand': None,
    'jetpack_up': JET_BACK,
    'pet': PET,
    'pitfall': PITFALL,
    'pitfall_down': PITFALL_DOWN,
    'pitfall_return': PITFALL_RETURN,
    'run_down': RUN_FRONT,
    'run_down_hand': None,
    'run_down_twohands': None,
    'run_right': RUN_SIDE,
    'run_right_hand': None,
    'run_right_twohands': None,
    'run_right_bw': RUN_SIDE,
    'run_right_bw_twohands': None,
    'run_up': RUN_BACK,
    'run_up_hand': None,
    'run_up_twohands': None,
    'slide_right': SLIDE_SIDE,
    'slide_up': SLIDE_UP,
    'slide_down': SLIDE_DOWN,
    'spinfall': SPIN,
    'spit_out': SPIT_OUT,
    'tablekick_down': KICK_FRONT,
    'tablekick_down_hand': None,
    'tablekick_right': KICK_SIDE,
    'tablekick_right_hand': None,
    'tablekick_up': KICK_BACK,
    'timefall': TIMEFALL,
}

# --- v2 breach idles: loaf, groom, knock a bowl off a ledge
LOAF = [with_tail(X.LOAF, 'none'), with_tail(shift(X.LOAF, 0, 1), 'none')]
GROOM = [overlay(IDLE_SIDE[0], X.GROOM_PAW, 14, 8), overlay(IDLE_SIDE[1], X.GROOM_PAW, 14, 10),
         overlay(IDLE_SIDE[2], X.GROOM_PAW, 15, 9), overlay(IDLE_SIDE[3], X.GROOM_PAW, 14, 10)]


def knock():
    """Side idle next to a ledge with a bowl; a paw nudges it and it falls."""
    frames = []
    ledge_x, ledge_y = 12, 12
    for i, (bowl_dx, bowl_dy, paw) in enumerate(((0, 0, False), (0, 0, True), (2, 1, True), (4, 4, False), (5, 8, False), (5, 8, False))):
        base = pad(LEDGE_CANVAS, W, H)
        base = overlay(base, X.LEDGE, ledge_x, ledge_y)
        base = overlay(base, X.BOWL, ledge_x + 1 + bowl_dx, ledge_y - 6 + bowl_dy)
        f = overlay(base, IDLE_SIDE[i % 4])
        if paw:
            f = overlay(f, X.GROOM_PAW, 15, 11)
        frames.append(f)
    return frames


LEDGE_CANVAS = ['.' * W] * H
KNOCK = knock()

BREACH_IDLES = {
    'select_idle': IDLE_SIDE,
    'select_choose': SELECT_CHOOSE,
    'stretch': [squash(IDLE_SIDE[0], 0.9), squash(IDLE_SIDE[0], 0.85), squash(IDLE_SIDE[0], 0.9), IDLE_SIDE[0]],
    'loaf': LOAF,
    'groom': GROOM,
    'knock': KNOCK,
}

# --- v2.1 "_hand" / "_twohands" variants: arm(s) extended toward the gun
def armed(frames, kind, two=False):
    out = []
    for f in frames:
        if kind == 'side':
            g = overlay(f, P.ARM_SIDE, 19, 11)
        else:  # front
            g = overlay(f, P.ARM_FRONT_R, 19, 12)
            if two:
                g = overlay(g, flip_h(P.ARM_FRONT_R), 1, 12)
        out.append(g)
    return out


for _clip, _src, _kind in (('idle_hand', IDLE_SIDE, 'side'), ('idle_twohands', IDLE_SIDE, 'side'),
                           ('idle_bw_twohands', IDLE_SIDE, 'side'),
                           ('idle_forward_hand', IDLE_FRONT, 'front'), ('idle_forward_twohands', IDLE_FRONT, 'front'),
                           ('run_right_hand', RUN_SIDE, 'side'), ('run_right_twohands', RUN_SIDE, 'side'),
                           ('run_right_bw_twohands', RUN_SIDE, 'side'),
                           ('run_down_hand', RUN_FRONT, 'front'), ('run_down_twohands', RUN_FRONT, 'front'),
                           ('jetpack_right_hand', JET_SIDE, 'side'), ('jetpack_down_hand', JET_FRONT, 'front'),
                           ('tablekick_right_hand', KICK_SIDE, 'side'), ('tablekick_down_hand', KICK_FRONT, 'front')):
    CLIPS[_clip] = armed(_src, _kind, two=_clip.endswith('twohands'))
# back-facing hand variants keep the placeholder fallback (arms are hidden behind the body).

# --- v2 co-op death: ghost Pluto hovering over the body
_ghost_small = scale_down(GHOST_FRONT[0], 0.6, anchor='center')
DEATH_COOP = [overlay(with_tail(X.LYING, 'lying'), shift(_ghost_small, 8, -8 + d), 0, 0) for d in (0, -1, 0, -1)]
CLIPS['death_coop'] = DEATH_COOP

# --- shading pass (rim shadow / highlight) on every drawn body frame; ghosts stay flat and translucent
for _k, _v in list(CLIPS.items()):
    if _v and not _k.startswith('ghost'):
        CLIPS[_k] = [shade(f) for f in _v]
for _k, _v in list(BREACH_IDLES.items()):
    BREACH_IDLES[_k] = [shade(f) for f in _v]

# --- v2 alt skin: Wet Pluto (fresh out of the bath): flattened dark fur, blue-grey white, grumpy eyes
WET_MAP = {'B': 'J', 'b': 'j', 'L': 'J', 'l': 'J', 'd': 'j', 'W': 'U', 'w': 'u', 'x': 'u', 'K': 'U'}


def wet(frames):
    return [recolor(f, WET_MAP) for f in frames]


ALT_CLIPS = {k: (wet(v) if v else None) for k, v in CLIPS.items()}
ALT_BREACH_IDLES = {k: wet(v) for k, v in BREACH_IDLES.items()}
ALT_HAND = recolor(P.HAND, WET_MAP)

for k, v in list(CLIPS.items()) + list(BREACH_IDLES.items()):
    if v:
        for f in v:
            check_rect(f)
            assert len(f) == H and len(f[0]) == W, (k, len(f), len(f[0]))
