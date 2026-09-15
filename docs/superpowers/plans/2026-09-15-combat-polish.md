# Combat and project polish implementation plan

> **For agentic workers:** Use superpowers:subagent-driven-development for bounded implementation and review tasks. The user approved the improvement review with “do it”; proceed without another approval gate.

**Goal:** Implement the actionable improvements in the 2026-09-15 review, preserving the story, existing art identity and damage defaults.

**Architecture:** Keep the two plugins separate. Extract encounter lifecycle/recovery into partial controller files and pure policies where useful; keep authored geometry and art in their existing generators. Use narrowly owned state, readable attack cues and deterministic math tests. Live balance and collider verification remain explicit game checks.

**Tech Stack:** C# net35, Unity/EtG/Alexandria, Python/Pillow art generation and tests, Mono compiler.

## 1. Companion and player kit

- [x] Fix per-projectile stuffing accounting and track/restore owned targeting changes through all lifecycle paths.
- [x] Replace random repulsion destinations with bounded reachable candidate scoring using incoming bullet trajectories, owner leash and destination stability.
- [x] Gate crumbs on successful combat hits, bound live crumbs per owner, and retain crumbs until useful pickup.
- [x] Add remaining-life feedback and a Samurai anger cue using existing effects; preserve damage defaults.
- [x] Add executable regression tests for extracted math/policies, compile and document runtime checks.

Files: `PlutoTheCat/src/CocoBlueItem.cs`, `CocoFriends.cs`, `KibbleSackGun.cs`, `NineLivesItem.cs`, `PuffedUpItem.cs`, new focused policies/tests as needed.

## 2. Encounter reliability (controller owner)

- [x] Include greeting Tech in wave tracking; prevent timeout from reporting failed kills as cleared.
- [x] Make actor descriptions observational; fallback targets must be alive and overrides temporary.
- [x] Track encounter actors and cancel delayed reinforcement spawns after victory; clear owned hazards before ending.
- [x] Separate routine loadout repair from explicit emergency repair. Preserve foreign input/render/gun locks.
- [x] Extract lifecycle/loadout sections into partial files and update wiring tests.
- [x] Add failure-first regression coverage and compile.

## 3. Vet combat and projectile readability

- [x] Add recognizable attack-family cues and dash anticipation with existing art/effects; preserve masked phase.
- [x] Add shared heavy-attack spacing, improve opening placement and avoid repeated pressure where API supports it.
- [x] Implement explicit pill shooting behavior, blank-safe cancellation and projectile countdown/release/expiry cues.
- [x] Validate math and compile against the real reference assemblies; document live physics checks.

Files: `PlutoVetVisit/src/VetBoss.cs`, `VetTech.cs`, `VetAttacks.cs`, focused helpers/tests. No uncontrolled asset redraws.

## 4. Room, attachments and tooling

- [x] Reduce combat-floor grid contrast at its source, retain original floor identity, and generate current room/projectile QA previews.
- [x] Centralize player weapon attachment metadata and add generated alignment inspection artifacts.
- [x] Validate bounded configuration, add build test/lint gates, pin Python dependencies and fix test resource warnings.
- [x] Investigate framework warnings without hiding incompatible references or raising the game target framework.
- [x] Refresh documentation, record shipped versus runtime-dependent items, and build both local packages.

## Verification

Run changed behavioral tests red then green; run all Python checks, character lint, both Release builds and package validators. Inspect generated art. Review spec coverage then code quality. Do not claim runtime balance or physics correctness without a game session. Do not publish or commit unrelated user assets.

## Results (2026-09-15)

All items implemented on `codex/combat-polish` in both repos (not pushed, no version bump, no release).

- Main repo: 862d639 companion kit, a7dfe7d Nine Lives + Samurai cue, 3414785 Dog/Junkan ownership, edb1059 config clamping, 4474ff2 docs/requirements, 59bf01b weapon layout + previews, fee0aa3 Mono.Cecil reference (MSB3277 gone), 3ba52cd build gates, 4e91434 validate deprecation.
- PlutoVetVisit: ce728cb encounter reliability, aafd100 docs/warnings, d9f88be + 352ed9f Vet readability/brain/pills, 690cc3f Mono.Cecil reference, 17ee149 build gate, fece8ec art_sources deprecation, e19e7c7 + 113e51a floor contrast and QA previews, 2b0f632 watchdog escalation (code-review fix).
- Verification: both `./build.sh` exit 0 (Pluto_The_Cat-2.16.2.zip, Pluto_Vet_Visit-0.14.2.zip); Vet Visit 203 tests OK with ResourceWarnings as errors; main 7 test modules OK; character lint 286 frames 0/0; no MSB3277 in either project.
- Not verified (needs a game session): all feel, physics, collider and UI claims — see the in-game checklist in the session summary. Thunderstore dependency not declared (no published namespace exists yet). Kibble grip in tools/mock_anim.py/mock_scene.py still (7,5) vs real (4,5).
