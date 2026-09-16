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

        // 2.17 cat items (section "Cat Items")
        public static float YarnSeconds = 6f;
        public static float YarnDamage = 4f;
        public static float YarnTangleSeconds = 1.5f;
        public static float YarnSlowSeconds = 3f;
        public static float YarnCooldownDamage = 300f;
        public static float CatnipSeconds = 7f;
        public static float CatnipSpeedBonus = 2f;
        public static float CatnipFireRateMultiplier = 1.25f;
        public static float CatnapSeconds = 2f;
        public static float CatnipCooldownDamage = 450f;
        public static float BellRadius = 2.5f;
        public static float BellCooldownSeconds = 4f;
        public static float BellStunSeconds = 1f;
        public static float HairballItemRadius = 3f;
        public static float HairballItemSeconds = 5f;
        public static float HairballItemBulletSpeed = 0.35f;
        public static float HairballItemCooldownDamage = 350f;
        public static float PostRadius = 2.5f;
        public static float PostDamageMultiplier = 1.3f;
        public static int PostPierce = 1;

        // 2.18 Yasupen (section "Yasupen")
        public static float YasupenSlideCooldown = 5f;
        public static float YasupenSlideRange = 6f;
        public static float YasupenSlideDamage = 8f;
        public static float YasupenSlideKnockback = 30f;
        public static float YasupenShopDiscount = 0.1f;
        public static float YasupenBargainChance = 0.2f;

        // 2.19 cat set (section "Cat Set 2.19")
        public static int SprayClip = 8;
        public static float SprayCooldown = 0.35f;
        public static float SprayRange = 6f;
        public static float SprayDamage = 4f;
        public static float SprayKnockback = 25f;
        public static float SprayFlinchChance = 0.35f;
        public static float SprayFlinchSeconds = 0.5f;
        public static float SprayReloadSeconds = 1f;
        public static float SprayCharmBonusSeconds = 2f;
        public static float FeatherChargeSeconds = 0.6f;
        public static int FeatherClip = 1;
        public static float FeatherRange = 7f;
        public static float FeatherDamage = 7f;
        public static float FeatherDistractSeconds = 1.5f;
        public static float FeatherBossSlowSeconds = 0.5f;
        public static float FeatherReloadSeconds = 0.4f;
        public static float TPRechargeDamage = 400f;
        public static float TPLength = 4f;
        public static float TPSeconds = 5f;
        public static int TPHits = 12;
        public static float TPConfettiDamage = 10f;
        public static float ConeCooldown = 3f;
        public static float ConeArcDegrees = 70f;
        public static float ConeRadius = 1.5f;
        public static int ConeCocoStuffing = 1;
        public static float CoffeeRechargeDamage = 300f;
        public static float CoffeeRange = 3f;
        public static int CoffeeShardCount = 10;
        public static float CoffeeShardDamage = 5f;
        public static float CoffeeSlowSeconds = 3f;
        public static float CoffeeZoomiesBonusSeconds = 2f;

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
            BindCatItems(cfg);
            BindYasupen(cfg);
            BindCatSet(cfg);
            LogPunchoutNames = cfg.Bind("Debug", "LogPunchoutNames", LogPunchoutNames, "Write the Pilot's Punch-Out sprite names to the log at startup.").Value;
            UnlockSamuraiCostume = cfg.Bind("Debug", "UnlockSamuraiCostume", UnlockSamuraiCostume, "Testing only: unlock the samurai costume in the Breach without beating Pluto's past (normally it appears after the Vet is beaten).").Value;
        }

        private static void BindCatItems(ConfigFile cfg)
        {
            const string S = "Cat Items";
            YarnSeconds = PlutoConfigRules.Clamp("YarnSeconds", cfg.Bind(S, "YarnSeconds", YarnSeconds, "Ball of Yarn: how long the thrown ball keeps bouncing around the room.").Value, YarnSeconds, Warn);
            YarnDamage = PlutoConfigRules.Clamp("YarnDamage", cfg.Bind(S, "YarnDamage", YarnDamage, "Ball of Yarn: damage each time the ball hits an enemy.").Value, YarnDamage, Warn);
            YarnTangleSeconds = PlutoConfigRules.Clamp("YarnTangleSeconds", cfg.Bind(S, "YarnTangleSeconds", YarnTangleSeconds, "Ball of Yarn: seconds a tangled enemy cannot move (bosses are only slowed).").Value, YarnTangleSeconds, Warn);
            YarnSlowSeconds = PlutoConfigRules.Clamp("YarnSlowSeconds", cfg.Bind(S, "YarnSlowSeconds", YarnSlowSeconds, "Ball of Yarn: seconds a tangled enemy stays slowed after it can move again.").Value, YarnSlowSeconds, Warn);
            YarnCooldownDamage = PlutoConfigRules.Clamp("YarnCooldownDamage", cfg.Bind(S, "YarnCooldownDamage", YarnCooldownDamage, "Ball of Yarn: damage dealt to recharge it.").Value, YarnCooldownDamage, Warn);
            CatnipSeconds = PlutoConfigRules.Clamp("CatnipSeconds", cfg.Bind(S, "CatnipSeconds", CatnipSeconds, "Catnip Pouch: length of the zoomies.").Value, CatnipSeconds, Warn);
            CatnipSpeedBonus = PlutoConfigRules.Clamp("CatnipSpeedBonus", cfg.Bind(S, "CatnipSpeedBonus", CatnipSpeedBonus, "Catnip Pouch: movement speed added during the zoomies (shares the MaxSpeedBonus cap).").Value, CatnipSpeedBonus, Warn);
            CatnipFireRateMultiplier = PlutoConfigRules.Clamp("CatnipFireRateMultiplier", cfg.Bind(S, "CatnipFireRateMultiplier", CatnipFireRateMultiplier, "Catnip Pouch: rate-of-fire multiplier during the zoomies.").Value, CatnipFireRateMultiplier, Warn);
            CatnapSeconds = PlutoConfigRules.Clamp("CatnapSeconds", cfg.Bind(S, "CatnapSeconds", CatnapSeconds, "Catnip Pouch: the drowsy slowdown after the zoomies (0 disables).").Value, CatnapSeconds, Warn);
            CatnipCooldownDamage = PlutoConfigRules.Clamp("CatnipCooldownDamage", cfg.Bind(S, "CatnipCooldownDamage", CatnipCooldownDamage, "Catnip Pouch: damage dealt to recharge it.").Value, CatnipCooldownDamage, Warn);
            BellRadius = PlutoConfigRules.Clamp("BellRadius", cfg.Bind(S, "BellRadius", BellRadius, "Jingle Bell Collar: radius in tiles of the jingle that erases enemy bullets (0 disables).").Value, BellRadius, Warn);
            BellCooldownSeconds = PlutoConfigRules.Clamp("BellCooldownSeconds", cfg.Bind(S, "BellCooldownSeconds", BellCooldownSeconds, "Jingle Bell Collar: seconds between jingles.").Value, BellCooldownSeconds, Warn);
            BellStunSeconds = PlutoConfigRules.Clamp("BellStunSeconds", cfg.Bind(S, "BellStunSeconds", BellStunSeconds, "Jingle Bell Collar: seconds non-boss enemies inside the jingle are startled (0 disables).").Value, BellStunSeconds, Warn);
            HairballItemRadius = PlutoConfigRules.Clamp("HairballItemRadius", cfg.Bind(S, "HairballItemRadius", HairballItemRadius, "Hairball (item): radius in tiles of the fur cloud.").Value, HairballItemRadius, Warn);
            HairballItemSeconds = PlutoConfigRules.Clamp("HairballItemSeconds", cfg.Bind(S, "HairballItemSeconds", HairballItemSeconds, "Hairball (item): how long the fur cloud lasts.").Value, HairballItemSeconds, Warn);
            HairballItemBulletSpeed = PlutoConfigRules.Clamp("HairballItemBulletSpeed", cfg.Bind(S, "HairballItemBulletSpeed", HairballItemBulletSpeed, "Hairball (item): enemy bullets inside the cloud move at this fraction of their speed.").Value, HairballItemBulletSpeed, Warn);
            HairballItemCooldownDamage = PlutoConfigRules.Clamp("HairballItemCooldownDamage", cfg.Bind(S, "HairballItemCooldownDamage", HairballItemCooldownDamage, "Hairball (item): damage dealt to recharge it.").Value, HairballItemCooldownDamage, Warn);
            PostRadius = PlutoConfigRules.Clamp("PostRadius", cfg.Bind(S, "PostRadius", PostRadius, "Scratching Post: how close (tiles) to stand to get sharpened claws.").Value, PostRadius, Warn);
            PostDamageMultiplier = PlutoConfigRules.Clamp("PostDamageMultiplier", cfg.Bind(S, "PostDamageMultiplier", PostDamageMultiplier, "Scratching Post: damage multiplier while sharpened.").Value, PostDamageMultiplier, Warn);
            PostPierce = PlutoConfigRules.Clamp("PostPierce", cfg.Bind(S, "PostPierce", PostPierce, "Scratching Post: extra enemies each shot pierces while sharpened.").Value, PostPierce, Warn);
        }

        private static void BindYasupen(ConfigFile cfg)
        {
            const string S = "Yasupen";
            YasupenSlideCooldown = PlutoConfigRules.Clamp("YasupenSlideCooldown", cfg.Bind(S, "YasupenSlideCooldown", YasupenSlideCooldown, "Yasupen: seconds between belly slides.").Value, YasupenSlideCooldown, Warn);
            YasupenSlideRange = PlutoConfigRules.Clamp("YasupenSlideRange", cfg.Bind(S, "YasupenSlideRange", YasupenSlideRange, "Yasupen: how far (tiles) an enemy may be for him to slide at it.").Value, YasupenSlideRange, Warn);
            YasupenSlideDamage = PlutoConfigRules.Clamp("YasupenSlideDamage", cfg.Bind(S, "YasupenSlideDamage", YasupenSlideDamage, "Yasupen: damage his belly slide deals to each enemy it hits.").Value, YasupenSlideDamage, Warn);
            YasupenSlideKnockback = PlutoConfigRules.Clamp("YasupenSlideKnockback", cfg.Bind(S, "YasupenSlideKnockback", YasupenSlideKnockback, "Yasupen: knockback of the belly slide (bosses are never knocked back).").Value, YasupenSlideKnockback, Warn);
            YasupenShopDiscount = PlutoConfigRules.Clamp("YasupenShopDiscount", cfg.Bind(S, "YasupenShopDiscount", YasupenShopDiscount, "Yasupen: shop discount while he is with you (0.1 = 10 % off, at most 0.5).").Value, YasupenShopDiscount, Warn);
            YasupenBargainChance = PlutoConfigRules.Clamp("YasupenBargainChance", cfg.Bind(S, "YasupenBargainChance", YasupenBargainChance, "Yasupen: chance (0-1) after a room is cleared that he finds a miracle bargain of 3-5 casings.").Value, YasupenBargainChance, Warn);
        }

        private static void BindCatSet(ConfigFile cfg)
        {
            const string S = "Cat Set 2.19";
            SprayClip = PlutoConfigRules.Clamp("SprayClip", cfg.Bind(S, "SprayClip", SprayClip, "Spray Bottle: shots per clip.").Value, SprayClip, Warn);
            SprayCooldown = PlutoConfigRules.Clamp("SprayCooldown", cfg.Bind(S, "SprayCooldown", SprayCooldown, "Spray Bottle: seconds between sprays.").Value, SprayCooldown, Warn);
            SprayRange = PlutoConfigRules.Clamp("SprayRange", cfg.Bind(S, "SprayRange", SprayRange, "Spray Bottle: mist range in tiles.").Value, SprayRange, Warn);
            SprayDamage = PlutoConfigRules.Clamp("SprayDamage", cfg.Bind(S, "SprayDamage", SprayDamage, "Spray Bottle: damage per mist hit.").Value, SprayDamage, Warn);
            SprayKnockback = PlutoConfigRules.Clamp("SprayKnockback", cfg.Bind(S, "SprayKnockback", SprayKnockback, "Spray Bottle: knockback per mist hit.").Value, SprayKnockback, Warn);
            SprayFlinchChance = PlutoConfigRules.Clamp("SprayFlinchChance", cfg.Bind(S, "SprayFlinchChance", SprayFlinchChance, "Spray Bottle: chance (0-1) to flinch an enemy.").Value, SprayFlinchChance, Warn);
            SprayFlinchSeconds = PlutoConfigRules.Clamp("SprayFlinchSeconds", cfg.Bind(S, "SprayFlinchSeconds", SprayFlinchSeconds, "Spray Bottle: flinch duration in seconds.").Value, SprayFlinchSeconds, Warn);
            SprayReloadSeconds = PlutoConfigRules.Clamp("SprayReloadSeconds", cfg.Bind(S, "SprayReloadSeconds", SprayReloadSeconds, "Spray Bottle: reload duration in seconds.").Value, SprayReloadSeconds, Warn);
            SprayCharmBonusSeconds = PlutoConfigRules.Clamp("SprayCharmBonusSeconds", cfg.Bind(S, "SprayCharmBonusSeconds", SprayCharmBonusSeconds, "Bath Time: charm duration added by the Spray Bottle.").Value, SprayCharmBonusSeconds, Warn);
            FeatherChargeSeconds = PlutoConfigRules.Clamp("FeatherChargeSeconds", cfg.Bind(S, "FeatherChargeSeconds", FeatherChargeSeconds, "Feather Teaser: charge duration in seconds.").Value, FeatherChargeSeconds, Warn);
            FeatherClip = PlutoConfigRules.Clamp("FeatherClip", cfg.Bind(S, "FeatherClip", FeatherClip, "Feather Teaser: shots per clip.").Value, FeatherClip, Warn);
            FeatherRange = PlutoConfigRules.Clamp("FeatherRange", cfg.Bind(S, "FeatherRange", FeatherRange, "Feather Teaser: flight range in tiles.").Value, FeatherRange, Warn);
            FeatherDamage = PlutoConfigRules.Clamp("FeatherDamage", cfg.Bind(S, "FeatherDamage", FeatherDamage, "Feather Teaser: damage on each flight leg.").Value, FeatherDamage, Warn);
            FeatherDistractSeconds = PlutoConfigRules.Clamp("FeatherDistractSeconds", cfg.Bind(S, "FeatherDistractSeconds", FeatherDistractSeconds, "Feather Teaser: normal-enemy distraction duration.").Value, FeatherDistractSeconds, Warn);
            FeatherBossSlowSeconds = PlutoConfigRules.Clamp("FeatherBossSlowSeconds", cfg.Bind(S, "FeatherBossSlowSeconds", FeatherBossSlowSeconds, "Feather Teaser: boss slowdown duration.").Value, FeatherBossSlowSeconds, Warn);
            FeatherReloadSeconds = PlutoConfigRules.Clamp("FeatherReloadSeconds", cfg.Bind(S, "FeatherReloadSeconds", FeatherReloadSeconds, "Feather Teaser: reload duration in seconds.").Value, FeatherReloadSeconds, Warn);
            TPRechargeDamage = PlutoConfigRules.Clamp("TPRechargeDamage", cfg.Bind(S, "TPRechargeDamage", TPRechargeDamage, "Toilet Paper Roll: damage dealt to recharge it.").Value, TPRechargeDamage, Warn);
            TPLength = PlutoConfigRules.Clamp("TPLength", cfg.Bind(S, "TPLength", TPLength, "Toilet Paper Roll: streamer length in tiles.").Value, TPLength, Warn);
            TPSeconds = PlutoConfigRules.Clamp("TPSeconds", cfg.Bind(S, "TPSeconds", TPSeconds, "Toilet Paper Roll: streamer lifetime in seconds.").Value, TPSeconds, Warn);
            TPHits = PlutoConfigRules.Clamp("TPHits", cfg.Bind(S, "TPHits", TPHits, "Toilet Paper Roll: bullets the streamer blocks.").Value, TPHits, Warn);
            TPConfettiDamage = PlutoConfigRules.Clamp("TPConfettiDamage", cfg.Bind(S, "TPConfettiDamage", TPConfettiDamage, "Shredder: confetti damage.").Value, TPConfettiDamage, Warn);
            ConeCooldown = PlutoConfigRules.Clamp("ConeCooldown", cfg.Bind(S, "ConeCooldown", ConeCooldown, "Cone of Shame: seconds between bullet blocks.").Value, ConeCooldown, Warn);
            ConeArcDegrees = PlutoConfigRules.Clamp("ConeArcDegrees", cfg.Bind(S, "ConeArcDegrees", ConeArcDegrees, "Cone of Shame: full blocking arc in degrees.").Value, ConeArcDegrees, Warn);
            ConeRadius = PlutoConfigRules.Clamp("ConeRadius", cfg.Bind(S, "ConeRadius", ConeRadius, "Cone of Shame: blocking radius in tiles.").Value, ConeRadius, Warn);
            ConeCocoStuffing = PlutoConfigRules.Clamp("ConeCocoStuffing", cfg.Bind(S, "ConeCocoStuffing", ConeCocoStuffing, "Matching Cones: extra stuffing for Coco.").Value, ConeCocoStuffing, Warn);
            CoffeeRechargeDamage = PlutoConfigRules.Clamp("CoffeeRechargeDamage", cfg.Bind(S, "CoffeeRechargeDamage", CoffeeRechargeDamage, "Coffee Mug: damage dealt to recharge it.").Value, CoffeeRechargeDamage, Warn);
            CoffeeRange = PlutoConfigRules.Clamp("CoffeeRange", cfg.Bind(S, "CoffeeRange", CoffeeRange, "Coffee Mug: throw range in tiles.").Value, CoffeeRange, Warn);
            CoffeeShardCount = PlutoConfigRules.Clamp("CoffeeShardCount", cfg.Bind(S, "CoffeeShardCount", CoffeeShardCount, "Coffee Mug: shards in the impact ring.").Value, CoffeeShardCount, Warn);
            CoffeeShardDamage = PlutoConfigRules.Clamp("CoffeeShardDamage", cfg.Bind(S, "CoffeeShardDamage", CoffeeShardDamage, "Coffee Mug: damage per shard.").Value, CoffeeShardDamage, Warn);
            CoffeeSlowSeconds = PlutoConfigRules.Clamp("CoffeeSlowSeconds", cfg.Bind(S, "CoffeeSlowSeconds", CoffeeSlowSeconds, "Coffee Mug: coffee puddle slowdown duration.").Value, CoffeeSlowSeconds, Warn);
            CoffeeZoomiesBonusSeconds = PlutoConfigRules.Clamp("CoffeeZoomiesBonusSeconds", cfg.Bind(S, "CoffeeZoomiesBonusSeconds", CoffeeZoomiesBonusSeconds, "Espresso: zoomies duration added by coffee.").Value, CoffeeZoomiesBonusSeconds, Warn);
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
