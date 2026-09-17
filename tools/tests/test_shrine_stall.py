"""Source-level wiring checks for the Shrine Stall 2.20 per-save unlock store."""
import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / 'PlutoTheCat' / 'src'
SHOP = ROOT / 'PlutoTheCat' / 'Resources' / 'Shop'
PREVIEW = ROOT / 'docs' / 'art-preview' / 'shrine-stall-2200.png'
KIT_CASES = ROOT / 'tools' / 'tests' / 'player_kit_cases.cs'

# The ten gated ids (Task 2/3/5's contract), each paired with its config price key (Task 1) and the
# Plugin.cs Step(...) call that loads it (Task 1-era item registration, unrelated to this round).
GATED_ITEMS = (
    ('BallOfYarnItem.ID', 'StallPriceBallOfYarn', 'Step("ball of yarn", BallOfYarnItem.Init)'),
    ('CatnipPouchItem.ID', 'StallPriceCatnipPouch', 'Step("catnip pouch", CatnipPouchItem.Init)'),
    ('HairballItem.ID', 'StallPriceHairball', 'Step("hairball item", HairballItem.Init)'),
    ('ScratchingPostItem.ID', 'StallPriceScratchingPost', 'Step("scratching post", ScratchingPostItem.Init)'),
    ('ToiletPaperRollItem.ID', 'StallPriceToiletPaperRoll', 'Step("toilet paper roll", ToiletPaperRollItem.Init)'),
    ('CoffeeMugItem.ID', 'StallPriceCoffeeMug', 'Step("coffee mug", CoffeeMugItem.Init)'),
    ('JingleBellCollarItem.ID', 'StallPriceJingleBellCollar', 'Step("jingle bell collar", JingleBellCollarItem.Init)'),
    ('ConeOfShameItem.ID', 'StallPriceConeOfShame', 'Step("cone of shame", ConeOfShameItem.Init)'),
    ('SprayBottleGun.ID', 'StallPriceSprayBottle', 'Step("spray bottle", SprayBottleGun.Add)'),
    ('FeatherTeaserGun.ID', 'StallPriceFeatherTeaser', 'Step("feather teaser", FeatherTeaserGun.Add)'),
)

# Ids that must NOT be gated: the two active/passive starter items, the two starter guns, and the
# 2.18 Yasupen costume item - none of these are 2.17.0/2.19.0 cat-set items.
EXCLUDED_IDS = (
    'KibbleSackGun.ID',
    'WetFoodCanItem.ID',
    'KatanaGun.ID',
    'TaiyakiCannonGun.ID',
    'CocoBlueItem.ID',
    'YasupenItem.ID',
)


class ShrineStallWiringTests(unittest.TestCase):
    def source(self, name):
        path = SRC / name
        self.assertTrue(path.exists(), name + ' is not implemented')
        return path.read_text(encoding='utf-8')

    def requires(self, name, *needles):
        text = self.source(name)
        for needle in needles:
            self.assertIn(needle, text, name + ' missing ' + needle)
        return text

    def test_unlock_store(self):
        self.requires(
            'PlutoUnlocks.cs',
            'ETGModCompatibility.ExtendEnum<GungeonFlags>(Plugin.GUID',
            'ShrineStallRules.FlagName(',
            'ShrineStallRules.MirrorKey(',
            'ShrineStallRules.Unlocked(',
            'GameStatsManager.Instance.SetFlag(',
            'GameStatsManager.Instance.GetFlag(',
            'ForceUnlock(',
            'IsForceUnlocked(',
            'GameStatsManager.Save()',
            'BallOfYarnItem.ID',
            'CatnipPouchItem.ID',
            'HairballItem.ID',
            'ScratchingPostItem.ID',
            'ToiletPaperRollItem.ID',
            'CoffeeMugItem.ID',
            'JingleBellCollarItem.ID',
            'ConeOfShameItem.ID',
            'SprayBottleGun.ID',
            'FeatherTeaserGun.ID',
        )

        plugin = self.source('Plugin.cs')
        unlocks_idx = plugin.find('Step("unlocks", PlutoUnlocks.Init)')
        self.assertGreaterEqual(unlocks_idx, 0, 'Plugin.cs missing Step("unlocks", PlutoUnlocks.Init)')
        stall_idx = plugin.find('Step("shrine stall"')
        if stall_idx >= 0:
            self.assertLess(unlocks_idx, stall_idx,
                             'Step("unlocks", ...) must come before Step("shrine stall", ...)')

    def test_unlock_gate(self):
        self.requires(
            'PlutoUnlockGate.cs',
            'DungeonPrerequisite',
            'prerequisiteType = DungeonPrerequisite.PrerequisiteType.FLAG',
            'saveFlagToCheck =',
            'requireFlag = true',
            'encounterTrackable',
            'LootUtility.RemovePickupFromLootTables(',
            'LootUtility.AddItemToPool(',
            'BallOfYarnItem.ID',
            'CatnipPouchItem.ID',
            'HairballItem.ID',
            'ScratchingPostItem.ID',
            'ToiletPaperRollItem.ID',
            'CoffeeMugItem.ID',
            'JingleBellCollarItem.ID',
            'ConeOfShameItem.ID',
            'SprayBottleGun.ID',
            'FeatherTeaserGun.ID',
        )
        gate = self.source('PlutoUnlockGate.cs')
        self.assertTrue(
            'DungeonHooks.OnPostDungeonGeneration' in gate or 'DungeonHooks.OnPreDungeonGeneration' in gate,
            'PlutoUnlockGate.cs missing a dungeon-start hook so the guard re-applies every run',
        )
        self.assertIn('public static void Teardown', gate, 'PlutoUnlockGate.cs missing a Teardown method to unhook the stored delegate')
        self.assertIn('DungeonHooks.OnPostDungeonGeneration -=', gate,
                       'Teardown() must unsubscribe the same DungeonHooks event Apply() subscribed')

        plugin = self.source('Plugin.cs')
        gate_idx = plugin.find('Step("unlock gate", PlutoUnlockGate.Apply)')
        self.assertGreaterEqual(gate_idx, 0, 'Plugin.cs missing Step("unlock gate", PlutoUnlockGate.Apply)')

        # Teardown() must actually be called somewhere, not just exist to satisfy this test: Plugin is a
        # BaseUnityPlugin (MonoBehaviour), so Unity's own OnDestroy is a real engine-invoked call site.
        destroy_idx = plugin.find('OnDestroy()')
        self.assertGreaterEqual(destroy_idx, 0, 'Plugin.cs missing an OnDestroy() method to unhook PlutoUnlockGate on teardown')
        destroy_body_end = plugin.find('}', plugin.find('{', destroy_idx))
        destroy_body = plugin[destroy_idx:destroy_body_end]
        self.assertIn('PlutoUnlockGate.Teardown()', destroy_body,
                       "Plugin.cs's OnDestroy() must call PlutoUnlockGate.Teardown() to unhook the stored delegate")

        unlocks_idx = plugin.find('Step("unlocks", PlutoUnlocks.Init)')
        self.assertGreaterEqual(unlocks_idx, 0, 'Plugin.cs missing Step("unlocks", PlutoUnlocks.Init)')
        self.assertLess(unlocks_idx, gate_idx, 'Step("unlock gate", ...) must come after Step("unlocks", ...)')

        item_steps = [
            'Step("ball of yarn", BallOfYarnItem.Init)',
            'Step("catnip pouch", CatnipPouchItem.Init)',
            'Step("jingle bell collar", JingleBellCollarItem.Init)',
            'Step("hairball item", HairballItem.Init)',
            'Step("scratching post", ScratchingPostItem.Init)',
            'Step("toilet paper roll", ToiletPaperRollItem.Init)',
            'Step("cone of shame", ConeOfShameItem.Init)',
            'Step("coffee mug", CoffeeMugItem.Init)',
            'Step("spray bottle", SprayBottleGun.Add)',
            'Step("feather teaser", FeatherTeaserGun.Add)',
        ]
        for step in item_steps:
            idx = plugin.find(step)
            self.assertGreaterEqual(idx, 0, 'Plugin.cs missing ' + step)
            self.assertLess(idx, gate_idx, step + ' must come before Step("unlock gate", ...)')


    def test_stall_purchase_unlocks(self):
        """Critical fix-round finding: SetUpFoyerShop's OnPurchase slot (the 4th of the
        CustomCanBuy/CustomRemoveCurrency/CustomPrice/OnPurchase/OnSteal group, confirmed against the
        Alexandria 0.5.10 IL as Func<PlayerController, PickupObject, int, bool>) must be wired to a real
        method that calls PlutoUnlocks.Unlock(...) - not left null. Passing null there means nothing in
        our code ever writes ShrineStallRules.MirrorKey's string mirror or calls GameStatsManager.Save(),
        which is the entire flag-id-drift protection the docs describe. A string match on 'PlutoUnlocks.Unlock'
        appearing anywhere in the file is not enough (e.g. a stray doc-comment mention would pass it), so
        this resolves the actual argument passed in the OnPurchase position and checks that argument's own
        method body.
        """
        stall = self.source('ShrineStall.cs')

        marker = '// CustomCanBuy / CustomRemoveCurrency / CustomPrice / OnPurchase / OnSteal'
        marker_idx = stall.find(marker)
        self.assertGreaterEqual(marker_idx, 0,
                                 'ShrineStall.cs missing the CustomCanBuy/.../OnPurchase/OnSteal argument marker')
        line_start = stall.rfind('\n', 0, marker_idx) + 1
        args_line = stall[line_start:marker_idx]
        args = [a.strip() for a in args_line.split(',') if a.strip()]
        self.assertEqual(len(args), 5,
                          'expected exactly 5 arguments (CustomCanBuy, CustomRemoveCurrency, CustomPrice, '
                          'OnPurchase, OnSteal) on the marker line, found %d: %r' % (len(args), args))
        on_purchase_arg = args[3]

        self.assertNotEqual(on_purchase_arg, 'null',
                             'SetUpFoyerShop\'s OnPurchase argument must not be null: nothing else calls '
                             'PlutoUnlocks.Unlock(...), so a purchase never writes the string mirror or '
                             'calls GameStatsManager.Save()')

        method_match = re.search(
            r'\bbool\s+' + re.escape(on_purchase_arg) + r'\s*\([^)]*\)\s*\{(.*?)\n        \}',
            stall, re.S)
        self.assertIsNotNone(
            method_match,
            'could not find a method named ' + on_purchase_arg + ' in ShrineStall.cs matching the '
            'OnPurchase argument passed to SetUpFoyerShop')
        method_body = method_match.group(1)
        self.assertIn('PlutoUnlocks.Unlock(', method_body,
                       'the method passed as OnPurchase (' + on_purchase_arg + ') must call '
                       'PlutoUnlocks.Unlock(...) so a purchase actually writes the string mirror')

    def test_stall_registration(self):
        self.requires(
            'ShrineStall.cs',
            'ShopAPI.SetUpFoyerShop(',
            'CustomShopItemController.ShopCurrencyType.META_CURRENCY',
            'ShopAPI.VoiceBoxes.BELLO',
            'Plugin.SHOP_ROOT',
            'PlutoConfig.StallPosition',
            'hitboxOffset',
            'ShrineStallRules.Price(',
            'GenericLootTable',
            'ShrineStallLines.',
        )
        stall = self.source('ShrineStall.cs')
        self.assertTrue(
            'GameObject' in stall and ('== null' in stall or 'is null' in stall),
            'ShrineStall.cs missing a null check on the GameObject SetUpFoyerShop returns',
        )
        self.assertIn('Plugin.Log', stall, 'ShrineStall.cs must log the outcome through Plugin.Log')

        # Finding 1 (round 1 + round 2 review): Kinsuke's koi art must actually be visible in game as a
        # second sprite, or he is permanently invisible/replaces Daifuku. AddParentedAnimationToShop /
        # AddUnparentedAnimationToShop were tried in round 1 and confirmed (against the Alexandria IL) to
        # register a dead clip on Daifuku's OWN animator rather than spawn a second sprite - a string
        # match on 'kinsuke_idle' alone cannot tell a real fix from that dead one, so assert the actual
        # wiring: Kinsuke goes through the same real-sprite PlaceProp(...) path as the torii and stall,
        # and the two dead Alexandria calls are gone.
        self.assertIn('PlaceProp("kinsuke_idle_001.png"', stall,
                       'ShrineStall.cs must place Kinsuke as a real sprite GameObject via PlaceProp, '
                       'the same way it places the torii and stall')
        self.assertNotIn('AddParentedAnimationToShop', stall,
                          'AddParentedAnimationToShop only adds a dead clip to Daifuku\'s own animator; '
                          'it creates no second sprite for Kinsuke and must not be used')
        self.assertNotIn('AddUnparentedAnimationToShop', stall,
                          'AddUnparentedAnimationToShop only adds a dead clip to Daifuku\'s own animator; '
                          'it creates no second sprite for Kinsuke and must not be used')

        # Finding 2 (round 1 review): ShrineStallLines' public contract is fixed by the plan's Task 6
        # section (IntroKey, GenericKey, StopperKey, PurchaseKey, PurchaseFailedKey, Register()), not by
        # this task's own guess. ShrineStall.cs must reference exactly those names.
        for key in ('IntroKey', 'GenericKey', 'StopperKey', 'PurchaseKey', 'PurchaseFailedKey'):
            self.assertIn('ShrineStallLines.' + key, stall,
                           'ShrineStall.cs must reference ShrineStallLines.' + key + ' (the plan\'s Task 6 contract)')

        lines = self.source('ShrineStallLines.cs')
        for key in ('IntroKey', 'GenericKey', 'StopperKey', 'PurchaseKey', 'PurchaseFailedKey'):
            self.assertIn('string ' + key, lines,
                           'ShrineStallLines.cs must define ' + key + ' (the plan\'s Task 6 contract)')
        self.assertIn('public static void Register(', lines, 'ShrineStallLines.cs missing Register()')

        plugin = self.source('Plugin.cs')
        self.assertIn('SHOP_ROOT', plugin, 'Plugin.cs missing SHOP_ROOT')

        gate_idx = plugin.find('Step("unlock gate", PlutoUnlockGate.Apply)')
        self.assertGreaterEqual(gate_idx, 0, 'Plugin.cs missing Step("unlock gate", ...)')
        stall_idx = plugin.find('Step("shrine stall", ShrineStall.Init)')
        self.assertGreaterEqual(stall_idx, 0, 'Plugin.cs missing Step("shrine stall", ShrineStall.Init)')
        self.assertLess(gate_idx, stall_idx, 'Step("shrine stall", ...) must come after Step("unlock gate", ...)')

        unlocks_idx = plugin.find('Step("unlocks", PlutoUnlocks.Init)')
        self.assertGreaterEqual(unlocks_idx, 0, 'Plugin.cs missing Step("unlocks", ...)')
        self.assertLess(unlocks_idx, gate_idx, 'Step("unlock gate", ...) must come after Step("unlocks", ...)')
        self.assertLess(unlocks_idx, stall_idx, 'Step("shrine stall", ...) must come after Step("unlocks", ...)')


    # Deliberately small: this is a "did a joke drift crude" tripwire, not a profanity filter. It
    # cannot tell a good line from a bad one, so it is paired with the shape checks below (a real
    # setup and a real punchline, both speakers, no repeats) and with a human read of every line.
    SWEARS = ('fuck', 'shit', 'piss', 'crap', 'damn', 'bitch', 'bastard', 'ass', 'hell', 'dick')

    # C# string literal, escapes included (\" and \n stay as written in the source).
    LITERAL = re.compile(r'"((?:[^"\\\n]|\\.)*)"')

    def stall_lines_literals(self):
        text = self.source('ShrineStallLines.cs')
        return text, [m.group(1) for m in self.LITERAL.finditer(text)]

    def test_stall_lines(self):
        text, literals = self.stall_lines_literals()

        self.assertIn('ETGMod.Databases.Strings.Core.Set(', text,
                       'ShrineStallLines.cs must register its lines through ETGMod.Databases.Strings.Core.Set(')

        # The five keys are the plan's Task 6 contract; their values are the game's own "#" key form.
        keys = {}
        for name in ('IntroKey', 'GenericKey', 'StopperKey', 'PurchaseKey', 'PurchaseFailedKey'):
            match = re.search(r'string\s+' + name + r'\s*=\s*"(#PLUTO_STALL_[A-Z_]+)"', text)
            self.assertIsNotNone(match, name + ' must be a "#PLUTO_STALL_..." string key')
            keys[name] = match.group(1)
            self.assertIn(name, text.split('Register(')[-1], name + ' must be registered in Register()')
        self.assertEqual(len(set(keys.values())), 5, 'the five string keys must all differ')

        self.assertIn('Daifuku', text, 'ShrineStallLines.cs must name Daifuku')
        self.assertIn('Kinsuke', text, 'ShrineStallLines.cs must name Kinsuke')

        # Every spoken line is a "Daifuku: setup \n Kinsuke: punchline" exchange - one dialogue box.
        exchanges = [s for s in literals if 'Daifuku:' in s and 'Kinsuke:' in s]
        self.assertGreaterEqual(len(exchanges), 20,
                                 'the generic pool needs at least 20 Daifuku/Kinsuke exchanges, found %d'
                                 % len(exchanges))
        self.assertEqual(len(exchanges), len(set(exchanges)), 'no exchange may be repeated')

        for line in exchanges:
            self.assertRegex(line, r'^Daifuku: .*\\nKinsuke: ',
                              'Daifuku sets up and Kinsuke lands it, in that order: ' + line)
            setup, punchline = line.split('\\nKinsuke: ', 1)
            setup = setup[len('Daifuku: '):]
            self.assertGreaterEqual(len(setup.strip()), 10, 'empty or stub setup: ' + line)
            self.assertGreaterEqual(len(punchline.strip()), 10, 'empty or stub punchline: ' + line)

        for line in literals:
            lowered = re.sub(r'[^a-z ]+', ' ', line.lower())
            for swear in self.SWEARS:
                self.assertNotIn(' ' + swear + ' ', ' ' + lowered + ' ',
                                  'the stall never swears: ' + line)


    def test_shrine_stall_integration(self):
        """Aggregate check across Tasks 1-6: catches drift no single task's test can see, e.g. the
        ids list and the config price table quietly falling out of step with each other."""
        unlocks = self.source('PlutoUnlocks.cs')
        ids_match = re.search(r'Ids\s*=\s*new\[\]\s*\{(.*?)\};', unlocks, re.S)
        self.assertIsNotNone(ids_match, 'PlutoUnlocks.cs missing the Ids array literal')
        ids_tokens = [tok.strip() for tok in ids_match.group(1).split(',') if tok.strip()]

        # All ten ids, exactly once each, and none of the excluded starter/costume items.
        self.assertEqual(len(ids_tokens), 10,
                          'PlutoUnlocks.Ids must list exactly ten gated ids, found %d' % len(ids_tokens))
        self.assertEqual(len(set(ids_tokens)), 10, 'PlutoUnlocks.Ids must not repeat an id')
        expected_tokens = [token for token, _, _ in GATED_ITEMS]
        self.assertEqual(sorted(ids_tokens), sorted(expected_tokens),
                          'PlutoUnlocks.Ids must be exactly the ten 2.17.0/2.19.0 cat items')
        for excluded in EXCLUDED_IDS:
            self.assertNotIn(excluded, ids_tokens, 'PlutoUnlocks.Ids must not gate ' + excluded)

        # Every gated id has a config price key (Task 1), a Ranges entry (Task 1) and a
        # player_kit_cases.cs default (Task 1's own test fixture).
        config = self.source('PlutoConfig.cs')
        rules = self.source('PlutoConfigRules.cs')
        kit_cases = KIT_CASES.read_text(encoding='utf-8')
        for token, price_key, step in GATED_ITEMS:
            self.assertIn('public static int ' + price_key, config,
                           'PlutoConfig.cs missing ' + price_key)
            self.assertIn('"' + price_key + '"', rules,
                           'PlutoConfigRules.cs missing a Ranges entry for ' + price_key)
            self.assertIn('"' + price_key + '"', kit_cases,
                           'player_kit_cases.cs missing a default case for ' + price_key)

        # Load-step order: items, then unlocks, then unlock gate, then shrine stall.
        plugin = self.source('Plugin.cs')
        unlocks_idx = plugin.find('Step("unlocks", PlutoUnlocks.Init)')
        gate_idx = plugin.find('Step("unlock gate", PlutoUnlockGate.Apply)')
        stall_idx = plugin.find('Step("shrine stall", ShrineStall.Init)')
        self.assertGreaterEqual(unlocks_idx, 0, 'Plugin.cs missing Step("unlocks", ...)')
        self.assertGreaterEqual(gate_idx, 0, 'Plugin.cs missing Step("unlock gate", ...)')
        self.assertGreaterEqual(stall_idx, 0, 'Plugin.cs missing Step("shrine stall", ...)')
        self.assertLess(unlocks_idx, gate_idx, 'Step("unlocks", ...) must come before Step("unlock gate", ...)')
        self.assertLess(gate_idx, stall_idx, 'Step("unlock gate", ...) must come before Step("shrine stall", ...)')
        for token, _, step in GATED_ITEMS:
            idx = plugin.find(step)
            self.assertGreaterEqual(idx, 0, 'Plugin.cs missing ' + step)
            self.assertLess(idx, unlocks_idx, step + ' must load before Step("unlocks", ...)')

        # Cross-task bug class this test exists to catch: ShrineStall.cs builds its weight/"price"
        # array positionally and looks prices up by walking PlutoUnlocks.Ids in lockstep with it
        # (ShrineStallRules.Price(id, prices, PlutoUnlocks.Ids)). If Task 2's Ids order and Task 5's
        # prices array order ever drift apart, an item silently gets sold at the wrong price - no
        # single task's own test can see this, because each only checks its own file.
        stall = self.source('ShrineStall.cs')
        prices_match = re.search(r'int\[\]\s*prices\s*=\s*\{(.*?)\};', stall, re.S)
        self.assertIsNotNone(prices_match, 'ShrineStall.cs missing the prices array literal')
        price_keys = re.findall(r'PlutoConfig\.(StallPrice\w+)', prices_match.group(1))
        token_to_price_key = dict((token, price_key) for token, price_key, _ in GATED_ITEMS)
        expected_price_keys = [token_to_price_key[token] for token in ids_tokens]
        self.assertEqual(price_keys, expected_price_keys,
                          "ShrineStall.cs's prices array must list the same items, in the same order, "
                          "as PlutoUnlocks.Ids, or prices silently attach to the wrong item")

        # Every Task 4 resource file actually delivered under Resources/Shop/ has its clip family
        # referenced by ShrineStall.cs - a new or renamed art file that nobody wires up is a silent
        # integration gap the art-only test (StallArtTests, below) cannot see, since it only checks
        # that the files exist, not that anything loads them.
        bases = set()
        for path in sorted(SHOP.glob('*.png')):
            frame_match = re.match(r'^(.*)_\d{3}$', path.stem)
            bases.add(frame_match.group(1) if frame_match else path.stem)
        self.assertEqual(bases, {'daifuku_idle', 'daifuku_talk', 'kinsuke_idle', 'torii', 'stall', 'blueprint'},
                          'unexpected set of Task 4 art families under Resources/Shop/: ' + repr(bases))
        for base in bases:
            pattern = re.compile(r'[/"]' + re.escape(base) + r'(_\d{3})?(\.png)?"')
            self.assertRegex(stall, pattern,
                              'ShrineStall.cs has no reference to the ' + base + ' art family')


class StallArtTests(unittest.TestCase):
    """The resource paths are a contract with ShrineStall.cs (ShopAPI loads them
    as embedded-resource names), so the files and the frame counts are asserted
    here rather than left to the art pipeline."""

    def test_stall_art(self):
        for clip, count in (('daifuku_idle', 4), ('daifuku_talk', 4), ('kinsuke_idle', 4)):
            for i in range(1, count + 1):
                name = '%s_%03d.png' % (clip, i)
                self.assertTrue((SHOP / name).exists(), 'missing ' + name)
            extra = '%s_%03d.png' % (clip, count + 1)
            self.assertFalse((SHOP / extra).exists(), clip + ' must have exactly %d frames' % count)
        for name in ('torii.png', 'stall.png', 'blueprint.png'):
            self.assertTrue((SHOP / name).exists(), 'missing ' + name)
        self.assertTrue(PREVIEW.exists(), 'missing docs/art-preview/shrine-stall-2200.png')


if __name__ == '__main__':
    unittest.main()
