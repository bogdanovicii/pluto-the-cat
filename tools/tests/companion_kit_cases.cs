using System;
using PlutoTheCat;
class CompanionKitCases
{
    static int count;
    static void Check(bool ok, string label) { if (!ok) throw new Exception(label); count++; }
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
        Console.WriteLine(count + " companion behavior cases passed");
    }
}
