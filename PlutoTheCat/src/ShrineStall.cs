using System.Collections.Generic;
using UnityEngine;
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
    /// SetUpFoyerShop itself only builds the one talking NPC (Daifuku); Kinsuke's koi-bowl idle clip is
    /// attached onto that same shop GameObject (AttachKinsuke), and the torii/stall backdrop are placed
    /// as plain decorative props (PlaceBackdropProps) alongside it.
    /// </summary>
    public static class ShrineStall
    {
        private const int IdleFps = 6;
        private const int TalkFps = 8;

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
                null, null, null, null, null,   // CustomCanBuy / CustomRemoveCurrency / CustomPrice / OnPurchase / OnSteal
                null, null,                 // currencyIconPath, currencyName (defaults for META_CURRENCY)
                false, null, null,          // hasCarpet, carpetSpritePath, CarpetOffset
                null,                       // prerequisites: ShopAPI does not gate NPC placement by them (see brief)
                new IntVector2(20, 18),     // hitboxSize: Alexandria's own default, passed explicitly
                new IntVector2(5, 0));      // hitboxOffset: Alexandria computes this same default internally but
                                            // discards it before use (a bug), so it must be passed explicitly here.

            // SetUpFoyerShop wraps its whole body in a try/catch that only logs and returns null (e.g. on
            // a mistyped resource path), so a null result here is silent otherwise - always check and log.
            if (shop == null)
            {
                Plugin.Log("shrine stall: SetUpFoyerShop returned null; see the [CharAPI]/Alexandria log lines above for the failed resource path");
            }
            else
            {
                Plugin.Log("shrine stall: registered at " + PlutoConfig.StallPosition);
                AttachKinsuke(shop);
            }

            PlaceBackdropProps();
        }

        /// <summary>
        /// Attaches Kinsuke's koi-bowl idle clip to the shop's own GameObject (there is no separate
        /// transform to place him at: SetUpFoyerShop returns a single NPC object, and both
        /// AddParentedAnimationToShop/AddUnparentedAnimationToShop add a named clip to that same object's
        /// existing tk2dSpriteAnimator rather than spawning a second sprite). Design: "Kinsuke's bowl
        /// rests on [the counter]" - a fixed prop, not something that should turn with Daifuku's own
        /// walk/facing state. AddParentedAnimationToShop runs the clip through
        /// ShopAPI.CreateDirectionalAnimation (the same call SetUpFoyerShop uses to build the idle/talk
        /// clips), which drives the clip from the NPC's AIAnimator facing direction; AddUnparentedAnimationToShop
        /// instead adds a plain looping clip via SpriteBuilder.AddAnimation, with no dependency on facing
        /// direction at all - the one that "keeps the bowl fixed" - so that is the one used here.
        /// UNVERIFIED: confirmed real signatures against the Alexandria 0.5.10 IL (both take
        /// (GameObject self, List&lt;string&gt; yourPaths, float YourAnimFPS, string AnimationName)), but
        /// the bowl's actual on-screen position comes from how kinsuke_idle_*'s frames were composited by
        /// Task 4's art pipeline (these calls carry no runtime offset), and this has never been seen
        /// in-game (no game install here; Assembly-CSharp.dll is a stripped stub).
        /// </summary>
        private static void AttachKinsuke(GameObject shop)
        {
            List<string> kinsukePaths = new List<string>
            {
                Plugin.SHOP_ROOT + "/kinsuke_idle_001",
                Plugin.SHOP_ROOT + "/kinsuke_idle_002",
                Plugin.SHOP_ROOT + "/kinsuke_idle_003",
                Plugin.SHOP_ROOT + "/kinsuke_idle_004",
            };
            ShopAPI.AddUnparentedAnimationToShop(shop, kinsukePaths, IdleFps, "kinsuke_idle");
        }

        /// <summary>Places the torii and stall backdrop props (see the offset comments above).</summary>
        private static void PlaceBackdropProps()
        {
            PlaceProp("torii.png", PlutoConfig.StallPosition + ToriiOffset, "pluto_shrine_stall_torii");
            PlaceProp("stall.png", PlutoConfig.StallPosition + StallOffset, "pluto_shrine_stall_stall");
        }

        /// <summary>A plain, non-interactive decorative sprite: no collider, no animation, bottom-center pivot.</summary>
        private static void PlaceProp(string fileName, Vector3 position, string objectName)
        {
            string resource = (Plugin.SHOP_ROOT + "/" + fileName).Replace('/', '.');
            Texture2D tex = Alexandria.ItemAPI.ResourceExtractor.GetTextureFromResource(resource, typeof(Plugin).Assembly);
            if (tex == null)
            {
                Plugin.Log("shrine stall: missing prop resource " + resource);
                return;
            }
            tex.filterMode = FilterMode.Point;
            Sprite sprite = Sprite.Create(tex, new Rect(0f, 0f, tex.width, tex.height), new Vector2(0.5f, 0f), 16f);
            GameObject obj = new GameObject(objectName);
            SpriteRenderer renderer = obj.AddComponent<SpriteRenderer>();
            renderer.sprite = sprite;
            obj.transform.position = position;
        }
    }
}
