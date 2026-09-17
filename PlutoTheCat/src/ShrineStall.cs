using System.Collections.Generic;
using UnityEngine;
using Alexandria.DungeonAPI;
using Alexandria.Misc;
using Alexandria.NPCAPI;
using Gungeon;

namespace PlutoTheCat
{
    /// <summary>
    /// Registers the Breach shrine stall (2.20): a foyer meta-shop run by Daifuku (idle+talk NPC) that
    /// sells permanent per-save unlocks for the ten cat items PlutoUnlockGate gates. With the foyer
    /// meta-shop, CustomShopController.DoSetup only stocks an item whose encounterTrackable.PrerequisitesMet()
    /// is false (i.e. still locked - see PlutoUnlockGate.Apply) and prices it Mathf.RoundToInt(wgo.weight),
    /// so each WeightedGameObject's weight IS the item's Hegemony-credit price: ShrineStallRules.Price
    /// reads the same config table PlutoUnlockGate and PlutoConfig already use.
    /// SetUpFoyerShop itself only builds the one talking NPC (Daifuku); Kinsuke's koi-bowl and the
    /// torii/stall backdrop are placed as their own separate sprite GameObjects (PlaceBackdropProps),
    /// since none of them are Daifuku himself.
    /// </summary>
    public static class ShrineStall
    {
        private const int IdleFps = 6;
        private const int TalkFps = 8;
        // Kinsuke's four-frame bob. Slower than Daifuku's idle on purpose: a koi drifting in a bowl should
        // read as calmer than the cat serving customers next to him.
        private const float KinsukeFps = 4f;

        private static readonly List<GameObject> Props = new List<GameObject>();
        private static readonly Dictionary<string, Sprite> SpriteCache = new Dictionary<string, Sprite>();
        private static System.Action _foyerHandler;

        // Task 4's art review found torii.png (78x48px) and stall.png (48x36px) share no anchor. Both
        // props below use a bottom-center sprite pivot, so placing them at the same Y sits their bottom
        // rows on one ground line; the X offsets are picked so the stall's center sits 6px right of the
        // torii's left edge, at this game's 16px/unit scale:
        //   toriiLeftEdge = toriiX - (78/2)/16 = toriiX - 2.4375
        //   stallCenterX  = toriiLeftEdge + 6/16 = toriiX - 2.0625
        // UNVERIFIED: picked from the art-review note alone. This session has no game install and the
        // referenced Assembly-CSharp.dll is a stripped stub, so this has never been seen composited
        // in-game. Re-check both offsets (and the ground-line Y) the first time the stall is visible.
        private static readonly Vector3 ToriiOffset = new Vector3(-3.0f, 0f, 0f);
        private static readonly Vector3 StallOffset = new Vector3(-3.0f - 2.0625f, 0f, 0f);

        // Kinsuke's bowl (kinsuke_idle_*, 22x20px) rests on the stall counter (design: "Daifuku stands
        // behind the counter, Kinsuke's bowl rests on it"), so it is offset from the stall itself rather
        // than from the torii. Same bottom-center pivot convention as the other props. UNVERIFIED, same
        // caveat as above, plus one more unknown: stall.png's own internal composition (how much of its
        // 36px height is a flat counter surface the bowl could plausibly sit on top of) was never
        // inspected pixel-by-pixel - the y offset below (28px, most of the sprite's height) is a guess at
        // "near the top of the counter", the x offset (12px right of the stall's center) just keeps the
        // bowl clear of the stall's own center where the three purchasable items sit. Re-check both,
        // and stall.png's actual composition, the first time this is visible in-game.
        private static readonly Vector3 KinsukeOffset = StallOffset + new Vector3(12f / 16f, 28f / 16f, 0f);

        public static void Init()
        {
            ShrineStallLines.Register();   // must run before SetUpFoyerShop so its string keys resolve

            int[] prices =
            {
                PlutoConfig.StallPriceBallOfYarn,
                PlutoConfig.StallPriceCatnipPouch,
                PlutoConfig.StallPriceHairball,
                PlutoConfig.StallPriceScratchingPost,
                PlutoConfig.StallPriceToiletPaperRoll,
                PlutoConfig.StallPriceCoffeeMug,
                PlutoConfig.StallPriceJingleBellCollar,
                PlutoConfig.StallPriceConeOfShame,
                PlutoConfig.StallPriceSprayBottle,
                PlutoConfig.StallPriceFeatherTeaser,
            };

            GenericLootTable table = ScriptableObject.CreateInstance<GenericLootTable>();
            table.defaultItemDrops = new WeightedGameObjectCollection();
            foreach (string id in PlutoUnlocks.Ids)
            {
                if (!Game.Items.ContainsID(id)) continue;
                PickupObject pickup = Game.Items[id];
                if (pickup == null) continue;
                LootUtility.AddItemToPool(table, pickup, ShrineStallRules.Price(id, prices, PlutoUnlocks.Ids));
            }

            List<string> idlePaths = new List<string>
            {
                Plugin.SHOP_ROOT + "/daifuku_idle_001",
                Plugin.SHOP_ROOT + "/daifuku_idle_002",
                Plugin.SHOP_ROOT + "/daifuku_idle_003",
                Plugin.SHOP_ROOT + "/daifuku_idle_004",
            };
            List<string> talkPaths = new List<string>
            {
                Plugin.SHOP_ROOT + "/daifuku_talk_001",
                Plugin.SHOP_ROOT + "/daifuku_talk_002",
                Plugin.SHOP_ROOT + "/daifuku_talk_003",
                Plugin.SHOP_ROOT + "/daifuku_talk_004",
            };

            // position and npcPosition both use PlutoConfig.StallPosition: this is a single stationary
            // shopkeeper, not a shop with a separate items table offset from the NPC.
            GameObject shop = ShopAPI.SetUpFoyerShop(
                "Daifuku", "pluto_shrine_stall",
                PlutoConfig.StallPosition,
                idlePaths, IdleFps,
                talkPaths, TalkFps,
                Plugin.SHOP_ROOT + "/blueprint",
                table,
                CustomShopItemController.ShopCurrencyType.META_CURRENCY,
                ShrineStallLines.GenericKey,
                ShrineStallLines.StopperKey,
                ShrineStallLines.PurchaseKey,
                ShrineStallLines.PurchaseFailedKey,
                ShrineStallLines.IntroKey,
                Vector3.zero,               // talkPointOffset; unverified, tune once visible in game
                PlutoConfig.StallPosition,  // npcPosition
                ShopAPI.VoiceBoxes.BELLO,
                ShopAPI.defaultItemPositions,
                1f,                         // costModifier
                null, null, null, OnPurchase, null,   // CustomCanBuy / CustomRemoveCurrency / CustomPrice / OnPurchase / OnSteal
                null, null,                 // currencyIconPath, currencyName (defaults for META_CURRENCY)
                false, null, null,          // hasCarpet, carpetSpritePath, CarpetOffset
                null,                       // prerequisites: ShopAPI does not gate NPC placement by them (see brief)
                new IntVector2(20, 18),     // hitboxSize: Alexandria's own default, passed explicitly
                new IntVector2(5, 0));      // hitboxOffset: Alexandria computes this same default internally but
                                            // discards it before use (a bug), so it must be passed explicitly here.

            // SetUpFoyerShop wraps its whole body in a try/catch that only logs and returns null (e.g. on
            // a mistyped resource path), so a null result here is silent otherwise - always check and log.
            // The props are only worth placing when the shop itself built: with no Daifuku, a torii and an
            // unattended counter in the middle of the Breach read as a bug rather than as decoration.
            if (shop == null)
            {
                Plugin.Log("shrine stall: SetUpFoyerShop returned null; see the [CharAPI]/Alexandria log lines above for the failed resource path");
                return;
            }

            Plugin.Log("shrine stall: registered at " + PlutoConfig.StallPosition);

            if (_foyerHandler == null)
            {
                _foyerHandler = PlaceBackdropProps;
                DungeonHooks.OnFoyerAwake += _foyerHandler;
            }
            PlaceBackdropProps();
        }

        /// <summary>Unhooks the foyer handler and drops the placed props. Safe to call if Init() never ran.</summary>
        public static void Teardown()
        {
            if (_foyerHandler != null)
            {
                DungeonHooks.OnFoyerAwake -= _foyerHandler;
                _foyerHandler = null;
            }
            DestroyProps();
        }

        /// <summary>
        /// Wired into SetUpFoyerShop's OnPurchase slot. Its real signature (read from the Alexandria 0.5.10
        /// IL with ikdasm, since monodis crashes on this assembly) is
        /// Func&lt;PlayerController, PickupObject, int, bool&gt; = (player, item, cost). Alexandria invokes it
        /// from CustomShopItemController's own purchase handler AFTER the item has already been added to the
        /// player's loadout and the currency already removed, and immediately discards the bool it returns
        /// (the IL pops the result) - so the return value is not a "allow/deny the purchase" gate, only a
        /// notification hook, and this always returns true.
        ///
        /// The item handed in is NOT the real cat item. In the foyer meta-shop path DoSetup takes the
        /// `baseShopType == 6 &amp;&amp; ExampleBlueprintPrefab != null` branch, instantiates the single
        /// ExampleBlueprintPrefab that SetUpFoyerShop built once via GenerateBluePrint
        /// (ItemBuilder.BuildItem&lt;ItemBlueprintItem&gt;), copies the real item's journal fields onto the clone
        /// and walks the real item's prerequisites for a FLAG one, copying its saveFlagToCheck into the
        /// clone's PickupObject.SaveFlagToSetOnAcquisition, and passes THAT clone to
        /// CustomShopItemController.Initialize - whose `item` field is what the invoke site
        /// (`OnPurchase.Invoke(player, this.item, ModifiedPrice)`) hands us. All three slots therefore share
        /// one PickupObjectId, so the old `pickup.PickupObjectId != item.PickupObjectId` test could never
        /// match and every purchase fell through to the "could not match" log. The save flag is the only
        /// field on the clone that still identifies which of the ten was bought, so that is what we match on;
        /// PickupObjectId stays as a fallback for a non-blueprint path (a plain CustomShopItemController
        /// initialised with the real item), where it is still the right test.
        ///
        /// KNOWN DEAD IN THIS PATH, and unfixable from here: that same blueprint branch jumps straight from
        /// Initialize to the m_itemControllers.Add, past the block that assigns customCanBuy, removeCurrency,
        /// customPrice, OnPurchase and OnSteal - those five are only wired in DoSetup's NON-blueprint branch
        /// (one `stfld CustomShopItemController::OnPurchase` in the whole assembly, inside that branch). So in
        /// Alexandria 0.5.10 this callback is never invoked for a foyer meta-shop at all. Nothing on our side
        /// can wire a field Alexandria owns. What still makes the unlock land is PlutoUnlocks.Reconcile:
        /// the clone's SaveFlagToSetOnAcquisition means the game's own pickup path sets the GungeonFlags
        /// value, and Reconcile writes the string mirror from it on the next foyer load / dungeon start.
        /// This method is kept, and fixed, because it costs nothing and is correct the moment Alexandria
        /// wires the delegate (META_CURRENCY itself is handled natively, so the other four nulls are inert).
        ///
        /// No source-text test can catch this class of bug: every assertion available to
        /// tools/tests/test_shrine_stall.py is a string match on our own file, and our file was already
        /// self-consistent and already called PlutoUnlocks.Unlock. Only reading Alexandria's IL, or a real
        /// purchase in game, can tell a matching rule that works from one that cannot.
        /// </summary>
        private static bool OnPurchase(PlayerController player, PickupObject item, int cost)
        {
            if (item == null)
            {
                Plugin.Log("shrine stall: purchase callback got a null item");
                return true;
            }

            foreach (string id in PlutoUnlocks.Ids)
            {
                // Flag(id) returns default(GungeonFlags) for an id whose flag never registered, which would
                // match any clone whose SaveFlagToSetOnAcquisition was left at its default - check first.
                bool flagMatch = PlutoUnlocks.IsRegistered(id)
                    && item.SaveFlagToSetOnAcquisition == PlutoUnlocks.Flag(id);

                bool idMatch = false;
                if (!flagMatch && Game.Items.ContainsID(id))
                {
                    PickupObject pickup = Game.Items[id];
                    idMatch = pickup != null && pickup.PickupObjectId == item.PickupObjectId;
                }
                if (!flagMatch && !idMatch) continue;

                PlutoUnlocks.Unlock(id);
                Plugin.Log("shrine stall: purchased and unlocked " + id + (flagMatch ? " (matched by save flag)" : " (matched by pickup id)"));
                return true;
            }

            Plugin.Log("shrine stall: purchase callback could not match the bought item back to a gated id");
            return true;
        }

        /// <summary>
        /// Places the torii, stall and Kinsuke's koi-bowl as real sprite GameObjects (see the offset
        /// comments above), replacing any earlier set first.
        ///
        /// Runs on every DungeonHooks.OnFoyerAwake (Alexandria's postfix on MainMenuFoyerController.Awake),
        /// not once from Init. These are unparented GameObjects with no DontDestroyOnLoad, so Unity destroys
        /// them the moment the Breach scene unloads for a run; Daifuku himself is re-placed by Alexandria on
        /// every foyer load, so placing the props once left the shopkeeper standing alone in mid-air from
        /// the second visit onwards. DontDestroyOnLoad was the alternative and was rejected: it would carry
        /// three Breach-positioned sprites into every dungeon floor for the rest of the session.
        ///
        /// Kinsuke gets all four kinsuke_idle_* frames through a PropFlipbook (below). Alexandria's two
        /// shop-animation helpers are still not usable for him - both were confirmed against the Alexandria
        /// 0.5.10 IL to register the new clip on Daifuku's OWN tk2dSpriteAnimator rather than create a
        /// second sprite - so the frames are advanced by hand on a timer instead.
        /// </summary>
        private static void PlaceBackdropProps()
        {
            DestroyProps();
            PlaceProp(new[] { "torii.png" }, PlutoConfig.StallPosition + ToriiOffset, "pluto_shrine_stall_torii");
            PlaceProp(new[] { "stall.png" }, PlutoConfig.StallPosition + StallOffset, "pluto_shrine_stall_stall");
            PlaceProp(
                new[] { "kinsuke_idle_001.png", "kinsuke_idle_002.png", "kinsuke_idle_003.png", "kinsuke_idle_004.png" },
                PlutoConfig.StallPosition + KinsukeOffset, "pluto_shrine_stall_kinsuke");
        }

        /// <summary>Destroys the props placed by the previous foyer load. The flipbook dies with its object.</summary>
        private static void DestroyProps()
        {
            foreach (GameObject prop in Props)
                if (prop != null) Object.Destroy(prop);
            Props.Clear();
        }

        /// <summary>
        /// A non-interactive decorative sprite: no collider, bottom-center pivot. One frame is static; more
        /// than one gets a PropFlipbook. Sprites are cached because this runs on every foyer load and
        /// Sprite.Create/GetTextureFromResource would otherwise leak a texture per visit.
        /// </summary>
        private static void PlaceProp(string[] fileNames, Vector3 position, string objectName)
        {
            Sprite[] frames = new Sprite[fileNames.Length];
            for (int i = 0; i < fileNames.Length; i++)
            {
                frames[i] = LoadSprite(fileNames[i]);
                if (frames[i] == null) return;   // LoadSprite already logged which resource is missing
            }

            GameObject obj = new GameObject(objectName);
            SpriteRenderer renderer = obj.AddComponent<SpriteRenderer>();
            renderer.sprite = frames[0];
            obj.transform.position = position;
            if (frames.Length > 1) obj.AddComponent<PropFlipbook>().Begin(frames, KinsukeFps);
            Props.Add(obj);
        }

        private static Sprite LoadSprite(string fileName)
        {
            Sprite cached;
            if (SpriteCache.TryGetValue(fileName, out cached) && cached != null) return cached;

            string resource = (Plugin.SHOP_ROOT + "/" + fileName).Replace('/', '.');
            Texture2D tex = Alexandria.ItemAPI.ResourceExtractor.GetTextureFromResource(resource, typeof(Plugin).Assembly);
            if (tex == null)
            {
                Plugin.Log("shrine stall: missing prop resource " + resource);
                return null;
            }
            tex.filterMode = FilterMode.Point;
            Sprite sprite = Sprite.Create(tex, new Rect(0f, 0f, tex.width, tex.height), new Vector2(0.5f, 0f), 16f);
            SpriteCache[fileName] = sprite;
            return sprite;
        }

        /// <summary>
        /// Advances a SpriteRenderer through a set of frames on a timer, so Kinsuke bobs in his bowl. Lives
        /// on the prop's own GameObject, so DestroyProps (and any scene change) takes it with it.
        /// BraveTime.DeltaTime rather than Time.deltaTime, like the rest of this mod's per-frame components,
        /// so the bob follows the game's own time scale.
        /// </summary>
        public sealed class PropFlipbook : MonoBehaviour
        {
            private Sprite[] frames;
            private float secondsPerFrame;
            private float elapsed;
            private int frame;

            public void Begin(Sprite[] clip, float fps)
            {
                frames = clip;
                secondsPerFrame = fps > 0f ? 1f / fps : 0f;
            }

            private void Update()
            {
                if (frames == null || frames.Length < 2 || secondsPerFrame <= 0f) return;
                elapsed += BraveTime.DeltaTime;
                if (elapsed < secondsPerFrame) return;

                // A single subtraction would fall behind after a long stall (a load, a pause); stepping
                // whole frames keeps the clip in phase however many it has to skip.
                int steps = (int)(elapsed / secondsPerFrame);
                elapsed -= steps * secondsPerFrame;
                frame = (frame + steps) % frames.Length;

                SpriteRenderer renderer = GetComponent<SpriteRenderer>();
                if (renderer != null) renderer.sprite = frames[frame];
            }
        }
    }
}
