"""Execute engine-independent companion decisions with Mono; engine wiring remains a game check."""
import pathlib
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]

class CompanionKitTests(unittest.TestCase):
    def test_companion_decisions(self):
        helper = ROOT / 'PlutoTheCat/src/CompanionKitRules.cs'
        self.assertTrue(helper.exists(), 'Companion decision helper is not implemented')
        if not shutil.which('mcs') or not shutil.which('mono'):
            self.skipTest('Mono compiler/runtime required')
        with tempfile.TemporaryDirectory() as tmp:
            exe = pathlib.Path(tmp) / 'tests.exe'
            subprocess.run(['mcs', '-out:' + str(exe), str(helper), str(ROOT / 'tools/tests/companion_kit_cases.cs')], check=True)
            subprocess.run(['mono', str(exe)], check=True)

if __name__ == '__main__':
    unittest.main()
