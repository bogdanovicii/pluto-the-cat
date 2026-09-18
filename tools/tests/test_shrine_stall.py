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

    def test_purchase_matches_by_save_flag(self):
        """Final-review P1-A. The foyer meta-shop hands the OnPurchase callback a *blueprint clone*, not
        the real cat item: CustomShopController.DoSetup's `baseShopType == 6 && ExampleBlueprintPrefab
        != null` branch instantiates the one shared blueprint prefab, copies the real item's journal
        fields and its FLAG prerequisite's saveFlagToCheck onto it
        (`ldloc.s V_56; ldloc.s V_58; stfld PickupObject::SaveFlagToSetOnAcquisition`), then calls
        CustomShopItemController.Initialize with *that* clone - and the invoke site passes
        `this.item`. So every slot shares one PickupObjectId and a PickupObjectId comparison can never
        match. Match on the save flag instead.

        This is a source-text assertion and cannot prove the callback behaves correctly at runtime;
        only an in-game purchase can (and, per the IL, the blueprint branch never assigns the
        OnPurchase delegate at all - see the comment in ShrineStall.OnPurchase).
        """
        stall = self.source('ShrineStall.cs')
        marker = '// CustomCanBuy / CustomRemoveCurrency / CustomPrice / OnPurchase / OnSteal'
        line_start = stall.rfind('\n', 0, stall.find(marker)) + 1
        on_purchase_arg = [a.strip() for a in stall[line_start:stall.find(marker)].split(',') if a.strip()][3]
        method_match = re.search(
            r'\bbool\s+' + re.escape(on_purchase_arg) + r'\s*\([^)]*\)\s*\{(.*?)\n        \}',
            stall, re.S)
        self.assertIsNotNone(method_match, 'could not find the OnPurchase method ' + on_purchase_arg)
        body = method_match.group(1)
        self.assertIn('SaveFlagToSetOnAcquisition', body,
                       'the OnPurchase method must match the bought item by '
                       'item.SaveFlagToSetOnAcquisition == PlutoUnlocks.Flag(id): the foyer meta-shop '
                       'passes a blueprint clone whose PickupObjectId is shared by all ten slots')
        self.assertIn('PlutoUnlocks.Flag(', body,
                       'the OnPurchase method must compare against PlutoUnlocks.Flag(id)')
        self.assertIn('PlutoUnlocks.IsRegistered(', body,
                       'Flag(id) returns default(GungeonFlags) for an unregistered id, which would '
                       'match any clone whose SaveFlagToSetOnAcquisition was never set - guard with '
                       'PlutoUnlocks.IsRegistered(id)')

    def test_unlock_reconciliation(self):
        """Final-review P2-D (and the fallback for the dead OnPurchase delegate). Nothing reconciles the
        string mirror and the GungeonFlags value, so in the drift scenario the mirror exists for,
        IsUnlocked() is true (the item drops) while PrerequisitesMet() is false (the stall re-stocks and
        re-charges it and its Ammonomicon page reverts). Reconcile must run both ways."""
        unlocks = self.source('PlutoUnlocks.cs')
        match = re.search(r'public static void Reconcile\(\)(.*?)\n        \}', unlocks, re.S)
        self.assertIsNotNone(match, 'PlutoUnlocks.cs must expose a Reconcile() that syncs flag and mirror')
        body = match.group(1)
        self.assertIn('SetFlag(', body, 'Reconcile() must set the flag when only the mirror says unlocked')
        self.assertIn('ForceUnlock(', body, 'Reconcile() must write the mirror when only the flag says unlocked')
        self.assertIn('GameStatsManager.Save()', body, 'Reconcile() must flush the save when it changed something')
        self.assertNotIn('IsUnlocked(', body,
                          'Reconcile() must read the raw flag and raw mirror, not IsUnlocked(), or the '
                          'StallUnlocksDisabled toggle would permanently write all ten unlocks into the save')
        gate = self.source('PlutoUnlockGate.cs')
        self.assertIn('PlutoUnlocks.Reconcile()', gate, 'PlutoUnlockGate must call PlutoUnlocks.Reconcile()')

    def test_toggle_skips_prerequisites(self):
        """Final-review P2-C. StallUnlocksDisabled was consulted only in ShrineStallRules.Unlocked, which
        drives only RefreshLootTables - the FLAG prerequisite was still attached, so the stall kept
        stocking all ten, prereq-respecting selectors kept skipping them and the Ammonomicon kept showing
        ???. With the toggle on, no prerequisite may be attached."""
        gate = self.source('PlutoUnlockGate.cs')
        apply_match = re.search(r'public static void Apply\(\)(.*?)\n        \}\n', gate, re.S)
        self.assertIsNotNone(apply_match, 'PlutoUnlockGate.cs missing Apply()')
        self.assertIn('PlutoConfig.StallUnlocksDisabled', apply_match.group(1),
                       'Apply() must consult PlutoConfig.StallUnlocksDisabled before attaching the FLAG '
                       'prerequisites, or the toggle is not a real escape hatch')

    def test_loot_guard_covers_chest_tables(self):
        """Final-review P1-B. LootUtility.RemovePickupFromLootTables touches only RewardManager's
        GunsLootTable and ItemsLootTable (verified in the Alexandria 0.5.10 IL). ItemDB.AddSpecific puts
        the same WeightedGameObject into ModLootPerFloor too, and ItemDB.DungeonStart (a Harmony prefix on
        Dungeonator.Dungeon.Start) AddRanges ModLootPerFloor into
        Dungeon.baseChestContents.defaultItemDrops.elements - the collection that actually feeds chests.
        The guard must sweep those as well."""
        gate = self.source('PlutoUnlockGate.cs')
        self.assertIn('ModLootPerFloor', gate,
                       'the loot guard must sweep ETGMod.Databases.Items.ModLootPerFloor, which '
                       'ItemDB.DungeonStart re-injects into the chest table every run')
        self.assertIn('baseChestContents', gate,
                       'the loot guard must sweep the current dungeon\'s baseChestContents, which '
                       'ItemDB.DungeonStart has already filled by the time the guard runs')

    def test_props_survive_a_run(self):
        """Final-review P2-E. PlaceProp made unparented GameObjects once, from Init, with no
        DontDestroyOnLoad: Unity destroys them on the next scene load, and only Daifuku is re-placed by
        Alexandria, so after one run the shopkeeper stood alone in mid-air."""
        stall = self.source('ShrineStall.cs')
        self.assertIn('DungeonHooks.OnFoyerAwake +=', stall,
                       'the backdrop props must be re-placed on every foyer load (DungeonHooks.OnFoyerAwake), '
                       'since unparented GameObjects do not survive a scene change')
        self.assertIn('public static void Teardown', stall, 'ShrineStall.cs missing Teardown()')
        self.assertIn('DungeonHooks.OnFoyerAwake -=', stall,
                       'Teardown() must unsubscribe the same hook Init() subscribed')
        plugin = self.source('Plugin.cs')
        destroy_idx = plugin.find('OnDestroy()')
        destroy_body = plugin[destroy_idx:plugin.find('}', plugin.find('{', destroy_idx))]
        self.assertIn('ShrineStall.Teardown()', destroy_body,
                       "Plugin.cs's OnDestroy() must call ShrineStall.Teardown()")
        # The props are only worth placing when the shop itself built: SetUpFoyerShop returning null
        # means no Daifuku, and a torii with no shopkeeper under it is worse than nothing.
        init_match = re.search(r'public static void Init\(\)(.*?)\n        \}\n', stall, re.S)
        self.assertIsNotNone(init_match, 'ShrineStall.cs missing Init()')
        init_body = init_match.group(1)
        null_idx = init_body.find('if (shop == null)')
        self.assertGreaterEqual(null_idx, 0, 'Init() must null-check the shop')
        self.assertLess(null_idx, init_body.find('PlaceBackdropProps'),
                         'PlaceBackdropProps() must not run when SetUpFoyerShop returned null')

    def test_kinsuke_animates(self):
        """The user asked for Kinsuke to bob in his bowl. All four kinsuke_idle_* frames must be driven by
        a timer component that lives and dies with the prop."""
        stall = self.source('ShrineStall.cs')
        for i in range(1, 5):
            self.assertIn('kinsuke_idle_%03d.png' % i, stall,
                           'ShrineStall.cs must use all four kinsuke_idle frames, not just the first')
        self.assertRegex(stall, r'class\s+\w+\s*:\s*MonoBehaviour',
                          'Kinsuke needs a small MonoBehaviour to advance his frames on a timer')
        self.assertIn('BraveTime.DeltaTime', stall,
                       'the flipbook must advance on BraveTime.DeltaTime, like the rest of this codebase')

    def test_stall_placement_command(self):
        """2.20.1: the (10.5, 22.1) launch default ran the shrine stall off-screen in the Breach (user
        report). This asserts the fix has three real, independently-checkable parts: a better default,
        a live pluto_stall console command wired into Init() (not just declared and never called), and a
        way to persist a chosen position back to the config file."""
        config = self.source('PlutoConfig.cs')

        # A better default: the old (10.5, 22.1) guess must be gone from both the field initializer and
        # the config's own fallback string, and StallPosition must still parse as a valid "x,y" pair.
        self.assertNotIn('new Vector3(10.5f, 22.1f, 0f)', config,
                          'PlutoConfig.cs must not keep the old off-screen (10.5, 22.1) StallPosition default')
        self.assertNotIn('"10.5,22.1"', config,
                          'PlutoConfig.cs must not keep the old off-screen "10.5,22.1" StallPosition config default')
        default_match = re.search(r'public static Vector3 StallPosition = new Vector3\(([-0-9.f]+), ?([-0-9.f]+)f?, 0f\);', config)
        self.assertIsNotNone(default_match, 'PlutoConfig.cs missing a parseable StallPosition default')
        bind_default_match = re.search(r'"StallPosition",\s*"(-?[\d.]+),(-?[\d.]+)"', config)
        self.assertIsNotNone(bind_default_match, 'PlutoConfig.cs\'s cfg.Bind("...", "StallPosition", ...) must have a literal "x,y" default string')

        # A way to persist a moved position: keep a ConfigEntry reference (the vet_trophy_here pattern in
        # PlutoVetVisit/src/PastConfig.cs) and expose a method that writes through it.
        self.assertIn('ConfigEntry<string>', config, 'PlutoConfig.cs must keep a ConfigEntry reference for StallPosition so a move can be saved without a restart')
        persist_match = re.search(r'public static bool PersistStallPosition\(\)(.*?)\n        \}', config, re.S)
        self.assertIsNotNone(persist_match, 'PlutoConfig.cs missing a public PersistStallPosition() that pluto_stall save can call')
        self.assertIn('.Value =', persist_match.group(1), 'PersistStallPosition() must write through the bound ConfigEntry, not just update the in-memory field')

        # A live console command, actually wired into Init() - not just present as dead code elsewhere.
        stall = self.source('ShrineStall.cs')
        self.assertIn('ETGModConsole.Commands.AddUnit("pluto_stall"', stall,
                       'ShrineStall.cs must register a pluto_stall console command')
        init_match = re.search(r'public static void Init\(\)(.*?)\n        \}\n', stall, re.S)
        self.assertIsNotNone(init_match, 'ShrineStall.cs missing Init()')
        self.assertRegex(init_match.group(1), r'RegisterConsoleCommand\(\)',
                          'Init() must call the method that registers pluto_stall, or the command never exists in a real run')

        # here / <x> <y> / save / no-args, and moving the tracked shop GameObject, not just the props.
        self.assertIn('GameManager.Instance.PrimaryPlayer', stall,
                       'pluto_stall here must read the live player position (the vet_trophy_here pattern)')
        self.assertIn('float.TryParse(args[0]', stall, 'pluto_stall must accept explicit <x> <y> coordinates')
        self.assertIn('PlutoConfig.PersistStallPosition()', stall, 'pluto_stall save must call PlutoConfig.PersistStallPosition()')
        move_match = re.search(r'private static void MoveStall\(Vector3 newPosition\)(.*?)\n        \}', stall, re.S)
        self.assertIsNotNone(move_match, 'ShrineStall.cs missing a MoveStall(Vector3) that both here/<x> <y> paths share')
        move_body = move_match.group(1)
        self.assertIn('FindLiveShop()', move_body,
                       'MoveStall must move the LIVE shop clone, not the stored template. Verified in the '
                       'Alexandria 0.5.10 IL (BreachShopTools::PlaceBreachShops, IL_00a1 onward): every '
                       'foyer load Instantiates the registered object and positions the CLONE, leaving the '
                       'registered one at the origin forever. 2.20.0-2.20.4 moved and measured that '
                       'template, so pluto_stall moved nothing visible and the 2.20.4 diagnostics reported '
                       'the whole hierarchy at 0,0 while the props sat correctly at the stall position.')
        self.assertIn('PlaceBackdropProps()', move_body, 'MoveStall must also re-place the three backdrop props at the new position')
        self.assertIn('_shopObject = shop;', stall, 'Init() must keep a reference to the built shop GameObject so it can later be moved')

    def test_npc_position_is_local_offset_not_world_duplicate(self):
        """2.20.2 root cause 1 (tester report: Daifuku entirely absent): SetUpFoyerShop parents the NPC
        to the shop root and then sets its WORLD position to the npcPosition argument BEFORE the root is
        later moved to `position` (verified against the Alexandria 0.5.10 IL - Transform::set_parent at
        IL_04fb, then Transform::set_position at IL_0509, while the root is still a fresh GameObject at
        Unity's (0,0,0) default). So npcPosition is Daifuku's offset from the shop root, and the final
        world position is `position + npcPosition`. Passing PlutoConfig.StallPosition for BOTH put Daifuku
        at roughly double his intended distance from the Breach origin, ~28 tiles from his own props. This
        must stay Vector3.zero: a regression back to PlutoConfig.StallPosition silently reintroduces the
        exact bug the tester hit, with no error logged anywhere."""
        stall = self.source('ShrineStall.cs')
        npc_position_line = next((l for l in stall.splitlines() if '// npcPosition:' in l), None)
        self.assertIsNotNone(npc_position_line, 'ShrineStall.cs missing the npcPosition argument (marked by a trailing "// npcPosition:" comment)')
        self.assertNotIn('PlutoConfig.StallPosition', npc_position_line,
                          'npcPosition must not reuse PlutoConfig.StallPosition - the shop root is already '
                          'placed there from BreachShopComp.offset, so passing it here doubles Daifuku\'s '
                          'distance from the Breach origin (the 2.20.2 bug: ~28 tiles from his own props)')
        self.assertIn('DaifukuBehindCounter', npc_position_line,
                       'npcPosition must be the DaifukuBehindCounter local offset. It is deliberately NOT '
                       'zero: at zero he stands on the counter\'s own ground line, and the counter (2.25 '
                       'tiles tall) is taller than he is (2), so it would cover him completely.')
        offset_match = re.search(r'DaifukuBehindCounter\s*=\s*(-?[\d.]+)f', stall)
        self.assertIsNotNone(offset_match, 'ShrineStall.cs missing a parseable DaifukuBehindCounter constant')
        self.assertGreater(float(offset_match.group(1)), 0.0,
                            'DaifukuBehindCounter must be positive: +Y is this engine\'s "further back", '
                            'which both raises him above the counter lip and sorts him behind it')

    def test_stall_offset_centers_counter_under_torii(self):
        """2.20.2 root cause 2 (tester report: counter sits low and to the left of the torii): the design
        (docs/superpowers/specs/2026-09-17-shrine-stall-design.md) wants the counter UNDER the gate. Both
        props are bottom-center pivoted, so centering the 3-tile-wide counter under the 4.875-tile-wide
        torii needs StallOffset.x == ToriiOffset.x, not the earlier -2.0625 nudge (which aligned the
        counter to the torii's left EDGE, not its center, and read as "left of the gate" in-game)."""
        stall = self.source('ShrineStall.cs')
        # Capture the FULL first-argument expression (not just its leading literal), so an old
        # "-3.0f - 2.0625f" style nudge is actually evaluated rather than truncated to "-3.0" and
        # spuriously matching.
        # Both may be written either as Vector3.zero (2.20.5 onwards, once the props were re-centered on
        # the shopkeeper himself) or as an explicit new Vector3(x, ...). Accept either and compare the X.
        def offset_x(name):
            if re.search(name + r'\s*=\s*Vector3\.zero', stall):
                return 0.0
            match = re.search(name + r'\s*=\s*new Vector3\(([^,]+),', stall)
            self.assertIsNotNone(match, 'ShrineStall.cs missing a parseable ' + name + ' declaration')
            return to_number(match.group(1))
        # Safe evaluator for the tiny subset of C# float arithmetic these fields use (e.g. "-3.0f",
        # "-3.0f - 2.0625f"): sum the signed float literals rather than calling eval() on source text.
        def to_number(expr):
            cleaned = re.sub(r'(?<![\d.])f(?![\w])', '', expr)
            terms = re.findall(r'[+-]?\s*[\d.]+', cleaned)
            self.assertTrue(terms, 'could not parse float literals out of %r' % expr)
            return sum(float(t.replace(' ', '')) for t in terms)
        torii_x = offset_x('ToriiOffset')
        stall_x = offset_x('StallOffset')
        self.assertEqual(torii_x, stall_x,
                          'StallOffset.x must equal ToriiOffset.x so the counter is centered under the '
                          'torii (both sprites are bottom-center pivoted; equal X centers one under the '
                          'other) - got ToriiOffset.x=%r, StallOffset.x=%r' % (torii_x, stall_x))

    def test_kinsuke_bowl_rests_on_measured_counter_height(self):
        """2.20.2 root cause 3 (tester report: the bowl floats near the torii's crossbeam): the old
        28/16 = 1.75-tile Y offset was a guess ("near the top of the sprite"). Measuring stall.png
        (48x36px, bottom-center pivot, 16px/tile) pixel-by-pixel: the counter's top lip (where the opaque
        pixels widen from the narrower noren curtain above to the full 48px width) starts at row 20 (from
        the top), so the counter surface sits (36 - 20) / 16 = 1.0 tile above the ground line - not 1.75."""
        stall = self.source('ShrineStall.cs')
        kinsuke_match = re.search(r'KinsukeOffset\s*=\s*StallOffset\s*\+\s*new Vector3\([^,]+,\s*([\d.]+)f\s*/\s*16f\s*,', stall)
        self.assertIsNotNone(kinsuke_match, 'ShrineStall.cs missing a parseable KinsukeOffset declaration')
        self.assertEqual(float(kinsuke_match.group(1)), 16.0,
                          "KinsukeOffset's Y numerator over 16f must be 16 (i.e. 1.0 tile, the measured "
                          "counter-top height), not the old guessed 28 (1.75 tiles)")

    def test_stall_registration(self):
        self.requires(
            'ShrineStall.cs',
            'ShopAPI.SetUpFoyerShop(',
            'CustomShopItemController.ShopCurrencyType.META_CURRENCY',
            'ShopAPI.VoiceBoxes.BELLO',
            'Plugin.SHOP_ROOT',
            'PlutoConfig.StallPosition',
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

        # hitboxOffset: Alexandria computes this same default internally but discards it before use, so
        # it has to be passed explicitly. Merely mentioning the name is not enough - a regression to
        # `null` would still contain the word in its trailing comment, and a null offset silently makes
        # Daifuku unclickable. Assert the value on the argument line itself.
        hitbox_line = next((l for l in stall.splitlines() if '// hitboxOffset' in l), None)
        self.assertIsNotNone(hitbox_line, 'ShrineStall.cs missing the hitboxOffset argument')
        self.assertIn('new IntVector2(5, 0)', hitbox_line,
                       'hitboxOffset must be passed explicitly as new IntVector2(5, 0) (Alexandria '
                       "computes this default and then discards it); null leaves Daifuku unclickable")
        hitbox_size_line = next((l for l in stall.splitlines() if '// hitboxSize' in l), None)
        self.assertIsNotNone(hitbox_size_line, 'ShrineStall.cs missing the hitboxSize argument')
        self.assertIn('new IntVector2(20, 18)', hitbox_size_line,
                       'hitboxSize must be passed explicitly as new IntVector2(20, 18)')

        # Finding 1 (round 1 + round 2 review): Kinsuke's koi art must actually be visible in game as a
        # second sprite, or he is permanently invisible/replaces Daifuku. AddParentedAnimationToShop /
        # AddUnparentedAnimationToShop were tried in round 1 and confirmed (against the Alexandria IL) to
        # register a dead clip on Daifuku's OWN animator rather than spawn a second sprite - a string
        # match on 'kinsuke_idle' alone cannot tell a real fix from that dead one, so assert the actual
        # wiring: Kinsuke goes through the same real-sprite PlaceProp(...) path as the torii and stall,
        # and the two dead Alexandria calls are gone.
        self.assertRegex(stall, r'PlaceProp\(\s*\n?\s*new\[\] \{ "kinsuke_idle_001\.png"',
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

    def test_props_use_tk2d_depth_not_a_raw_sprite_renderer(self):
        """2.20.4 root-cause fix: PlaceProp used to build plain Unity SpriteRenderer GameObjects at z=0
        with no sortingOrder/sortingLayer and none of this game's own depth handling - the same tk2d
        z-sort convention every other prop in this mod already uses (CoffeeMugItem.cs's puddle,
        PuffedUpItem.cs's fur layer, ScratchingPostItem.cs's placed post all call
        `sprite.HeightOffGround = ...; sprite.UpdateZDepth()` on a tk2dSprite). With the torii and counter
        now centered on Daifuku's own anchor, either one drawing in front of him at an undefined z would
        hide him completely with no error logged - this is the tester's "shopkeeper is missing" bug."""
        stall = self.source('ShrineStall.cs')
        self.assertNotIn('AddComponent<SpriteRenderer>', stall,
                          'ShrineStall.cs must not build props as plain SpriteRenderer GameObjects - they '
                          'need a tk2dSprite so HeightOffGround/UpdateZDepth can place them relative to '
                          "Daifuku's own depth (see CoffeeMugItem.cs:149-150 for the established pattern)")
        self.assertIn('AddComponent<tk2dSprite>', stall,
                       'PlaceProp must build a tk2dSprite, the depth mechanism this mod already uses '
                       'everywhere else')
        self.assertIn('.HeightOffGround = heightOffGround', stall,
                       'PlaceProp must set HeightOffGround so each prop has an explicit, deterministic '
                       'depth instead of an undefined z=0')
        self.assertIn('.UpdateZDepth()', stall,
                       'PlaceProp must call UpdateZDepth() after setting HeightOffGround, like every other '
                       'tk2d depth site in this codebase')

    def test_prop_depth_ordering_is_correct_after_world_y_is_accounted_for(self):
        """The 2.20.4 build ordered the props by HeightOffGround alone and got the order wrong in game,
        because that is not what decides depth. The tester derived the real relationship from our own
        diagnostic output:

            z = worldY - heightOffGround        (lower z draws in front)

        Kinsuke's bowl is the only prop raised in world Y (a tile, to sit on the counter lip), so that
        lift also pushed it a tile backwards and swamped its -0.3: measured z came out counter 22.725,
        torii 23.125, bowl 23.425 - the bowl behind everything, when it should be in front.

        So this asserts the computed z, combining each prop's Y offset with its HeightOffGround, rather
        than comparing HeightOffGround values that only tell half the story. Required order, front to
        back: bowl, counter, Daifuku (at +DaifukuBehindCounter, depth untouched by this file), torii."""
        stall = self.source('ShrineStall.cs')

        def constant(name):
            match = re.search(name + r'\s*=\s*(-?[\d.]+)f', stall)
            self.assertIsNotNone(match, 'ShrineStall.cs missing a parseable ' + name + ' constant')
            return float(match.group(1))

        def offset_y(expr):
            """The Y term of a Vector3 offset expression, relative to StallPosition."""
            match = re.search(expr, stall)
            self.assertIsNotNone(match, 'ShrineStall.cs missing offset ' + expr)
            return match

        daifuku_y = constant('DaifukuBehindCounter')
        # torii and counter sit on the stall's own ground line (Vector3.zero offsets)
        self.assertRegex(stall, r'ToriiOffset\s*=\s*Vector3\.zero',
                          'the torii shares the stall anchor, so its world Y offset is zero')
        self.assertRegex(stall, r'StallOffset\s*=\s*Vector3\.zero',
                          'the counter shares the stall anchor, so its world Y offset is zero')
        kinsuke_match = re.search(r'KinsukeOffset\s*=\s*StallOffset\s*\+\s*new Vector3\([^,]+,\s*([\d.]+)f?\s*/\s*16f\s*,', stall)
        self.assertIsNotNone(kinsuke_match, "ShrineStall.cs missing a parseable KinsukeOffset Y term")
        kinsuke_y = float(kinsuke_match.group(1)) / 16.0

        z_torii = 0.0 - constant('ToriiHeightOffGround')
        z_counter = 0.0 - constant('StallHeightOffGround')
        z_kinsuke = kinsuke_y - constant('KinsukeHeightOffGround')
        z_daifuku = daifuku_y - 0.0    # Alexandria manages his depth; this file leaves it alone

        self.assertLess(z_kinsuke, z_counter,
                         "the bowl must draw in front of the counter it rests on (z = worldY - "
                         "heightOffGround; raising it without compensating puts it behind, the 2.20.4 bug)")
        self.assertLess(z_counter, z_daifuku,
                         'the counter must draw in front of Daifuku, so he reads as standing behind it')
        self.assertLess(z_daifuku, z_torii,
                         'the gate must draw behind Daifuku, framing the whole stall')

    def test_diagnostics_and_moves_resolve_the_live_shop_not_the_template(self):
        """The single most expensive bug of this round: the object SetUpFoyerShop returns is a template
        that Alexandria Instantiates per foyer load, positioning the clone and leaving the template at the
        origin. Measuring or moving the template looks exactly like "the shopkeeper does not exist", with
        nothing in the log to distinguish the two - which cost four builds. FindLiveShop must exist, must
        match by component and our own prefix (not a "(Clone)" name suffix), must exclude the template
        explicitly, and must be what the diagnostics report."""
        stall = self.source('ShrineStall.cs')
        self.assertIn('private static GameObject FindLiveShop()', stall,
                       'ShrineStall.cs missing FindLiveShop()')
        body_start = stall.index('private static GameObject FindLiveShop()')
        body = stall[body_start:stall.index('private static void LogShopDiagnostics', body_start)]
        self.assertIn('FindObjectsOfType<CustomShopController>()', body,
                       'FindLiveShop must find the live shop by component rather than by name suffix')
        self.assertIn('go == _shopObject', body,
                       'FindLiveShop must skip the registered template, which never moves off the origin')
        self.assertIn('ShopPrefix', body,
                       "FindLiveShop must filter by our own prefix so another mod's breach shop is never moved")

        diag_start = stall.index('private static void LogShopDiagnostics')
        diag = stall[diag_start:stall.index('private static string FormatSize', diag_start)] \
            if 'private static string FormatSize' in stall[diag_start:] else stall[diag_start:]
        self.assertIn('FindLiveShop()', diag,
                       'LogShopDiagnostics must report the LIVE shop; reporting the template is what made '
                       'the 2.20.4 run show every child at 0,0')

    def test_shop_is_placed_even_when_the_foyer_awoke_before_we_registered(self):
        """The startup race that kept the stall empty for a whole session in every build up to 2.20.5.

        Alexandria raises OnFoyerAwake only from its patch on MainMenuFoyerController.Awake - the title
        screen's controller, in the Breach scene - which runs at launch, before this mod registers. So
        Alexandria's PlaceBreachShops placed nothing of ours, and starting a run does not reload the scene,
        so there was never a second Awake. Confirmed on the Steam machine: a forced foyer reload produced
        the live clone on the first try, and our own subscribed handler fired on that reload and never
        before it. Init must therefore catch up itself when the foyer is already up."""
        stall = self.source('ShrineStall.cs')
        self.assertIn('private static void PlaceIfFoyerAlreadyUp()', stall,
                       'ShrineStall.cs missing PlaceIfFoyerAlreadyUp()')
        body = stall[stall.index('private static void PlaceIfFoyerAlreadyUp()'):]
        body = body[:body.index('private static void ReconcileLiveShopPosition()')]
        self.assertIn('FindObjectOfType<MainMenuFoyerController>()', body,
                       'the catch-up must key off the same controller whose Awake raises OnFoyerAwake')
        self.assertIn('"Alexandria.NPCAPI.BreachShopTools"', body,
                       "the catch-up must use Alexandria's own placement (via reflection, the type is "
                       "internal) so the shopkeeper's TalkDoerLite is registered as an interactable too")
        self.assertIn('"PlaceBreachShops"', body)
        self.assertIn('FindLiveShop() != null', body,
                       'the catch-up must not re-place a shop that is already live')

        init = stall[stall.index('public static void Init()'):]
        init = init[:init.index('private static void RegisterConsoleCommand()')]
        subscribe = init.index('DungeonHooks.OnFoyerAwake += _foyerHandler;')
        catch_up = init.index('PlaceIfFoyerAlreadyUp();')
        props = init.index('PlaceBackdropProps();', catch_up)
        self.assertLess(subscribe, catch_up,
                         'subscribe first, so a foyer Awake that lands during start-up is not missed either')
        self.assertLess(catch_up, props,
                         'the shop must exist before the props are placed and reconciled against it')

    def test_a_move_updates_the_template_even_with_no_live_shop(self):
        """2.20.5 regression caught by the tester's own log line: 'LIVE shop root ... at 19.7,22.1
        (config says 19.75,19.688)'. pluto_stall here had been run while no clone existed yet, and the
        template's offset was only rewritten inside the live-shop branch, so the next foyer load placed
        the clone at the stale registered position. The template is what PlaceBreachShops reads, so it
        must be rewritten unconditionally."""
        stall = self.source('ShrineStall.cs')
        move = stall[stall.index('private static void MoveStall'):]
        move = move[:move.index('private static void ReportStallStatus')]
        template_write = move.find('SetBreachOffset(_shopObject, newPosition);')
        live_branch = move.find('if (live != null)')
        self.assertNotEqual(template_write, -1, 'MoveStall must rewrite the template offset')
        self.assertNotEqual(live_branch, -1)
        self.assertLess(template_write, live_branch,
                         'the template offset must be rewritten BEFORE and outside the live-shop branch, '
                         'or a move made while no clone exists is lost on the next Breach load')

    def test_every_placement_reconciles_the_live_shop_to_the_config(self):
        """Backstop for the offset rewrite: BreachShopComp is internal to Alexandria and reached by
        reflection, so if that write ever silently fails, re-asserting the live clone's position against
        the config on every placement is what still makes a pluto_stall move stick."""
        stall = self.source('ShrineStall.cs')
        placement = stall[stall.index('private static void PlaceBackdropProps()'):]
        placement = placement[:placement.index('private static void DestroyProps()')]
        reconcile = placement.find('ReconcileLiveShopPosition();')
        diag = placement.find('LogShopDiagnostics();')
        self.assertNotEqual(reconcile, -1, 'PlaceBackdropProps must reconcile the live shop position')
        self.assertLess(reconcile, diag,
                         'reconcile before logging, so the diagnostics report the corrected position')

    def test_shopkeeper_diagnostic_logs_the_whole_shop_hierarchy(self):
        """The tester asked for a diagnostic that distinguishes a working stall from one with no visible
        shopkeeper, unconditionally (not behind a debug flag), at foyer placement time and after a
        pluto_stall move. It must walk the shop GameObject's own children (Daifuku is one of several -
        Alexandria also builds a blueprint prefab instance, item points and a talk point under the same
        root), since the tester's own measurement of the narrow white bar (~3x58 art px) matches none of
        this mod's own art and needs a name, not another guess."""
        stall = self.source('ShrineStall.cs')
        self.assertIn('private static void LogShopDiagnostics', stall,
                       'ShrineStall.cs missing a LogShopDiagnostics() method')
        self.assertIn('GetComponentsInChildren<Transform>(true)', stall,
                       'LogShopDiagnostics must walk the full shop GameObject transform hierarchy, not '
                       'just the root, so a stray child (e.g. the narrow white bar) has a name')
        self.assertIn('LogShopDiagnostics();', stall,
                       'PlaceBackdropProps (which runs at foyer placement and after every pluto_stall '
                       'move) must call LogShopDiagnostics()')
        placement_idx = stall.find('private static void PlaceBackdropProps')
        diag_call_idx = stall.find('LogShopDiagnostics();', placement_idx)
        self.assertGreater(diag_call_idx, placement_idx,
                            'PlaceBackdropProps must call LogShopDiagnostics()')
        # Unconditional: no #if DEBUG or a config/debug-flag guard wrapping the diagnostic.
        method_start = stall.find('private static void LogShopDiagnostics')
        method_body = stall[method_start:stall.find('\n        }\n', method_start)]
        self.assertNotIn('#if', method_body,
                          'the diagnostic must be unconditional, not compiled out in some configuration')
        self.assertNotIn('Debug', method_body.replace('DebugMenu', ''),
                          'the diagnostic must run on a normal run, not only behind a debug flag')

    def test_shopkeeper_diagnostic_reports_position_renderer_and_bounds(self):
        """Task 2's exact ask: at foyer placement time, log the shopkeeper's resolved world position (read
        back from the transform), whether his sprite/animator actually bound (renderer present, sprite
        non-null, bounds/size, renderer enabled), and each prop's resolved world position and depth."""
        stall = self.source('ShrineStall.cs')
        diag = stall[stall.find('private static void LogShopDiagnostics'):stall.find('private static string FormatSize')]
        for needle in ('t.position', 'GetComponent<Renderer>', 'renderer.enabled', 'renderer.bounds'):
            self.assertIn(needle, diag,
                           'LogShopDiagnostics must report ' + needle + ' for each child in the hierarchy')
        prop_log = stall[stall.find('private static void PlaceProp('):stall.find('private static int LoadSpriteId')]
        self.assertIn('resolved to', prop_log,
                       "PlaceProp must log each prop's own resolved world position")
        self.assertIn('depth(heightOffGround)', prop_log,
                       "PlaceProp must log each prop's resolved draw depth")


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
