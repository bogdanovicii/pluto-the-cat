---
name: pluto-pixel-art
description: Rules, palette, canvas specs, animation timing and the check/preview workflow for drawing or changing any sprite of the Pluto the Cat mod (Enter the Gungeon). Use whenever editing tools/*.py art, poses, clips, items, guns, VFX, cards or previews.
---

# Pluto pixel art

Every sprite is hand-authored as row-strings of palette keys in `tools/*.py` and rendered by
`tools/make_art.py`. Generated images are never sprites (the user compared and chose hand-drawn).

## Workflow

1. Edit rows in `tools/poses.py` (heads, bodies, legs, paw), `tools/poses_extra.py` (ball, low poses,
   tip, lying, tails, props), `tools/character_anims.py` (clip derivation), `tools/art_v3.py` /
   `art_v4.py` / `art_v5.py` (items, guns, companion, VFX, cards).
2. `python3 tools/lint_art.py` — must report 0 errors (size, outline margin, feet row, colours, holds, orphans).
3. `python3 tools/make_art.py` — regenerates every PNG, the fur layers and the previews in `docs/art-preview/`
   (`character-sheet.png`, `breach-and-variants.png`, `scale-check.png`, `anim/*.png` APNGs at real fps).
4. Look at the previews at 1x on the three floor tones before judging anything; the game adds the
   black outline, and the previews simulate it.
5. `python3 tools/validate.py`, then `./build.sh`.

To touch a frame up in an editor: export it, edit at 1x, `python3 tools/import_png.py frame.png --outline`
and paste the rows back. Row-strings stay the source of truth.

## Hard rules (from docs/research/03a, 03b, 03c)

- Body, breach and hand frames ship WITHOUT an outline: the game draws a 1-px black outline at
  runtime around the player sprite. Keep `o` in the rows (it marks the silhouette for tools) — the
  exporter strips it. Guns, items, VFX and cards keep their drawn outlines.
- Canvas 24x26, pose 18x22 at (3, 4). Frames are anchored bottom-left: feet fill on row 24 for every
  grounded frame, fill never touches the canvas edge (1-px margin for the outline), hops move pixels
  UP inside the canvas (4 px for the run).
- `pad` / `overlay` raise `DroppedPixels` when art leaves the canvas. Never silence it for body art;
  `allow_drop=True` only for things that really leave (sinking into a pit).
- Three tones per material, hue-shifted (shadow cooler and greyer, light warmer). No automatic rim
  shading, no anti-aliasing, no dithering on anything that animates. One shadow shape per mass from a
  top-left light. Interior seams use the darker tone of the material, never `o`.
- One head part per view (`HEAD_SIDE`, `HEAD_FRONT`, `HEAD_BACK`, `HEAD_BW`); eyes via `eyes()`,
  never hand-copied. Markings: tabby mask around the eyes, white blaze between the eyes down to the
  white muzzle, white 3x2 oval on the crown fully surrounded by tabby, big pink ears, forehead M,
  mackerel bars, ringed tail (base tone / near-black bands, 2 rows each).
- No accidental duplicate frames: identical consecutive frames must be declared holds in `lint_art.HOLDS`.
- Timing is fixed by Alexandria (see reference/animation.md); frame counts are free.

Details: [reference/palette.md](reference/palette.md), [reference/specs.md](reference/specs.md),
[reference/animation.md](reference/animation.md), [reference/checklist.md](reference/checklist.md).
