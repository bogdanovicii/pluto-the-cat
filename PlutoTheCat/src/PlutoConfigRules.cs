using System;
using System.Collections.Generic;

namespace PlutoTheCat
{
    /// <summary>
    /// Valid ranges for numeric config values, applied when PlutoConfig binds them. An out-of-range value is
    /// clamped and a non-number falls back to the default; both log a warning. Engine-free for Mono tests.
    /// Settings whose description says "0 disables" keep 0 as a valid minimum.
    /// </summary>
    internal static class PlutoConfigRules
    {
        private struct Range
        {
            public readonly double Min, Max;
            public Range(double min, double max) { Min = min; Max = max; }
        }

        private const double Damage = 1000, Seconds = 600, Cooldown = 100000;

        private static readonly Dictionary<string, Range> Ranges = new Dictionary<string, Range>
        {
            { "StartingLife", new Range(1, 9) },
            { "KibbleDamage", new Range(0.01, Damage) },
            { "KibbleClip", new Range(1, 1000) },
            { "KibbleCritChance", new Range(0, 1) },
            { "TaiyakiDamage", new Range(0.01, Damage) },
            { "TaiyakiClip", new Range(1, 1000) },
            { "SecretDoorDamage", new Range(0, Damage) },
            { "CanSplashRadius", new Range(0.1, 20) },
            { "CanDamage", new Range(0, Damage) },
            { "CharmDuration", new Range(0.1, Seconds) },
            { "BossStunSeconds", new Range(0, 60) },
            { "CanCooldownDamage", new Range(1, Cooldown) },
            { "TailWhipDamage", new Range(0, Damage) },
            { "ZoomiesSeconds", new Range(0, 60) },
            { "ZoomiesSpeedBonus", new Range(0, 20) },
            { "InvulnerableRollFrames", new Range(0, 9) },
            { "AngrySeconds", new Range(0, 60) },
            { "AngryDamageMultiplier", new Range(0.1, 10) },
            { "AngryFireRateMultiplier", new Range(0.1, 10) },
            { "AngryScale", new Range(0.5, 3) },
            { "MaxSpeedBonus", new Range(0, 20) },
            { "DecoySeconds", new Range(0.5, 120) },
            { "DecoyCooldownDamage", new Range(1, Cooldown) },
            { "CocoStuffing", new Range(1, 99) },
            { "CocoKnockoutSeconds", new Range(0.1, 120) },
            { "CocoStuffingRegenSeconds", new Range(0.1, 120) },
            // 2.17 cat items
            { "YarnSeconds", new Range(0.5, 30) },
            { "YarnDamage", new Range(0, Damage) },
            { "YarnTangleSeconds", new Range(0, 10) },
            { "YarnSlowSeconds", new Range(0, 30) },
            { "YarnCooldownDamage", new Range(1, Cooldown) },
            { "CatnipSeconds", new Range(0.5, 60) },
            { "CatnipSpeedBonus", new Range(0, 20) },
            { "CatnipFireRateMultiplier", new Range(0.1, 10) },
            { "CatnapSeconds", new Range(0, 30) },
            { "CatnipCooldownDamage", new Range(1, Cooldown) },
            { "BellRadius", new Range(0, 20) },
            { "BellCooldownSeconds", new Range(0, 120) },
            { "BellStunSeconds", new Range(0, 10) },
            { "HairballItemRadius", new Range(0.5, 20) },
            { "HairballItemSeconds", new Range(0.5, 60) },
            { "HairballItemBulletSpeed", new Range(0.05, 1) },
            { "HairballItemCooldownDamage", new Range(1, Cooldown) },
            { "PostRadius", new Range(0.5, 20) },
            { "PostDamageMultiplier", new Range(1, 10) },
            { "PostPierce", new Range(0, 10) },
            { "YasupenSlideCooldown", new Range(0.5, 60) },
            { "YasupenSlideRange", new Range(0, 20) },
            { "YasupenSlideDamage", new Range(0, Damage) },
            { "YasupenSlideKnockback", new Range(0, 200) },
            { "YasupenShopDiscount", new Range(0, 0.5) },
            { "YasupenBargainChance", new Range(0, 1) },
            // 2.19 cat set
            { "SprayClip", new Range(1, 99) },
            { "SprayCooldown", new Range(0.05, 10) },
            { "SprayRange", new Range(0.5, 50) },
            { "SprayDamage", new Range(0, Damage) },
            { "SprayKnockback", new Range(0, 200) },
            { "SprayFlinchChance", new Range(0, 1) },
            { "SprayFlinchSeconds", new Range(0, 10) },
            { "SprayReloadSeconds", new Range(0.05, 30) },
            { "SprayCharmBonusSeconds", new Range(0, 30) },
            { "SprayCharmMaxBonusSeconds", new Range(0.1, 60) },
            { "FeatherChargeSeconds", new Range(0.05, 10) },
            { "FeatherClip", new Range(1, 99) },
            { "FeatherRange", new Range(0.5, 50) },
            { "FeatherDamage", new Range(0, Damage) },
            { "FeatherDistractSeconds", new Range(0, 20) },
            { "FeatherBossSlowSeconds", new Range(0, 10) },
            { "FeatherReloadSeconds", new Range(0.05, 30) },
            { "TPRechargeDamage", new Range(1, Cooldown) },
            { "TPLength", new Range(0.5, 20) },
            { "TPSeconds", new Range(0.1, 60) },
            { "TPHits", new Range(1, 99) },
            { "TPConfettiDamage", new Range(0, Damage) },
            { "ConeCooldown", new Range(0.1, 60) },
            { "ConeArcDegrees", new Range(1, 180) },
            { "ConeRadius", new Range(0.1, 10) },
            { "ConeCocoStuffing", new Range(0, 20) },
            { "CoffeeRechargeDamage", new Range(1, Cooldown) },
            { "CoffeeRange", new Range(0.5, 20) },
            { "CoffeeShardCount", new Range(1, 50) },
            { "CoffeeShardDamage", new Range(0, Damage) },
            { "CoffeeSlowSeconds", new Range(0, 30) },
            { "CoffeeZoomiesBonusSeconds", new Range(0, 30) },
            // 2.20 shrine stall
            { "StallPriceBallOfYarn", new Range(1, 99) },
            { "StallPriceCatnipPouch", new Range(1, 99) },
            { "StallPriceHairball", new Range(1, 99) },
            { "StallPriceScratchingPost", new Range(1, 99) },
            { "StallPriceToiletPaperRoll", new Range(1, 99) },
            { "StallPriceCoffeeMug", new Range(1, 99) },
            { "StallPriceJingleBellCollar", new Range(1, 99) },
            { "StallPriceConeOfShame", new Range(1, 99) },
            { "StallPriceSprayBottle", new Range(1, 99) },
            { "StallPriceFeatherTeaser", new Range(1, 99) },
        };

        public static ICollection<string> Keys { get { return Ranges.Keys; } }

        public static bool Contains(string key, double value)
        {
            Range r = Get(key);
            return value >= r.Min && value <= r.Max;
        }

        public static float Clamp(string key, float value, float fallback, Action<string> warn)
        {
            Range r = Get(key);
            if (float.IsNaN(value) || float.IsInfinity(value))
            {
                Warn(warn, key + " = " + value + " is not a number; using the default " + fallback + ".");
                value = fallback;
            }
            float clamped = (float)Math.Max(r.Min, Math.Min(r.Max, value));
            if (clamped != value) Warn(warn, key + " = " + value + " is outside " + r.Min + " to " + r.Max + "; using " + clamped + ".");
            return clamped;
        }

        public static int Clamp(string key, int value, int fallback, Action<string> warn)
        {
            Range r = Get(key);
            int clamped = (int)Math.Max(Math.Ceiling(r.Min), Math.Min(Math.Floor(r.Max), value));
            if (clamped != value) Warn(warn, key + " = " + value + " is outside " + r.Min + " to " + r.Max + "; using " + clamped + ".");
            return clamped;
        }

        private static Range Get(string key)
        {
            Range r;
            if (key == null || !Ranges.TryGetValue(key, out r)) throw new ArgumentException("No config range for " + key);
            return r;
        }

        // 2.20.0 shipped StallPosition defaulting to (10.5, 22.1), which put the Shrine Stall off-screen; 2.20.1
        // raised the default to (19.7, 22.1). BepInEx keeps a value an existing config already has, so anyone
        // who ran 2.20.0 stays stuck on the broken position after updating unless PlutoConfig migrates it away
        // on load. Narrow on purpose: it only matches this exact legacy value, so it can never overwrite a
        // position a player deliberately chose (including one that happens to be near, but not exactly, it).
        public static bool IsLegacyBrokenStallPosition(float x, float y)
        {
            return Near(x, 10.5f) && Near(y, 22.1f);
        }

        private static bool Near(float a, float b)
        {
            return Math.Abs(a - b) < 0.0001f;
        }

        private static void Warn(Action<string> warn, string message)
        {
            if (warn != null) warn(message);
        }
    }
}
