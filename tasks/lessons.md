# Lessons

## 2026-09-13 — Alexandria CharacterAPI altGuns
- Alexandria 0.5.10 `HandleLoadout` iterates `altGun` without a null check; the list only exists when characterdata.txt has an `<altGuns>` block. Always include it, even with no alt skin.
- `Loader.BuildCharacter` catches its own exceptions and returns null. Check the return value before logging success; never print "ready" unconditionally.
- Static validation caught none of this. Runtime API contracts (what a loader tolerates) need a real in-game run; keep the remote Steam-machine test loop as the final gate.

## 2026-09-13 — vanilla item ids
- Never guess a vanilla console id. Every id must be looked up in `docs/research/gungeon_items_idmap.txt` (Cardboard Box is `box`, the cheese is `partially_eaten_cheese`). `tools/validate.py` now enforces this for synergy ids.
- Optional features (synergies) register last and each in its own try/catch, so one bad id costs a synergy, not the character.

## 2026-09-13 — AI art vs hand-drawn sprites
- Gemini-generated sprites pixelized to 16-34 px lost to the hand-authored row-string art in a side-by-side; the user chose hand-drawn. Do not replace sprites with generated images; at most use generations as colour/shape references.
- Before spending API calls on sprite-sized art, show a comparison sheet (AI vs current) at 7x and let the user decide. Large painted pieces (boss card, win pic, icon) are a separate decision.
- "Better graphics" now means raising the craft of the hand-drawn pipeline (palette ramps, outlines, animation timing), not swapping the source of the art.

## 2026-09-14 — read the engine before drawing for it
- Enter the Gungeon adds the 1-px black outline to player and hand sprites at runtime; vanilla body frames have no outline. A baked outline gives a double outline in game. Check the renderer's decompiled code (outline, anchor, hand semantics) before an art pass, not after.
- `_bw` clips are the back-view side sprite (aiming up-diagonal), `_hand` means the body draws its free hand (one-handed gun), `_twohands` means no gun. Names in the Alexandria table are not self-explanatory; look them up in `PlayerController.GetBaseAnimationName`.
- Frames are anchored bottom-left: hops are drawn inside the canvas, so the canvas needs headroom (24x24, not 24x20).

## 2026-09-14 — art passes A-C
- A strict canvas (`pad`/`overlay` raising on dropped pixels) found five silent clipping bugs on the first run. Keep transforms strict for body art; give item/VFX art explicit lenient aliases instead of loosening the rule.
- Lint metrics must match the craft rule they encode: a "changed pixel %" flicker check flagged every legitimate hop; the rule is "a lone pixel toggling", so the check aligns frames and looks for a single-pixel difference.
- Previews must render what the game renders: without the simulated runtime outline the outline-free frames look wrong and judgement drifts.
- Verify engine claims from the decompiled source before shipping a change that depends on them: `PlayerController.Start` and `AIActor.Start` (with `procedurallyOutlined = true` by default) both add the runtime outline, which is why Pluto and Coco ship outline-free. The Re-ETG raw dump on GitHub answers such questions in one fetch.
- Release chains: a failing check (`strings -e` does not exist on macOS) short-circuited `cp`/drop-page steps while the later `git commit` still ran, and the artifact got republished with the old zip. Keep the archive + drop-page step in its own command and verify the published sha before announcing.

## 2026-09-14 — shared tooling drift (Vet Visit)
- A sibling project that imports the main mod's `tools/pixel.py` palette live re-rendered 36 committed PNGs when the main palette changed, and `validate.py` stayed green. Snapshot shared constants (palette values) into the consumer and add a test that fails loudly on drift; never import mutable art constants across projects.
- When two sessions work in one tree, keep every generated artifact's source of truth inside the project that ships it.

## 2026-09-14 — build status behind a pipe (Vet Visit 0.5.0)
- `./build.sh | grep ...` returned grep's status, so a compile error (CS0507) slipped past `&&` and the commit ran with a stale zip. Never chain a commit after a piped build; write the log to a file, check `$?` (or `set -o pipefail`) and only then archive and commit.
- `BraveBehaviour.OnDestroy` is `public virtual`; override it as `public override` and call `base.OnDestroy()`.

## 2026-09-14 — splayed run legs came back (2.13.0)
- The "short splayed stride, vanilla-like" legs (two outward diagonals on the contact frames) read as the splits at 1x, and the user had to flag it twice. The rule now lives in the skill's animation.md: run legs stay vertical under the hips, stride at most 1 px, never diagonal.
- "Similar to the other characters" means open the vanilla frames first (wiki.gg `File:Convict_Dodge*.gif`, four directions). Pluto had one clip for all four dodge directions and an anonymous ball; vanilla rolls keep head, limbs and back readable in every tumble frame.

## 2026-09-14 — Vet Visit 0.10.0 in-game test (user report: Pluto cannot shoot, enemies cannot shoot)
- A console shortcut is not the real route. `vet_visit` loads the past straight from the Breach and skips `Foyer.OnDepartedFoyer`, so `GameManager.IsFoyer` stays true (input reads `FoyerInputOnly`: no firing), `ForceNoGun` stays true and the gun object stays `SetActive(false)`. When a debug entry point exists, trace what the normal exit from the previous scene does and replay it; log the flag that gates the behaviour (`isFoyer`), not only its symptoms.
- Clearing a flag is not restoring state: `ForceNoGun = false` makes `CurrentGun` non-null again but leaves the object inactive. Check the object (`activeSelf`) after every repair, and log the value you repaired, not the value you set.
- Read the helper you wrap. Alexandria's `CopyBulletBankEntry` already makes a private inactive fake-prefab copy; cloning it again with `FakePrefab.Clone` let Alexandria's own Instantiate hook re-activate the clone, which lived in the world, died, and nulled every bank entry. The enemy NRE had the same stack since 0.3.0: a stack trace that survives several "fixes" means the fixes were aimed elsewhere; open the top frame (`AIBulletBank.CreateProjectileFromBank`) and list every dereference.
- Depth claims from reasoning alone need an in-game check: flat sprites lose to the tileset's standing wall face. Ask for screenshots early and compare them with the concept before adding more art.

## 2026-09-14 — CS0507 again (Wet Food Can 2.14.0)
- `PlayerItem.DoEffect` is `public virtual`, like `BraveBehaviour.OnDestroy` before it. Before overriding any EtG member, grep an existing override in this repo (or the decompiled source) for its access modifier instead of assuming `protected`.
- A new C# file that uses Alexandria helpers needs `using Alexandria.Misc;` (`ProjectileUtility`); copy the using block from the file whose pattern you are reusing.

## 2026-09-14 — committing while another session edits the same files
- A "did I stage someone else's paths?" check that only prints is not a guard. The other session added hunks between the check and `git add`, and the commit picked up its knight art and changelog section. Make the check abort (`grep ... && exit 1`) and run it on the staged index immediately before `git commit`, in the same command.
- In zsh a `$VAR` holding several paths is one word; use an array (`PATHS=(...)`, `"${PATHS[@]}"`).
- With another session live in the tree, agree on a file freeze ("tell me before you touch X") before committing, or commit only files the other session said it does not edit.

## 2026-09-14 — player boss card covered the boss (2.15.1 tester report)
- `BossCardUIController` draws `PrimaryPlayer.BosscardSprites` on its own sprite over the boss art, and Alexandria passes `bosscard_*.png` straight in. A player card must be a cut-out on transparency (known-good Kotonoha cards: 427x240, ~12 % opaque, figure in the bottom-left). Pluto's 100 % opaque panel hid the Vet. `validate.py` now fails any card above 30 % opaque.
- The "big painted card" assumption came from the file's size in a table, not from how the game draws it. For any UI texture, read the controller that renders it and compare against a working mod's file before designing the art.
- A generator that deletes old outputs before producing the new ones leaves the tree broken when it crashes (NameError left no boss card at all). Build the new files first, then remove stale ones.

## 2026-09-14 — Vet Visit 0.10.1 in-game test (user: "their bullets go through Pluto and no hit is registered")
- "No exception" is not "works". The bullets spawned, flew and made sound, yet every hitbox was 0x0. For anything that must collide, log the collider after it is built (generation mode, layer, manual size, `Dimensions`) and put the expected values in the tester checklist.
- A helper written for one kind of object can silently break another. Alexandria's `SetProjectileSpriteRight` is for player projectiles: it moves the sprite into ETGMod's ProjectileCollection. Vanilla enemy bullets build a BagelCollider from a frame named in their own collection, so the lookup failed and `RegenerateEmptyCollider` produced 0x0. When re-skinning an enemy bullet, set a Manual (or Circle) collider sized to the new sprite.
- `Duplicate prefab name` from SpawnPool means several copies share a GameObject name. It is harmless for spawning, since pools match by reference, but give every copy a unique name so the log stays clean.

## 2026-09-14 — Playdate did nothing in game (user report, 2.15.0-2.15.1)
- A companion's `AIActor.ParentRoom` is always null: `CompanionItem.CreateCompanion` instantiates the prefab without `ConfigureOnPlacement`, the only place (besides mimics) that sets it. `CocoFriends.FindChaser` returned null on its first line, so the Dog and Squire's Junkan never moved, and no static check could see it. Look a companion's room up from the owner (`CurrentRoom`) or its position (`GetAbsoluteRoom`), like vanilla `TargetEnemiesBehavior`; Coco's own decoy only worked because `CocoBlueController.CurrentRoom()` already did.
- Every engine field a new feature reads needs the same decompiled-source check as the calls it makes: I verified `OverrideTarget`, `CurrentForm` and petting, but not `ParentRoom`. Add a log line at each step of a chain that can only be tested in game (synergy active, companion found, target found), so the first tester log shows where it stops.

## Boss card text (Vet Visit 0.11.1 test, 2026-09-14)
- BossCardUIController sets nameLabel.Text straight from the enemies string table, and its title font lacks some lowercase glyphs: "The Vet" rendered "Te Vet". Write boss card name and subtitle strings in capitals, like vanilla ("THE EVIL EYE!", "BEHOLSTER").
- Boss card art must bleed off the card edges; a portrait that ends in a straight line mid-card reads as a pasted rectangle.
- When a boss sprite grows, re-check its spawn cell against surrounding props: the 48x40 Vet spawned behind the exam table and under the lamp.

## 2026-09-14 — boss-card bust: generated first, then pixel-perfect (user correction)
- A procedural "hand-drawn" bust (ellipses, auto outline, cel bands at 2x) was rejected: "does not look good". For large art next to vanilla painted cards, start from a Gemini generation that matches the reference style, copy it as faithfully as possible, then make it pixel-perfect (palette, outline, no anti-aliasing, integer scale).
- Never show a stand-in draft for art the user judges by look alone; run the artist skill's review rubric first and show only what passes.

## 2026-09-14 — shared index sweeps (2.16.0)
- Twice today a plain `git commit` in the shared tree recorded another session's staged files: f1's knight art in my
  490fb03, and my 342 staged task 6-8 files in the Vet Visit session's ebdebfc (my own commit had just failed on
  `.git/index.lock`, leaving the paths staged). A path guard on `git diff --cached` doesn't protect the other sessions.
- Rule: commit in one step with explicit paths, `git commit -m ... -- <paths>` (it commits only those paths, whatever
  else is staged), and never leave files staged between commands. If a commit fails, `git restore --staged <paths>`
  before doing anything else.

## Shared git index (2026-09-14, commit ebdebfc)
- Two sessions share the parent repo's index. A plain `git add X && git commit` records everything the other session has staged too: ebdebfc (a one-line spec edit) carried 342 files of the character session's 2.16.0 work.
- Rule: in the parent repo, commit only with explicit paths in one step, `git commit -m "..." -- <paths>`, and never leave files staged between commands. Check `git show --stat` after committing.

## Hero sword swing is the gun's fire animation (2.16.1, user: "the katana does not have a swing animation like blasphemy")
- `IsHeroSword` only runs the slash logic and plays `shootAnimation` (Gun.cs HandleShootAnimation); nothing rotates the sword. The visible swing must be drawn: the blade sweeps around the grip over many frames (Blasphemy, Planetside's Crystalline).
- A still blade plus a crescent reads as "no swing". Review a weapon's fire clip as motion (APNG at the real fps), not as a strip of stills.
- Swing frames need a taller canvas; shift their sprite definitions in code (position0..3) so the grip pixel lands on the idle grip, and keep the jtk2d hand at the idle position.

## Playdate still did nothing visible (2.16.1 user report: "the dog does not attack, it should attack like the wolf does")
- Vanilla Dog (item 300, enemy Dog c07ef60a...) has no attack behaviours; the attacking "Wolf" is a separate companion prefab (Dog_Past ededff1d..., item 492) with SeekTargetBehavior + WolfCompanionAttackBehavior. A scripted ApplyDamage next to an idle-looking Dog reads as "no attack" even when it lands.
- When the user names a vanilla behaviour to copy ("like the wolf"), reuse that behaviour class with its prefab values instead of scripting a look-alike; add it to the speculator lists, call RefreshBehaviors(), and on removal Interrupt() first and reset BehaviorOverridesVelocity, LockFacingDirection, PathableTiles and OverrideTarget.

## Narrowing an automatic repair (combat polish, 2026-09-15 review finding)
- The Vet Visit loadout watchdog was narrowed to respect foreign input/gun/render locks, but the broad repair became console-only (`vet_loadout`). That silently removed the automatic fix for the 0.10.0 in-game "Pluto cannot fire" bug; tests passed because they only checked the narrowing.
- Rule: when making a recovery path less aggressive, keep an escalation path (persistent + unexplained state for N checks -> the broad repair, logged), and add a test that the escalation is still wired. A fix verified in game must not become manual-only without the user's say.

## 2.16.3 / 0.14.3 in-game report (2026-09-15, user)
- "Coco no longer runs in the room when the active is triggered": the scored-dodge rewrite let "stay" win whenever no bullet threatened him, so the decoy stood still. A behaviour a player can see (a panicky run) is part of the feature, not an implementation detail: when replacing movement logic, keep a test that the idle/no-threat case still moves, and list the visible behaviour in the in-game checklist.
- "The Vet remains stuck a lot" after adding fairness gates (budget, recovery, repeat avoidance, distance bands): gates that remove attacks must never also remove movement. Simulate several seconds of selection with long-lived hazards before shipping.
- Confirmed working: Playdate Dog bites enemies (2.16.2 Wolf behaviours).

## Samurai Puffed Up had no fur (user, 2026-09-15: "pluto is no longer fluffy when getting damaged in the samurai skin, it only gets bigger")
- a7dfe7d picked "turn the fur off for the costume" out of the spec's two options (mask where the kimono covers, or turn off) and swapped in a red tint cue. The user reads the fur as the item itself, so removing it for a costume was a regression, not a style choice.
- When a costume or skin conflicts with an existing visual effect, keep the effect and adapt it to the costume (here: grow fur only from fur-coloured edges), or ask the user before dropping it.
- "Gets bigger" comes only from `Balance/AngryScale` != 1 in the tester's cfg (the default has been 1.0 since 2.4.1), so a size change the defaults cannot produce points at a stale config value.
