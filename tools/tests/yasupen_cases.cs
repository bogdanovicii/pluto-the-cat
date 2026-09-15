using System;
using PlutoTheCat;
class YasupenCases
{
    static int count;
    static void Check(bool ok, string label) { if (!ok) throw new Exception(label); count++; }
    static bool Near(float a, float b) { return Math.Abs(a - b) < 0.0001f; }
    static void Main()
    {
        // Slide: only in combat, only with an enemy in range, only after the cooldown; the first slide is ready.
        Check(YasupenRules.SlideReady(0.1f, float.NegativeInfinity, 5f, true, 3f, 6f), "first slide ready");
        Check(!YasupenRules.SlideReady(14.9f, 10f, 5f, true, 3f, 6f) && YasupenRules.SlideReady(15f, 10f, 5f, true, 3f, 6f), "cooldown");
        Check(!YasupenRules.SlideReady(99f, 0f, 5f, false, 3f, 6f), "not in combat");
        Check(!YasupenRules.SlideReady(99f, 0f, 5f, true, 6.01f, 6f) && YasupenRules.SlideReady(99f, 0f, 5f, true, 6f, 6f), "range edge");
        Check(!YasupenRules.SlideReady(99f, 0f, 5f, true, float.NaN, 6f), "no enemy");

        // Bargain: roll under the chance drops 3-5 casings, otherwise nothing.
        Check(YasupenRules.BargainCasings(0.19f, 0.2f, 0f) == 3 && YasupenRules.BargainCasings(0.19f, 0.2f, 0.999f) == 5, "3 to 5");
        Check(YasupenRules.BargainCasings(0.5f, 0.2f, 0.5f) == 0, "over the chance drops none");
        Check(YasupenRules.BargainCasings(0f, 0f, 0.5f) == 0, "chance 0 never drops");
        Check(YasupenRules.BargainCasings(0.99f, 1f, 1f) == 5, "chance 1 always drops, amount roll 1 caps at 5");

        // Price: 10 % off is 0.9; discounts are clamped so a bad config cannot make shops free.
        Check(Near(YasupenRules.PriceMultiplier(0.1f), 0.9f), "10 % off");
        Check(Near(YasupenRules.PriceMultiplier(-1f), 1f) && Near(YasupenRules.PriceMultiplier(0.9f), 0.5f), "clamped 0..0.5");
        Check(Near(YasupenRules.PriceMultiplier(float.NaN), 1f), "NaN is no discount");

        Console.WriteLine(count + " yasupen cases passed");
    }
}
