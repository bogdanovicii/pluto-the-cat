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


if __name__ == '__main__':
    unittest.main()
