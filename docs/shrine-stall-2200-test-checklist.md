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
- [ ] The log contains `shrine stall: registered at (10.5, 22.1, 0.0)` (or whatever `StallPosition` is set to).
  If instead it contains `shrine stall: SetUpFoyerShop returned null; see the [CharAPI]/Alexandria log lines
  above for the failed resource path`, the stall failed to build — copy the Alexandria/CharAPI lines immediately
  above it into the report; do not assume the stall is simply invisible.
- [ ] Daifuku, Kinsuke, the torii and the stall counter are all visible in the Breach. If any one of the four is
  missing, check for `shrine stall: missing prop resource ...` in the log (torii/stall/Kinsuke are placed by a
  separate code path, `PlaceBackdropProps`, that fails independently of Daifuku's own NPC and logs per-prop).

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

The FLAG prerequisite on each item is the primary lock; the per-run loot-table guard (`PlutoUnlockGate`,
re-applied on every `DungeonHooks.OnPostDungeonGeneration`) is a backstop whose ordering against the mod API's
own loot re-injection (`ItemDB.DungeonStart` writing into `Dungeon.baseChestContents`) could not be determined
without the game installed.
- [ ] With no items unlocked (fresh save), none of the ten gated items (Ball of Yarn, Catnip Pouch, Hairball,
  Scratching Post, Toilet Paper Roll, Coffee Mug, Jingle Bell Collar, Cone of Shame, Spray Bottle, Feather
  Teaser) appears in any chest, shop, or boss/floor reward across at least 3-4 floors of play.
- [ ] Unlock one item at the stall, then do a full run: that one item can now appear in loot, and the other nine
  still cannot.
- [ ] If a locked item ever turns up in loot, note which floor/source and whether it was the first floor after a
  fresh dungeon generation (that would point at the ordering-with-`ItemDB.DungeonStart` unknown above) versus a
  later floor in the same run (that would point at a different bug).

## 5. Per-save persistence

`PlutoUnlocks` mirrors the unlock into both an extended `GungeonFlags` value and a string key
(`GameStatsManager.ForceUnlock`/`IsForceUnlocked`), then calls `GameStatsManager.Save()`.
- [ ] Unlock an item, quit to the main menu (not just to the Breach), relaunch the game, and load the same save:
  the item is still unlocked (drops normally, stall no longer offers it).
- [ ] Start or switch to a **different** save slot: that slot's unlocks are independent — nothing purchased on
  the first slot is unlocked on the second.

## 6. Flag-id drift (the string mirror)

`GungeonFlags` values from `ETGModCompatibility.ExtendEnum` are assigned per-save based on registration order,
so installing or removing another mod that also extends `GungeonFlags` can shift the numeric ids. The string
mirror (`bogdan.etg.plutothecat:<item>`) exists specifically so unlocks survive that shift.
- [ ] Unlock at least one item. Install another mod that also extends `GungeonFlags` (any Alexandria/ETGMod mod
  that registers its own custom flags), relaunch, and confirm the previously unlocked item is still unlocked.
- [ ] Now remove that other mod and relaunch again: the item must still read as unlocked (this is the actual
  drift scenario — the flag's numeric id likely changed or was freed, and only the string mirror keeps the
  unlock correct). If it reverts to locked, the mirror is not being checked correctly.

## 7. Buying an item

- [ ] Buying an item at the stall: charges the correct number of Hegemony credits (8 for Ball of Yarn, Catnip
  Pouch, Hairball, Scratching Post, Toilet Paper Roll and Coffee Mug; 15 for Jingle Bell Collar, Cone of Shame,
  Spray Bottle and Feather Teaser — `Shrine Stall 2.20` config defaults), permanently unlocks that item for the
  save, and hands one copy of it to Pluto to carry into the current run immediately (not just an unlock with
  nothing handed over).
- [ ] The bought item disappears from the stall's mat on the same visit (it is now unlocked, so
  `encounterTrackable.PrerequisitesMet()` is true and the foyer shop no longer stocks it).
- [ ] After that purchase, the item drops normally from chests/shops/rewards in later runs, same as any of
  Pluto's other loot-pool pieces.
- [ ] Trying to buy with insufficient credits fails cleanly: no credits are deducted, no item is unlocked or
  handed over, and the "cannot afford" dialogue plays (see Dialogue below).

## 8. The mat: item count and prices

- [ ] The mat shows three items at a time (the foyer shop's normal display slot count), drawn from whichever of
  the ten are still locked; buying one causes another locked item to appear in its place if any remain.
- [ ] Prices on the mat read 8 or 15 credits, matching the tier a given item belongs to (listed above), not some
  other rounding of the config value.

## 9. Ammonomicon

- [ ] Each of the ten gated items shows as **undiscovered** in the Ammonomicon while locked (grey silhouette /
  "???"), because the FLAG prerequisite drives the same discovery gating vanilla items use.
- [ ] After buying an item at the stall, its Ammonomicon page flips to the full entry (picture, name, subtitle,
  story) without needing to encounter it again in a run.

## 10. `StallUnlocksDisabled` config toggle

- [ ] Set `StallUnlocksDisabled = true` under `[Shrine Stall 2.20]` in the BepInEx config and relaunch: all ten
  items behave as already unlocked (they drop normally, and the Ammonomicon shows them as discovered) even
  though nothing was purchased.
- [ ] The stall itself still stands in the Breach with Daifuku and Kinsuke — it becomes pure decoration (nothing
  to buy, or everything shows as already-owned/no-op), rather than disappearing or erroring.

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

## 12. Kinsuke is a static sprite

Kinsuke is placed as a single unanimated frame (`kinsuke_idle_001.png`), not the full four-frame idle clip — a
deliberate reduction because Alexandria's shop-animation helpers were confirmed (via IL) to attach a new clip to
Daifuku's own animator rather than create a second animated sprite.
- [ ] Confirm Kinsuke reads acceptably as a still bowl on the counter at 1x, rather than looking obviously broken
  or like a bug (e.g. a "frozen" character where motion is expected).

## 13. Art at 1x

- [ ] Torii, stall counter and Kinsuke's bowl all read clearly at 1x game resolution (no illegible blob, no
  stray artifacts from the sprite import).
- [ ] Daifuku's idle and talk animations play at the intended speed (6 fps idle, 8 fps talk) and don't look like
  they're skipping or stuttering.
