# Pluto project improvement review

Date: 2026-09-15. Reviewed Pluto the Cat 2.16.2 and Vet Visit 0.14.2.

## Summary

The strongest elements are Pluto's recognizable silhouette, the food-and-plush identity, the samurai reward, and the waiting room → ward → theatre → rescue story. The largest improvement opportunity is combat clarity and reliability: communicate what actors will do, coordinate overlapping attacks, and make physical behavior match the art.

This is a source and asset review, with compilation and existing automated checks. It is not a live gameplay review. “Confirmed” below means the code path is present; gameplay impact still needs reproduction. Design proposals are recommendations, not measured balance conclusions. Some stored preview sheets show earlier iterations; current code and generated layout take precedence.

## 1. Highest-priority correctness findings

### A. Coco blocks more bullets than his stuffing description promises — confirmed

`PlutoTheCat/src/CocoBlueItem.cs:294`: enemy projectiles can collide with the shield continuously, but `stuffing--` occurs only inside the 0.15-second `blockCooldown` gate. Several bullets arriving together can be blocked for one stuffing point.

**Improve:** separate the visual/sound cooldown from damage accounting. Decide explicitly whether one stuffing means one projectile or one short shield interval; the config currently promises projectiles. Verify simultaneous bullets, sustained streams, and the final stuffing point.

### B. Diagnostic logging changes enemy movement — confirmed

`PlutoVetVisit/src/VetVisitController.cs:613`: `Describe()` calls `a.PathfindToPosition(target.CenterPosition)`. `Heartbeat()` invokes it at 0.2, 2, and 6 seconds after a wave spawns. Reading the actor's diagnostic state therefore issues a movement command toward the primary player, potentially interfering with strafing and preferred distance.

**Improve:** make diagnostics observational. Put any path repair in a separate, explicitly gated recovery method. Verify identical movement with diagnostics enabled and disabled.

### C. Ward greeter can bypass the wave recovery mechanism — confirmed

`VetVisitController.cs:112` and `:671`: the greeting Tech is held in `wave1Extra`, outside the `RunWave()` list. After wave 1, a separate unbounded loop waits for it to die. The wave's 90-second timeout does not cover this enemy.

**Improve:** register the greeter with the encounter's tracked enemies. A trapped or inactive greeter must use the same recovery rules as the wave. Prefer targeted unstick recovery before the existing emergency kill fallback.

### D. Delayed reinforcements can spawn after boss death — confirmed missing guard

`VetVisitController.cs:432`: `Reinforce()` waits 1.2 seconds and then spawns enemies without rechecking `ending` or the Vet's health. A quick kill after crossing half health can leave this coroutine spawning during the ending. `OnBossDied()` starts the ending without explicitly cancelling that coroutine or clearing tracked reinforcements; `EndPast()` waits 3.5 seconds before locking the conversation.

**Improve:** recheck encounter state after every delayed spawn; cancel pending spawns and retire surviving encounter hazards on victory. Test a high-damage kill that crosses multiple phase thresholds, with Nurse and persistent projectiles active. Confirm engine boss-death cleanup rather than assuming it covers these custom actors.

### E. Recovery can clear another system's control locks — confirmed broad mutation

`VetVisitController.cs:777`: loadout recovery clears gun lock overrides, renderer hide reasons, and all input overrides. The periodic input branch excludes this controller's cutscene and boss intro, but cannot identify every legitimate external lock.

**Improve:** own named overrides and clear only those during normal transitions. Keep broad recovery as an explicit emergency diagnostic command. Test death, co-op ghost transitions, stealth, dialogue, and modded items.

### F. “Shoot the pill to pop it” is not implemented explicitly — likely contract mismatch

`VetAttacks.cs:216` describes destructible pills, but `VetBoss.cs:267` disables projectile collisions for all bank entries, including pills. No pill-specific player-shot destruction handler was found. The timed burst and destruction-triggered burst exist.

**Improve:** confirm the live collision behavior, then either implement an explicit shootable-pill contract or remove the claim. Blanking a pill must not create replacement hazards; retain the existing `preventSpawningProjectiles` check.

## 2. Weapons and attack presentation

| Weapon | Current strength | Recommended improvement |
|---|---|---|
| Royal Kibble Sack | Distinctive two-pellet starter; bounce, crumbs, critical chunks and reload hairball | Establish a clear primary role as close/mid-range scatter. Make the empty-reload cough readable, distinguish critical chunks by silhouette, and limit free ammo farming. |
| Taiyaki Cannon | Recognizable food weapon with a precise single shot and bonito impact | Strengthen precision identity through a clearly timed mouth recoil and Churu reload. Align animation timing with the actual shot cadence. |
| Katana | Melee, full-health wave, bullet cutting and reload defense | Show the real damaging arc and reload defensive radius. Validate swing reach against sprite attachment points in every aim direction before adding power. |
| Wet Food Can | Aimed crowd control with splash and boss stun | Show the splash clearly and explain boss stun separately from charm. Test its interaction with Coco's target overrides and chained stun effects. |

### Balance should use sustained output and the whole kit

At defaults, Kibble's two 3.5-damage pellets and 0.2-second cadence give 35 damage/second before reload, misses and criticals. Its 5% chance of 3.5× damage gives an expected 39.375 before reload if both pellets hit. Taiyaki is 40 before reload. Thus its code comment comparing 40 against 35 understates Kibble's expected output.

A simple ten-shot-cycle estimate gives Kibble 26.25 damage/second including critical expectation, versus Taiyaki 27.59, using clip × cooldown + reload. These are model estimates, not exact engine timings. Kibble's hairball, bounce and ammo utility are additional benefits. Measure boss kill time and hit rate before another damage buff.

`KibbleCrumbDropper` rolls on projectile destruction without requiring combat or an enemy hit. An infinite-ammo starter can therefore generate crumbs against walls. `KibbleCrumb.Update()` also consumes a crumb when the held gun cannot receive ammo. Require an intended earning condition, cap room drops, and collect only when useful unless deliberate waste is part of the design.

### Attachment and animation consistency

Taiyaki's documented canvas is 57×31, versus Pluto's 24×26 body. This may be intentionally oversized, but test whether it hides Pluto and nearby threats. Use shared grip/muzzle metadata for art export and runtime offsets. Katana currently has a special 27-pixel fire-frame shift and separately adjusted Casing reach; these should derive from the same authored data.

The Vet and staff use fixed generated shoot points and horizontally flipped animations (`VetTech.ShootPoint()` and `Clips()`). Verify left/right muzzle placement and vertical aim in-game; the source alone does not establish how the engine transforms these attachments. Capture idle, tell and fire overlays with the actual projectile origin marked.

## 3. Pluto character design

Preserve the rounded body, white chest, tabby face and small feet: the scale-check sheet reads clearly on light and dark backgrounds. Prioritize animation silhouette and timing over adding tiny fur detail.

- Make roll anticipation, airborne ball, landing and recovery distinguishable at 1× scale.
- Review backward/two-handed clips with guns attached, not just isolated sprite sheets.
- Make remaining Nine Lives saves visible on demand or through a compact indicator. Current notifications explain a spent life, but players need to plan around the remaining resource.
- Give Samurai Pluto a distinct Puffed Up cue: the current fur layer is intentionally hidden for that costume, while the mechanical buff remains.
- Assess the combined starting package: two death saves, faster movement/rolls, pit immunity, bullet-blocking companion, two actives, and an anger buff. Puffed Up's default damage and fire-rate multipliers imply approximately 1.95× firing output before reload effects. Tune the full package against the intended power fantasy.

Sources: `characterdata.txt`, `PlutoConfig.cs`, `NineLivesItem.cs`, `PuffedUpItem.cs`, `CatTricks.cs`.

## 4. The Vet: visual design and attack brain

The coat, glasses, syringe and masked final phase establish a coherent character. The current sprite sheet has one general syringe-raising tell. Most attacks use the same `tell`/`fire` clips (`VetBoss.Shoot()`), even when producing pills, scalpels, sutures or clouds.

### Give each threat family an identifiable preparation

| Family | Proposed cue | Player response to teach |
|---|---|---|
| Booster / dart | Aim pose and brief weapon glint | Change movement after aim commitment |
| Spray / droplet wall | Bottle shake and widening nozzle gesture | Read the fan or moving opening |
| Pill | Capsule raised, then visible fuse pulse | Decide whether to shoot it, if implemented, or reposition |
| Ring / spiral | Circular wind-up with a marked opening or rotation direction | Move into a lane before release |
| Stitches | Needle pull and pulse before each re-aim | Dodge the release rhythm |
| Anesthesia | Mask adjustment, visible canister vent | Leave space for persistent hazards |
| Hop / lunge | Crouch, direction cue and landing recovery | Move away from the destination |

The reusable `Hop()` currently has null charge and dash animation fields. Distinct anticipation and landing poses would improve perceived intentionality more than additional movement speed.

### Coordinate selection rather than continually expanding the attack list

Phase 2 already introduces many families. Keep phase 1 as instruction, phase 2 as combinations, and phase 3 as a recognizable escalation. Add repeat avoidance, a preferred distance band with separate enter/exit thresholds, and a recovery period after heavy sequences.

The current ring gaps are mathematical omissions, not guarantees of a reachable safe route. Arena walls, the table, other enemies and lingering clouds can invalidate them. Score candidate openings against available floor and player travel time. A leap-then-ring is especially important to test near walls and at minimum distance.

Budget simultaneous threat across Vet, Nurse and Techs. For example, let the Nurse apply area pressure while the Vet uses a light burst; delay another heavy wall until the existing lane opens. This is a proposal to test, not a claim that current overlaps are always unfair.

## 5. Companions and movement AI

Coco already has a valuable role: mobile protection and distraction. Keep the Dog as pursuer and Junkan as protector, so companions remain distinguishable.

`CocoBlueController.Flee()` uses distance-based repulsion from all nearby projectiles, then random wobble and sometimes a random available cell. It does not account for projectile velocity, so a receding bullet influences movement like an incoming one at the same position.

**Recommended brain:** explicit Follow, Decoy, Dodge, KnockedOut, Pet and CatchUp states. Score a small set of reachable destinations using incoming collision time, walls, pits, distance from owner and nearby enemies. Keep a chosen dodge briefly to reduce oscillation; invalidate it only when unsafe. Stay within a combat leash so Coco does not draw attacks into Pluto's path.

Track the exact enemies whose target overrides Coco owns, and release those references on room change, disable, knockout and destruction. Currently `EndDecoy()` scans only the current room, creating a cleanup risk when crossing a doorway. Use ownership-aware cleanup for Dog/Junkan changes too; Dog restoration currently resets several fields to assumed defaults.

Profile before optimizing: Coco reinitializes its shield body every update, and companion synergy lookups scan passive items frequently. Cache stable references and avoid redundant physics work only after measuring the runtime cost.

## 6. Past room and encounter design

The current generator defines one 36×63 room with three gated zones, not three separate dungeon rooms. Keep that structure while improving each zone's purpose.

- **Waiting room:** warm, readable staging; one obvious exit; short mandatory dialogue with optional personality chatter. Retain both owners and the animal reactions.
- **Ward:** teach staff roles one at a time before mixing them. The second default wave mixes several vanilla enemy types; make their visual relation to escaped clinic patients explicit.
- **Theatre:** preserve a clear orbit around the central operating-table group. Validate paths using the largest actor footprint, not just a one-cell floor check. Make solid props visually distinct from decoration.
- **Rescue:** preserve the emotional payoff. Offer a replay skip that still performs progression and cleanup. Verify the freed animals' authored paths do not cross furniture; their movement is direct interpolation rather than navigation.

The current theatre preview is strongly dominated by repeated bright tile grids. Reduce floor contrast beneath combat, concentrate detail on walls and perimeter props, and keep enemy bullets above decorative effects. Add localized scuffs and story details sparingly. Check that the final red lighting preserves red stitch and pill readability.

Use a short in-game route inspection: spawn → ward entrance → both sides of the kennels → theatre doorway → each side of the table → rescue route. Repeat with co-op and Coco.

## 7. Vet projectile design

The existing projectile sheet and central `BANK` definition are good foundations: custom silhouettes, light/dark previews, and smaller explicit hitboxes already exist. Preserve this discipline.

- Pair color with shape and motion; syringe/vaccine and droplet/scalpel already share related hues.
- Test thin rotated syringes and scalpels at horizontal, vertical and diagonal angles. Show the live collider, not just the static preview rectangle.
- Give pills a burst countdown, stitches a release pulse, and clouds a clearly readable expiration cue.
- Distinguish persistent hazards from decorative smoke. The cloud has a 12×12 damaging box inside 16×16 art; its border should communicate the dangerous region.
- Test 1× scale on the actual white floor and red final-phase lighting, with friendly shots and bonito/fur effects active.
- Check all multi-stage scripts under blanks, boss death and scene exit. Some scripts explicitly set `EndOnBlank`; others rely on inherited behavior. Verify the contract rather than inferring it from comments.

## 8. Engineering and release improvements

1. Split the 1,229-line `VetVisitController` by responsibility: encounter progression, dialogue, loadout recovery, diagnostics and ending. Preserve behavior while extracting; do not rewrite everything at once.
2. Validate config ranges at binding: positive health, speed and cooldowns; valid clips; bounded counts and probability values. Current binders accept raw values, although a few consumers clamp locally.
3. Add meaningful behavioral tests for pure logic: phase selection, pattern geometry, wave completion, state transitions and cleanup ownership. Keep source-string contracts as wiring checks; they cannot prove AI execution.
4. Put existing tests and art lint into build/release gates. The two build scripts regenerate, compile and validate, but do not run the unit suite or the standalone character art lint.
5. Resolve the compiler's `mscorlib`, `System` and `System.Core` version conflicts using a consistent target-framework/reference set.
6. Pin the Python environment, address Pillow deprecation and unclosed-file warnings, and verify regeneration produces no unexpected tracked diff.
7. Refresh the root and past READMEs and old roadmap. They describe older versions, layouts and features; identify which design documents are historical.
8. Define the two-package compatibility contract. Vet Visit says it needs Pluto but its Thunderstore manifest does not declare a Pluto dependency. Add the real published package coordinate when available; retain clear manual instructions until then.
9. Record runtime results per build: loadout, first actor movement, first damaging shot, phase entry, victory cleanup, costume unlock and co-op completion. Existing checklists contain historical pending items and should not be treated as current verification.

## 9. Recommended order and acceptance criteria

| Priority | Work | Acceptance |
|---|---|---|
| P1 | Stuffing accounting, greeter tracking, reinforcement cancellation, observational diagnostics | Reproduce each edge case; no stuck ward, post-victory spawns or logging-induced movement |
| P1 | Control-lock ownership and encounter cleanup | Dialogue, death, co-op and scene exit restore the correct controls and targeting |
| P2 | Unique tells, dash anticipation, reachable gaps and shared threat budget | Players can identify attacks before release; test corner and obstruction cases |
| P2 | Coco destination scoring and override cleanup | No repeated wall oscillation, stale target overrides or avoidable owner crossings in test scenarios |
| P2 | Weapon attachment and sustained-output pass | All-direction grip/muzzle/collider captures; measured kill times for both costumes |
| P3 | Room contrast, costume feedback, projectile lifecycle cues | Clear at 1× on normal and red-lit floors with all effects enabled |
| P3 | Controller extraction, tests, build gates and documentation | Existing checks pass; clean regeneration; release checklist records runtime evidence |

## Verification performed

- Both projects: `msbuild <project>.csproj -p:Configuration=Release -v:q -nologo` exited 0. Both reported MSB3277 assembly-version conflicts for mscorlib, System and System.Core.
- Vet Visit: `python3 -m unittest discover -s tools/tests -q` passed **186 tests**. Pillow deprecation and unclosed-file ResourceWarnings were emitted.
- Main character: `python3 tools/lint_art.py` checked **286 frames**, with **0 errors and 0 warnings**.
- Inspected character scale, weapon/costume, Vet animation, theatre and projectile preview images.
- No live game session, full packaging validation or measured performance/balance run was performed. Gameplay code and art were not changed by this review.
