# Combat and project polish implementation plan

> **For agentic workers:** Use superpowers:subagent-driven-development for bounded implementation and review tasks. The user approved the improvement review with “do it”; proceed without another approval gate.

**Goal:** Implement the actionable improvements in the 2026-09-15 review, preserving the story, existing art identity and damage defaults.

**Architecture:** Keep the two plugins separate. Extract encounter lifecycle/recovery into partial controller files and pure policies where useful; keep authored geometry and art in their existing generators. Use narrowly owned state, readable attack cues and deterministic math tests. Live balance and collider verification remain explicit game checks.

**Tech Stack:** C# net35, Unity/EtG/Alexandria, Python/Pillow art generation and tests, Mono compiler.

## 1. Companion and player kit

- [ ] Fix per-projectile stuffing accounting and track/restore owned targeting changes through all lifecycle paths.
- [ ] Replace random repulsion destinations with bounded reachable candidate scoring using incoming bullet trajectories, owner leash and destination stability.
- [ ] Gate crumbs on successful combat hits, bound live crumbs per owner, and retain crumbs until useful pickup.
- [ ] Add remaining-life feedback and a Samurai anger cue using existing effects; preserve damage defaults.
- [ ] Add executable regression tests for extracted math/policies, compile and document runtime checks.

Files: `PlutoTheCat/src/CocoBlueItem.cs`, `CocoFriends.cs`, `KibbleSackGun.cs`, `NineLivesItem.cs`, `PuffedUpItem.cs`, new focused policies/tests as needed.

## 2. Encounter reliability (controller owner)

- [ ] Include greeting Tech in wave tracking; prevent timeout from reporting failed kills as cleared.
- [ ] Make actor descriptions observational; fallback targets must be alive and overrides temporary.
- [ ] Track encounter actors and cancel delayed reinforcement spawns after victory; clear owned hazards before ending.
- [ ] Separate routine loadout repair from explicit emergency repair. Preserve foreign input/render/gun locks.
- [ ] Extract lifecycle/loadout sections into partial files and update wiring tests.
- [ ] Add failure-first regression coverage and compile.

## 3. Vet combat and projectile readability

- [ ] Add recognizable attack-family cues and dash anticipation with existing art/effects; preserve masked phase.
- [ ] Add shared heavy-attack spacing, improve opening placement and avoid repeated pressure where API supports it.
- [ ] Implement explicit pill shooting behavior, blank-safe cancellation and projectile countdown/release/expiry cues.
- [ ] Validate math and compile against the real reference assemblies; document live physics checks.

Files: `PlutoVetVisit/src/VetBoss.cs`, `VetTech.cs`, `VetAttacks.cs`, focused helpers/tests. No uncontrolled asset redraws.

## 4. Room, attachments and tooling

- [ ] Reduce combat-floor grid contrast at its source, retain original floor identity, and generate current room/projectile QA previews.
- [ ] Centralize player weapon attachment metadata and add generated alignment inspection artifacts.
- [ ] Validate bounded configuration, add build test/lint gates, pin Python dependencies and fix test resource warnings.
- [ ] Investigate framework warnings without hiding incompatible references or raising the game target framework.
- [ ] Refresh documentation, record shipped versus runtime-dependent items, and build both local packages.

## Verification

Run changed behavioral tests red then green; run all Python checks, character lint, both Release builds and package validators. Inspect generated art. Review spec coverage then code quality. Do not claim runtime balance or physics correctness without a game session. Do not publish or commit unrelated user assets.
