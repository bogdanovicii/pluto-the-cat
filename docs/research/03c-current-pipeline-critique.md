# 03c — Critique of the current sprite pipeline (tools/*.py) and what limits the art

Reviewed 2026-09-14 against: `tools/pixel.py`, `poses.py`, `poses_extra.py`, `character_anims.py`, `art_v3.py`,
`art_v4.py`, `art_v5.py`, `fur.py`, `ui_and_items.py`, `make_art.py`, `mock_scene.py`, `validate.py`; the rendered
previews in `docs/art-preview/`; the generated PNGs; and the photos in `reference/photos/` (`white_spot_on_head.jpeg`,
the balcony and the sitting/back photos). Measurements below come from a Pillow script (appendix) run on the PNGs and
on the in-memory clips; zoomed renders were made at 6-8x on a Gungeon-floor grey to check what the 4x sheets hide.

## Verdict in four lines

1. The *style* is right (big head, 2-px eyes, single dark outline, 12 colours per frame — all in vanilla range) but the
   *derivation code* damages it: the run frames lose the head's leading outline, hop frames clip the ear tips, the dodge
   ball bounces 0/2/4/2 px, and `squash`/`scale_down` shred faces. None of this is caught because nothing lints the art.
2. Likeness is limited by a **markings map that contradicts itself**: the 34x34 face card puts the eyes inside the tabby
   mask with a white blaze (matches the photos); the 24x20 sprite gives Pluto a white face with a tabby cap. The head
   spot is drawn as a notch touching the outline, the stripes are four isolated pixels, and the fur is caramel-orange
   although `gen_art.py` itself specifies "GREY-BROWN ... NOT orange".
3. Animation is mostly *transforms of one pose* (shift/squash/rotate/recolor): 32 of 260 frames are exact duplicates,
   the run is a bounce in place (feet travel <= 1 px), and nothing has follow-through.
4. The row-string format is fine as a *storage* format but wrong as an *editing* format: faces are hand-copied into
   11 poses, offsets are magic numbers, and there is no layering, no lint, no 1x preview on a real floor.

## Measurements

| Asset (generated PNG)                         | Size  | Colours | Keys                    |
|-----------------------------------------------|-------|---------|-------------------------|
| newspritesetup/idle/*.png (4 frames)          | 24x20 | 12      | o W w x B b d L G g P p |
| newspritesetup/run_right/*.png (6)            | 24x20 | 12      | same                    |
| newspritesetup/idle_forward/*.png             | 24x20 | 12      | same                    |
| newspritesetup/idle_backward/*.png            | 24x20 | 7       | o W w B b d L           |
| WeaponCollection/pluto_kibble_sack_*.png (8)  | 32x18 | 14      | o W w K N s R r V v Z z M m |
| WeaponCollection/pluto_gravy_pouch_*.png (6)  | 24x14 | 10      |                         |
| Items/wet_food_can_icon / toss (5)            | 20x20 | 13      |                         |
| Items/coco_blue_icon.png                      | 16x13 | 8       |                         |

Palette ramps (HSV from `pixel.py`): tabby `l L B d b 9` = hue 34/31/32/29/29/23, sat 31->56, value 80/70/56/43/35/23;
white `W w x` = hue 40/36/33, value 98/85/75; outline `o` #1E1614 (v 12) is the *only* outline colour on every asset.
So: the ramps are value ramps — the comment "hue-shifted toward red" on `d` (`pixel.py:53`) is a 3-degree shift, invisible;
the four tabby mid-tones sit 12 value points apart, and stripe `b` (v 35) vs. the automatic rim-shadow `d` (v 43) cannot be
told apart at 1x, which is why the stripes vanish (see 8).

Frames: 260 drawn, 228 unique. `item_get` 9/4, `chest_recover` 7/3, `idle` 4/3, `spinfall` 6/4, `death` 8/7.
Open-edge fill pixels (non-outline pixel touching transparency): idle 3/frame (belly rim between the legs), `run_right`
8-17/frame, `slide_right` 18, `pitfall` 10-18, `spit_out` up to 12.

## Findings and fixes, prioritised (S < 1 h, M = a few hours, L = a day or more)

### P0 — derivation bugs (cheap, visible in every run)

**1. `lean()` deletes the head's leading outline in every run frame — S.**
`character_anims.py:59-61` builds `('.' + row)[:len(row)]`, which drops the last character of rows 4-9 of `IDLE_SIDE`
(they end in `o`). Every `run_right*`, `tablekick_right*`, `doorway` frame has the face's front edge open; the `shade()`
pass then paints `d`/`w` rim colour where the outline should be (measure: 8-10 open px at x=20 in frames 0/3; visible in
the 8x render as a tan edge against the floor). Fix: lean after `pad()` on the 24-wide canvas (there are 3 free columns
at x=21..23), i.e. `overlay(EMPTY, rows[:12], BODY_DX + 1, 0)` + `overlay(..., rows[12:], BODY_DX, 12)`.

**2. Hop frames push the ear tips off the canvas — S code / M layout.** Ears start at row 0 and the airborne frames
`shift(body, 0, -2)` (`character_anims.py:70-75, 88-93`, `jetpack` 187-189, `PAWS_BOB` 158): rows 0-1 are silently
clipped by `pad()`, so the ears become flat-topped with the pink `P` on the edge (17 open px in run frames 1/4). Fix:
give the canvas headroom — 24x24 with feet on row 23 (update `validate.py:71`, `fur.py:17`, `mock_scene.py`), and make
`pad()`/`shift()` raise when they drop a non-`.` pixel (see 16).

**3. The dodge ball wobbles because `rotate()` spins the whole canvas — S.** `character_anims.py:112-113` pads the 16x16
ball at (4,4) then rotates the 24x20 canvas about (12,10); measured bboxes: y=4 / 2 / 0 / 2 and x shifted -2/+2. The
roll bobs 4 px and slides sideways. Fix: rotate `X.BALL` first, then pad — and while there, draw two ball keys with
squash (contact) and stretch (launch) instead of four pure rotations.

**4. `squash()` and `scale_down()` drop whole rows/columns — M.** `pixel.py:145-170` are nearest-neighbour resamplers.
`slide_right` (`squash(...,0.6)`, `character_anims.py:191`) loses rows 2,4,7,9,12,14,17,19: no nose, half an eye, broken
outline (18 open px). `pitfall` frames 2-4 are noise blobs (`scale_down` 0.6/0.45/0.3). `stretch`, `pet`, `item_get[1]`
and `timefall` are the same 0.9 squash. Fix: draw the slide (belly-slide with ears back) and 2 pitfall keys (crouch,
half-size ball) by hand; reserve `scale_down` for VFX; if scaling must stay, box-filter then palette-snap and re-outline
(`pixelize.py` already has that code).

**5. Tail has no follow-through and the dead tail is invisible — S.** `with_tail()` (`character_anims.py:23-36`) pins
the tail at (0,7) while the body moves by `dy`; `TAIL_A`/`TAIL_B` differ by one tip pixel (`poses_extra.py:176-201`)
and `sway=(i % 2)` (`:79`) flips it every frame at run speed = a 1-px flicker, not a wave. `TAIL_FLAT` is placed at
(0,15) *behind* `LYING` (`:33,129`), so only columns 0-2 show: a 3-px stub (death frames 6-8 in `character-sheet.png`).
Fix: give the tail its own per-frame offset table (lag the body by one frame: body -2 -> tail 0, body -1 -> tail -2 ...),
draw 3 tail keys (up, streaming back, down) rather than a tip flick, and place `TAIL_FLAT` beside the body, not under it.

**6. Ghost keeps a 100 %-opaque outline on a 75 %-alpha body — S.** `GHOST_MAP` (`character_anims.py:173`) does not
remap `o`; the ghost frames read as a heavy dark ring around a pale wash. Map `o` to a translucent dark key.

### P1 — likeness and 1x readability

**7. Two different cats: face card vs. sprite — M.** `art_v3.FACE_34` rows 14-18 put the eyes inside the tabby with a
white blaze between them and the spot as a diamond inside tabby (rows 5-9) — this matches the balcony photo (tabby mask,
blaze from between the eyes, white muzzle). `poses.IDLE_SIDE` rows 7-8 (`...oBBWWGgWWWWGgBo`) put both eyes on white
with tabby only at the outer corners; `IDLE_FRONT` and `PAWS_UP` the same. Side by side (8x) they are obviously
different markings. Fix: adopt the face card's map as canonical and redraw the head rows of the sprite: eye row =
`B eye W(blaze) eye B`, next row white cheeks, a `b` liner pixel at each outer eye corner (the photo's eyeliner).

**8. The head spot is drawn as a notch, and reads as a sparkle on the ball — S.** `IDLE_SIDE` rows 3-4 (`WW`, `WWWW`) sit
directly under the row-2 `ooo` bridge between the ears, so at 1x-4x it reads as a gap in the head silhouette (see the
side idle at 4x: a white V between the ears). On `X.BALL` row 1 (`.oWo.`) it is on the outline and reads as a star.
In the photo the spot is a small oval on the crown, fully surrounded by tabby, behind the ear line. Fix: move it one row
down, 3x2 (`WWW` / `.W.` or `Ww`), with `B` on all sides; keep the back view's version (it is the best one).

**9. Stripes are four isolated pixels and the same tone as the shading — S/M.** Side body: `b` at (6,4),(14,4),(5,12),
(4,14) only — measured 18 `b` in the side frame of which 12 are tail rings. Front: 2 pixels. Back: a chevron sweater.
The photos show a mackerel tabby: black vertical bars on the flank, the forehead M, and a dark spine line. Fix: draw
2-3-px vertical bars on the flank (rows 11-15) and shoulder, the M as three short strokes between the ears, and use a
darker stripe key (`9` #3A2A20 exists; or add ~#2E2420) so stripes are 15+ value points below the `d` rim shadow;
apply the same bars on front and back so the three views agree.

**10. Palette hue: caramel vs. the project's own spec — S.** `B` #8E7150 (h 32, s 44) with `b` chocolate makes a
ginger-brown cat; `gen_art.py:22-23` says "GREY-BROWN tabby (cool taupe brown ...) NOT orange". The photos are cool
taupe with near-black stripes and pale hazel-green eyes. Fix: `B` -> ~#7E6B58 (s ~30), `L` -> ~#A8967C (warmer/yellower
highlight), `d` -> ~#584840 (cooler, greyer shadow — a real hue shift, not 3 degrees), stripe ~#2E2420, `G` -> ~#9DB84E
(hazel). Keep 12 colours; the problem is spacing and hue, not count.

**11. Front pose is wall-eyed; eyes differ per pose — S.** `IDLE_FRONT` rows 7-8 `gG....Gg`: pupils on the *outer*
edge of each eye (divergent). `CROUCH`/`HIT`/`KNEEL`/`TIP` use `oo` slits, `LAND` uses `Gg`, `BALL`/`LYING` a single
`g`/`P`. Fix: one `EYES` part (open-right, open-front, closed, X) placed per frame (see 17); front pupils inward or
centred.

**12. Proportions: a wide oval, not a Gungeoneer capsule — M.** Body 18 px wide (21 with tail) x 20 tall, head 15x11;
the Pilot is ~14x22, Kotonoha's custom frames 23x24, the Shade 17x19 (research 01). At 1x on the floor Pluto is a squat
brown/white blob with two 2-px nubs; ears are 3 rows with a 1-px `P` (the photos show large pink ears, one of the
strongest cat cues). Fix (with the 24x24 canvas from 2): ears 4-5 rows with a 2-px pink interior, legs +1 row, and let
the head keep 50 % of the height. Tail rings: alternate `L`/`9` bands (2 rows each) so they survive at 1x.

### P2 — animation

**13. The run is a bounce in place — M.** `run_side` (`character_anims.py:64-81`): between contact and pass the leg
origins move at most 1 px (`hipB-1`, `hipB`, `hipB+1`), so the feet never travel; the whole "run" is the 0/-2/-1 body
bob plus the diagonal 5x4 strokes. Vanilla contact frames put one foot 3-4 px ahead and the other 3-4 px behind, and the
pass frame brings them under the hips. Fix: contact keys with feet at +3/-3 px, pass at 0, 1-px ear flatten on airborne
frames, tail lag from 5, and head bob decoupled from the body (head -1 on airborne, body -2) — all doable as offset
tables once parts exist. `run_front` frames 2 and 5 (and 1 and 4) differ only by the tail tip pixel.

**14. Held and duplicated frames stand in for missing keys — M.** `item_get` = 5x `PAWS` (raised paws are 1-px columns at
x=0/17 of `PAWS_UP`, invisible at 1x); `death` frames 7-8 identical, 1-2 and 3-4 are ±1 px shakes; `jetpack` = idle ±1;
`spinfall` reuses the three idles. Fix: draw the two missing keys per clip that carry the read (paws-up with 3-px-wide
paws over the head; death "settle" with the tail dropping and the ears folding), and mark true holds explicitly in a
frame spec so the lint (16) can tell a hold from an accident.

**15. `armed()` arm stubs ignore the body offset and cover the tail — S (+ one in-game check).**
`character_anims.py:298-308` overlays `ARM_SIDE` at a fixed (19,11) on every frame; in airborne run frames the body is
2 px higher so the stub hangs from the hip (`ui-sheet.png` row 5, `run_right_hand[1]`). The front two-hands left arm at
(1,12) is drawn *on top of* the tail curl. The paw itself is the game's 4x4 `hand_001.png` at the Pilot's `primaryHand`
offset (base: Pilot, `characterdata.txt:4`), which nothing in the repo reads; `mock_scene.py:57` assumes (21,13). Fix:
shift the arm with `dy`; drop the tail (or move it right) in front two-hands frames; log `primaryHand.localPosition`
once in-game and end the stub 1 px short of it so the drawn paw overlaps the join.

### P3 — items

**16. The kibble bag is a white box — M.** `art_v3.gun_bag()` is a 28x14 `rrect` with 14 colours of interior detail
(crown 5x3, cat 5x7, kibble pic, zip teeth) and a symmetric silhouette; at 1x beside the cat (`ingame-mock.png`) it reads
as a document/brick, and it is longer than the cat is wide. Vanilla guns read by silhouette first. Fix: asymmetric
outline — pinched/gathered grip end at the hand (x 1-6), a torn flap at the spout with kibble spilling, a 1-px fold
line — and keep only the red band + purple circle as brand cues at gun scale (move the crown/cat to the 24x32 Ammonomicon
sprite, where they fit). The can (13 colours, gold/pink/red) reads fine in the HUD slot; leave it.

### P4 — pipeline structure

**17. No art lint; `validate.py` only checks sizes and folders — M.** Every bug above shipped through `make_art.py`
without a message. Add `tools/lint_art.py`, run from `make_art` and `validate`: (a) `pad`/`shift`/`rotate` report any
dropped non-transparent pixel; (b) open-outline count per frame with an allowlist (the belly rim between the legs is
intentional); (c) colours per frame <= 13 and keys within the asset's allowed set; (d) consecutive identical frames
unless declared as holds; (e) orphan pixels (a fill pixel with no same-key 4-neighbour — the current stripes would all
fail); (f) mirror check for front/back poses excluding eyes/tail; (g) arm-stub end == hand attach constant. The script in
the appendix already does (b)-(d).

**18. Row strings as the editing format — L (do after 17).** `poses.py`/`poses_extra.py` hand-copy the face into
`IDLE_SIDE`, `IDLE_FRONT`, `PAWS_UP`, `LYING`(x2), `CROUCH`, `LAND`, `HIT`, `KNEEL`, `TIP`, `LOAF`, `BALL` — which is how
7, 8 and 11 diverged. Offsets are literals (`5 + BODY_DX, 17`, `(0, 7)`, `(19, 11)`, `(14, 8)`), and 24-wide rows are
counted by eye. Better structure, using the `overlay`/`pad` helpers that already exist: a parts library (`HEAD_SIDE`,
`HEAD_FRONT`, `EARS[up|flat|back]`, `EYES[...]`, `NOSE`, `SPOT`, `BODY_*`, `LEG[...]`, `TAIL[...]`, `ARM`) each with a
named anchor; a frame = a list of `(part, variant, x, y, flip)`; clips = tables of per-frame deltas (body dy, ear
variant, tail variant + lag, leg pair, arm dy). Shade parts once by hand (a sphere's shadow wraps the lower-right
quarter 2-3 px wide) instead of the global 1-px rim in `pixel.shade()` (`:221-257`), which bevels every edge equally.
Also delete the dead art the imports shadow: `ui_and_items.py:8-63, 115-302` (overridden at `:67` and `:305`) and
`poses.BALL` (`poses.py:98-115`, unused — `X.BALL` is the live one).

**19. Preview sheets hide the white fur and never show 1x — S.** `pixel.sheet()` (`:206`) pastes without a mask, so cell
interiors are transparent (white in every viewer) and the white belly/legs disappear; sheets are 4x/5x/6x only, no
reference size, no floor. Fix: `alpha_composite` onto the floor grey from `mock_scene.py`, rows at 1x/2x/3x, a 14x22
(Pilot) and 23x24 (Kotonoha) reference box at the left of every row, one filmstrip per clip, and a GIF per clip at the
Alexandria fps so bob/flicker problems show up in motion.

**20. 2x masters — only for the cards and icons — M.** For 20-px body frames, hand-placed 1x pixels beat downscaling
(the 2-px eyes and 1-px nose would blur). Where it pays: the 34x34 face card, 38x38 foyer card and the boss card / win
pic / 256 icon, which today are 6x nearest upscales of the 34-px face (`ui_and_items.py:329, 375`). Draw one 136x136
portrait master, show it 1:1 on the boss card, and box-downscale + palette-snap to 34 for the HUD (`pixelize.py` has the
filter and the outline redraw).

## Suggested order

1. Day 1 (all S): 1, 3, 5, 6, 8, 10, 11, 15, 19 — regenerate, look at the new 1x/floor sheet.
2. Day 2: 2 (canvas 24x24) + 12 (ears/legs) + 7 + 9 — the likeness pass; check against `white_spot_on_head.jpeg`.
3. Day 3: 17 (lint) so the rest cannot regress; then 4, 13, 14, 16 as time allows; 18 and 20 when the clip set is stable.

## Appendix — measurement snippet (Pillow)

```python
import glob, os, sys; from PIL import Image
sys.path.insert(0, 'tools'); import character_anims as A
for f in sorted(glob.glob('PlutoTheCat/Characters/Pluto/newspritesetup/idle/*.png')
                + glob.glob('PlutoTheCat/Resources/SpriteRoot/WeaponCollection/*.png')
                + glob.glob('PlutoTheCat/Resources/Items/*.png')):
    im = Image.open(f).convert('RGBA'); cols = {c for c in im.getdata() if c[3]}
    print(os.path.basename(f), im.size, len(cols), 'colours')
for clip, frames in A.CLIPS.items():                      # duplicates and open outlines
    if not frames: continue
    uniq = len({tuple(fr) for fr in frames})
    def open_px(rows): return sum(1 for y, r in enumerate(rows) for x, ch in enumerate(r) if ch not in '.o'
        and any(not (0 <= x+dx < len(r) and 0 <= y+dy < len(rows)) or rows[y+dy][x+dx] == '.' for dx, dy in ((1,0),(-1,0),(0,1),(0,-1))))
    print(clip, len(frames), 'frames', uniq, 'unique', [open_px(fr) for fr in frames], 'open px')
```
