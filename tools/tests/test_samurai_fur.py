"""Puffed Up fur for the samurai costume: fur grows from fur, never from kimono cloth (tools/fur.py KIMONO)."""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import fur as F  # noqa: E402


def spikes(layer):
    return sum(ch != '.' for row in layer for ch in row)


class SamuraiFurTests(unittest.TestCase):
    def test_cloth_never_grows_fur(self):
        cloth = ['.' * 24] * 6 + ['.' * 6 + 'o' + '5' * 10 + 'o' + '.' * 6] * 8 + ['.' * 24] * 6
        for v in range(4):
            self.assertEqual(spikes(F.fur_layer(cloth, v)), 0, 'kimono cloth grew fur (variant %d)' % v)

    def test_tabby_still_grows_fur(self):
        tabby = ['.' * 24] * 6 + ['.' * 6 + 'o' + 'B' * 10 + 'o' + '.' * 6] * 8 + ['.' * 24] * 6
        self.assertGreater(spikes(F.fur_layer(tabby, 2)), 0)

    def test_samurai_set_covers_the_standing_clips_with_fur(self):
        sam = F.all_samurai_fur()
        normal = F.all_fur()
        self.assertEqual(set(sam), set(normal), 'samurai fur must cover the same clips as the normal set')
        for clip in ('idle', 'run_right', 'idle_forward'):
            self.assertTrue(all(spikes(layers[2]) > 0 for layers in sam[clip]), clip + ': a frame has no samurai fur')
            ratio = sum(spikes(l[2]) for l in sam[clip]) / max(1, sum(spikes(l[2]) for l in normal[clip]))
            self.assertLess(ratio, 1.0, clip + ': the kimono should hide some of the fur')


if __name__ == '__main__':
    unittest.main()
