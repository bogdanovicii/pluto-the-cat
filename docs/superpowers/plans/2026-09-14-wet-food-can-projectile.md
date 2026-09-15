# Wet Food Can Projectile Implementation Plan

> **Historical: implementation plan, shipped in Pluto the Cat 2.14.0.** Unchecked boxes are not open work.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the Wet Food Can active into a thrown, tumbling projectile that charms what it hits and bursts into a charming gravy splash, with new hand-drawn can art.

**Architecture:** `WetFoodCanItem : PlayerItem` spawns a cloned .38 Special projectile (hairball pattern). Two MonoBehaviours on the prefab: `CanTumble` cycles four `ProjectileCollection` sprites; `CanBurst` charms/stuns on `OnHitEnemy` and runs the splash once on `OnDestruction`. Art stays row strings in `tools/art_v3.py`.

**Tech Stack:** C# net35 (Mono msbuild), Alexandria 0.5.10 ItemAPI/VisualAPI, Python 3 + PIL art pipeline.

Spec: `docs/superpowers/specs/2026-09-14-wet-food-can-projectile-design.md`

## Global Constraints
- Item id `pluto:wet_food_can`, GameObject name "Wet Food Can", icon `Items/wet_food_can_icon` unchanged.
- Never edit `PlutoTheCat/src/PlutoSynergies.cs` (another session owns it); read `PlutoSynergies.DinnerTime` only.
- Config: `CanSplashRadius` = 2.0 (replaces `CharmRadius`), `CanDamage` = 5; `CharmDuration` 10, `BossStunSeconds` 3, `CanCooldownDamage` 200 stay.
- Projectile: speed 14, range 10, `shouldRotate = false`; tumble frames `ProjectileCollection/pluto_wet_food_can_001..004.png` (16x16).
- Burst VFX: `VFX/gravyburst_001..004.png` (20x20), pool `PlutoVFX.GravyBurst`.
- Build logs go to a file; check the exit status, never a pipe. Stage only this plan's paths when committing.

---

### Task 1: Validation checks for the new assets (the failing test)

**Files:** Modify `tools/validate.py` (section 4, item art)

**Produces:** checks for `wet_food_can_icon.png`, `ProjectileCollection/pluto_wet_food_can_00{1..4}.png`, `VFX/gravyburst_*` x4; the old `wet_food_can_toss_*`/`wet_food_can_splash_*` checks go.

- [ ] Replace the toss/splash list with the icon only; add the projectile-frame loop and `'gravyburst'` to the 4-frame VFX prefixes.
- [ ] Run `python3 tools/validate.py` → expect errors for the missing projectile frames and gravyburst.

### Task 2: Can art

**Files:** Modify `tools/art_v3.py` (`can()`, `CAN_TOSS`, `splash()` → `CAN_ICON`, `CAN_TOSS`, `GRAVY_BURST`), `tools/make_art.py`, `tools/ui_and_items.py` import.

**Produces:** `CAN_ICON` (20x18), `CAN_TOSS` (4 x 16x16: side, lid, side upside down, bottom), `GRAVY_BURST` (4 x 20x20: lid pops, splat + lid, splat + heart, splat + two hearts).

- [ ] Draw the rows (outlined; gold `A/Y/a`, pink `q/I/P/p`, white panel, crown, red band with `K` dots, gravy window `M/m`).
- [ ] `make_art.py`: toss frames → `write_clip(pc, U.CAN_TOSS, 'pluto_wet_food_can')`; drop the items toss/splash clips; `write_clip(vfx, U.GRAVY_BURST, 'gravyburst')` after the love burst; preview sheet uses `U.GRAVY_BURST`.
- [ ] `python3 tools/make_art.py && python3 tools/validate.py` → all checks pass; look at a 10x preview.

### Task 3: Projectile item

**Files:** Rewrite `PlutoTheCat/src/WetFoodCanItem.cs`; modify `PlutoTheCat/src/PlutoConfig.cs`, `PlutoTheCat/src/PlutoVFX.cs`.

**Consumes:** Task 2 sprite names. **Produces:** `WetFoodCanItem.ID`, `PlutoVFX.GravyBurst`, `PlutoConfig.CanSplashRadius`, `PlutoConfig.CanDamage`.

- [ ] `PlutoVFX`: `GravyBurst = VFXBuilder.CreateVFXPool("PlutoGravyBurst", Frames("gravyburst", 4), 10, new IntVector2(20, 20), tk2dBaseSprite.Anchor.MiddleCenter, false, 0f);`
- [ ] `PlutoConfig`: replace `CharmRadius` with `CanSplashRadius = 2f` (key "CanSplashRadius"), add `CanDamage = 5f`.
- [ ] `WetFoodCanItem`: `Init` builds the item + prefab (`SetupProjectile(56)`, `SetProjectileSpriteRight("pluto_wet_food_can_001", 16, 16, false, MiddleCenter, 12, 10)`, add `CanTumble`, `CanBurst`); `DoEffect` spawns toward `unadjustedAimPoint`, sets `Owner`/`Shooter`, plays `Play_OBJ_item_throw_01`.
- [ ] `CanBurst`: hit → remember target, charm (or stun a boss) unless fatal; destruction → guard flag, spawn GravyBurst + LoveBurst, charm/stun every other enemy in the room within the radius (Dinner Time: radius x1.5, duration x2).
- [ ] `./build.sh > log 2>&1; echo $?` → 0; `python3 tools/validate.py` → pass.

### Task 4: Docs and hand-off
- [ ] Ammonomicon text in `WetFoodCanItem.Init`, changelog 2.13.0 entry, `tasks/todo.md` line.
- [ ] Preview sheet to the user; commit only the paths above after the user agrees.
