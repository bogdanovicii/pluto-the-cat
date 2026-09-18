"""Geometric regression test for the Shrine Stall redesign (2.20.8) against the three user problems of 2.20.7.

  P1  the items are not on the counter: two ItemPoints past the counter's right edge, item 0 over Daifuku.
  P2  the bowl sits 0.19 tiles from Daifuku and covers him; the torii and the counter are flat and overlap.
  P3  nothing has a collider.

Unlike test_shrine_stall.py / test_shrine_stall_collision.py, which pin the redesign's own constant NAMES and
numbers, this file builds the scene the way the game would and asserts only the outcome, so it gives a
geometric verdict on ANY revision of ShrineStall.cs (2.20.7's included): the layout is read from the source
whatever it is called (Vector3.zero, `StallOffset + new Vector3(...)`, an inline npcPosition,
ShopAPI.defaultItemPositions), and every sprite size is read from the Resources/Shop PNGs of the same tree.

Frame: the shop root R (= PlutoConfig.StallPosition), x right, y up, px (16 px = 1 tile). R is assumed to be
on the pixel grid. Rectangles are half-open [x0, x1) x [y0, y1). Placement rules (archaeology, measured):
  * props (torii, counter, bowl) are PlaceProp'd LowerCenter, then their transform is quantised to 1/16:
    sprite lower-left = round(offset * 16 - width / 2), offset.y * 16;
  * Daifuku's npcPosition is his sprite's LOWER-LEFT, local to R;
  * each shop item is centred (MiddleCenter) on its ItemPoint, drawn as blueprint.png plus the shop's
    1-px runtime outline;
  * depth z = worldY(sprite bottom) - HeightOffGround, lower z draws in front. Alexandria forces
    HeightOffGround -1.25 on every foyer item unless the mod overrides it after DoSetup; Daifuku keeps 0;
  * a Manual PixelCollider's offset is measured from its prop's lower-left.
"""
import ast
import math
import operator
import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / 'PlutoTheCat' / 'src'
SHOP = ROOT / 'PlutoTheCat' / 'Resources' / 'Shop'
STALL_CS = SRC / 'ShrineStall.cs'
COLLISION_CS = SRC / 'ShrineStallCollision.cs'

PX = 16.0

# Alexandria 0.5.10 ShopAPI.defaultItemPositions (ShopAPI::.cctor IL: (1.125, 2.125, 1), (2.625, 1, 1),
# (4.125, 2.125, 1)), for a SetUpFoyerShop call that passes them instead of its own points.
ALEXANDRIA_DEFAULT_ITEM_POSITIONS = ((1.125, 2.125, 1.0), (2.625, 1.0, 1.0), (4.125, 2.125, 1.0))
ALEXANDRIA_FORCED_ITEM_HEIGHT_OFF_GROUND = -1.25   # CustomShopItemController.Initialize, foyer items
MIN_BOWL_TO_DAIFUKU_TILES = 1.2
ITEM_OUTLINE_PX = 1

# SetUpFoyerShop's positional parameters we read (same order in every revision).
ARG_NPC_POSITION, ARG_ITEM_POSITIONS = 16, 18
ARG_HITBOX_SIZE, ARG_HITBOX_OFFSET = -2, -1

SOLID_LAYERS = {'HighObstacle', 'LowObstacle', 'PlayerBlocker', 'EnemyBlocker', 'BulletBlocker'}

_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv}


# ---------------------------------------------------------------------------------------------------------------
# C# source parsing
# ---------------------------------------------------------------------------------------------------------------

def strip_comments(text):
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
    return re.sub(r'//[^\n]*', '', text)


def num_eval(expr, names, integer=False):
    """C# float/int constant arithmetic (+ - * /, unary minus, parentheses, known names), no eval()."""
    cleaned = re.sub(r'(\d)f\b', r'\1', expr.strip())

    def ev(node):
        if isinstance(node, ast.Expression):
            return ev(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value if integer else float(node.value)
        if isinstance(node, ast.Name):
            if node.id not in names:
                raise ValueError('unknown name %r in %r' % (node.id, expr))
            return names[node.id]
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -ev(node.operand)
        if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
            a, b = ev(node.left), ev(node.right)
            if integer and isinstance(node.op, ast.Div):
                return int(a / b)   # C# int division truncates toward zero
            return _OPS[type(node.op)](a, b)
        raise ValueError('unsupported expression %r' % expr)

    return ev(ast.parse(cleaned, mode='eval'))


def consts(text, kind):
    """Every `const <kind> NAME = EXPR;` in declaration order, evaluated."""
    values = {}
    for name, expr in re.findall(r'const\s+' + kind + r'\s+(\w+)\s*=\s*([^;]+);', text):
        try:
            values[name] = num_eval(expr, values, integer=(kind == 'int'))
        except ValueError:
            pass
    return values


def split_args(text):
    out, depth, cur = [], 0, ''
    for ch in text:
        if ch == ',' and depth == 0:
            out.append(cur)
            cur = ''
            continue
        depth += ch in '({['
        depth -= ch in ')}]'
        cur += ch
    out.append(cur)
    return [a.strip() for a in out]


def call_args(text, start):
    """Arguments of the call whose '(' is at text[start]."""
    i, depth = start + 1, 1
    while depth:
        depth += {'(': 1, ')': -1}.get(text[i], 0)
        i += 1
    return split_args(text[start + 1:i - 1])


class Source(object):
    """ShrineStall.cs, comments stripped, with its float constants and static readonly Vector3 fields."""

    def __init__(self, path):
        self.text = strip_comments(path.read_text(encoding='utf-8'))
        self.f = consts(self.text, 'float')
        self.fields = dict(re.findall(r'static\s+readonly\s+Vector3\s+(\w+)\s*=\s*([^;]+);', self.text))

    def vec(self, expr):
        """Vector3 expression: sums of Vector3.zero, new Vector3(a, b, c) and other Vector3 fields."""
        total = [0.0, 0.0, 0.0]
        for term in self._terms(expr):
            if term == 'Vector3.zero':
                v = (0.0, 0.0, 0.0)
            elif term.startswith('new Vector3('):
                v = tuple(num_eval(a, self.f) for a in call_args(term, term.index('(')))
            elif term in self.fields:
                v = self.vec(self.fields[term])
            else:
                raise ValueError('cannot evaluate Vector3 term %r' % term)
            total = [a + b for a, b in zip(total, v)]
        return tuple(total)

    @staticmethod
    def _terms(expr):
        terms, depth, cur = [], 0, ''
        for ch in expr.strip():
            if ch == '+' and depth == 0:
                terms.append(cur.strip())
                cur = ''
                continue
            depth += ch == '('
            depth -= ch == ')'
            cur += ch
        terms.append(cur.strip())
        return terms

    def field(self, name):
        if name not in self.fields:
            raise AssertionError('ShrineStall.cs has no Vector3 field ' + name)
        return self.vec(self.fields[name])


# ---------------------------------------------------------------------------------------------------------------
# Scene
# ---------------------------------------------------------------------------------------------------------------

def png(name):
    from PIL import Image
    with Image.open(SHOP / name) as im:
        im = im.convert('RGBA')
        return im.size, im.getchannel('A').getbbox(), im.getchannel('A').load()


def overlaps(a, b):
    return a[0][0] < b[0][1] and b[0][0] < a[0][1] and a[1][0] < b[1][1] and b[1][0] < a[1][1]


def centre(r):
    return ((r[0][0] + r[0][1]) / 2.0, (r[1][0] + r[1][1]) / 2.0)


class Scene(object):
    def __init__(self, t):
        src = Source(STALL_CS)
        self.src = src
        text = src.text

        # Props: variable/filename/offset/heightOffGround straight from the PlaceProp calls.
        self.props = {}
        for m in re.finditer(r'PlaceProp\(', text):
            args = call_args(text, m.end() - 1)
            files = re.findall(r'"(\w+\.png)"', args[0])
            if not files:
                continue
            pos = re.sub(r'PlutoConfig\.StallPosition\s*\+\s*', '', args[1])
            hog = num_eval(args[3], src.f)
            before = text[max(0, m.start() - 80):m.start()]
            var = re.search(r'(\w+)\s*=\s*$', before)
            self.props[files[0]] = dict(offset=src.vec(pos), hog=hog, var=var.group(1) if var else None)
        for name in ('torii.png', 'stall.png', 'kinsuke_idle_001.png'):
            t.assertIn(name, self.props, 'ShrineStall.cs never places ' + name)

        # SetUpFoyerShop: Daifuku, his hitbox, the item points.
        i = text.index('ShopAPI.SetUpFoyerShop(')
        shop = call_args(text, text.index('(', i))
        self.npc = src.vec(shop[ARG_NPC_POSITION]) if not re.fullmatch(r'\w+', shop[ARG_NPC_POSITION]) \
            else src.field(shop[ARG_NPC_POSITION])
        items_arg = shop[ARG_ITEM_POSITIONS]
        if items_arg == 'ShopAPI.defaultItemPositions':
            self.items = [tuple(p) for p in ALEXANDRIA_DEFAULT_ITEM_POSITIONS]
        else:
            m = re.search(r'\b' + items_arg + r'\s*=\s*(?:new\s+Vector3\[\]\s*)?\{(.*?)\};', text, re.S)
            t.assertIsNotNone(m, 'cannot find the ItemPositions array ' + items_arg)
            self.items = [src.vec(a) for a in split_args(m.group(1)) if a]
        t.assertEqual(len(self.items), 3, 'three item slots')
        ivec = lambda a: tuple(int(v) for v in re.findall(r'-?\d+', a))
        self.hitbox_size, self.hitbox_offset = ivec(shop[ARG_HITBOX_SIZE]), ivec(shop[ARG_HITBOX_OFFSET])

        # Item depth: the mod's override after DoSetup if it applies one, else Alexandria's forced value.
        self.item_hog = ALEXANDRIA_FORCED_ITEM_HEIGHT_OFF_GROUND
        m = re.search(r'sprite\.HeightOffGround\s*=\s*(ShopItem\w+)\s*;', text)
        if m and m.group(1) in src.f:
            self.item_hog = src.f[m.group(1)]

        # Rectangles (px, frame R).
        self.size = {}
        self.rect = {}
        self.drawn = {}
        for name, p in self.props.items():
            (w, h), bbox, _ = png(name)
            ll = (round(p['offset'][0] * PX - w / 2.0), round(p['offset'][1] * PX))
            self.size[name] = (w, h)
            self.rect[name] = ((ll[0], ll[0] + w), (ll[1], ll[1] + h))
            self.drawn[name] = self._drawn(ll, (w, h), bbox)
        (dw, dh), dbox, _ = png('daifuku_idle_001.png')
        dll = (round(self.npc[0] * PX), round(self.npc[1] * PX))
        self.daifuku_ll = dll
        self.rect['daifuku'] = ((dll[0], dll[0] + dw), (dll[1], dll[1] + dh))
        self.drawn['daifuku'] = self._drawn(dll, (dw, dh), dbox)
        (bw, bh), _, _ = png('blueprint.png')
        self.plaque = (bw, bh)
        self.item_rects = []
        for x, y, _z in self.items:
            cx, cy = x * PX, y * PX
            o = ITEM_OUTLINE_PX
            self.item_rects.append(((cx - bw / 2.0 - o, cx + bw / 2.0 + o), (cy - bh / 2.0 - o, cy + bh / 2.0 + o)))

    @staticmethod
    def _drawn(ll, size, bbox):
        """Opaque bounding box of the sprite, placed (PIL bbox is top-down, the frame is y-up)."""
        w, h = size
        x0, top, x1, bottom = bbox
        return ((ll[0] + x0, ll[0] + x1), (ll[1] + h - bottom, ll[1] + h - top))

    def post_spans(self):
        """The torii's two posts: the leftmost and the rightmost opaque runs of its bottom row, placed."""
        (w, h), _, a = png('torii.png')
        runs = []
        for x in range(w):
            if a[x, h - 1]:
                if runs and runs[-1][1] == x:
                    runs[-1][1] = x + 1
                else:
                    runs.append([x, x + 1])
        left = self.rect['torii.png'][0][0]
        return [(left + runs[0][0], left + runs[0][1]), (left + runs[-1][0], left + runs[-1][1])]


# ---------------------------------------------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------------------------------------------

class ShrineStallGeometryRegressionTests(unittest.TestCase):
    def setUp(self):
        self.s = Scene(self)

    def counter_x(self):
        return self.s.drawn['stall.png'][0]

    # ---- P1: the items stand on the counter ----------------------------------------------------------------

    def test_p1_every_item_lies_on_the_counter_top_in_x(self):
        cx0, cx1 = self.counter_x()
        off = ['item %d x %r' % (i, r[0]) for i, r in enumerate(self.s.item_rects)
               if not (cx0 <= r[0][0] and r[0][1] <= cx1)]
        self.assertEqual(off, [], 'items hang off the counter, which spans x %r px' % ((cx0, cx1),))

    def test_p1_p2_items_bowl_and_daifuku_do_not_overlap(self):
        s = self.s
        rects = [('item %d' % i, r) for i, r in enumerate(s.item_rects)]
        rects += [('bowl', s.drawn['kinsuke_idle_001.png']), ('Daifuku', s.drawn['daifuku'])]
        hits = ['%s %r / %s %r' % (na, a, nb, b)
                for i, (na, a) in enumerate(rects) for nb, b in rects[i + 1:] if overlaps(a, b)]
        self.assertEqual(hits, [], 'overlapping rectangles (px)')

    # ---- P2: the bowl clears Daifuku, the torii frames the counter from behind -----------------------------

    def test_p2_bowl_centre_is_far_enough_from_daifuku(self):
        (bx, by), (dx, dy) = centre(self.s.rect['kinsuke_idle_001.png']), centre(self.s.rect['daifuku'])
        dist = math.hypot(bx - dx, by - dy) / PX
        self.assertGreaterEqual(dist, MIN_BOWL_TO_DAIFUKU_TILES,
                                'bowl centre is %.3f tiles from Daifuku\'s (needs >= %.1f)'
                                % (dist, MIN_BOWL_TO_DAIFUKU_TILES))

    def test_p2_torii_posts_stand_outside_the_counter(self):
        cx0, cx1 = self.counter_x()
        for side, (p0, p1) in zip(('left', 'right'), self.s.post_spans()):
            self.assertTrue(p1 <= cx0 or p0 >= cx1,
                            '%s torii post x [%d, %d) px overlaps the counter [%d, %d)' % (side, p0, p1, cx0, cx1))

    def test_p2_torii_stands_behind_the_counter_not_flat_on_its_ground_line(self):
        torii_y = self.s.rect['torii.png'][1][0]
        counter_y = self.s.rect['stall.png'][1][0]
        self.assertGreater(torii_y, counter_y,
                           'torii ground line (%d px) is not behind the counter\'s (%d px): the two are flat'
                           % (torii_y, counter_y))

    def test_p2_draw_order_is_monotonic_back_to_front(self):
        """Approved mockup, back to front: torii, Daifuku, counter, then the bowl and the items on top."""
        s = self.s
        z = {
            'torii': s.rect['torii.png'][1][0] / PX - s.props['torii.png']['hog'],
            'daifuku': s.rect['daifuku'][1][0] / PX - 0.0,
            'counter': s.rect['stall.png'][1][0] / PX - s.props['stall.png']['hog'],
            'bowl': s.rect['kinsuke_idle_001.png'][1][0] / PX - s.props['kinsuke_idle_001.png']['hog'],
        }
        for i, (_x, y, _z) in enumerate(s.items):
            z['item%d' % i] = (y * PX - s.plaque[1] / 2.0) / PX - s.item_hog
        self.assertGreater(z['torii'], z['daifuku'], 'torii must draw behind Daifuku: %r' % z)
        self.assertGreater(z['daifuku'], z['counter'], 'Daifuku must draw behind the counter: %r' % z)
        for k in ['bowl'] + ['item%d' % i for i in range(len(s.items))]:
            self.assertLess(z[k], z['counter'], k + ' must draw in front of the counter: %r' % z)

    # ---- P3: colliders ------------------------------------------------------------------------------------

    def bodies(self):
        """(prop png, layer, rect px) for every Manual box the placement code attaches, in frame R."""
        self.assertTrue(COLLISION_CS.exists(), 'no ShrineStallCollision.cs: the stall has no colliders')
        ctext = strip_comments(COLLISION_CS.read_text(encoding='utf-8'))
        ints = consts(ctext, 'int')
        layers = dict(re.findall(r'(\w+)\s*=\s*CollisionLayer\.(\w+)\s*;', ctext))
        by_var = dict((p['var'], name) for name, p in self.s.props.items() if p['var'])
        out = []
        for method, var in re.findall(r'ShrineStallCollision\.(Attach\w+)\((\w+)\)', self.s.src.text):
            self.assertIn(var, by_var, '%s is called on %s, which is not a placed prop' % (method, var))
            prop = by_var[var]
            m = re.search(r'static\s+\w+\s+' + method + r'\s*\([^)]*\)\s*\{(.*?)\n        \}', ctext, re.S)
            self.assertIsNotNone(m, 'ShrineStallCollision.cs has no ' + method)
            body = m.group(1)
            ll = (self.s.rect[prop][0][0], self.s.rect[prop][1][0])
            for b in re.finditer(r'\bBox\(', body):
                layer, x, y, w, h = call_args(body, b.end() - 1)
                x, y, w, h = (num_eval(a, ints, integer=True) for a in (x, y, w, h))
                layer = layers.get(layer, layer.replace('CollisionLayer.', ''))
                out.append((prop, layer, ((ll[0] + x, ll[0] + x + w), (ll[1] + y, ll[1] + y + h))))
        return out

    def test_p3_counter_has_a_solid_collider_under_it(self):
        counter = self.s.rect['stall.png']
        boxes = [b for b in self.bodies() if b[0] == 'stall.png' and b[1] in SOLID_LAYERS and overlaps(b[2], counter)]
        self.assertTrue(boxes, 'no solid collider on the counter')

    def test_p3_each_torii_post_has_a_solid_collider(self):
        bodies = [b for b in self.bodies() if b[0] == 'torii.png' and b[1] in SOLID_LAYERS]
        ty = self.s.rect['torii.png'][1][0]
        for side, (p0, p1) in zip(('left', 'right'), self.s.post_spans()):
            post = ((p0, p1), (ty, ty + 1))   # the post's ground contact row
            self.assertTrue(any(overlaps(b[2], post) for b in bodies),
                            'no solid collider under the %s torii post x [%d, %d)' % (side, p0, p1))

    def test_p3_nothing_solid_in_front_of_the_counter_front_edge(self):
        front = self.s.rect['stall.png'][1][0]
        s = self.s
        daifuku = ('daifuku', 'LowObstacle',
                   ((s.daifuku_ll[0] + s.hitbox_offset[0], s.daifuku_ll[0] + s.hitbox_offset[0] + s.hitbox_size[0]),
                    (s.daifuku_ll[1] + s.hitbox_offset[1], s.daifuku_ll[1] + s.hitbox_offset[1] + s.hitbox_size[1])))
        bodies = self.bodies()
        self.assertTrue(bodies, 'no colliders at all')
        for prop, layer, r in bodies + [daifuku]:
            self.assertGreaterEqual(r[1][0], front,
                                    '%s %s box %r reaches in front of the counter front edge y=%d'
                                    % (prop, layer, r, front))


if __name__ == '__main__':
    unittest.main()
