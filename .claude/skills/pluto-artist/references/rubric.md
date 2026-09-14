# Review rubric

Score every line pass / fix. A piece ships only when every line passes. Write the fix list in concrete terms
("left pupil is 2 px wide, make it a 1 px slit"), never "looks off".

## Character accuracy (Pluto)
- Grey-brown taupe tabby, NOT orange or ginger; near-black mackerel stripes; forehead M.
- White blaze between the eyes down to a white muzzle, chest and paws.
- Small white oval spot on the crown, fully surrounded by tabby.
- Big ears with pink inner ear; hazel-green eyes with vertical slit pupils; pink nose.
- Long raccoon-ringed tail (base / near-black bands, dark tip) when visible.
- Proportions: chunky, round, a cat - not a human with a cat head (unless the brief says costume/biped).
- Compare side by side with `reference/photos/` and the current in-game sprite; name any mismatch.

## Style match
- Sits next to the art it shares the screen with (vanilla boss cards, Gungeon sprites) without looking pasted:
  same outline weight, same shading depth, same level of detail at the displayed size.
- Cel shading: 2-4 tones per material, hue-shifted (shadows cooler/greyer, lights warmer); one light direction
  (top-left) across the whole piece.
- Bold, consistent dark outline around the silhouette; interior lines use darker tones of the material.

## Pixel craft
- Alpha only 0/255; no anti-aliased edges, no blurred or smeared areas left from the generation.
- No stray pixels, no jaggy staircases on curves (use consistent step lengths), no banding (parallel same-length
  steps across tones), no pillow shading.
- Integer scale only; one art pixel is the same size everywhere.
- Controlled palette (see the kind limits in review_art.py); no near-duplicate colours.
- Small features (eyes, nose, mouth, fingers/toes, labels) are placed by hand and read at 1x.

## Composition for the target
- Placement and size follow `references/targets.md` (bleed edges, empty regions, what it must not cover).
- Reads at the size the game shows it: check the in-game mock, not just the zoom.
- Silhouette readable as a solid shape (squint test).

## Before showing the user
- The review sheet (1x dark/light, zoom, in-game mock) is attached.
- Show it next to what it replaces, and say what changed.
