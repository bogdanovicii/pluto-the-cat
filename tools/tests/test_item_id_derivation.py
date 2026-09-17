"""
Guards against the Yasupen bug: ItemBuilder.SetupItem (Alexandria 0.5.10) derives the item id it actually
registers under from the GameObject's own name - i.e. the local `string name = "...";` used to build the
GameObject just before the SetupItem call - not from the `ID` constant the file declares. It lowercases that
name and replaces spaces with underscores, but does NOT strip apostrophes.

YasupenItem.cs declared `ID = "pluto:yasupen"` but used `string name = "Yasupen's Price Tag";`, so it actually
registered as "pluto:yasupen's_price_tag". Nothing was ever bound to "pluto:yasupen", so `give pluto:yasupen`
and the Penguin Pals synergy could never have worked, and nothing failed loudly because SetupItem itself
succeeds.

For every `*Item.cs` in PlutoTheCat/src that calls ItemBuilder.SetupItem, this test derives the id the same way
Alexandria does and asserts either:
  - the derived id matches the file's own `ID` constant, or
  - the file renames the mismatch back with Game.Items.Rename(...) (the fix HairballItem.cs and now
    YasupenItem.cs both use).
"""
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / 'PlutoTheCat' / 'src'

ID_RE = re.compile(r'public const string ID\s*=\s*"([^"]+)"')
NAME_RE = re.compile(r'string name\s*=\s*"([^"]+)"\s*;')
RENAME_RE = re.compile(r'Game\.Items\.Rename\(')


def derive_id(display_name):
    """Mirrors Alexandria's ItemBuilder.SetupItem id derivation: idPool + ":" + name.lower().replace(' ', '_')."""
    return 'pluto:' + display_name.lower().replace(' ', '_')


class ItemIdDerivationTests(unittest.TestCase):
    def test_every_item_registers_under_its_own_id_constant(self):
        item_files = sorted(SRC.glob('*Item.cs'))
        self.assertTrue(item_files, 'no *Item.cs files found under ' + str(SRC))

        checked = []
        for path in item_files:
            text = path.read_text(encoding='utf-8')
            if 'ItemBuilder.SetupItem(' not in text:
                continue  # not an Alexandria item (e.g. a helper/controller file)

            id_match = ID_RE.search(text)
            self.assertIsNotNone(id_match, path.name + ' calls ItemBuilder.SetupItem but has no ID constant')
            declared_id = id_match.group(1)

            # SetupItem is called once per Init(); the `name` used to build the GameObject sits above it in
            # source order and is what Alexandria actually keys the id on.
            setup_index = text.index('ItemBuilder.SetupItem(')
            preceding = text[:setup_index]
            name_matches = list(NAME_RE.finditer(preceding))
            self.assertTrue(name_matches, path.name + ' has no `string name = "...";` before ItemBuilder.SetupItem')
            display_name = name_matches[-1].group(1)

            derived_id = derive_id(display_name)
            renamed = RENAME_RE.search(text) is not None

            checked.append(path.name)
            self.assertTrue(
                derived_id == declared_id or renamed,
                '{}: ItemBuilder.SetupItem will register "{}" (derived from name "{}") but ID is "{}", and the '
                'file has no Game.Items.Rename(...) to reconcile them. Either match the ID to the derived id, '
                'or rename it back right after SetupItem (see HairballItem.cs / YasupenItem.cs).'.format(
                    path.name, derived_id, display_name, declared_id))

        # Sanity: make sure this test is actually exercising files, not silently matching nothing.
        self.assertGreaterEqual(len(checked), 10, 'expected at least 10 item files to be checked, got: ' + str(checked))


if __name__ == '__main__':
    unittest.main()
