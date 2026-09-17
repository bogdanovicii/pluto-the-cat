using System;
using PlutoTheCat;
class StallPositionMigrationCases
{
    static int count;
    static void Check(bool ok, string label) { if (!ok) throw new Exception(label); count++; }
    static void Main()
    {
        // The exact 2.20.0 broken default must be recognized so it gets migrated.
        Check(PlutoConfigRules.IsLegacyBrokenStallPosition(10.5f, 22.1f), "exact legacy default is recognized");

        // The current (2.20.1+) default must NOT be treated as the legacy one, or every fresh install would
        // "migrate" on first run for no reason.
        Check(!PlutoConfigRules.IsLegacyBrokenStallPosition(19.7f, 22.1f), "current default is left alone");

        // A position the player deliberately chose - even one close to the old broken default - must never be
        // clobbered. The migration is intentionally exact-match only.
        Check(!PlutoConfigRules.IsLegacyBrokenStallPosition(10.6f, 22.1f), "a nearby deliberate x is not touched");
        Check(!PlutoConfigRules.IsLegacyBrokenStallPosition(10.5f, 22.2f), "a nearby deliberate y is not touched");
        Check(!PlutoConfigRules.IsLegacyBrokenStallPosition(0f, 0f), "an unrelated position is not touched");

        // Floating point round-trips through config text ("10.5,22.1" -> float -> string) should still compare
        // equal within a tiny epsilon.
        Check(PlutoConfigRules.IsLegacyBrokenStallPosition(10.500001f, 22.099999f), "tiny float noise still matches");

        Console.WriteLine(count + " checks passed");
    }
}
