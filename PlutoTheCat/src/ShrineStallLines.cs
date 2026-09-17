namespace PlutoTheCat
{
    /// <summary>
    /// Placeholder for Task 6, whose interface is fixed by the plan (docs/superpowers/plans/2026-09-17-
    /// shrine-stall-2200.md, Task 6): IntroKey, GenericKey, StopperKey, PurchaseKey, PurchaseFailedKey and
    /// Register(). ShrineStall.Init passes these five keys straight through to ShopAPI.SetUpFoyerShop's
    /// introStringKey / runBasedMultilineGenericStringKey / runBasedMultilineStopperStringKey /
    /// purchaseItemStringKey / purchaseItemFailedStringKey, and calls Register() first so the keys resolve
    /// to real dialogue. Task 6 fills in Register() (writing every line through
    /// ETGMod.Databases.Strings.Core.Set) and the actual line text; until then the keys are just
    /// placeholders and Register() is a no-op.
    /// </summary>
    public static class ShrineStallLines
    {
        public const string IntroKey = "PLUTO_SHRINE_STALL_INTRO";
        public const string GenericKey = "PLUTO_SHRINE_STALL_GENERIC";
        public const string StopperKey = "PLUTO_SHRINE_STALL_STOPPER";
        public const string PurchaseKey = "PLUTO_SHRINE_STALL_PURCHASE";
        public const string PurchaseFailedKey = "PLUTO_SHRINE_STALL_PURCHASE_FAILED";

        /// <summary>No-op until Task 6 registers the real dialogue strings under the keys above.</summary>
        public static void Register() { }
    }
}
