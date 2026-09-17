using System;
using PlutoTheCat;

class ShrineStallCases
{
    static int count;
    static void Check(bool ok, string label) { if (!ok) throw new Exception(label); count++; }

    static void Main()
    {
        string[] ids = { "pluto:coffee_mug", "pluto:cone_of_shame" };
        int[] prices = { 8, 15 };
        Check(ShrineStallRules.Price("pluto:coffee_mug", prices, ids) == 8, "C item price");
        Check(ShrineStallRules.Price("pluto:cone_of_shame", prices, ids) == 15, "B item price");
        Check(ShrineStallRules.Price("pluto:nope", prices, ids) == 0, "unknown id has no price");
        Check(ShrineStallRules.Price(null, prices, ids) == 0, "null id has no price");

        Check(ShrineStallRules.FlagName("pluto:coffee_mug") == "PLUTO_UNLOCK_COFFEE_MUG", "flag name");
        Check(ShrineStallRules.FlagName("pluto:ball_of_yarn") == "PLUTO_UNLOCK_BALL_OF_YARN", "flag name underscores");
        Check(ShrineStallRules.MirrorKey("pluto:coffee_mug") == "bogdan.etg.plutothecat:coffee_mug", "mirror key");

        Check(!ShrineStallRules.Unlocked(false, false, false), "locked by default");
        Check(ShrineStallRules.Unlocked(true, false, false), "flag unlocks");
        Check(ShrineStallRules.Unlocked(false, true, false), "mirror unlocks when the flag id drifted");
        Check(ShrineStallRules.Unlocked(false, false, true), "disabled config unlocks everything");

        Console.WriteLine(count + " shrine stall cases passed");
    }
}
