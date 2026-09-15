# Samurai Pluto and a living clinic — design

> **Historical: design shipped as Pluto the Cat 2.16.0 and Vet Visit 0.14.0.** Current behaviour: the two CHANGELOGs.

Date: 2026-09-14. Status: design, awaiting the user's review. Nothing here is built yet.

Two parts, two owners, one shared interface:

| Part | Release | Owner | Repo area |
|---|---|---|---|
| A. The Vet Visit: pick-up ending, living kennels, theatre mood, masked Vet, clinic sounds, Breach trophy, costume-aware loadout, art redone with the new pipeline | Vet Visit 0.14.0 (after 0.13.0 ships) | session enter-the-gungeon-pluto-3d | `PlutoVetVisit/` |
| B. Pluto: samurai costume replacing Wet Pluto, unlocked by beating the past; Taiyaki Cannon and katana as the costume's starting guns; boss card busts | Pluto_The_Cat 2.16.0 | session enter-the-gungeon-pluto-c4 | `PlutoTheCat/`, root `tools/` |

Neither part edits the other's files. They meet only at the interface in section C.

## Decisions (from the user, 2026-09-14)

- Features picked: pick-up ending, living kennels, theatre mood, masked last phase, clinic sounds, a reward, Pluto's boss card, plus a samurai skin.
- Reward: a Breach trophy (the Vet's broken syringe on a pedestal) that Pluto can examine.
- Samurai skin: replaces Wet Pluto in the single alternate-costume slot; the bathtub and the Gravy Pouch are retired.
- Loadout is costume-bound: the samurai costume starts with the Taiyaki Cannon and the katana; the normal skin keeps the Royal Kibble Sack.
- Treats gun: Taiyaki Cannon.
- Katana: Blasphemy's rules, longer reach.
- Kimono: indigo and crimson, no helmet.
- Ending: Bianca carries Pluto.
- Sounds: the game's built-in sound events only.
- Art rule (replaces "hand-drawn only, Gemini for reference"): all new art is generated with Gemini first, copied as faithfully as possible, then converted to pixel-perfect game art and cleaned up by hand. This covers sprites, props, animations, cards and pictures.

## A. The Vet Visit 0.14.0

### A1. Pick-up ending

Where: `VetVisitController.EndPast`. Today it sets KILLED_PAST, waits 3.5 s, locks the conversation camera, shows the epilogue, freezes the frame, then starts the credits and the win page. No timer runs before the credits, so a scene of any length fits between the epilogue and the freeze frame.

Beats, all during the existing conversation lock (input override, letterbox, HUD hidden):
1. Bogdan and Bianca are re-shown (`ClinicNpc.Show`) at the theatre's east side door (`TheatreSpawns[0]`, where the Nurse arrives; the zone door behind Pluto has no opening animation) and run to Pluto with `ClinicNpc.Walk`. The camera follows with `OverridePosition`.
2. Bianca: "There you are!" She kneels (clip `kneel`), Pluto is hidden (`IsVisible = false` plus the shadow; both players in co-op), and Bianca switches to `carry` (Pluto in her arms).
3. Bogdan picks up the carrier (clip `pat`, a pat on Pluto's head): "Let's go home, buddy."
4. Pluto thinks: "Home."
5. Both walk two cells toward the door, then the existing freeze frame, credits and win page run. Pluto stays hidden through the credits, as the Convict's getaway car does.

New art: Bianca `kneel` (3 frames), `carry` idle (2) and `carry_walk` (6); Bogdan `pat` (3). New config keys: `EndingBianca`, `EndingBogdan`, `EndingThink`. The loadout watchdog must not restore Pluto's visibility during the ending: the controller sets its `cutscene` flag and a new `ending` flag the watchdog checks.

Log: `[VetVisit] ending: owners in, bianca carries Pluto, credits`.

### A2. Living kennels

Where: `ClinicObjects.AddLoop` builds one loop clip today. Generalise it to several named clips per prop from `<png>_<clip>_f<k>.png` frames. All ten ward kennels move from `Frames = 1` to three clips each:

- `idle`: a slow loop (a tail flick, breathing, an ear twitch).
- `react`: once, then back to idle. Dogs jump up and bark, cats puff up and hiss.
- `rattle`: once, the animal paws the cage door.

A new `KennelCritter` component polls every 0.25 s. If a player is within 2.5 cells, it plays `react` with an 8 s cooldown, and a dog plays `Play_PET_dog_bark_02`. A static `KennelCritter.All` list lets `RunWave` and `Reinforce` call `RattleAll()`. If a clip is missing, the component falls back to a one-frame jitter of ±1/16 cell, so nothing breaks.

Log: `[VetVisit] kennels: 10 critters, 3 clips each`.

### A3. Theatre mood

- Fight start: the operating lamp switches on. An `AdditionalBraveLight` cone sits at `pluto_op_lamp`, warm white, and its intensity ramps from 0 to the `LampIntensity` knob over 0.5 s with `Play_ENM_lighten_world_01`. Fallback if the light doesn't render: the existing `pluto_lamp_pool` floor sprite starts hidden and turns on.
- Last phase (the existing `LastFifth` hook at a quarter of health): set the theatre room's `area.runtimePrototypeData.customAmbient` to `MoodRed` (default 1.0, 0.55, 0.55). The game eases the ambient toward it by itself at 0.35 per second. Play `Play_ENM_darken_world_01`. The lab ambient controller stays disabled; it would take over every frame.
- The Vet's death: the ambient eases back to the normal clinic value.

Knobs: `LampIntensity`, `LampRadius`, `MoodRedR/G/B`. Log: `[VetVisit] mood: lamp on` / `mood: last phase red`.

### A4. The masked Vet

At a quarter of health, the Vet plays a one-shot `mask_on` clip (5 frames: he snaps on gloves and pulls up a surgical mask) with `PlayUntilFinished`. Then `aiAnimator.OverrideIdleAnimation = "mask_idle"` and `OverrideMoveAnimation = "mask_move"`. Phase 3 attacks, which are separate items for the last quarter, use `mask_tell` and `mask_fire`. The death clip gets a masked version, `mask_die`, used after the swap. The clips are named `mask_*` because EnemyBuilder matches clip folders by resource-path prefix, so `idle` would also pick up `idle_mask`.

New art, all with the same canvas and hitbox as the current Vet (48x40, `CastLayout.VET_*`): mask_on 5, mask_idle 5, mask_move 6, mask_tell 4, mask_fire 4, mask_die 8. Log: `[VetVisit] the Vet puts on the mask`.

### A5. Clinic sounds (built-in events only)

`AkSoundEngine.PostEvent(name, gameObject)`. An unknown name is silent, so every event below is logged once the first time it plays, and the tester reports which ones are heard.

| Moment | Event |
|---|---|
| Kennel dog reacts | `Play_PET_dog_bark_02` |
| Intercom line starts | `Play_UI_menu_confirm_01` (the chime) |
| Clinic doors open and close | `Play_OBJ_door_open_01`, `Play_OBJ_door_close_01` (in use today) |
| Heart monitor in the theatre, every 1.2 s while the fight runs | `Play_UI_cooldown_ready_01` |
| Lamp on / last-phase red | `Play_ENM_lighten_world_01` / `Play_ENM_darken_world_01` |
| The Vet charges a big pattern | `Play_ENM_deathray_charge_01` |
| The Vet falls: his tray crashes | `Play_OBJ_glassbottle_shatter_01` |
| Nurse station hearts appear | `Play_OBJ_item_spawn_01` |
| The ending starts | `Play_MUS_Ending_State_02` |

Knob: `ClinicSounds` (default true) turns all of them off.

### A6. Breach trophy

The reward is a trophy in the Breach: the Vet's broken syringe on a small wooden pedestal with a brass plaque.

- When: a Harmony postfix on `Foyer.Start` (Vet Visit DLL). If `GetCharacterSpecificFlag(PlutoLink.Identity, KILLED_PAST)` is true, the trophy spawns once at `TrophyPosition` (config knob; the default is picked from a Breach screenshot, clear of NPCs and the character select pads).
- Examine: a `ClinicExaminable` thought bubble cycling `CommentTrophy`: "The Vet's syringe. He won't need it.|Still sharp. Still mine.|No procedure today."
- Depends on part B removing the forced KILLED_PAST (see C1). Until then the trophy would show for every Pluto player. Vet Visit therefore also checks its own flag file (C2) and shows the trophy only if both are set.

Log: `[VetVisit] breach trophy placed at (x, y)`.

### A7. Costume-aware loadout in the past

`VetVisitController` re-arms Pluto with a hard-coded `STARTING_GUNS = { "pluto:kibble_sack" }`. It changes to: if `player.IsUsingAlternateCostume` and `startingAlternateGunIds` isn't empty, use those ids; otherwise use `startingGunIds`. The loadout log line adds `costume alt True/False, guns [ids]`. For the samurai costume it must show `pluto:taiyaki_cannon` and `pluto:katana`.

### A8. Art with the new pipeline

Order of work for every asset: prompt, generate, copy, convert, clean up, check.

1. Write a Gemini prompt per asset in `tools/gemini_past_concepts.py`: Enter the Gungeon pixel style, exact canvas, facing, palette hints, plain background.
2. Generate with `gemini-3-pro-image` into `reference/gemini/`.
3. Convert with a new tool, `tools/pixelize.py`: crop, downscale to the exact canvas with nearest or area sampling, quantize to the `vetpixel` palette (new keys added as needed), add the 1 px outline rule, and export row strings, so the result stays editable and testable like the current art.
4. Clean up by hand in the row strings: stray pixels, symmetric frames, animation continuity, and the anchor rows the tests pin.
5. Check with the existing validate.py and the tests, and a side-by-side preview (the generation vs the result).

Use the project skill `pluto-artist` (`.claude/skills/pluto-artist/SKILL.md`, written by the character session) for generating, converting and reviewing every asset, paired with `pluto-pixel-art` for animation timing and row-string bodies. Both parts use the same skill, so the Vet's card and Pluto's busts are judged by one rubric.

Scope in 0.14.0:
- New: the ending clips, kennel clips, mask clips and trophy.
- Redone with the pipeline, because the user rejected the hand-drawn look for large art: the Vet's boss card (427x240 card, x < 190 transparent) and the win picture (115x71, fully opaque).

Animated clips are generated as a sheet in one image so the frames stay consistent, then converted frame by frame.

### A9. Testing (part A)

Unit tests:
- The ending clips exist with their frame counts.
- Kennel clips exist for all ten kennels.
- The mask clips share the Vet's canvas and hitbox.
- Every sound event name is in the allowed list above.
- The trophy art is in bounds.
- The costume-aware gun choice (a pure function, tested with both costume states).
- `pixelize.py` output uses only palette keys and exact canvases.

validate.py:
- Card transparency.
- Win picture fully opaque.
- Clip frame counts.

Steam checklist (new `## 0.14.0` section):
- The ending plays with Pluto in Bianca's arms.
- Kennels react and bark.
- The lamp turns on and the room turns red in the last phase.
- The masked Vet appears at a quarter of health.
- Which sounds are heard.
- The trophy appears in the Breach only after the kill.
- As samurai Pluto, the past log shows the Taiyaki Cannon and the katana.

## B. Pluto the Cat 2.16.0 (owner: enter-the-gungeon-pluto-c4)

### B1. Samurai costume replaces Wet Pluto

- `newaltspritesetup/` (Wet Pluto, 63 clips plus `hand_alt_001`) is replaced by the samurai costume with the same clip names.
- The bathtub swapper sprites (`alt_skin_obj_sprite_001/002`) become a kimono on a stand.
- The Gravy Pouch alt gun is removed from `<altGuns>`. The gun itself is either kept as a normal item or removed; that's the character session's call.
- Look: indigo haori `#2b3a67` with a white paw-print crest `#f0ece0`, charcoal hakama `#3a3a44`, crimson obi and hachimaki headband `#b3202a` with trailing tails, and an open V collar showing the white chest. No helmet, so the ears stay visible.
- `PlutoFur` layers must not poke through the sleeves: either mask the fur layers where the kimono covers or turn them off for the costume.
- Art follows the new pipeline (A8), with the character session's artist skill.

### B2. Unlock

- Remove the forced `KILLED_PAST` and `KILLED_PAST_ALTERNATE_COSTUME` in `Plugin.cs`, which exist today only to unlock the bathtub.
- The vanilla `CharacterCostumeSwapper` already shows only once `KILLED_PAST` is set for the character.
- Debug key `UnlockSamuraiCostume` (default false) forces the flag for the tester.
- Verified by the character session: the vanilla `CharacterCostumeSwapper` (line 24) and Alexandria's swapper read only `KILLED_PAST`; `KILLED_PAST_ALTERNATE_COSTUME` is never read. So the Vet Visit's `EndPast` setting `KILLED_PAST` is the whole gate.

### B3. Costume-bound loadout

- Alexandria puts `<altGuns>` into `startingAlternateGunIds`, but only the Breach alt-gun shrine sets `UsingAlternateStartingGuns`.
- Add a Harmony postfix on `PlayerController.SwapToAlternateCostume` that sets `UsingAlternateStartingGuns = IsUsingAlternateCostume` and calls `ReinitializeGuns()`.
- Verified: quick restart keeps both the costume and `UsingAlternateStartingGuns`. Continuing a saved run keeps only the costume (`CostumeID`). The swap also runs before `Start` at character select, quick restart and continue, when the inventory is still null.
- So the postfix sets the flag and calls `ReinitializeGuns()` only in the Breach and only for Pluto, and the Breach alt-gun shrine is blocked for Pluto.
- Unverified: whether a continued run's saved inventory already restores the samurai guns. The Vet Visit logs the gun ids on arrival (A7) to show it.
- `<altGuns>`: `pluto:taiyaki_cannon`, `pluto:katana`.

### B4. Taiyaki Cannon (`pluto:taiyaki_cannon`)

- Model: `GravyPouchGun` or `KibbleSackGun`.
- Look: a golden taiyaki held sideways, about 32x14 px, with the open mouth as the muzzle. Outline `#5a3514`, body `#b8742a`, highlight `#e8b04a`, and red bean `#6b1f24` at the mouth.
- Fires: 6 px mini taiyaki.
- Reload: Pluto tears a white Churu tube and squeezes beige purée into the tail, 3-4 frames.
- Hit: a pale pink bonito-flake puff.
- Starter flags: infinite ammo, not droppable, excluded from the loot pool.

### B5. Katana (`pluto:katana`)

- Blasphemy's rules with a longer reach:
  - A swing that destroys enemy bullets.
  - A piercing crescent wave at full health, white-cyan with 2x2 sakura petals `#f7b7c8` / `#e98aa6`.
  - Reload blocks bullets around Pluto.
  - Infinite ammo; not droppable as a starter.
- Sprite: a curved blade about 32 px long, a black and white diamond-wrap handle and a gold disc guard.
- Route (verified by the character session):
  - Build a new gun like `KibbleSackGun` (not a clone of Blasphemy 417) and take Blasphemy's projectile module.
  - Set `IsHeroSword = true` and `HeroSwordDoesntBlank = false`. True would disable the full-health wave and the reload block, and make the swing reflect bullets instead of destroying them. The wave is in `Gun.HandleSlash`, the reload clear in `Gun.Reload`.
  - Set `InfiniteAmmo`, `CanBeDropped = false` and a larger `blankReloadRadius` (the reload clear radius, default 1).
- Reach:
  - The slash radius is 1.85 × the distance from the gun's `PrimaryHand` point to its `Casing` child transform, not the sprite length.
  - The reach grows by moving `Casing` outward. Unverified: the sprite setup may reset it.
  - The arc is fixed at 45°, and swing damage equals the projectile module's damage, so it is tied to the wave's damage.
- Route 2, the fallback: Alexandria `SlashData` / `SlashDoer` with `slashRange` about 4. It needs its own full-health wave and reload blank.

### B6. Boss card busts

- One shared pose and placement for both skins: the left third of the card, bleeding off the bottom and left edges, transparent elsewhere.
- The normal skin shows Pluto holding the Royal Kibble Sack; the samurai skin shows the kimono with the katana.
- Verified: vanilla has no per-costume card and Alexandria adds every `*bosscard_*` file to one list. The samurai card uses its own file names and a prefix patch on `BossCardUIController.ToggleCoreVisiblity` that picks the set by `IsUsingAlternateCostume`. The Vet's card is unaffected.
- Name strings on the card go in capitals, because the card font drops some lowercase letters.
- Set `player.BosscardSpriteFPS` explicitly. Neither the game nor Alexandria sets it, so Pluto may inherit the Pilot base's value (unverified).
- The samurai card's file names must not contain `bosscard_`, or Alexandria adds them to the normal card list.
- Art: the normal-skin bust (in progress with the pluto-artist skill) fixes the shared pose and placement for the samurai bust.

## C. Interface between the parts

- **C1. Past kill flag:**
  - Vet Visit's `EndPast` calls `GameStatsManager.Instance.SetCharacterSpecificFlag(PlutoLink.Identity, CharacterSpecificGungeonFlags.KILLED_PAST, true)`.
  - The character side reads it with `GetCharacterSpecificFlag(identity, KILLED_PAST)`, with no reference to the Vet Visit DLL. `identity` is the value Alexandria registered for `playerpluto`.
- **C2. Flag file (for the trophy and as a check that the kill is real):**
  - `EndPast` also writes `BepInEx/config/bogdan.etg.plutovetvisit.progress` containing `VetBeaten=true` and the date.
  - Either DLL may read it.
- **C3. Gun ids:** `pluto:taiyaki_cannon` and `pluto:katana`, registered by the character DLL before the character is built.
- **C4. Release order:**
  - Vet Visit 0.13.0 ships first (owners, win picture, reception counter).
  - Part B (character 2.16.0) and part A (Vet Visit 0.14.0) can then be built in parallel.
  - They go on the drop page together, because the trophy and the costume unlock are only meaningful once the forced flag is gone.
  - Each session swaps only its own card on the drop page.

## D. Risks

- `AdditionalBraveLight` initialisation couldn't be read, since the reference DLL has no method bodies. The floor-pool sprite is the fallback.
- A custom `PlayableCharacters` value may not survive in the save file. The flag file in C2 covers the trophy either way.
- The katana's swing cooldown (0.5 s) and the knockback on Pluto (40) are hard-coded in the game, and the vanilla slash effect won't grow with the longer reach.
- A continued (saved) run may not restore the samurai guns (B3). The arrival log in A7 shows it; if it doesn't, the character side re-arms on run start.
- The Gemini-to-pixel conversion may need heavy clean-up for animation consistency. Generate a whole clip as one sheet and keep the tests' anchor rows.
- Removing the forced flags also locks the costume for existing players until they beat the past. This is the intended vanilla behaviour, with the debug key for testing.
