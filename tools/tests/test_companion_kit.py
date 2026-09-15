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

    def test_numeric_config_is_clamped_at_bind(self):
        """Wiring check: every numeric setting goes through PlutoConfigRules when it is bound."""
        text = (SRC / 'PlutoConfig.cs').read_text()
        unranged = {'NoFallDamage', 'Hairball', 'FoyerPosition', 'BathtubOffset', 'CocoBlocksBullets',
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


if __name__ == '__main__':
    unittest.main()
