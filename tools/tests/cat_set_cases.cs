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

        // Oriented streamer-strip vs enemy hitbox AABB. Boundaries are inclusive and
        // a diagonal strip must not damage actors that only touch its enclosing world AABB.
        Check(CatSetRules.StreamerStripOverlapsAabb(0f, 0f, 1f, 0f, 4f, 0.375f,
            -0.2f, -0.1f, 0.2f, 0.1f), "horizontal strip crosses central hitbox");
        Check(CatSetRules.StreamerStripOverlapsAabb(0f, 0f, 1f, 0f, 4f, 0.375f,
            2f, -0.1f, 2.2f, 0.1f), "strip length boundary is inclusive");
        Check(!CatSetRules.StreamerStripOverlapsAabb(0f, 0f, 1f, 0f, 4f, 0.375f,
            2.001f, -0.1f, 2.2f, 0.1f), "outside strip length is rejected");
        Check(CatSetRules.StreamerStripOverlapsAabb(0f, 0f, 0f, 3f, 4f, 0.375f,
            -0.1f, 1.9f, 0.1f, 2.1f), "scaled vertical axis is normalized");
        float diagonal = (float)Math.Sqrt(0.5);
        Check(CatSetRules.StreamerStripOverlapsAabb(0f, 0f, diagonal, diagonal, 4f, 0.375f,
            0.9f, 0.9f, 1.1f, 1.1f), "diagonal strip crosses hitbox on its axis");
        Check(!CatSetRules.StreamerStripOverlapsAabb(0f, 0f, diagonal, diagonal, 4f, 0.375f,
            1.25f, -1.25f, 1.45f, -1.05f), "diagonal enclosing-AABB false positive is rejected");
        Check(CatSetRules.StreamerStripOverlapsAabb(12f, -7f, diagonal, -diagonal, 4f, 0.375f,
            11.9f, -7.1f, 12.1f, -6.9f), "translated rotated strip crosses hitbox");
        Check(CatSetRules.StreamerStripOverlapsAabb(0f, 0f, diagonal, diagonal, 4f, 0.375f,
            -10f, -10f, 10f, 10f), "large boss hitbox enclosing strip overlaps");
        Check(!CatSetRules.StreamerStripOverlapsAabb(0f, 0f, 0f, 0f, 4f, 0.375f,
            -1f, -1f, 1f, 1f), "zero strip axis rejected");
        Check(!CatSetRules.StreamerStripOverlapsAabb(0f, 0f, 1f, 0f, 0f, 0.375f,
            -1f, -1f, 1f, 1f), "zero strip length rejected");
        Check(!CatSetRules.StreamerStripOverlapsAabb(0f, 0f, 1f, 0f, 4f, 0f,
            -1f, -1f, 1f, 1f), "zero strip width rejected");
        Check(!CatSetRules.StreamerStripOverlapsAabb(float.NaN, 0f, 1f, 0f, 4f, 0.375f,
            -1f, -1f, 1f, 1f), "NaN strip data rejected");
        Check(!CatSetRules.StreamerStripOverlapsAabb(float.PositiveInfinity, 0f, 1f, 0f, 4f, 0.375f,
            -1f, -1f, 1f, 1f), "infinite strip data rejected");
        Check(!CatSetRules.StreamerStripOverlapsAabb(0f, 0f, 1f, 0f, 4f, 0.375f,
            1f, -1f, -1f, 1f), "inverted hitbox rejected");

        // Sweep all orientations through an on-axis box and reject an equally distant
        // box on the strip normal. This catches axis/sign/normalization mistakes.
        for (int degrees = 0; degrees < 360; degrees += 5)
        {
            float radians = degrees * (float)Math.PI / 180f;
            float axisX = (float)Math.Cos(radians);
            float axisY = (float)Math.Sin(radians);
            float onX = axisX * 1.4f, onY = axisY * 1.4f;
            Check(CatSetRules.StreamerStripOverlapsAabb(3f, -2f, axisX, axisY, 4f, 0.375f,
                3f + onX - 0.04f, -2f + onY - 0.04f, 3f + onX + 0.04f, -2f + onY + 0.04f),
                "orientation sweep on-axis " + degrees);
            float normalX = -axisY * 0.55f, normalY = axisX * 0.55f;
            Check(!CatSetRules.StreamerStripOverlapsAabb(3f, -2f, axisX, axisY, 4f, 0.375f,
                3f + normalX - 0.04f, -2f + normalY - 0.04f, 3f + normalX + 0.04f, -2f + normalY + 0.04f),
                "orientation sweep off-width " + degrees);
        }

        Check(CatSetRules.ConeReady(0f, float.NegativeInfinity, 3f), "cone ready on first use");
        Check(!CatSetRules.ConeReady(2.99f, 0f, 3f), "cone waits for cooldown");
        Check(CatSetRules.ConeReady(3f, 0f, 3f), "cone ready at cooldown boundary");

        Check(CatSetRules.InCone(1f, 0f, 1f, 0f, 1.5f, 70f), "cone center");
        float plus35 = 35f * (float)Math.PI / 180f;
        float minus35 = -35f * (float)Math.PI / 180f;
        float plus3501 = 35.01f * (float)Math.PI / 180f;
        Check(CatSetRules.InCone((float)Math.Cos(plus35), (float)Math.Sin(plus35), 1f, 0f, 1.5f, 70f), "positive half-angle is inclusive");
        Check(CatSetRules.InCone((float)Math.Cos(minus35), (float)Math.Sin(minus35), 1f, 0f, 1.5f, 70f), "negative half-angle is inclusive");
        Check(CatSetRules.InCone(1.5f * (float)Math.Cos(plus35), 1.5f * (float)Math.Sin(plus35), 1f, 0f, 1.5f, 70f), "positive half-angle at default radius is inclusive");
        Check(CatSetRules.InCone(1.5f * (float)Math.Cos(minus35), 1.5f * (float)Math.Sin(minus35), 1f, 0f, 1.5f, 70f), "negative half-angle at default radius is inclusive");
        Check(CatSetRules.InCone(1.5f, 0f, 1f, 0f, 1.5f, 70f), "radial boundary is inclusive");
        float rotatedAim = 73f * (float)Math.PI / 180f;
        float rotatedBoundary = rotatedAim + plus35;
        Check(CatSetRules.InCone((float)Math.Cos(rotatedBoundary), (float)Math.Sin(rotatedBoundary),
            4f * (float)Math.Cos(rotatedAim), 4f * (float)Math.Sin(rotatedAim), 1.5f, 70f), "rotated scaled aim keeps half-angle inclusive");
        float maxRadiusAngle = 4f * (float)Math.PI / 180f;
        float maxRadiusX = 10f * (float)Math.Cos(maxRadiusAngle);
        float maxRadiusY = 10f * (float)Math.Sin(maxRadiusAngle);
        Check(CatSetRules.InCone(maxRadiusX, maxRadiusY, maxRadiusX, maxRadiusY, 10f, 70f), "configured maximum radius is inclusive at four degrees");
        foreach (float sweepDegrees in new float[] { 0f, 4f, 17f, 43f, 89f, 137f, 181f, 227f, 313f })
        {
            float sweepAngle = sweepDegrees * (float)Math.PI / 180f;
            float sweepX = 10f * (float)Math.Cos(sweepAngle);
            float sweepY = 10f * (float)Math.Sin(sweepAngle);
            Check(CatSetRules.InCone(sweepX, sweepY, sweepX, sweepY, 10f, 70f), "maximum-radius sweep remains inclusive at " + sweepDegrees);
        }
        Check(!CatSetRules.InCone(10.001f * (float)Math.Cos(maxRadiusAngle), 10.001f * (float)Math.Sin(maxRadiusAngle),
            maxRadiusX, maxRadiusY, 10f, 70f), "meaningfully outside maximum radius is rejected");
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

        // Bath Time budgets the seconds it may ADD to one charm, independently of how long that charm is.
        // AllowedBonus is the increment still available; ExtendBudgeted applies it to the live duration.
        Check(Near(CatSetRules.AllowedBonus(0f, 2f, 6f), 2f), "first mist adds the whole bonus");
        Check(Near(CatSetRules.AllowedBonus(4f, 2f, 6f), 2f), "third mist lands exactly on the budget");
        Check(Near(CatSetRules.AllowedBonus(5f, 2f, 6f), 1f), "the final increment is partial");
        Check(Near(CatSetRules.AllowedBonus(6f, 2f, 6f), 0f), "an exhausted budget adds nothing");
        Check(Near(CatSetRules.AllowedBonus(7f, 2f, 6f), 0f), "an overspent budget adds nothing");
        Check(Near(CatSetRules.AllowedBonus(0f, 2f, 0f), 0f), "a zero budget never adds");
        Check(Near(CatSetRules.AllowedBonus(0f, 2f, -1f), 0f), "a negative budget never adds");
        Check(Near(CatSetRules.AllowedBonus(-3f, 2f, 6f), 2f), "negative added counts as zero");
        Check(Near(CatSetRules.AllowedBonus(0f, -2f, 6f), 0f), "a negative bonus adds nothing");

        // The budget is the same whatever the base charm is: 10 s reaches 16 s, a 20 s Dinner Time charm reaches 26 s.
        float bathed = 10f, added = 0f;
        for (int mist = 0; mist < 5; mist++)
        {
            float step = CatSetRules.AllowedBonus(added, 2f, 6f);
            bathed = CatSetRules.ExtendBudgeted(bathed, added, 2f, 6f);
            added += step;
        }
        Check(Near(bathed, 16f), "repeated misting stops six seconds above the base charm");
        Check(Near(added, 6f), "the spent budget stops at the maximum bonus");
        float dinner = 20f, dinnerAdded = 0f;
        for (int mist = 0; mist < 5; mist++)
        {
            float step = CatSetRules.AllowedBonus(dinnerAdded, 2f, 6f);
            dinner = CatSetRules.ExtendBudgeted(dinner, dinnerAdded, 2f, 6f);
            dinnerAdded += step;
        }
        Check(Near(dinner, 26f), "a longer base charm gets the same six added seconds");
        Check(Near(CatSetRules.ExtendBudgeted(9f, 5f, 2f, 6f), 10f), "a partial final increment extends by what is left");
        Check(Near(CatSetRules.ExtendBudgeted(9f, 6f, 2f, 6f), 9f), "an exhausted budget leaves the duration alone");
        Check(CatSetRules.ExtendBudgeted(12f, 0f, 2f, 6f) >= 12f, "a duration is never shortened");
        Check(Near(CatSetRules.ExtendBudgeted(-1f, 0f, 2f, 6f), 2f), "negative duration counts as zero");

        Console.WriteLine(count + " cat set cases passed");
    }
}
