using System;
using PlutoTheCat;
class CatItemCases
{
    static int count;
    static void Check(bool ok, string label) { if (!ok) throw new Exception(label); count++; }
    static bool Near(float a, float b) { return Math.Abs(a - b) < 0.0001f; }
    static void Main()
    {
        // Ball of Yarn: no re-tangle until the first (stun + slow) wears off.
        Check(!CatItemRules.CanTangle(2f, 1.5f, 3f) && CatItemRules.CanTangle(4.5f, 1.5f, 3f) && CatItemRules.CanTangle(float.NaN, 1.5f, 3f), "re-tangle waits");

        // Catnip Pouch: zoomies, catnap, done.
        Check(CatItemRules.Catnip(0f, 7f, 2f) == CatItemRules.CatnipPhase.Zoomies && CatItemRules.Catnip(6.9f, 7f, 2f) == CatItemRules.CatnipPhase.Zoomies, "zoomies first");
        Check(CatItemRules.Catnip(7f, 7f, 2f) == CatItemRules.CatnipPhase.Catnap && CatItemRules.Catnip(8.9f, 7f, 2f) == CatItemRules.CatnipPhase.Catnap, "catnap after");
        Check(CatItemRules.Catnip(9f, 7f, 2f) == CatItemRules.CatnipPhase.Done && CatItemRules.Catnip(7f, 7f, 0f) == CatItemRules.CatnipPhase.Done, "done; catnap 0 skips it");
        Check(CatItemRules.Catnip(-1f, 7f, 2f) == CatItemRules.CatnipPhase.Done, "not started is done");

        // Jingle Bell Collar: first roll jingles, cooldown after.
        Check(CatItemRules.BellReady(0.2f, float.NegativeInfinity, 4f), "first roll jingles");
        Check(!CatItemRules.BellReady(13.9f, 10f, 4f) && CatItemRules.BellReady(14f, 10f, 4f), "cooldown between jingles");
        Check(CatItemRules.BellReady(10f, 10f, 0f), "cooldown 0 jingles every roll");

        // Ranges: edge counts, zero radius never.
        Check(CatItemRules.Inside(6.25f, 2.5f) && !CatItemRules.Inside(6.26f, 2.5f) && !CatItemRules.Inside(0f, 0f), "radius check");

        // Hairball cloud: slows, never speeds up, never freezes a bullet in place.
        Check(Near(CatItemRules.CloudBulletSpeed(20f, 20f, 0.35f), 7f), "slowed to the factor");
        Check(Near(CatItemRules.CloudBulletSpeed(20f, 5f, 0.35f), 5f), "an already slower bullet keeps its speed");
        Check(Near(CatItemRules.CloudBulletSpeed(2f, 2f, 0.05f), 1f), "slow bullets still crawl out");
        Check(Near(CatItemRules.CloudBulletSpeed(0.5f, 0.5f, 0.35f), 0.5f), "a bullet slower than a crawl is untouched");
        Check(CatItemRules.CloudVisualScale(3f) == 1f && Near(CatItemRules.CloudVisualScale(0.5f), 0.8f) && CatItemRules.CloudVisualScale(0f) == 0f, "cloud thins at the end");

        // Scratching Post.
        Check(CatItemRules.Sharpened(true, 4f, 2.5f) && !CatItemRules.Sharpened(false, 4f, 2.5f) && !CatItemRules.Sharpened(true, 9f, 2.5f), "near a standing post");

        Console.WriteLine(count + " cat item cases passed");
    }
}
