# Shrine Stall: Daifuku and Kinsuke (2.20.0)

A Breach shop where a cat and a koi sell permanent unlocks for the ten cat items,
told through a setup-and-punchline double act under a red torii gate.

Approved by the user on 2026-09-17. API claims below are verified against
Alexandria 0.5.10 and ModTheGungeonAPI 1.9.2 IL unless marked unverified.

## Goal

Give the cat items a collection arc. The ten items from 2.17.0 and 2.19.0 no longer
drop until bought from the stall, so each run's credits buy a piece of Pluto's world,
and every visit is worth a joke.

## Cast

**Daifuku** — a large, unbothered ginger cat in a haori, the shopkeeper. Deadpan, slow,
treats selling as a mild inconvenience. Sets up every joke.

**Kinsuke** — a koi in a water bowl on the counter. Thinks he is the funny one. Delivers
the punchlines, splashes for emphasis, never acknowledges being a fish.

## The stall

A red torii gate beside the walkway that leads to the Breach shop door, positioned so it
never covers the door or its interaction prompt. Under the gate: a counter with a noren
curtain, paper lanterns, a maneki-neko, a stone lantern, koi banners, and the mat where
three items sit. Daifuku stands behind the counter, Kinsuke's bowl rests on it.

Art is drawn with the pluto-artist and pluto-pixel-art skills, Gemini concept first, then
copied faithfully into pixel art on the mod's fixed palette.

## What is gated

Ten items, all currently loot-pool items:

| From | Items |
|---|---|
| 2.17.0 | Ball of Yarn, Catnip Pouch, Jingle Bell Collar, Hairball, Scratching Post |
| 2.19.0 | Spray Bottle, Feather Teaser, Toilet Paper Roll, Cone of Shame, Coffee Mug |

Untouched: Pluto's starting Kibble Sack and Wet Food Can, the Katana, Taiyaki Cannon,
Coco Blue and Yasupen. Pluto is fully playable from the first run with no unlocks.

Locked items do not drop anywhere in the Gungeon. Unlocks live in the save slot, so a new
save starts the collection again.

## How it works

Alexandria's foyer meta-shop already implements the core loop. `ShopAPI.SetUpFoyerShop` sets
`BaseShopController.baseShopType = 6` and builds a single `ExampleBlueprintPrefab`; it leaves
`FoyerMetaShopForcedTiers` at its default `false` (only `SetUpShop` touches that field, and it
also sets it `false`). With `currencyType == META_CURRENCY` and a blueprint present,
`CustomShopController.DoSetup` then:

- stocks **only** items whose `encounterTrackable.PrerequisitesMet()` is false, so unlocked
  items leave the stall on their own;
- prices each item at its `WeightedGameObject.weight` in the shop's own loot table, written
  to `PickupObject.CustomCost` with `UsesCustomCost = true`;
- at *setup* time (not on purchase) instantiates the shared blueprint prefab per slot, copies
  the real item's journal fields onto the clone, and copies the real item's `FLAG`
  prerequisite's `saveFlagToCheck` into the clone's `SaveFlagToSetOnAcquisition` — so it is the
  blueprint clone the player picks up, and the game's own pickup path is what sets the unlock
  flag.

Two consequences of that blueprint branch, both read from the Alexandria 0.5.10 IL and both
worked around rather than fixed here (they are Alexandria's code):

- the branch never assigns `customCanBuy`, `removeCurrency`, `customPrice`, `OnPurchase` or
  `OnSteal` on the `CustomShopItemController` — those five are wired only in the
  *non*-blueprint branch. So the mod's own `OnPurchase` callback is never invoked for this
  shop. `META_CURRENCY` is charged natively, so the other four nulls are inert.
- `PlutoUnlocks.Reconcile()` therefore carries the unlock the rest of the way: it runs on
  every dungeon start and reads the flag the game set, writing the stable string mirror from
  it (and, in the drift case, the flag from the mirror).

So the design is: give each of the ten items a FLAG prerequisite, build a shop loot table
whose weights are the credit prices, and let Alexandria do the rest.

### Unlock flags

One flag per item, registered through
`ETGModCompatibility.ExtendEnum<GungeonFlags>(Plugin.GUID, "PLUTO_UNLOCK_<ITEM>")`, read and
written with `GameStatsManager.Instance.GetFlag/SetFlag` and flushed with
`GameStatsManager.Save()`. ModTheGungeonAPI persists extended enum values per save slot by
patching `GameStatsManager.Save/Load` into `Slot{N}.enumCache`, and patches
`fsEnumConverter.TryDeserialize` so unknown names never break a load.

`ExtendEnum` assigns `max + 1` at registration, so ids depend on which mods load. To survive
another flag-extending mod being installed or removed, each purchase is mirrored into
`GameStatsManager.ForceUnlock("bogdan.etg.plutothecat:<item>")`, which is string-keyed and
per-slot, and the mirror is treated as the authority when the two disagree.

Not used: `Alexandria.Misc.EnumUtility.GetEnumValue` (its `START_INDEX = 1000` collides with
real flags and its store is never loaded), and SpecialAPI's SaveAPI (a separate, old,
third-party dependency).

### Gating the loot

Each of the ten gets `encounterTrackable.prerequisites` set to a single
`DungeonPrerequisite { prerequisiteType = FLAG, saveFlagToCheck = <flag>, requireFlag = true }`.

`DungeonPrerequisite.CheckConditionsFulfilled` is **not** virtual and has no subclass anywhere,
so custom prerequisite logic is impossible without a Harmony patch; the plain FLAG form is
what the engine and Alexandria both understand.

Because only the `…FullPrereqs` loot selectors consult prerequisites, and chest selection
could not be read from the stubbed reference assembly, a second guard runs on every dungeon
start. It has to sweep three collections, not one:

- `RewardManager.GunsLootTable` / `.ItemsLootTable`, via
  `LootUtility.RemovePickupFromLootTables` — whose entire body touches only those two;
- `ETGMod.Databases.Items.ModLootPerFloor`, because `ItemDB.AddSpecific` puts the same
  `WeightedGameObject` there as well as in the RewardManager tables;
- the current run's `Dungeon.baseChestContents.defaultItemDrops.elements`, because
  `ItemDB.DungeonStart` — a Harmony **prefix** on `Dungeonator.Dungeon.Start` — has already
  `AddRange`d `ModLootPerFloor` into it by the time `OnPostDungeonGeneration` fires.

Sweeping only the first pair (as the first implementation did) would leave the backstop
touching none of the collection that actually feeds chests.

### Prices

Fixed per item, by quality, all config-bound in a `Shrine Stall 2.20` section, within 5..20
credits. Prices are integers because the shop rounds the weight.

| Quality | Items | Price |
|---|---|---|
| C | Ball of Yarn, Catnip Pouch, Hairball, Scratching Post, Toilet Paper Roll, Coffee Mug | 8 |
| B | Jingle Bell Collar, Cone of Shame, Spray Bottle, Feather Teaser | 15 |

Payment uses `ShopCurrencyType.META_CURRENCY`, which is Hegemony credits: Alexandria checks
`GameStatsManager.GetPlayerStatValue(TrackedStats.META_CURRENCY)` and charges by setting the
stat and registering `META_CURRENCY_SPENT_AT_META_SHOP`.

### Buying unlocks the item — it does not hand a copy over

An earlier draft of this section said a purchase also drops a copy into Pluto's hands. It does
not. Alexandria calls `LootEngine.GivePrefabToPlayer(this.item.gameObject, player)`, and in the
foyer meta-shop path `this.item` is the **blueprint clone**, not the cat item — so what the
player picks up is the blueprint. The purchase's real effect is the permanent unlock: the
clone's `SaveFlagToSetOnAcquisition` sets the item's unlock flag, the item leaves the stall,
and from then on it drops normally in the Gungeon like any other loot-pool piece.

Handing over a real copy as well would mean instantiating the item ourselves after the fact;
decided against (2026-09-17, user) — the unlock is the product.

### Three slots

`itemPositions.Length` sets the number of slots; the default three positions are used, which
is exactly the three-on-the-mat display.

The stock is **deterministic, and is not re-rolled**. Because `SetUpFoyerShop` leaves
`FoyerMetaShopForcedTiers` false, `DoSetup` fills each of the three slots by scanning the
shop's compiled loot table from the top and taking the first entry that is not already stocked
and whose `PrerequisitesMet()` is false. So the mat always shows the first three still-locked
items in `PlutoUnlocks.Ids` order, on every Breach visit, with no randomness.

Consequences, all accepted (2026-09-17, user):

- buying an item does not shuffle the mat; the next still-locked item in table order simply
  moves up into the free slot;
- when fewer than three items remain locked, the leftover slots are filled with `null` (a
  price of `1` is pushed alongside, and the controller loop skips null slots) — they render as
  **empty spots on the mat**, not as an error;
- with all ten unlocked the mat is three empty spots and the stall still stands and still
  talks. Nothing logs and nothing throws.

## Dialogue

Five string keys registered with `ETGMod.Databases.Strings.Core.Set`, injected by Alexandria
into a copy of the vanilla trucker dialogue machine:

| Key | When | Content |
|---|---|---|
| intro | first meeting per run | who they are |
| generic multiline | walking up | the joke pool: Daifuku sets up, Kinsuke lands it |
| stopper | pool exhausted | a line about running out of material |
| purchase | buying | Kinsuke takes credit for the sale |
| purchase failed | not enough credits | a joke at the player's expense, never mean |

Jokes are cat and fish humour in the mod's warm domestic voice, where Bogdan and Bianca are
Pluto's owners. Never crude. Roughly 20 exchanges at launch.

Voice box: `ShopAPI.VoiceBoxes.BELLO`, the least human-sounding of the 34 options, so the
pair do not read as people. `ChangeVoiceBox` can swap it later if it sounds wrong in game.

## Ammonomicon

Locked items render as the standard undiscovered entry through
`AmmonomiconPokedexEntry`'s `questionMarkSprite`, driven by the same prerequisites. To let
that work: keep `journalData.SuppressInAmmonomicon = false` and leave `ForceEncounterState`
and `SuppressKnownState` alone, since either pins the state and stops the flip.
2.1.9.1 has no `UnlockText` on `JournalEntry`, so there is no custom "how to unlock" line;
the entry simply becomes the item's normal page, art and lore included, once bought.

Daifuku and Kinsuke get their own Ammonomicon-style lore in the README and changelog rather
than a journal entry, since NPCs have no journal page.

## Configuration

A `Shrine Stall 2.20` config section, every key clamped through `PlutoConfigRules.Clamp` with
a `Ranges` entry and a default case, matching the existing config discipline:

- one price key per item (range 1..99)
- the stall's Breach position (so it can be nudged without a rebuild)
- a switch to disable the gating entirely, which unlocks all ten and leaves the stall as
  decoration, for players who dislike unlock grinds

## Testing

Engine-free rules get pure functions in a `ShrineStallRules` class with Mono cases: price
lookup by item id, the locked/unlocked decision, flag-name construction, and the
flag-versus-mirror disagreement rule. Wiring is asserted by a `test_shrine_stall` unittest in
the existing style: the ten prerequisites, flag registration, the config section, the shop
registration and its step order, the string keys, and every art resource path.

Art passes `lint_art.py`, `make_art.py` and `validate.py` like all other art.

## Risks

- **Nothing can be run here.** The game is not installed on this Mac, and the reference
  assembly is a stub whose method bodies are missing, so every claim about vanilla runtime
  behaviour is inference. The whole feature needs an in-game pass on the Steam machine.
- **`SetUpFoyerShop` fails silently.** It wraps its body in a try/catch that only logs and
  returns null, so a mistyped resource path yields no stall and no error in game. The
  in-game checklist starts by confirming the stall exists at all and reading the log.
- **Placement is absolute.** The position is a Breach world coordinate, and the default
  hitbox offset is built then discarded by Alexandria, so the hitbox offset must be passed
  explicitly. Expect to tune both in game.
- **Chest gating is unproven.** If chests turn out to ignore prerequisites, the per-run loot
  table guard is what actually enforces the lock; that is why it exists rather than being an
  optimisation.
- **Flag id drift** across mod sets, mitigated by the string mirror above.

## Out of scope

No new synergies, no consumables or run-scoped goods, no changes to Pluto's starting kit or
to the older gear, and no second shop.
