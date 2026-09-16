"""2.19.0 Feather Teaser from approved feather_teaser/sheet_c2.png.

40x20 gun, no baked paw. Pink grip, warm wooden wand, white string, silver
bell, pink/gold/blue feather fan. Existing palette, hard alpha, top-left light.
"""
from pixel import check_rect as R, pad, overlay

W, H = 40, 20
WAND = R([
    '...........................oooo...',
    '.....................ooooooLLLLo..',
    '...............ooooooLLLLLLBooo...',
    '..oooooooooooooLLLLLLBoooooo......',
    '.oqqqqqqqqPpLLLBoooooo............',
    'oqqPPPPPPPpooooo..................',
    'oPPPPPPPPpo.......................',
    '.ooooooooo........................',
])
FAN = R([
    '...ooo....',
    '..oWSso...',
    '..oSsoo...',
    '..oHYoFo..',
    '.oPHYoFFo.',
    '.oHpYyFFo.',
    'oPHpYyFFfo',
    'oHooYyFFfo',
    '.o.oYyoffo',
    '....oo.oo.',
])
STRING = R(['oWo', 'oWo', 'oWo'])
EMPTY = pad(WAND, W, H, 1, 3)
IDLE = overlay(overlay(EMPTY, STRING, 31, 5), FAN, 28, 8)
CHARGE_WAND = R([
    '........................ooooooo...',
    '....................ooooLLLLLLLo..',
    '.................oooLLLLBoooooo...',
    '..............oooLLLBoooo.........',
    '..ooooooooooooLLBoooo.............',
    '.oqqqqqqqqPpLLooo.................',
    'oqqPPPPPPPpooo....................',
    'oPPPPPPPPpo.......................',
    '.ooooooooo........................',
])
CHARGE = overlay(overlay(pad(CHARGE_WAND, W, H, 1, 1), STRING, 31, 4), FAN, 28, 7)
CAST_HANDLE = R([
    '...ooooooo...',
    '.ooqqqqqqqoo.',
    'oqqPPPPPPppPo',
    'oPPPPPPPPPppo',
    'oPPPPPPPPPppo',
    '.oPPPPPPPppo.',
    '..ooooooooo..',
])
CAST_SHAFT_STRING = R([
    'ooooooooooooooooooooo',
    'oLLLLLLLLLLLLLWWWWWWo',
    'ooooooooooooooooooooo',
])
CAST_BELL = R([
    '.ooo.',
    'oSSSo',
    'oSsSo',
    'oSSSo',
    '.ooo.',
])
CAST_FEATHERS = R([
    '.oHHo.',
    'oHhHYo',
    'oHYFfo',
    'oYYFfo',
    '.oFFfo',
    '..oooo',
])
# The c2 fire key is a new, straight horizontal cast: grip -> rigid shaft ->
# white string -> bell -> feather bunch.  Every part overlaps its neighbour,
# so the lure reads as one continuous extended toy at native size.
FIRE = pad(CAST_HANDLE, W, H, 1, 7)
FIRE = overlay(FIRE, CAST_SHAFT_STRING, 11, 9)
FIRE = overlay(FIRE, CAST_BELL, 30, 7)
FIRE = overlay(FIRE, CAST_FEATHERS, 34, 6)
RETURN_STRING = R([
    '......oWo',
    '.....oWo.',
    '.ooooWo..',
    'oWWWWo...',
    '.oooo....',
])
RETURN = overlay(overlay(EMPTY, RETURN_STRING, 23, 6), FAN, 27, 8)
CLIPS = {'idle': [IDLE], 'charge': [CHARGE], 'fire': [FIRE], 'empty': [EMPTY], 'return': [RETURN]}
LURE = R([
    '......oo......',
    '.....oPHo.....',
    '....oPHpo.....',
    '...oHppoo.....',
    '..oSYoooo.....',
    '.oSsoYYYYyo...',
    'oWoo.oFFffo...',
    'oWo...oFFFo...',
    'oWo....oooo...',
    '.o............',
    '..............',
    '..............',
])
# A separately authored quarter-turn; not a mirrored duplicate.
LURE_2 = R([
    '..............',
    '.....oo.......',
    '....oHHo......',
    '...oPpHHo.....',
    '..oSYHpo......',
    '.oWSsYoo......',
    'oWooYYFfo.....',
    '.oWoYFFfo.....',
    '..oWoFFfo.....',
    '...oWooo......',
    '....o.........',
    '..............',
])
BURST = R([
    '.oo.........',
    'oPHo........',
    '.oPHo.......',
    '..oHpo......',
    '...oo.......',
    '.........oo.',
    '........oFFo',
    '.oo....oFFo.',
    'oAYo...ofo..',
    '.oYYo...o...',
    '..oYyo......',
    '...ooo......',
])
PROJECTILES = {'pluto_feather_lure_001': LURE, 'pluto_feather_lure_002': LURE_2,
               'pluto_loose_feather_burst_001': BURST}
# Separately authored upright inventory view, not a scaled-down 40px gun.
PAGE_WAND = R([
    '..............ooo...',
    '.............oLBo...',
    '............oLBoWo..',
    '...........oLBo.Wo..',
    '..........oLBo..Wo..',
    '.........oLBo...Wo..',
    '........oLBo....Wo..',
    '.......oLBo.........',
    '......oLBo..........',
    '.....oLBo...........',
    '....oLBo............',
    '...oLBo.............',
    '..oqPo..............',
    '.oqPPo..............',
    'oqPPpo..............',
    'oPPpo...............',
    '.ooo................',
])
PAGE = overlay(pad(PAGE_WAND, 24, 32, 1, 7), FAN, 13, 14)
