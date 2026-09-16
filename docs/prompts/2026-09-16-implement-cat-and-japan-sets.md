# Prompt: implement the cat set (2.19.0) and the Japan set (2.20.0)

Paste everything below the line into a new Claude Code session opened in
`/Users/bogdanionescu/Claude Code Projects/Enter the gungeon pluto mod`.
To run only one round, delete the other round's section.

---

Implement rounds 2 and 3 of the approved design for the Pluto the Cat Enter the Gungeon mod: ten new pieces, one version per round. The design, balance numbers and concept art are already approved by me — do not redesign them, and do not ask me to re-approve them. Build each round end to end, and only stop where this prompt says to stop.

## What to build

**Round 2 → version 2.19.0 (cat set):**
- Spray Bottle — gun, C, `pluto:spray_bottle`
- Feather Teaser — gun, B, `pluto:feather_teaser`
- Toilet Paper Roll — active, C, `pluto:toilet_paper_roll`
- Cone of Shame — passive, B, `pluto:cone_of_shame`
- Coffee Mug "Off The Table" — active, C, `pluto:coffee_mug`

**Round 3 → version 2.20.0 (Japan set), only after round 2 is finished:**
- Takoyaki Launcher — gun, B, `pluto:takoyaki_launcher`
- Ramune Bottle — gun, B, `pluto:ramune_bottle`
- Maneki-neko — passive, B, `pluto:maneki_neko`
- Daruma Doll — active, C, `pluto:daruma_doll`
- Uchiwa Fan — active, C, `pluto:uchiwa_fan`

## Read these first

1. `docs/superpowers/specs/2026-09-16-cat-japan-items-yasupen-design.md`. It is the source of truth: "Shared implementation rules", the "Round 2" and "Round 3" sections (look, mechanic with numbers, synergy, lore seed per piece), "Art sheets and prompts", **"Chosen concepts"** (which candidate to copy for each sheet and the pixel-copy fixes), "Testing and acceptance" and "Risks".
2. `docs/superpowers/plans/2026-09-16-yasupen-2180.md`. The round 1 plan that shipped as 2.18.0. Use it as the template for task shape, TDD steps, file map, commit commands and the hand-off checklist.
3. `tasks/lessons.md` (review at session start, per my CLAUDE.md) and the project memory index.
4. The code you will copy patterns from:
   - Guns: `PlutoTheCat/src/TaiyakiCannonGun.cs`, `KatanaGun.cs`, `KibbleSackGun.cs`.
   - Items: the 2.17.0 cat items `BallOfYarnItem.cs`, `CatnipPouchItem.cs`, `JingleBellCollarItem.cs`, `HairballItem.cs`, `ScratchingPostItem.cs`, with `CatItemKit.cs` and `CatItemRules.cs`.
   - Companion and synergies: `YasupenItem.cs`, `CocoBlueItem.cs`, `CocoFriends.cs`, `PlutoSynergies.cs`.
   - Config: `PlutoConfig.cs` and `PlutoConfigRules.cs`.

The concept images are **local, untracked files** — they are not in git: `reference/gemini/{cat_items_2,japan_items,spray_bottle,feather_teaser,takoyaki_launcher,ramune_bottle}/sheet.png` and `sheet_c2.png` (the Ramune pick is the re-roll's `sheet_c2.png`; the first roll is in `ramune_bottle/roll1/`). The chosen candidate per sheet is in the spec's "Chosen concepts" table. Copy those faithfully; only generate new Gemini art where a piece needs art that no concept covers (see below).

## Process (per round)

1. **Plan:** use `superpowers:writing-plans` to write `docs/superpowers/plans/2026-09-16-cat-set-2190.md` (round 2) or `docs/superpowers/plans/2026-09-16-japan-set-2200.md` (round 3). Follow the Yasupen plan's structure: Global Constraints, file map, one task per reviewable deliverable, complete code in each task, exact balance values from the spec, and a final version/build/hand-off task. Self-review it for placeholders and spec coverage, and commit it.
2. **Build:** use `superpowers:subagent-driven-development`. Do **not** stop to ask me to choose between subagent-driven and inline — use subagent-driven. One implementer and one reviewer per task, the ledger in `.superpowers/sdd/<plan>/`, a final whole-branch review on the most capable model, one fix wave, and a scoped re-review. Carry the "deferred minor" list into the final review.
3. **Art:** every sprite goes through the `pluto-artist` and `pluto-pixel-art` skills: copy the chosen concept, apply the spec's fix notes, review with `review_art.py` and the rubric, and preview at 1x. Gun frames need `.jtk2d` attach points. Grip and muzzle go in `tools/weapon_layout.py` (generated `WeaponLayout.cs`), and every new gun needs an Ammonomicon page icon — extend the gun loop in `tools/validate.py` (around line 170). Send me the preview sheets once they pass review. Do not wait for my approval to continue unless a piece fails the rubric twice.
4. **Finish the round:** bump the version, update both READMEs (the repo `README.md` **and** the packaged `thunderstore/README.md` — the 2.18.0 final review caught the second one missing) and `thunderstore/CHANGELOG.md`, run the full `./build.sh`, and rebuild the zip after any fix wave.
5. **STOP and ask me** with `AskUserQuestion` before any push, drop-page publish or message to the Steam machine. Offer: push + drop page + Steam (recommended) / push only / keep local.

After round 2's hand-off question is answered, start round 3 the same way. Do not wait for my in-game test results between rounds unless I say so.

## Rules that bind every task (my standing instructions)

- **All work goes on `main`**, one new version per round. Version numbers continue from the latest build I have (2.18.0 → 2.19.0 → 2.20.0).
- **Commit** only with explicit paths in one command, and never leave files staged. The shell is zsh, so `$P` does not word-split: use `git add ${=P} && git commit -m "..." -- ${=P}` or list the paths. End every commit message with `Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`.
- **Other sessions:** peer Claude sessions may share this tree. Before building, check `ListAgents` and `git worktree list`. Tell any active peer before building or editing shared files, and let only one session build at a time.
- **Balance:** do not change the spec's numbers. If a mechanic cannot be built as specified, ask me with the options, rather than choosing yourself.
- **Config:** every numeric key goes through `PlutoConfigRules.Clamp` and gets a range in `PlutoConfigRules.Ranges`. **Also add its default to the `defaults` dictionary in `tools/tests/player_kit_cases.cs`**: a test counts one default per ranged key, and the Yasupen plan's file map forgot this file.
- **Findings:** a reviewer finding labelled plan-mandated, or one that contradicts the spec, is my decision. Ask me with the options and your recommendation.

## Verified technical facts (do not re-derive; verified against the real DLLs during 2.18.0)

- **Overrides:** in the referenced Assembly-CSharp.dll, `PassiveItem.DisableEffect`, `Drop` and `OnDestroy` are **public virtual**, so use `public override`. `CompanionItem.Pickup` is `public override`.
- **Companion Update:** a `CompanionController` subclass must use `public override void Update() { base.Update(); ... }`. A private `Update` silently stops the base petting and following logic.
- **Clip swaps:** Coco-style clips are `DirectionType.Single`, which plays `DirectionalAnimation.Prefix`, **not** `AnimNames`. Any runtime clip swap must set `Prefix` (the 2.17.1 helmet bug).
- **Event unhooking:** unhook every player event in `DisableEffect`, `Drop` **and** `OnDestroy`, using the `JingleBellCollarItem` "Unhook" pattern with a stored `wearer` field.
- **Coroutines:** keep the `Coroutine` handle for anything that overrides velocity or state, and `StopCoroutine` it on disable or destroy.
- **Enemy scans:** use `RoomHandler.ActiveEnemyType.All`, and **skip charmed and harmless enemies** (`IsHarmlessEnemy`, see `KibbleSackGun.cs:200`). The 2.18.0 final review found Yasupen hitting charmed allies. The new items (Feather Teaser distract, Coffee Mug shards, Uchiwa gust, Daruma roll) must not repeat that.
- **Hit tests:** test against the enemy's `specRigidbody.HitboxPixelCollider` box (`UnitBottomLeft`/`UnitTopRight`), not its `CenterPosition`. Centre tests miss bosses and big enemies (the 2.18.0 ruling).
- **Engine APIs:** `ItemBuilder.AddPassiveStatModifier(PickupObject, PlayerStats.StatType, float, StatModifier.ModifyMethod)`; `PlayerStats.StatType.GlobalPriceMultiplier` (shops read it); `PlayerController.OnRoomClearEvent`; `LootEngine.SpawnCurrency(Vector2, int)`; `KnockbackDoer.ApplyKnockback(Vector2, float)`; `AIActor.BehaviorOverridesVelocity` / `BehaviorVelocity`.
- **Decompiled source:** https://raw.githubusercontent.com/FlowSand/Re-ETG/master/Assets/_RawDump/C%23/Assembly-CSharp/<ClassName>.cs. For exact signatures, run `ikdasm` on the referenced DLLs under `PlutoTheCat/packages` or the project references. When the decompile and the referenced DLL disagree, **the DLL the project compiles against wins**.
- **Tests:** engine-free decisions go in a `*Rules.cs` file, tested by Mono-compiled cases through `run_cases` in `tools/tests/test_companion_kit.py`. `./build.sh` regenerates art, builds, validates, runs the unit tests and art lint, and packages `dist/`.

## Pieces that need work the concepts do not cover — plan these explicitly

- **Round 2, "Matching Cones"** (Cone of Shame + Coco Blue): Coco wears a little cone. This needs a cone clip set for Coco (idle, move, pet, block, ko) in the style of his existing `knight_` helmet clips, swapped in through `Prefix`. Decide how it combines with the knight helmet when Coco has both Junkan and the Cone: pick a precedence rule and put it in the plan.
- **Round 2, "Cone of Shame" ready glint:** a small VFX over Pluto's head. Reuse an existing VFX pool if one reads well; otherwise draw a small one.
- **Round 3, "Osaka Branch"** (Takoyaki Launcher + Yasupen): Yasupen wears a takoyaki costume. This needs Yasupen costume clips (idle, move, slide, pet, cheer). No concept exists, so write a brief and generate one with Gemini first (the pluto-artist skill; `gemini-3-pro-image` at 2K, 2 candidates, using Yasupen's sheet as the reference). Then copy it the same way as the other art.
- **Round 3, Daruma Doll "both eyes" state:** a second icon with both eyes painted, once the floor boss has died while Pluto holds it.
- **Round 3, Maneki-neko + Yasupen discounts:** Yasupen already applies `GlobalPriceMultiplier` via `YasupenRules.PriceMultiplier` (clamped to `MaxDiscount = 0.5`). Two multiplicative stat modifiers would give 0.9 × 0.9 = 0.81, which is not the spec's "stack to at most 25 %". Design the combined rule in a `*Rules.cs`: normal cap, and "Lucky Bargain" raising the cap to 25 % and doubling bargain casings. Test it, and make sure dropping either item restores the other's discount alone.

## Known 2.18.0 leftovers you may fold in (ask me first if they grow a task)

These are optional. The final review triaged them as not blocking, and they are **not** part of rounds 2 or 3 unless I say yes:
- **Yasupen belly-slide frame:** it sits 1 px low.
- **ヤ on his belly:** in seated poses it touches the beak and closes into a loop.
- **Cheer sign:** it merges with the cap.
- **Cap tag:** it reads pale, not neon.
- **Bargain casings:** they spawn at Yasupen and can land over a pit (`player.CenterPosition` is safer).

If you touch `YasupenItem.cs` for "Osaka Branch" or the discount cap anyway, you may fix the charmed-enemy skip and the casing position there.

## Hand-off details (only after I approve at the stop point)

- **Drop page:** https://claude.ai/artifact/HsDtVvvhZqJ9LgQrnjh9zJ (currently version 52: Pluto 2.18.0 + Vet Visit 0.14.4).
  - Read the live page and any payload JSON with `action: read_file` **before** republishing, or the publish is refused as unread.
  - Keep the Vet Visit card and `pluto_vet_visit_zip.json` untouched.
  - Replace the Pluto card and `pluto_the_cat_zip.json`.
  - After publishing, download both JSONs back and verify size, SHA-256 and the inner `manifest.json` version before telling anyone.
- **Steam machine:** the tester is a Remote Control session named `plutosm-*`. It was **offline** at the 2.18.0 hand-off. Check `ListAgents`; if no `plutosm-*` session is listed, say so and point me at the drop page instead of pretending it was sent. Checklist results for these rounds come to your session.
- **Memory:** update the project memory files `steam-machine-handoff.md` and `github-repos.md` with the new version, commit, drop-page version and checksums.

## Done means

For each round:
- all five pieces are in the loot pool and each has its synergy;
- the tests, lint and `validate.py` all pass;
- the full build succeeds and the package zip carries the right manifest version;
- the final review is clean after at most one fix wave;
- both READMEs and the changelog are updated;
- an in-game checklist (per piece: the spec's behaviour, its synergy, its art at 1x) is ready for the drop page;
- you have asked me the hand-off question.

Report honestly what was not built or verified, especially anything that can only be checked in game.
