"""Derive every Alexandria CharacterAPI animation clip for Pluto from the key poses.

Canvas: 24 x 26. The 18 x 22 pose sits at x=3 (centred, so the game's uv flip does not move the
body) and y=4 at rest; the 4 rows above are headroom for the vanilla 4-px run hop. Frames are
anchored bottom-left by Alexandria, so the feet fill row (GROUND = 24) must be identical on every
grounded frame; airborne frames move the pixels UP inside the canvas.

Returns {clip_folder: [rows, ...]}. Folders whose value is None get a cc_sprite_placeholder.png
(Alexandria then falls back to the base clip). FRAME_DY records the body offset of each frame of
the derived clips so the free-hand stubs can follow the body.
"""
from pixel import shift, overlay, flip_h, recolor, squash, rotate, pad, check_rect, scale_down
import poses as P
import poses_extra as X

W, H = 24, P.H + 4
BODY_DX, BODY_DY = 3, 4
GROUND = H - 2                  # feet fill row (row H-1 is the transparent outline margin)
TAIL_Y = 8                      # tail top, pose-relative (base tucks in behind the rump)
EMPTY = ['.' * W] * H
FRAME_DY = {}                   # clip -> [body dy per frame]


# ---------------------------------------------------------------- composition helpers
def with_legs(body, legs):
    """legs: list of (rows, x, y) placed on the canvas (canvas coords)."""
    out = body
    for rows, x, y in legs:
        out = overlay(out, rows, x, y)
    return out


def with_tail(pose, kind='side', tail='A', dy=0, tail_dy=0, dx=0):
    """Place an 18x22 pose on the canvas at (BODY_DX+dx, BODY_DY+dy) and draw the ringed tail BEHIND it.
    kind: side/front (tail curls up on the left), back (on the right), lying (flat on the floor),
    none. tail: 'A' / 'B' (sway variants). tail_dy lets the tail lag the body; dx knocks the body back."""
    body = pad(pose, W, H, BODY_DX + dx, BODY_DY + dy)
    if kind == 'none':
        return body
    if kind == 'lying':
        canvas = pad(X.TAIL_FLAT, W, H, 0, BODY_DY + 19 + tail_dy)   # on the floor, left of the body
        return overlay(canvas, body)
    t = X.TAIL_B if tail == 'B' else X.TAIL_A
    ty = BODY_DY + TAIL_Y + tail_dy
    if kind == 'back':
        canvas = pad(flip_h(t), W, H, W - 8, ty)
    else:
        canvas = pad(t, W, H, 0, ty)
    return overlay(canvas, body)


def record(clip, dys):
    FRAME_DY[clip] = list(dys)


# ---------------------------------------------------------------- idle (breathing: 4 frames @ 6 fps)
LEG_Y = BODY_DY + P.HEAD_ROWS + P.BODY_ROWS      # canvas row where the legs start at rest (23)
SIDE_LEGS = [(P.SIDE_LEG, 5 + BODY_DX, LEG_Y), (P.SIDE_LEG, 12 + BODY_DX, LEG_Y)]
FRONT_LEGS = [(P.SIDE_LEG, 3 + BODY_DX, LEG_Y), (P.SIDE_LEG, 12 + BODY_DX, LEG_Y)]
BACK_LEGS = FRONT_LEGS


def breathe(head, body_part, kind, legs, flick):
    """4 frames: rest, ear flick, squash (the head sinks one row into the shoulders while belly and
    feet stay put), rest with the tail catching up. No two frames identical, feet never move."""
    rest = P.stack(head, body_part, P.EMPTY_LEGS)
    flicked = P.stack(P.ear_flick(head, *flick), body_part, P.EMPTY_LEGS)
    low = P.squashed(head, body_part, P.EMPTY_LEGS, 1)
    frames = [(rest, 'A', 0), (flicked, 'A', 0), (low, 'B', 0), (rest, 'B', 1)]
    return [with_legs(with_tail(pose, kind, tail=t, tail_dy=tdy), legs) for pose, t, tdy in frames]


IDLE_SIDE = breathe(P.HEAD_SIDE, P.BODY_SIDE, 'side', SIDE_LEGS, (12, 15))
IDLE_FRONT = breathe(P.HEAD_FRONT, P.BODY_FRONT, 'front', FRONT_LEGS, (11, 14))
IDLE_BACK = breathe(P.HEAD_BACK, P.BODY_BACK, 'back', BACK_LEGS, (11, 14))
IDLE_BW = breathe(P.HEAD_BW, P.BODY_BW, 'side', SIDE_LEGS, (12, 15))
for _c in ('idle', 'idle_forward', 'idle_backward', 'idle_bw'):
    record(_c, (0, 0, 0, 0))


# ---------------------------------------------------------------- run cycles (6 frames @ 9 fps, vanilla hop)
def lean(pose, dx=1, upto=P.HEAD_ROWS - 1):
    """Lean the head forward by dx pixels (rows 0..upto) on the 24-wide canvas (never truncates)."""
    return [(('.' * dx) + r) if i <= upto else r for i, r in enumerate(pose)]


RUN_DY = (0, -4, -3, 0, -4, -3)          # contact, airborne (4 px up), pass, and again for the other leg
RUN_TAIL_DY = (-1, -2, -4, -1, -2, -4)   # tail lags the body by one frame


def run_pose(head, body_part, i):
    """Pose for run frame i: airborne frames get the head lagging one row into the shoulders and the
    ear tips blown back; the head leans forward one pixel on every frame."""
    airborne = RUN_DY[i] == -4
    h = P.ears_back(head) if airborne else head
    pose = P.squashed(h, body_part, P.EMPTY_LEGS, 1 if airborne else 0)
    return lean(pose)


def run_side(head, body_part):
    """Vanilla hop: contact (feet on the ground, legs straight under the hips, 1 px wider than idle)
    -> airborne (+4, legs tucked) -> pass (+3, legs gathered under the belly), then a gathered
    contact. Legs stay vertical: diagonal legs read as the splits at 1x."""
    hipB, hipF = 5 + BODY_DX, 12 + BODY_DX
    keys = [
        [(P.SIDE_LEG, hipB - 1, LEG_Y), (P.SIDE_LEG, hipF + 1, LEG_Y)],            # contact, stride
        [(P.LEG_TUCK, hipB, LEG_Y), (P.LEG_TUCK, hipF, LEG_Y)],                    # airborne
        [(P.SIDE_LEG_LONG, hipB + 1, LEG_Y - 1), (P.SIDE_LEG_LONG, hipF - 1, LEG_Y - 1)],  # pass, gathered
        [(P.SIDE_LEG, hipB + 1, LEG_Y), (P.SIDE_LEG, hipF - 1, LEG_Y)],            # contact, gathered
        [(P.LEG_TUCK, hipB, LEG_Y), (P.LEG_TUCK, hipF, LEG_Y)],                    # airborne
        [(P.SIDE_LEG_LONG, hipB - 1, LEG_Y - 1), (P.SIDE_LEG_LONG, hipF + 1, LEG_Y - 1)],  # pass, reaching
    ]
    out = []
    for i, legs in enumerate(keys):
        dy = RUN_DY[i]
        bd = with_tail(run_pose(head, body_part, i), 'side', tail='B' if i % 3 == 2 else 'A', dy=dy, tail_dy=RUN_TAIL_DY[i])
        out.append(with_legs(bd, [(rows, x, y + dy) for rows, x, y in legs]))
    return out


def run_front(head, body_part, kind):
    """Front/back hop: one foot plants under its hip while the other lifts, both tuck when airborne.
    Feet never leave the hip columns (no sideways splay)."""
    hipL, hipR = 3 + BODY_DX, 12 + BODY_DX
    keys = [
        [(P.SIDE_LEG, hipL, LEG_Y), (P.LEG_TUCK, hipR, LEG_Y)],                    # left foot plants, right lifts
        [(P.LEG_TUCK, hipL, LEG_Y), (P.LEG_TUCK, hipR, LEG_Y)],                    # airborne
        [(P.SIDE_LEG_LONG, hipL, LEG_Y - 1), (P.SIDE_LEG_LONG, hipR, LEG_Y - 1)],  # pass
        [(P.LEG_TUCK, hipL, LEG_Y), (P.SIDE_LEG, hipR, LEG_Y)],                    # right foot plants, left lifts
        [(P.LEG_TUCK, hipL, LEG_Y), (P.LEG_TUCK, hipR, LEG_Y)],                    # airborne
        [(P.SIDE_LEG_LONG, hipL, LEG_Y - 1), (P.SIDE_LEG_LONG, hipR, LEG_Y - 1)],  # pass
    ]
    out = []
    for i, legs in enumerate(keys):
        dy = RUN_DY[i]
        airborne = dy == -4
        pose = P.squashed(head, body_part, P.EMPTY_LEGS, 1 if airborne else 0)
        bd = with_tail(pose, kind, tail='B' if i % 3 == 2 else 'A', dy=dy, tail_dy=RUN_TAIL_DY[i])
        out.append(with_legs(bd, [(rows, x, y + dy) for rows, x, y in legs]))
    return out


RUN_SIDE = run_side(P.HEAD_SIDE, P.BODY_SIDE)
RUN_BW = run_side(P.HEAD_BW, P.BODY_BW)
RUN_FRONT = run_front(P.HEAD_FRONT, P.BODY_FRONT, 'front')
RUN_BACK = run_front(P.HEAD_BACK, P.BODY_BACK, 'back')
for _c in ('run_right', 'run_right_bw', 'run_down', 'run_up'):
    record(_c, RUN_DY)


# ---------------------------------------------------------------- dodge rolls (9 frames each)
# PlayerController picks the clip from the roll direction: |x| >= 0.1 -> dodge_left (dodge_left_bw
# when rolling up), else dodge (down) / dodge_bw (up). Rolling left forces the sprite flip, so the
# side rolls face right like the run. Vanilla shape: wind-up, dive, somersault with the body still
# readable in every frame, stand up. Alexandria flags frames 0-4 invulnerable/airborne.
def fill_bottom(rows):
    return max(y for y, r in enumerate(rows) if any(ch not in '.o' for ch in r))


def seat(part, dy, dx=BODY_DX):
    """Place a part so its lowest fill row sits dy px above the ground."""
    return pad(part, W, H, dx, GROUND - fill_bottom(part) - dy)


def tumble(tuck, angle, dy):
    """Rotate the square 16x16 tuck BEFORE placing it, so the tumble never wobbles or slides."""
    return seat(rotate(tuck, angle), dy, BODY_DX + 1)


def dodge_side(crouch, head, body_part, tuck, land, idle):
    """Crouch, forward dive (paws out, tail streaming), four 90-degree somersault frames rotating
    forward (clockwise), curled touch-down, landing squash, idle."""
    hipB, hipF = 5 + BODY_DX, 12 + BODY_DX
    dive = with_tail(lean(P.squashed(P.ears_back(head), body_part, P.EMPTY_LEGS, 1), 2), 'side', tail='B', dy=-3, tail_dy=-4)
    dive = with_legs(dive, [(P.LEG_TUCK, hipB - 2, LEG_Y - 3), (P.LEG_TUCK, hipF + 2, LEG_Y - 4)])
    return [crouch, dive, tumble(tuck, 0, 4), tumble(tuck, -90, 5), tumble(tuck, -180, 4), tumble(tuck, -270, 2),
            tumble(tuck, 0, 0), land, idle]


def dodge_vertical(crouch, low, first, second, land, idle):
    """Down/up roll seen along the roll: crouch, low, the head goes over (first part), upside down
    (second part), coming back round low, landing squash, idle."""
    return [crouch, low, seat(first, 3), seat(second, 5), seat(second, 3), seat(first, 1), land, idle[2], idle[0]]


DODGE_SIDE = dodge_side(with_tail(X.CROUCH, 'side'), P.HEAD_SIDE, P.BODY_SIDE, X.TUCK_SIDE,
                        with_tail(X.LAND, 'side', tail='B'), IDLE_SIDE[0])
DODGE_SIDE_BW = dodge_side(with_legs(with_tail(P.squashed(P.HEAD_BW, P.BODY_BW, P.EMPTY_LEGS, 3), 'side'), SIDE_LEGS),
                           P.HEAD_BW, P.BODY_BW, X.TUCK_SIDE_BW,
                           with_legs(with_tail(P.squashed(P.HEAD_BW, P.BODY_BW, P.EMPTY_LEGS, 2), 'side', tail='B'), SIDE_LEGS),
                           IDLE_BW[0])
DODGE_DOWN = dodge_vertical(with_legs(with_tail(P.squashed(P.HEAD_FRONT, P.BODY_FRONT, P.EMPTY_LEGS, 3), 'front'), FRONT_LEGS),
                            squash(IDLE_FRONT[0], 0.8), X.CROWN, X.BACK_UP,
                            with_legs(with_tail(P.squashed(P.HEAD_FRONT, P.BODY_FRONT, P.EMPTY_LEGS, 2), 'front', tail='B'), FRONT_LEGS),
                            IDLE_FRONT)
DODGE_UP = dodge_vertical(with_legs(with_tail(P.squashed(P.HEAD_BACK, P.BODY_BACK, P.EMPTY_LEGS, 3), 'back'), BACK_LEGS),
                          squash(IDLE_BACK[0], 0.8), X.BELLY_UP, X.BACK_UP,
                          with_legs(with_tail(P.squashed(P.HEAD_BACK, P.BODY_BACK, P.EMPTY_LEGS, 2), 'back', tail='B'), BACK_LEGS),
                          IDLE_BACK)


# ---------------------------------------------------------------- death (8) / death_shot (6)
def death():
    """Hit (mouth open, knocked back), wobble, knees buckle, tip over, flat on his side."""
    kneel = with_tail(X.KNEEL, 'side', tail='B')
    kneel_low = with_tail(X.KNEEL_LOW, 'side', tail='B', tail_dy=1)
    tip = with_tail(X.TIP, 'side', tail='B', tail_dy=2)
    lying = with_tail(X.LYING, 'lying')
    return [with_tail(X.HIT, 'side', dx=1), with_tail(X.HIT, 'side', dx=-1), kneel, kneel_low, tip,
            with_tail(X.LYING, 'lying', tail_dy=-2), with_tail(X.LYING, 'lying', tail_dy=-1), lying]


DEATH = death()
DEATH_SHOT = [with_tail(X.HIT, 'side', dx=2), with_tail(X.HIT, 'side', dx=-2),
              with_tail(X.KNEEL, 'side', tail='B'), with_tail(X.TIP, 'side', tail='B', tail_dy=2),
              shift(with_tail(X.LYING, 'lying'), 0, -1), with_tail(X.LYING, 'lying')]


# ---------------------------------------------------------------- pitfall (5) / pitfall_down (5) / return (8)
def cross(rows):
    cw = len(rows[0])
    return pad(rows, W, H, BODY_DX + 9 - cw // 2, GROUND - len(rows) + 1)


CROSS5, CROSS3 = cross(X.CROSS5), cross(X.CROSS3)


def pitfall(crouch, idle):
    """Vanilla shape: crouch at the edge, shrink toward the hole twice, then two single-colour blips."""
    return [crouch, shift(scale_down(idle, 0.7), 0, 2, allow_drop=True),
            shift(scale_down(idle, 0.45), 0, 5, allow_drop=True), CROSS5, CROSS3]


PITFALL = pitfall(with_tail(X.CROUCH, 'side'), IDLE_SIDE[0])
PITFALL_DOWN = pitfall(squash(IDLE_FRONT[0], 0.85), IDLE_FRONT[0])
PITFALL_RETURN = [CROSS3, CROSS5, shift(scale_down(IDLE_FRONT[0], 0.45), 0, 5, allow_drop=True),
                  shift(scale_down(IDLE_FRONT[0], 0.7), 0, 2, allow_drop=True), IDLE_FRONT[2],
                  with_legs(with_tail(P.FRONT_BODY, 'front', dy=-1), [(P.SIDE_LEG_LONG, 3 + BODY_DX, LEG_Y - 1), (P.SIDE_LEG_LONG, 12 + BODY_DX, LEG_Y - 1)]),
                  IDLE_FRONT[0], IDLE_FRONT[3]]


# ---------------------------------------------------------------- item get (9) / chest recover (7) / select choose
PAWS = with_legs(with_tail(P.PAWS_UP, 'front'), FRONT_LEGS)
PAWS_BOB = with_legs(with_tail(P.PAWS_UP, 'front', tail='B', dy=-1), FRONT_LEGS)
ITEM_GET = [IDLE_FRONT[0], squash(IDLE_FRONT[0], 0.9), PAWS_BOB, PAWS, PAWS, PAWS, PAWS, PAWS_BOB, PAWS]
CHEST_RECOVER = [IDLE_FRONT[0], PAWS_BOB, PAWS, PAWS, PAWS, PAWS_BOB, IDLE_FRONT[0]]
SELECT_CHOOSE = [IDLE_SIDE[0], squash(IDLE_SIDE[0], 0.9), PAWS_BOB, PAWS, PAWS, PAWS]


# ---------------------------------------------------------------- spin (spinfall 6, timefall 8, spit_out 6)
SPIN = [IDLE_FRONT[0], IDLE_SIDE[0], IDLE_BACK[0], flip_h(IDLE_SIDE[0]), IDLE_FRONT[0], IDLE_SIDE[0]]
TIMEFALL = [IDLE_FRONT[0], IDLE_SIDE[0], IDLE_BACK[0], flip_h(IDLE_SIDE[0]),
            squash(IDLE_FRONT[0], 0.9), squash(IDLE_SIDE[0], 0.9), squash(IDLE_BACK[0], 0.9), squash(flip_h(IDLE_SIDE[0]), 0.9)]


def spin_out(frame):
    """Tumble for spit_out: rotate the frame's content about its own centre, then re-seat it."""
    out = []
    for a in (0, -90, -180, -270):
        r = rotate(frame, a)
        out.append(r)
    return out


SPIT_OUT = spin_out(IDLE_FRONT[0]) + [IDLE_FRONT[0], IDLE_FRONT[2]]
DOORWAY = RUN_BACK[:5]


# ---------------------------------------------------------------- ghost (recolour + float)
GHOST_MAP = {'W': 'c', 'w': 'c', 'x': 'c', 'B': 'C', 'b': 'D', 'd': 'D', '9': 'D', 'L': 'c', 'l': 'c',
             'P': 'c', 'p': 'C', 'G': 'c', 'g': 'D'}


def ghost(frames):
    return [shift(recolor(frames[i % len(frames)], GHOST_MAP), 0, d) for i, d in enumerate((0, -1, 0))]


GHOST_FRONT = ghost(IDLE_FRONT)
GHOST_BACK = ghost(IDLE_BACK)
GHOST_SIDE = ghost(IDLE_SIDE)
GHOST_SNEEZE = [recolor(f, GHOST_MAP) for f in (squash(IDLE_SIDE[0], 0.9), with_legs(with_tail(P.SIDE_BODY, 'side', dx=1), SIDE_LEGS),
                                                with_legs(with_tail(P.SIDE_BODY, 'side', dx=-1, dy=1), [(r, x - 1, y) for r, x, y in SIDE_LEGS]), IDLE_SIDE[0])]


# ---------------------------------------------------------------- jetpack (2), pet (2), slide (1), tablekick
JET_SIDE = [shift(IDLE_SIDE[0], 0, -1), IDLE_SIDE[0]]
JET_BW = [shift(IDLE_BW[0], 0, -1), IDLE_BW[0]]
JET_FRONT = [shift(IDLE_FRONT[0], 0, -1), IDLE_FRONT[0]]
JET_BACK = [shift(IDLE_BACK[0], 0, -1), IDLE_BACK[0]]
for _c in ('jetpack_right', 'jetpack_right_bw', 'jetpack_down', 'jetpack_up'):
    record(_c, (-1, 0))
PET = [IDLE_SIDE[0], squash(IDLE_SIDE[0], 0.92)]
SLIDE_SIDE = [with_tail(X.SLIDE, 'side')]
SLIDE_UP = [squash(IDLE_BACK[0], 0.6)]
SLIDE_DOWN = [squash(IDLE_FRONT[0], 0.6)]
KICK_SIDE = [RUN_SIDE[0], RUN_SIDE[3], RUN_SIDE[0], IDLE_SIDE[0]]
KICK_FRONT = [RUN_FRONT[0], RUN_FRONT[2]]
KICK_BACK = [RUN_BACK[0], RUN_BACK[2]]
record('tablekick_right', (0, 0, 0, 0))
record('tablekick_down', (0, -3))


# ---------------------------------------------------------------- the full clip table
CLIPS = {
    'chest_recover': CHEST_RECOVER,
    'death': DEATH,
    'death_coop': None,
    'death_shot': DEATH_SHOT,
    'dodge': DODGE_DOWN,
    'dodge_bw': DODGE_UP,
    'dodge_left': DODGE_SIDE,
    'dodge_left_bw': DODGE_SIDE_BW,
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
    'idle_bw': IDLE_BW,
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
    'jetpack_right_bw': JET_BW,
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
    'run_right_bw': RUN_BW,
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

# --- breach idles: loaf, groom, knock a bowl off a ledge
LOAF = [with_tail(X.LOAF, 'none'), with_tail(X.LOAF_DOWN, 'none')]
GROOM = [overlay(IDLE_SIDE[0], X.GROOM_PAW, 14, 13), overlay(IDLE_SIDE[1], X.GROOM_PAW, 14, 15),
         overlay(IDLE_SIDE[2], X.GROOM_PAW, 15, 14), overlay(IDLE_SIDE[3], X.GROOM_PAW, 14, 15)]


def knock():
    """Side idle next to a ledge with a bowl; a paw nudges it and it falls."""
    frames = []
    ledge_x, ledge_y = 10, 17
    for i, (bowl_dx, bowl_dy, paw) in enumerate(((0, 0, False), (0, 0, True), (1, 1, True), (2, 4, False), (3, 7, False), (3, 7, False))):
        base = overlay(EMPTY, X.LEDGE, ledge_x, ledge_y)
        base = overlay(base, X.BOWL, ledge_x + 1 + bowl_dx, ledge_y - 6 + bowl_dy)
        f = overlay(base, IDLE_SIDE[i % 4])
        if paw:
            f = overlay(f, X.GROOM_PAW, 15, 16)
        frames.append(f)
    return frames


KNOCK = knock()

BREACH_IDLES = {
    'select_idle': IDLE_SIDE,
    'select_choose': SELECT_CHOOSE,
    'stretch': [squash(IDLE_SIDE[0], 0.9), squash(IDLE_SIDE[0], 0.85), squash(IDLE_SIDE[0], 0.9), IDLE_SIDE[0]],
    'loaf': LOAF,
    'groom': GROOM,
    'knock': KNOCK,
}


# --- "_hand" / "_twohands" variants. Vanilla semantics (PlayerController.GetBaseAnimationName):
#   no suffix  = two-handed gun, both hands are the game's hand sprites -> body draws no paw
#   _hand      = one-handed gun (the kibble sack) -> body draws its FREE paw on the chest
#   _twohands  = no gun -> body draws both paws
PAW_SIDE = (12, 14)                 # pose coords of the free paw on the chest (side view)
PAW_FRONT_R, PAW_FRONT_L = (11, 14), (3, 14)


def pawed(clip, frames, kind, two=False):
    dys = FRAME_DY.get(clip.replace('_twohands', '').replace('_hand', ''), [0] * len(frames))
    out = []
    for f, dy in zip(frames, dys):
        spots = [PAW_SIDE] if kind == 'side' else ([PAW_FRONT_R, PAW_FRONT_L] if two else [PAW_FRONT_R])
        g = f
        for (px, py) in spots:
            g = overlay(g, P.PAW, BODY_DX + px, BODY_DY + py + dy)
        out.append(g)
    return out


for _clip, _src, _kind in (('idle_hand', IDLE_SIDE, 'side'), ('idle_twohands', IDLE_SIDE, 'side'),
                           ('idle_bw_twohands', IDLE_BW, 'side'),
                           ('idle_forward_hand', IDLE_FRONT, 'front'), ('idle_forward_twohands', IDLE_FRONT, 'front'),
                           ('run_right_hand', RUN_SIDE, 'side'), ('run_right_twohands', RUN_SIDE, 'side'),
                           ('run_right_bw_twohands', RUN_BW, 'side'),
                           ('run_down_hand', RUN_FRONT, 'front'), ('run_down_twohands', RUN_FRONT, 'front'),
                           ('jetpack_right_hand', JET_SIDE, 'side'), ('jetpack_down_hand', JET_FRONT, 'front'),
                           ('tablekick_right_hand', KICK_SIDE, 'side'), ('tablekick_down_hand', KICK_FRONT, 'front')):
    CLIPS[_clip] = pawed(_clip, _src, _kind, two=_clip.endswith('twohands'))
# back-facing hand variants keep the placeholder fallback (arms are hidden behind the body).

# --- co-op death: ghost Pluto hovering over the body
_ghost_small = scale_down(GHOST_FRONT[0], 0.6, anchor='bottom')
_gtop = next(y for y, r in enumerate(_ghost_small) if any(ch != '.' for ch in r))
DEATH_COOP = [overlay(with_tail(X.LYING, 'lying'), shift(_ghost_small, 6, 2 - _gtop + d, allow_drop=True), 0, 0) for d in (0, -1, 0, -1)]
CLIPS['death_coop'] = DEATH_COOP

# --- alt skin: Wet Pluto (fresh out of the bath): flattened dark fur, blue-grey white, grumpy eyes
WET_MAP = {'B': 'J', 'b': 'j', 'L': 'J', 'l': 'J', 'd': 'j', '9': 'j', 'W': 'U', 'w': 'u', 'x': 'u', 'K': 'U'}


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
