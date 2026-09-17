# 2.20.0 shrine stall: in-game checklist

Test build `Pluto_The_Cat-2.20.0.zip` from `main`. Nothing below has been run in game yet: the build Mac has no
game, so every line is still open. Daifuku (ginger cat) and Kinsuke (koi in a bowl) run the Shrine Stall in the
Breach, beside the Breach shop, selling permanent per-save unlocks for ten cat items in Hegemony credits (config
section `Shrine Stall 2.20`). Until unlocked, those ten no longer drop anywhere. Ordered riskiest first, because
several of the failure modes below are silent by design.

## 1. Does the stall exist at all?

`ShopAPI.SetUpFoyerShop` (Alexandria) wraps its entire body in a try/catch that only logs and returns `null` — a
mistyped resource path or bad argument produces **no stall and no exception**, just a quiet gap in the Breach.
`ShrineStall.Init` checks for that null and logs one of two lines; read the BepInEx log first, before looking at
anything else:
- [ ] The log contains `shrine stall: registered at (19.7, 22.1, 0.0)` (or whatever `StallPosition` is set to).
  If instead it contains `shrine stall: SetUpFoyerShop returned null; see the [CharAPI]/Alexandria log lines
  above for the failed resource path`, the stall failed to build — copy the Alexandria/CharAPI lines immediately
  above it into the report; do not assume the stall is simply invisible.
- [ ] **If the stall (or any part of it) is off screen**, do not just report it — place it yourself with the
  `pluto_stall` console command (2.20.1) and report the value it logs: walk to a spot where the whole assembly
  (Daifuku, Kinsuke, the torii and the counter) would read well, then type `pluto_stall here`. Check the
  BepInEx log for the `shrine stall: moved to ...` line and the footprint line right after it, and paste both
  into the report. `pluto_stall save` then writes that position into the config so the next test build keeps it
  without you having to redo this.
- [ ] Daifuku, Kinsuke, the torii and the stall counter are all visible in the Breach. If any one of the four is
  missing, check for `shrine stall: missing prop resource ...` in the log (torii/stall/Kinsuke are placed by a
  separate code path, `PlaceBackdropProps`, that fails independently of Daifuku's own NPC and logs per-prop).
- [ ] **The props survive leaving and coming back.** They are unparented `GameObject`s with no
  `DontDestroyOnLoad`, so Unity destroys them when the Breach unloads; they are re-placed on every
  `DungeonHooks.OnFoyerAwake`. Alexandria re-places Daifuku itself, so if the re-placement is broken the symptom
  is Daifuku standing alone in mid-air with no torii, counter or Kinsuke. Check all four are still there:
  - [ ] after finishing or abandoning a run and returning to the Breach;
  - [ ] after **dying** and returning to the Breach;
  - [ ] after several Breach → run → Breach cycles in one session — and confirm there is exactly one of each
    prop, not a stack of duplicates piling up at the same spot (each foyer load destroys the previous set first).

## 2. Draw order (torii, stall counter, Kinsuke's bowl)

None of the three backdrop props sets an explicit sorting layer or order, and all three sit at the same Z depth.
- [ ] Kinsuke's bowl renders **on top of** the stall counter it is supposed to sit on, not behind it.
- [ ] The torii does not draw over the stall counter or Daifuku in a way that looks wrong (it is meant to frame
  the stall from behind/above).
- [ ] If any prop draws in the wrong order, note which one is behind which — the fix is an explicit
  `SpriteRenderer.sortingOrder` on the three `PlaceProp` calls in `ShrineStall.PlaceBackdropProps`, not a
  position change.

## 3. Placement: offsets and the Breach shop door

The torii offset, the stall offset, Kinsuke's offset (all in `ShrineStall.cs`) and `talkPointOffset` (currently
`Vector3.zero` in the `SetUpFoyerShop` call) are all unverified guesses, picked from a pixel-math comment with no
in-game confirmation.
- [ ] The whole stall (torii + counter + Kinsuke + Daifuku) sits beside the Breach shop without overlapping the
  shop door or blocking its interaction prompt. Walk up to the Breach shop door from a few angles and confirm the
  prompt still appears normally.
- [ ] The torii and stall counter look anchored together (stall roughly in front of/under the torii), not
  floating apart or overlapping oddly.
- [ ] Kinsuke's bowl looks like it is resting on the counter surface, not floating above it, sunk into it, or off
  to the side.
- [ ] Talking to Daifuku (interact key) opens the dialogue from a natural distance/angle — `talkPointOffset` is
  zero, so if the talk prompt triggers from an awkward spot (e.g. behind the counter, or through a wall), that is
  the value to tune.
- [ ] Daifuku's hitbox (`IntVector2(20, 18)` size, `IntVector2(5, 0)` offset) is reachable from the front of the
  stall without having to stand somewhere unnatural.

## 4. Loot gating actually works

The FLAG prerequisite on each item is the primary lock. The per-run loot-table guard (`PlutoUnlockGate`,
re-applied on every `DungeonHooks.OnPostDungeonGeneration`) is the backstop, and it now sweeps all three
collections that matter, not just the two `LootUtility.RemovePickupFromLootTables` touches:
`RewardManager.GunsLootTable`/`.ItemsLootTable`, `ETGMod.Databases.Items.ModLootPerFloor` (so the next
`Dungeon.Start` cannot re-inject a locked item) and the current run's
`Dungeon.baseChestContents.defaultItemDrops.elements` (because `ItemDB.DungeonStart` is a Harmony *prefix* on
`Dungeon.Start` and has already filled it by the time this hook runs). The ordering is no longer an unknown —
it was read from the ModTheGungeonAPI IL — but nothing here has been seen running, and the *re-add* side (an
unlocked item being put back into `ModLootPerFloor["ANY"]` and the live chest table at weight 1) is the part
most likely to be wrong in practice.
- [ ] With no items unlocked (fresh save), none of the ten gated items (Ball of Yarn, Catnip Pouch, Hairball,
  Scratching Post, Toilet Paper Roll, Coffee Mug, Jingle Bell Collar, Cone of Shame, Spray Bottle, Feather
  Teaser) appears in any chest, shop, or boss/floor reward across at least 3-4 floors of play.
- [ ] Unlock one item at the stall, then do a full run: that one item can now appear in loot, and the other nine
  still cannot.
- [ ] If a locked item ever turns up in loot, note which floor/source and whether it was the first floor of a run
  or a later one — a first-floor-only leak points at the guard running too late for that floor, a later-floor leak
  points at the `ModLootPerFloor` sweep not sticking.
- [ ] The opposite failure, and the newly risky one: an **unlocked** item must still appear in chests. After
  unlocking one item, play 3-4 floors and confirm it can actually drop — if unlocked items stop dropping
  entirely, the guard is removing them from `baseChestContents` without the re-add landing.

## 5. Per-save persistence

`PlutoUnlocks` mirrors the unlock into both an extended `GungeonFlags` value and a string key
(`GameStatsManager.ForceUnlock`/`IsForceUnlocked`), then calls `GameStatsManager.Save()`.
- [ ] Unlock an item, quit to the main menu (not just to the Breach), relaunch the game, and load the same save:
  the item is still unlocked (drops normally, stall no longer offers it).
- [ ] Start or switch to a **different** save slot: that slot's unlocks are independent — nothing purchased on
  the first slot is unlocked on the second.
- [ ] **Co-op.** Start a two-player game, have **player 2** buy an item at the stall, then finish or abandon the
  run and come back to the Breach. The unlock is stored per *save*, not per player
  (`GameStatsManager.SetFlag`/`ForceUnlock`), so it should be unlocked for both — the item should be gone from
  the mat and should drop for either player. Note specifically whether the purchase registered at all when the
  buyer was not player 1, and whether the mat updated for the host.

## 6. Flag-id drift (the string mirror)

`GungeonFlags` values from `ETGModCompatibility.ExtendEnum` are assigned per-save based on registration order,
so installing or removing another mod that also extends `GungeonFlags` can shift the numeric ids. The string
mirror (`bogdan.etg.plutothecat:<item>`, written by `PlutoUnlocks.Unlock` via `GameStatsManager.ForceUnlock`)
exists specifically so unlocks survive that shift.

How the mirror actually gets written changed in the final fix round, and this is the single most important thing
to confirm in game. Reading the Alexandria 0.5.10 IL showed that `CustomShopController.DoSetup`'s foyer
meta-shop (blueprint) branch **never assigns the `OnPurchase` delegate at all** — those five callbacks are wired
only in its non-blueprint branch — so `ShrineStall.OnPurchase` is expected never to fire here, and its log line
is expected to be **absent**. What is expected to happen instead: the blueprint clone carries the item's
`SaveFlagToSetOnAcquisition`, the game's own pickup path sets the `GungeonFlags` value, and
`PlutoUnlocks.Reconcile()` (run from `PlutoUnlockGate` on load and on every dungeon start) writes the string
mirror from that flag. Neither half has been seen running.
- [ ] **First, confirm the unlock is recorded at all.** Buy an item, then leave the Breach and start a run (that
  is when `Reconcile` next runs) and look in the log for
  `unlocks: flag said unlocked but the mirror did not, mirror written for <id>`. That line appearing is the
  expected, working path.
- [ ] If instead `shrine stall: purchased and unlocked <id> (matched by save flag)` appears, Alexandria *did*
  invoke the callback — also fine, and better (the mirror is written immediately). Note which of the two you saw.
- [ ] If **neither** line ever appears, the unlock is being kept only as a `GungeonFlags` value with no mirror:
  the item will work now but will be lost the first time another flag-extending mod shifts the ids. Everything
  below in this section is meaningless until one of the two lines shows up.
- [ ] Unlock at least one item. Install another mod that also extends `GungeonFlags` (any Alexandria/ETGMod mod
  that registers its own custom flags), relaunch, and confirm the previously unlocked item is still unlocked.
- [ ] Now remove that other mod and relaunch again: the item must still read as unlocked (this is the actual
  drift scenario — the flag's numeric id likely changed or was freed, and only the string mirror keeps the
  unlock correct). If it reverts to locked, the mirror is not being written or not being checked correctly.

## 7. Buying an item

A purchase **unlocks only**. Alexandria's `LootEngine.GivePrefabToPlayer` is handed
`CustomShopItemController.item`, which in the foyer meta-shop path is the shared *blueprint clone*, not the cat
item — so nothing hands a real copy of the item to Pluto, by design. The docs were corrected to match.
- [ ] Buying an item at the stall charges the correct number of Hegemony credits (8 for Ball of Yarn, Catnip
  Pouch, Hairball, Scratching Post, Toilet Paper Roll and Coffee Mug; 15 for Jingle Bell Collar, Cone of Shame,
  Spray Bottle and Feather Teaser — `Shrine Stall 2.20` config defaults) and permanently unlocks that item.
- [ ] **BLOCKING — what you actually receive.** Watch the moment of purchase carefully and write down exactly
  what, if anything, lands in Pluto's hands or on the floor. Expected: nothing usable — either no pickup at all,
  or a blueprint-looking object. If a blueprint item ends up in Pluto's inventory, or a pickup appears that
  cannot be picked up / looks broken / persists in the Breach, that is a real bug to report even though the
  unlock itself worked.
- [ ] The bought item disappears from the stall's mat on the same visit (it is now unlocked, so
  `encounterTrackable.PrerequisitesMet()` is true and the foyer shop no longer stocks it).
- [ ] After that purchase, the item drops normally from chests/shops/rewards in later runs, same as any of
  Pluto's other loot-pool pieces. This is the only way the player gets the item — confirm it works.
- [ ] Trying to buy with insufficient credits fails cleanly: no credits are deducted, nothing is unlocked, and
  the "cannot afford" dialogue plays (see Dialogue below).

## 8. The mat: fixed order, fixed count, prices

The stock is **deterministic and never re-rolled**. `SetUpFoyerShop` leaves `FoyerMetaShopForcedTiers` false, so
`DoSetup` fills each of the three slots by scanning the shop's loot table from the top and taking the first
entry not already stocked whose `PrerequisitesMet()` is false. The mat is therefore always the first three
still-locked items in `PlutoUnlocks.Ids` order (Ball of Yarn, Catnip Pouch, Hairball, then Scratching Post,
Toilet Paper Roll, Coffee Mug, Jingle Bell Collar, Cone of Shame, Spray Bottle, Feather Teaser).
- [ ] On a fresh save the mat shows exactly Ball of Yarn, Catnip Pouch and Hairball.
- [ ] Leaving the Breach and coming back shows **the same three**, in the same spots — no re-roll.
- [ ] Buying one of them leaves the other two where they were, and the next locked item in that order (Scratching
  Post) moves up into the free spot.
- [ ] With only one or two items still locked, the leftover spots are simply **empty** — no placeholder, no
  error, no exception in the log.
- [ ] With all ten unlocked the mat is three empty spots, Daifuku and Kinsuke are still there and still talk, and
  nothing throws. (Easiest way to reach this state: `StallUnlocksDisabled = true`, see §10.)
- [ ] Prices on the mat read 8 or 15 credits, matching the tier a given item belongs to (listed above), not some
  other rounding of the config value.

## 9. Ammonomicon

- [ ] Each of the ten gated items shows as **undiscovered** in the Ammonomicon while locked (grey silhouette /
  "???"), because the FLAG prerequisite drives the same discovery gating vanilla items use.
- [ ] After buying an item at the stall, its Ammonomicon page flips to the full entry (picture, name, subtitle,
  story) without needing to encounter it again in a run.

## 10. `StallUnlocksDisabled` config toggle

The toggle used to be consulted only by the loot-table guard, which meant items came back into the loot tables
while still carrying an unmet FLAG prerequisite — so the stall still stocked all ten, prereq-respecting
selectors still skipped them and the Ammonomicon still showed `???`. `PlutoUnlockGate.Apply()` now clears the
prerequisites outright when the toggle is set. All four checks below have to pass, not just the drop one.
- [ ] Set `StallUnlocksDisabled = true` under `[Shrine Stall 2.20]` in the BepInEx config and relaunch: all ten
  items drop normally in runs even though nothing was purchased.
- [ ] **The stall's mat is empty** — three empty spots, nothing on offer, because every item now counts as
  unlocked. If the stall still stocks items under the toggle, the prerequisites are not being cleared.
- [ ] **The Ammonomicon shows all ten as discovered** (full entries, not `???`), again without buying anything.
- [ ] The stall itself still stands in the Breach with Daifuku and Kinsuke — pure decoration, rather than
  disappearing or erroring.
- [ ] Set the toggle back to `false` and relaunch: items that were never actually bought go back to locked
  (the toggle must not have written real unlocks into the save — `PlutoUnlocks.Reconcile` deliberately reads the
  raw flag and mirror, not `IsUnlocked`, precisely so this cannot happen). Anything genuinely bought stays
  unlocked.

## 11. Dialogue

`ShrineStallLines` registers five keys: intro (first meeting), a 25-line generic pool (one exchange per visit,
walked in order, wrapping to a stopper line once exhausted), the stopper, a purchase line and a "can't afford"
line. Every exchange is `"Daifuku: ...\nKinsuke: ..."` — one literal `\n` between the two speakers.
- [ ] The intro plays on first talking to Daifuku each run/session, distinct from the generic pool.
- [ ] Generic exchanges play in sequence across repeated conversations, not randomly, and repeating on a later
  run starts back at the top of the pool.
- [ ] **Whether the `\n` renders as two separate dialogue-box speaker lines (Daifuku, then Kinsuke) or runs the
  two speakers together as one line is unverified and must be checked directly** — this affects all 25
  exchanges plus the intro, stopper, purchase and failed-purchase lines.
- [ ] After all 25 generic exchanges have been seen once, the stopper line plays instead of repeating or erroring.
- [ ] The purchase line plays on a successful buy; the "not quite enough" line plays on a failed buy for
  insufficient credits.
- [ ] Check the five longest exchanges specifically for clipping against the dialogue box (up to 155 characters
  including both speaker prefixes, per the doc comment in `ShrineStallLines.cs`): the koi-keeps-the-accounts
  exchange ("A customer once asked why a koi keeps the accounts..."), the intro line, the fresh-water exchange
  ("Do not ask him about the water..."), the whole-Breach exchange ("He claims he can see the whole Breach..."),
  and the lending-library ("Everything on this mat belonged to Pluto first...") and not-quite-enough
  (purchase-failed) lines.

## 12. Kinsuke's bob

Kinsuke now cycles all four `kinsuke_idle_*` frames at 4 fps, driven by `ShrineStall.PropFlipbook`, a small
component on his own prop GameObject that advances the `SpriteRenderer` on `BraveTime.DeltaTime`. (Alexandria's
shop-animation helpers are still unusable for him: both were confirmed via IL to attach a clip to Daifuku's own
animator rather than create a second sprite.)
- [ ] Kinsuke visibly bobs in his bowl, and the loop reads as a loop — not a stutter, not a single frame stuck,
  not a visible jump between the last frame and the first.
- [ ] 4 fps looks right beside Daifuku's 6 fps idle (the koi should read calmer than the cat). If it looks too
  slow or too fast, `KinsukeFps` in `ShrineStall.cs` is the one number to change.
- [ ] Pausing the game stops the bob (it is on `BraveTime.DeltaTime`, so it follows the game's own time scale).

## 13. Art at 1x

- [ ] Torii, stall counter and Kinsuke's bowl all read clearly at 1x game resolution (no illegible blob, no
  stray artifacts from the sprite import).
- [ ] Daifuku's idle and talk animations play at the intended speed (6 fps idle, 8 fps talk) and don't look like
  they're skipping or stuttering.
