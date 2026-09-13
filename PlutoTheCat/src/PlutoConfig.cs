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
        public static int NineLives = 9;
        public static float KibbleDamage = 3.5f;
        public static int KibbleClip = 10;
        public static float KibbleCritChance = 0.05f;
        public static float CharmRadius = 4.5f;
        public static float CharmDuration = 10f;
        public static float BossStunSeconds = 3f;
        public static float CanCooldownDamage = 200f;
        public static float TailWhipDamage = 6f;
        public static float ZoomiesSeconds = 4f;
        public static float ZoomiesSpeedBonus = 2.5f;
        public static bool HairballEnabled = true;
        public static int InvulnerableRollFrames = 6;
        public static Vector3 FoyerPosition = new Vector3(14.6f, 22.1f, 0f);
        public static Vector3 BathtubPosition = new Vector3(15.6f, 20.4f, 0f);
        public static bool LogPunchoutNames = true;
        public static float AngrySeconds = 6f;
        public static float AngryDamageMultiplier = 1.5f;
        public static float AngryFireRateMultiplier = 1.3f;
        public static float AngryScale = 1.25f;
        public static float MaxSpeedBonus = 4f;

        public static void Bind(ConfigFile cfg)
        {
            NineLives = cfg.Bind("Balance", "NineLives", NineLives, "Lives per run for the Nine Lives passive (0 disables it).").Value;
            KibbleDamage = cfg.Bind("Balance", "KibbleDamage", KibbleDamage, "Damage per kibble (two kibble per shot).").Value;
            KibbleClip = cfg.Bind("Balance", "KibbleClip", KibbleClip, "Shots per clip for the Royal Kibble Sack.").Value;
            KibbleCritChance = cfg.Bind("Balance", "KibbleCritChance", KibbleCritChance, "Chance (0-1) that a kibble is a big chunk (3.5x damage).").Value;
            CharmRadius = cfg.Bind("Balance", "CharmRadius", CharmRadius, "Wet Food Can charm radius in tiles.").Value;
            CharmDuration = cfg.Bind("Balance", "CharmDuration", CharmDuration, "Wet Food Can charm duration in seconds.").Value;
            BossStunSeconds = cfg.Bind("Balance", "BossStunSeconds", BossStunSeconds, "How long the can stuns a boss.").Value;
            CanCooldownDamage = cfg.Bind("Balance", "CanCooldownDamage", CanCooldownDamage, "Damage dealt to recharge the Wet Food Can.").Value;
            TailWhipDamage = cfg.Bind("Balance", "TailWhipDamage", TailWhipDamage, "Damage dealt when Pluto rolls through an enemy (0 disables).").Value;
            ZoomiesSeconds = cfg.Bind("Balance", "ZoomiesSeconds", ZoomiesSeconds, "Speed burst duration after clearing a room (0 disables).").Value;
            ZoomiesSpeedBonus = cfg.Bind("Balance", "ZoomiesSpeedBonus", ZoomiesSpeedBonus, "Movement speed added during zoomies.").Value;
            HairballEnabled = cfg.Bind("Balance", "Hairball", HairballEnabled, "Reloading an empty clip coughs up a slow stunning hairball.").Value;
            InvulnerableRollFrames = cfg.Bind("Balance", "InvulnerableRollFrames", InvulnerableRollFrames, "Dodge-roll frames (of 9) that are invulnerable.").Value;
            FoyerPosition = Vec(cfg.Bind("Breach", "FoyerPosition", "14.6,22.1", "Where Pluto stands in the Breach (x,y).").Value, FoyerPosition);
            BathtubPosition = Vec(cfg.Bind("Breach", "BathtubPosition", "15.6,20.4", "Where the alt-skin bathtub stands (x,y).").Value, BathtubPosition);
            AngrySeconds = cfg.Bind("Balance", "AngrySeconds", AngrySeconds, "How long Pluto stays puffed up after a hit (0 disables).").Value;
            AngryDamageMultiplier = cfg.Bind("Balance", "AngryDamageMultiplier", AngryDamageMultiplier, "Damage multiplier while puffed up.").Value;
            AngryFireRateMultiplier = cfg.Bind("Balance", "AngryFireRateMultiplier", AngryFireRateMultiplier, "Rate-of-fire multiplier while puffed up.").Value;
            AngryScale = cfg.Bind("Balance", "AngryScale", AngryScale, "Sprite scale while puffed up (1 = normal size).").Value;
            MaxSpeedBonus = cfg.Bind("Balance", "MaxSpeedBonus", MaxSpeedBonus, "Cap on the total movement speed Pluto's own boosts (zoomies, anger, petting) can add at once.").Value;
            LogPunchoutNames = cfg.Bind("Debug", "LogPunchoutNames", LogPunchoutNames, "Write the Pilot's Punch-Out sprite names to the log at startup.").Value;
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
