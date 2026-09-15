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
- [x] 2.15.1: plain Coco hop frames clipped his ears (lenient shift on the bare 16x13 drawing) — fixed with a 17x16 canvas, strict pad/shift, Coco clips in the art lint and a 19x18 size guard in validate.py; built green (sha256 48df73ba...faec93)

### Review (2.15.0 Coco synergies)
Built green 2026-09-14: dist/Pluto_The_Cat-2.15.0.zip sha256 380fb7241bd1843d8ea980aee1b8a29954b2725e30851fd38482e54fbd890611 (combined release with the peer's Wet Food Can rework).
Verified statically: compiles, lint 0/0 (knight clips included), validate ok (dog/junkan ids, knight clip counts, no baked outline), 19 knight frames embedded.
Not verified (needs the game): Dog pathing with its follow behaviour paused (the Dog prefab's behaviour list is prefab data), Junkan's SeekTargetBehavior walking to OverrideTarget, `AIAnimator.PlayForDuration("pet")` on the Dog, the helmet clip swap mid-pet/KO.

## Taiyaki Cannon reload v2 + Churu drop finisher (branch taiyaki-reload, 2026-09-15)

User after testing 2.16.3: "Taiyaki reload animation should be improved; also add something at the end like the hairball."

- [x] Reload clip redrawn (reference/gemini/taiyaki_cannon/reload_v2.py): 9 frames at 10 fps = 0.9 s = reloadTime (was 4 frames at 8 fps = 0.5 s,
      and two frames pasted a differently shaped Gemini fish). The approved idle gun stays pixel-for-pixel, so the grip never moves; a Churu
      stick pack arrives at the tail, pushes in, is squeezed flat while a shine runs tail to mouth, pulls out, a bead swells in the mouth,
      the drop falls from the jaw, a glint on the fin.
- [x] Churu drop finisher (TaiyakiCannonGun): a reload that started from an empty clip ends with a drop spat toward the aim
      (5 damage, speed 11, range 7) that splashes where it stops: bonito puff + 3 damage to other enemies within 1.5 tiles.
      ~+1.8 DPS single target on a 40 DPS gun (10 shots in ~1.9 s + 0.9 s reload). Config `Balance/ChuruDrop` (default on).
      GunBehaviour has no reload-ended hook, so OnAutoReload starts a coroutine that waits for Gun.IsReloading to clear and
      only spits if the gun is still in hand with a refilled clip.
      Log lines: `taiyaki churu drop: empty-clip reload ended, drop spawned ...` and `taiyaki churu drop: first splash ...`.
- [x] Previews: docs/art-preview/weapons/taiyaki_cannon-reload-strip.png, -reload.png (APNG 10 fps) / .gif, -reload-inhand.png (APNG) + -still.
- [ ] In-game (Steam machine): the tube reads at 1x and the grip stays in the paw; the clip ends as the gun becomes usable (if the engine
      stretches reload clips to reloadTime nothing changes, the clip is already 0.9 s); empty the clip -> one drop flies from the mouth at
      the end of the reload, the splash puffs flakes and hurts a neighbour; a partial-clip reload gives no drop; switching guns mid-reload
      gives no drop; both log lines present.

## 2.17.0 cat items (branch feat/cat-items from codex/combat-polish 42dae88, worktree ../pluto-cat-items, 2026-09-15)

User: "do all of them, create lore and ammonomicon image for all of them, make sure also the existing ones have funny
story like the other ones, look at the other items that are in the enter the gungeon. You can make all of them a little
bit better. make sure they work properly in the game"

Peer notes (enter-the-gungeon-pluto-37): the Kibble Sack already has a reload "Hairball" -> new item uses
`pluto:hairball_item`, `HairballItem*` config, `hairball_item_icon`; description-only edits in Coco/Taiyaki/KibbleSack
files; changelog under `2.17.0 (in progress)`, no version bump.

- [x] Research: vanilla APIs for root/slow, bullet erase, bullet slow, placed object, piercing, roll hook (subagent)
- [x] Research: mod item pipeline, descriptions, art export, tests (subagent)
- [x] Art: Gemini unavailable (429 prepaid credits depleted on pro and flash, 2026-09-15) -> hand-drawn 16x16 row strings (small-sprite route), review_art pass
- [x] Art: approved icons in reference/art/cat_items/, make_art.py copies them to Resources/Items, validate required list
- [x] C#: BallOfYarnItem (active throw, bounces, tangles: root then slow, re-bat on touch)
- [x] C#: CatnipPouchItem (active timed zoomies: speed + fire rate, afterimage, catnap slowdown after)
- [x] C#: JingleBellCollarItem (passive: dodge roll jingles, erases enemy bullets in a ring, cooldown)
- [x] C#: HairballItem (active grenade: fur cloud slows enemy bullets inside)
- [x] C#: ScratchingPostItem (active placed post: +damage and piercing near it for the room)
- [x] Pure rules class + C# test cases for timers/cooldowns/radius; config block with clamping
- [x] Loot pool: quality tiers, not EXCLUDED; five synergies with existing items
- [x] Lore: five new Ammonomicon entries + rewrite the existing items/guns in vanilla style (mechanic line, then a joke)
- [x] CHANGELOG 2.17.0 (in progress), README item list
- [x] ./build.sh in this worktree green (build, validate, tests, art lint); code review subagent
- [ ] In-game checklist + test build to the Steam tester (read drop page first)

### Review (2.17.0 cat items, 2026-09-15)
Built green in ../pluto-cat-items: art lint 0/0, validate all checks passed, 15 cat item + 52 companion + 75 player kit/config cases, 8 tests OK.
Code review subagent (decompiled-source checks of item lifecycle, active state, bounce+pierce, SilencerInstance signature,
Projectile.Speed / Bullet.TimeScale, synergy registration order): no findings >= 80 %. Its sub-threshold note (a pooled enemy
bullet reused inside a cloud could be "restored" to the old bullet's speed) is fixed: the cloud restores only the exact speed /
bullet it changed.
Previews: docs/art-preview/ammonomicon-cat-items.png (all 13 Ammonomicon pages), reference/gemini/cat_items/build/ (icons, world sprites, mock).
Not verified (needs the game): everything in docs/cat-items-2170-test-checklist.md, in particular tk2dSprite depth of the placed post,
AdditionalShotPiercing on Pluto's guns, the afterimage colour, Bullet.TimeScale on boss patterns, and that the loot pool offers the items.
