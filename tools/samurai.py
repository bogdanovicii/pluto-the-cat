"""Samurai costume (2.16.0): every Pluto clip rebuilt with kimono parts.

The costume design is copied from the approved Gemini sheet (reference/gemini/samurai_costume/sheet.png): a crimson
hachimaki across the forehead with two tails behind the head, an indigo haori with an open V collar showing the white
chest, a crimson obi, charcoal hakama, a white paw crest on the back. It is applied to the head and body PARTS, then
character_anims is rebuilt from those parts, so every derived frame (idle squash, run lean, crouch, hit, loaf) carries
the costume the same way the normal frames carry the markings. Originals are restored afterwards.

build() -> (clips, breach_idles, hand)
"""
import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

TABBY = {'B': '5', 'L': '7', 'l': '7', 'd': '6', 'b': '6', '9': '6', 'G': 'G', 'g': 'g'}
HAKAMA = {'B': '4', 'L': '4', 'l': '4', 'W': '4', 'K': '4', 'w': '0', 'x': '0', 'd': '0', 'b': '0', '9': '0'}
WHITE = 'WwxK'


def _fill(ch):
    return ch not in '.o'


def headband(rows, view):
    """Crimson band on the forehead row (row 4 of the 12-row head); tails trail behind the head (left) for the side,
    back-diagonal and front views; a knot on the back of the head for the back view."""
    g = [list(r) for r in rows]
    y = 4
    xs = [x for x in range(len(g[y])) if _fill(g[y][x])]
    for x in xs:
        g[y][x] = '8'
    for x in xs[-2:]:
        g[y][x] = 'r'
    if view in ('side', 'bw', 'front'):
        for (x, yy, c) in ((1, 3, '8'), (0, 4, '8'), (1, 4, '8'), (2, 4, '8'), (0, 5, 'r'), (1, 5, '8'), (0, 6, 'r')):
            if yy < len(g) and g[yy][x] == '.':
                g[yy][x] = c
    if view == 'back':
        cx = len(g[0]) // 2
        for (x, yy) in ((cx - 1, 5), (cx, 5), (cx - 1, 6), (cx, 6)):
            if _fill(g[yy][x]):
                g[yy][x] = 'r'
    return [''.join(r) for r in g]


def kimono(rows, view, obi_row=4):
    """Body part rows: haori above the obi (tabby -> indigo; white kept only in the V collar), obi row crimson,
    hakama below (charcoal). Back view gets the white paw crest."""
    g = [list(r) for r in rows]
    w = len(g[0])
    whites0 = [x for x in range(w) if g[0][x] in WHITE] or [w // 2]
    centre = sum(whites0) / len(whites0)
    for y in range(len(g)):
        xs = [x for x in range(w) if _fill(g[y][x])]
        for x in xs:
            ch = g[y][x]
            if y == obi_row:
                g[y][x] = '8'
            elif y > obi_row:
                g[y][x] = HAKAMA.get(ch, ch)
            elif ch in TABBY:
                g[y][x] = TABBY[ch]
            elif ch in WHITE:
                if view == 'back' or abs(x - centre) > max(0, 3 - y):
                    g[y][x] = '5' if ch in 'WK' else '6'
        if y == obi_row and xs:
            for x in xs[-2:]:
                g[y][x] = 'r'
    if view == 'back':
        cx = w // 2
        for (x, yy) in ((cx - 1, 1), (cx, 1), (cx - 1, 2), (cx, 2), (cx - 2, 0), (cx + 1, 0)):
            if 0 <= yy < obi_row and _fill(g[yy][x]):
                g[yy][x] = 'W'
    return [''.join(r) for r in g]


def region(rows, body=lambda x, y: False, band=lambda x, y: False, obi=lambda x, y: False, hakama=lambda x, y: False):
    """Costume for a hand-drawn part: pixels selected by position. body: tabby -> haori indigo (white stays: chest,
    paws, muzzle); band: fill -> headband crimson; obi: fill -> crimson; hakama: fill -> charcoal."""
    g = [list(r) for r in rows]
    for y in range(len(g)):
        for x in range(len(g[y])):
            ch = g[y][x]
            if not _fill(ch):
                continue
            if band(x, y) or obi(x, y):
                g[y][x] = '8'
            elif hakama(x, y):
                g[y][x] = HAKAMA.get(ch, ch)
            elif body(x, y) and ch in TABBY:
                g[y][x] = TABBY[ch]
    return [''.join(r) for r in g]


def build():
    import poses as P
    import poses_extra as X
    import character_anims as A

    heads = {'HEAD_SIDE': 'side', 'HEAD_FRONT': 'front', 'HEAD_BACK': 'back', 'HEAD_BW': 'bw'}
    bodies = {'BODY_SIDE': 'side', 'BODY_FRONT': 'front', 'BODY_BACK': 'back', 'BODY_BW': 'bw'}
    try:
        for n, v in heads.items():
            setattr(P, n, headband(getattr(P, n), v))
        for n, v in bodies.items():
            setattr(P, n, kimono(getattr(P, n), v))
        # derived poses in poses.py
        P.IDLE_SIDE = P.stack(P.HEAD_SIDE, P.BODY_SIDE, P.LEGS_SIDE)
        P.IDLE_FRONT = P.stack(P.HEAD_FRONT, P.BODY_FRONT, P.LEGS_FRONT)
        P.IDLE_BACK = P.stack(P.HEAD_BACK, P.BODY_BACK, P.LEGS_BACK)
        P.SIDE_BODY = P.stack(P.HEAD_SIDE, P.BODY_SIDE, P.EMPTY_LEGS)
        P.FRONT_BODY = P.stack(P.HEAD_FRONT, P.BODY_FRONT, P.EMPTY_LEGS)
        P.BACK_BODY = P.stack(P.HEAD_BACK, P.BODY_BACK, P.EMPTY_LEGS)
        P.BW_BODY = P.stack(P.HEAD_BW, P.BODY_BW, P.EMPTY_LEGS)
        pu = list(P.PAWS_UP)
        P.PAWS_UP = headband(pu[:P.HEAD_ROWS], 'front') + kimono(pu[P.HEAD_ROWS:P.HEAD_ROWS + P.BODY_ROWS], 'front') + pu[P.HEAD_ROWS + P.BODY_ROWS:]
        # derived poses in poses_extra.py (low body: 2 haori rows, obi, hakama)
        X.BODY_SIDE_LOW = kimono(X.BODY_SIDE_LOW, 'side', obi_row=2)
        X.CROUCH, X.LAND = X.low_pose(3), X.low_pose(2)
        X.KNEEL, X.KNEEL_LOW, X.SLIDE = X.low_pose(3, 'shut'), X.low_pose(4, 'shut'), X.low_pose(3, 'wide')
        X.HIT = P.stack(P.mouth_open(P.eyes(P.HEAD_SIDE, P.EYES_SIDE, 'shut'), 11, 11), P.BODY_SIDE, P.LEGS_SIDE)
        X.LOAF_BODY = kimono(X.LOAF_BODY, 'side', obi_row=1)
        X.LOAF, X.LOAF_DOWN = X.loaf(6), X.loaf(7)
        # hand-drawn tumble / roll / lying parts: haori over the tabby body, obi and headband where the layout puts them
        X.TUCK_SIDE = region(X.TUCK_SIDE, body=lambda x, y: x <= 8 and 2 <= y <= 13, band=lambda x, y: y == 4 and x >= 9)
        X.TUCK_SIDE_BW = region(X.TUCK_SIDE_BW, body=lambda x, y: x <= 8 and 2 <= y <= 13, band=lambda x, y: y == 4 and x >= 9)
        X.CROWN = region(X.CROWN, body=lambda x, y: False, band=lambda x, y: y == 4)
        X.BACK_UP = region(X.BACK_UP, body=lambda x, y: 4 <= y <= 9, band=lambda x, y: y == 11, obi=lambda x, y: y == 3)
        X.BELLY_UP = region(X.BELLY_UP, body=lambda x, y: 5 <= y <= 6, band=lambda x, y: y == 10, obi=lambda x, y: y == 4,
                            hakama=lambda x, y: y == 3)
        X.LYING = region(X.LYING, body=lambda x, y: x <= 9 and 14 <= y <= 20)
        X.TIP = region(X.TIP, body=lambda x, y: y <= 12, band=lambda x, y: y == 14)
        importlib.reload(A)
        clips, breach = A.CLIPS, A.BREACH_IDLES
        hand = ['.oo.', 'o55o', 'oWWo', '.oo.']    # white paw with an indigo sleeve cuff
        return clips, breach, hand
    finally:
        importlib.reload(P)
        importlib.reload(X)
        importlib.reload(A)


if __name__ == '__main__':
    clips, breach, hand = build()
    print(len(clips), 'samurai clips,', len(breach), 'breach idles')
