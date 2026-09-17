"""Execute engine-independent companion, player-kit and config decisions with Mono; engine wiring remains a game check."""
import pathlib
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / 'PlutoTheCat/src'


def run_cases(test, sources, cases):
    for source in sources:
        test.assertTrue(source.exists(), source.name + ' is not implemented')
    if not shutil.which('mcs') or not shutil.which('mono'):
        test.skipTest('Mono compiler/runtime required')
    with tempfile.TemporaryDirectory() as tmp:
        exe = pathlib.Path(tmp) / 'tests.exe'
        subprocess.run(['mcs', '-out:' + str(exe)] + [str(s) for s in sources] + [str(cases)], check=True)
        subprocess.run(['mono', str(exe)], check=True)


class CompanionKitTests(unittest.TestCase):
    def test_companion_decisions(self):
        run_cases(self, [SRC / 'CompanionKitRules.cs'], ROOT / 'tools/tests/companion_kit_cases.cs')

    def test_player_kit_and_config_rules(self):
        run_cases(self, [SRC / 'PlayerKitRules.cs', SRC / 'PlutoConfigRules.cs'], ROOT / 'tools/tests/player_kit_cases.cs')

    def test_cat_item_rules(self):
        run_cases(self, [SRC / 'CatItemRules.cs'], ROOT / 'tools/tests/cat_item_cases.cs')

    def test_yasupen_rules(self):
        run_cases(self, [SRC / 'YasupenRules.cs'], ROOT / 'tools/tests/yasupen_cases.cs')

    def test_cat_set_rules(self):
        run_cases(self, [SRC / 'CatSetRules.cs'], ROOT / 'tools/tests/cat_set_cases.cs')

    def test_yasupen_wiring(self):
        src = (SRC / 'YasupenItem.cs').read_text(encoding='utf-8')
        for needle in ('YasupenRules.SlideReady(', 'YasupenRules.BargainCasings(', 'YasupenRules.PriceMultiplier(',
                       'StatType.GlobalPriceMultiplier', 'OnRoomClearEvent', 'CanBePet = true',
                       'BehaviorOverridesVelocity = false', '"slide"', '"cheer"'):
            self.assertIn(needle, src, needle)
        plugin = (SRC / 'Plugin.cs').read_text(encoding='utf-8')
        self.assertIn('Step("yasupen", YasupenItem.Init)', plugin)
        synergies = (SRC / 'PlutoSynergies.cs').read_text(encoding='utf-8')
        self.assertIn('Register(PenguinPals, new List<string> { CocoBlueItem.ID, YasupenItem.ID });', synergies)
        self.assertIn('PlutoSynergies.PenguinPals', src)

    def test_numeric_config_is_clamped_at_bind(self):
        """Wiring check: every numeric setting goes through PlutoConfigRules when it is bound."""
        text = (SRC / 'PlutoConfig.cs').read_text()
        cat_set_keys = (
            'SprayClip', 'SprayCooldown', 'SprayRange', 'SprayDamage', 'SprayKnockback',
            'SprayFlinchChance', 'SprayFlinchSeconds', 'SprayReloadSeconds', 'SprayCharmBonusSeconds',
            'SprayCharmMaxSeconds',
            'FeatherChargeSeconds', 'FeatherClip', 'FeatherRange', 'FeatherDamage',
            'FeatherDistractSeconds', 'FeatherBossSlowSeconds', 'FeatherReloadSeconds',
            'TPRechargeDamage', 'TPLength', 'TPSeconds', 'TPHits', 'TPConfettiDamage',
            'ConeCooldown', 'ConeArcDegrees', 'ConeRadius', 'ConeCocoStuffing',
            'CoffeeRechargeDamage', 'CoffeeRange', 'CoffeeShardCount', 'CoffeeShardDamage',
            'CoffeeSlowSeconds', 'CoffeeZoomiesBonusSeconds',
        )
        self.assertIn('const string S = "Cat Set 2.19";', text)
        for key in cat_set_keys:
            self.assertRegex(text, r'public static (?:int|float) ' + key + r'\s*=')
            self.assertIn('cfg.Bind(S, "%s"' % key, text)
        unranged = {'NoFallDamage', 'Hairball', 'ChuruDrop', 'FoyerPosition', 'BathtubOffset', 'CocoBlocksBullets',
                    'LogPunchoutNames', 'UnlockSamuraiCostume'}
        bound = 0
        for line in text.splitlines():
            match = re.search(r'cfg\.Bind\("[^"]+", "(\w+)"', line)
            if not match:
                continue
            bound += 1
            key = match.group(1)
            if key in unranged:
                continue
            self.assertIn('PlutoConfigRules.Clamp("%s"' % key, line, key + ' is bound without range validation')
        self.assertGreater(bound, 30)


    def test_helmet_swap_writes_prefix(self):
        # Coco's clips are DirectionType.Single: the game plays DirectionalAnimation.Prefix and ignores AnimNames,
        # so a helmet swap that only rewrites AnimNames[0] never shows (2.16.4 in-game report).
        src = (ROOT / 'PlutoTheCat/src/CocoBlueItem.cs').read_text(encoding='utf-8')
        start = src.index('private static void SetClip(')
        body = src[start:src.index('}', src.index('{', start)) + 1]
        self.assertIn('anim.Prefix = clip', body)

if __name__ == '__main__':
    unittest.main()
