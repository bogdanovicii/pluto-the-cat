# Pluto the Cat mod — task list

- [x] Research custom character creation (docs/research/01)
- [x] Research custom gun / active / charm (docs/research/02)
- [x] Verify Mono msbuild + NuGet toolchain compiles against EtG assemblies
- [x] Write design spec (docs/superpowers/specs/2026-09-13-pluto-the-cat-design.md)
- [x] Art generator: palette + base poses (idle side/front/back)
- [x] Art generator: run cycles, dodge roll, death, pitfall, item_get, misc clips
- [x] Art generator: ghost, jetpack, slide, tablekick, breach idles, hand
- [x] Art generator: facecard, foyercard, bosscard, minimap icon, win pic, coop death, loadout sprites
- [x] Art generator: gun sprites (idle/fire/reload) + .jtk2d attach points, kibble projectile
- [x] Art generator: wet food can icon, toss + splash frames
- [x] C#: csproj + packages + Plugin.cs
- [x] C#: KibbleSackGun.cs
- [x] C#: PlutoCharmEffect.cs + WetFoodCanItem.cs
- [x] characterdata.txt
- [x] build.sh + thunderstore manifest/README/icon → zip
- [x] Static validation script (folders, sizes, ids, embedded resources)
- [x] Round 2: better dodge roll + death poses, Royal Canin bag/can/kibble art from references, Ammonomicon page + story, stat pass
- [x] Round 3: white crown spot between the ears on every pose, face card and icons
- [x] Round 4: long raccoon-ringed tail with dark tip on a 24x20 canvas; sways on idle/run, flat on death
- [x] In-game test 1 (Steam Machine, SteamOS/Proton): DLL loads, character build failed (altGun NULL) → fixed in 1.0.1
- [ ] In-game test 2 with 1.0.1: character builds, Breach, gun, can
- [x] v2 phase 1: Nine Lives passive, cat reflexes, kibble x2 + crit + crumbs, can vulnerability + boss stun, 4 synergies
- [x] v2 phase 2: Wet Pluto alt skin, breach idles (loaf/groom/knock), co-op death ghost, bathtub swapper
- [x] 2.0.2: synergy id fix (guessed ids) + per-synergy try/catch + id validation
- [x] 2.0.3: run cycle on the vanilla hop rhythm, short trot stride
- [x] 2.1.0: BepInEx config file, isolated load steps, pluto_check.sh, tail whip / zoomies / hairball, hand-variant sprites
- [x] 2.1.1: v3 art pass (frame-filling shaded face, composed bag/can), hairball hook fix
- [x] 2.2.0: Coco Blue companion (CompanionBuilder), gravy pouch alt gun, kibble bowl drops, Nine Lives banner + fur puff, love burst VFX, select-card pop-in
- [x] 2.3.0: Puffed Up anger passive (scale + fur halo attached like a hat + anger marks + stat mods)
- [x] 2.3.1: bigger fur halo
- [x] 2.4.0: Coco Blue pettable (CanBePet + pet clip), hearts + 3 s speed on pet
- [x] 2.4.1: rim-shading pass on all body frames, Nine Lives mid-run save, capped speed boosts, guarded Puffed Up trigger
- [x] 2.5.0: frame-following fur for Puffed Up (552 layers), bathtub unlock flag fix, git repo
- [x] 2.6.0: Coco blocks enemy bullets (BulletBlocker layer + squish + spark), Squeaky Toy decoy mode (OverrideTarget + flee pathing)
- [x] 2.7.0: Coco knocked-out state (stuffing counter, KO animation, pet to revive, regen)
- [x] 2.8.0: Squeaky Toy in the loot pool (grants/removes Coco), Coco-shaped icon, Pluto cannot drop it
- [x] 2.8.1: two active slots (AdditionalItemCapacity), pet-in-combat decoy, bathtub above Pluto via BathtubOffset
- [ ] 2.9: Punch-Out sprites once the Steam machine logs the Pilot's punchout sprite names
- [ ] git init + tag releases (user has not asked yet)
- [x] Gemini pipeline set up (tools/gen_art.py, key in settings env); 7 references generated to docs/gen; AI-vs-hand comparison → user chose hand-drawn
- [x] Art research: 4 reports in docs/research/03a-03d (craft rules, vanilla EtG conventions, pipeline critique, tooling) → synthesis in 03-hand-drawn-art-improvement-plan.md
- [x] 2.9.0 Art Pass A: no baked outline on body/hand, 24x26 canvas + 4-px hop, lean/ball/tail/ghost fixes, grey-brown hue-shifted palette, one head per view, ear flick, strict pad/overlay, lint_art.py, game-like previews + APNG (awaiting in-game outline screenshot)
- [x] 2.10.0 Art Pass B: squash idle + ear flick, run head lag/ears back, leap/overshoot dodge, tail-drop death, pit blips, slide pose, _bw poses, free-paw hand variants, fur regen
- [x] 2.10.1 Art Pass C: parts library (heads/bodies/legs/paw/tails + squashed/stack helpers), tools/import_png.py, orphan + stray-flicker lint, project skill .claude/skills/pluto-pixel-art, bag silhouette
- [x] Runtime outline verified in decompiled code (PlayerController.Start + AIActor.Start via procedurallyOutlined); 2.10.2 strips Coco too
- [x] 2.11.0: Nine Lives lore (starts on life 7; lives 7, 8, 9; ninth is final), StartingLife config, named-life banner
- [x] 2.12.0: kibble cracks secret-room walls (extra wall damage on hit; no passive reveal by request); no fall damage (OnPitfall + ModifyDamage cancel, Nine Lives skips it)
- [x] 2.13.0: straight run legs (no splits), four vanilla-style dodge clips (side dive + somersault, down/up over-the-back rolls, bw side roll)
- [ ] In-game checks on the Steam machine: Pluto vs Pilot screenshot, gun paw alignment, punchout log lines
- [ ] v2 later: custom sounds (Alexandria SoundAPI needs Wwise soundbanks), custom past, Hegemony unlock cost

## Review

Built and validated on 2026-09-13. `./build.sh` → `dist/Pluto_The_Cat-1.0.0.zip` (DLL 132 KB, 267 embedded PNGs).

What was verified:
- Compiles against the real game assemblies (EtG.GameLibs 2.1.9.1, Alexandria 0.5.10, MtG API 1.9.2) with zero errors.
- Embedded resource names match what Alexandria CharacterAPI (`PlutoTheCat.Characters.Pluto.…`) and the MtG API sprite loader (`PlutoTheCat.Resources.SpriteRoot.<Collection>.<name>.png`) look for.
- All 61 animation clip folders present, every real frame 24x20, placeholders only where Alexandria has a fallback.
- Gun frames each have a `.jtk2d` with a PrimaryHand attach point (Gun.Initialize null-refs without one).
- Loadout ids in characterdata.txt match the ids registered in C#.

Not verified (needs the game): sprite anchoring in-game, foyer position, gun hand placement, charm on bosses.

Risks / notes:
- `PlutoCharmEffect` derives from `GameActorEffect` (not `GameActorCharmEffect`) to bypass the boss gate. Some boss AIs may ignore `CanTargetPlayers = false`; if a boss just idles, that is expected vanilla behaviour of charm on non-standard AI.
- Punch-Out (Rat fight) uses the base Pilot body sprites; only the face cards are Pluto's.
- Foyer position (14.6, 22.1) is a guess; tune in `Plugin.cs`.

## 2.15.0 — Coco Blue synergies (Dog, Ser Junkan)

Design chosen by the user 2026-09-14: Playdate (Dog), Squire +1 stuffing per Junkan form (Junkan), Knighted
(helmet while Junkan is a Holy Knight), helmet BAKED into clips the way vanilla Junkan does it (junk_shspcg_* clip
sets swapped by AnimNames). Version 2.15.0: the peer session enter-the-gungeon-pluto-c4 owns 2.14.0 (Wet Food Can
projectile) and its uncommitted hunks in make_art.py / validate.py / CHANGELOG / PlutoConfig — never revert them.
Engine facts (Re-ETG decompiled): `SackKnightController.CurrentForm` (HOLY_KNIGHT = 6 junk, rebuilt every frame),
`AIActor.OverrideTarget` wins over `PlayerTarget`, Dog has no attack (only `DogItemFindBehavior`), one
`m_pettingTarget` per player; Alexandria `AddAnimation` keeps clip names in `DirectionalAnimation.AnimNames`.

- [x] **Playdate** (`pluto:coco_blue` + `dog`): CocoFriends — while Coco is a decoy the Dog (follow paused) paths to the
      enemy chasing Coco and bites (6 dmg, 1.2 s); petting one wiggles the other (hearts + pet clip, Dog pet → speed burst)
- [x] **Squire** (`pluto:coco_blue` + `junkan`): `MaxStuffing` = CocoStuffing + min(form, 6); Junkan `OverrideTarget` = chaser during decoy
- [x] **Knighted**: Squire tier (not registered — Alexandria can't require 6 junk); `SetKnighted` swaps idle/move/pet/block/ko to knight_* clips
- [x] Art: HELMET 9x8 + HELMET_DOWN in tools/art_v4.py, COCO_KNIGHT_* on a 16x20 canvas (KO 24x16), strict helpers; preview checked
- [x] Swap the 3 `PlutoConfig.CocoStuffing` reads in CocoBlueController for `MaxStuffing` (+ clamp) — after the peer's build is green
- [x] make_art.py export (knight_* folders), lint_art.py companion lint, validate.py tuple list — after the peer's build is green
- [x] ./build.sh (log to file, check exit status), CHANGELOG 2.15.0 above 2.14.0, version bump
- [ ] In-game check on the Steam machine: Dog pathing while follow is paused, Dog bite reach, Junkan charging the override target, helmet swap on pet/KO
- Found in passing: plain COCO_MOVE hop frames clip Coco's ears (lenient shift) — spun off as its own task

### Review (2.15.0 Coco synergies)
Built green 2026-09-14: dist/Pluto_The_Cat-2.15.0.zip sha256 380fb7241bd1843d8ea980aee1b8a29954b2725e30851fd38482e54fbd890611 (combined release with the peer's Wet Food Can rework).
Verified statically: compiles, lint 0/0 (knight clips included), validate ok (dog/junkan ids, knight clip counts, no baked outline), 19 knight frames embedded.
Not verified (needs the game): Dog pathing with its follow behaviour paused (the Dog prefab's behaviour list is prefab data), Junkan's SeekTargetBehavior walking to OverrideTarget, `AIAnimator.PlayForDuration("pet")` on the Dog, the helmet clip swap mid-pet/KO.
