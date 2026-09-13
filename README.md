# Pluto the Cat — Enter the Gungeon mod

A BepInEx / Alexandria mod that adds Pluto (a real chunky tabby-and-white cat) as a playable Gungeoneer with a kibble-flinging starter gun and a wet-food active that charms every enemy, bosses included.

## Layout

| Path | What |
|---|---|
| `PlutoTheCat/` | C# plugin (net35). `src/` code, `Characters/Pluto/` character data + art, `Resources/` gun/item art. All art is embedded in the DLL. |
| `tools/` | Python art pipeline. `poses.py` holds the hand-drawn parts (heads, bodies, legs, paw) and key poses as ASCII pixel maps, `poses_extra.py` the ball/low/lying poses and tails, `character_anims.py` derives every animation clip on the 24x26 canvas, `art_v3.py`/`art_v4.py`/`art_v5.py` + `ui_and_items.py` the cards/gun/item/companion/VFX art, `fur.py` the Puffed Up fur layers, `lint_art.py` the art checks, `preview.py` the game-like previews, `make_art.py` writes the PNGs, `validate.py` checks the package, `import_png.py` brings an edited PNG back to rows. |
| `thunderstore/` | `manifest.json`, `README.md`, `CHANGELOG.md`, `icon.png` for the Thunderstore/r2modman package. |
| `docs/` | Design spec (`superpowers/specs/`), research reports (`research/`), art preview sheets (`art-preview/`). |
| `reference/photos/` | Photos of Pluto the art is based on. |
| `dist/` | Build output: `Pluto_The_Cat-<version>.zip`. |

## Build

Needs Mono (msbuild + nuget), Python 3 and Pillow. Reference assemblies come from the BepInEx NuGet feed, so the game does not need to be installed.

```bash
./build.sh
```

That regenerates the art, restores packages, compiles, validates, and writes `dist/Pluto_The_Cat-1.0.0.zip`.

## Install in r2modman

r2modman → Settings → Import local mod → choose the zip. Dependencies (BepInExPack_EtG, Mod the Gungeon API, Alexandria) are declared in the manifest.

## Editing the art

Everything is hand-drawn as row-strings of palette keys (`tools/pixel.py` documents the keys). The rules,
palette, canvas specs, animation timing and a checklist live in `.claude/skills/pluto-pixel-art/`
(also readable as plain Markdown). The short version:

- Body frames are exported **without** an outline: the game draws the 1-px black outline itself.
  Keep `o` in the rows (it marks the silhouette for the tools); `make_art.py` strips it. Items, guns,
  VFX and cards keep their drawn outline.
- Canvas 24x26, feet fill on row 24, 4 px of headroom for the run hop. `pad`/`overlay` raise if a
  pixel would leave the canvas.
- `python3 tools/lint_art.py` (sizes, outline margin, feet row, colour budget, holds, orphans, flicker)
  then `python3 tools/make_art.py`; look at `docs/art-preview/` (`scale-check.png` at 1x on three
  floors, `character-sheet.png`, `breach-and-variants.png`, `anim/*.png` animated at the real fps).
- Research behind the rules: `docs/research/03-hand-drawn-art-improvement-plan.md` and `03a`–`03d`.

## In-game checklist (not yet verified, game not installed on the build machine)

1. Console shows `[Pluto] Pluto the Cat is ready. Meow.` with no red errors.
2. Pluto stands in the Breach near the other Gungeoneers; his select card shows his face.
3. Sprites render in all directions, dodge roll curls into a ball, death lies him down.
4. Royal Kibble Sack fires kibble that bounces once. Infinite ammo.
5. Wet Food Can lobs a can; on landing nearby enemies get hearts and fight each other. Test on a boss.
6. If Pluto overlaps another modded character in the Breach, change `FoyerPosition` in `PlutoTheCat/src/Plugin.cs`.
