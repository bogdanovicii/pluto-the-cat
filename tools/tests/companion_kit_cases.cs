using System;
using PlutoTheCat;
class CompanionKitCases
{
    static int count;
    static void Check(bool ok, string label) { if (!ok) throw new Exception(label); count++; }
    static float Dist(float ax, float ay, float bx, float by) { return (float)Math.Sqrt((ax - bx) * (ax - bx) + (ay - by) * (ay - by)); }
    static void Main()
    {
        var charges = new CocoShieldCharges(2);
        object first = new object(), second = new object();
        Check(charges.TryBlock(first) && charges.Remaining == 1, "first projectile consumes stuffing");
        Check(!charges.TryBlock(first) && charges.Remaining == 1, "duplicate collision consumes once");
        Check(charges.TryBlock(second) && charges.Remaining == 0, "simultaneous second projectile consumes final stuffing");
        Check(!charges.TryBlock(new object()), "empty shield passes subsequent bullets");
        charges.Refill(2);
        Check(charges.TryBlock(new object()) && charges.Remaining == 1, "recover resets shield");
        var owned = new CompanionOwnedValue<string>();
        owned.Record("original", "coco");
        Check(owned.Restore("coco") == "original", "restore original target");
        owned.Record("original", "coco");
        Check(owned.Restore("charm") == "charm", "preserve newer override");
        owned.Record("original", "coco"); owned.Record("coco", "new chaser");
        Check(owned.Restore("new chaser") == "original", "retarget retains original");
        owned.Record("original", "coco");
        Check(!owned.CanWrite("charm"), "do not reclaim externally replaced target");
        owned.Restore("charm");
        owned.Record(null, "chaser");
        Check(owned.Restore("chaser") == null, "restore an empty original target");
        var seen = new CompanionOwnedValue<int>();
        seen.Observe(1, 1);
        Check(seen.Restore(1) == 1, "unchanged field is not claimed");
        seen.Observe(1, 5);
        Check(seen.Restore(5) == 1, "restore a field our behaviour changed");
        seen.Observe(1, 5);
        Check(seen.Restore(7) == 7, "keep a newer outside change");
        seen.Observe(1, 5); seen.Observe(1, 1);
        Check(seen.Restore(1) == 1, "field already back at its original stays");
        Check(seen.Restore(5) == 5, "restore without ownership leaves the field alone");
        Check(CompanionKitRules.ProjectileRisk(3, 0, -6, 0, 0.8f) > CompanionKitRules.ProjectileRisk(3, 0, 6, 0, 0.8f), "incoming outranks receding bullet");
        Check(CompanionKitRules.ProjectileRisk(3, 0, -6, 0, 0.8f) > CompanionKitRules.ProjectileRisk(3, 3, -6, 0, 0.8f), "near miss safer than collision course");
        Check(CompanionKitRules.ProjectileRisk(3, 0, 0, 0, 0.8f) == 0, "distant stationary shot harmless");
        Check(CompanionKitRules.ProjectileRisk(0.1f, 0, 0, 0, 0.8f) > 0, "overlap unsafe even when stationary");
        Check(!CompanionKitRules.CanCollectCrumb(true, 4, 10), "infinite gun cannot waste crumb");
        Check(!CompanionKitRules.CanCollectCrumb(false, 10, 10), "full gun cannot waste crumb");
        Check(CompanionKitRules.CanCollectCrumb(false, 9, 10), "finite gun gains ammo");
        Check(CompanionKitRules.CanDropCrumb(true, true, 11) && !CompanionKitRules.CanDropCrumb(true, true, 12), "owner live crumb cap");
        Check(!CompanionKitRules.CanDropCrumb(false, true, 0) && !CompanionKitRules.CanDropCrumb(true, false, 0), "crumb requires earned hit and owner");
        // Decoy run (2.16.3 regression: "stay" won every tie, so a decoy Coco with nothing shooting at him stood still).
        float[] xs = new float[CompanionKitRules.DecoyCandidateCount], ys = new float[CompanionKitRules.DecoyCandidateCount];
        float[] calm = new float[CompanionKitRules.DecoyCandidateCount], jitter = new float[CompanionKitRules.DecoyCandidateCount];
        CompanionKitRules.DecoyCandidates(2.5f, 0f, 0f, 0f, 0f, 3f, xs, ys);
        int leg = CompanionKitRules.PickDecoyLeg(2.5f, 0f, 0f, 0f, xs, ys, calm, jitter);
        Check(leg >= 0, "no threats still produces a target");
        Check(Dist(2.5f, 0f, xs[leg], ys[leg]) >= CompanionKitRules.DecoyMinStep, "no threats still produces a moving target");
        for (int i = 0; i < xs.Length; i++)
            Check(Dist(2.5f, 0f, xs[i], ys[i]) >= CompanionKitRules.DecoyMinStep || CompanionKitRules.DecoyLegScore(2.5f, 0f, xs[i], ys[i], 0f, 0f, 0f, 0f) == float.MaxValue,
                "standing still is never a candidate leg");
        float[] threat = new float[CompanionKitRules.DecoyCandidateCount];
        for (int i = 0; i < threat.Length; i++) threat[i] = 20f;
        int safe = (leg + 3) % threat.Length;
        threat[safe] = 0f;
        Check(CompanionKitRules.PickDecoyLeg(2.5f, 0f, 0f, 0f, xs, ys, threat, jitter) == safe, "prefers the leg away from incoming bullets");
        Check(CompanionKitRules.DecoyLegScore(7.5f, 0f, 10.5f, 0f, 0f, 0f, 0f, 0f) == float.MaxValue, "leash: never run further past 8 tiles from the owner");
        Check(CompanionKitRules.DecoyLegScore(9f, 0f, 6f, 0f, 0f, 0f, 0f, 0f) < float.MaxValue, "leash: running back toward the owner is allowed");
        Check(CompanionKitRules.DecoyLegScore(3f, 0f, 6f, 0f, 0f, 0f, 0f, 0f) > CompanionKitRules.DecoyLegScore(3f, 0f, 0f, 3f, 0f, 0f, 0f, 0f), "prefers staying within reach of the owner");
        Check(CompanionKitRules.PickDecoyLeg(7.9f, 0f, 0f, 0f, new float[] { 7.9f }, new float[] { 0f }, new float[1], new float[1]) == -1, "no allowed leg reports none");
        Check(CompanionKitRules.NeedsNewDecoyLeg(false, 0f, 0f, 1f, 0f, 0f), "no leg yet: pick one");
        Check(CompanionKitRules.NeedsNewDecoyLeg(true, 0.3f, 0.5f, 1f, 0f, 0f), "arrived: run on at once");
        Check(!CompanionKitRules.NeedsNewDecoyLeg(true, 2f, 0.5f, 1f, 0f, 0f), "mid-leg and safe: keep running");
        Check(CompanionKitRules.NeedsNewDecoyLeg(true, 2f, 0.5f, 0.01f, 0f, 0f), "stalled against something: pick another leg");
        Check(CompanionKitRules.NeedsNewDecoyLeg(true, 2f, 5f, 1f, 0f, 0f), "a leg never lasts long enough to stand around");
        Check(CompanionKitRules.NeedsNewDecoyLeg(true, 2f, 0.5f, 1f, 15f, 2f), "a bullet crossing the current leg forces a swerve");
        Check(!CompanionKitRules.NeedsNewDecoyLeg(true, 2f, 0.5f, 1f, 3f, 2f), "a slightly better leg does not cause jitter");
        // Squire helmet: grey pot helmet for every Junkan form below Holy Knight, the gold plumed helmet from Holy Knight up.
        Check(CompanionKitRules.CocoHelmetPrefix(false, 7) == "", "no Squire: no helmet");
        Check(CompanionKitRules.CocoHelmetPrefix(true, 0) == "squire_", "Peasant Junkan: pot helmet");
        Check(CompanionKitRules.CocoHelmetPrefix(true, 5) == "squire_", "Knight Commander: pot helmet");
        Check(CompanionKitRules.CocoHelmetPrefix(true, 6) == "knight_" && CompanionKitRules.CocoHelmetPrefix(true, 7) == "knight_", "Holy and Angelic Knight: gold helmet");
        Check(CompanionKitRules.CocoHelmetPrefix(true, 8) == "knight_", "Mecha Junkan: gold helmet");
        Console.WriteLine(count + " companion behavior cases passed");
    }
}
