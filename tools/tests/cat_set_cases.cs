using System;
using PlutoTheCat;

class CatSetCases
{
    static int count;
    static void Check(bool ok, string label) { if (!ok) throw new Exception(label); count++; }
    static bool Near(float a, float b) { return Math.Abs(a - b) < 0.0001f; }

    static void Main()
    {
        Check(CatSetRules.RollFlinch(0.349f, 0.35f), "roll below chance flinches");
        Check(!CatSetRules.RollFlinch(0.35f, 0.35f), "roll at chance does not flinch");
        Check(!CatSetRules.RollFlinch(float.NaN, 0.35f), "NaN roll does not flinch");

        Check(Near(CatSetRules.DistractSeconds(false, 1.5f, 0.5f), 1.5f), "normal distract duration");
        Check(Near(CatSetRules.DistractSeconds(true, 1.5f, 0.5f), 0.5f), "boss distract duration");

        Check(CatSetRules.StreamerAlive(4.999f, 0f, 5f, 11, 12), "streamer alive before expiry and hit cap");
        Check(!CatSetRules.StreamerAlive(5f, 0f, 5f, 11, 12), "streamer expires at duration");
        Check(!CatSetRules.StreamerAlive(4.999f, 0f, 5f, 12, 12), "streamer expires at hit cap");

        Check(CatSetRules.ConeReady(0f, float.NegativeInfinity, 3f), "cone ready on first use");
        Check(!CatSetRules.ConeReady(2.99f, 0f, 3f), "cone waits for cooldown");
        Check(CatSetRules.ConeReady(3f, 0f, 3f), "cone ready at cooldown boundary");

        Check(CatSetRules.InCone(1f, 0f, 1f, 0f, 1.5f, 70f), "cone center");
        float plus35 = 35f * (float)Math.PI / 180f;
        float minus35 = -35f * (float)Math.PI / 180f;
        float plus3501 = 35.01f * (float)Math.PI / 180f;
        Check(CatSetRules.InCone((float)Math.Cos(plus35), (float)Math.Sin(plus35), 1f, 0f, 1.5f, 70f), "positive half-angle is inclusive");
        Check(CatSetRules.InCone((float)Math.Cos(minus35), (float)Math.Sin(minus35), 1f, 0f, 1.5f, 70f), "negative half-angle is inclusive");
        Check(!CatSetRules.InCone((float)Math.Cos(plus3501), (float)Math.Sin(plus3501), 1f, 0f, 1.5f, 70f), "outside half-angle");
        Check(!CatSetRules.InCone(-1f, 0f, 1f, 0f, 1.5f, 70f), "behind cone");
        Check(!CatSetRules.InCone(1.51f, 0f, 1f, 0f, 1.5f, 70f), "outside cone radius");
        Check(!CatSetRules.InCone(float.NaN, 0f, 1f, 0f, 1.5f, 70f), "NaN rejected");
        Check(!CatSetRules.InCone(1f, 0f, 1f, 0f, float.NaN, 70f), "NaN radius rejected");
        Check(!CatSetRules.InCone(1f, 0f, 1f, 0f, 1.5f, float.NaN), "NaN angle rejected");
        Check(!CatSetRules.InCone(1f, 0f, 1f, 0f, 0f, 70f), "nonpositive radius rejected");
        Check(!CatSetRules.InCone(1f, 0f, 1f, 0f, 1.5f, 0f), "nonpositive angle rejected");
        Check(!CatSetRules.InCone(0f, 0f, 1f, 0f, 1.5f, 70f), "zero offset rejected");
        Check(!CatSetRules.InCone(1f, 0f, 0f, 0f, 1.5f, 70f), "zero aim rejected");

        for (int i = 0; i < 10; i++)
            Check(Near(CatSetRules.ShardAngle(i, 10), 36f * i), "shard angle " + i);
        Check(Near(CatSetRules.ShardAngle(5, 0), 0f), "nonpositive shard count has zero angle");

        float extended = CatSetRules.ExtendDuration(10f, 2f);
        Check(Near(extended, 12f), "duration gains bonus");
        foreach (float elapsed in new float[] { 0f, 0.5f, 2f })
            Check(Near((extended - elapsed) - (10f - elapsed), 2f), "duration gain remains exactly two at elapsed " + elapsed);
        Check(Near(CatSetRules.ExtendDuration(extended, 2f), 14f), "repeated duration extension stacks");
        Check(Near(CatSetRules.ExtendRemaining(3f, 2f, true), 5f), "active remaining time extends");
        Check(Near(CatSetRules.ExtendRemaining(3f, 2f, false), 3f), "inactive remaining time stays unchanged");

        Console.WriteLine(count + " cat set cases passed");
    }
}
