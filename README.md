# Pluto the Cat — Enter the Gungeon mod

A BepInEx / Alexandria mod that adds Pluto (a real chunky tabby-and-white cat) as a playable Gungeoneer with a kibble-flinging starter gun and a wet-food active that charms every enemy, bosses included.

## Layout

| Path | What |
|---|---|
| `PlutoTheCat/` | C# plugin (net35). `src/` code, `Characters/Pluto/` character data + art, `Resources/` gun/item art. All art is embedded in the DLL. |
| `tools/` | Python art pipeline. `poses.py` holds the hand-drawn key poses as ASCII pixel maps, `character_anims.py` derives every animation clip, `ui_and_items.py` the cards/gun/item art, `make_art.py` writes the PNGs, `validate.py` checks the package. |
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

Edit the ASCII maps in `tools/poses.py` or `tools/ui_and_items.py`, run `python3 tools/make_art.py`, and look at `docs/art-preview/*.png`. Palette keys are documented in `tools/pixel.py`.

## In-game checklist (not yet verified, game not installed on the build machine)

1. Console shows `[Pluto] Pluto the Cat is ready. Meow.` with no red errors.
2. Pluto stands in the Breach near the other Gungeoneers; his select card shows his face.
3. Sprites render in all directions, dodge roll curls into a ball, death lies him down.
4. Royal Kibble Sack fires kibble that bounces once. Infinite ammo.
5. Wet Food Can lobs a can; on landing nearby enemies get hearts and fight each other. Test on a boss.
6. If Pluto overlaps another modded character in the Breach, change `FoyerPosition` in `PlutoTheCat/src/Plugin.cs`.
