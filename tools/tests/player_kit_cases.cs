using System;
using System.Collections.Generic;
using PlutoTheCat;
class PlayerKitCases
{
    static int count;
    static void Check(bool ok, string label) { if (!ok) throw new Exception(label); count++; }
    static bool Near(float a, float b) { return Math.Abs(a - b) < 0.0001f; }
    static void Main()
    {
        // Nine Lives: remaining saves and the story-toned status line.
        Check(NineLivesRules.SavesLeft(7) == 2 && NineLivesRules.SavesLeft(9) == 0 && NineLivesRules.SavesLeft(1) == 8, "saves left per life");
        Check(NineLivesRules.SavesLeft(0) == 8 && NineLivesRules.SavesLeft(12) == 0, "out-of-range life clamps");
        Check(NineLivesRules.Title(7) == "Seventh Life" && NineLivesRules.Title(9) == "Ninth Life", "item subtitle names the life");
        Check(NineLivesRules.Status(7) == "Seventh life. Two to spare.", "two saves status");
        Check(NineLivesRules.Status(8) == "Eighth life. One to spare.", "one save status");
        Check(NineLivesRules.Status(9) == "Ninth life. The last one.", "no saves status keeps the old line");
        Check(NineLivesRules.Status(1) == "First life. Eight to spare.", "config life 1 status");

        // Samurai anger cue: opening flash, bounded pulse, fade before calming down.
        float opening = AngerCueRules.TintAlpha(0f, 6f);
        float mid = AngerCueRules.TintAlpha(2.3f, 3.7f);
        Check(opening > mid, "hit flash is stronger than the pulse");
        Check(mid >= AngerCueRules.PulseMin - 0.0001f && mid <= AngerCueRules.PulseMax + 0.0001f, "pulse stays in its band");
        Check(AngerCueRules.TintAlpha(2.3f, 0f) == 0f, "no tint once calm");
        Check(AngerCueRules.TintAlpha(2.3f, 0.1f) < AngerCueRules.TintAlpha(2.3f, 1f), "tint fades out at the end");
        bool bounded = true;
        for (float t = 0f; t < 8f; t += 0.037f) { float a = AngerCueRules.TintAlpha(t, 8f - t); if (a < 0f || a > AngerCueRules.FlashAlpha) bounded = false; }
        Check(bounded, "tint alpha never exceeds the flash");
        Check(AngerCueRules.TintAlpha(float.NaN, 3f) == 0f, "invalid time draws nothing");
        bool spawn;
        float timer = AngerCueRules.NextMarkTimer(AngerCueRules.MarkInterval, 0.5f, out spawn);
        Check(!spawn && Near(timer, AngerCueRules.MarkInterval - 0.5f), "marks wait for the interval");
        timer = AngerCueRules.NextMarkTimer(timer, 0.5f, out spawn);
        Check(spawn && timer > 0f, "marks repeat after the interval");
        timer = AngerCueRules.NextMarkTimer(0.1f, 5f, out spawn);
        Check(spawn && Near(timer, AngerCueRules.MarkInterval), "a long frame spawns one mark, not a burst");

        // Config: clamp at bind time, warn, keep shipped defaults valid.
        var warnings = new List<string>();
        Action<string> warn = warnings.Add;
        Check(PlutoConfigRules.Clamp("KibbleCritChance", 1.5f, 0.05f, warn) == 1f && warnings.Count == 1, "probability capped at 1");
        Check(warnings[0].Contains("KibbleCritChance"), "warning names the setting");
        Check(PlutoConfigRules.Clamp("KibbleCritChance", 0.05f, 0.05f, warn) == 0.05f && warnings.Count == 1, "valid value passes silently");
        Check(PlutoConfigRules.Clamp("StartingLife", 0, 7, warn) == 1 && PlutoConfigRules.Clamp("StartingLife", 12, 7, warn) == 9, "life range 1-9");
        Check(PlutoConfigRules.Clamp("KibbleDamage", -3f, 3.5f, warn) > 0f, "damage stays positive");
        Check(PlutoConfigRules.Clamp("CocoStuffing", 0, 8, warn) == 1 && PlutoConfigRules.Clamp("KibbleClip", -5, 10, warn) == 1, "counts at least one");
        Check(PlutoConfigRules.Clamp("DecoyCooldownDamage", 0f, 150f, warn) > 0f && PlutoConfigRules.Clamp("CocoStuffingRegenSeconds", 0f, 4f, warn) > 0f, "cooldowns positive");
        Check(PlutoConfigRules.Clamp("InvulnerableRollFrames", 20, 6, warn) == 9, "roll frames bounded by the clip");
        int before = warnings.Count;
        Check(PlutoConfigRules.Clamp("KibbleDamage", float.NaN, 3.5f, warn) == 3.5f && PlutoConfigRules.Clamp("CanDamage", float.PositiveInfinity, 5f, warn) == 5f, "non-numbers use the default");
        Check(warnings.Count == before + 2, "non-numbers warn");
        before = warnings.Count;
        Check(PlutoConfigRules.Clamp("TailWhipDamage", 0f, 6f, warn) == 0f && PlutoConfigRules.Clamp("AngrySeconds", 0f, 6f, warn) == 0f
              && PlutoConfigRules.Clamp("ZoomiesSeconds", 0f, 4f, warn) == 0f && warnings.Count == before, "documented 0 = disabled stays allowed");
        bool threw = false;
        try { PlutoConfigRules.Clamp("NoSuchSetting", 1f, 1f, warn); } catch (ArgumentException) { threw = true; }
        Check(threw, "unknown key is a programming error");

        var defaults = new Dictionary<string, double> {
            {"StartingLife", 7}, {"KibbleDamage", 3.5}, {"KibbleClip", 10}, {"KibbleCritChance", 0.05}, {"TaiyakiDamage", 8}, {"TaiyakiClip", 10},
            {"SecretDoorDamage", 15}, {"CanSplashRadius", 2}, {"CanDamage", 5}, {"CharmDuration", 10}, {"BossStunSeconds", 3},
            {"CanCooldownDamage", 200}, {"TailWhipDamage", 6}, {"ZoomiesSeconds", 4}, {"ZoomiesSpeedBonus", 2.5}, {"InvulnerableRollFrames", 6},
            {"AngrySeconds", 6}, {"AngryDamageMultiplier", 1.5}, {"AngryFireRateMultiplier", 1.3}, {"AngryScale", 1}, {"MaxSpeedBonus", 4},
            {"DecoySeconds", 8}, {"DecoyCooldownDamage", 150}, {"CocoStuffing", 8}, {"CocoKnockoutSeconds", 10}, {"CocoStuffingRegenSeconds", 4},
            // 2.17 cat items
            {"YarnSeconds", 6}, {"YarnDamage", 4}, {"YarnTangleSeconds", 1.5}, {"YarnSlowSeconds", 3}, {"YarnCooldownDamage", 300},
            {"CatnipSeconds", 7}, {"CatnipSpeedBonus", 2}, {"CatnipFireRateMultiplier", 1.25}, {"CatnapSeconds", 2}, {"CatnipCooldownDamage", 450},
            {"BellRadius", 2.5}, {"BellCooldownSeconds", 4}, {"BellStunSeconds", 1},
            {"HairballItemRadius", 3}, {"HairballItemSeconds", 5}, {"HairballItemBulletSpeed", 0.35}, {"HairballItemCooldownDamage", 350},
            {"PostRadius", 2.5}, {"PostDamageMultiplier", 1.3}, {"PostPierce", 1},
            // 2.18 Yasupen
            {"YasupenSlideCooldown", 5}, {"YasupenSlideRange", 6}, {"YasupenSlideDamage", 8}, {"YasupenSlideKnockback", 30}, {"YasupenShopDiscount", 0.1}, {"YasupenBargainChance", 0.2},
            // 2.19 cat set
            {"SprayClip", 8}, {"SprayCooldown", 0.35}, {"SprayRange", 6}, {"SprayDamage", 4}, {"SprayKnockback", 25},
            {"SprayFlinchChance", 0.35}, {"SprayFlinchSeconds", 0.5}, {"SprayReloadSeconds", 1}, {"SprayCharmBonusSeconds", 2},
            {"SprayCharmMaxBonusSeconds", 6},
            {"FeatherChargeSeconds", 0.6}, {"FeatherClip", 1}, {"FeatherRange", 7}, {"FeatherDamage", 7},
            {"FeatherDistractSeconds", 1.5}, {"FeatherBossSlowSeconds", 0.5}, {"FeatherReloadSeconds", 0.4},
            {"TPRechargeDamage", 400}, {"TPLength", 4}, {"TPSeconds", 5}, {"TPHits", 12}, {"TPConfettiDamage", 10},
            {"ConeCooldown", 3}, {"ConeArcDegrees", 70}, {"ConeRadius", 1.5}, {"ConeCocoStuffing", 1},
            {"CoffeeRechargeDamage", 300}, {"CoffeeRange", 3}, {"CoffeeShardCount", 10}, {"CoffeeShardDamage", 5},
            {"CoffeeSlowSeconds", 3}, {"CoffeeZoomiesBonusSeconds", 2},
        };
        foreach (var d in defaults) Check(PlutoConfigRules.Contains(d.Key, d.Value), "default in range: " + d.Key);
        Check(PlutoConfigRules.Keys.Count == defaults.Count, "every ranged setting has a default case");

        Console.WriteLine(count + " player kit and config cases passed");
    }
}
