"""Source-level contract tests for ShrineStallCollision.cs (Shrine Stall redesign, problem P3: no collision).

The game is not installed here, so these tests read the C# and re-derive every collider box from the FINAL art
dimensions in .superpowers/sdd/2026-09-18-shrine-stall-redesign/art-spec.md sections 5-7. The geometry is checked
in the COUNTER FRAME: origin = the counter's bottom-centre anchor, x right, y up, px (16 px = 1 tile). Boxes are
half-open pixel ranges [x0, x1) x [y0, y1).
"""
import ast
import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / 'PlutoTheCat' / 'src'
COLLISION = SRC / 'ShrineStallCollision.cs'

# ---- FINAL art numbers, copied from art-spec.md (user-approved 2026-09-18), independent of the C# ----
COUNTER_W, COUNTER_H = 104, 23           # stall.png; anchor (52, 23) bottom-centre at counter frame (0, 0)
COUNTER_TOP_FACE_ROWS = 9                # rows 0-8 top face, rows 9-22 front face (art-spec section 5 / 6)
COUNTER_FRONT_FACE_ROWS = COUNTER_H - COUNTER_TOP_FACE_ROWS   # 14
TORII_W, TORII_H = 136, 56               # torii.png; anchor (68, 56) bottom-centre at counter frame (0, +24)
TORII_ANCHOR_Y = 24
TORII_POST_COLS = ((8, 14), (122, 128))  # inclusive canvas columns, 7 px wide each
TORII_BASE_COLS = ((7, 15), (121, 129))  # inclusive canvas columns of the stone bases, 9 px wide
TORII_BASE_ROWS = 4                      # canvas rows 52-55 = the bottom 4 rows
DAIFUKU_W, DAIFUKU_H = 26, 32            # anchor (13, 32) bottom-centre at counter frame (+21, +21)
DAIFUKU_ANCHOR = (21, 21)
DAIFUKU_HITBOX_OFFSET = (5, 0)           # SetUpFoyerShop args in ShrineStall.cs: LowObstacle 20x18 @ (5,0)
DAIFUKU_HITBOX_SIZE = (20, 18)
BOWL_W, BOWL_H = 12, 14                  # anchor (6, 14) bottom-centre at counter frame (+42, +17)
BOWL_ANCHOR = (42, 17)
ITEM_SLOT_ANCHORS_X = (-40, -21, -2)     # item bottom-centres at y = +16, slot boxes 16x16
ITEM_SLOT_Y = 16
APPROACH_DEPTH = 32                      # the strip the player walks in to reach the counter: 2 tiles deep

COUNTER_LL = (-COUNTER_W // 2, 0)                     # (-52, 0): the counter prop's transform (sprite lower-left)
TORII_LL = (-TORII_W // 2, TORII_ANCHOR_Y)            # (-68, 24): the torii prop's transform
DAIFUKU_LL = (DAIFUKU_ANCHOR[0] - DAIFUKU_W // 2, DAIFUKU_ANCHOR[1])   # (8, 21): his transform


def int_expr(expr, names):
    """Evaluates a C# integer constant expression (+ - * /, parentheses, names) without eval().
    C# int division truncates toward zero; the constants only divide even numbers, and this checks that."""
    ops = {ast.Add: lambda a, b: a + b, ast.Sub: lambda a, b: a - b, ast.Mult: lambda a, b: a * b}

    def walk(node):
        if isinstance(node, ast.Expression):
            return walk(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, int):
            return node.value
        if isinstance(node, ast.Name):
            return names[node.id]
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -walk(node.operand)
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            a, b = walk(node.left), walk(node.right)
            assert a % b == 0, 'inexact integer division in a collider constant'
            return a // b
        if isinstance(node, ast.BinOp) and type(node.op) in ops:
            return ops[type(node.op)](walk(node.left), walk(node.right))
        raise ValueError('unsupported constant expression: ' + expr)

    return walk(ast.parse(expr.strip(), mode='eval'))


def overlaps(a, b):
    """Half-open box overlap: ((x0, x1), (y0, y1))."""
    return a[0][0] < b[0][1] and b[0][0] < a[0][1] and a[1][0] < b[1][1] and b[1][0] < a[1][1]


def box(ll, ox, oy, w, h):
    return ((ll[0] + ox, ll[0] + ox + w), (ll[1] + oy, ll[1] + oy + h))


class ShrineStallCollisionSourceTests(unittest.TestCase):
    def source(self):
        self.assertTrue(COLLISION.exists(), 'ShrineStallCollision.cs is not implemented')
        return COLLISION.read_text(encoding='utf-8')

    def consts(self):
        """Evaluates every `const int NAME = EXPR;` in declaration order (integer arithmetic only)."""
        text = self.source()
        values = {}
        for name, expr in re.findall(r'const\s+int\s+(\w+)\s*=\s*([^;]+);', text):
            values[name] = int_expr(expr, values)
        return values

    def test_entry_points_exist(self):
        text = self.source()
        self.assertIn('namespace PlutoTheCat', text)
        self.assertRegex(text, r'internal\s+static\s+class\s+ShrineStallCollision')
        for sig in (
            r'static\s+\w+\s+AttachCounterBody\(\s*GameObject\s+\w+\s*\)',
            r'static\s+\w+\s+AttachToriiBody\(\s*GameObject\s+\w+\s*\)',
            r'static\s+\w+\s+AttachBackBlocker\(\s*GameObject\s+\w+\s*\)',
            r'static\s+\w+\s+ReinitializeShopBodies\(\s*GameObject\s+\w+\s*\)',
            r'static\s+void\s+LogBodies\(',
        ):
            self.assertRegex(text, sig)

    def test_house_collider_idiom(self):
        text = self.source()
        for needle in (
            'AddComponent<SpeculativeRigidbody>()',
            'PixelCollider.PixelColliderGeneration.Manual',
            'CollideWithTileMap = false',
            'CollideWithOthers = true',
            'IsTrigger = false',
            'Reinitialize()',
            'RegisterOverlappingGhostCollisionExceptions',
        ):
            self.assertIn(needle, text, 'ShrineStallCollision.cs missing ' + needle)
        # Tk2dPolygon would ignore the Manual box and trace the whole drawn sprite, full height.
        self.assertNotIn('Tk2dPolygon', text)
        self.assertNotIn('GenerateOrAddToRigidBody', text)

    def test_layers(self):
        text = self.source()
        self.assertRegex(text, r'CounterLayer\s*=\s*CollisionLayer\.HighObstacle')
        self.assertRegex(text, r'PostLayer\s*=\s*CollisionLayer\.HighObstacle')
        self.assertRegex(text, r'BackBlockerLayer\s*=\s*CollisionLayer\.PlayerBlocker')

    def test_bowl_gets_no_floating_collider(self):
        text = self.source()
        self.assertNotRegex(text, r'static\s+\w+\s+Attach\w*(Bowl|Kinsuke)\w*\(')
        self.assertIn('bowl', text.lower())   # the comment that says the counter body covers it

    def test_reinitialize_walks_every_child_body(self):
        text = self.source()
        self.assertIn('GetComponentsInChildren<SpeculativeRigidbody>(true)', text)
        start = text.find('ReinitializeShopBodies(')
        self.assertIn('.Reinitialize()', text[start:start + 2500])

    def test_diagnostics_settle_the_unknowns(self):
        text = self.source()
        for needle in (
            'UnitBottomLeft', 'UnitDimensions', 'CollisionLayer', 'renderer.bounds',
            'GetDistanceToPoint', 'GetOverrideMaxDistance()', 'speakPoint',
            'CustomShopItemController', 'TalkDoerLite', 'PrimaryPlayer', 'STALE',
        ):
            self.assertTrue(needle in text, 'LogBodies is missing ' + needle)
        self.assertIn('shrine stall collision:', text)   # one grep prefix for the tester

    def test_does_not_touch_the_placement_file(self):
        # The peer owns ShrineStall.cs; this file must be self-contained entry points only.
        text = self.source()
        self.assertIsNone(re.search(r'\bShrineStall\.(?!cs\b)\w', text),
                          'ShrineStallCollision must not call into ShrineStall (the controller calls us)')

    def test_art_constants_match_the_final_spec(self):
        c = self.consts()
        expected = {
            'CounterWidthPx': COUNTER_W, 'CounterHeightPx': COUNTER_H, 'CounterTopFaceRows': COUNTER_TOP_FACE_ROWS,
            'ToriiWidthPx': TORII_W, 'ToriiHeightPx': TORII_H, 'ToriiAnchorAboveCounterPx': TORII_ANCHOR_Y,
            'ToriiLeftPostCol': TORII_POST_COLS[0][0], 'ToriiRightPostCol': TORII_POST_COLS[1][0],
            'ToriiPostWidthPx': TORII_POST_COLS[0][1] - TORII_POST_COLS[0][0] + 1,
            'ToriiLeftBaseCol': TORII_BASE_COLS[0][0], 'ToriiRightBaseCol': TORII_BASE_COLS[1][0],
            'ToriiBaseWidthPx': TORII_BASE_COLS[0][1] - TORII_BASE_COLS[0][0] + 1, 'ToriiBaseRows': TORII_BASE_ROWS,
            'DaifukuWidthPx': DAIFUKU_W, 'DaifukuHeightPx': DAIFUKU_H,
            'DaifukuAnchorXPx': DAIFUKU_ANCHOR[0], 'DaifukuAnchorYPx': DAIFUKU_ANCHOR[1],
            'DaifukuHitboxOffsetXPx': DAIFUKU_HITBOX_OFFSET[0], 'DaifukuHitboxOffsetYPx': DAIFUKU_HITBOX_OFFSET[1],
            'DaifukuHitboxWidthPx': DAIFUKU_HITBOX_SIZE[0], 'DaifukuHitboxHeightPx': DAIFUKU_HITBOX_SIZE[1],
            'BowlWidthPx': BOWL_W, 'BowlHeightPx': BOWL_H, 'BowlAnchorXPx': BOWL_ANCHOR[0], 'BowlAnchorYPx': BOWL_ANCHOR[1],
        }
        for name, value in expected.items():
            self.assertIn(name, c, 'missing const ' + name)
            self.assertEqual(c[name], value, name)

    def derived_boxes(self):
        c = self.consts()
        counter = box(COUNTER_LL, c['CounterBoxOffsetXPx'], c['CounterBoxOffsetYPx'],
                      c['CounterBoxWidthPx'], c['CounterBoxHeightPx'])
        left_post = box(TORII_LL, c['LeftPostBoxOffsetXPx'], c['PostBoxOffsetYPx'],
                        c['PostBoxWidthPx'], c['PostBoxHeightPx'])
        right_post = box(TORII_LL, c['RightPostBoxOffsetXPx'], c['PostBoxOffsetYPx'],
                         c['PostBoxWidthPx'], c['PostBoxHeightPx'])
        blocker = box(COUNTER_LL, c['BackBlockerOffsetXPx'], c['BackBlockerOffsetYPx'],
                      c['BackBlockerWidthPx'], c['BackBlockerHeightPx'])
        daifuku = box(DAIFUKU_LL, DAIFUKU_HITBOX_OFFSET[0], DAIFUKU_HITBOX_OFFSET[1], *DAIFUKU_HITBOX_SIZE)
        return counter, left_post, right_post, blocker, daifuku

    def test_counter_box_spans_the_width_within_the_bottom_rows(self):
        counter = self.derived_boxes()[0]
        self.assertEqual(counter[0], (-COUNTER_W // 2, COUNTER_W // 2), 'counter box must span the whole counter')
        self.assertEqual(counter[1][0], 0, 'counter box must sit flush on the ground line (no gap in front)')
        self.assertLessEqual(counter[1][1], COUNTER_FRONT_FACE_ROWS,
                             'counter box must stay within the front-face (bottom) rows, not the drawn top')
        self.assertEqual(counter[1][1], COUNTER_TOP_FACE_ROWS, 'footprint depth = the top face depth (rows 0-8)')

    def test_post_boxes_sit_under_the_posts(self):
        _, left_post, right_post, _, _ = self.derived_boxes()
        for post_box, post_cols, base_cols in ((left_post, TORII_POST_COLS[0], TORII_BASE_COLS[0]),
                                               (right_post, TORII_POST_COLS[1], TORII_BASE_COLS[1])):
            post_x = (TORII_LL[0] + post_cols[0], TORII_LL[0] + post_cols[1] + 1)
            base_x = (TORII_LL[0] + base_cols[0], TORII_LL[0] + base_cols[1] + 1)
            self.assertLessEqual(post_box[0][0], post_x[0], 'post box must cover the post')
            self.assertGreaterEqual(post_box[0][1], post_x[1], 'post box must cover the post')
            self.assertEqual(post_box[0], base_x, 'post box = the stone base footprint')
            self.assertEqual(post_box[1], (TORII_ANCHOR_Y, TORII_ANCHOR_Y + TORII_BASE_ROWS),
                             'post box = the stone base rows only, not the drawn post')
        self.assertEqual(left_post[0], (-61, -52))
        self.assertEqual(right_post[0], (53, 62))

    def test_nothing_blocks_the_approach_strip(self):
        approach = ((-COUNTER_W // 2, COUNTER_W // 2), (-APPROACH_DEPTH, 0))
        for name, b in zip(('counter', 'left post', 'right post', 'back blocker', 'Daifuku'), self.derived_boxes()):
            self.assertFalse(overlaps(b, approach), name + ' box intrudes on the approach strip ' + repr(b))

    def test_daifuku_box_stays_behind_the_counter(self):
        counter, _, _, _, daifuku = self.derived_boxes()
        self.assertGreaterEqual(daifuku[1][0], counter[1][1], 'Daifuku box must start behind the counter box')
        self.assertFalse(overlaps(daifuku, counter))
        self.assertEqual(daifuku, ((13, 33), (21, 39)))

    def test_back_blocker_seals_the_gap_behind_the_counter(self):
        counter, left_post, right_post, blocker, _ = self.derived_boxes()
        self.assertEqual(blocker[1][0], counter[1][1], 'no walkable seam between counter footprint and blocker')
        self.assertLessEqual(blocker[0][0], left_post[0][0], 'blocker must reach the left post outer edge')
        self.assertGreaterEqual(blocker[0][1], right_post[0][1], 'blocker must reach the right post outer edge')
        self.assertGreaterEqual(blocker[1][1], left_post[1][1], 'blocker must reach the back of the post bases')
        self.assertEqual(blocker, ((-61, 62), (9, 28)))

    def test_bowl_and_items_rest_on_the_counter_body(self):
        counter = self.derived_boxes()[0]
        bowl_x = (BOWL_ANCHOR[0] - BOWL_W // 2, BOWL_ANCHOR[0] + BOWL_W // 2)
        self.assertTrue(counter[0][0] <= bowl_x[0] and bowl_x[1] <= counter[0][1],
                        'bowl must sit inside the counter body width, so it needs no collider of its own')
        for x in ITEM_SLOT_ANCHORS_X:
            self.assertTrue(counter[0][0] <= x - 8 and x + 8 <= counter[0][1], 'item slot off the counter')


if __name__ == '__main__':
    unittest.main()
