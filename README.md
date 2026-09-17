# Pluto the Cat — Enter the Gungeon mod

A BepInEx / Alexandria mod that adds Pluto (a real chunky tabby-and-white cat) as a playable Gungeoneer. Current
version: **2.20.0** (`thunderstore/manifest.json`, `PlutoTheCat/src/Plugin.cs`). Player-facing feature list:
`thunderstore/README.md`; full history: `thunderstore/CHANGELOG.md`.

What ships today, in short:

- **Pluto**: Royal Kibble Sack (starter gun), Wet Food Can (thrown tin that charms, stuns bosses), Squeaky Toy
  (second active: sends Coco out as a decoy), Nine Lives (starts on his seventh life), Puffed Up, cat reflexes and no
  pit damage.
- **Coco Blue**: plush companion that blocks enemy bullets, can be knocked out and petted; synergies Playdate,
  Squire and Knighted.
- **Yasupen** (loot pool, 2.18.0): Donpen's twin brother. Belly slides, a shop discount and miracle bargains; Penguin Pals with Coco Blue.
- **Cat set** (loot pool, 2.19.0): Spray Bottle (gun, C: mist that flinches and leaves water), Feather Teaser (gun, B:
  charged returning lure that distracts enemies), Toilet Paper Roll (active, C: bullet-blocking streamer), Cone of Shame
  (passive, B: blocks a bullet in front every 3 s) and Coffee Mug (active, C: shatters into shards and a slowing
  puddle). No piece hits a harmless or charmed enemy: the mist, mug and shards pass through them. Synergies Bath Time
  (+ Wet Food Can: tops a charm up by `SprayCharmBonusSeconds` per mist, up to `SprayCharmMaxBonusSeconds` (6 s)
  added to that charm however long it already was, without damaging the charmed enemy), Playtime (+ Ball of Yarn: the tangle wins over the feather, so a tangled enemy stops
  instead of chasing), Shredder (+ Scratching Post), Matching Cones (+ Coco Blue) and Espresso (+ Catnip Pouch). Every
  number is in the config section `Cat Set 2.19`; in-game checklist `docs/cat-set-2190-test-checklist.md`.
- **Shrine Stall** (Breach, 2.20.0): Daifuku (a ginger cat) and Kinsuke (a koi in a bowl) run a stall beside the
  Breach shop, under a red torii gate. **The ten cat items above (the five-piece cat set and Yasupen's items are
  unaffected; specifically Ball of Yarn, Catnip Pouch, Hairball, Scratching Post, Toilet Paper Roll, Coffee Mug,
  Jingle Bell Collar, Cone of Shame, Spray Bottle and Feather Teaser no longer drop until unlocked at the stall**,
  a permanent per-save purchase for 8 or 15 Hegemony credits depending on the item. Buying one unlocks that item
  for good — it then drops normally in the Gungeon; the purchase is the unlock and does not also hand a copy
  over. The mat shows the first three still-locked items in a fixed order, not a fresh roll per visit. Config section
  `Shrine Stall 2.20` (prices, stall position, `StallUnlocksDisabled` to unlock everything for testing); in-game
  checklist `docs/shrine-stall-2200-test-checklist.md`.
- **Samurai Pluto** (alternate costume, 2.16.0): unlocked by beating Pluto's past (the Vet Visit), switched at the
  kimono stand in the Breach. Starts with the **Taiyaki Cannon** and the **Katana** instead of the kibble sack, and has
  his own boss-intro card.
- **The Vet Visit** (Pluto's past) is a separate plugin and package in `PlutoVetVisit/` (0.14.2); see its README.

## Layout

| Path | What |
|---|---|
| `PlutoTheCat/` | C# plugin (net35). `src/` code (plugin, config, guns, items, Coco, synergies, patches), `Characters/Pluto/` character data and art (`newspritesetup/` default skin, `newaltspritesetup/` samurai costume, cards, punchout), `Resources/` companion, fur, item, gun and VFX art. All art is embedded in the DLL. |
| `tools/` | Python art pipeline. `pixel.py` palette and helpers, `poses.py`/`poses_extra.py` hand-drawn key poses, `character_anims.py` every animation clip on the 24x26 canvas, `samurai.py` the costume clips, `art_v3.py`/`art_v4.py`/`art_v5.py` + `ui_and_items.py` cards, guns, items, Coco and VFX, `fur.py` Puffed Up fur, `lint_art.py` art checks, `preview.py`/`mock_scene.py`/`mock_anim.py` game-like previews, `gen_art.py`/`pixelize.py` Gemini references, `make_art.py` writes the PNGs, `validate.py` checks the package, `import_png.py` brings an edited PNG back to rows. |
| `tools/tests/` | Unit tests. `test_companion_kit.py` compiles the engine-independent rule classes from `PlutoTheCat/src/` with the `*_cases.cs` files and runs them with Mono (`mcs`, `mono`); engine wiring still needs a game check. |
| `thunderstore/` | `manifest.json`, `README.md`, `CHANGELOG.md`, `icon.png`, `pluto_check.sh` for the Thunderstore / r2modman package. |
| `PlutoVetVisit/` | The Vet Visit past: its own git repo, build and package (see `PlutoVetVisit/README.md`). |
| `docs/` | Design specs and plans (`superpowers/`), research (`research/`), art previews (`art-preview/`), tester checklists. Documents marked **Historical** at the top describe older versions. |
| `.claude/skills/` | `pluto-pixel-art` (palette, canvas, timing rules) and `pluto-artist` (Gemini-first art workflow). |
| `reference/photos/` | Photos of Pluto the art is based on. |
| `dist/`, `releases/` | Build output `Pluto_The_Cat-<version>.zip`, and the zips kept per release. |

## Requirements

- Mono (msbuild, nuget, mcs). Reference assemblies come from the BepInEx NuGet feed (`PlutoTheCat/nuget.config`,
  `packages.config`), so the game does not need to be installed. The plugin targets .NET 3.5 like the game.
- Python 3 with the pinned packages: `python3 -m pip install -r requirements.txt` (Pillow).

## Build and test

```bash
python3 -m unittest discover -s tools/tests
./build.sh
```

`build.sh` regenerates the art, restores packages, compiles, validates and writes
`dist/Pluto_The_Cat-<version>.zip` (the version comes from `thunderstore/manifest.json`). It does not run the unit
tests; run them first.

## Install in r2modman

r2modman → Settings → Import local mod → choose the zip. Dependencies (BepInExPack_EtG, Mod the Gungeon API,
Alexandria) are declared in the manifest. To play the past and unlock the costume, also import the Vet Visit zip.

## Editing the art

Everything drawn by hand is row-strings of palette keys (`tools/pixel.py` documents the keys). Large pictures (cards,
win pictures) are generated with Gemini first and converted into pixel art with the `pluto-artist` skill. The rules,
palette, canvas specs, animation timing and a checklist live in `.claude/skills/pluto-pixel-art/` (plain Markdown).
The short version:

- Body frames are exported **without** an outline: the game draws the 1-px black outline itself. Keep `o` in the rows
  (it marks the silhouette for the tools); `make_art.py` strips it. Items, guns, VFX and cards keep their drawn outline.
- Canvas 24x26, feet fill on row 24, 4 px of headroom for the run hop. `pad`/`overlay` raise if a pixel would leave
  the canvas.
- `python3 tools/lint_art.py` (sizes, outline margin, feet row, colour budget, holds, orphans, flicker) then
  `python3 tools/make_art.py`; look at `docs/art-preview/`.

## Checking a build in game

The build Mac has no game. On the test machine, `thunderstore/pluto_check.sh` greps the BepInEx log and prints
PASS/FAIL; the console should show `[Pluto] Pluto the Cat is ready. Meow.` with no red errors. Record what was
actually seen per build; older checklists in `docs/` are historical.
