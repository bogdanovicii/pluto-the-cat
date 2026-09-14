# The Vet Visit (Pluto's custom past) — task list

Separate project in `PlutoVetVisit/`; never touch `PlutoTheCat/`, `tools/`, `thunderstore/`, `build.sh`
(another session edits them). Spec: `docs/superpowers/specs/2026-09-13-vet-visit-past-design.md`.

## Research (done 2026-09-13)
- [x] How Alexandria 0.5.10 wires `hasCustomPast` / `customPast` (docs/research/03)
- [x] Vanilla past pipeline + DungeonAPI room/flow/dungeon loading (docs/research/04)
- [x] Custom boss with EnemyAPI BossBuilder (docs/research/05)
- [x] Draft design spec written

## Awaiting user approval of the design
- [x] User approves spec (story, attack set, room tiles, integration path)
- [x] Write implementation plan (writing-plans skill)

## Milestone 1 — plumbing
- [x] `PlutoVetVisit/` csproj, packages, build.sh, validate.py, thunderstore test manifest
- [x] PastPlugin attaches past to Pluto via `CharacterBuilder.storedCharacters["playerpluto"]`
- [x] PastLevel: GameLevelDefinition `tt_pluto_past`, Harmony patches, Soldier template + hygiene
- [x] VetFlow one-node flow, empty placeholder room
- [x] VetVisitController: fade-in + timed ending (flag, credits, win page, pastWinPic)
- [ ] In-game test 1 (Steam machine): bullet from Blacksmith, `load_level tt_pluto_past`, ending, Breach card — result: pending

## Milestone 2 — clinic room
- [x] clinic_room.py ASCII map -> vet_clinic.newroom + preview
- [x] ClinicObjects (carrier, table, cabinets, scale) + player start + intro dialogue
- [ ] In-game test 2 — result: pending

## Milestone 3 — The Vet
- [x] vet_poses.py clips (idle, move, tell, fire, intro, die), boss card
- [x] VetBoss prefab + Booster Shot + Spray Bottle + intro + health bar + death -> ending
- [ ] In-game test 3 — result: pending

## Milestone 4 — polish
- [x] Pill Time, Cone of Shame, phase-2 tempo, projectile sprites, win picture, music, balance
- [ ] Mid-game save hygiene verified, KILLED_PAST persistence verified — result: pending

## Milestone 5 — integration (separate approval)
- [ ] Merge into PlutoTheCat (or ship second DLL), version bump, changelog

## Status 2026-09-14
- [x] All 13 plan tasks built and reviewed; final whole-branch review clean after one fix wave; tag v0.1.0 (PlutoVetVisit repo, commit 4eec6e8)
- [x] Test zips: PlutoVetVisit/releases/Pluto_Vet_Visit-0.1.0.zip (final), -m1 and -m3 milestone builds
- [ ] In-game tests 1-4 on the Steam machine (docs/checklist.md in PlutoVetVisit) — results pending
- [ ] Milestone 5 integration into PlutoTheCat after the in-game pass
- [x] Pushed to https://github.com/bogdanovicii/pluto-vet-visit (private, main + tag v0.1.0, release with the m1/m3/final zips) — 2026-09-14

## v0.2.0 2026-09-14 — Blacksmith route
- [x] Pluto gets the Bullet That Can Kill The Past from the Blacksmith (Alexandria hasPast registration; already wired)
- [x] Harmony postfix on BulletThatCanKillThePast.Pickup sets BLACKSMITH_BULLET_COMPLETE for Pluto so the Ark opens the past (src/BlacksmithBullet.cs, config GuaranteePastAccess)
- [x] Built, tagged v0.2.0, GitHub release with the zip; README trigger flow fixed (Blacksmith -> Dragun -> Ark, not 'beat the Lich')
- [x] Sent install instructions to the Steam machine session (plutosm-twinkling-valiant): download both GitHub release zips, import in r2modman, test the Blacksmith route
- [ ] Steam machine in-game results (Blacksmith offers bullet, Ark loads the past, room/boss look) — pending

## v0.3.0 / v0.4.0 2026-09-14 — user feedback after the first in-game past
Feedback: Pluto had no weapon, the Vet never attacked / had no weapon, the boss name showed as an error, art and room too plain.
- [x] 0.3.0: starting loadout given in the past (ReinitializeGuns, then by console id); boss card/bar/actor names are string-table keys; fight watchdog (14 s) + directional walk-in; Vet AI: flee/seek/strafe stack, range-gated leading attacks, three phases (Droplet Wall, Vaccination Spiral, Cone of Shame, Snip Time)
- [x] 0.4.0: Vet redrawn (glasses, stethoscope, pocket, shoes, vaccine gun; outline-free export since AIActors are outlined at runtime), 16 new props, room re-dressed; tests updated; docs/preview/clinic-room-mock.png
- [x] GitHub releases v0.3.0 and v0.4.0; drop page carries pluto_vet_visit_zip.json (0.4.0)
- [ ] In-game: does Pluto now spawn with the sack, does the Vet shoot and move, is the name right, how does the room look

## v2 — vanilla-depth past (design 2026-09-14, docs/superpowers/specs/2026-09-14-vet-visit-v2-design.md)
- [x] Research: vanilla pasts structure (04a), Alexandria APIs for waves/enemies/NPCs/cutscenes (04b)
- [x] Design spec drafted: one 30x52 room with three gated zones, three acts, cast (Owner, Receptionist, Rex, Grandma Cat, critters, Vet Techs, escaped patients, the Nurse, the Vet)
- [x] User approval of the design (2026-09-14: "start with the next phase")
- [x] Gemini concept set for the three-zone past (PlutoVetVisit/docs/past-concepts.md, 17 images, ASCII zone draft) — 2026-09-14
- [x] 0.5.0 room + gates + vanilla waves: 30x52 map with two 2-cell dividers and centre gaps; clinic door prop (closed/open frames,
      ClinicDoor.cs toggles the HighObstacle collider); kennels + nurse station; controller runs waiting room -> ward (door seals,
      two config-driven waves of rat/parrot/mutant kin at side-door and kennel cells, timeout guard) -> theatre (Vet spawns on entry,
      dialogue, fight). 46 unit tests; build + validate green; dist/Pluto_Vet_Visit-0.5.0.zip — 2026-09-14
- [ ] In-game test 5 (docs/checklist.md milestone 5): doors render and block, waves spawn and clear, wall segments draw as walls — pending
- [x] 0.6.0 cast: tools/tech_poses.py (32x32, 5 clips) + tools/nurse_poses.py (48x40, 6 clips); src/VetTech.cs (Tech + Nurse via
      EnemyBuilder, Bullet-Kin brain, syringe/droplet/net bank); waves use Techs; Vet calls Nurse + 2 Techs at half health — 2026-09-14
- [x] 0.7.0 story: tools/npc_poses.py (owner, receptionist, rex, grandma), src/ClinicNpc.cs placeables with comments, intro cutscene
      (skippable lines, intercom, Owner walks out), critters, epilogue line — 2026-09-14
- [x] 0.8.0 dressing: 8 new props placed, hearts on the nurse station, door sounds, [Cast] health config; CastLayout.cs generated;
      72 unit tests; build + validate green; releases/Pluto_Vet_Visit-0.8.0.zip — 2026-09-14
- [ ] Steam hand-off of 0.8.0 (GitHub release v0.8.0 + drop page + message to plutosm-unified-hearth) — in-game results pending
- [ ] 1.0 merge into PlutoTheCat (separate approval)

## 0.9.0 2026-09-14 — feedback after the in-game 0.8.0 test (this session)
Feedback: still no gun; ward Techs did nothing; wants greetings in the ward, dialogue in the theatre before the boss, everyone shooting with boss-like patterns, balanced; white-tile vet-lab look.
- [x] Loadout watchdog (arrival + 1/3/6/10/20/40/60 s), AddGunToInventory then LootEngine, logged, `vet_loadout` console command
- [x] Engage(): HasBeenEngaged + State Normal + brain on + damage on for every spawned actor; OverrideTarget fallback after 2 s; heartbeat log at 2 s / 6 s
- [x] Tech three-round bursts (Hegemony-soldier style), cooldown 2.2 s; Vet syringes 10; phase-1 cooldowns longer; Vet 1000 / Tech 18 / Nurse 150; wave 2 = 5
- [x] Ward greeting by a Tech (Ward1-3), intercom lines (Ward4-5), Vet half-health line + Nurse arrival line + last-fifth line (Fight1-4)
- [x] White floor tiles as 25 strip props (HeightOffGround -4, config FloorTiles)
- [x] Built, tests pass, tag v0.9.0, GitHub release, drop page
- [ ] In-game: gun present? Techs move+shoot? floor under actors? difficulty (hearts lost, time to kill)

## 0.8.0 in-game feedback (user, 2026-09-14) -> brief for the next session
Tested 0.8.0: works, much better, but not the Gemini look; Pluto has no gun and cannot shoot; ward staff do nothing
(no movement, no shots); wants a Tech greeting in the ward that sends Pluto to the theatre, the Vet dialogue then the
boss fight; every clinic human able to attack with vanilla-like patterns; balanced (not easy, not hard); story well driven.
- [x] Brief written: PlutoVetVisit/docs/prompts/next-session-0.10-prompt.md (starts from the other session's 0.9.0)
- [ ] 0.10.0 by the next session; then the in-game pass; then 1.0 merge (separate approval)

## 0.10.0 2026-09-14 — plays, looks and reads like a vanilla past (this session)
Started from 0.9.0; verified its claims against the decompiled game (fedes1to/EtG-source) before changing anything.
- [x] Guns: the Ark's ResetPlayers hands the starting guns back and clears input overrides before the load; nothing strips them after.
      Loadout check rewritten: repairs gun + renderer (empty-reason ToggleGunRenderers clears every hide key) + input
      (ClearAllInputOverrides, PreventPausing) outside our own cutscenes; runs after the fall-spawn, after each cutscene, every 3 s;
      logs a before/after snapshot; `vet_loadout` prints it.
- [x] Staff: root cause = EnemyBuilder actors are born State Inactive (no ObjectVisibilityManager; autoEngage only feeds it) so the
      BehaviorSpeculator never ticks. Engage() hardened (each step logged), heartbeat re-engages, SelfEngage component on Tech/Nurse
      (console spawns fight too, greeter held until his lines). Tech range 20, LOS on, Hegemony burst cadence, no timing differentiator.
- [x] Story: greeting sends Pluto to the far door; Rex/Grandma bubble on the door; Vet line at the Nurse's arrival; BeginCutscene/EndCutscene
      pair (lock, unlock, loadout repair, input logged) in a finally for all three acts.
- [x] Patterns: measured vs Bullet King / Gorgun / Beholster / Gull; three phases (60 %, 25 %), InitialAttackDelay 2 s, breathers,
      wall gap opens on Pluto and walks, "full course" sequential group, pills pop when shot, shot audio on every bank entry; Vet 800 HP.
      `[Balance]` knobs: BulletSpeedScale, BossCooldownScale, speeds, Tech/Nurse cooldowns.
- [x] Look (art subagent, hand-drawn row-strings): per-zone tiled floors, wall faces (room now 30x54), lamp head/arm/pool, strapped
      80x40 table, barred kennels + cone variant, 9 orange chairs, 112 px desk, double cabinets, station with bowls, tank on a stand;
      FloorTiles/WallFaces wired; pale ambient via Room.customAmbientLight + LabAmbientLightController disabled. validate.py check_look.
- [x] 79 unit tests, build + validate green; docs/checklist.md milestone 10 (log lines + knobs); changelog; version 0.10.0.
- [x] Release chain: releases/Pluto_Vet_Visit-0.10.0.zip (sha256 e1f0ca65...86cf4a), tag v0.10.0 pushed, GitHub release v0.10.0, drop page v31 (pluto_vet_visit_zip.json verified)
- [x] Steam session messaged as `Download [1e08e7]` (its name changes, the ref stays) with the links, sha256 and the milestone-10 steps; results pending
- [ ] Tester must report: the `loadout on arrival` line; each `wave 1 Vet Tech ... state/awoken/pathed` line; whether Techs move within 2 s;
      hearts lost + time to kill the Vet; anything drawn over Pluto (lamp head, floors, wall faces); screenshot of each zone next to level_overview.png.

## 0.10.1 2026-09-14 — after the 0.10.0 in-game test
Test: Techs awake and moving but every shot threw the AIBulletBank NRE (188x); Pluto's gun active=False, input FoyerInputOnly; stuck at wave 1.
Screenshots (repo root, 13.57.57 / 13.58.04 / 13.58.10): purple lab walls over the wall faces, noisy floor, scattered kennels.
- [x] Root cause (enemy shots): double clone of the bullet copy; Alexandria's Instantiate hook activated it, it died, BulletObject null, aiShooter null deref. One inactive copy + CheckBank/repair per actor.
- [x] Root cause (Pluto): `vet_visit` skips Foyer.OnDepartedFoyer (IsFoyer, ForceNoGun, gun SetActive(false)). Replayed in EnsureLoadout; gun object reactivated; watchdog tick line.
- [x] Engage NRE: no RefreshBehaviors; greeter speculator no longer disabled.
- [x] Art pass from the screenshots: wall faces 480x48 standing at HOG -0.2 (in front of the lab's purple wall, behind Pluto hugging it), wall decor standing on them (HOG from wall_decor_hog), floor variants capped per zone, kennel bank 5 per side (cat/dog/cone/open), ward side doors and mid-floor litter box removed, brown doormat, spaced chairs, 16 px clock, theatre toys in the corner; generator emits ObjectSpec.Perpendicular; validate.py checks the depth rules; build green (51 sprites, 75 placeables)
- [x] Watchdog split: full pass at arrival/cutscene end/console; the 3 s pass only acts on a hidden gun or input override that lasted two ticks outside stealth, rolls, cutscenes and the boss intro
- [x] Code review of the runtime fixes: root causes confirmed against the source; fixed per-player watchdog counters, the engage comment, bank repair write-back to the prefab, preload off, recipe warning, validate.py guard
- [x] Build + validate + 89 tests green; commit c66f603, tag v0.10.1 pushed, GitHub release v0.10.1 (344288 bytes, sha256 058abc2a...16d2); drop page v32 payload decoded and verified
- [x] Steam session messaged as `Download [1e08e7]` with the 10.1 steps
- [x] On request, drop page v33 also carries Pluto_The_Cat 2.13.0 (dist/ build by another session, sha256 ac0441cc...3709, not on GitHub); both payloads verified; Steam session asked to test both
- [x] The character session then republished the drop page with Pluto_The_Cat 2.15.0 (GitHub v2.15.0, sha256 1d9a90ab...9e57); payloads re-verified against the page and GitHub; Steam session sent a correction (install 2.15.0, Vet Visit 0.10.1 unchanged)
- [x] Character session republished again with Pluto_The_Cat 2.15.1 (sha256 48df73ba...ec93, GitHub v2.15.1, verified); tester and character session told that character checksums now come only from the character session; this session sends only Vet Visit checksums
- [ ] Tester must report: the three prefab bank lines, the `loadout on arrival` line, whether Tech bursts fly and hurt, hearts lost and Vet time, a screenshot per zone (purple walls gone? Pluto in front of walls?), cardboard box still hides the gun, all [VetVisit] lines

## 0.11.0 2026-09-14 — hard past (after the 0.10.1 in-game test)
0.10.1 result: the whole past runs start to finish, 0 CreateProjectileFromBank exceptions, Pluto fires, everyone shoots, `past killed`.
Fight ~60-90 s, whole past ~3 min, 1.5 of 3 hearts lost. New from the tester: wave-2 "rat" spawned "Your own slow reflexes" (wrong GUID);
`Duplicate prefab name: 8x8_enemy_projectile_dark(Clone)` x5 in the Vet fight.
User: enemy and add bullets pass through Pluto (no hits); wants normal boss bullets, a HARD past, good AI movement, more weapon-like attacks
(liked the shotgun syringe); boss card: the Vet's art shows 1 s then Pluto's portrait covers it; some dialogue boxes off screen, wants more
dialogue incl. side characters; room nicer, more engaging, hand-drawn, structured placement, Gemini references allowed.
- [x] Research: bullets do not hit because SetProjectileSpriteRight moves the sprite into ProjectileCollection, the vanilla BagelCollider frame lookup fails and the hitbox regenerates as 0x0; duplicate prefab names = six copies named 8x8_enemy_projectile_dark(Clone) (harmless, pools match by reference)
- [x] Research: boss card = both textures stretched full screen, player layer (z 14) over boss (z 6) from about 1.0 s; Pluto's opaque card covers the Vet (character session fixing). Our Vet card is also 100% opaque: make it a transparent hand-drawn cut-out in the right half (x 200-420).
- [x] Research: dialogue off screen because Line() adds +2.25 on top of the NPC talkPoint, TextBox/ThoughtBubble prefabs have fitToScreen off, the camera never moves to the speaker, and the 0.35 letterbox leaves ~11.8 units of height. Plan: PastTalk helper (Head anchor, measure box, pan camera to fit, slide orientation, nudge, two-stage skip); intercom lines as letterbox over Pluto in the ward.
- [x] Research: "rat" 6ad1cafc = Candle Rat (harmless 5 HP, no brain; "Your own slow reflexes" = #KILLEDBYDEFAULT); chick/rabbit/squirrel are harmless critters (fine for the waiting room only); parrot -> gigi ed37fa13 (id map). Vet bug: FleeTargetBehavior triggers on every hit and interrupts his attacks (Uninterruptible false); vanilla floor bosses use Seek only. DashBehavior needs a ShadowObject (the Vet has none). Proposed brains (Seek + MoveErratically, dashes), Syringe Tech flanker, Nurse hop+net, new scripts (stitches, scalpel ring, anesthesia cloud, dart rifle, syringe shotgun, tranquilizer spray, IV line), hard waves with verified GUIDs, HP/cooldown knobs.
- [x] Code: PastTalk dialogue helper + richer script + multi-line NPC comments + chatter + barks (written; compile pending)
- [x] Code: boss card + win picture hand-drawn only; card transparent left of x 190 (validate + test)
- [x] Art: structured room on a grid, 19 new + 5 redrawn hand-drawn props, 6 animated props, 20 examinable props, warm/cool zone floors, ward stripe, pixel-letter signs; NPCs re-seated; 106 tests. Gemini layout references not generated (API prepaid credits used up; prompts saved in LAYOUT_PROMPTS)
- [x] Code: real enemy bullets: manual hitbox sized to each sprite on every bank copy, hitsPlayer/0.5 damage explicit, unique PlutoVet_<name>_<n> names, sprite-exists guard, `bank <name>: ...` and `<actor> first shot: ... built WxH` log lines (compile pending the art regeneration)
- [x] Boss card: owned by the character session (Pluto's player card bosscard_001.png is 427x240 and fully opaque, so it covers the Vet's art); Vet card settings stay as they are; forward the research findings to enter-the-gungeon-pluto-c4
- [x] Code: animated props (ObjectSpec Frames/Fps, looping clip) and examinable props (ClinicExaminable thought bubble, [Props] Comment_* config) written; compile after the art agent regenerates ClinicLayout.cs
- [ ] Code: PastTalk dialogue helper, richer script (intro with Rex/Grandma/Receptionist exchanges, Pluto thought bubbles, ward barks, phase lines, Nurse death), multi-line NPC comments, ambient waiting-room chatter
- [x] Code: hard-past brains: Vet Tech (Seek 9 LOS + MoveErratically, TellOnly burst, dart rifle, sidestep, lunge), new Syringe Tech flanker (syringe shotgun, lunge+fan, flank roll; Tech art for now), Nurse (Seek 6 + MoveErratically, spray, hop back+net, far net, tranquilizer spray, IV line <50 %), Vet (no Flee, Seek 10 + MoveErratically, uninterruptible patterns, hops per phase, stitches, scalpel ring, anesthesia clouds, leap+ring); shadows on for dashes; contact 0.5 for grunts; verified GUIDs, harmless-enemy warning; Wave1/Wave2/Reinforce2/Reinforce3 defaults; [Balance] knobs; vet_cloud_001 sprite (compile pending)
- [x] Art: Syringe Tech variant: the Tech body in plum scrubs ( and ) keys) with a hand-drawn two-needle pump syringe, all five clips via make_clips; CastLayout STECH_*; validate + 5 tests; build exit 0, 218 PNGs, 111 tests
- [x] Art: hand-drawn Vet boss card after the user's example (boss card example.jpg, the Beholster card): 232x229 portrait at (195, 11) on a transparent 427x240 card, 69 % transparent, nothing left of x 195; tools/vet_card.py rows; 4 palette keys (; , < >); preview docs/preview/bosscard-preview.png; projectile test updated for vet_cloud_001
- [x] Code: animated props + examinable props in ClinicObjects (missing frames skipped, not fatal)
- [x] Build, validate, 112 tests, checklist milestone 11; commit 43b15e1, tag v0.11.0, GitHub release (214846 bytes, sha256 ca027ade...f2d2); drop page v36 (Vet Visit card swapped in the published index.html, both payloads decoded); tester messaged (Download [1e08e7])
- [x] Gemini credits back: layout_waiting_room/ward/theatre references generated (reference/gemini/past_concepts/layout_*.png); the redesigned room already follows them
- [x] Vet sprite redraw in Enter the Gungeon style (user, 2026-09-14): 48x40 big-head Vet from Gemini sprite references; CastLayout VET_* drives hitbox, shadow and shoot point; 118 tests; released v0.11.1 (sha 7092f597...), drop page v37 (Pluto 2.15.1 + Vet Visit 0.11.1), tester Download [1e08e7] messaged
- [x] Drop page now Pluto_The_Cat 2.15.3 (published by the character session; transparent bottom-left boss card) + Vet Visit 0.11.1; both payloads decoded and verified; tester sent one combined message (user, 2026-09-14)
- [ ] Await Steam results for 0.11.0/0.11.1 (hits register, AI, boss card, dialogue on screen, new Vet sprite)
- [ ] Tester must report for 0.11.0: bullet lines (built WxH), hits on Pluto, dialogue on screen, wave behaviour, boss card, room screenshots, hearts lost and Vet time
- [x] Code review of 0.11.0 before compiling: no compile blockers; fixed the Syringe Tech lunge fan (a dash's bulletScript is force-stopped before it ticks -> lunge + shoot sequence), PastTalk measuring (renderer bounds after the scale-in, only its own box, intercom anchor not parented to Pluto, body sprite for the head), missing animation frames non-fatal, anesthesia EndOnBlank
- [x] First full 0.11.0 build: exit 0, validate all checks, 106 tests OK, 196 PNGs embedded, 97 placeables

## 0.12.0 (user, 2026-09-14, after the 0.11.1 + 2.15.3 Steam run)
Tester: past runs start to finish, bullets hit for half a heart, 0 bank errors, Pluto's gun works, Vet killed in 30-60 s with Pluto at 0.5 hearts.
- [ ] Vet boss card portrait redrawn like vanilla boss art (bleeds off the card edges, no hard rectangle); agent on tools/vet_card.py
- [x] Card title font drops some lowercase glyphs ("Te Vet", "Doc?or's"): name and subtitle now in capitals (VetBoss.cs)
- [ ] Enemy projectiles: distinct readable sprites per attack family, speed/spread retune, knobs + checklist 0.12.0; agent on projectiles.py / VetAttacks.cs
- [ ] The Vet buried under the operating table and lamp at his theatre spawn: investigate depth + spawn clearance for the 48x40 sprite; agent on clinic_room.py
- [ ] Rooms a little bigger, vet-clinic wall art (X-ray, anatomy poster, vaccination chart, diplomas); same agent
- [ ] Pluto's boss card portrait looks blocky: forwarded to the character session (enter-the-gungeon-pluto-c4), not ours
- [ ] Notes from the log: last-reinforcement Fungun shows the odd display name "Your own slow reflexes" (vanilla actor name, GUID verified earlier); Poisbulon has no bullet bank (goop enemy)
- [ ] Build, tests, release 0.12.0, drop page, tester message
