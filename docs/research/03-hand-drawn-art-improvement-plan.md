# 03 — Hand-drawn art: what limits it today and the plan to raise it

Synthesis of four research reports (2026-09-14), all in this folder:
- `03a-pixel-art-craft-rules.md` — craft rules from Saint11 (Pedro Medeiros), Pixel Logic, Lospec, Derek Yu, Slynyrd, Pixel Joint; each rule sourced.
- `03b-etg-vanilla-sprite-conventions.md` — what the game and Alexandria actually do (decompiled code + measured vanilla frames).
- `03c-current-pipeline-critique.md` — 20 measured defects in `tools/*.py`, with file/line evidence.
- `03d-pixel-art-tooling-options.md` — editors, pure-Python helpers, lint, references, a project skill.

Decision recorded in `tasks/lessons.md`: sprites stay hand-drawn (row-strings in `tools/*.py`); generated images are references at most.

## 1. The five findings that change the most

| # | Finding | Evidence | Why it matters in game |
|---|---------|----------|------------------------|
| 1 | **The game adds a 1-px black outline to the player sprite and hands at runtime.** Vanilla body frames contain no outline at all (Convict: zero black pixels). We bake a dark-brown outline into every body frame, so in game Pluto wears a 2-px double outline. | 03b §1.4/§3 (`PlayerController.Start` → `SpriteOutlineManager.AddOutlineToSprite`; modding guide: "the game auto-generates the black border, avoid pure black at edges") | Pluto looks heavier and lumpier than the Gungeoneers next to him. Removing the baked outline from body + hand frames is a recolour on export, the cheapest large win. Needs one in-game screenshot to confirm (see §4). |
| 2 | **Frames are anchored bottom-left and the run hop must be drawn inside the canvas.** Vanilla run rises 4 px; our 24x20 canvas has zero headroom, so the −2 px hop clips the ear tips (17 open pixels on run frames 1/4). | 03b §1.2, 03c #2 | Flat-topped ears on every airborne frame. Fix: 24x24 canvas (feet on row 23), taller for item_get / death_shot / pitfall_return. |
| 3 | **Derivation bugs damage every run/dodge frame.** `lean()` drops the last character of rows 4-9 (leading outline of the face missing in all run/tablekick/doorway frames); the dodge ball is rotated as the whole canvas so it bounces 0/2/4/2 px and slides ±2 px; `squash()`/`scale_down()` drop rows so the slide loses the nose and pitfall frames become noise. | 03c #1, #3, #4 (verified in `character_anims.py:59-61, 112-113`, `pixel.py:145-170`) | These are the frames the player sees most. All are small code fixes plus a few hand-drawn keys. |
| 4 | **Palette and markings do not match Pluto.** Fur is caramel (`B` #8E7150, sat 44 %) while the photos and our own spec say grey-brown; ramps only change value (3° hue shift); stripes use the same tone as the automatic rim shadow so they vanish; the sprite's face (white face, tabby cap) contradicts the face card (tabby mask, blaze, spot inside tabby) which matches the photos; the head spot touches the outline and reads as a notch. | 03c #6-#10, 03a §2 | Likeness and 1x readability. One palette edit + one head redraw used by every pose. |
| 5 | **The `shade()` rim pass is textbook banding.** A 1-px tone hugging the outline on every edge = "hugging" banding + pillow shading, the two most-cited beginner mistakes. Vanilla uses flat colour with one shadow tone along one side of a shape. | 03a §0 A1, §1 R8/R9; 03b §3 | Delete the pass; hand-place one shadow shape per mass from a top-left light. |

Smaller but real: `_bw` clips mean *back-view side sprite* (aiming up-diagonal), we map them to the plain side view; the kibble sack is `OneHanded`, so the game shows the `_hand` clips, and vanilla `_hand` means "the body draws its **free** hand" while our `armed()` draws an arm reaching toward the gun; the tail is pinned while the body bobs and flicks 1 px every frame instead of lagging; 32 of 260 frames are exact duplicates; the ghost keeps a 100 % opaque outline on a 75 % body; the preview sheets hide white fur (pasted without a mask) and never show 1x on a floor.

## 2. Target spec (what "vanilla-like" means in numbers)

- Canvas 24x24, feet on row 23, body centred on one column in every frame; extra height only where vanilla needs it (item_get 28, death_shot 28, pitfall_return 26).
- Body 16-18 wide x 20-21 tall, head ≈ 50-55 % of height, 1-px stick legs 2-3 px long, ears 4-5 rows with 2-px pink interiors, tail rings as 2-row bands.
- No baked outline on body and hand frames. Interior seams in the darker tone of the adjacent material. Guns, items, VFX, cards keep their drawn outlines.
- ≤ 10 colours on the body: tabby light/base/shadow (hue-shifted: shadow cooler and greyer, light warmer), stripe near-black, white light/shade, eye green, pink, plus the wet-skin keys for the alt costume.
- No anti-aliasing, no dithering, no automatic rim shading.
- Timing is fixed by Alexandria: idle Loop 6 fps, run Loop 9, dodge Once (fps forced by roll time), death 12, item_get 9, pitfall 15, breach idles 8.
- Idle: 4 frames, feet fixed, head-top squashes 1-2 px, tail and ears lag one frame.
- Run: 6 frames contact → airborne → pass ×2, whole body up 4 px on airborne frames, feet ±3 px on contact, legs tucked in the air, head lags 1 frame, tail counter-sways.
- Dodge: 9 frames crouch → leap → 4 hand-varied ball frames (10-13 px tall, ears/tail/blaze move around the ball) → stretch/land squash → overshoot → idle.
- Death: impact pose first (held), stagger, topple, overshoot 1 px below ground, settle; tail drops last.

## 3. Plan in three passes

### Pass A — fix and re-tune (2.9.0, about a day)
1. Strip the baked outline from body and hand frames on export (`o → transparent`), redraw interior seams in fill tones; keep outlines on guns/items/VFX/cards. Verify in game with one zoomed screenshot next to the Pilot (§4).
2. Canvas 24x24 with headroom; `pad()`/`shift()` raise on dropped pixels; update `validate.py`, `fur.py`, `mock_scene.py`.
3. Fix `lean()`, rotate the ball before padding, per-frame tail offset table with one-frame lag, three tail keys (up / streaming / down), tail beside the body on death, translucent ghost outline.
4. Palette: grey-brown base, hue-shifted 3-tone ramps, stripe key 15+ value points below the shadow, hazel-green eyes. Delete the `shade()` rim pass; hand-place one shadow shape per mass.
5. Canonical head: eyes inside the tabby mask, white blaze between them, muzzle white, spot as a 3x2 oval fully inside tabby one row below the ear bridge, bigger pink ears, forehead M, flank bars; one `EYES` part reused by every pose (fixes the wall-eyed front pose).
6. Preview sheets composited on the three floor tones at 1x/2x/3x with a 14x21 Pilot box, one filmstrip per clip, APNG at the real fps.
7. Minimal lint wired into `make_art.py`: dropped pixels, colour budget, duplicate frames, feet baseline on grounded frames, off-palette keys.

### Pass B — animation keys (2.10.0, one to two days)
1. Run cycle on the vanilla hop: 4-px rise, feet ±3 px, tuck in the air, head lag, tail counter-sway; same for run_down/run_up.
2. Idle as a squash (not a translation) with tail/ear lag and a blink.
3. Dodge: crouch, leap, four hand-drawn ball frames, landing squash, 1-px overshoot.
4. Death: impact-first, topple, overshoot, settle; hand-drawn slide, pitfall (crouch, half-ball, two crosses) and paws-up keys; remove accidental duplicate frames, keep declared holds.
5. Hand semantics: `_hand` = free paw hanging, `_twohands` = both paws, base = none; `_bw` = over-the-shoulder side pose (back stripes, tail on the near side).
6. Regenerate the Puffed Up fur layers from the new frames (fur is derived, no extra drawing).

### Pass C — pipeline and skill (about a day)
1. Parts library with anchors (`HEAD[side|front|back|bw]`, `EARS`, `EYES`, `SPOT`, `BODY`, `LEG`, `TAIL`, `PAW`) and per-frame offset tables per clip; row-strings stay the storage format.
2. `tools/import_png.py`: PNG → rows with an exact fixed-palette snap, so a frame can be touched up in LibreSprite or Pixelorama (both free on macOS) and imported back.
3. Full lint (`tools/lint_art.py`) as a build gate: orphan pixels, open silhouette, 2x2 outline blocks on outlined assets, hugging bands, ramp hue-shift, symmetry of front/back poses, flicker per clip type, mass conservation on squash frames.
4. Project skill `.claude/skills/pluto-pixel-art/` (SKILL.md + palette / specs / animation / checklist references + the scripts) so every future art session starts from these rules.
5. Kibble sack silhouette: pinched grip end, torn spout with spilling kibble, only the red band + purple circle as brand cues at gun scale; the crown and cat move to the Ammonomicon sprite.

## 4. Things to verify in game (Steam machine, one session)
- Zoomed screenshot of Pluto beside the Pilot in the Breach: confirms the double outline today and the fix after Pass A.
- Whether Coco Blue (an AIActor companion) also receives a runtime outline; if yes, strip his baked outline too.
- The Pilot `primaryHand` / `gunAttachPoint` offsets (log once) so the hand sprite and the bag line up.
- The two `[Pluto] punchout ...` log lines (still pending) for the Punch-Out sprites.

## 5. Not doing
- Replacing sprites with generated art (decided). The painted boss card / win pic / icon from Gemini stay in `docs/gen/fit/` as an optional separate decision.
- Anti-aliasing, dithering, 2x-and-downscale for body frames (all three hurt at 20 px per the sources).
- Buying Aseprite: LibreSprite / Pixelorama cover touch-ups; the Python pipeline remains the source of truth.
