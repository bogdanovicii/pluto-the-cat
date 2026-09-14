using BepInEx.Configuration;
using UnityEngine;

namespace PlutoTheCat
{
    /// <summary>
    /// Tunables exposed through BepInEx/config/bogdan.etg.plutothecat.cfg so balance and Breach
    /// placement can be adjusted without a rebuild. Read once at load.
    /// </summary>
    public static class PlutoConfig
    {
        public static int StartingLife = 7;
        public static float KibbleDamage = 3.5f;
        public static int KibbleClip = 10;
        public static float KibbleCritChance = 0.05f;
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

        public static void Bind(ConfigFile cfg)
        {
            StartingLife = cfg.Bind("Balance", "StartingLife", StartingLife, "Which of his nine lives Pluto starts a run on (7 = two saves left; 9 = no saves; 1 = eight saves).").Value;
            KibbleDamage = cfg.Bind("Balance", "KibbleDamage", KibbleDamage, "Damage per kibble (two kibble per shot).").Value;
            KibbleClip = cfg.Bind("Balance", "KibbleClip", KibbleClip, "Shots per clip for the Royal Kibble Sack.").Value;
            KibbleCritChance = cfg.Bind("Balance", "KibbleCritChance", KibbleCritChance, "Chance (0-1) that a kibble is a big chunk (3.5x damage).").Value;
            SecretDoorDamage = cfg.Bind("Kibble Sack", "SecretDoorDamage", SecretDoorDamage, "Extra damage each kibble deals to a secret-room wall on top of its own (walls have 100 hit points; 0 = normal damage only).").Value;
            NoFallDamage = cfg.Bind("Balance", "NoFallDamage", NoFallDamage, "Pluto lands on his feet: falling into a pit costs no health.").Value;
            CanSplashRadius = cfg.Bind("Balance", "CanSplashRadius", CanSplashRadius, "Wet Food Can: radius in tiles of the gravy splash that charms enemies around the burst.").Value;
            CanDamage = cfg.Bind("Balance", "CanDamage", CanDamage, "Wet Food Can: damage to the enemy the thrown can hits.").Value;
            CharmDuration = cfg.Bind("Balance", "CharmDuration", CharmDuration, "Wet Food Can charm duration in seconds.").Value;
            BossStunSeconds = cfg.Bind("Balance", "BossStunSeconds", BossStunSeconds, "How long the can stuns a boss.").Value;
            CanCooldownDamage = cfg.Bind("Balance", "CanCooldownDamage", CanCooldownDamage, "Damage dealt to recharge the Wet Food Can.").Value;
            TailWhipDamage = cfg.Bind("Balance", "TailWhipDamage", TailWhipDamage, "Damage dealt when Pluto rolls through an enemy (0 disables).").Value;
            ZoomiesSeconds = cfg.Bind("Balance", "ZoomiesSeconds", ZoomiesSeconds, "Speed burst duration after clearing a room (0 disables).").Value;
            ZoomiesSpeedBonus = cfg.Bind("Balance", "ZoomiesSpeedBonus", ZoomiesSpeedBonus, "Movement speed added during zoomies.").Value;
            HairballEnabled = cfg.Bind("Balance", "Hairball", HairballEnabled, "Reloading an empty clip coughs up a slow stunning hairball.").Value;
            InvulnerableRollFrames = cfg.Bind("Balance", "InvulnerableRollFrames", InvulnerableRollFrames, "Dodge-roll frames (of 9) that are invulnerable.").Value;
            FoyerPosition = Vec(cfg.Bind("Breach", "FoyerPosition", "14.6,22.1", "Where Pluto stands in the Breach (x,y).").Value, FoyerPosition);
            BathtubOffset = Vec(cfg.Bind("Breach", "BathtubOffset", "0,2.1", "Where the samurai costume's kimono stand stands, relative to Pluto (dx,dy); positive dy is above him. (The key keeps its old name so existing configs still work.)").Value, BathtubOffset);
            AngrySeconds = cfg.Bind("Balance", "AngrySeconds", AngrySeconds, "How long Pluto stays puffed up after a hit (0 disables).").Value;
            AngryDamageMultiplier = cfg.Bind("Balance", "AngryDamageMultiplier", AngryDamageMultiplier, "Damage multiplier while puffed up.").Value;
            AngryFireRateMultiplier = cfg.Bind("Balance", "AngryFireRateMultiplier", AngryFireRateMultiplier, "Rate-of-fire multiplier while puffed up.").Value;
            AngryScale = cfg.Bind("Balance", "AngryScale", AngryScale, "Extra body scale while puffed up (1 = normal; the standing fur already makes him look bigger; values above 1 may misalign the fur).").Value;
            MaxSpeedBonus = cfg.Bind("Balance", "MaxSpeedBonus", MaxSpeedBonus, "Cap on the total movement speed Pluto's own boosts (zoomies, anger, petting) can add at once.").Value;
            CocoBlocksBullets = cfg.Bind("Balance", "CocoBlocksBullets", CocoBlocksBullets, "Enemy bullets that touch Coco Blue are stopped.").Value;
            DecoySeconds = cfg.Bind("Balance", "DecoySeconds", DecoySeconds, "How long Coco stays in decoy mode after the Squeaky Toy is used.").Value;
            DecoyCooldownDamage = cfg.Bind("Balance", "DecoyCooldownDamage", DecoyCooldownDamage, "Damage dealt to recharge the Squeaky Toy.").Value;
            CocoStuffing = cfg.Bind("Balance", "CocoStuffing", CocoStuffing, "Bullets Coco can block before he is knocked out (regenerates one every CocoStuffingRegenSeconds).").Value;
            CocoKnockoutSeconds = cfg.Bind("Balance", "CocoKnockoutSeconds", CocoKnockoutSeconds, "How long Coco stays knocked out (petting him ends it early).").Value;
            CocoStuffingRegenSeconds = cfg.Bind("Balance", "CocoStuffingRegenSeconds", CocoStuffingRegenSeconds, "Seconds per point of stuffing regained while not knocked out.").Value;
            LogPunchoutNames = cfg.Bind("Debug", "LogPunchoutNames", LogPunchoutNames, "Write the Pilot's Punch-Out sprite names to the log at startup.").Value;
            UnlockSamuraiCostume = cfg.Bind("Debug", "UnlockSamuraiCostume", UnlockSamuraiCostume, "Testing only: unlock the samurai costume in the Breach without beating Pluto's past (normally it appears after the Vet is beaten).").Value;
        }

        private static Vector3 Vec(string text, Vector3 fallback)
        {
            try
            {
                string[] parts = text.Split(',');
                return new Vector3(float.Parse(parts[0].Trim(), System.Globalization.CultureInfo.InvariantCulture),
                                   float.Parse(parts[1].Trim(), System.Globalization.CultureInfo.InvariantCulture), 0f);
            }
            catch { return fallback; }
        }
    }
}
