"""Five cat item icons (16x16), hand-drawn as row strings. Gemini was out of credits (2026-09-15), so these are
drawn directly in the style of the existing icons (Resources/Items/*_icon.png).
Run from the repo root: python3 reference/gemini/cat_items/draw_items.py"""
import os
from PIL import Image

OUT = 'reference/gemini/cat_items/build'
PAL = {
    'o': '1E1614',                                   # outline, shared darkest
    'P': 'E8A0B0', 'p': 'D46A7A', 'q': 'F5C6D0',     # pink ramp (ear pink, yarn)
    'L': 'B4A180', 'B': '8B7A66', 'd': '66524A', 'b': '3B2C24',   # tabby ramp (burlap, hairball)
    'G': '9CB64E', 'g': '5E7A30',                    # hazel green + dark leaf (new: catnip leaf shadow)
    'R': 'C0392B', 'r': '7E2A22',                    # collar red (new: collar)
    'Y': 'E8B04A', 'y': 'B8742A', 'h': 'FFF0B0',     # gold, from the Taiyaki Cannon ramp
    'W': 'FAF6EE', 'w': 'D6CEC6', 'x': 'B9B0A8',     # white / silver
    'S': 'D6BE8A', 's': '9C8058',                    # sisal rope (new: scratching post)
    'V': '7A6A8A', 'v': '54466A',                    # carpet (new: scratching post base)
}

ITEMS = {
    'ball_of_yarn_icon': [
        '................',
        '.....oooooo.....',
        '...ooqqqqPPoo...',
        '..oqqqPPPppPPo..',
        '..oqqPPppPPPPo..',
        '.oqPPppPPPPPppo.',
        '.oqPppPPPPpppPo.',
        '.oPpPPPPpppPPPo.',
        '.oppPPPppPPPPpo.',
        '.oPPPppPPPPpppo.',
        '..oPppPPPppppo..',
        '..oPPPPpppPPpo..',
        '...oopppPPppoo..',
        '.....ooooooPPo..',
        '...........oPo..',
        '............o...',
    ],
    'catnip_pouch_icon': [
        '..oo........oo..',
        '.oGGo......oGGo.',
        '.oGGGo....oGGGo.',
        '..oGGGo..oGGGo..',
        '...oGGGooGGGo...',
        '....oggggggo....',
        '.....obbbbo.....',
        '....oLLbbLBo....',
        '...oLLLLLLBBo...',
        '..oLLLLLLLBBdo..',
        '..oLLBBLLLBBdo..',
        '.oLLLLLLLLBBddo.',
        '.oLLLLLBBLBBddo.',
        '.oBBBBBBBBBdddo.',
        '..oddddddddddo..',
        '...oooooooooo...',
    ],
    'jingle_bell_collar_icon': [
        '................',
        '....oooooooo....',
        '..ooRRRRRRRRoo..',
        '.oRRooooooooRRo.',
        '.oRo........oRo.',
        'oRRo.......oWWo.',
        'oRRo.......oxxo.',
        'orro........oro.',
        '.orro......orro.',
        '..orrooooooorro.',
        '...ooooooooo....',
        '.....ohYYyo.....',
        '....oYhYYyyo....',
        '....oYYYYyyo....',
        '....oyyooyyo....',
        '.....oooooo.....',
    ],
    'hairball_icon': [
        '................',
        '.....o....o.....',
        '......o..oo.....',
        '....ooooooooo...',
        '...oLLLLLBBBBo..',
        '..oLWWLLBBBBBBo.',
        '..oLWLLBBddBBddo',
        'ooLLLBBddBBBBddo',
        '.oLLBBddBBBddBdo',
        '.oLBBddBBBddBBdo',
        '.oBBBBBBBddBBddo',
        'ooBBBBBBddBBddoo',
        '..odBBBddBBdddo.',
        '...oodddddddoo..',
        '.....ooooooo....',
        '................',
    ],
    'scratching_post_icon': [
        '....oooooooo....',
        '...oVVVVVVVVo...',
        '...ovvvvvvvvoo..',
        '....ooSSSSoo.b..',
        '.....oSSSSo..b..',
        '.....ossssoo.b..',
        '.....oSSSSo.oqo.',
        '.....oSSSSooqqPo',
        '.....ossssooPPPo',
        '.....oSSSSo.ooo.',
        '.....oSSSSo.....',
        '...oossssoo.....',
        '..oVVVVVVVVVVo..',
        '..oVVVVVVVVVvo..',
        '..ovvvvvvvvvvo..',
        '...oooooooooo...',
    ],
}


def render(rows):
    assert len(rows) == 16 and all(len(r) == 16 for r in rows), [len(r) for r in rows]
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    for y, row in enumerate(rows):
        for x, k in enumerate(row):
            if k != '.':
                im.putpixel((x, y), tuple(int(PAL[k][i:i + 2], 16) for i in (0, 2, 4)) + (255,))
    return im


def main():
    os.makedirs(OUT, exist_ok=True)
    ims = {n: render(r) for n, r in ITEMS.items()}
    for n, im in ims.items():
        im.save(f'{OUT}/{n}.png')
    # contact sheet: zoomed row on green (Gemini-ref style) plus 1x/2x on a dungeon-floor grey
    existing = ['nine_lives_icon', 'wet_food_can_icon']
    ref = [Image.open(f'PlutoTheCat/Resources/Items/{e}.png').convert('RGBA') for e in existing]
    Z = 12
    row = list(ims.values()) + ref
    W = sum(i.width * Z + 16 for i in row) + 16
    sheet = Image.new('RGBA', (W, 20 * Z + 120), (0, 0, 0, 255))
    top = Image.new('RGBA', (W, 18 * Z + 16), (0, 177, 64, 255))
    sheet.paste(top, (0, 0))
    floor = Image.new('RGBA', (W, 120), (58, 52, 60, 255))
    sheet.paste(floor, (0, 18 * Z + 16))
    x = 16
    for im in row:
        z = im.resize((im.width * Z, im.height * Z), Image.NEAREST)
        sheet.paste(z, (x, 8), z)
        for s, dy in ((1, 18 * Z + 30), (2, 18 * Z + 56)):
            zi = im.resize((im.width * s, im.height * s), Image.NEAREST)
            sheet.paste(zi, (x, dy), zi)
        x += im.width * Z + 16
    sheet.save(f'{OUT}/sheet.png')
    print('wrote', len(ims), 'icons +', f'{OUT}/sheet.png')


if __name__ == '__main__':
    main()
