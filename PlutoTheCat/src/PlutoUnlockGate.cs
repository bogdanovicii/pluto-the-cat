using System;
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
        /// Attaches a FLAG prerequisite to each of the ten items and hooks dungeon start so the loot-table
        /// guard re-applies every run (ItemDB.DungeonStart() re-injects mod loot into Dungeon.baseChestContents
        /// on every Dungeon.Start(), so a one-time RefreshLootTables() call here would not stick).
        /// </summary>
        public static void Apply()
        {
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

                DungeonPrerequisite prereq = new DungeonPrerequisite();
                prereq.prerequisiteType = DungeonPrerequisite.PrerequisiteType.FLAG;
                prereq.saveFlagToCheck = PlutoUnlocks.Flag(id);
                prereq.requireFlag = true;
                pickup.encounterTrackable.prerequisites = new DungeonPrerequisite[] { prereq };
            }

            if (_dungeonStartHandler == null)
            {
                _dungeonStartHandler = RefreshLootTables;
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
        /// Removes locked items from the live loot tables and re-adds unlocked ones. Safe to call repeatedly:
        /// RemovePickupFromLootTables is a no-op when the pickup is already absent, and re-adding an already
        /// present pickup only duplicates its loot-table entry, which the per-run refresh from dungeon start
        /// then removes and re-adds cleanly on the next call.
        /// </summary>
        public static void RefreshLootTables()
        {
            if (!GameManager.HasInstance || GameManager.Instance.RewardManager == null) return;

            foreach (string id in PlutoUnlocks.Ids)
            {
                if (!Game.Items.ContainsID(id)) continue;
                PickupObject pickup = Game.Items[id];
                if (pickup == null) continue;

                if (!PlutoUnlocks.IsUnlocked(id))
                {
                    LootUtility.RemovePickupFromLootTables(pickup);
                }
                else
                {
                    GenericLootTable table = pickup is Gun
                        ? GameManager.Instance.RewardManager.GunsLootTable
                        : GameManager.Instance.RewardManager.ItemsLootTable;
                    if (table == null) continue;
                    LootUtility.RemovePickupFromLootTables(pickup);   // avoid duplicate entries on repeat calls
                    LootUtility.AddItemToPool(table, pickup, 1f);
                }
            }
        }
    }
}
