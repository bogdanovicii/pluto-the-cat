# 03b — Vanilla Gungeoneer sprite & animation conventions (for Pluto)

Research date: 2026-09-14. Legend: **[C]** confirmed from game code / asset data / official-wiki frame data; **[I]** inferred.
Vanilla pixel numbers below were measured by decoding the ETG wiki's animation GIFs in a browser (no files downloaded);
Convict is the fully documented vanilla reference (the wiki hosts every Convict clip), Pilot/Hunter only have idle GIFs.

## 0. The ten numbers that matter

| # | Rule | Value | Status |
|---|------|-------|--------|
| 1 | Pixels per unit | **16** (`w = tex.width / 16f` in Alexandria; `n = px/16` in the modding guide) | C |
| 2 | Visible body size (idle) | Pilot **14×21**, Convict **16×20**, Hunter **14×22** px | C |
| 3 | Vanilla per-clip canvas (Convict) | idle 16×20 · run 15–17×23 · dodge 17×24 · death 21×20 · item_get / death_shot 22×28 · pitfall 16×18 · pitfall_return 16×26 | C |
| 4 | Proportions | head ≈ **52–59 %** of height; torso ≈ 7 px; legs = **1-px-wide sticks, 2–3 px long**, 4 px apart | C |
| 5 | Outline | **none in the art** — a 1-px black outline is added at runtime (`SpriteOutlineManager.AddOutlineToSprite`) | C |
| 6 | Palette | **8–15 colours for the whole character**; ~2 tones per material; no dithering, no anti-aliasing | C |
| 7 | Idle | **4 frames, 6 fps** (160–180 ms), feet fixed, top of head dips **1–2 px** (breathing squash) | C |
| 8 | Run | **6 frames, 9–10 fps** (100 ms), whole-body **hop of 4 px** — feet leave the ground on 2 of 6 frames | C |
| 9 | Dodge | **9 frames**, fps forced to `frames / rollTime` ≈ 13–14 fps (≈ 0.65 s); first 5 frames invulnerable | C |
| 10 | Hands | separate **4×4 px** `hand_001.png`, snapped to the *gun's* `PrimaryHand`/`SecondaryHand` attach points; body clips come in `""` / `_hand` / `_twohands` variants | C |

## 1. Vanilla Gungeoneer sprite specs

### 1.1 Sizes and canvases
- Wiki in-game idle GIFs (trimmed to visible pixels): **Pilot 14×21**, **Convict 16×20**, **Hunter 14×22** (the Marine GIF is upscaled, unusable). [C]
- Vanilla Convict clip canvases (wiki GIF frame size = untrimmed dump frame): idle 16×20, run_right 17×23, run_down / run_up 15×23, run_right_bw 16×23,
  dodge 17×24, dodge_bw 13×24, dodge_left 20×23, death 21×20, death_shot & death_coop 22×28, pitfall 16×18, pitfall_down 15×13,
  pitfall_return 16×26, item_get 22×28, doorway 15×20, spinfall 18×21, chest_recover 21×25, spit_out 18×41, timefall 21×21,
  tablekick_right 17×21, slide_right 15×18, pet 16×19, jetpack_right 16×19, ghost_idle 16×21, select_idle 16×20, select_choose 18×26. [C]
- Community sheets: Kotonoha (Pilot base, vanilla file names) uses a uniform **23×24** canvas for every body frame; OMITB's Shade (Robot base) uses 17×19 (idle) / 16×18 (dodge, pitfall). Both ship a **4×4 px** hand. [C] The 23×24 Pilot canvas most likely mirrors the Pilot dump. [I]
- Modding-guide rule of thumb: keep sprites under ~30×30 px; never change a base frame's canvas size (the game stretches it back). [C]
- Pluto's 24×20 canvas: fine for idle/run width, but vanilla dodge / item_get / pitfall_return / death_shot need **24–28 px of height**. Alexandria anchors every frame at the PNG's bottom-left, so a taller canvas for those clips is legal as long as the feet row and centre column stay identical across clips. [I]

### 1.2 Pivot / anchor
- Alexandria `ConstructDefinition` builds each frame's quad from (0,0) to (w/16, h/16): **origin = bottom-left corner of the PNG**, no per-frame offset. Kyle's original CC mod does the same. [C]
- Consequence: keep the feet on a fixed bottom row and the body centred on a fixed column in every frame; the hop in run/dodge is drawn by moving pixels *up* inside the canvas (Convict run: bottom row 22 on contact frames, 18–19 when airborne). [C]
- `gunAttachPoint` (where the gun hangs) is a transform on the base-character prefab, quantised to 1/16 units; GungeonCraft overrides it to (0.5, 0.5) = 8 px, 8 px for its custom character. [C]

### 1.3 Proportions and face (measured on vanilla idle frames)
- Pilot (21 rows): helmet+head rows 0–10 = 11 px (52 %), torso rows 11–17 = 7 px, hips row 18 = 6 px wide, legs rows 19–20 = two 1-px sticks 4 px apart. [C]
- Convict (20 rows): hair+head 11 px (55 %), torso 7 px, legs 2 rows of 1-px sticks. Hunter (22 rows): hood+head ≈ 13 px (59 %), same stick legs. [C]
- Faces are a flat single skin tone. **Eyes = one dark pixel each, 5–6 px apart** (Pilot cols 5 & 11; Convict blue `0,62,205` at cols 5 & 11; Hunter cols 6 & 12). **Mouth = 2–3 px dark line one row below the eyes.** No eye whites, no highlights, no nose. [C]
- Sprites are drawn facing **right** only; the game flips them horizontally (`HandleFlipping`) when aiming left. [C]

### 1.4 Hands and guns
- Hands are separate `tk2dSprite`s (`PlayerHandController`): a **4×4 px** sprite (`Convict_hand_001.png` is 4×4; Alexandria sets the hand quad to ±0.125 units = 4×4 px centred). Each hand's `attachPoint` is the **gun's** `PrimaryHand` / `SecondaryHand` child transform; `LateUpdate` snaps the hand to `QuantizeVector(attachPoint.position, 16)` and lifts it 0.05 units above the gun. Hands get their own black outline. [C]
- The gun is positioned so its `PrimaryHand` attach point sits on the player's `gunAttachPoint` (`Gun.cs`: `m_defaultLocalPosition = -attachPoint.position`). Hand positions on a gun are set in gun sprite data (`n = px/16`, counted from the sprite's bottom-left). [C]
- Body-clip hand variants (`PlayerController.GetBaseAnimationName`): [C]
  - no suffix (`idle`, `run_right`, …) → body drawn **without hands**; used with **two-handed** guns (both hands are the separate sprites);
  - `_hand` → body draws **one** hand (the free hand); used with **one-handed** guns (`RenderBodyHand` true);
  - `_twohands` → body draws **both** hands; used when holding **no gun** (or a `NoHanded` gun).
  - Visually confirmed on the Convict wiki frames: `Idle` has no arms, `Idle_Hand` one arm, `Idle_Twohands` both arms.
  - Vanilla never requests `idle_bw_hand` or `run_right_bw_hand` (back-diagonal one-handed view falls back to `idle_bw` / `run_right_bw`), which is why Alexandria's table omits them.

## 2. Animation clip inventory (Alexandria CharacterAPI `newspritesetup/`)

### 2.1 How Alexandria loads it (CharApi/CharacterBuilding/SpriteHandler.cs, Loader.cs) [C]
- Folder layout: `newspritesetup/<clip>/<any>_001.png…`, `newspritesetup/hand_001.png` (alt skin: `newaltspritesetup/`, `hand_alt_001.png`),
  `newspritesetup/breach_idles/<name>/`, `newspritesetup/custom/<name>/`, plus `foyercard/`, `loadoutsprites/`, `punchout/sprites/`, `facecard.png` (34×34), `bosscard`, `icon.png`.
- The **folder name is the clip name**; wrap mode + fps come from the hard-coded `playerAnimInfo` table (below). Unknown folder → warning "No Anim data found", clip skipped.
- `cc_sprite_placeholder.png` inside a `_hand` / `_twohands` / `death_coop` folder makes that clip reuse the frames of the base folder (Shade ships 1-frame placeholders for most `_twohands` folders).
- `dodge*`: frames `0 … floor(n/2)` are flagged `invulnerableFrame = true, groundedFrame = false` (5 of 9). `tablekick*` and `slide*`: every frame invulnerable.
- `breach_idles/*` and `custom/*` clips are created as **Loop, 8 fps**; change with `Loader.SetupCustomBreachAnimation(character, clip, fps, wrapMode, loopStart, maxFidget, minFidget)`.
- Breach select uses `select_idle` (core idle) and `select_choose` (on selection) via `CharacterSelectIdleDoer` with fidget interval 4–10 s. Default sprite after build: `{nameShort}_idle0`.
- `_armorless` twins of every clip are supported (Marine-style armour), dropped otherwise.

### 2.2 The 61 clips: Alexandria wrap/fps vs. vanilla Convict frames (wiki GIF delay) [C]

| Clip(s) | Alexandria wrap / fps | Vanilla Convict frames @ ms | Notes |
|---|---|---|---|
| `idle`, `idle_hand`, `idle_twohands` | Loop 6 | 4 @ 160 | side view (aim −60…25° or 155…−120°) |
| `idle_forward`, `_hand`, `_twohands` | Loop 6 | 4 @ 160 | facing camera (aim −60…−120°) |
| `idle_backward`, `_hand`, `_twohands` | Loop 6 | 4 @ 160 | facing away (aim 60…120°) |
| `idle_bw`, `idle_bw_twohands` | Loop 6 | 4 @ 160 | back-diagonal (aim 25…60° / 120…155°) |
| `run_right`, `_hand`, `_twohands` | Loop 9 | 6 @ 100 | side run (all sideways movement) |
| `run_right_bw`, `_twohands` | Loop 9 | 6 @ 100 | side run seen from behind (aiming up-diagonal) |
| `run_down`, `_hand`, `_twohands` | Loop 9 | 6 @ 100 | aiming straight down |
| `run_up`, `_hand`, `_twohands` | Loop 9 | 6 @ 100 | aiming straight up |
| `dodge`, `dodge_bw` | Once 12* | 9 @ 70 | roll down / up; *fps overridden = frames ÷ roll time |
| `dodge_left`, `dodge_left_bw` | Once 12* | 9 @ 70 | sideways roll (`_bw` = sideways-and-up) |
| `death` | Once 12 | 8 (410 ms hold, then 80) | stagger → fall sideways → lie |
| `death_shot` / `death_coop` | Once 12 / 16 | 12 @ 50 / 12 @ 60 | launched upward, lands (22×28 canvas) |
| `pitfall`, `pitfall_down` | Once 15 | 6 @ 70 | shrink into the pit (see §3) |
| `pitfall_return` | Once 11 | 6 @ 70 | climb back out (16×26) |
| `chest_recover` | Once 12 | 7 @ 80 | climbing out of a chest |
| `item_get` | Once 9 | 9 @ 120 | holds item overhead (22×28) |
| `doorway` | Once 10 | 10 @ 100 | walks into the elevator, shrinking to 3×5 px |
| `spinfall`, `timefall` | Loop 16 / 8 | 6 @ 60 / 8 @ 120 | falling between floors / time-fall flail |
| `spit_out` | Once 12 | 12 @ 80–160 | spat out by the tarnisher (18×41) |
| `slide_right`, `slide_up`, `slide_down` | Loop 2 | 1 static | table slide poses |
| `tablekick_right`, `_hand`, `tablekick_down`, `_hand`, `tablekick_up` | Once 8 | 4 @ 80 / 3 @ 100 | table flip |
| `pet` | Loop 6 | 2 @ 200 | petting the dog |
| `jetpack_down`, `_hand`, `jetpack_right`, `_bw`, `_hand`, `jetpack_up` | Loop 6 | 2 @ 160 | flying |
| `ghost_idle_{back,back_left,back_right,front,left,right}` | Loop 4 | 4 @ 250 | co-op ghost |
| `ghost_sneeze_left`, `ghost_sneeze_right` | Once 8 | 4 @ 250/120 | ghost fidget |

Where the wiki delay disagrees with Alexandria (run 100 ms ≈ 10 fps vs 9; death_shot 50 ms vs 12 fps; tablekick 80 ms vs 8 fps; pitfall_return 70 ms vs 11 fps) trust the game feel over the table — both are within a frame of each other. Every other clip's wiki delay matches Alexandria's fps to rounding, so the table is a faithful copy of vanilla timing. [I]

Vanilla **Pilot** sprite-name frame counts (from a Kyle-style sheet that reuses the dump's names): idle 4, idle_front 6, idle_back 6, idle_backwards 4, run_forward/front/back/backward 6 each, dodge_front/back/left/left_back 9, death 9, shot_death 10, pitfall / pitfall_down / pit_return 6, spin 6, weaponget 6, chest_recover 7, spaceflail 8, run_back_doorway 10, tarnisher 6, tablekick 3–4, jetpack 2, pet 2, slide 1, ghost 4, hand 1. [C]

### 2.3 Which clip plays when (decompiled `PlayerController.GetBaseAnimationName`) [C]
- `gunAngle` is the aim angle (0° = right, 90° = up). Upper half (25…155°) selects the *back* set: 60…120° → `*_backward` / `run_up`; the diagonals → `*_bw` / `run_right_bw`. Lower half: −60…−120° → `*_forward` / `run_down`; everything else → `idle` / `run_right`. "`_bw`" therefore means **back-view side sprite**, not "moving backwards"; moonwalking is just `run_right` flipped.
- Dodge: `|dir.x| ≥ 0.1` → `dodge_left` (or `dodge_left_bw` if `dir.y > 0.1`); otherwise `dodge` (or `dodge_bw` when rolling up). The clip's fps is replaced by `frames / rollStats.GetModifiedTime()`; the wiki states the roll lasts ≈ 0.7 s with the first half invulnerable, so 9 frames ≈ 70–78 ms each.
- Outline: `PlayerController.Start()` calls `SpriteOutlineManager.AddOutlineToSprite(sprite, outlineColor, 0.1f, NORMAL)`; the hand controller adds a black outline too. Ghost and jetpack sets pick by the same angle bands.
- Breach (foyer) idles are separate clips: Convict `select_idle` 12 @ 200 ms, `select_choose` 11 @ 110 ms, plus fidgets (`select_crossarms` 4, `select_light` 18, `select_smoke_idle` 4, `select_trash` 6, `select_wind` 11 …). Pilot: `select_idle` 5, `select_choose` 9, `select_crouch` 4, `select_crouch_draw` 4, `select_pose` 5, `select_pose_dance` 3, `select_thumbs_up` 7. Robot (Shade base): `select_idle` 4, `select_choose` 8, `error` 16, `head_spin` 6, `off` 5, `stargaze` 3, `stargaze_cry` 5, `tummy` 9. [C]

## 3. Style rules of vanilla sprites (measured)

- **No baked outline.** Convict frames contain **zero** near-black pixels; Pilot has 12–14 (a `17,17,19` belt/strap accent), Hunter 5–7 (pure-black eye/detail pixels). Silhouette edges are fill colours touching transparency; the black 1-px outline you see in game is generated at runtime. The modding guide warns: pure black near the edge makes the auto-outline "strange and bumpy". [C]
- **Palette:** 8 colours (Pilot), 9–10 (Convict), 15 (Hunter) across an entire frame. Each material gets a base tone plus one darker edge/shadow tone, occasionally a single-pixel highlight (Convict's hair has `255,255,255` glints). Shadow tone is placed along one side of a shape, not rendered as volume. [C]
- **No dithering, no anti-aliasing:** no checkerboard runs and no intermediate tones anywhere in the decoded frames. [C]
- **Idle (4 fr, 6 fps):** feet stay on the same row; the top of the head drops 1 px (Convict `0,1,1,0`; Hunter `0,1,1,0`) or up to 2 px (Pilot `0,1,2,1`). The body *squashes* — it is not translated. [C]
- **Run (6 fr, ~10 fps):** Convict `run_right` head-top rows `4,0,1,4,1,4` and bottom rows `22,18,20,22,19,21` → the whole body rises **4 px**, feet off the ground on frames 2 and 5, legs tucked on airborne frames, splayed 1-px sticks on contact frames. Pattern: contact → airborne → passing → contact → airborne → passing. `run_down`/`run_up` do the same with 4–5 px travel. A community Pilot-base sheet copies it (tops `2,0,1,2,0,2`). This snappy hop is what "vanilla-like" means; an eased 6-frame sine reads as "too smooth". [C]
- **Dodge (9 fr):** crouch (17 px tall) → leap (13 px, top row 1) → tuck → four ball frames 10–13 px tall rotating through back and upside-down views (one frame 17 px wide with arms out) → stand-up (18 px). The sprite squashes and rotates in place; horizontal travel is done by the game. [C]
- **Death (8 fr):** frame 1 held ≈ 0.4 s (hit pose), then stagger and topple sideways; bbox shifts 5 px to the side and height drops 20 → 17 as the body lies down; last two frames identical. `death_shot` launches the body up 6 px then drops it. [C]
- **Pitfall (6 fr, 70 ms):** the character shrinks toward the hole's centre (18 → 14 → 11 → 7 px tall), then two single-colour frames: a 3×3 cross and a 5×5 cross (a sparkle/blip). `pitfall_return` starts 8–10 px below the canvas top and rises. [C]
- Wiki comment on The Spriters Resource sheets: "about 150 ms per frame" for character animations (page itself blocked by a bot check during research). [I]

## 4. Tutorials, templates and tools

- **MTG "Creating A Standalone Custom Character"** (gitbook → embedded Google Doc): recommends Aseprite (or LibreSprite, GIMP, Paint.net), ImBatch for batch recolours; links the Sorted/Unsorted **Sprite Dump** and ready-made **Custom Base** zips for each vanilla character (incl. *Pilot Custom Base*); rule: keep every frame at its original canvas size; sheet-form sprites are packed edge-to-edge. Also documents `characterdata.txt` stat defaults and `ccremove.spapi`.
- **Gitbook "Important Sprite Creation Information"**: stay under 30×30 px; the game auto-generates the black border; avoid pure black at edges; practise by editing base-game sprites. **"Pixel Measurement Conversions"**: `n = px/16`, count from the sprite's bottom-left (hand and barrel offsets).
- **Kyle's Custom Characters Mod** (ModWorkshop 24802 / Thunderstore / GitHub): the original loader (`sprites/` with vanilla file names, `foyercard/`, `punchout/`), bundled creation guide and video; **Sprite Replacement Extension** (ModWorkshop 23807) adds the `tk2ddump` console command and links the Farewell-to-Arms TK2D/DF sprite dumps; **ETGMod Reskinnable Sprite Dump** (ModWorkshop 17528).
- **Bama EtG Custom Character Sprite Tool** (ModWorkshop 31073, GitHub AlabamaHit/Bama-EtG-Sprite-Tool): renames/copies your frames into the correctly named files; does not resize.
- **Reference implementations for Alexandria's new sprite setup:** OMITB `Characters/Shade` and `Acolyte` (Robot base; art by TankTheta) — canonical folder layout incl. `breach_idles/`; GungeonCraft `Rancher.cs` (per-clip fps overrides — idle 9, run 11, select_choose 12; notes that dodge fps overrides have no effect; `AddHatOffset` per frame); Kotonoha (Pilot base, vanilla names); Some-Bunny `Modular/Storage/AnimationData.cs` (vanilla sprite-name → clip-name map, e.g. `run_side → run_right`, `run_bw → run_right_bw`, `tarnisher → spit_out`, `pitfall_front → pitfall_down`).
- **SpecialAPI/RemoveBreachCharacterEffects** (`ccremove.spapi`) strips base-specific breach effects (Convict cigarette, Hunter dog, Gunslinger cost).
- Community help: Mod the Gungeon Discord (link on the wiki Modding page), `#modding` channel.

## 5. Direct implications for Pluto's generator

1. Draw **no outline**; keep the darkest fur tone clearly above black (a black cat needs a dark-grey/blue-grey body so the runtime outline still reads). [I]
2. Body ≈ 14–16 px wide, 19–22 px tall; head ≈ half the height; 1-px stick legs; eyes = 1 px dots 5–6 px apart, mouth a 2–3 px line. Whiskers/ears as 1-px features. [I from §1.3]
3. Whole-character palette ≤ ~10 colours, 2 tones per material, hard edges, no AA/dither.
4. Idle: 4 frames @ 6 fps, 1–2 px head-top squash, feet fixed.
5. Run: 6 frames @ 9 fps (Alexandria) with a **4 px hop**, feet off the ground on 2 frames, legs tucked when airborne — not a smoothed sine.
6. Dodge: 9 frames, crouch–leap–4 ball frames–stand; keep the ball ~10–13 px tall; the game sets the fps.
7. Use the Alexandria table (§2.2) for every other clip; keep clip folder names exact; use `cc_sprite_placeholder.png` for `_hand`/`_twohands`/`death_coop` variants you don't draw.
8. Keep the bottom-left anchor discipline: same feet row and centre column in every frame; allow taller canvases for dodge/item_get/pitfall_return if 20 px is not enough.

## Sources

- Alexandria CharApi: [SpriteHandler.cs](https://github.com/Nevernamed22/Alexandria/blob/main/CharApi/CharacterBuilding/SpriteHandler.cs) (playerAnimInfo table, SetupLitterallyEverything, hand quad), [Loader.cs](https://github.com/Nevernamed22/Alexandria/blob/main/CharApi/CharacterBuilding/Loader.cs) (folder names, SetupCustomBreachAnimation, select_idle/choose), [SharedExtensions.cs](https://github.com/Nevernamed22/Alexandria/blob/main/Misc/SharedExtensions.cs) (ConstructDefinition, 16 ppu, bottom-left anchor), [Thunderstore page](https://thunderstore.io/c/enter-the-gungeon/p/Alexandria/Alexandria/).
- Decompiled game code (Re-ETG dump): [PlayerController.cs](https://github.com/FlowSand/Re-ETG/blob/master/Assets/_RawDump/C%23/Assembly-CSharp/PlayerController.cs), [PlayerHandController.cs](https://github.com/FlowSand/Re-ETG/blob/master/Assets/_RawDump/C%23/Assembly-CSharp/PlayerHandController.cs), [Gun.cs](https://github.com/FlowSand/Re-ETG/blob/master/Assets/_RawDump/C%23/Assembly-CSharp/Gun.cs), [DodgeRollStats.cs](https://github.com/FlowSand/Re-ETG/blob/master/Assets/_RawDump/C%23/Assembly-CSharp/DodgeRollStats.cs).
- ETG wiki frame data: [Pilot_ingame.gif](https://enterthegungeon.wiki.gg/wiki/File:Pilot_ingame.gif), [Convict_ingame.gif](https://enterthegungeon.wiki.gg/wiki/File:Convict_ingame.gif), [Hunter_ingame.gif](https://enterthegungeon.wiki.gg/wiki/File:Hunter_ingame.gif), [Convict_Run_Right.gif](https://enterthegungeon.wiki.gg/wiki/File:Convict_Run_Right.gif), [Convict_Dodge.gif](https://enterthegungeon.wiki.gg/wiki/File:Convict_Dodge.gif), [Convict_Death.gif](https://enterthegungeon.wiki.gg/wiki/File:Convict_Death.gif), [Convict_Pitfall.gif](https://enterthegungeon.wiki.gg/wiki/File:Convict_Pitfall.gif), [Convict_Idle_Hand.gif](https://enterthegungeon.wiki.gg/wiki/File:Convict_Idle_Hand.gif), [Convict_hand_001.png](https://enterthegungeon.wiki.gg/wiki/File:Convict_hand_001.png), [Dodge Roll (Move)](https://enterthegungeon.wiki.gg/wiki/Dodge_Roll_(Move)), [Modding](https://enterthegungeon.wiki.gg/wiki/Modding).
- Modding guide: [Creating a standalone custom character](https://mtgmodders.gitbook.io/etg-modding-guide/custom-characters/creating-a-standalone-custom-character) (+ [Google Doc](https://docs.google.com/document/d/135ntlWancU6Mw6o2fevZQVtaIEMWL8TNu9Hd8-Bgng4/edit)), [Important sprite creation information](https://mtgmodders.gitbook.io/etg-modding-guide/all-things-spriting/important-sprite-creation-information.), [Pixel measurement conversions](https://mtgmodders.gitbook.io/etg-modding-guide/making-a-gun/making-the-gun/creating-gun-jsons/pixel-measurement-conversions), [Perpendicularity & height off ground](https://mtgmodders.gitbook.io/etg-modding-guide/sprites/perpendicularity-and-height-off-ground).
- Custom-character repos: [OMITB Shade newspritesetup](https://github.com/Nevernamed22/OnceMoreIntoTheBreach/tree/master/MakingAnItem/Characters/Shade/newspritesetup), [GungeonCraft Rancher.cs](https://github.com/pcrain/GungeonCraft/blob/master/src/Cwaff-Characters/Rancher/Rancher.cs), [Kotonoha](https://github.com/kio-stdioh/gungeon-custom-character-kotonoha), [KyleTheScientist/GungeonCharacters SpriteHandler.cs](https://github.com/KyleTheScientist/GungeonCharacters/blob/master/CustomCharacters/CharacterBuilding/SpriteHandler.cs), [Some-Bunny Modular AnimationData.cs](https://github.com/Some-Bunny/Modular/blob/master/Storage/AnimationData.cs), [SpecialAPI/RemoveBreachCharacterEffects](https://github.com/SpecialAPI/RemoveBreachCharacterEffects).
- Tools / mods: [Custom Characters Mod (ModWorkshop 24802)](https://modworkshop.net/mod/24802), [Sprite Replacement Extension (23807)](https://modworkshop.net/mod/23807), [ETGMod Reskinnable Sprite Dump (17528)](https://modworkshop.net/mod/17528), [Bama Sprite Tool (31073)](https://modworkshop.net/mod/31073), [Custom Characters Mod on Thunderstore](https://thunderstore.io/c/enter-the-gungeon/p/KyleTheScientist/Custom_Characters_Mod/).
- The Spriters Resource (blocked by Cloudflare during research; numbers quoted from search snippets only): [ETG index](https://www.spriters-resource.com/pc_computer/enterthegungeon/), [The Pilot](https://www.spriters-resource.com/pc_computer/enterthegungeon/asset/155533/), [The Hunter](https://www.spriters-resource.com/pc_computer/enterthegungeon/asset/155712/).
