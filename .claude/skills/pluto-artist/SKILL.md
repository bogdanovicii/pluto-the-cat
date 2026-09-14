---
name: pluto-artist
description: Create and review art for the Pluto the Cat Enter the Gungeon mods (main mod and Vet Visit) - boss-intro cards, portraits, win pictures, icons, gun/item/projectile sprites, costume art, UI pieces. Generates with Gemini first using reference images, copies that art faithfully into pixel-perfect game art (fixed palette, clean outline, hard alpha, integer scale), then reviews it with automated checks, a rubric and an in-game mock before anyone sees it. Use this whenever the task involves making, redrawing, improving, fixing or judging any picture for Pluto, Coco, the Vet or their items, even if the user only says "the card looks bad", "improve the art" or "make a sprite for X". For animation frame timing and the row-string body pipeline, pair it with pluto-pixel-art.
---

# Pluto artist

The user's standard (2026-09-14): every piece is **pixel-perfect good art**. Start from a Gemini generation that
matches the reference style, copy it as faithfully as possible into pixels, and only show work that passed review.
Procedural or quick hand-drawn stand-ins for large art were rejected ("does not look good") - don't show them.

Scope split with `pluto-pixel-art`: in-game body frames (Pluto 24x26, Coco) stay row-strings in `tools/*.py`
(the user chose hand-drawn sprites over pixelized generations at sprite size). Everything larger - boss cards,
portraits, win pictures, icons, item art that reads as an illustration - goes through this skill. For a small
sprite (gun, item, projectile) generate a reference with Gemini, then copy it by hand into rows or with
`pixelize.py` at the exact size, whichever reviews better.

## 1. Brief (write it down before generating)

- **Target**: which file, exact canvas, where the game draws it and on top of what. Read `references/targets.md`;
  if the target isn't there, find how the game renders it (decompiled source, a working mod's file) and add it.
  The boss card bug happened because a size table was trusted instead of the renderer.
- **References**: Pluto photos `reference/photos/`, user examples (e.g. `boss card example.jpg`), the current
  in-game sprite, the style target (vanilla art the piece sits next to). Gemini copies what it is shown far better
  than what it is told.
- **Palette**: start from `.claude/skills/pluto-pixel-art/reference/palette.md`; add ramps only with a reason.

## 2. Generate

```bash
python3 .claude/skills/pluto-artist/scripts/gemini_image.py \
  --prompt-file brief.txt --ref reference/photos/<photo>.jpeg --ref "boss card example.jpg" \
  --ratio 16:9 --size 2K --candidates 3 --out reference/gemini/<piece>/<piece>.png
```

Prompt structure that works: (1) what the image is and where it is used, (2) "match the attached reference
exactly" for style and for the character, (3) subject description (Pluto block in `references/targets.md`),
(4) pose/composition with the transparent/empty regions spelled out, (5) rendering rules: crisp pixel art,
bold dark outline, cel shading, no gradients, no anti-aliasing, plain flat background colour for easy removal.
Default model `gemini-3-pro-image`; `gemini-3.1-flash-image` for fast iterations. Generate 2-4 candidates.

Pick with the rubric (`references/rubric.md`), not by first impression. If none passes on character accuracy
(wrong fur colour, missing head spot, orange cat), fix the prompt/refs and regenerate instead of repairing pixels.

## 3. Copy into pixels

```bash
python3 .claude/skills/pluto-artist/scripts/pixelize.py reference/gemini/<piece>/<piece>.png \
  --crop 0.02,0.30,0.48,1.0 --grid 180x150 --bg auto --colors 24 --outline 1E1614 \
  --canvas 427x240 --place=-8,98 --out build/<piece>.png
```

Negative values need the `=` form (`--place=-8,98`), or argparse reads them as a new flag.

- Choose the grid so one art pixel is 1-2 target pixels. Never scale a small sprite up to fill a big target;
  that is exactly the "blown-up blocky" look the user rejected.
- `--colors N` builds a palette from the image; `--palette file.txt` (hex per line) snaps to a fixed palette
  instead. Cells take their majority colour, so edges stay hard.
- Then clean by hand where the conversion guessed: eyes, pupils, mouth, outline gaps, single stray pixels.
  Edit the PNG at 1x (any pixel editor, or PIL point edits in a small script); keep the script if you used one.

## 4. Review (required before showing anyone)

```bash
python3 .claude/skills/pluto-artist/scripts/review_art.py build/<piece>.png --kind bosscard \
  --mock "Screenshot ... .png" --mock-rect 438,0,3000,1440 --out build/<piece>_review.png
```

It fails on semi-transparent pixels, too many colours, stray pixels, broken integer scaling and target rules
(boss card opacity, name area, placement). Then look at the review sheet yourself against every line of
`references/rubric.md` and write the verdict (pass / fix list). Only a pass goes to the user, shown in the
in-game mock next to what it replaces.

## 5. Ship

- Keep the chosen generation, the prompt (sidecar json) and the conversion command in `reference/gemini/<piece>/`.
- Approved final art lives in the repo as the source (e.g. `reference/art/<piece>/final.png`); `tools/make_art.py`
  copies it to the resource path, so a regeneration never silently replaces approved art.
- Run `tools/make_art.py`, `tools/validate.py` (it enforces the boss card rules), `./build.sh`.
- Coordinate shared files with the other sessions before editing (see project memory).
