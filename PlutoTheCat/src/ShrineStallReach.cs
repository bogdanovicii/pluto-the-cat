using System;
using System.Collections;
using System.Globalization;
using System.Reflection;
using HarmonyLib;
using UnityEngine;
using Alexandria.NPCAPI;

namespace PlutoTheCat
{
    /// <summary>
    /// Reach at the Breach shrine stall (2.20.9), the two things the 2.20.8 in-game test could not settle alone:
    ///
    /// 1. Item reach. Alexandria 0.5.10's CustomShopItemController declares its own GetOverrideMaxDistance
    ///    (`public hidebysig newslot virtual final instance float32 GetOverrideMaxDistance()`, body `ldc.r4 -1; ret`),
    ///    so the game default applies (INFERRED ~1 tile), and with the solid counter every plaque measured 1.125
    ///    tiles from the counter front: OUT OF REACH. A Harmony postfix raises it to ShrineItemReachTiles for items
    ///    of OUR shop only. An item knows its shop through the private m_baseParentShop, set by
    ///    Initialize(PickupObject i, CustomShopController parent) (IL_0001..0003); the items also sit under the
    ///    live shop root in the hierarchy, which is the fallback.
    ///
    /// 2. A headless reach test, `pluto_stall stand &lt;daifuku|0|1|2&gt;`: warps the player to the counter front under
    ///    that target and, half a second later, reads the interactable the GAME selected
    ///    (PlayerController.m_lastInteractionTarget). That is the definitive answer, measured by the game rather
    ///    than by our assumed default.
    /// </summary>
    internal static class ShrineStallReach
    {
        // Reach for our shop's items, in tiles (compared with CustomShopItemController.GetDistanceToPoint, world
        // units). 1.125 was measured from the counter front in game; 1.5 covers it with 3/8 of a tile to spare and
        // stays below Daifuku's 1.75, so standing at a plaque still selects the nearer plaque.
        internal const float ShrineItemReachTiles = 1.5f;

        // The warp puts the player's feet (specRigidbody.UnitBottomCenter) this many art pixels in front of the
        // counter collider's front edge.
        private const int StandGapPx = 2;
        private const float PixelsPerTile = 16f;
        // Long enough for several player Updates, so m_lastInteractionTarget reflects the new spot.
        private const float StandProbeDelaySeconds = 0.5f;

        private static bool _itemReachPatched;
        private static FieldInfo _baseParentShopField;
        private static FieldInfo _lastInteractionTargetField;

        internal static bool ItemReachPatched
        {
            get { return _itemReachPatched; }
        }

        /// <summary>Registers the item-reach postfix once, at plugin load (Plugin.Awake's Step list).</summary>
        internal static void ApplyItemReachPatch()
        {
            if (_itemReachPatched) return;
            MethodInfo target = AccessTools.DeclaredMethod(typeof(CustomShopItemController), "GetOverrideMaxDistance");
            if (target == null)
            {
                Plugin.Log("shrine stall reach: CustomShopItemController.GetOverrideMaxDistance not found - the stall's "
                    + "items keep the game's default reach");
                return;
            }
            _baseParentShopField = AccessTools.Field(typeof(CustomShopItemController), "m_baseParentShop");
            Harmony harmony = new Harmony(Plugin.GUID + ".shrine_item_reach");
            harmony.Patch(target, postfix: new HarmonyMethod(typeof(ShrineStallReach), "ItemReach"));
            _itemReachPatched = true;
            Plugin.Log("shrine stall reach: patched CustomShopItemController.GetOverrideMaxDistance - items of '"
                + ShrineStall.ShopPrefix + "' reach " + ShrineItemReachTiles.ToString("0.###", CultureInfo.InvariantCulture)
                + " tiles, every other shop is untouched"
                + (_baseParentShopField == null ? " (m_baseParentShop not found: matching by the parent chain only)" : ""));
        }

        /// <summary>Postfix: only items of our shop get the wider reach; every other shop keeps Alexandria's -1.</summary>
        private static void ItemReach(CustomShopItemController __instance, ref float __result)
        {
            try
            {
                if (IsOurShopItem(__instance)) __result = ShrineItemReachTiles;
            }
            catch (Exception e)
            {
                Plugin.Log("shrine stall reach: item reach postfix threw (reach left as is): " + e.Message);
            }
        }

        /// <summary>True for an item of the pluto_shrine_stall shop: its m_baseParentShop's GameObject, or any
        /// transform above the item, is named with ShrineStall.ShopPrefix (Alexandria names the shop root
        /// "&lt;prefix&gt;:&lt;name&gt;_Shop").</summary>
        private static bool IsOurShopItem(CustomShopItemController item)
        {
            if (item == null) return false;
            if (_baseParentShopField != null)
            {
                CustomShopController shop = _baseParentShopField.GetValue(item) as CustomShopController;
                if (shop != null) return shop.gameObject.name.StartsWith(ShrineStall.ShopPrefix, StringComparison.Ordinal);
            }
            for (Transform t = item.transform.parent; t != null; t = t.parent)
                if (t.name.StartsWith(ShrineStall.ShopPrefix, StringComparison.Ordinal)) return true;
            return false;
        }

        // ------------------------------------------------------------------------------------------------------

        /// <summary>
        /// `pluto_stall stand &lt;daifuku|0|1|2&gt;` (Breach only): warps the primary player so his feet stand StandGapPx
        /// in front of the counter collider's front edge, directly under the target, then lets the game pick its
        /// interaction target and logs it (StandProbe). Registers ghost-collision exceptions for the player so a
        /// warp that overlaps a body never traps him.
        /// </summary>
        internal static void Stand(string target, GameObject liveShop, GameObject counterProp)
        {
            if (UnityEngine.Object.FindObjectOfType<MainMenuFoyerController>() == null)
            {
                Plugin.Log("shrine stall: stand refused - not in the Breach (no MainMenuFoyerController); the stall only exists there");
                return;
            }
            PlayerController player = GameManager.HasInstance ? GameManager.Instance.PrimaryPlayer : null;
            if (player == null || player.specRigidbody == null)
            {
                Plugin.Log("shrine stall: stand - no player yet (pick a character first)");
                return;
            }
            if (liveShop == null || counterProp == null)
            {
                Plugin.Log("shrine stall: stand - " + (liveShop == null ? "no live shop" : "no counter prop") + " in the scene");
                return;
            }

            Component expected;
            string expectedLabel;
            if (string.Equals(target, "daifuku", StringComparison.OrdinalIgnoreCase))
            {
                expected = liveShop.GetComponentInChildren<TalkDoerLite>(true);
                expectedLabel = "Daifuku";
                if (expected == null)
                {
                    Plugin.Log("shrine stall: stand daifuku - no TalkDoerLite under the live shop");
                    return;
                }
            }
            else
            {
                CustomShopItemController[] items = liveShop.GetComponentsInChildren<CustomShopItemController>(true);
                int index;
                if (!int.TryParse(target, NumberStyles.Integer, CultureInfo.InvariantCulture, out index) || index < 0 || index > 2)
                {
                    Plugin.Log("shrine stall: usage - pluto_stall stand <daifuku|0|1|2>");
                    return;
                }
                if (index >= items.Length || items[index] == null)
                {
                    Plugin.Log("shrine stall: stand " + index + " - the live shop has " + items.Length
                        + " item(s); they exist once DoSetup has run, after character select");
                    return;
                }
                expected = items[index];
                expectedLabel = "Shop item " + index;
            }

            tk2dBaseSprite sprite = expected.GetComponent<tk2dBaseSprite>();
            float underX = sprite != null ? sprite.WorldCenter.x : expected.transform.position.x;
            Vector2 feet = new Vector2(underX, ShrineStallCollision.CounterFrontY(counterProp) - StandGapPx / PixelsPerTile);
            // WarpToPoint(Vector2 targetPoint, bool useDefaultPoof = false, bool doFollowers = false) places the
            // player's transform (INFERRED: the stub body is stripped). The feet's offset from the transform does
            // not change with a translation, so aiming the transform at feet - offset puts the FEET on the point.
            // The probe logs the feet the player actually ended up with, so a wrong inference shows at once.
            Vector2 feetOffset = player.specRigidbody.UnitBottomCenter - (Vector2)player.transform.position;
            player.WarpToPoint(feet - feetOffset, false, false);
            FreeFromOverlaps(player, "after the warp");
            Plugin.Log("shrine stall: stand " + target + " - warped the player's feet to " + F(feet) + " ("
                + StandGapPx + " px in front of the counter collider's front edge, under " + expectedLabel
                + "); asking the game in " + StandProbeDelaySeconds.ToString("0.#", CultureInfo.InvariantCulture) + " s");
            player.StartCoroutine(StandProbe(player, target, expected, expectedLabel, liveShop, feet));
        }

        /// <summary>Waits for the game to choose its interaction target at the new spot, then logs that choice
        /// against the expected target, plus where the player really stands.</summary>
        private static IEnumerator StandProbe(PlayerController player, string target, Component expected,
            string expectedLabel, GameObject liveShop, Vector2 intendedFeet)
        {
            yield return new WaitForSeconds(StandProbeDelaySeconds);
            if (player == null)
            {
                Plugin.Log("shrine stall: stand " + target + ": the player is gone - no answer");
                yield break;
            }
            FreeFromOverlaps(player, "before the probe");

            object selected = ReadLastInteractionTarget(player);
            Component chosen = selected as Component;
            bool ok = chosen != null && expected != null && chosen.gameObject == expected.gameObject;
            Plugin.Log("shrine stall: stand " + target + ": the game selected " + Describe(selected, liveShop)
                + " (expected " + expectedLabel + ") -> " + (ok ? "REACH OK" : "NOT REACHED"));
            Vector2 feet = player.specRigidbody != null ? player.specRigidbody.UnitBottomCenter : player.CenterPosition;
            Plugin.Log("shrine stall: stand " + target + ": player centre " + F(player.CenterPosition) + " feet " + F(feet)
                + " (aimed " + F(intendedFeet) + ", off by " + F(feet - intendedFeet) + ")");
            ShrineStall.ReportWhere("pluto_stall stand " + target);
        }

        /// <summary>PlayerController.m_lastInteractionTarget (private in the game, public in the publicized stub),
        /// read by reflection: the interactable the game's own reach rule picked.</summary>
        private static object ReadLastInteractionTarget(PlayerController player)
        {
            if (_lastInteractionTargetField == null)
                _lastInteractionTargetField = typeof(PlayerController).GetField("m_lastInteractionTarget",
                    BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public);
            if (_lastInteractionTargetField == null)
            {
                Plugin.Log("shrine stall: stand - PlayerController.m_lastInteractionTarget not found; cannot ask the game");
                return null;
            }
            return _lastInteractionTargetField.GetValue(player);
        }

        private static string Describe(object selected, GameObject liveShop)
        {
            if (selected == null) return "nothing";
            Component c = selected as Component;
            if (c == null) return "a non-component interactable (" + selected.GetType().Name + ")";
            bool underStall = liveShop != null && c.transform.IsChildOf(liveShop.transform);
            string role = "not part of the stall";
            if (underStall && c is TalkDoerLite) role = "Daifuku";
            else if (underStall && c is CustomShopItemController)
            {
                CustomShopItemController[] items = liveShop.GetComponentsInChildren<CustomShopItemController>(true);
                role = "Shop item " + Array.IndexOf(items, (CustomShopItemController)c);
            }
            return "'" + c.gameObject.name + "' (" + role + ")";
        }

        /// <summary>Lets the player walk out of anything the warp dropped him into (INFERRED: registers exceptions
        /// only against bodies that overlap his, as vanilla does for solid spawns).</summary>
        private static void FreeFromOverlaps(PlayerController player, string when)
        {
            if (!PhysicsEngine.HasInstance || player.specRigidbody == null) return;
            PhysicsEngine.Instance.RegisterOverlappingGhostCollisionExceptions(player.specRigidbody);
            Plugin.Log("shrine stall: stand - registered ghost-collision exceptions for the player " + when
                + " (so any body he overlaps cannot trap him)");
        }

        private static string F(Vector2 v)
        {
            return v.x.ToString("0.###", CultureInfo.InvariantCulture) + "," + v.y.ToString("0.###", CultureInfo.InvariantCulture);
        }
    }
}
