using System;

namespace PlutoTheCat
{
    /// <summary>Engine-free rules for the Shrine Stall: prices, unlock-flag naming and the unlock decision.</summary>
    public static class ShrineStallRules
    {
        /// <summary>The price bound to an item id, or 0 when the id is unknown or any argument is missing.</summary>
        public static int Price(string itemId, int[] prices, string[] ids)
        {
            if (itemId == null || prices == null || ids == null) return 0;
            for (int i = 0; i < ids.Length && i < prices.Length; i++)
                if (ids[i] == itemId) return prices[i];
            return 0;
        }

        private static string Suffix(string itemId)
        {
            if (string.IsNullOrEmpty(itemId)) return "";
            int colon = itemId.IndexOf(':');
            return colon >= 0 ? itemId.Substring(colon + 1) : itemId;
        }

        /// <summary>The extended GungeonFlags name for an item id, e.g. "pluto:coffee_mug" to "PLUTO_UNLOCK_COFFEE_MUG".</summary>
        public static string FlagName(string itemId) { return "PLUTO_UNLOCK_" + Suffix(itemId).ToUpperInvariant(); }

        /// <summary>The string-mirror key for an item id, used because extended flag ids drift when other mods are installed.</summary>
        public static string MirrorKey(string itemId) { return "bogdan.etg.plutothecat:" + Suffix(itemId); }

        /// <summary>The disagreement rule: a disabled config unlocks everything; otherwise either the flag or the mirror unlocks.</summary>
        public static bool Unlocked(bool flag, bool mirror, bool disabled) { return disabled || flag || mirror; }
    }
}
