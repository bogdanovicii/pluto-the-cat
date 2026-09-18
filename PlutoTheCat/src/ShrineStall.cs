using System;
using System.Collections.Generic;
using System.Globalization;
using UnityEngine;
using Alexandria.DungeonAPI;
using Alexandria.ItemAPI;
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
        private static readonly Dictionary<string, int> SpriteIdCache = new Dictionary<string, int>();
        private static System.Action _foyerHandler;

        // The NPC GameObject SetUpFoyerShop built, kept so pluto_stall can move Daifuku himself (not just
        // the backdrop props) without a Breach reload. Null until Init() succeeds; cleared by Teardown().
        private static GameObject _shopObject;
        private static bool _commandRegistered;

        /// <summary>Alexandria names the shop root "&lt;prefix&gt;:&lt;name&gt;_Shop" and keys registeredShops by the
        /// same string, so this prefix is how FindLiveShop tells our stall from another mod's.</summary>
        private const string ShopPrefix = "pluto_shrine_stall";

        // 2.20.3 root-cause fix (placement round 2): the design (docs/superpowers/specs/
        // 2026-09-17-shrine-stall-design.md, "Under the gate: a counter...") wants the stall counter
        // CENTERED UNDER the torii gate, not offset from it. The earlier -2.0625 nudge came from an
        // art-review note about aligning the counter 6px right of the torii's LEFT EDGE, which is a
        // different, and wrong, target - it put the counter to the left of the gate instead of under it
        // (tester report, 2.20.2). Both torii.png (78x48px) and stall.png (48x36px) are bottom-center
        // pivoted, so centering one 3-tile-wide sprite under a 4.875-tile-wide one bottom-center pivoted
        // needs no offset at all: StallOffset.x == ToriiOffset.x. Same Y for both keeps their bottom rows
        // on one ground line. Still no game install this session - re-confirm visually the first time the
        // stall is on screen.
        // 2.20.5 (placement round 3, from the first diagnostic run): the -3.0 was wrong in a way no
        // amount of prop-vs-prop reasoning could catch, because it was measured against the wrong thing.
        // Daifuku does not stand at "StallPosition + some offset" - PlaceBreachShops sets the live shop
        // clone's transform straight to BreachShopComp.offset, which IS PlutoConfig.StallPosition. So the
        // shopkeeper is always exactly at StallPosition, and every -3.0 here pushed the entire visible
        // stall three tiles to his left: he would have stood three tiles clear of his own counter even
        // once the clone moved (tester's 2.20.4 log: props resolved to x=14.25/15.19/16.75 while the shop
        // anchor was 19.7). Both props are therefore centered on him now - counter around him so he is
        // behind it, gate around both so it frames them - which is also what makes the gate read as a
        // gate: at 4.875 tiles against the counter's 3, sharing a center leaves ~0.94 tiles of pillar
        // showing on EACH side. Before, the whole gate sat left of the counter and only its left pillar
        // was visible (tester screenshot, 2.20.4).
        private static readonly Vector3 ToriiOffset = Vector3.zero;
        private static readonly Vector3 StallOffset = Vector3.zero;

        // Daifuku's own local offset inside the shop clone, passed as SetUpFoyerShop's npcPosition. Not
        // zero: at zero he stands on the counter's own ground line, and since the counter is 2.25 tiles
        // tall against his 2, the counter would cover him completely. A tile of +Y is this engine's usual
        // "further back" - it raises him on screen AND pushes his z back (z = y - heightOffGround), so he
        // reads as standing behind the counter with roughly his top 0.75 tile visible above its lip, and
        // he sorts behind it without any special-casing. UNVERIFIED in game; the amount is the first thing
        // to tune if he is hidden or floating.
        private const float DaifukuBehindCounter = 1.0f;

        // Kinsuke's bowl (kinsuke_idle_*, 22x20px) rests on the stall counter (design: "Daifuku stands
        // behind the counter, Kinsuke's bowl rests on it"), so it is offset from the stall itself rather
        // than from the torii. Same bottom-center pivot convention as the other props.
        //
        // 2.20.3: measured stall.png (48x36px, bottom-center pivot, 16px/tile) pixel-by-pixel instead of
        // guessing. Rows 0-19 (top-down) span x=11-47: that is the noren curtain, and it is right-biased
        // in its own canvas (center ~x=29 of 48). Rows 20-25 widen to x=0-47 (some rows x=0-46): that
        // widening is the counter's top lip, i.e. the counter's actual playing surface starts at row 20.
        // With a bottom-center pivot the sprite's bottom row sits on the ground line, so the surface's
        // height above ground is (spriteHeight - topRow) / pixelsPerTile = (36 - 20) / 16 = 1.0 tile. The
        // old value (28/16 = 1.75 tiles) put the bowl three quarters of a tile above the counter, floating
        // near the torii's crossbeam (tester report, 2.20.2) - it was guessed as "near the top of the
        // sprite", not measured against the actual counter geometry.
        // Re-checked the X too, since the curtain's right bias could mislead a guess about where the
        // counter's visible mass sits: averaging the left/right opaque edges of rows 20-35 (the counter
        // itself, below the curtain) gives a mass-center at x=24.16 of 48 - i.e. within 0.16px (~0.01
        // tile) of the sprite's own pivot (x=24, the 0.5 pivot on a 48px-wide canvas). The counter is
        // already centered on StallOffset; the curtain's bias does not carry over to it. The 12px
        // (0.75-tile) rightward nudge below is therefore kept as the deliberate design choice it always
        // was - clearing the three purchasable items that sit at the stall's own center - not a
        // measurement correction.
        //
        // 2.20.5: X widened from 0.75 to 0.9 tiles. The counter's right edge is at StallOffset.x + 1.5,
        // and the bowl's own half-width is ~0.69, so at 0.75 it was fine on paper - but the tester
        // measured it hanging 0.06 tiles PAST the counter's end on screen, resting on air (2.20.4 report,
        // bowl center 16.75 against a counter edge of 16.688). 0.9 puts its center on the right half of
        // the surface with its whole width inboard. The Y stays at the measured 1.0-tile counter lip.
        private static readonly Vector3 KinsukeOffset = StallOffset + new Vector3(0.9f, 16f / 16f, 0f);

        // 2.20.4 depth fix: PlaceProp used to build plain Unity SpriteRenderer GameObjects at z=0 with no
        // sortingOrder/sortingLayer and none of this game's own depth handling - the same tk2d-based
        // z-sort every other prop/decal in this mod goes through (CoffeeMugItem.cs's puddle,
        // PuffedUpItem.cs's fur layer, ScratchingPostItem.cs's placed post: all call
        // sprite.HeightOffGround = <value>; sprite.UpdateZDepth() on a tk2dSprite). A raw SpriteRenderer at
        // z=0 has no defined relationship to Daifuku's own tk2d depth, so with the torii (77x48px, ~4.8x3
        // tiles) and the counter (48x36px, 3x2.25 tiles) both now centered on the same anchor Daifuku
        // stands at, either one drawing in front of him would hide him completely with no error in the
        // log - which is exactly "the shopkeeper is missing" with nothing to grep for.
        // PlaceProp below now builds tk2dSprite GameObjects and sets HeightOffGround explicitly so the
        // stack order is deterministic regardless of how close these three props sit to Daifuku's own Y:
        // more negative = further back, matching CoffeeMugItem's -0.5f and PuffedUpItem's -0.6f. Ordering,
        // back to front: torii (furthest back) -> stall/counter -> Kinsuke's bowl -> Daifuku (managed by
        // Alexandria's own NPC depth handling, not this file, and left at its default so he stays in front
        // of all three).
        // 2.20.5 depth fix. The 2.20.4 values were chosen as if HeightOffGround were the only thing
        // feeding the sort, but the tester derived the real relationship from our own diagnostic numbers:
        //
        //     z = worldY - heightOffGround          (lower z draws IN FRONT)
        //
        // and that exposed a double-count. The bowl is the only piece raised in world Y (a tile, to sit on
        // the counter lip), so that lift also pushed it a full tile BACKWARDS, swamping its -0.3:
        //     counter 22.125 - (-0.6) = 22.725 (front)   torii 22.125 - (-1.0) = 23.125 (middle)
        //     bowl    23.125 - (-0.3) = 23.425 (BACK)
        // Intended gate/counter/bowl; actual counter/gate/bowl, with the bowl behind everything.
        //
        // The tester's suggested fix was to give all three props one world Y and carry the whole lift with
        // heightOffGround. Not taken, deliberately: it assumes HeightOffGround also raises the sprite
        // visually, which this session cannot confirm - and the bowl's current world-Y lift is the one
        // piece of this composition a human has confirmed looks right ("sitting ON the counter surface",
        // 2.20.4). Breaking a verified visual to fix an unverified sort would be a bad trade. Instead the
        // lift stays and the bowl's heightOffGround compensates for it.
        //
        // Resulting z, with P = StallPosition.y, front to back:
        //     bowl     (P + 1.0) - ( 1.4) = P - 0.4     frontmost
        //     counter  (P      ) - ( 0.0) = P
        //     Daifuku  (P + 1.0) - ( 0.0) = P + 1.0     behind the counter, in front of the gate
        //     torii    (P      ) - (-1.5) = P + 1.5     backmost
        // Monotonic, and it no longer depends on the props' world Y agreeing with each other.
        private const float ToriiHeightOffGround = -1.5f;
        private const float StallHeightOffGround = 0.0f;
        private const float KinsukeHeightOffGround = 1.4f;

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

            // 2.20.3 root-cause fix: npcPosition is NOT "where Daifuku ends up" - it is his offset from
            // the shop root's ORIGIN at build time, before the root is later moved to `position`. Verified
            // against the Alexandria 0.5.10 IL (ikdasm; monodis crashes on this assembly):
            // SetUpFoyerShop parents the NPC GameObject to the new CustomShopController's transform
            // (`callvirt instance void Transform::set_parent`, IL_04fb) and IMMEDIATELY sets that NPC's
            // WORLD position to npcPosition (`callvirt instance void Transform::set_position`, IL_0509) -
            // at that point the shop root is still a freshly-`new`'d GameObject sitting at the Unity
            // default of (0,0,0), so this bakes the NPC's local offset from the root as npcPosition - 0 =
            // npcPosition. Only later does BreachShopTools.PlaceBreachShops (same assembly) Instantiate
            // the registered shop and set the CLONE's root position to BreachShopComp.offset, which is
            // exactly the `position` argument we pass here (`stfld ... BreachShopComp::offset` reads
            // ldarg.2, i.e. `position`, at IL_04bb-04c1). Instantiate preserves each child's local
            // transform, so Daifuku's final WORLD position is position + npcPosition.
            // Before this fix both were PlutoConfig.StallPosition, so Daifuku ended up at
            // StallPosition + StallPosition (~doubled distance from the Breach origin - roughly (39.4,
            // 44.2) against his own props at (19.7, 22.1), about 28 tiles apart) while the props (placed
            // by the separate method below that is not subject to this double-application) stayed put -
            // explaining why Daifuku read as simply absent and nothing near the stall was interactable.
            // Passing Vector3.zero here makes Daifuku's local offset from the shop root
            // zero, so his final world position is just `position` - i.e. PlutoConfig.StallPosition,
            // same as the props. This also fixes pluto_stall's "here"/<x> <y> path (MoveStall, below):
            // it sets _shopObject.transform.position directly, and with npcPosition zero the NPC's local
            // offset from that root is (0,0,0), so it lands exactly on the new position instead of a
            // further PlutoConfig.StallPosition away from it.
            GameObject shop = ShopAPI.SetUpFoyerShop(
                "Daifuku", ShopPrefix,
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
                new Vector3(0f, DaifukuBehindCounter, 0f),   // talkPointOffset: follow him behind the
                                            // counter, so the talk prompt is where he is and not on the
                                            // counter's ground line. 2.20.4 logged SpeechPoint at the
                                            // same place as the NPC, so these two want to agree.
                new Vector3(0f, DaifukuBehindCounter, 0f),   // npcPosition: his LOCAL offset from the shop
                                            // root at build time (see the comment above this call), never
                                            // a second copy of the world position. A tile of +Y stands
                                            // him behind his own counter instead of inside it.
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

            _shopObject = shop;
            Plugin.Log("shrine stall: registered at " + PlutoConfig.StallPosition);

            if (_foyerHandler == null)
            {
                _foyerHandler = PlaceBackdropProps;
                DungeonHooks.OnFoyerAwake += _foyerHandler;
            }
            PlaceIfFoyerAlreadyUp();
            PlaceBackdropProps();

            if (!_commandRegistered)
            {
                RegisterConsoleCommand();
                _commandRegistered = true;
            }
        }

        /// <summary>
        /// pluto_stall console command (2.20.1): the (10.5, 22.1) launch default ran the whole assembly
        /// off-screen in the Breach and nobody testing it could see the Breach to pick a better one by eye.
        /// This lets the user walk to the right spot in-game and place it live, no restart required:
        ///   pluto_stall            - report the current position and footprint (no move)
        ///   pluto_stall here       - move the whole assembly to the player's current position
        ///   pluto_stall &lt;x&gt; &lt;y&gt;   - move it to explicit coordinates
        ///   pluto_stall save       - write the current position back to the config file
        /// </summary>
        private static void RegisterConsoleCommand()
        {
            ETGModConsole.Commands.AddUnit("pluto_stall", args =>
            {
                if (args == null || args.Length == 0)
                {
                    ReportStallStatus();
                    return;
                }

                if (args.Length == 1 && string.Equals(args[0], "save", StringComparison.OrdinalIgnoreCase))
                {
                    if (PlutoConfig.PersistStallPosition())
                        Plugin.Log("shrine stall: saved " + FormatPos(PlutoConfig.StallPosition) + " to the config file.");
                    else
                        Plugin.Log("shrine stall: could not save (config not bound yet) - put StallPosition = "
                            + FormatPos(PlutoConfig.StallPosition) + " in the config file by hand.");
                    return;
                }

                Vector3 target;
                if (args.Length == 1 && string.Equals(args[0], "here", StringComparison.OrdinalIgnoreCase))
                {
                    PlayerController player = GameManager.HasInstance ? GameManager.Instance.PrimaryPlayer : null;
                    if (player == null)
                    {
                        Plugin.Log("shrine stall: no player found (are you in the Breach?)");
                        return;
                    }
                    Vector2 at = player.CenterPosition;
                    target = new Vector3(at.x, at.y, 0f);
                }
                else if (args.Length == 2
                    && float.TryParse(args[0], NumberStyles.Float, CultureInfo.InvariantCulture, out float x)
                    && float.TryParse(args[1], NumberStyles.Float, CultureInfo.InvariantCulture, out float y))
                {
                    target = new Vector3(x, y, 0f);
                }
                else
                {
                    Plugin.Log("shrine stall: usage - pluto_stall (report) | pluto_stall here | pluto_stall <x> <y> | pluto_stall save");
                    return;
                }

                MoveStall(target);
            });
        }

        /// <summary>
        /// Moves the whole assembly - Daifuku's NPC GameObject AND the three backdrop props - to a new
        /// position, in memory only (the config file is untouched until "pluto_stall save"). Daifuku only
        /// moves if the shop has actually been built this session (_shopObject != null); the props always
        /// move because PlaceBackdropProps() re-reads PlutoConfig.StallPosition, which this always updates.
        /// </summary>
        private static void MoveStall(Vector3 newPosition)
        {
            PlutoConfig.StallPosition = newPosition;

            // The template's offset is what PlaceBreachShops reads on the NEXT foyer load, so it has to be
            // rewritten whether or not a live clone exists right now. 2.20.5 only did this inside the
            // live-shop branch, and the tester's reload caught it: pluto_stall here had run while no clone
            // existed yet (before the foyer race was understood), so the template kept its old offset and
            // the reload placed the clone at 19.7,22.1 while the config said 19.75,19.688. The type is
            // internal to Alexandria, so this goes through reflection; ReconcileLiveShopPosition() below
            // is the backstop that makes a move stick even if that reflection ever stops working.
            SetBreachOffset(_shopObject, newPosition);

            GameObject live = FindLiveShop();
            if (live != null)
            {
                live.transform.position = newPosition;
                SetBreachOffset(live, newPosition);
            }
            else
            {
                Plugin.Log("shrine stall: no live shop found in the scene - only the backdrop props were "
                    + "moved. Daifuku is placed by Alexandria on foyer load; reload the Breach to move him too.");
            }

            PlaceBackdropProps();
            Plugin.Log("shrine stall: moved to " + FormatPos(newPosition)
                + " - put StallPosition = " + FormatPos(newPosition) + " in the config to keep it, or type pluto_stall save.");
            LogFootprint();
        }

        private static void ReportStallStatus()
        {
            Plugin.Log("shrine stall: currently at " + FormatPos(PlutoConfig.StallPosition));
            LogFootprint();
        }

        /// <summary>Logs how far left/right of StallPosition the assembly's four pieces (Daifuku at
        /// offset zero, torii, stall, Kinsuke) reach, so the user can tell whether it now fits on screen.</summary>
        private static void LogFootprint()
        {
            // Real drawn extents, not just anchor offsets: every prop is bottom-CENTER pivoted, so each
            // one reaches half its art width either side of its own offset. The gate is the widest at
            // 78px/16 = 4.875 tiles, so it sets both edges now that everything shares a center. Reporting
            // anchors alone understated the width and made the stall look like it fitted where it did not.
            const float ToriiHalf = 78f / 16f / 2f;     // 2.4375
            const float StallHalf = 48f / 16f / 2f;     // 1.5
            const float KinsukeHalf = 22f / 16f / 2f;   // 0.6875
            const float DaifukuHalf = 26f / 16f / 2f;   // 0.8125
            float[] lefts = { -DaifukuHalf, ToriiOffset.x - ToriiHalf, StallOffset.x - StallHalf, KinsukeOffset.x - KinsukeHalf };
            float[] rights = { DaifukuHalf, ToriiOffset.x + ToriiHalf, StallOffset.x + StallHalf, KinsukeOffset.x + KinsukeHalf };
            float minOffset = lefts[0], maxOffset = rights[0];
            foreach (float edge in lefts) if (edge < minOffset) minOffset = edge;
            foreach (float edge in rights) if (edge > maxOffset) maxOffset = edge;
            float left = PlutoConfig.StallPosition.x + minOffset;
            float right = PlutoConfig.StallPosition.x + maxOffset;
            Plugin.Log("shrine stall: footprint spans x=" + left.ToString("0.##", CultureInfo.InvariantCulture)
                + " to x=" + right.ToString("0.##", CultureInfo.InvariantCulture)
                + " at y=" + PlutoConfig.StallPosition.y.ToString("0.##", CultureInfo.InvariantCulture));
        }

        private static string FormatPos(Vector3 v)
        {
            return v.x.ToString("0.###", CultureInfo.InvariantCulture) + "," + v.y.ToString("0.###", CultureInfo.InvariantCulture);
        }

        /// <summary>Unhooks the foyer handler and drops the placed props. Safe to call if Init() never ran.</summary>
        public static void Teardown()
        {
            if (_foyerHandler != null)
            {
                DungeonHooks.OnFoyerAwake -= _foyerHandler;
                _foyerHandler = null;
            }
            _shopObject = null;
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
            PlaceProp(new[] { "torii.png" }, PlutoConfig.StallPosition + ToriiOffset, "pluto_shrine_stall_torii", ToriiHeightOffGround);
            PlaceProp(new[] { "stall.png" }, PlutoConfig.StallPosition + StallOffset, "pluto_shrine_stall_stall", StallHeightOffGround);
            PlaceProp(
                new[] { "kinsuke_idle_001.png", "kinsuke_idle_002.png", "kinsuke_idle_003.png", "kinsuke_idle_004.png" },
                PlutoConfig.StallPosition + KinsukeOffset, "pluto_shrine_stall_kinsuke", KinsukeHeightOffGround);

            // 2.20.4 diagnostic (tester's ask, and the controller's follow-up after a fresh look at the
            // screenshots ruled out the small pale cat - that is stall.png's own painted maneki-neko, not
            // a stray sprite - and ruled out the narrow white bar being Daifuku himself, since in 2.20.0 he
            // was 28 tiles away yet the bar was already there beside the torii). This turns "the
            // shopkeeper is missing" / "there is an unexplained white bar" into hard data on the very next
            // run instead of another round of screenshots and guessing.
            ReconcileLiveShopPosition();
            LogShopDiagnostics();
        }

        /// <summary>Destroys the props placed by the previous foyer load. The flipbook dies with its object.</summary>
        private static void DestroyProps()
        {
            foreach (GameObject prop in Props)
                if (prop != null) UnityEngine.Object.Destroy(prop);
            Props.Clear();
        }

        /// <summary>
        /// A non-interactive decorative sprite: no collider, bottom-center pivot, tk2d depth (see the
        /// HeightOffGround comment above the three *HeightOffGround constants). One frame is static; more
        /// than one gets a PropFlipbook. Sprite ids are cached in the shared item collection because this
        /// runs on every foyer load and re-adding the same PNG would otherwise leak a collection entry
        /// (and a texture) per visit.
        /// </summary>
        private static void PlaceProp(string[] fileNames, Vector3 position, string objectName, float heightOffGround)
        {
            int[] ids = new int[fileNames.Length];
            for (int i = 0; i < fileNames.Length; i++)
            {
                ids[i] = LoadSpriteId(fileNames[i]);
                if (ids[i] < 0) return;   // LoadSpriteId already logged which resource is missing
            }

            GameObject obj = new GameObject(objectName);
            tk2dSprite sprite = obj.AddComponent<tk2dSprite>();
            sprite.SetSprite(SpriteBuilder.itemCollection, ids[0]);
            sprite.PlaceAtPositionByAnchor(position, tk2dBaseSprite.Anchor.LowerCenter);
            obj.transform.position = obj.transform.position.Quantize(1f / 16f);
            sprite.HeightOffGround = heightOffGround;
            sprite.UpdateZDepth();
            if (ids.Length > 1) obj.AddComponent<PropFlipbook>().Begin(SpriteBuilder.itemCollection, ids, KinsukeFps);
            Props.Add(obj);

            Vector3 resolved = obj.transform.position;
            Plugin.Log("shrine stall: prop '" + objectName + "' resolved to " + FormatPos(resolved)
                + ",z=" + resolved.z.ToString("0.###", CultureInfo.InvariantCulture)
                + " depth(heightOffGround)=" + heightOffGround.ToString("0.##", CultureInfo.InvariantCulture));
        }

        private static int LoadSpriteId(string fileName)
        {
            int cached;
            if (SpriteIdCache.TryGetValue(fileName, out cached)) return cached;

            string resourcePath = Plugin.SHOP_ROOT + "/" + fileName;
            int id = SpriteBuilder.AddSpriteToCollection(resourcePath, SpriteBuilder.itemCollection, typeof(Plugin).Assembly);
            if (id < 0)
            {
                Plugin.Log("shrine stall: missing prop resource " + resourcePath);
                return -1;
            }
            SpriteIdCache[fileName] = id;
            return id;
        }

        /// <summary>
        /// Walks the shopkeeper GameObject's own transform hierarchy and logs one line per child: name,
        /// resolved world position, whether it has a renderer (and if so, whether it is enabled and how
        /// big its world-space bounds are), and whether that renderer's sprite is actually bound (a
        /// tk2dBaseSprite with a null current sprite def, or a SpriteRenderer with a null sprite, is a
        /// silent blank - the "LoadSprite returns null and logs on a missing resource" case, but for
        /// something Alexandria built rather than one of our own props).
        ///
        /// SetUpFoyerShop's GameObject is not just Daifuku: Alexandria parents the NPC, the blueprint
        /// prefab instance, item spawn points and a talk point all under the one root it returns, so this
        /// single walk covers "is Daifuku there and is he drawn behind the counter" (he is one of these
        /// children) AND "what is the narrow white sliver beside the torii" (something else in this same
        /// hierarchy, per the tester's measurement, ~3x58 art px - too thin for any of our own art) in one
        /// pass, without guessing which child is which ahead of time.
        /// </summary>
        /// <summary>
        /// Finds the shop that is actually in the Breach, which is NOT the object SetUpFoyerShop returned.
        ///
        /// Verified in the Alexandria 0.5.10 IL (BreachShopTools::PlaceBreachShops, IL_00a1 onward): on
        /// every foyer load it walks registeredShops.Values and, for each, calls
        /// Object.Instantiate&lt;GameObject&gt;(prefab), SetActive(true) on the clone, then sets the CLONE's
        /// transform.position from its BreachShopComp.offset. The registered object is a template that
        /// stays at the Unity origin for the whole session.
        ///
        /// That is the 2.20.0-2.20.4 bug in one sentence: this file stored the template, so pluto_stall
        /// moved something nothing renders and the diagnostics measured it too - which is why 2.20.4
        /// reported the shop root, Daifuku, all three ItemPoints and the SpeechPoint at 0,0 while the
        /// props sat correctly at the stall position. Daifuku was healthy the whole time (renderer
        /// present, sprite bound, bounds 1.625x2 matching his art exactly); he was just standing on a
        /// template at the origin.
        ///
        /// Matched by component rather than by a "(Clone)" name suffix, so it survives Unity changing how
        /// it names clones, and filtered by our own prefix so another mod's breach shop is never touched.
        /// </summary>
        /// <summary>
        /// Closes the startup race that kept the stall empty for a whole session (2.20.0-2.20.5).
        ///
        /// Alexandria raises DungeonHooks.OnFoyerAwake from exactly one place - its
        /// MainMenuFoyerControllerAwakePatch - and MainMenuFoyerController is the TITLE SCREEN's
        /// controller, which lives in the Breach scene. At launch that Awake fires while the title menu is
        /// up, which is before this mod's Init (it waits for GameManager start). So Alexandria's
        /// PlaceBreachShops ran with our shop not yet registered and placed nothing of ours, and pressing
        /// start does not reload the scene, so no second Awake ever came - which is also why our own
        /// subscribed handler never fired at Breach load. Confirmed on the Steam machine: a forced foyer
        /// reload (`load_level tt_foyer`) produced the live clone, positioned correctly, on the first try.
        ///
        /// So: if the foyer is already up by the time we register, invoke Alexandria's own placement now
        /// rather than waiting for an Awake that has already happened. Its own PlaceBreachShops is used
        /// (rather than cloning the template ourselves) because it also registers the shopkeeper's
        /// TalkDoerLite as a room interactable, which is what makes him talkable. It calls
        /// CleanupBreachShops first, so a later real foyer Awake running it again cannot duplicate him.
        /// </summary>
        private static void PlaceIfFoyerAlreadyUp()
        {
            if (UnityEngine.Object.FindObjectOfType<MainMenuFoyerController>() == null)
            {
                Plugin.Log("shrine stall: foyer not up yet - Alexandria will place the shop on its Awake");
                return;
            }
            if (FindLiveShop() != null) return;   // already placed; nothing to catch up on

            System.Type tools = typeof(ShopAPI).Assembly.GetType("Alexandria.NPCAPI.BreachShopTools");
            System.Reflection.MethodInfo place = tools != null
                ? tools.GetMethod("PlaceBreachShops", System.Reflection.BindingFlags.Public
                    | System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Static)
                : null;
            if (place == null)
            {
                Plugin.Log("shrine stall: foyer was already up at startup but Alexandria's PlaceBreachShops "
                    + "could not be found by reflection - the shop will only appear after the next Breach reload");
                return;
            }
            try
            {
                place.Invoke(null, null);
                Plugin.Log("shrine stall: foyer was already up at startup - placed the shop now instead of "
                    + "waiting for a foyer Awake that already happened");
            }
            catch (Exception e)
            {
                Plugin.Log("shrine stall: placing the shop at startup failed: " + e.GetBaseException().Message);
            }
        }

        /// <summary>
        /// Puts the live clone where the config says, every time the props are placed. PlaceBreachShops
        /// positions the clone from the template's BreachShopComp.offset; if that reflection-written
        /// offset is ever stale or the write silently fails, this is what still makes a pluto_stall move
        /// survive the next Breach load. Cheap and idempotent.
        /// </summary>
        private static void ReconcileLiveShopPosition()
        {
            GameObject live = FindLiveShop();
            if (live == null) return;
            Vector3 want = PlutoConfig.StallPosition;
            if ((live.transform.position - want).sqrMagnitude < 0.0001f) return;
            Plugin.Log("shrine stall: live shop was at " + FormatPos(live.transform.position)
                + " but the config says " + FormatPos(want) + " - moved it");
            live.transform.position = want;
            SetBreachOffset(live, want);
        }

        /// <summary>
        /// Rewrites Alexandria's BreachShopComp.offset, the value PlaceBreachShops positions the clone
        /// from on every foyer load. The component is internal to Alexandria 0.5.10, so it is reached by
        /// reflection over the object's components; a miss is logged once and otherwise ignored, since the
        /// caller has already moved the transform for this session either way.
        /// </summary>
        private static void SetBreachOffset(GameObject target, Vector3 position)
        {
            if (target == null) return;
            foreach (Component component in target.GetComponents<Component>())
            {
                if (component == null || component.GetType().Name != "BreachShopComp") continue;
                System.Reflection.FieldInfo field = component.GetType().GetField("offset");
                if (field != null && field.FieldType == typeof(Vector3)) field.SetValue(component, position);
                return;
            }
            Plugin.Log("shrine stall: no BreachShopComp on '" + target.name + "' - this move lasts only "
                + "until the next Breach load; use pluto_stall save to make it stick.");
        }

        private static GameObject FindLiveShop()
        {
            CustomShopController[] shops = UnityEngine.Object.FindObjectsOfType<CustomShopController>();
            foreach (CustomShopController shop in shops)
            {
                if (shop == null) continue;
                GameObject go = shop.gameObject;
                if (go == _shopObject) continue;                 // the template: registered, never placed
                if (!go.name.StartsWith(ShopPrefix)) continue;    // someone else's breach shop
                return go;
            }
            return null;
        }

        private static void LogShopDiagnostics()
        {
            GameObject live = FindLiveShop();
            if (live == null)
            {
                Plugin.Log("shrine stall: NO LIVE SHOP in the scene"
                    + (_shopObject == null
                        ? " and no template either - SetUpFoyerShop never returned one (see any failure logged above)"
                        : " - the template exists, so registration worked but Alexandria has not placed a clone yet"));
                return;
            }

            Transform[] all = live.GetComponentsInChildren<Transform>(true);
            Plugin.Log("shrine stall: LIVE shop root '" + live.name + "' at " + FormatPos(live.transform.position)
                + " (config says " + FormatPos(PlutoConfig.StallPosition) + ") has " + all.Length + " transform(s)");

            foreach (Transform t in all)
            {
                Renderer renderer = t.GetComponent<Renderer>();
                tk2dBaseSprite tkSprite = t.GetComponent<tk2dBaseSprite>();
                SpriteRenderer plainSprite = t.GetComponent<SpriteRenderer>();

                string spriteState;
                if (tkSprite != null) spriteState = tkSprite.GetCurrentSpriteDef() != null ? "bound" : "UNBOUND";
                else if (plainSprite != null) spriteState = plainSprite.sprite != null ? "bound" : "UNBOUND";
                else spriteState = renderer != null ? "unknown-type" : "n/a";

                Plugin.Log("shrine stall: child '" + t.name + "' at " + FormatPos(t.position)
                    + " renderer=" + (renderer != null ? "present enabled=" + renderer.enabled : "none")
                    + " bounds=" + (renderer != null ? FormatSize(renderer.bounds.size) : "n/a")
                    + " sprite=" + spriteState);
            }
        }

        private static string FormatSize(Vector3 v)
        {
            return v.x.ToString("0.###", CultureInfo.InvariantCulture) + "x"
                + v.y.ToString("0.###", CultureInfo.InvariantCulture) + "x"
                + v.z.ToString("0.###", CultureInfo.InvariantCulture);
        }

        /// <summary>
        /// Advances a tk2dSprite through a set of frames (by sprite id, in the shared item collection) on a
        /// timer, so Kinsuke bobs in his bowl. Lives on the prop's own GameObject, so DestroyProps (and any
        /// scene change) takes it with it. BraveTime.DeltaTime rather than Time.deltaTime, like the rest of
        /// this mod's per-frame components, so the bob follows the game's own time scale.
        /// </summary>
        public sealed class PropFlipbook : MonoBehaviour
        {
            private tk2dSpriteCollectionData collection;
            private int[] frames;
            private float secondsPerFrame;
            private float elapsed;
            private int frame;

            public void Begin(tk2dSpriteCollectionData spriteCollection, int[] clip, float fps)
            {
                collection = spriteCollection;
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

                tk2dSprite sprite = GetComponent<tk2dSprite>();
                if (sprite != null && collection != null) sprite.SetSprite(collection, frames[frame]);
            }
        }
    }
}
