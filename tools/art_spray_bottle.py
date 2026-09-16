"""2.19.0 Spray Bottle. Rows copied from approved spray_bottle/sheet_c2.png.

26x20 canvas; the concept's drawn paw is omitted (the runtime supplies Pluto's
paw). Pale-blue glass uses existing 1/F/f and W highlights with hard alpha:
translucency is suggested by the water line and dip tube, never partial alpha.
The pink paw label stays on the white sprayer. Light comes from top-left.
"""
from pixel import check_rect as R, pad, overlay, flip_h

W, H = 26, 20
HEAD = R([
    '....oooooooo..',
    '..ooWWWWWWWWo.',
    '.oWWWWPpPWWWxo',
    'oWWWWWpppWWWxo',
    '.ooWWWWWwoooo.',
    '...owwwoo.oxo.',
    '....ooo....oxo',
])
PRESSED = R([
    '....oooooooo..',
    '..ooWWWWWWWWo.',
    '.oWWWWPpPWWWxo',
    'oWWWWWpppWWWxo',
    '.ooWWWWWwoooo.',
    '...owwwoooxo..',
    '....ooo..oxo..',
])
BODY = R([
    '....oooo...',
    '...oSxSxo..',
    '...o1F1fo..',
    '..o1W1F1fo.',
    '.o1W11F11fo',
    '.o1WWWWWWfo',
    '.oFWFFfFFfo',
    '.oFWFFfFFfo',
    '.oFFWfFFFfo',
    '.oFFFFFFffo',
    '..oooooooo.',
])
LOW_BODY = R([
    '....oooo...',
    '...oSxSxo..',
    '...o1F1fo..',
    '..o1W1F1fo.',
    '.o1W11F11fo',
    '.o1W11F11fo',
    '.o1W11F11fo',
    '.o1W11f11fo',
    '.oFWWWWFFfo',
    '.oFFFFFFffo',
    '..oooooooo.',
])
OPEN_BODY = R([
    '....oooo...',
    '...o1F1fo..',
    '...oF1Ffo..',
    '..o1W1F1fo.',
    '.o1W11F11fo',
    '.o1W11F11fo',
    '.o1W11F11fo',
    '.o1WWWWWWfo',
    '.oFFWfFFFfo',
    '.oFFFFFFffo',
    '..oooooooo.',
])


def bottle(head=HEAD, body=BODY, head_y=2):
    # The approved sheet aims to the right.  Only the sprayer is mirrored: the
    # bottle keeps its authored top-left highlight and left-side glass shine.
    return overlay(pad(body, W, H, 6, 8), flip_h(head), 5, head_y)


IDLE = bottle()
# The two firing keys carry the c2 action on the gun frames themselves.  The
# first is a connected nozzle cone; the second is the departing cloud and
# droplets.  Projectile sprites remain separate for runtime travel/impact.
FIRE_CONE = R([
    '......o',
    '....o1o',
    '..o1W1o',
    'o1WWW1o',
    '..o1W1o',
    '....o1o',
    '......o',
])
FIRE_PUFF = R([
    '.oooo..',
    'o1WW1o.',
    'oWWWW1o',
    '.o1W1o.',
    '...o...',
    '.....o.',
    '....o1o',
    '.....o.',
])
FIRE = [overlay(bottle(PRESSED), FIRE_CONE, 19, 1),
        overlay(bottle(HEAD, LOW_BODY), FIRE_PUFF, 19, 0)]
# Unscrew: detached head lifted; refill: droplets enter the exposed neck;
# screw: sprayer seated one pixel high, settling back onto idle.
REFILL = overlay(pad(OPEN_BODY, W, H, 6, 8), R([
    '..o....',
    '.o1o...',
    '.oFo.o.',
    '..o.o1o',
    '.....o.',
]), 8, 2)
RELOAD = [bottle(HEAD, LOW_BODY, 0), REFILL, bottle(HEAD, BODY, 1)]
CLIPS = {'idle': [IDLE], 'fire': FIRE, 'reload': RELOAD}
MIST = R([
    '...ooo....',
    '..o1W1oo..',
    '.o1WWWW1o.',
    'o1WW1WWW1o',
    'oWWW1WW11o',
    '.o1WWWW1o.',
    '..o1W1oo..',
    '...ooo....',
])
DROP = R([
    '..o...',
    '.o1o..',
    '.oWFo.',
    'o1FFfo',
    'oFFFfo',
    '.oooo.',
])
SPLASH = R([
    '.....o......',
    '....o1o.....',
    '.oo.oWo..oo.',
    '.o1ooWooo1o.',
    '..o1W1W11o..',
    '.o1WWWW1F1o.',
    '..oFFFFFFo..',
    '...oooooo...',
])
PROJECTILES = {'pluto_spray_mist_001': MIST, 'pluto_water_drop_001': DROP,
               'pluto_water_splash_001': SPLASH}
# The gun has 5 empty columns at the right; removing just that whitespace
# keeps the exact 1x drawing on the required 24x32 inventory page.
PAGE = pad([r[:24] for r in IDLE], 24, 32, 0, 6)
