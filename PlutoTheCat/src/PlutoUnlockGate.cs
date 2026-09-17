using System;
using System.Collections.Generic;
using Alexandria.DungeonAPI;
using Alexandria.Misc;
using Gungeon;

namespace PlutoTheCat
{
    /// <summary>
    /// Gates the Shrine Stall's ten cat items (PlutoUnlocks.Ids, in price-table order: BallOfYarnItem.ID,
    /// CatnipPouchItem.ID, HairballItem.ID, ScratchingPostItem.ID, ToiletPaperRollItem.ID, CoffeeMugItem.ID,
    /// JingleBellCollarItem.ID, ConeOfShameItem.ID, SprayBottleGun.ID, FeatherTeaserGun.ID): locked items get
    /// a FLAG prerequisite (so the Ammonomicon shows them as undiscovered and the foyer meta-shop stocks
    /// them) and are pulled out of the live loot tables so they stop dropping; both flip back the moment
    /// PlutoUnlocks.Unlock(id) sets the flag.
    /// </summary>
    public static class PlutoUnlockGate
    {
        private static Action _dungeonStartHandler;

        /// <summary>
        /// Reconciles the flag/mirror pair, attaches a FLAG prerequisite to each of the ten items, and hooks
        /// dungeon start so the loot-table guard re-applies every run (ItemDB.DungeonStart() re-injects mod
        /// loot into Dungeon.baseChestContents on every Dungeon.Start(), so a one-time RefreshLootTables()
        /// call here would not stick).
        /// </summary>
        public static void Apply()
        {
            PlutoUnlocks.Reconcile();

            foreach (string id in PlutoUnlocks.Ids)
            {
                if (!PlutoUnlocks.IsRegistered(id))
                {
                    Plugin.Log("unlock gate: skipping " + id + " (its unlock flag never registered)");
                    continue;
                }
                if (!Game.Items.ContainsID(id))
                {
                    Plugin.Log("unlock gate: skipping " + id + " (item not registered)");
                    continue;
                }

                PickupObject pickup = Game.Items[id];
                if (pickup == null || pickup.encounterTrackable == null) continue;

                // The testing escape hatch has to clear the prerequisite, not just the loot-table guard.
                // ShrineStallRules.Unlocked(disabled: true) only drives RefreshLootTables; an item put back
                // in the loot tables while still carrying an unmet FLAG prerequisite is still skipped by
                // every prereq-respecting selector, still stocked by the stall, and still "???" in the
                // Ammonomicon - which is the opposite of what both READMEs promise the toggle does.
                if (PlutoConfig.StallUnlocksDisabled)
                {
                    pickup.encounterTrackable.prerequisites = new DungeonPrerequisite[0];
                    continue;
                }

                DungeonPrerequisite prereq = new DungeonPrerequisite();
                prereq.prerequisiteType = DungeonPrerequisite.PrerequisiteType.FLAG;
                prereq.saveFlagToCheck = PlutoUnlocks.Flag(id);
                prereq.requireFlag = true;
                pickup.encounterTrackable.prerequisites = new DungeonPrerequisite[] { prereq };
            }

            if (_dungeonStartHandler == null)
            {
                _dungeonStartHandler = OnDungeonGenerated;
                DungeonHooks.OnPostDungeonGeneration += _dungeonStartHandler;
            }

            RefreshLootTables();
        }

        /// <summary>Unhooks the dungeon-start guard. Safe to call even if Apply() was never called.</summary>
        public static void Teardown()
        {
            if (_dungeonStartHandler == null) return;
            DungeonHooks.OnPostDungeonGeneration -= _dungeonStartHandler;
            _dungeonStartHandler = null;
        }

        /// <summary>
        /// Per-run entry point. Reconcile first: a purchase made in the Breach lands as a GungeonFlags value
        /// only (see PlutoUnlocks.Reconcile), and the mirror has to catch up before the guard decides what
        /// counts as unlocked.
        /// </summary>
        private static void OnDungeonGenerated()
        {
            PlutoUnlocks.Reconcile();
            RefreshLootTables();
        }

        /// <summary>
        /// Removes locked items from the live loot tables and re-adds unlocked ones. Safe to call repeatedly:
        /// every removal path here is keyed on PickupObjectId and is a no-op when the pickup is absent, and a
        /// re-add is always preceded by a removal so repeat calls cannot duplicate an entry.
        ///
        /// Three collections, not one. LootUtility.RemovePickupFromLootTables touches ONLY
        /// RewardManager.GunsLootTable and .ItemsLootTable (its whole body, read from the Alexandria 0.5.10
        /// IL, is two FindWeightedGameObjectInCollection + List.Remove pairs against exactly those two). But
        /// ItemDB.AddSpecific puts the same WeightedGameObject into ModLootPerFloor as well, and
        /// ItemDB.DungeonStart - a Harmony *prefix* on Dungeonator.Dungeon.Start - AddRanges
        /// ModLootPerFloor["ANY"] and ModLootPerFloor[&lt;floor&gt;] into
        /// Dungeon.baseChestContents.defaultItemDrops.elements, which is what actually feeds chests. Sweeping
        /// only the RewardManager tables would leave the backstop touching none of the chest path at all.
        /// ModLootPerFloor is swept so the next Dungeon.Start cannot re-inject a locked item; baseChestContents
        /// is swept because by the time OnPostDungeonGeneration fires, that prefix has already run for this run.
        /// </summary>
        public static void RefreshLootTables()
        {
            if (!GameManager.HasInstance || GameManager.Instance.RewardManager == null) return;

            foreach (string id in PlutoUnlocks.Ids)
            {
                if (!Game.Items.ContainsID(id)) continue;
                PickupObject pickup = Game.Items[id];
                if (pickup == null) continue;

                // Clear every collection first, unlocked or not, so a repeat call can never duplicate an
                // entry and so an item that was unlocked and is somehow no longer (a save slot switch)
                // really does leave the tables.
                LootUtility.RemovePickupFromLootTables(pickup);
                RemoveFromModLoot(pickup);
                RemoveFromList(ChestTable(), pickup);

                if (!PlutoUnlocks.IsUnlocked(id)) continue;

                GenericLootTable table = pickup is Gun
                    ? GameManager.Instance.RewardManager.GunsLootTable
                    : GameManager.Instance.RewardManager.ItemsLootTable;
                // 1f is not a guess: ItemDB.AddSpecific builds its WeightedGameObject with `weight = 1f`
                // and `additionalPrerequisites = new DungeonPrerequisite[0]`, and LootUtility.AddItemToPool
                // defaults its optional weight parameter to 1f as well, so re-adding at 1f restores exactly
                // the entry the mod API created when the item was registered.
                if (table != null) LootUtility.AddItemToPool(table, pickup, 1f);
                AddToModLoot(pickup);
                // The chest table needs its own re-add for the run already generating: ItemDB.DungeonStart
                // ran as a prefix on Dungeon.Start, long before this hook, so a fresh ModLootPerFloor entry
                // would not reach this run's chests until the next floor.
                List<WeightedGameObject> chest = ChestTable();
                if (chest != null) chest.Add(NewEntry(pickup));
            }
        }

        /// <summary>An entry shaped exactly like the one LootUtility.AddItemToPool builds.</summary>
        private static WeightedGameObject NewEntry(PickupObject pickup)
        {
            WeightedGameObject entry = new WeightedGameObject();
            entry.pickupId = pickup.PickupObjectId;
            entry.weight = 1f;
            entry.rawGameObject = pickup.gameObject;
            entry.forceDuplicatesPossible = false;
            entry.additionalPrerequisites = new DungeonPrerequisite[0];
            return entry;
        }

        /// <summary>ETGMod.Databases.Items.ModLootPerFloor, or null when the mod API is not up yet.</summary>
        private static Dictionary<string, List<WeightedGameObject>> ModLoot()
        {
            return ETGMod.Databases.Items == null ? null : ETGMod.Databases.Items.ModLootPerFloor;
        }

        /// <summary>
        /// The current dungeon's chest table (Dungeon.baseChestContents.defaultItemDrops.elements), or null
        /// in the Breach / before generation.
        /// </summary>
        private static List<WeightedGameObject> ChestTable()
        {
            Dungeonator.Dungeon dungeon = GameManager.Instance.Dungeon;
            if (dungeon == null || dungeon.baseChestContents == null) return null;
            WeightedGameObjectCollection drops = dungeon.baseChestContents.defaultItemDrops;
            return drops == null ? null : drops.elements;
        }

        private static void RemoveFromList(List<WeightedGameObject> list, PickupObject pickup)
        {
            if (list == null) return;
            for (int i = list.Count - 1; i >= 0; i--)
                if (list[i] != null && list[i].pickupId == pickup.PickupObjectId) list.RemoveAt(i);
        }

        /// <summary>Drops this pickup from every floor list, so the next Dungeon.Start cannot re-inject it.</summary>
        private static void RemoveFromModLoot(PickupObject pickup)
        {
            Dictionary<string, List<WeightedGameObject>> modLoot = ModLoot();
            if (modLoot == null) return;
            foreach (KeyValuePair<string, List<WeightedGameObject>> floor in modLoot)
                RemoveFromList(floor.Value, pickup);
        }

        /// <summary>Puts an unlocked pickup back under "ANY", the key ItemDB.AddSpecific defaults to.</summary>
        private static void AddToModLoot(PickupObject pickup)
        {
            Dictionary<string, List<WeightedGameObject>> modLoot = ModLoot();
            if (modLoot == null) return;
            List<WeightedGameObject> list;
            if (!modLoot.TryGetValue("ANY", out list) || list == null)
            {
                list = new List<WeightedGameObject>();
                modLoot["ANY"] = list;
            }
            list.Add(NewEntry(pickup));
        }
    }
}
