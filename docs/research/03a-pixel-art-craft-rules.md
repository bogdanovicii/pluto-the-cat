# 03a — Pixel-art craft rules for the Pluto sprite pipeline

> **Historical research (2026-09-14):** written for the old 24x20 canvas and `shade()` rim pass, both since replaced (24x26 canvas, no rim pass, see 2.9.0).

Scope: hand-authored row-string sprites rendered by `tools/pixel.py` (character 24x20 canvas, 18x20 used;
icons 16–34 px; guns 32x18; one dark outline key `o`; 47 opaque palette keys; `shade()` rim pass).
Every rule carries a source tag; the tag → URL table is at the end. Numbers are the sources' numbers,
adapted to this pipeline's sizes. Note: *Pixel Logic* is by Michael Azzi (Michafrar), not C. Neofotistou.

Playback facts the animation rules are built on (Alexandria `playerAnimInfo`, see `01-custom-character-research.md`):
idle Loop **6 fps** (167 ms/frame) · run Loop **9 fps** (111 ms) · dodge Once **12 fps** (83 ms, first half invulnerable) ·
death/death_shot Once 12 fps · item_get Once 9 fps · pitfall 15 fps · breach idles 8 fps. Shade (reference mod) ships
idle 4 / run 6 / dodge 9 / death 8 frames. Frame count per clip is free (folder contents), fps is not.

## 0. Audit: what the current pipeline does that the sources say not to do

| # | Current behaviour | Rule broken | Fix |
|---|---|---|---|
| A1 | `shade()` darkens every `B/W` pixel whose bottom/right neighbour is outline and lightens top/left ones → a 1-px band hugging the whole outline | "Hugging" banding: outline and the band inside it line up and expose the grid [PJ][LB][PL p.~60][S11-Align] and pillow shading: shade follows the *shape*, not the *form* + light [PJ][PM4] | Delete the pass. Hand-place 1 shadow *shape* per body mass from a fixed top-left light (belly/under-chin/under-ear/far leg), sharp terminator, band steps offset ≥1 px from the outline steps [S11-Shade][PM4] |
| A2 | Tabby ramp `l L B d b 9 o` = 7 tones, hues 34/31/32/29/29/23/12° | Straight ramp (only value changes) [PJ][SL1]; too many tones for an 18-px body (2–3 shades per colour [DY], ≤16 colours per sprite [PL p.~70]) | 3 fur tones + stripe: light `L`, base `B`, shadow `d`; `b` only for stripes/rings; retire `l`, `9` on the body. Hue-shift per §2 |
| A3 | `d` "hue-shifted toward red" (H 29° vs base 32°) | Shadows should go **cooler** (toward purple/blue), highlights **warmer** (toward yellow) [PM1][PJ][SL1][AR] | `d` → H≈15–20°, S≈50%, V≈42%; `L` → H≈38–42°, S≈32%, V≈70% |
| A4 | Internal lines (ear/head, head/body, tail rings) drawn with the exterior `o` | Interior lines should be a darker shade of the adjacent colour; black everywhere flattens and eats space [LO2][PM7][AR][S11-Outl] | Interior seams use `b` (tabby) / `x` (white); keep `o` only on the silhouette |
| A5 | `rotate(ball, ±90/180/270)` for the roll; `squash()`/`scale_down()` nearest-resample frames | Auto rotate/scale must be redrawn; sliding parts unedited "looks tweened" [S11-Resize][PL p.~228] | Use transforms as a *base*, then hand-fix each frame (visible ear/tail/blaze rotation cues, cleaned jaggies) |
| A6 | Idle: pure 1-px vertical bob, legs planted, tail sway on the same frames | Vertical-only movement is boring; add horizontal/secondary motion, delay head/tail 1 frame; mass must not change [S11-Idle][S11-Squash] | §4 N2 idle plan |

## 1. Readability at 16–32 px

- R1 **Silhouette first.** Sketch/verify each pose as a flat mask; ears, ringed tail, head spot and blaze must be identifiable at 1× and in a blurred/thumbnail view [S11-Sil][PL p.102, p.111–112][S11-Proc "keep fixing the silhouette"].
- R2 **Chibi proportions.** < 4 heads tall; head ≈ 50 % of height (Pluto: rows 0–10 of 20 = 55 %, good); big forehead/eyes/ears, small nose, stubby limbs, "fewer marks" [S11-Cute][DY "chibi for 32x32"][PL p.100 "big heads give room for expression"].
- R3 **Colour, not lines, defines the character at this size** [DY]. Reduce to 2–3 main colours per character (tabby, white, green-eye accent; pink only nose/inner ear) [PL p.103].
- R4 **Spacing.** Every feature needs ≥1 px of a different value around it; a mouth needs space above and below; pupils are 2×2 clusters that never touch the outline [PL p.105–106]. Eyes get one 1-px highlight, nothing else.
- R5 **Clusters.** Aim for the fewest clusters; no 1-px clusters ("orphans") except eye shine / specular / a deliberately strong detail [S11-Fund1][PM1][PM2][PJ "noise"]. When animating, keep clusters intact frame to frame [S11-Fund1].
- R6 **Lines.** 1-px wide; steps connect diagonally, never through an extra corner pixel; no unintentional 2×2 squares — place colours "brick-like" [S11-Fund2][PM7][S11-Outl]. Straight lines: equal steps. Curves: step length shrinks toward the "corner" then grows (e.g. 4,2,1,1,2,4; Lospec: 7→1) [S11-Fund2][PM2][PL p.26][LO1]. Irregular slopes: repeat a pattern (2,2,3,2,2,3) [S11-Fund2].
- R7 **Jaggies / doubles.** A jaggy is a step that breaks the progression (3,1,3); a double is a 2-px-thick blip on a 1-px line. Fix by moving one pixel, not by adding AA [PJ][PM2][PL].
- R8 **Banding.** No 1-px shade band running parallel to and touching the outline with the same steps (hugging); no staircase bands; no 45° bands. Break alignment: offset the band's steps or end it before the outline's step [PJ][LB][PL][S11-Align].
- R9 **Pillow shading.** One light (top-left, ~45°). Never darken every edge of a shape. Flat "faces" = one solid colour; rounded masses = 1 ramp in one direction with a sharp terminator; compress bands into small areas [PJ][PM4][S11-Shade][LB].
- R10 **Outline policy for Gungeon floors (light stone to near-black).** Exterior: closed 1-px `o` all around — an outline must be darker than both object and background [LO2][PL p.197]. Interior: coloured (one shade darker than the adjacent lighter part; colour of the part nearest the viewer) [LO2][PM7]. Drop interior lines where value contrast already separates (white muzzle vs tabby cap) [PM7][AR]. Sel-out / broken outlines only when backgrounds are always dark → not here [PJ][PL p.197].
- R11 Optional softening: top/lit-side silhouette pixels may use the deep shade (`9`) instead of `o` where they touch white fur; bottom/shadow side stays `o` [AR][DY].
- R12 **Corners.** Pixels are square — use that for ear tips and tail tip (pointy); remove every corner that is not meant (3-of-4 pixels of a 2×2 filled) [S11-Outl][PM7].
- R13 **Outlines cost space.** At 16×16 (icons, minimap) prefer no interior lines at all and let value do the work [PM7][S11-Outl]; keep the exterior line.

## 2. Palette construction

- P1 **3 tones per material + shared outline** (light / base / shadow) [DY 2–3 shades][PJ cohesion]. Sprite budget: ≤16 colours, most sprites fine at 10 [PL p.~70]. Targets: body ≤10 keys (idle currently uses 10: `B G P W b g o p w 9`), 16-px icons ≤8, 34-px face card ≤14.
- P2 **Hue shift every ramp.** Shadow hue toward blue/purple, highlight toward yellow; ≤20° per step, 8–15° typical [SL1][PJ][PM1][AR]. Warm-hue shadows are "not a stone-written rule" but the default when unsure [PM1].
- P3 **Saturation** peaks at the mid tone; darker steps may be slightly more saturated but very dark + very saturated looks "rich and weighty"; highlights desaturate; never 0 % or 100 % [SL1].
- P4 **Value steps** ≥15–20 V-points between adjacent tones so they read at 1×; smaller steps near the top of the ramp [SL1][PJ "contrast"]. Current tabby `L→B→d` = 70/56/43 V (ok); white `W→w→x` = 98/85/75 (ok).
- P5 **No pure black or white inside ramps** [AR]; the warm near-black `o` (#1E1614) is the one colour every ramp shares (darkest colour belongs to all ramps) [PJ].
- P6 **One game palette.** Reuse ramps across character, items and guns instead of adding keys (kibble tan ↔ tabby light, can silver ↔ white shade, gravy ↔ tabby shadow) [PL][SL1 "160-colour palette keeps everything consistent"]. Adding a key needs a justification comment.
- P7 **Eye-burn guard.** Accent colours (`G` eye green, `H` heart) S ≤ 65 %; a colour that "punches through" is either too saturated or hue-clashes with its ramp neighbours [PJ].
- P8 Grey-scale test: recolour a frame to V only; if materials merge, fix values before hues [PJ "relative value matters more than hue"].

## 3. Anti-aliasing and dithering at sprite scale

- A1 **Default: no AA on the 24×20 character.** AA needs colours and space, blurs small sprites, and every AA colour counts toward the budget [PL p.109][PM5][PJ]. Face card (34×34) and gun (32×18): allowed on long outline curves only.
- A2 **Never AA the exterior outline against transparency** — game backgrounds vary; internal AA only [PJ (jalonso, "selective AA")][PL p.197].
- A3 When used: 1 intermediate colour (max 2), at corners only, strip ≈ half the step length ("too little is better than too much"), never on straight or 45° (1:1) lines, and the AA runs in the slope's direction [PL][PM5][LB].
- A4 **No dithering** on anything that animates or is < 32 px ("things that don't animate. Seriously.") [PL p.116][PJ]. A 2-px checker is acceptable only as *texture* on static icons (kibble bag weave) with low contrast between the two colours [PJ][AR].
- A5 Don't fake AA with automatic rim tones (A1 above): the result is banding, not smoothing [PJ][LB].

## 4. Animation for small sprites

- N1 **Keys first, then in-betweens that favour the keys.** More in-betweens never fix weak keys; the contact pose decides 80 % of a cycle [PL p.215][SL8][S11-Plan]. Process: still frame → rough silhouettes → keyframes → in-betweens (copy/paste, adjust timing) [S11-Plan].
- N2 **Idle (Loop 6 fps).** Two keys 1 px apart (down: body drops 1 px, belly +1 px wider, knees bend; up: back), mass constant [S11-Idle][S11-Squash]. Middle frame = eased in-between with the head delayed 1 frame [S11-Idle]. Add a horizontal element (tail sway, ear flick, head tilt) — "vertical movement alone is boring" [S11-Idle]. Move face contents one frame *after* the silhouette moves; eyes never sub-pixel [S11-Idle][PL p.204]. Plan: ship 12 frames = body bob period 4 × tail period 3, blink 1 frame per loop; sub-loops start on different frames [S11-Loop].
- N3 **Run (Loop 9 fps, 6 frames = 667 ms cycle).** Per leg: contact (body lowest, forward leg straight, widest) → recover/pass (thinnest, legs cross) → up (highest, both feet off the ground, legs tucked); repeat mirrored for the other leg, except asymmetric features (blaze curl, tail) [S11-Run][S11-Walk][S11-TDRun][SL8 "6 frames = nice gallop"]. Body bob 1–2 px; head lags torso 1 frame; tail counter-sways; the grounded foot only ever moves backwards [S11-Walk]. Feet baseline row is fixed; bob moves the body, never the baseline — design the body 1 px short of the canvas for this [AR "23 of 24 px"]. Top-down/front: think head, body, feet as 3 stacked shapes; 3 "jump" + 2 "recover" frames also works [S11-TDRun].
- N4 **Squash & stretch.** Conserve mass: −1 row ⇒ +1 column; stretch along the motion on the fastest frames, squash on contact; stiff parts deform less [S11-Squash][PM3][PL p.217].
- N5 **Dodge roll (Once 12 fps, 9 frames = 750 ms, frames 1–4 invulnerable).** No anticipation frame — player-controlled actions start on the button press [S11-Jump][PL p.218]. F1 crouch/paws down; F2–F6 ball with per-frame rotation cues (ear pair, tail tip, blaze move around the ball; no two identical rotations); F7 stretch out + landing squash (+1 wide, −1 tall); F8 overshoot 1 px past idle; F9 idle [S11-Roll][S11-Squash][PL "overshoot by just 1 pixel"]. Dust/motion blur optional [S11-Roll].
- N6 **Death (Once 12 fps, 8 frames) / hit.** F1 impact = strongest pose, thrown back (largest displacement); "give up": knees bend, head and limbs lag; hit ground: limbs lag, overshoot 1 px *below* the ground line, bounce, rest [S11-Death]. Hit reaction: 1 impact frame, overshoot the first frame, ease slowly back to idle [S11-Death][S11-Imp]. A 1-frame flash/contrast frame is allowed on impact [S11-Death].
- N7 **Overlap / follow-through.** Tail tip and ears lag the body by 1–2 frames and keep moving 1 frame after the body stops ("when 1 pixel moves, the others take a frame or two to catch up") [PL p.225–226][S11-Idle "hair lagging behind the head"]. Lead with the main mass; draw followers last [PL].
- N8 **Sub-pixel motion.** For < 1-px movement recolour along the edge (one row `W→w`, `B→L`) instead of moving pixels; 1–2 in-between shades max; shift direction follows the *edge's* angle, not the motion; when a curve pops a new row make it ≥2–3 px wide; never on the face [PL ch. 8][S11-Sub][2D]. Reuse palette colours; too many makes it blurry [S11-Sub].
- N9 **Easing / overshoot.** Distort or skip the middle frame for snap; overshoot 1 px then settle; linear spacing "looks dull" [S11-Ease][PL p.219–221].
- N10 **Loop hygiene.** A single stray pixel in a loop is obvious [SL8]; no accidental duplicate frames; sub-loops of different lengths hide the seam [S11-Loop].
- N11 Timing reference: 12 fps = 83 ms ("twos"), 9 fps = 111 ms, 6 fps = 167 ms ("fours"); hold frames are set by duration, not by adding frames [PL p.216–217].
- N12 Quadruped reference (for any 4-legged pose): treat it as two bipeds with a small time offset; each leg: contact → drag → rise → forward; head follows the front pair with a delay [S11-Quad].

## 5. Workflow rules that suit a code pipeline

- W1 **Author at 1× on the 18×20 grid.** Scaling/rotating pixel art "should always be avoided; you need to redraw it" [S11-Resize]; a resized sprite is only a mosaic *base* to redraw over [PL p.177]; plain box/bilinear downscaling destroys the implied detail and produces off-palette colours [HV]. If a 2× draft exists: majority colour per 2×2 block (not averaging), snap to palette, then hand-fix silhouette, outline and missing detail [HV][S11-Resize].
- W2 **Part composition (with_tail / with_legs / overlay) is for blocking, not shipping.** Modular animation is "not as useful" for small sprites; avoid rotation/scaling of parts; hide joints behind solid colour; some parts stay frame-by-frame [S11-Mod]. "You can NOT just slide body parts around and leave it at that" — edit every composed frame at the seams [PL p.228]. `rotate_free`/`scale_down` output must be cleaned like any rotated sprite [PL p.178].
- W3 **Draw order per frame:** silhouette → flat colours → shading → details/small highlights last; fix orphans and noise at the end; check proportion, light direction, hard-to-read areas [S11-Proc][PM7].
- W4 **Review at 1×, 2× and blurred** on a mid grey, a light-stone and a dark floor swatch (`mock_scene.py`); "if it looks bad when blurred, fix the pixels" [PL p.111–112].
- W5 Keep the old and new frame side by side; recycle frames (copy, slide, mirror) then "frankenstein" them so they look distinct [PL p.228].

## 6. Lint spec — checks that encode the rules (run per sprite / per clip)

| Check | Rule | Threshold / detail | Source |
|---|---|---|---|
| palette_conformance | every pixel is a palette key; count ≤ budget | body ≤10, 16-px icon ≤8, 34-px ≤14 (P1) | [PL][PAL] |
| orphan_pixels | 4-connected component of size 1 | warn unless key ∈ {eye shine `K`, pupil `g`} or tagged `# orphan-ok` | [S11-Fund1][PM1][PJ] |
| outline_closed | every opaque pixel 4-adjacent to transparency is `o` (or `9` on top/left only) | fail; needed by `fur.py` edge walk too | [LO2][R10] |
| outline_thin | no 2×2 block of `o`; no 3-of-4 `o` square unless tagged corner (ear/tail tip) | fail / warn | [S11-Fund2][PM7][S11-Outl] |
| outline_steps | run-lengths of the silhouette per octant; a,b,c with b=1 < min(a,c) = jaggy; two orthogonally adjacent edge `o` on a diagonal run = double | warn | [PM2][PL p.26][PJ] |
| hugging_band | 1-px run (≥4) of one shade key whose every pixel touches `o` on the same side and copies its steps | warn (the old `shade()` fails this by design) | [PJ][LB][S11-Align] |
| contrast | adjacent different keys: ΔV ≥ 15; `o` at least 25 V below every neighbour | warn | [SL1][LO2][PJ] |
| ramp_hueshift | per ramp: hue(shadow)−hue(base) ∈ [−20°, −5°]; hue(light)−hue(base) ∈ [+5°, +20°]; S(light) ≤ S(base) | warn | [SL1][PJ][PM1] |
| symmetry | front/back poses: mirror-diff halves; asymmetric pixels must be in an allow-list (tail, blaze curl) | report | [S11-TDRun] |
| anim_baseline | lowest opaque row constant on grounded frames; airborne frames declared | fail | [S11-Walk][AR] |
| anim_bob | centroid Δy ≤ 2 px between consecutive frames (idle ≤1) | warn | [S11-Idle][S11-Run] |
| anim_cluster_delta | per key, cluster count changes ≤2 between frames; changed-pixel count of exactly 1 = stray pixel | warn | [S11-Fund1][SL8] |
| anim_holds | identical consecutive frames flagged unless marked hold | warn | [PL p.216] |
| mass_conservation | on frames tagged squash/stretch, bbox area within ±10 % of idle | warn | [S11-Squash][PM3] |
| frame_size | 24×20 body, gun frames share one size (existing `validate.py`) | fail | [PAL] |

## Sources (tag → URL)

- [S11-*] Pedro Medeiros (Saint11) tutorial cards, index https://saint11.art/blog/pixel-art-tutorials/ ; cards at `https://saint11.art/img/pixel-tutorials/<Name>.gif`: Outlines (`Outlines`), Shading (`Shading`), Fundamentals 1/2 (`Fundamentals`, `Fundamentals2`), Character Design 1 / silhouette (`Silhouette`), Cuteness (`Cuteness`), Character Idle (`characterIdle`), Run Cycle 1 (`RunCycleSimple`), Walk Cycle (`Walk`), Quadruped Walk (`4LegsWalk`), Top-Down Run (`TopDownRun`), Squash & Stretch (`Squash`), <1 Pixel Movement (`Subpixel`), Slide-Roll-Dash (`Slide-Roll`), Death/Take Hit (`Death.GIF`), Impact (`Impact-export`), Animation Easing (`Easings`), Jump (`Jump`), Seamless Looping (`loop`), Modular Animation (`Modular`), Resizing (`Resizing`), Animation Planning (`Planning`), Pixel Art Process (`Pipeline`), Alignment (`Alignment.png`). CC-BY 4.0 (https://github.com/saint11/Saint11Tutorials).
- [PM1] Medeiros, *How to start making pixel art #1* https://medium.com/pixel-grimoire/how-to-start-making-pixel-art-2d1e31a5ceab
- [PM2] *#2 Cluster sketching* https://medium.com/pixel-grimoire/how-to-start-making-pixel-art-2-bcd705cb04d7
- [PM3] *#3 A basic Aseprite animation* https://medium.com/pixel-grimoire/how-to-start-making-pixel-art-3-c9eb70270fa1
- [PM4] *#4 Basic shading* https://medium.com/pixel-grimoire/how-to-start-making-pixel-art-4-f57f51dcfa02
- [PM5] *#5 Anti-alias and banding* https://medium.com/pixel-grimoire/how-to-start-making-pixel-art-4-ff4bfcd2d085
- [PM7] *#7 Working with lines* https://medium.com/pixel-grimoire/how-to-start-making-pixel-art-7-e504bfa4ddf2
- [PJ] cure, *The Pixel Art Tutorial* (Pixel Joint) https://pixeljoint.com/forum/forum_posts.asp?TID=11299
- [PL] Michael Azzi, *Pixel Logic — A Guide to Pixel Art* (page numbers from the book) https://pixellogicbook.com/ ; full text https://archive.org/stream/pixel-logic-a-guide-to-pixel-art-michael-azzi/Pixel%20logic%20a%20guide%20to%20pixel%20art%20-%20Michael%20Azzi_djvu.txt
- [DY] Derek Yu, *Pixel Art Tutorial: Basics* https://www.derekyu.com/makegames/pixelart.html
- [LO1] Lospec, *Pixel Art Outlines* https://lospec.com/articles/pixel-art-outlines/
- [LO2] Lospec, *Pixel Art Outlines Part 2: Using Color* https://lospec.com/articles/pixel-art-outlines-part-2-using-color/
- [AR] Arne Niklas Jansson, *Pixel Art Tutorial* https://androidarts.com/pixtut/pixelart.htm
- [SL1] Raymond Schlitter (Slynyrd), *Pixelblog 1 — Color Palettes* https://www.slynyrd.com/blog/2018/1/10/pixelblog-1-color-palettes
- [SL8] Slynyrd, *Pixelblog 8 — Intro to Animation* https://www.slynyrd.com/blog/2018/8/19/pixelblog-8-intro-to-animation
- [LB] The Logbook Project, *Banding, Anti-Aliasing, Pillow Shading* https://the-logbook-project.blogspot.com/2013/04/pixel-art-lessons-jiinchus-darkness.html
- [2D] 2D Will Never Die, *Give your sprites depth with sub-pixel animation* https://2dwillneverdie.com/tutorial/give-your-sprites-depth-with-sub-pixel-animation/
- [BR] Blake Reynolds, *A Pixel Artist Renounces Pixel Art* (clusters imply form; "pixel tax") https://www.killscreen.com/pixel-artist-renounces-pixel-art/
- [HV] Hiive Labs, *Adaptive Downscaling of Pixel Art* https://hiivelabs.com/blog/gamedev/graphics/2025/01/19/adaptive-downscaling-pixel-art/
- [PAL] pixel art lint (CI checks: palette drift, frame dimensions) https://pixelartlint.com/
- Local: `docs/research/01-custom-character-research.md` (Alexandria clip fps / wrap modes, Shade frame counts).
