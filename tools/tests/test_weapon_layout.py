"""The generated WeaponLayout.cs constants equal the exported art's grip/muzzle pixels (tools/weapon_layout.py is the source)."""
import json
import pathlib
import re
import sys
import unittest

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import weapon_layout as WL  # noqa: E402

WC = ROOT / 'PlutoTheCat/Resources/SpriteRoot/WeaponCollection'
SRC = ROOT / 'PlutoTheCat/src'


def cs_constants():
    text = WL.CS_PATH and pathlib.Path(WL.CS_PATH).read_text()
    consts = {}
    for name, value in re.findall(r'(\w+) = ([0-9.]+)f?[,;]', text):
        consts[name] = float(value) if '.' in value else int(value)
    return consts


def attach(path):
    pts = json.loads(path.read_text())['attachPoints']
    return {p['name']: (round(p['position']['x'] * 16, 6), round(p['position']['y'] * 16, 6)) for p in pts if 'position' in p}


def opaque_near(im, x, y):
    """Any drawn pixel in the 3x3 around bottom-left pixel (x, y)."""
    w, h = im.size
    return any(im.getpixel((xx, h - 1 - yy))[3] > 0
               for xx in range(max(0, x - 1), min(w, x + 2)) for yy in range(max(0, y - 1), min(h, y + 2)))


class WeaponLayoutTests(unittest.TestCase):
    def test_generated_file_is_current(self):
        self.assertEqual(pathlib.Path(WL.CS_PATH).read_text(), WL.layout_cs(), 'run tools/make_art.py')

    def test_constants_equal_the_exported_art(self):
        consts = cs_constants()
        for key, spec in WL.WEAPONS.items():
            p = key.upper()
            frames = sorted(WC.glob(spec['sprite'] + '_*.png'))
            self.assertTrue(frames, key + ': no exported frames')
            for png in frames:
                pts = attach(png.with_suffix('.jtk2d'))
                self.assertEqual(pts['PrimaryHand'], (consts[p + '_HAND_X'], consts[p + '_HAND_Y']), png.name)
                self.assertEqual(pts['Casing'], (consts[p + '_MUZZLE_X'], consts[p + '_MUZZLE_Y']), png.name)
                im = Image.open(png).convert('RGBA')
                if '_fire_' in png.name and p + '_SWING_H' in consts:
                    self.assertEqual(im.size, (consts[p + '_SWING_W'], consts[p + '_SWING_H']), png.name)
                    grip = (consts[p + '_SWING_GRIP_X'], consts[p + '_SWING_GRIP_Y'])
                else:
                    self.assertEqual(im.size, (consts[p + '_W'], consts[p + '_H']), png.name)
                    grip = (consts[p + '_HAND_X'], consts[p + '_HAND_Y'])
                if '_reload_' not in png.name:   # reload poses may move the handle away from the grip
                    self.assertTrue(opaque_near(im, *grip), png.name + ': grip is on empty pixels')
            idle = Image.open(WC / (spec['sprite'] + '_idle_001.png')).convert('RGBA')
            self.assertTrue(opaque_near(idle, consts[p + '_MUZZLE_X'], consts[p + '_MUZZLE_Y']), key + ': muzzle is on empty pixels')

    def test_runtime_numbers_unchanged(self):
        """Values the gun classes used before centralisation (2.16.2)."""
        c = cs_constants()
        self.assertEqual((c['KIBBLE_SACK_MUZZLE_X'], c['KIBBLE_SACK_MUZZLE_Y']), (29, 9))
        self.assertEqual((c['TAIYAKI_CANNON_MUZZLE_X'], c['TAIYAKI_CANNON_MUZZLE_Y']), (46, 15))
        self.assertEqual((c['KATANA_MUZZLE_X'], c['KATANA_MUZZLE_Y']), (41, 13))
        self.assertEqual(c['KATANA_SWING_GRIP_OFFSET'], 27)
        self.assertEqual(c['KATANA_SWING_GRIP_Y'] - c['KATANA_HAND_Y'], c['KATANA_SWING_GRIP_OFFSET'])
        self.assertEqual(c['KATANA_CASING_REACH_UNITS'], 2.4)

    def test_gun_classes_read_the_layout(self):
        for cs, key in (('KibbleSackGun.cs', 'KIBBLE_SACK'), ('TaiyakiCannonGun.cs', 'TAIYAKI_CANNON'), ('KatanaGun.cs', 'KATANA')):
            text = (SRC / cs).read_text()
            self.assertIn('WeaponLayout.%s_MUZZLE_X / 16f, WeaponLayout.%s_MUZZLE_Y / 16f' % (key, key), text, cs)
            self.assertNotRegex(text, r'barrelOffset[^;]*\d+f / 16f', cs + ' hard-codes barrel pixels')
        katana = (SRC / 'KatanaGun.cs').read_text()
        self.assertIn('SwingGripOffsetPixels = WeaponLayout.KATANA_SWING_GRIP_OFFSET', katana)
        self.assertIn('CasingReachUnits = WeaponLayout.KATANA_CASING_REACH_UNITS', katana)

    def test_validate_uses_one_shared_gun_manifest(self):
        text = (ROOT / 'tools/validate.py').read_text()
        self.assertIn('GUN_MANIFEST = (', text)
        self.assertIn('for gun_name, clips in GUN_MANIFEST:', text)
        self.assertNotIn("for gun_name in ('pluto_kibble_sack', 'pluto_taiyaki_cannon', 'pluto_katana')", text)
        for gun in ('pluto_kibble_sack', 'pluto_taiyaki_cannon', 'pluto_katana',
                    'pluto_spray_bottle', 'pluto_feather_teaser'):
            self.assertIn("('" + gun + "',", text)


if __name__ == '__main__':
    unittest.main()
