namespace PlutoTheCat
{
    /// <summary>
    /// Everything Daifuku and Kinsuke say, and nothing else: no shop logic lives here.
    ///
    /// The five keys are the plan's Task 6 contract. ShrineStall.Init passes them straight through to
    /// ShopAPI.SetUpFoyerShop's introStringKey / runBasedMultilineGenericStringKey /
    /// runBasedMultilineStopperStringKey / purchaseItemStringKey / purchaseItemFailedStringKey, and calls
    /// Register() first so the keys resolve by the time the dialogue machine is built.
    ///
    /// Why the generic pool goes through SetComplex and the other four through Set: ETGMod's
    /// StringDBTable.Set builds a StringTableManager.SimpleStringCollection, which holds exactly one
    /// string (its only field is `singleString`). The run-based pool has to be a collection the game can
    /// walk one entry at a time - StringCollection.GetWeightedStringSequential(ref lastIndex, out isLast)
    /// - so it must be a ComplexStringCollection, which is what SetComplex(key, string[]) builds.
    ///
    /// Each pool entry is one dialogue box: Daifuku sets it up, Kinsuke lands it, one "\n" between them.
    /// UNVERIFIED (the game is not installed here): that the box renders that newline rather than
    /// running the two speakers together, and that a ~110-character exchange fits the box without
    /// clipping. Both need one look in game; if either is wrong the fix is local to this file.
    /// </summary>
    public static class ShrineStallLines
    {
        public const string IntroKey = "#PLUTO_STALL_INTRO";
        public const string GenericKey = "#PLUTO_STALL_GENERIC";
        public const string StopperKey = "#PLUTO_STALL_STOPPER";
        public const string PurchaseKey = "#PLUTO_STALL_PURCHASE";
        public const string PurchaseFailedKey = "#PLUTO_STALL_PURCHASE_FAILED";

        /// <summary>First meeting of the run: who these two are, in their own words.</summary>
        private const string Intro =
            "Daifuku: I am Daifuku. The koi is Kinsuke. We sell the things Pluto has already knocked off a shelf.\nKinsuke: He handles the shelf. I handle the charm.";

        /// <summary>The repeating pool, one exchange per visit, walked in order by the dialogue machine.</summary>
        private static readonly string[] Exchanges =
        {
            "Daifuku: Everything on this mat belonged to Pluto first.\nKinsuke: And it will belong to him again. We are less a shop and more a lending library.",
            "Daifuku: A customer once asked why a koi keeps the accounts.\nKinsuke: I have a head for figures. I can count to eight. After that I start again, refreshed.",
            "Daifuku: Bianca has still not forgiven anyone about the mug.\nKinsuke: Bogdan bought her a new one. Pluto found the new table.",
            "Daifuku: Kinsuke insists he is not a fish.\nKinsuke: I am a consultant. I simply consult in water.",
            "Daifuku: We take credits here. Not treats.\nKinsuke: Speak for yourself. I take treats. Small ones. Ones that sink.",
            "Daifuku: The spray bottle came to us barely used.\nKinsuke: It works on everyone except the one cat it was bought for.",
            "Daifuku: You are dripping on my counter again.\nKinsuke: That is not dripping. That is presentation.",
            "Daifuku: Mind the bowl. Kinsuke is delicate.\nKinsuke: Kinsuke is structural. This entire stall rests on me.",
            "Daifuku: He has been rehearsing his sales pitch all morning.\nKinsuke: Buy something. That is the pitch. I workshopped it.",
            "Daifuku: Business has been slow today.\nKinsuke: Slow? I have been going in circles since sunrise.",
            "Daifuku: Do not ask him about the water.\nKinsuke: It is fresh. Bogdan changes it, Pluto tests it, and Pluto tests it hourly.",
            "Daifuku: The cone of shame is our steadiest seller.\nKinsuke: Nobody buys it twice. Everybody buys it once.",
            "Daifuku: Pluto knocked the stone lantern over again.\nKinsuke: He did not knock it over. He relocated it. Downward.",
            "Daifuku: You have been standing there a while.\nKinsuke: Take all the time you like. I have nothing but water and opinions.",
            "Daifuku: I do not chase him. I am not a young cat.\nKinsuke: That is what he says. Then the yarn moves, and so does he.",
            "Daifuku: They say a koi brings good fortune.\nKinsuke: They say a great many things to me. Usually while I am eating.",
            "Daifuku: He went over the side of the bowl last week.\nKinsuke: That was a dive. It was scored. I was given a seven.",
            "Daifuku: We are open whenever we are open.\nKinsuke: Which is whenever Daifuku is awake. Plan the rest of your week accordingly.",
            "Daifuku: The feather teaser sells well to cats.\nKinsuke: It sells well to me too. I simply have nothing to hold it with.",
            "Daifuku: Bogdan built this stall in one afternoon.\nKinsuke: Bianca held the nails. Pluto held the tape measure. Briefly.",
            "Daifuku: Every item here has been slept on.\nKinsuke: Thoroughly, and by a professional. That is our quality control.",
            "Daifuku: Please do not tap the glass.\nKinsuke: There is no glass. It is a bowl. Do not tap that either.",
            "Daifuku: He claims he can see the whole Breach from up there.\nKinsuke: I can. It is round, it is damp, and it comes back around every few seconds.",
            "Daifuku: Some customers ask whether the fish is for sale.\nKinsuke: The fish is management.",
            "Daifuku: The catnip pouch. Handle that one carefully.\nKinsuke: Or do not. It is your afternoon, and Pluto has cleared his.",
        };

        /// <summary>Shown once the pool is exhausted: they have run out of material, and admit nothing.</summary>
        private const string Stopper =
            "Daifuku: That was the last of it. He has nothing left.\nKinsuke: I am not out of jokes. I am between jokes. Indefinitely.";

        /// <summary>A sale closed. Kinsuke takes the credit, as he takes the credit for everything.</summary>
        private const string Purchase =
            "Daifuku: It is yours. Try not to lose it.\nKinsuke: And remember who sold it to you. That was me. I did that.";

        /// <summary>Not enough credits. Teasing, never mocking: they want the player to come back.</summary>
        private const string PurchaseFailed =
            "Daifuku: Not quite enough. It happens to everyone.\nKinsuke: Come back richer and we will pretend this never happened. I will remember it forever.";

        /// <summary>Registers every line. Must run before the dialogue machine is built.</summary>
        public static void Register()
        {
            ETGMod.Databases.Strings.Core.Set(IntroKey, Intro);
            ETGMod.Databases.Strings.Core.SetComplex(GenericKey, Exchanges);
            ETGMod.Databases.Strings.Core.Set(StopperKey, Stopper);
            ETGMod.Databases.Strings.Core.Set(PurchaseKey, Purchase);
            ETGMod.Databases.Strings.Core.Set(PurchaseFailedKey, PurchaseFailed);
            Plugin.Log("shrine stall: registered " + (Exchanges.Length + 4) + " dialogue lines");
        }
    }
}
