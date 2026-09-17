namespace PlutoTheCat
{
    /// <summary>
    /// Placeholder for Task 6. ShrineStall.Init passes these five string-table keys straight through to
    /// ShopAPI.SetUpFoyerShop (runBasedMultilineGenericStringKey, runBasedMultilineStopperStringKey,
    /// purchaseItemStringKey, purchaseItemFailedStringKey, introStringKey) and calls Register() first so
    /// the keys resolve to real dialogue. Task 6 fills in Register() and the actual line text; until then
    /// the keys are just placeholders and Register() is a no-op.
    /// </summary>
    public static class ShrineStallLines
    {
        public const string RunBasedMultilineGenericKey = "PLUTO_SHRINE_STALL_GENERIC";
        public const string RunBasedMultilineStopperKey = "PLUTO_SHRINE_STALL_STOPPER";
        public const string PurchaseItemKey = "PLUTO_SHRINE_STALL_PURCHASE";
        public const string PurchaseItemFailedKey = "PLUTO_SHRINE_STALL_PURCHASE_FAILED";
        public const string IntroKey = "PLUTO_SHRINE_STALL_INTRO";

        /// <summary>No-op until Task 6 registers the real dialogue strings under the keys above.</summary>
        public static void Register() { }
    }
}
