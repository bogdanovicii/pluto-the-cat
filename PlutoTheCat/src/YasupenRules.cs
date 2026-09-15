using System;

namespace PlutoTheCat
{
    /// <summary>
    /// Yasupen's decisions (2.18.0), engine-free so they run under Mono: when he may belly-slide, how many casings a
    /// "miracle bargain" drops, and the shop price multiplier. YasupenItem wires them to the game.
    /// </summary>
    internal static class YasupenRules
    {
        public const int BargainMin = 3, BargainMax = 5;
        public const float MaxDiscount = 0.5f;

        /// <summary>In combat, an enemy within range (NaN = none), and the cooldown passed (the first slide is always ready).</summary>
        public static bool SlideReady(float now, float lastSlide, float cooldownSeconds, bool ownerInCombat, float nearestEnemyDistance, float maxRange)
        {
            if (!ownerInCombat || float.IsNaN(nearestEnemyDistance) || nearestEnemyDistance > maxRange) return false;
            return now - lastSlide >= cooldownSeconds;
        }

        /// <summary>A roll under the chance drops BargainMin..BargainMax casings, picked by amountRoll in [0, 1].</summary>
        public static int BargainCasings(float chanceRoll, float chance, float amountRoll)
        {
            if (float.IsNaN(chanceRoll) || float.IsNaN(chance) || chance <= 0f || chanceRoll >= chance) return 0;
            float roll = float.IsNaN(amountRoll) ? 0f : Math.Max(0f, Math.Min(1f, amountRoll));
            int amount = BargainMin + (int)(roll * (BargainMax - BargainMin + 1));
            return Math.Min(BargainMax, amount);
        }

        /// <summary>1 - discount, with the discount clamped to 0..MaxDiscount so shops never become free.</summary>
        public static float PriceMultiplier(float discount)
        {
            if (float.IsNaN(discount)) return 1f;
            return 1f - Math.Max(0f, Math.Min(MaxDiscount, discount));
        }
    }
}
