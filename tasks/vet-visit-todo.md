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
