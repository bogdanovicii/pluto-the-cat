"""Source-level wiring checks for the Shrine Stall 2.20 per-save unlock store."""
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / 'PlutoTheCat' / 'src'


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


if __name__ == '__main__':
    unittest.main()
