"""Source-contract tests for the two failures of the 2.20.8 in-game test, and the headless reach probe (2.20.9).

  FIX 1  the back fill stayed a 0x0 box: AttachBackBlocker appended a PlayerBlocker to the counter's body after
         AttachCounterBody had already built (and possibly reinitialised) it. The counter body is now built in ONE
         AddColliders call holding both boxes, and AddColliders never appends to an existing body.
  FIX 2  every item measured 1.125 tiles from the counter front against the game's default reach (INFERRED ~1),
         because Alexandria's CustomShopItemController.GetOverrideMaxDistance returns -1 (IL: ldc.r4 -1). A Harmony
         postfix raises it to ShrineItemReachTiles for items of OUR shop only.
  FIX 3  `pluto_stall stand <daifuku|0|1|2>` warps the player to the counter front and reads back which
         interactable the GAME selected (PlayerController.m_lastInteractionTarget), so no human has to stand there.

Like the other test_shrine_stall*.py files these read the C#; comments are stripped before code checks, so a comment
that merely mentions a fix never satisfies its test.
"""
import pathlib
import re
import unittest

from test_shrine_stall_review import code_only, method_body


ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / 'PlutoTheCat' / 'src'
STALL_CS = SRC / 'ShrineStall.cs'
COLLISION_CS = SRC / 'ShrineStallCollision.cs'
REACH_CS = SRC / 'ShrineStallReach.cs'
PLUGIN_CS = SRC / 'Plugin.cs'

PX = 16.0
# 2.20.8 log: every plaque measured 1.125 tiles from the counter front; Daifuku 1.313 against his 1.75 override.
ITEM_DISTANCE_FROM_FRONT_TILES = 1.125
DAIFUKU_REACH_TILES = 1.75


def read(path):
    return code_only(path.read_text(encoding='utf-8')) if path.exists() else ''


class Fix1BackBlockerTests(unittest.TestCase):
    """The back fill must be part of the counter body from the start, never appended to a live body."""

    def collision(self):
        return read(COLLISION_CS)

    def body(self, text, sig):
        b = method_body(text, sig)
        self.assertIsNotNone(b, 'missing method ' + sig)
        return b

    def test_counter_body_holds_both_boxes_in_one_add_colliders_call(self):
        attach = self.body(self.collision(), r'static\s+\w+\s+AttachCounterBody\(\s*GameObject\s+\w+\s*\)')
        calls = re.findall(r'AddColliders\(', attach)
        self.assertEqual(len(calls), 1, 'AttachCounterBody must build the whole counter body in ONE AddColliders call')
        call = attach[attach.index('AddColliders('):]
        self.assertRegex(call, r'Box\(CounterLayer,\s*CounterBoxOffsetXPx,\s*CounterBoxOffsetYPx,\s*CounterBoxWidthPx,\s*CounterBoxHeightPx\)')
        self.assertRegex(call, r'Box\(BackBlockerLayer,\s*BackBlockerOffsetXPx,\s*BackBlockerOffsetYPx,\s*BackBlockerWidthPx,\s*BackBlockerHeightPx\)')

    def test_no_separate_back_blocker_append_path(self):
        coll = self.collision()
        self.assertNotRegex(coll, r'static\s+\w+\s+AttachBackBlocker\(',
                            'the separate back-fill entry point appended to an initialised body; fold it into AttachCounterBody')
        self.assertEqual(len(re.findall(r'Box\(BackBlockerLayer', coll)), 1, 'the back fill box is built in one place only')
        self.assertNotRegex(read(STALL_CS), r'AttachBackBlocker\(', 'ShrineStall.cs must not call the removed entry point')

    def test_add_colliders_never_appends_to_an_existing_body(self):
        add = self.body(self.collision(), r'private static SpeculativeRigidbody AddColliders\(')
        self.assertNotIn('AddRange', add, 'appending to an existing body left the back fill at 0x0 in game')
        existing = add.index('GetComponent<SpeculativeRigidbody>()')
        guard = add[existing:existing + 900]
        self.assertRegex(guard, r'if\s*\(\s*body\s*!=\s*null\s*\)', 'an existing body must be refused, not extended')
        self.assertIn('return body;', guard)
        self.assertIn('Plugin.Log(', guard, 'a refused append must be logged')
        self.assertRegex(add, r'PixelColliders\s*=\s*new\s+List<PixelCollider>\(\s*colliders\s*\)',
                         'the fresh body gets all its colliders before it is ever initialised')
        self.assertLess(add.index('new List<PixelCollider>(colliders)'), add.index('Reinitialize()'))

    def test_log_bodies_says_why_the_bowl_has_no_body(self):
        coll = self.collision()
        self.assertRegex(coll, r'static\s+void\s+LogBodies\(\s*GameObject\s+liveShop,\s*GameObject\s+counterProp,'
                               r'\s*GameObject\s+toriiProp,\s*GameObject\s+bowlProp\s*\)')
        log = self.body(coll, r'static\s+void\s+LogBodies\(')
        self.assertIn('bowlProp', log)
        self.assertNotIn('"\' has NO body (walk-through)"', coll, 'the bowl is not walk-through: say where it sits')
        self.assertIn('back fill', coll.split('static void LogBodies(')[1].lower()
                      if 'static void LogBodies(' in coll else '', 'the bowl line must name the back fill')
        self.assertIn('ShrineStallCollision.LogBodies(FindLiveShop(), _counterProp, _toriiProp, _kinsukeProp)', read(STALL_CS))

    def test_bowl_footprint_lies_inside_the_back_fill(self):
        consts = {}
        from test_shrine_stall_collision import int_expr
        for name, expr in re.findall(r'const\s+int\s+(\w+)\s*=\s*([^;]+);', self.collision()):
            consts[name] = int_expr(expr, consts)
        left = -consts['CounterWidthPx'] // 2 + consts['BackBlockerOffsetXPx']
        fill_x = (left, left + consts['BackBlockerWidthPx'])
        fill_y = (consts['BackBlockerOffsetYPx'], consts['BackBlockerOffsetYPx'] + consts['BackBlockerHeightPx'])
        self.assertEqual((fill_x, fill_y), ((-61, 62), (9, 28)), 'box numbers must not change')
        bowl_x = (consts['BowlAnchorXPx'] - consts['BowlWidthPx'] // 2, consts['BowlAnchorXPx'] + consts['BowlWidthPx'] // 2)
        self.assertTrue(fill_x[0] <= bowl_x[0] and bowl_x[1] <= fill_x[1])
        self.assertTrue(fill_y[0] <= consts['BowlAnchorYPx'] < fill_y[1], 'the bowl stands on floor the back fill makes solid')

    def test_wiring_attaches_the_counter_once(self):
        m = re.search(r'private static void PlaceBackdropProps\(\)(.*?)\n        \}\n', read(STALL_CS), re.S)
        self.assertIsNotNone(m)
        self.assertEqual(len(re.findall(r'ShrineStallCollision\.AttachCounterBody\(_counterProp\)', m.group(1))), 1)


class Fix2ItemReachTests(unittest.TestCase):
    """Alexandria's items never override the game's reach; our shop's items get ShrineItemReachTiles via Harmony."""

    def reach(self):
        text = read(REACH_CS)
        self.assertTrue(text, 'PlutoTheCat/src/ShrineStallReach.cs is not implemented')
        return text

    def test_named_reach_constant_covers_the_measured_distance(self):
        m = re.search(r'const\s+float\s+ShrineItemReachTiles\s*=\s*([0-9.]+)f\s*;', self.reach())
        self.assertIsNotNone(m, 'a named ShrineItemReachTiles constant (tiles) is required')
        value = float(m.group(1))
        self.assertEqual(value, 1.5)
        self.assertGreater(value, ITEM_DISTANCE_FROM_FRONT_TILES, 'must cover the 1.125 tiles measured in game')
        self.assertLess(value, DAIFUKU_REACH_TILES, 'must stay below Daifuku\'s reach so the nearer plaque wins')

    def test_postfix_targets_the_declared_alexandria_method(self):
        text = self.reach()
        self.assertIn('using HarmonyLib;', read(REACH_CS.parent / 'ShrineStallReach.cs').replace('\r', ''))
        self.assertRegex(text, r'AccessTools\.DeclaredMethod\(\s*typeof\(CustomShopItemController\),\s*"GetOverrideMaxDistance"\s*\)',
                         'patch CustomShopItemController\'s own (newslot virtual final) GetOverrideMaxDistance')
        self.assertRegex(text, r'new\s+Harmony\(\s*Plugin\.GUID\s*\+\s*"[^"]+"\s*\)')
        self.assertRegex(text, r'\.Patch\([^;]*postfix:\s*new\s+HarmonyMethod\(\s*typeof\(ShrineStallReach\),\s*"(\w+)"\s*\)')

    def test_postfix_only_touches_our_shop(self):
        text = self.reach()
        name = re.search(r'postfix:\s*new\s+HarmonyMethod\(\s*typeof\(ShrineStallReach\),\s*"(\w+)"', text).group(1)
        post = method_body(text, r'static\s+void\s+' + name + r'\(\s*CustomShopItemController\s+__instance,\s*ref\s+float\s+__result\s*\)')
        self.assertIsNotNone(post, 'postfix must take (CustomShopItemController __instance, ref float __result)')
        self.assertRegex(post, r'if\s*\(\s*IsOurShopItem\(__instance\)\s*\)\s*__result\s*=\s*ShrineItemReachTiles\s*;')
        self.assertEqual(len(re.findall(r'__result\s*=', post)), 1, '__result is set in one guarded place only')
        self.assertIn('catch', post, 'a throwing postfix must never break another shop\'s interaction')
        ours = method_body(text, r'static\s+bool\s+IsOurShopItem\(\s*CustomShopItemController\s+\w+\s*\)')
        self.assertIsNotNone(ours)
        self.assertIn('"m_baseParentShop"', text, 'the item\'s own shop link (set by Initialize(i, parent), IL_0003)')
        self.assertIn('.parent', ours, 'fall back to the transform parent chain')
        self.assertIn('ShrineStall.ShopPrefix', ours)
        self.assertIn('StartsWith(', ours)
        self.assertRegex(read(STALL_CS), r'internal\s+const\s+string\s+ShopPrefix\s*=\s*"pluto_shrine_stall"\s*;')

    def test_patch_registered_once_at_plugin_load(self):
        text = self.reach()
        apply = method_body(text, r'static\s+void\s+ApplyItemReachPatch\(\s*\)')
        self.assertIsNotNone(apply)
        self.assertRegex(apply, r'if\s*\(\s*_itemReachPatched\s*\)\s*return\s*;')
        self.assertRegex(apply, r'_itemReachPatched\s*=\s*true\s*;')
        self.assertIn('Plugin.Log(', apply)
        plugin = read(PLUGIN_CS)
        self.assertEqual(len(re.findall(r'ShrineStallReach\.ApplyItemReachPatch', plugin)), 1)
        self.assertRegex(plugin, r'Step\("[^"]+",\s*ShrineStallReach\.ApplyItemReachPatch\)')

    def test_log_bodies_reports_the_effective_item_max(self):
        coll = read(COLLISION_CS)
        reach = method_body(coll, r'private static void LogReach\(GameObject liveShop, GameObject counterProp\)')
        self.assertRegex(reach, r'item\.GetOverrideMaxDistance\(\)', 'the effective max is what the patched method returns')
        self.assertIn('ShrineStallReach.ItemReachPatched', reach)
        self.assertIn('ShrineStallReach.ShrineItemReachTiles', reach)
        to = method_body(coll, r'private static void LogReachTo\(')
        self.assertIn('OUT OF REACH', to)
        self.assertIn('in reach', to)


class Fix3StandProbeTests(unittest.TestCase):
    """`pluto_stall stand <daifuku|0|1|2>`: the game, not our assumed default, answers the reach question."""

    def reach(self):
        text = read(REACH_CS)
        self.assertTrue(text, 'PlutoTheCat/src/ShrineStallReach.cs is not implemented')
        return text

    def stand(self):
        b = method_body(self.reach(), r'internal\s+static\s+void\s+Stand\(\s*string\s+\w+,\s*GameObject\s+liveShop,\s*GameObject\s+counterProp\s*\)')
        self.assertIsNotNone(b, 'ShrineStallReach.Stand(string target, GameObject liveShop, GameObject counterProp)')
        return b

    def test_command_is_wired(self):
        stall = read(STALL_CS)
        self.assertRegex(stall, r'string\.Equals\(args\[0\], "stand"')
        self.assertIn('ShrineStallReach.Stand(args[1], FindLiveShop(), _counterProp)', stall)
        self.assertIn('pluto_stall stand <daifuku|0|1|2>', stall, 'the usage line must list it')

    def test_breach_only(self):
        stand = self.stand()
        self.assertIn('FindObjectOfType<MainMenuFoyerController>() == null', stand)
        refuse = stand.index('FindObjectOfType<MainMenuFoyerController>() == null')
        self.assertLess(refuse, stand.index('WarpToPoint('), 'refuse before warping anywhere')
        self.assertIn('return;', stand[refuse:refuse + 400])

    def test_targets(self):
        stand = self.stand()
        self.assertIn('"daifuku"', stand)
        self.assertIn('GetComponentInChildren<TalkDoerLite>(true)', stand)
        self.assertIn('GetComponentsInChildren<CustomShopItemController>(true)', stand)
        self.assertRegex(stand, r'int\.TryParse\(')

    def test_feet_two_pixels_in_front_of_the_counter_collider(self):
        text = self.reach()
        self.assertRegex(text, r'const\s+int\s+StandGapPx\s*=\s*2\s*;')
        stand = self.stand()
        self.assertIn('ShrineStallCollision.CounterFrontY(counterProp)', stand)
        self.assertRegex(stand, r'-\s*StandGapPx\s*/\s*PixelsPerTile')
        self.assertIn('GroundTopCenter(player)', stand, 'aim the ground collider top, not the transform')
        self.assertRegex(stand, r'\.WarpToPoint\([^;]*,\s*false,\s*false\)', 'WarpToPoint(Vector2, bool useDefaultPoof, bool doFollowers)')
        coll = read(COLLISION_CS)
        front = method_body(coll, r'internal\s+static\s+float\s+CounterFrontY\(\s*GameObject\s+counterProp\s*\)')
        self.assertIsNotNone(front, 'the counter collider front edge comes from the collision file')
        self.assertIn('CounterBoxOffsetYPx / PixelsPerTile', front)

    def test_no_ghost_collision_trap(self):
        text = self.reach()
        self.assertIn('RegisterOverlappingGhostCollisionExceptions(player.specRigidbody)', text)
        self.assertIn('PhysicsEngine.HasInstance', text)

    def test_probe_reads_the_games_own_selection(self):
        text = self.reach()
        self.assertIn('"m_lastInteractionTarget"', text)
        self.assertRegex(text, r'BindingFlags\.NonPublic')
        self.assertIn('StartCoroutine(', self.stand(), 'the probe runs as a coroutine on a live object')
        probe = method_body(text, r'IEnumerator\s+\w+\(')
        self.assertIsNotNone(probe, 'the probe is a coroutine')
        self.assertRegex(probe, r'new\s+WaitForSeconds\(\s*StandProbeDelaySeconds\s*\)')
        self.assertRegex(text, r'const\s+float\s+StandProbeDelaySeconds\s*=\s*0\.5f\s*;')
        self.assertIn('"shrine stall: stand "', probe)
        self.assertIn('": the game selected "', probe)
        self.assertIn('" (expected "', probe)
        self.assertIn('"REACH OK"', probe)
        self.assertIn('"NOT REACHED"', probe)
        self.assertIn('ShrineStall.ReportWhere(', probe, 'pluto_where-style position')
        self.assertIn('CenterPosition', probe)
        self.assertRegex(read(STALL_CS), r'internal\s+static\s+void\s+ReportWhere\(string command\)')

    def test_probe_names_daifuku_and_shop_items(self):
        text = self.reach()
        self.assertIn('"Daifuku"', text)
        self.assertIn('"Shop item "', text)


class StandAimsTheGroundColliderTop(unittest.TestCase):
    """2.20.9 controller review: aiming the whole body's bottom at the counter front sinks the ground box
    into the counter and over-reports reach. The warp must aim the PlayerCollider box's top."""

    def test_warp_aims_ground_collider_top(self):
        src = (pathlib.Path(__file__).resolve().parents[2] / 'PlutoTheCat' / 'src' / 'ShrineStallReach.cs').read_text(encoding='utf-8')
        code = re.sub(r'//.*', '', src)
        self.assertIn('CollisionLayer.PlayerCollider', code)
        self.assertRegex(code, r'Vector2 feetOffset = GroundTopCenter\(player\)')
        self.assertNotRegex(code, r'feetOffset = player\.specRigidbody\.UnitBottomCenter')


if __name__ == '__main__':
    unittest.main()
