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
    /// SetUpFoyerShop itself only builds the one talking NPC (Daifuku); Kinsuke's koi-bowl and the
    /// torii/stall backdrop are placed as their own separate sprite GameObjects (PlaceBackdropProps),
    /// since none of them are Daifuku himself.
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
            }

            PlaceBackdropProps();
        }

        /// <summary>
        /// Places the torii, stall and Kinsuke's koi-bowl as real sprite GameObjects (see the offset
        /// comments above). Kinsuke's four kinsuke_idle_* frames are an animation, but this file has no
        /// animation machinery of its own: PlaceProp is a single static SpriteRenderer, and Alexandria's
        /// two shop-animation helper methods were tried in an earlier review round and rejected - both
        /// were confirmed against the Alexandria 0.5.10 IL to register the new clip on Daifuku's OWN
        /// tk2dSpriteAnimator rather than create a second sprite, so at best they would be dead code and
        /// at worst they would make Daifuku's own sprite swap to Kinsuke's frames instead of showing both.
        /// This is a deliberate reduction, not equivalent to animating him: Kinsuke is placed as a single
        /// static sprite using only kinsuke_idle_001.png, so he will not idle-animate in game. Animating
        /// him properly would need either a small MonoBehaviour here that manually advances a
        /// SpriteRenderer through the four frames on a timer (a tk2dSpriteAnimator only comes from
        /// Alexandria's own NPC-building helpers, which are built around a single tracked character), or
        /// a follow-up task once one exists.
        /// </summary>
        private static void PlaceBackdropProps()
        {
            PlaceProp("torii.png", PlutoConfig.StallPosition + ToriiOffset, "pluto_shrine_stall_torii");
            PlaceProp("stall.png", PlutoConfig.StallPosition + StallOffset, "pluto_shrine_stall_stall");
            PlaceProp("kinsuke_idle_001.png", PlutoConfig.StallPosition + KinsukeOffset, "pluto_shrine_stall_kinsuke");
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
