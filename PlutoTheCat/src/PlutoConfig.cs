using System;
using BepInEx.Configuration;
using UnityEngine;

namespace PlutoTheCat
{
    /// <summary>
    /// Tunables exposed through BepInEx/config/bogdan.etg.plutothecat.cfg so balance and Breach
    /// placement can be adjusted without a rebuild. Read once at load; numeric values are range-checked
    /// by PlutoConfigRules (clamped with a warning in the BepInEx log).
    /// </summary>
    public static class PlutoConfig
    {
        public static int StartingLife = 7;
        public static float KibbleDamage = 3.5f;
        public static int KibbleClip = 10;
        public static float KibbleCritChance = 0.05f;
        public static float TaiyakiDamage = 8f;
        public static int TaiyakiClip = 10;
        public static float SecretDoorDamage = 15f;
        public static bool NoFallDamage = true;
        public static float CanSplashRadius = 2f;
        public static float CanDamage = 5f;
        public static float CharmDuration = 10f;
        public static float BossStunSeconds = 3f;
        public static float CanCooldownDamage = 200f;
        public static float TailWhipDamage = 6f;
        public static float ZoomiesSeconds = 4f;
        public static float ZoomiesSpeedBonus = 2.5f;
        public static bool HairballEnabled = true;
        public static bool ChuruDropEnabled = true;
        public static int InvulnerableRollFrames = 6;
        public static Vector3 FoyerPosition = new Vector3(14.6f, 22.1f, 0f);
        public static Vector3 BathtubOffset = new Vector3(0f, 2.1f, 0f);
        public static Vector3 BathtubPosition { get { return FoyerPosition + BathtubOffset; } }
        public static bool LogPunchoutNames = true;
        public static bool UnlockSamuraiCostume = false;
        public static float AngrySeconds = 6f;
        public static float AngryDamageMultiplier = 1.5f;
        public static float AngryFireRateMultiplier = 1.3f;
        public static float AngryScale = 1.0f;
        public static float MaxSpeedBonus = 4f;
        public static bool CocoBlocksBullets = true;
        public static float DecoySeconds = 8f;
        public static float DecoyCooldownDamage = 150f;
        public static int CocoStuffing = 8;
        public static float CocoKnockoutSeconds = 10f;
        public static float CocoStuffingRegenSeconds = 4f;

        private static readonly Action<string> Warn = message => Debug.LogWarning("[Pluto] config: " + message);

        public static void Bind(ConfigFile cfg)
        {
            StartingLife = PlutoConfigRules.Clamp("StartingLife", cfg.Bind("Balance", "StartingLife", StartingLife, "Which of his nine lives Pluto starts a run on (7 = two saves left; 9 = no saves; 1 = eight saves).").Value, StartingLife, Warn);
            KibbleDamage = PlutoConfigRules.Clamp("KibbleDamage", cfg.Bind("Balance", "KibbleDamage", KibbleDamage, "Damage per kibble (two kibble per shot).").Value, KibbleDamage, Warn);
            KibbleClip = PlutoConfigRules.Clamp("KibbleClip", cfg.Bind("Balance", "KibbleClip", KibbleClip, "Shots per clip for the Royal Kibble Sack.").Value, KibbleClip, Warn);
            KibbleCritChance = PlutoConfigRules.Clamp("KibbleCritChance", cfg.Bind("Balance", "KibbleCritChance", KibbleCritChance, "Chance (0-1) that a kibble is a big chunk (3.5x damage).").Value, KibbleCritChance, Warn);
            TaiyakiDamage = PlutoConfigRules.Clamp("TaiyakiDamage", cfg.Bind("Balance", "TaiyakiDamage", TaiyakiDamage, "Damage per mini taiyaki from the Taiyaki Cannon (samurai costume; one shot every 0.2 s).").Value, TaiyakiDamage, Warn);
            TaiyakiClip = PlutoConfigRules.Clamp("TaiyakiClip", cfg.Bind("Balance", "TaiyakiClip", TaiyakiClip, "Shots per clip for the Taiyaki Cannon.").Value, TaiyakiClip, Warn);
            SecretDoorDamage = PlutoConfigRules.Clamp("SecretDoorDamage", cfg.Bind("Kibble Sack", "SecretDoorDamage", SecretDoorDamage, "Extra damage each kibble deals to a secret-room wall on top of its own (walls have 100 hit points; 0 = normal damage only).").Value, SecretDoorDamage, Warn);
            NoFallDamage = cfg.Bind("Balance", "NoFallDamage", NoFallDamage, "Pluto lands on his feet: falling into a pit costs no health.").Value;
            CanSplashRadius = PlutoConfigRules.Clamp("CanSplashRadius", cfg.Bind("Balance", "CanSplashRadius", CanSplashRadius, "Wet Food Can: radius in tiles of the gravy splash that charms enemies around the burst.").Value, CanSplashRadius, Warn);
            CanDamage = PlutoConfigRules.Clamp("CanDamage", cfg.Bind("Balance", "CanDamage", CanDamage, "Wet Food Can: damage to the enemy the thrown can hits.").Value, CanDamage, Warn);
            CharmDuration = PlutoConfigRules.Clamp("CharmDuration", cfg.Bind("Balance", "CharmDuration", CharmDuration, "Wet Food Can charm duration in seconds.").Value, CharmDuration, Warn);
            BossStunSeconds = PlutoConfigRules.Clamp("BossStunSeconds", cfg.Bind("Balance", "BossStunSeconds", BossStunSeconds, "How long the can stuns a boss.").Value, BossStunSeconds, Warn);
            CanCooldownDamage = PlutoConfigRules.Clamp("CanCooldownDamage", cfg.Bind("Balance", "CanCooldownDamage", CanCooldownDamage, "Damage dealt to recharge the Wet Food Can.").Value, CanCooldownDamage, Warn);
            TailWhipDamage = PlutoConfigRules.Clamp("TailWhipDamage", cfg.Bind("Balance", "TailWhipDamage", TailWhipDamage, "Damage dealt when Pluto rolls through an enemy (0 disables).").Value, TailWhipDamage, Warn);
            ZoomiesSeconds = PlutoConfigRules.Clamp("ZoomiesSeconds", cfg.Bind("Balance", "ZoomiesSeconds", ZoomiesSeconds, "Speed burst duration after clearing a room (0 disables).").Value, ZoomiesSeconds, Warn);
            ZoomiesSpeedBonus = PlutoConfigRules.Clamp("ZoomiesSpeedBonus", cfg.Bind("Balance", "ZoomiesSpeedBonus", ZoomiesSpeedBonus, "Movement speed added during zoomies.").Value, ZoomiesSpeedBonus, Warn);
            HairballEnabled = cfg.Bind("Balance", "Hairball", HairballEnabled, "Reloading an empty clip coughs up a slow stunning hairball.").Value;
            ChuruDropEnabled = cfg.Bind("Balance", "ChuruDrop", ChuruDropEnabled, "Taiyaki Cannon: finishing a reload of an empty clip spits a Churu drop (5 damage, 3 splash within 1.5 tiles).").Value;
            InvulnerableRollFrames = PlutoConfigRules.Clamp("InvulnerableRollFrames", cfg.Bind("Balance", "InvulnerableRollFrames", InvulnerableRollFrames, "Dodge-roll frames (of 9) that are invulnerable.").Value, InvulnerableRollFrames, Warn);
            FoyerPosition = Vec(cfg.Bind("Breach", "FoyerPosition", "14.6,22.1", "Where Pluto stands in the Breach (x,y).").Value, FoyerPosition);
            BathtubOffset = Vec(cfg.Bind("Breach", "BathtubOffset", "0,2.1", "Where the samurai costume's kimono stand stands, relative to Pluto (dx,dy); positive dy is above him. (The key keeps its old name so existing configs still work.)").Value, BathtubOffset);
            AngrySeconds = PlutoConfigRules.Clamp("AngrySeconds", cfg.Bind("Balance", "AngrySeconds", AngrySeconds, "How long Pluto stays puffed up after a hit (0 disables).").Value, AngrySeconds, Warn);
            AngryDamageMultiplier = PlutoConfigRules.Clamp("AngryDamageMultiplier", cfg.Bind("Balance", "AngryDamageMultiplier", AngryDamageMultiplier, "Damage multiplier while puffed up.").Value, AngryDamageMultiplier, Warn);
            AngryFireRateMultiplier = PlutoConfigRules.Clamp("AngryFireRateMultiplier", cfg.Bind("Balance", "AngryFireRateMultiplier", AngryFireRateMultiplier, "Rate-of-fire multiplier while puffed up.").Value, AngryFireRateMultiplier, Warn);
            AngryScale = PlutoConfigRules.Clamp("AngryScale", cfg.Bind("Balance", "AngryScale", AngryScale, "Extra body scale while puffed up (1 = normal; the standing fur already makes him look bigger; values above 1 may misalign the fur).").Value, AngryScale, Warn);
            MaxSpeedBonus = PlutoConfigRules.Clamp("MaxSpeedBonus", cfg.Bind("Balance", "MaxSpeedBonus", MaxSpeedBonus, "Cap on the total movement speed Pluto's own boosts (zoomies, anger, petting) can add at once.").Value, MaxSpeedBonus, Warn);
            CocoBlocksBullets = cfg.Bind("Balance", "CocoBlocksBullets", CocoBlocksBullets, "Enemy bullets that touch Coco Blue are stopped.").Value;
            DecoySeconds = PlutoConfigRules.Clamp("DecoySeconds", cfg.Bind("Balance", "DecoySeconds", DecoySeconds, "How long Coco stays in decoy mode after the Squeaky Toy is used.").Value, DecoySeconds, Warn);
            DecoyCooldownDamage = PlutoConfigRules.Clamp("DecoyCooldownDamage", cfg.Bind("Balance", "DecoyCooldownDamage", DecoyCooldownDamage, "Damage dealt to recharge the Squeaky Toy.").Value, DecoyCooldownDamage, Warn);
            CocoStuffing = PlutoConfigRules.Clamp("CocoStuffing", cfg.Bind("Balance", "CocoStuffing", CocoStuffing, "Bullets Coco can block before he is knocked out (regenerates one every CocoStuffingRegenSeconds).").Value, CocoStuffing, Warn);
            CocoKnockoutSeconds = PlutoConfigRules.Clamp("CocoKnockoutSeconds", cfg.Bind("Balance", "CocoKnockoutSeconds", CocoKnockoutSeconds, "How long Coco stays knocked out (petting him ends it early).").Value, CocoKnockoutSeconds, Warn);
            CocoStuffingRegenSeconds = PlutoConfigRules.Clamp("CocoStuffingRegenSeconds", cfg.Bind("Balance", "CocoStuffingRegenSeconds", CocoStuffingRegenSeconds, "Seconds per point of stuffing regained while not knocked out.").Value, CocoStuffingRegenSeconds, Warn);
            LogPunchoutNames = cfg.Bind("Debug", "LogPunchoutNames", LogPunchoutNames, "Write the Pilot's Punch-Out sprite names to the log at startup.").Value;
            UnlockSamuraiCostume = cfg.Bind("Debug", "UnlockSamuraiCostume", UnlockSamuraiCostume, "Testing only: unlock the samurai costume in the Breach without beating Pluto's past (normally it appears after the Vet is beaten).").Value;
        }

        private static Vector3 Vec(string text, Vector3 fallback)
        {
            try
            {
                string[] parts = text.Split(',');
                float x = float.Parse(parts[0].Trim(), System.Globalization.CultureInfo.InvariantCulture);
                float y = float.Parse(parts[1].Trim(), System.Globalization.CultureInfo.InvariantCulture);
                if (float.IsNaN(x) || float.IsInfinity(x) || float.IsNaN(y) || float.IsInfinity(y))
                {
                    Warn("position \"" + text + "\" is not a pair of numbers; using the default.");
                    return fallback;
                }
                return new Vector3(x, y, 0f);
            }
            catch { return fallback; }
        }
    }
}
