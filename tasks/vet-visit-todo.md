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
