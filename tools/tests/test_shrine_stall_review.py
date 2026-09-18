"""Source-contract tests for the adversarial review of the Shrine Stall redesign (after 34ba1c3).

  S1  Daifuku's talk reach: a solid counter holds the player ~1.06-1.19 tiles from his body, past the game's
      default reach (INFERRED ~1 tile), so the template's TalkDoerLite gets an overrideInteractionRadius.
  S2  the stock probe is attached before any diagnostic, and each diagnostic is caught on its own.
  S3  the stock probe waits for DoSetup's own mark (m_itemControllers non-null), with a logged give-up.
  M1  bodies are re-registered only after a real move, and only when a PhysicsEngine exists.
  M3  the stall position is snapped to the 1/16-tile grid, in memory only.
  M4  pluto_stall here / <x> <y> refuses to move outside the Breach.
  M5  the reach log names the interactable's own distance as the reach, not the speech bubble anchor.

The game is not installed here, so like the other test_shrine_stall*.py files these read the C#. Comments are
stripped before code checks, so a comment that merely mentions a fix never satisfies its test.
"""
import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / 'PlutoTheCat' / 'src'
STALL_CS = SRC / 'ShrineStall.cs'
COLLISION_CS = SRC / 'ShrineStallCollision.cs'

PX = 16.0
# Counter frame (art-spec section 5): Daifuku's body (Alexandria's 20x18 LowObstacle at (5, 0) from his lower-left
# (8, 21)) starts 21 px behind the counter's front line; a player touching the counter has his centre ~0.12-0.25
# tiles above that line (review S1).
DAIFUKU_BODY_BOTTOM_TILES = 21 / PX
PLAYER_CENTRE_ABOVE_FRONT_TILES = (0.12, 0.25)
ASSUMED_DEFAULT_REACH_TILES = 1.0


def code_only(text):
    """Drops // comments (and /// doc comments) outside string literals."""
    out = []
    for line in text.splitlines():
        in_string = False
        cut = len(line)
        i = 0
        while i < len(line):
            ch = line[i]
            if ch == '\\' and in_string:
                i += 2
                continue
            if ch == '"':
                in_string = not in_string
            elif not in_string and line.startswith('//', i):
                cut = i
                break
            i += 1
        out.append(line[:cut])
    return '\n'.join(out)


def method_body(text, signature_regex):
    """The brace-matched body of the first method whose signature matches."""
    m = re.search(signature_regex, text)
    if m is None:
        return None
    start = text.index('{', m.end())
    depth = 0
    for i in range(start, len(text)):
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                return text[start + 1:i]
    raise AssertionError('unbalanced braces after ' + signature_regex)


class ShrineStallReviewTests(unittest.TestCase):
    def stall(self):
        return code_only(STALL_CS.read_text(encoding='utf-8'))

    def collision(self):
        return code_only(COLLISION_CS.read_text(encoding='utf-8'))

    def body(self, text, signature_regex):
        b = method_body(text, signature_regex)
        self.assertIsNotNone(b, 'missing method ' + signature_regex)
        return b

    # ---- S1: Daifuku's reach ----------------------------------------------------------------------------------

    def test_s1_daifuku_talk_radius_reaches_past_the_counter(self):
        stall = self.stall()
        m = re.search(r'const\s+float\s+DaifukuTalkRadiusTiles\s*=\s*([0-9.]+)f\s*;', stall)
        self.assertIsNotNone(m, 'ShrineStall.cs needs a named DaifukuTalkRadiusTiles constant (in tiles)')
        radius = float(m.group(1))
        nearest = DAIFUKU_BODY_BOTTOM_TILES - PLAYER_CENTRE_ABOVE_FRONT_TILES[0]   # worst case, ~1.19
        self.assertGreater(nearest, ASSUMED_DEFAULT_REACH_TILES,
                           'premise: the default reach does not get past the counter')
        self.assertGreaterEqual(radius, nearest + 0.25,
                                'the radius must clear the worst-case counter-front distance with margin')
        self.assertLessEqual(radius, 2.0, 'a radius past 2 tiles would make Daifuku talkable from the walkway')

    def test_s1_radius_is_set_on_the_template_right_after_set_up_foyer_shop(self):
        stall = self.stall()
        init = self.body(stall, r'public static void Init\(\)')
        setup = init.index('ShopAPI.SetUpFoyerShop(')
        null_check = init.index('if (shop == null)', setup)
        extend = init.find('ExtendDaifukuReach(shop);')
        self.assertNotEqual(extend, -1, 'Init must set Daifuku\'s reach on the shop SetUpFoyerShop returned')
        self.assertLess(null_check, extend)
        self.assertLess(extend, init.index('PlaceIfFoyerAlreadyUp();'),
                        'the reach goes on the TEMPLATE before any clone is placed, so every clone inherits it')
        extend_body = self.body(stall, r'private static void ExtendDaifukuReach\(GameObject shop\)')
        self.assertIn('GetComponentInChildren<TalkDoerLite>(true)', extend_body)
        self.assertRegex(extend_body, r'\.overrideInteractionRadius\s*=\s*DaifukuTalkRadiusTiles\s*;')
        self.assertIn('Plugin.Log(', extend_body)

    def test_s1_items_reach_is_reported_for_the_tester(self):
        coll = self.collision()
        reach = self.body(coll, r'private static void LogReach\(GameObject liveShop, GameObject counterProp\)')
        self.assertRegex(reach, r'LogReachTo\("item " \+ i[^;]*item\.GetDistanceToPoint, effective[,)]',
                         'each item\'s reach must be measured by the item itself')
        self.assertRegex(reach, r'float\s+effective\s*=\s*item\.GetOverrideMaxDistance\(\)\s*;',
                         'the max is what the item itself returns (through the 2.20.9 reach patch)')
        to = self.body(coll, r'private static void LogReachTo\(')
        self.assertIn('REACH', to)
        self.assertIn('OUT OF REACH', to, 'the reach line must give the tester a verdict, not just a number')
        self.assertIn('AssumedDefaultReachTiles', to, 'with no override, the verdict uses the assumed default reach')

    # ---- S2: probe before diagnostics, diagnostics caught -------------------------------------------------------

    def test_s2_probe_attached_before_diagnostics_and_diagnostics_caught(self):
        place = self.body(self.stall(), r'private static void PlaceBackdropProps\(\)')
        depth = place.index('RefreshLiveShopDepth(FindLiveShop(), "placement");')
        probe = place.index('AttachStockProbe();')
        diag = place.index('LogShopDiagnostics();')
        bodies = place.index('ShrineStallCollision.LogBodies(')
        self.assertLess(depth, probe, 'the probe goes on straight after the placement depth refresh')
        self.assertLess(probe, diag, 'a throwing diagnostic must not stop the probe being attached')
        self.assertLess(probe, bodies)
        for call in ('LogShopDiagnostics();', 'ShrineStallCollision.LogBodies('):
            at = place.index(call)
            before = place[:at]
            self.assertTrue(before.rstrip().endswith('{') and before.rstrip()[:-1].rstrip().endswith('try'),
                            call + ' must be the first statement of its own try block')
            after = place[at:]
            catch = re.search(r'\}\s*catch\s*\(\s*Exception\s+(\w+)\s*\)\s*\{([^}]*)\}', after)
            self.assertIsNotNone(catch, call + ' needs a catch (Exception e)')
            self.assertIn('Plugin.Log(', catch.group(2), call + '\'s catch must log the exception')
            self.assertIn(catch.group(1), catch.group(2), call + '\'s catch must log the exception itself')

    # ---- S3: probe waits for DoSetup ----------------------------------------------------------------------------

    def test_s3_stock_probe_waits_for_do_setup_not_a_fixed_delay(self):
        stall = self.stall()
        probe = stall[stall.index('class StockProbe'):]
        probe = probe[:probe.index('class PropFlipbook')]
        update = self.body(probe, r'private void Update\(\)')
        self.assertNotIn('GraceSeconds', probe, 'a fixed grace period after character select misses a late DoSetup')
        self.assertRegex(update, r'ReadField\(\w+, "m_itemControllers"\)\s*!=\s*null',
                         'the probe must wait for DoSetup\'s own mark, m_itemControllers non-null')
        gate = re.search(r'bool (\w+) = [^;]*"m_itemControllers"[^;]*;', update)
        self.assertIsNotNone(gate)
        branch = update[update.index('if (' + gate.group(1) + ')'):]
        self.assertLess(branch.index('RefreshLiveShopDepth(gameObject'), branch.index('else if'),
                        'the item depth is applied inside the stocked branch')
        self.assertLess(branch.index('LogStock(gameObject'), branch.index('else if'))
        timeout = branch[branch.index('else if'):]
        self.assertIn('GiveUpSeconds', timeout)
        self.assertIn('gave up', timeout, 'a give-up must be logged, never silent')
        self.assertRegex(probe, r'const float GiveUpSeconds = \d+f;')

    # ---- M1: reinitialise only after a real move, with a PhysicsEngine -----------------------------------------

    def test_m1_reconcile_reports_whether_it_moved(self):
        stall = self.stall()
        reconcile = self.body(stall, r'private static bool ReconcileLiveShopPosition\(\)')
        self.assertIn('return false;', reconcile)
        move = reconcile.index('live.transform.position = want;')
        self.assertLess(move, reconcile.index('return true;'), 'true only once it has moved the clone')

    def test_m1_shop_bodies_reinitialised_only_after_a_move(self):
        stall = self.stall()
        place = self.body(stall, r'private static void PlaceBackdropProps\(\)')
        m = re.search(r'bool (\w+) = ReconcileLiveShopPosition\(\);', place)
        self.assertIsNotNone(m, 'PlaceBackdropProps must use the reconcile result')
        call = place.index('ShrineStallCollision.ReinitializeShopBodies(FindLiveShop())')
        guard = re.search(r'if \((\w+)\)\s*$', place[:call])
        self.assertIsNotNone(guard, 'ReinitializeShopBodies must be behind an if (moved) guard')
        moved = re.search(r'bool ' + guard.group(1) + r' = ([^;]+);', place)
        self.assertIsNotNone(moved)
        self.assertIn(m.group(1), moved.group(1), 'a reconcile that moved the clone counts as a move')
        self.assertIn('_liveShopMovedByCommand', moved.group(1), 'a pluto_stall move counts as a move')
        self.assertRegex(place, r'_liveShopMovedByCommand = false;', 'the move flag is consumed')
        move_stall = self.body(stall, r'private static void MoveStall\(Vector3 newPosition\)')
        live_at = move_stall.index('if (live != null)')
        live = move_stall[live_at:move_stall.index('else', live_at)]
        self.assertIn('_liveShopMovedByCommand = true;', live, 'MoveStall flags the move only when it moved the clone')

    def test_m1_every_reinitialize_is_guarded_by_physics_engine(self):
        coll = self.collision()
        reinit = self.body(coll, r'internal static int ReinitializeShopBodies\(GameObject liveShop\)')
        self.assertLess(reinit.index('PhysicsEngine.HasInstance'), reinit.index('.Reinitialize()'))
        add = self.body(coll, r'private static SpeculativeRigidbody AddColliders\(')
        guard = add.index('if (PhysicsEngine.HasInstance)')
        self.assertLess(guard, add.index('body.Reinitialize();'))
        self.assertEqual(add.count('.Reinitialize()'), 1)

    # ---- M3: snap to the pixel grid, in memory only -------------------------------------------------------------

    def test_m3_snap_rounds_to_sixteenths(self):
        stall = self.stall()
        self.assertRegex(stall, r'const float PixelsPerTile = 16f;')
        snap = self.body(stall, r'private static Vector3 SnapToPixelGrid\(Vector3 position\)')
        for axis in ('x', 'y'):
            self.assertIn('Mathf.Round(position.' + axis + ' * PixelsPerTile) / PixelsPerTile', snap)
        # The shipped default is the case the review found: 61.063 is 977.008 px, off the grid.
        self.assertNotEqual(61.063 * PX, round(61.063 * PX))
        self.assertEqual(round(61.063 * PX) / PX, 61.0625)

    def test_m3_snapped_before_set_up_foyer_shop_and_on_every_move_in_memory_only(self):
        stall = self.stall()
        init = self.body(stall, r'public static void Init\(\)')
        self.assertLess(init.index('SnapStallPositionToPixelGrid('), init.index('ShopAPI.SetUpFoyerShop('))
        move = self.body(stall, r'private static void MoveStall\(Vector3 newPosition\)')
        snap_at = move.index('SnapStallPositionToPixelGrid(')
        self.assertLess(snap_at, move.index('SetBreachOffset(_shopObject, newPosition);'))
        self.assertRegex(move[snap_at:], r'^SnapStallPositionToPixelGrid\("move"\);\s*newPosition = PlutoConfig\.StallPosition;',
                         'MoveStall must continue with the snapped position')
        snapper = self.body(stall, r'private static void SnapStallPositionToPixelGrid\(string when\)')
        self.assertIn('PlutoConfig.StallPosition = snapped;', snapper)
        self.assertNotIn('PersistStallPosition', snapper, 'the user\'s config text is never rewritten by a snap')
        self.assertNotIn('.Value', snapper)
        self.assertIn('Plugin.Log(', snapper, 'the snapped value is logged')

    # ---- M4: refuse to move outside the Breach -----------------------------------------------------------------

    def test_m4_move_refused_outside_the_breach(self):
        move = self.body(self.stall(), r'private static void MoveStall\(Vector3 newPosition\)')
        guard = re.search(r'if \(UnityEngine\.Object\.FindObjectOfType<MainMenuFoyerController>\(\) == null\)\s*\{([^}]*)\}', move)
        self.assertIsNotNone(guard, 'MoveStall must check for the Breach (MainMenuFoyerController) first')
        self.assertIn('Plugin.Log(', guard.group(1))
        self.assertIn('return;', guard.group(1))
        self.assertLess(guard.start(), move.index('PlutoConfig.StallPosition = newPosition;'),
                        'nothing may change before the refusal')

    # ---- M5: the reach is the interactable's own distance ------------------------------------------------------

    def test_m5_reach_log_does_not_call_the_speech_point_the_reach(self):
        coll = self.collision()
        reach = self.body(coll, r'private static void LogReach\(GameObject liveShop, GameObject counterProp\)')
        self.assertNotIn('talk point', reach.lower(), 'the speech point over Daifuku\'s head is not a talk point')
        self.assertRegex(reach, r'LogReachTo\("Daifuku[^;]*talker\.GetDistanceToPoint, talker\.GetOverrideMaxDistance\(\)[,)]')
        self.assertIn('speech bubble anchor', reach, 'the straight-line value must be named for what it is')
        self.assertIn('not the reach', reach)
        to = self.body(coll, r'private static void LogReachTo\(')
        self.assertNotIn('Vector2.Distance', to, 'the REACH line reports only the interactable\'s own distance')
        self.assertIn('measure(', to)


if __name__ == '__main__':
    unittest.main()
