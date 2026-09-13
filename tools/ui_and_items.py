"""UI cards, gun, projectile and active-item art for Pluto."""
from PIL import Image, ImageDraw, ImageFont
from pixel import check_rect as R, img_from_rows, rotate, shift_clip as shift, pad_clip as pad, overlay_clip as overlay, recolor, rows_from_img, PALETTE
import character_anims as A
import poses as P

# ---------------------------------------------------------------- 34 x 34 face card (HUD / dialogue portrait)
FACE_34 = R([
"........oooo..........oooo........",
".......oBBBBo........oBBBBo.......",
"......oBBPPBBo......oBBPPBBo......",
"......oBBPPPBBo....oBBPPPBBo......",
".....oBBBPPPBBBooooBBBPPPBBBo.....",
".....oBBBBPBBoWWWWWWoBBPBBBBo.....",
"....oBBBBBBBBWWWWWWWWBBBBBBBBo....",
"...oBBbbBBBBLLWWWWWWLLBBBBbbBBo...",
"..oBBBbBBBBBBLBBBBBBLBBBBBBbBBBo..",
"..oBBBBBBBBBBBBBBBBBBBBBBBBBBBBo..",
".oBBBBBBBBBBBBWWWWWWBBBBBBBBBBBBo.",
".oBBbBBBBBBBBWWWWWWWWBBBBBBBBbBBo.",
".oBBBBBBBBBBWWWWWWWWWWBBBBBBBBBBo.",
"oBBBBBBBBBBWWWWWWWWWWWWBBBBBBBBBBo",
"oBBBBBWWWWWWWWWWWWWWWWWWWWWWBBBBBo",
"oBBBWWWoooWWWWWWWWWWWWoooWWWWBBBBo",
"oBBBWWoGGGoWWWWWWWWWWoGGGoWWWBBBBo",
"oBBBWWoGggGoWWWWWWWWoGggGoWWWBBBBo",
"oBBBWWoGggGoWWWWWWWWoGggGoWWWBBBBo",
"oBBBWWWoGGoWWWWWWWWWWoGGoWWWWBBBBo",
"oBBBBWWWooWWWWWWWWWWWWooWWWWBBBBBo",
".oBBBWWWWWWWWWWWWWWWWWWWWWWWBBBBo.",
".oBBBWWWWWWWWWWPPPPWWWWWWWWWWBBBo.",
".oBBWWWWWWWWWWPPPPPPWWWWWWWWWWBBo.",
"..oWWWWWWWWWWWWPPPPWWWWWWWWWWWWo..",
"..oWWWWWWWWWWWWWppWWWWWWWWWWWWWo..",
"...oWWWWWWWWWWWpWWpWWWWWWWWWWWo...",
"...oWWWWWWWWWWWWWWWWWWWWWWWWWWo...",
"....oWWWWWWWWWWWWWWWWWWWWWWWWo....",
".....oWWWWWWWWWWWWWWWWWWWWWWo.....",
"......oWWWWWWWWWWWWWWWWWWWWo......",
".......ooWWWWWWWWWWWWWWWWoo.......",
".........ooooWWWWWWWWoooo.........",
".............oooooooo.............",
])

# blink variant (eyes closed) for foyer idle
FACE_34_BLINK = list(FACE_34)
for y in (16, 17, 18):
    FACE_34_BLINK[y] = FACE_34_BLINK[y].replace('GggG', 'WWWW').replace('GGG', 'WWW').replace('oWW', 'oWW')
FACE_34_BLINK[18] = "oBBBWWooooooWWWWWWWWoooooooWWBBBBo"
FACE_34_BLINK[16] = "oBBBWWWWWWWWWWWWWWWWWWWWWWWWWBBBBo"
FACE_34_BLINK[17] = "oBBBWWWWWWWWWWWWWWWWWWWWWWWWWBBBBo"
FACE_34_BLINK[15] = "oBBBWWWWWWWWWWWWWWWWWWWWWWWWWBBBBo"
FACE_34_BLINK[19] = "oBBBWWWWWWWWWWWWWWWWWWWWWWWWWBBBBo"
FACE_34_BLINK[20] = "oBBBBWWWWWWWWWWWWWWWWWWWWWWWBBBBBo"
R(FACE_34_BLINK)

# punchout / hurt variants: 34x34 with progressively sadder face
FACE_34_HURT = list(FACE_34)
FACE_34_HURT[15] = "oBBBWWWoooWWWWWWWWWWWWoooWWWWBBBBo"
FACE_34_HURT[25] = "..oWWWWWWWWWWWWWppWWWWWWWWWWWWWo.."
FACE_34_HURT[26] = "...oWWWWWWWWWWpWWWWpWWWWWWWWWWo..."
FACE_34_HURT[27] = "...oWWWWWWWWWpWWWWWWpWWWWWWWWWo..."
R(FACE_34_HURT)


# v3 (shaded, frame-filling) portraits replace the flat v1 ones above.
from art_v3 import FACE_34, FACE_34_BLINK, FACE_34_HURT  # noqa: E402


def framed_38(face):
    """38 x 38 foyer select card: parchment frame around the 34 x 34 face."""
    rows = ['o' * 38] + ['o' + 'E' * 36 + 'o'] + ['oE' + '.' * 34 + 'Eo'] * 34 + ['o' + 'E' * 36 + 'o'] + ['o' * 38]
    return overlay(rows, face, 2, 2)


FOYER_IDLE = [framed_38(FACE_34), framed_38(FACE_34), framed_38(FACE_34), framed_38(FACE_34_BLINK)]
from pixel import scale_down, squash  # noqa: E402
_card = framed_38(FACE_34)
# pop-in: small -> grows -> lands with a squash -> settles
FOYER_APPEAR = [scale_down(_card, 0.35, anchor='center'), scale_down(_card, 0.6, anchor='center'),
                scale_down(_card, 0.85, anchor='center'), squash(_card, 0.9), _card]

# ---------------------------------------------------------------- minimap icon 9x9 and coop death 11x13
ICON_9 = R([
".oo...oo.",
"oBBo.oBBo",
"oBBBWBBBo",
"oBWWWWWBo",
"oWGWWWGWo",
"oWWWPWWWo",
".oWWWWWo.",
"..oWWWo..",
"...ooo...",
])

COOP_DEATH = R([
".oo.....oo.",
"oBBo...oBBo",
"oBBBoooBBBo",
"oBBBWWWBBBo",
"oBWWWWWWWBo",
"oWgWgWgWgWo",
"oWWWWPWWWWo",
".oWWWWWWWo.",
".oWWWWWWWo.",
"..oWWWWWo..",
"..oWWWWWo..",
"...ooooo...",
"..........."[:11],
])

# ---------------------------------------------------------------- gun: Royal Canin dry-food bag, held sideways (26 x 16, opening on the right)
# Reference: reference/ideas/weapon_idea.png. White bag with silver edges, the five-dot crown,
# the red ROYAL CANIN band, the purple Sterilised label with the grey cat, kibble spilling out.
GUN_IDLE = R([
"...oooooooooooooooooooo...",
"..oNNWWWWWWRRRWWWWWWWWNo..",
".oNWWWWWWWWRRRWWWVVVWWWNo.",
".oNWWWWRWWWRRRWWVVVVVWWNoo",
"oNWWWWRRRWWRRRWVVZZZVVWNoM",
"oNWWWWWRWWWRRRWVVZzZVVWNoo",
"oNWWWWWWWWWRRRWVVZZZVVWNo.",
"oNWWWWWWWWWRRRWVVzZzVVWNoM",
"oNWWWWWWWWWRRRWWVVVVVWWNoo",
".oNWWWWWWWWRRRWWWVVVWWWNo.",
".oNWWWWWWWWRRRWWWWWWWWWNo.",
"..oNNWWWWWWRRRWWWWWWWWNo..",
"...oooooooooooooooooooo...",
"..........................",
"..........................",
"..........................",
])
GUN_W, GUN_H = 26, 16

_BURST = R([  # kibble flying out of the opening
"..........................",
"..........................",
".........................M",
"..........................",
"........................MM",
"..........................",
"........................M.",
"..........................",
".........................M",
"..........................",
"..........................",
"..........................",
"..........................",
"..........................",
"..........................",
"..........................",
])
GUN_FIRE = [
    overlay(shift(GUN_IDLE, -1, 0), _BURST),
    overlay(GUN_IDLE, shift(_BURST, 0, 1)),
    GUN_IDLE,
]
_POUR = R([  # kibble tumbling back into the bag during reload
"..........................",
"..........................",
"..........................",
"..........................",
".......................M..",
"..........................",
"......................M...",
"..........................",
"..........................",
"..........................",
"..........................",
"..........................",
"..........................",
"..........................",
"..........................",
"..........................",
])
GUN_RELOAD = [
    shift(GUN_IDLE, 0, 1),
    overlay(shift(GUN_IDLE, 1, 0), _POUR),
    overlay(shift(GUN_IDLE, 0, -1), shift(_POUR, 0, 2)),
    GUN_IDLE,
]

# Upright bag for the Ammonomicon page (20 x 26).
GUN_AMMONOMICON = R([
"....oooooooooooo....",
"...oNNNNNNNNNNNNo...",
"..oNWWWWWWWWWWWWNo..",
".oNWWWWWWWWWWWWWWNo.",
".oNWWWWWWRWWWWWWWNo.",
".oNWWWWWRWRWWWWWWNo.",
".oNWWWWWRRRWWWWWWNo.",
".oNWWWWWWWWWWWWWWNo.",
".oNRRRRRRRRRRRRRRNo.",
".oNRRRRRRRRRRRRRRNo.",
".oNWWWWWWWWWWWWWWNo.",
".oNWWWWVVVVVWWWWWNo.",
".oNWWWVVVVVVVWWWWNo.",
".oNWWWVVZZZVVWWWWNo.",
".oNWWWVVZzZVVWWWWNo.",
".oNWWWVVZZZVVWWWWNo.",
".oNWWWVVVZVVVWWWWNo.",
".oNWWWWVVVVVWWWWWNo.",
".oNWWWWWWWWWWWWWWNo.",
".oNWWWWWWWWWWWMMWNo.",
".oNWWWWWWWWWWWMmWNo.",
".oNWWWWWWWWWWWWWWNo.",
".oNRRRRRRRRRRRRRRNo.",
".oNNNNNNNNNNNNNNNNo.",
"..oNNNNNNNNNNNNNNo..",
"...oooooooooooooo...",
])

# Triangular brown kibble (reference/ideas/weapon_projectile_idea.png), 8 x 8.
KIBBLE = R([
"...oo...",
"..ommo..",
"..omMo..",
".omMMmo.",
".omMMMo.",
"omMMMMmo",
"ommmmmmo",
".oooooo.",
])

# ---------------------------------------------------------------- active: Royal Canin wet-food can (16 x 16)
# Reference: reference/ideas/active_item_idea.png. Gold tin, pink label, crown + red band, kitten.
CAN_ICON = R([
"....oooooooo....",
"..ooAAAAAAAAoo..",
".oAKAAaAAAAaAAo.",
".oAAAAAAAAAAAAo.",
".oooooooooooooo.",
".oIIIIIIIIIIIIo.",
".oIIWWRWRWWWIIo.",
".oIWWWWRRRWWWIo.",
".oIWWRRRRRRWWIo.",
".oIWWWWWWWWWWIo.",
".oIIZZWWWMMWIIo.",
".oIIIIIIIIIIIIo.",
".oooooooooooooo.",
".oAAAAAAAAAAAAo.",
"..ooaaaaaaaaoo..",
"....oooooooo....",
])
CAN_TOSS = [rotate(CAN_ICON, a) for a in (0, -90, -180, -270)]

CAN_SPLASH = [
    R([
"................",
"................",
"................",
"................",
".....oooooo.....",
"....oAAaAAAo....",
"...oAAAMMMAAo...",
"...oAMMMMMMAo...",
"..oMMMmMMMmMMo..",
".oMMMMMMMMMMMMo.",
".oMmMMMMMMMMmMo.",
"..ooMMMMMMMMoo..",
"....oooooooo....",
"................",
"................",
"................",
    ]),
    R([
"................",
"......oHo.......",
".....oHHHo......",
"......oHo.......",
".....oooooo.....",
"....oAAaAAAo....",
"...oAAAMMMAAo...",
"..oAMMMMMMMMAo..",
".oMMMmMMMmMMMMo.",
"oMMMMMMMMMMMMMMo",
"oMmMMMMMMMMMMmMo",
".ooMMMMMMMMMMoo.",
"...oooooooooo...",
"................",
"................",
"................",
    ]),
    R([
"..oHo......oHo..",
".oHHHo....oHHHo.",
"..oHo..oHo.oHo..",
"......oHHHo.....",
".....ooHHHoo....",
"....oAAoHoAAo...",
"...oAAAMMMAAAo..",
"..oAMMMMMMMMMAo.",
".oMMMmMMMmMMMMMo",
"oMMMMMMMMMMMMMMo",
"oMmMMMMMMMMMMmMo",
".ooMMMMMMMMMMoo.",
"...oooooooooo...",
"................",
"................",
"................",
    ]),
]

# v3 composed bag / can replace the flat v2 ones above.
from art_v3 import GUN_IDLE, GUN_FIRE, GUN_RELOAD, GUN_AMMONOMICON, GUN_W, GUN_H, CAN_ICON, CAN_TOSS, CAN_SPLASH  # noqa: E402

# ---------------------------------------------------------------- big cards rendered with PIL


def _font(size):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def boss_card():
    """427 x 240 boss-intro card: dark background, big portrait, name."""
    W, H = 427, 240
    im = Image.new('RGBA', (W, H), PALETTE['Q'])
    d = ImageDraw.Draw(im)
    for y in range(H):  # vertical gradient
        t = y / H
        c = tuple(int(PALETTE['Q'][i] * (1 - t) + PALETTE['X'][i] * t) for i in range(3)) + (255,)
        d.line([(0, y), (W, y)], fill=c)
    # decorative frame
    d.rectangle([4, 4, W - 5, H - 5], outline=PALETTE['E'], width=2)
    d.rectangle([10, 10, W - 11, H - 11], outline=PALETTE['B'], width=1)
    face = img_from_rows(FACE_34).resize((34 * 6, 34 * 6), Image.NEAREST)
    im.alpha_composite(face, (24, 18))
    # name text, pixel-style: render small then upscale nearest
    small = Image.new('RGBA', (60, 34), (0, 0, 0, 0))
    ds = ImageDraw.Draw(small)
    ds.text((1, 0), "PLUTO", font=_font(16), fill=PALETTE['E'])
    ds.text((1, 19), "THE CAT", font=_font(11), fill=PALETTE['W'])
    small = small.resize((60 * 3, 34 * 3), Image.NEAREST)
    im.alpha_composite(small, (236, 62))
    # kibble trail
    kib = img_from_rows(KIBBLE).resize((24, 24), Image.NEAREST)
    for i, (x, y) in enumerate(((250, 180), (290, 195), (330, 178), (370, 192))):
        im.alpha_composite(kib, (x, y))
    return im


def win_pic():
    """115 x 71 end-of-run picture: Pluto with hearts on parchment."""
    W, H = 115, 71
    im = Image.new('RGBA', (W, H), PALETTE['E'])
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W - 1, H - 1], outline=PALETTE['o'])
    d.rectangle([0, 52, W - 1, H - 1], fill=PALETTE['B'])
    d.line([(0, 52), (W, 52)], fill=PALETTE['b'])
    cat_im = img_from_rows(A.PAWS)
    cat = cat_im.resize((cat_im.width * 3, cat_im.height * 3), Image.NEAREST)
    im.alpha_composite(cat, (30, 0))
    heart = img_from_rows(R([".oo.oo.", "oHHoHHo", "oHHHHHo", ".oHHHo.", "..oHo..", "...o..."]))
    for (x, y, s) in ((8, 10, 2), (95, 8, 2), (14, 32, 1), (100, 30, 1), (88, 40, 1)):
        im.alpha_composite(heart.resize((7 * s, 6 * s), Image.NEAREST), (x, y))
    bowl = img_from_rows(R([
"..oooooooooo..",
".oYYyYYyYYyYo.",
"oSSSSSSSSSSSSo",
".oSSsSSSSsSSo.",
"..oossssssoo..",
"....oooooo....",
    ])).resize((28, 12), Image.NEAREST)
    im.alpha_composite(bowl, (80, 48))
    return im


def thunderstore_icon():
    """256 x 256 package icon: face on a tabby-brown background with a border."""
    im = Image.new('RGBA', (256, 256), PALETTE['X'])
    d = ImageDraw.Draw(im)
    d.rectangle([6, 6, 249, 249], outline=PALETTE['E'], width=4)
    face = img_from_rows(FACE_34).resize((34 * 6, 34 * 6), Image.NEAREST)
    im.alpha_composite(face, (26, 20))
    kib = img_from_rows(KIBBLE).resize((32, 32), Image.NEAREST)
    im.alpha_composite(kib, (200, 200))
    heart = img_from_rows(R([".oo.oo.", "oHHoHHo", "oHHHHHo", ".oHHHo.", "..oHo..", "...o..."])).resize((28, 24), Image.NEAREST)
    im.alpha_composite(heart, (22, 200))
    return im


# ---------------------------------------------------------------- v2: Nine Lives icon (16x16 paw with a 9), crumb (5x5), laser dot (4x4)
NINE_LIVES_ICON = R([
"....oo....oo....",
"...oWWo..oWWo...",
"...oWWo..oWWo...",
"oo.oWWo..oWWo.oo",
"oWo.oo....oo.oWo",
"oWWo..oooo..oWWo",
".oo..oWWWWo..oo.",
".....oWWWWo.....",
"....oWWWWWWo....",
"....oWWWWWWo....",
"....oWWWWWWo....",
".....oWWWWo.....",
"......oooo......",
".......ooo......",
".......oHo......",
".......ooo......",
])
CRUMB = R([
".ooo.",
"omMmo",
"oMMMo",
"ommmo",
".ooo.",
])
LASER_DOT = R([
".RR.",
"RRRR",
"RRRR",
".RR.",
])


# ---------------------------------------------------------------- v2: alt-skin swapper object (32x32 bathtub) and wet face card
BATHTUB = R([
"................................",
"................................",
"................................",
"................................",
"................................",
"...........ooo..................",
"..........oSSSo.................",
"..........oSooSo................",
"..........oSo.oo................",
"....oooooooSooooooooooooooo.....",
"...oKKKKKKKKKKKKKKKKKKKKKKKo....",
"..oKFFFFFFFFFFFFFFFFFFFFFFFKo...",
"..oKFfFFFFFFfFFFFFFFfFFFFFFKo...",
"..oKFFFFFFFFFFFFFFFFFFFFFFFKo...",
"..oKKKKKKKKKKKKKKKKKKKKKKKKKo...",
"..oKKKKKKKKKKKKKKKKKKKKKKKKKo...",
"..oKKKKKKKKKKKKKKKKKKKKKKKKKo...",
"...oKKKKKKKKKKKKKKKKKKKKKKKo....",
"....oooooooooooooooooooooooo....",
"......oSo..............oSo......",
"......ooo..............ooo......",
"................................",
"................................",
"................................",
"................................",
"................................",
"................................",
"................................",
"................................",
"................................",
"................................",
"................................",
])
BATHTUB_2 = list(BATHTUB)
BATHTUB_2[11] = "..oKFfFFFFFFFFFfFFFFFFFFFfFKo..."
BATHTUB_2[12] = "..oKFFFFFFFFFFFFFFFFFFFFFFFKo..."
R(BATHTUB_2)


# ---------------------------------------------------------------- v2.1: hairball projectile (10x10)
HAIRBALL = R([
"...oooo...",
"..oJjJJo..",
".oJJjJjJo.",
"oJjJJJJJJo",
"oJJJjJJjJo",
"oJjJJJJJJo",
"oJJJJjJJJo",
".oJjJJJjo.",
"..oJJjJo..",
"...oooo...",
])
