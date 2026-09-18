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
        // The counter and the bowl from the current placement: the counter's measured z is what the shop
        // items must sort in front of, and the bowl's depth is re-logged beside theirs.
        private static tk2dBaseSprite _counterSprite;
        private static tk2dBaseSprite _kinsukeSprite;
        private static readonly Dictionary<string, int> SpriteIdCache = new Dictionary<string, int>();
        private static System.Action _foyerHandler;

        // The NPC GameObject SetUpFoyerShop built, kept so pluto_stall can move Daifuku himself (not just
        // the backdrop props) without a Breach reload. Null until Init() succeeds; cleared by Teardown().
        private static GameObject _shopObject;
        private static bool _commandRegistered;

        /// <summary>Alexandria names the shop root "&lt;prefix&gt;:&lt;name&gt;_Shop" and keys registeredShops by the
        /// same string, so this prefix is how FindLiveShop tells our stall from another mod's.</summary>
        private const string ShopPrefix = "pluto_shrine_stall";

        // ---- Layout: the 2026-09-18 redesign, user-approved "as shown", item slots raised 2 px ----
        // Contract: .superpowers/sdd/2026-09-18-shrine-stall-redesign/art-spec.md section 5, the scene
        // docs/art-preview/mockup-2026-09-18/mockup.py rendered. Every number is art pixels over 16 (px per
        // tile) in the COUNTER FRAME: origin = the counter's bottom-centre = the shop root R (the live
        // clone's transform, i.e. PlutoConfig.StallPosition), x right, y up; +y is also "further back".
        // History that still applies: PlaceBreachShops puts the live clone's root exactly at StallPosition
        // (2.20.5), and nothing may be laid out relative to the template, which stays at the origin.
        //
        // Props are placed LowerCenter (PlaceProp), so each offset IS that sprite's bottom-centre; tk2d then
        // reports the prop's transform at the sprite's lower-left.
        private static readonly Vector3 StallOffset = new Vector3(0f / 16f, 0f / 16f, 0f);      // counter 104x23
        private static readonly Vector3 ToriiOffset = new Vector3(0f / 16f, 24f / 16f, 0f);     // torii 136x56, 24 px behind the counter; posts clear both ends
        private static readonly Vector3 KinsukeOffset = new Vector3(42f / 16f, 17f / 16f, 0f);  // bowl 12x14 on the counter top, 21 px right of Daifuku

        // Daifuku (26x32, unchanged art). SetUpFoyerShop's npcPosition is his LOCAL offset from the shop
        // root, not a world position (Alexandria sets it while the root is still at the origin, then
        // parents: the 2.20.2 double-offset bug), and it is his sprite's LOWER-LEFT (SpriteFromResource
        // builds the sprite from (0,0); archaeology 1.9, consistent with every 2.20.x measurement). His
        // bottom-centre, canvas column 13, goes to (+21, +21): his sleeve-paws rest on the counter's back
        // edge and only his hem (bottom 2 rows) is hidden behind it.
        private const float DaifukuAnchorColumn = 13f;
        private static readonly Vector3 DaifukuNpcPosition = new Vector3((21f - DaifukuAnchorColumn) / 16f, 21f / 16f, 0f);
        // talkPointOffset is relative to DAIFUKU, not the root (archaeology 1.3): centred over him, 3 px
        // above his 32-px canvas - the same point as Alexandria's own default (0.8125, 2.1875).
        private static readonly Vector3 DaifukuTalkPointOffset = new Vector3(DaifukuAnchorColumn / 16f, 35f / 16f, 0f);

        // Item slots. Alexandria centres each shop item (Anchor.MiddleCenter) on its ItemPoint, and the foyer
        // meta-shop draws blueprint.png (the 14x16 ema plaque) in every slot, so an ItemPoint is the slot's
        // bottom-centre plus half the plaque's height. Bottom-centres (-40,+18), (-21,+18), (-2,+18): the
        // art-spec's +16 raised 2 px so the crimson mats show under the plaques. The 2.20.7 default points
        // put two of the three items past the counter's end. z = 1 like Alexandria's defaults (UpdateZDepth
        // rewrites it). Never pass null here: Alexandria then throws inside its try/catch and returns no shop.
        private const float PlaqueHeight = 16f;
        private static readonly Vector3[] ItemPositions =
        {
            new Vector3(-40f / 16f, (18f + PlaqueHeight / 2f) / 16f, 1f),
            new Vector3(-21f / 16f, (18f + PlaqueHeight / 2f) / 16f, 1f),
            new Vector3(-2f / 16f, (18f + PlaqueHeight / 2f) / 16f, 1f),
        };

        // ---- Depth ----
        //     z = worldY - HeightOffGround        (lower z draws IN FRONT; derived from our 2.20.4 logs)
        // worldY is each sprite's bottom edge (its lower-left transform). At R.y = 0, back to front:
        //     torii    24/16 - 0     = +1.5
        //     Daifuku  21/16 - 0     = +1.3125   (Alexandria leaves his HeightOffGround at the default)
        //     counter   0    - 0     =  0
        //     bowl     17/16 - 18/16 = -0.0625
        //     items    18/16 - 19/16 = -0.0625   (sprite bottom = ItemPoint.y - PlaqueHeight / 2)
        // The torii and Daifuku sort correctly from their anchors alone. The bowl and the plaques stand on
        // the counter's top face, ABOVE its anchor on screen, so by y alone they would sort behind the
        // counter (and Alexandria forces every foyer item to -1.25, pushing them further back; 2.20.7 had
        // the bowl over Daifuku for the same reason in reverse). Each is lifted exactly enough to sit one
        // pixel of depth in front of the counter and no more, so a player standing at the counter front
        // (z = his feet, below R.y) still draws in front of the goods. The item value is applied to the live
        // items after DoSetup, see RefreshLiveShopDepth.
        private const float ToriiHeightOffGround = 0f;
        private const float StallHeightOffGround = 0f;
        private const float KinsukeHeightOffGround = 18f / 16f;
        private const float ShopItemHeightOffGround = 19f / 16f;

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

            // Stock root cause (2026-09-18): LootUtility.CreateLootTable, never a bare CreateInstance. The live
            // clone's BaseShopController.Start -> HandleDelayedFoyerInitialization calls DoSetup once a
            // character is picked, and Alexandria's DoSetup calls shopItems.GetCompiledRawItems() for every
            // slot (CustomShopController::DoSetup IL_02ab). Vanilla GenericLootTable.GetCompiledCollection
            // reads includedLootTables.Count unconditionally, and a bare ScriptableObject.CreateInstance leaves
            // that list (and tablePrerequisites) null: DoSetup threw a NullReferenceException before
            // stocking a single slot, logged by Unity only - "i dont see anything to buy". CreateLootTable
            // (Alexandria 0.5.10 IL) initialises defaultItemDrops, includedLootTables and tablePrerequisites.
            GenericLootTable table = LootUtility.CreateLootTable();
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

            // Position arguments (Alexandria 0.5.10 IL, archaeology 1.2): `position` becomes BreachShopComp.offset,
            // where PlaceBreachShops puts the live clone's root; npcPosition and itemPositions are LOCAL offsets
            // from that root (written while the root sits at the origin, then parented - 2.20.2 put
            // StallPosition in npcPosition and Daifuku landed ~28 tiles away); talkPointOffset is relative to
            // Daifuku himself. The values are the counter-frame layout above.
            LogLootTable(table);

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
                DaifukuTalkPointOffset,     // talkPointOffset: relative to Daifuku, over his head
                DaifukuNpcPosition,         // npcPosition: his LOCAL lower-left inside the shop root, behind the counter
                ShopAPI.VoiceBoxes.BELLO,
                ItemPositions,              // itemPositions: on the counter top (never null, see ItemPositions)
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
        ///   pluto_stall stock      - log what the live shop actually stocked, slot by slot
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

                if (args.Length == 1 && string.Equals(args[0], "stock", StringComparison.OrdinalIgnoreCase))
                {
                    GameObject live = FindLiveShop();
                    if (live == null) Plugin.Log("shrine stall: stock - no live shop in the scene");
                    else LogStock(live, "on request");
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
                    Plugin.Log("shrine stall: usage - pluto_stall (report) | pluto_stall here | pluto_stall <x> <y> | pluto_stall save | pluto_stall stock");
                    return;
                }

                MoveStall(target);
            });

            // Read-only: logs where the player stands so layout landmarks (the Breach shop door, the
            // walkway) can be measured in world tiles without moving anything. pluto_here is the same
            // reading under the name testers reach for (2.20.7); `pluto_stall here` is the one that MOVES.
            ETGModConsole.Commands.AddUnit("pluto_where", args => ReportWhere("pluto_where"));
            ETGModConsole.Commands.AddUnit("pluto_here", args => ReportWhere("pluto_here"));
        }

        private static void ReportWhere(string command)
        {
            PlayerController player = GameManager.HasInstance ? GameManager.Instance.PrimaryPlayer : null;
            if (player == null)
            {
                Plugin.Log(command + ": no player found");
                return;
            }
            Vector2 at = player.CenterPosition;
            Vector2 feet = player.specRigidbody != null ? player.specRigidbody.UnitBottomCenter : at;
            Plugin.Log(command + ": center " + FormatPos(new Vector3(at.x, at.y, 0f))
                + " feet " + FormatPos(new Vector3(feet.x, feet.y, 0f))
                + " stall " + FormatPos(PlutoConfig.StallPosition));
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

        /// <summary>Logs how far the assembly's four pieces (torii, counter, Daifuku, Kinsuke) reach around
        /// StallPosition, so the user can tell whether it fits where it stands.</summary>
        private static void LogFootprint()
        {
            // Real drawn extents, not just anchors: each piece reaches half its art width either side of its
            // bottom-centre. The 136-px torii sets both edges; the stall is 8.5 x 5 tiles (art-spec D3).
            const float ToriiHalf = 136f / 16f / 2f;    // 4.25
            const float StallHalf = 104f / 16f / 2f;    // 3.25
            const float KinsukeHalf = 12f / 16f / 2f;   // 0.375
            const float DaifukuHalf = 26f / 16f / 2f;   // 0.8125
            const float ToriiHeight = 56f / 16f;        // 3.5, standing 1.5 behind the counter's ground line
            float daifukuX = DaifukuNpcPosition.x + DaifukuAnchorColumn / 16f;
            float[] lefts = { daifukuX - DaifukuHalf, ToriiOffset.x - ToriiHalf, StallOffset.x - StallHalf, KinsukeOffset.x - KinsukeHalf };
            float[] rights = { daifukuX + DaifukuHalf, ToriiOffset.x + ToriiHalf, StallOffset.x + StallHalf, KinsukeOffset.x + KinsukeHalf };
            float minOffset = lefts[0], maxOffset = rights[0];
            foreach (float edge in lefts) if (edge < minOffset) minOffset = edge;
            foreach (float edge in rights) if (edge > maxOffset) maxOffset = edge;
            float left = PlutoConfig.StallPosition.x + minOffset;
            float right = PlutoConfig.StallPosition.x + maxOffset;
            float bottom = PlutoConfig.StallPosition.y + StallOffset.y;
            float top = PlutoConfig.StallPosition.y + ToriiOffset.y + ToriiHeight;
            Plugin.Log("shrine stall: footprint spans x=" + left.ToString("0.##", CultureInfo.InvariantCulture)
                + " to x=" + right.ToString("0.##", CultureInfo.InvariantCulture)
                + ", y=" + bottom.ToString("0.##", CultureInfo.InvariantCulture)
                + " to y=" + top.ToString("0.##", CultureInfo.InvariantCulture));
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
            // Back to front, as in the approved mockup (the draw order itself comes from z, see Depth above).
            PlaceProp(new[] { "torii.png" }, PlutoConfig.StallPosition + ToriiOffset, "pluto_shrine_stall_torii", ToriiHeightOffGround);
            _counterSprite = SpriteOf(PlaceProp(new[] { "stall.png" }, PlutoConfig.StallPosition + StallOffset, "pluto_shrine_stall_stall", StallHeightOffGround));
            _kinsukeSprite = SpriteOf(PlaceProp(
                new[] { "kinsuke_idle_001.png", "kinsuke_idle_002.png", "kinsuke_idle_003.png", "kinsuke_idle_004.png" },
                PlutoConfig.StallPosition + KinsukeOffset, "pluto_shrine_stall_kinsuke", KinsukeHeightOffGround));

            // 2.20.4 diagnostic (tester's ask): logs the live shop's whole hierarchy on every placement, so
            // "the shopkeeper is missing" or an unexplained sprite is hard data on the next run instead of
            // another round of screenshots and guessing.
            ReconcileLiveShopPosition();
            // After the clone is where the config says: a move or reconcile shifts its children in y
            // without touching their z, and the shop items (once DoSetup has stocked them) need their lift.
            RefreshLiveShopDepth(FindLiveShop(), "placement");
            LogShopDiagnostics();
            AttachStockProbe();
        }

        /// <summary>Destroys the props placed by the previous foyer load. The flipbook dies with its object.</summary>
        private static void DestroyProps()
        {
            foreach (GameObject prop in Props)
                if (prop != null) UnityEngine.Object.Destroy(prop);
            Props.Clear();
            _counterSprite = null;
            _kinsukeSprite = null;
        }

        private static tk2dBaseSprite SpriteOf(GameObject prop)
        {
            return prop != null ? prop.GetComponent<tk2dBaseSprite>() : null;
        }

        /// <summary>
        /// A non-interactive decorative sprite: no collider, bottom-center pivot, tk2d depth (see the
        /// Depth comment above the *HeightOffGround constants). One frame is static; more
        /// than one gets a PropFlipbook. Sprite ids are cached in the shared item collection because this
        /// runs on every foyer load and re-adding the same PNG would otherwise leak a collection entry
        /// (and a texture) per visit. Returns the prop, or null if a frame's resource is missing.
        /// </summary>
        private static GameObject PlaceProp(string[] fileNames, Vector3 position, string objectName, float heightOffGround)
        {
            int[] ids = new int[fileNames.Length];
            for (int i = 0; i < fileNames.Length; i++)
            {
                ids[i] = LoadSpriteId(fileNames[i]);
                if (ids[i] < 0) return null;   // LoadSpriteId already logged which resource is missing
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
                + " depth(heightOffGround)=" + heightOffGround.ToString("0.####", CultureInfo.InvariantCulture)
                + " centre " + FormatPos(sprite.WorldCenter));
            return obj;
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
        /// Puts the live shop's sprites at the depth the approved layout needs (see Depth, above), and logs
        /// each one's centre, z and HeightOffGround so the in-game order can be read straight off the log.
        ///
        /// Shop items: Alexandria's CustomShopItemController.Initialize forces HeightOffGround -1.25 on every
        /// foyer item (IL, archaeology 1.5), which sorts plaques standing on the counter top BEHIND the
        /// counter. The items only exist once DoSetup has run (after character select), so this runs from
        /// the stock probe as well as on every placement. A move/reconcile shifts the clone in y, and its
        /// children keep their old world z until UpdateZDepth, so Daifuku (HeightOffGround untouched) is
        /// refreshed too. Backstop: z = y - HeightOffGround is measured, but whether tk2d takes y from an
        /// item's transform or its trimmed bounds is not; if an item still reads at or behind the counter's
        /// actual z, it is lifted by the measured difference plus one pixel, and that is logged.
        /// </summary>
        private static void RefreshLiveShopDepth(GameObject live, string when)
        {
            if (live == null) return;

            TalkDoerLite daifuku = live.GetComponentInChildren<TalkDoerLite>(true);
            tk2dBaseSprite daifukuSprite = daifuku != null ? daifuku.GetComponent<tk2dBaseSprite>() : null;
            if (daifukuSprite != null)
            {
                daifukuSprite.UpdateZDepth();
                Plugin.Log("shrine stall: depth (" + when + ") Daifuku " + DescribeDepth(daifukuSprite));
            }

            float counterZ = _counterSprite != null ? _counterSprite.transform.position.z : float.NaN;
            CustomShopController shop = live.GetComponent<CustomShopController>();
            Transform[] points = shop != null ? shop.spawnPositions : null;
            int items = 0;
            for (int i = 0; points != null && i < points.Length; i++)
            {
                CustomShopItemController slot = points[i] != null ? points[i].GetComponentInChildren<CustomShopItemController>(true) : null;
                tk2dBaseSprite sprite = slot != null ? slot.GetComponent<tk2dBaseSprite>() : null;
                if (sprite == null) continue;
                items++;
                sprite.HeightOffGround = ShopItemHeightOffGround;
                sprite.UpdateZDepth();
                float z = sprite.transform.position.z;
                if (!float.IsNaN(counterZ) && z >= counterZ)
                {
                    float lift = z - counterZ + 1f / 16f;
                    Plugin.Log("shrine stall: depth (" + when + ") shop item " + i + " still sorted behind the counter (z "
                        + z.ToString("0.####", CultureInfo.InvariantCulture) + " >= counter "
                        + counterZ.ToString("0.####", CultureInfo.InvariantCulture) + ") - lifting it by "
                        + lift.ToString("0.####", CultureInfo.InvariantCulture));
                    sprite.HeightOffGround += lift;
                    sprite.UpdateZDepth();
                }
                Plugin.Log("shrine stall: depth (" + when + ") shop item " + i + " " + DescribeDepth(sprite));
            }
            if (items == 0)
                Plugin.Log("shrine stall: depth (" + when + ") - no shop items yet (expected before character select: "
                    + "DoSetup stocks the slots once a character is picked, and the stock probe re-runs this then)");

            if (_kinsukeSprite != null)
                Plugin.Log("shrine stall: depth (" + when + ") Kinsuke's bowl " + DescribeDepth(_kinsukeSprite));
            if (_counterSprite != null)
                Plugin.Log("shrine stall: depth (" + when + ") counter " + DescribeDepth(_counterSprite));
        }

        private static string DescribeDepth(tk2dBaseSprite sprite)
        {
            return "centre " + FormatPos(sprite.WorldCenter)
                + " z=" + sprite.transform.position.z.ToString("0.####", CultureInfo.InvariantCulture)
                + " heightOffGround=" + sprite.HeightOffGround.ToString("0.####", CultureInfo.InvariantCulture);
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
                    + " z=" + t.position.z.ToString("0.####", CultureInfo.InvariantCulture)
                    + (tkSprite != null ? " heightOffGround=" + tkSprite.HeightOffGround.ToString("0.####", CultureInfo.InvariantCulture) : "")
                    + " renderer=" + (renderer != null ? "present enabled=" + renderer.enabled : "none")
                    + " bounds=" + (renderer != null ? FormatSize(renderer.bounds.size) : "n/a")
                    + " sprite=" + spriteState);
            }
        }

        /// <summary>
        /// Registration-time half of the stock report: every entry of the loot table handed to
        /// SetUpFoyerShop, with its price (the entry weight, which DoSetup rounds into the price) and whether
        /// its prerequisites are met right now (met = unlocked = DoSetup will NOT stock it). Also reports the
        /// two lists whose null-ness broke 2.20.0-2.20.6, so a regression is one grep away.
        /// </summary>
        private static void LogLootTable(GenericLootTable table)
        {
            if (table == null || table.defaultItemDrops == null || table.defaultItemDrops.elements == null)
            {
                Plugin.Log("shrine stall: loot table is NULL or has no element list - the shop can stock nothing");
                return;
            }
            List<WeightedGameObject> entries = table.defaultItemDrops.elements;
            Plugin.Log("shrine stall: loot table has " + entries.Count + " entr" + (entries.Count == 1 ? "y" : "ies")
                + " (includedLootTables " + (table.includedLootTables == null ? "NULL" : "ok")
                + ", tablePrerequisites " + (table.tablePrerequisites == null ? "NULL" : "ok") + ")");
            foreach (WeightedGameObject entry in entries)
            {
                if (entry == null) { Plugin.Log("shrine stall: loot table entry NULL"); continue; }
                GameObject go = entry.gameObject;
                PickupObject pickup = go != null ? go.GetComponent<PickupObject>() : null;
                Plugin.Log("shrine stall: loot table entry pickup " + entry.pickupId + " " + DescribePickup(pickup)
                    + " price " + Mathf.RoundToInt(entry.weight) + " " + DescribePrereqs(pickup));
            }
        }

        /// <summary>
        /// Stock half of the report: what DoSetup actually put in each slot of the LIVE shop. DoSetup builds
        /// a "Shop item N" child under each ItemPoint with a CustomShopItemController whose `item` is the
        /// blueprint clone (not the real cat item - see OnPurchase), so the real item is recovered from the
        /// clone's SaveFlagToSetOnAcquisition, the one field DoSetup copies from our FLAG prerequisite.
        /// m_shopItems / m_itemControllers are protected in the real game (the stub is publicized), so they
        /// are read by reflection; null means DoSetup has not run on this clone (or threw before assigning).
        /// </summary>
        private static void LogStock(GameObject live, string when)
        {
            CustomShopController shop = live != null ? live.GetComponent<CustomShopController>() : null;
            if (shop == null)
            {
                Plugin.Log("shrine stall: stock (" + when + ") - no CustomShopController on the live shop");
                return;
            }
            System.Collections.IList chosen = ReadField(shop, "m_shopItems") as System.Collections.IList;
            System.Collections.IList controllers = ReadField(shop, "m_itemControllers") as System.Collections.IList;
            Transform[] points = shop.spawnPositions;
            Plugin.Log("shrine stall: stock (" + when + ") on '" + live.name + "': DoSetup "
                + (chosen == null
                    ? "has NOT run yet (m_shopItems null) - expected before character select: DoSetup stocks the "
                        + "slots once a character is picked, so EMPTY slots below are normal until then"
                    : "chose " + chosen.Count + " item(s)")
                + ", item controllers " + (controllers == null ? "NULL (DoSetup did not finish)" : controllers.Count.ToString())
                + ", slots " + (points == null ? 0 : points.Length)
                + ", loot table " + (shop.shopItems == null ? "NULL" : "entries=" + (shop.shopItems.defaultItemDrops == null
                    || shop.shopItems.defaultItemDrops.elements == null ? -1 : shop.shopItems.defaultItemDrops.elements.Count)
                    + " includedLootTables=" + (shop.shopItems.includedLootTables == null ? "NULL" : "ok")));
            if (points == null) return;

            for (int i = 0; i < points.Length; i++)
            {
                Transform point = points[i];
                CustomShopItemController slot = point != null ? point.GetComponentInChildren<CustomShopItemController>(true) : null;
                GameObject choice = chosen != null && i < chosen.Count ? chosen[i] as GameObject : null;
                PickupObject chosenPickup = choice != null ? choice.GetComponent<PickupObject>() : null;
                if (slot == null)
                {
                    Plugin.Log("shrine stall: stock slot " + i + " EMPTY (no shop item under "
                        + (point != null ? point.name : "null point") + "); DoSetup chose "
                        + (chosenPickup != null ? DescribePickup(chosenPickup) + " " + DescribePrereqs(chosenPickup) : "nothing"));
                    continue;
                }
                PickupObject shown = slot.item;
                string realId = null;
                if (shown != null)
                    foreach (string id in PlutoUnlocks.Ids)
                        if (PlutoUnlocks.IsRegistered(id) && shown.SaveFlagToSetOnAcquisition == PlutoUnlocks.Flag(id)) { realId = id; break; }
                PickupObject real = realId != null && Game.Items.ContainsID(realId) ? Game.Items[realId] : chosenPickup;
                Plugin.Log("shrine stall: stock slot " + i + " " + (real != null ? DescribePickup(real) : "unidentified")
                    + " shown as " + DescribePickup(shown)
                    + " price " + slot.CurrentPrice + " (" + slot.CurrencyType + ")"
                    + " " + DescribePrereqs(real)
                    + " active=" + slot.gameObject.activeInHierarchy);
            }
        }

        private static object ReadField(object target, string name)
        {
            for (System.Type t = target.GetType(); t != null; t = t.BaseType)
            {
                System.Reflection.FieldInfo f = t.GetField(name, System.Reflection.BindingFlags.Instance
                    | System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.NonPublic);
                if (f != null) return f.GetValue(target);
            }
            return null;
        }

        private static string DescribePickup(PickupObject pickup)
        {
            if (pickup == null) return "(null pickup)";
            return "id " + pickup.PickupObjectId + " '" + (pickup.EncounterNameOrDisplayName ?? pickup.name) + "'";
        }

        private static string DescribePrereqs(PickupObject pickup)
        {
            if (pickup == null) return "prereqs n/a";
            EncounterTrackable et = pickup.encounterTrackable;
            if (et == null) return "prereqs NO-ENCOUNTERTRACKABLE (DoSetup would throw on this entry)";
            int n = et.prerequisites == null ? 0 : et.prerequisites.Length;
            return "prereqs met=" + et.PrerequisitesMet() + " (" + n + " prerequisite(s); met = unlocked = not stocked)";
        }

        /// <summary>Puts a StockProbe on the live clone; the clone (and its probe) dies with the scene.</summary>
        private static void AttachStockProbe()
        {
            GameObject live = FindLiveShop();
            if (live == null || live.GetComponent<StockProbe>() != null) return;
            live.AddComponent<StockProbe>();
        }

        /// <summary>
        /// Runs LogStock once DoSetup can have run. For a FOYER_META shop vanilla BaseShopController.Start
        /// starts HandleDelayedFoyerInitialization, which waits while GameManager.IsSelectingCharacter or
        /// PrimaryPlayer is null and THEN calls DoSetup - so a placement-time report can only ever say
        /// "not run yet". This waits for the same condition plus a short grace period, logs once, and also
        /// logs if it gave up waiting, so a missing report is never silent.
        /// </summary>
        public sealed class StockProbe : MonoBehaviour
        {
            private const float GraceSeconds = 1.5f;
            private const float GiveUpSeconds = 600f;
            private float readyFor;
            private float waited;
            private bool done;

            private void Update()
            {
                if (done) return;
                waited += Time.unscaledDeltaTime;
                bool ready = GameManager.HasInstance && !GameManager.Instance.IsSelectingCharacter
                    && GameManager.Instance.PrimaryPlayer != null;
                if (ready) readyFor += Time.unscaledDeltaTime;
                if (ready && readyFor >= GraceSeconds)
                {
                    done = true;
                    RefreshLiveShopDepth(gameObject, "after character select");   // DoSetup has stocked the items now
                    LogStock(gameObject, "after character select");
                }
                else if (waited >= GiveUpSeconds)
                {
                    done = true;
                    Plugin.Log("shrine stall: stock probe gave up after " + GiveUpSeconds + "s - no character was "
                        + "selected; type pluto_stall stock to report it by hand");
                    RefreshLiveShopDepth(gameObject, "probe timeout");
                    LogStock(gameObject, "probe timeout");
                }
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
