using System.Collections.Generic;
using System.Globalization;
using UnityEngine;
using Alexandria.NPCAPI;

namespace PlutoTheCat
{
    /// <summary>
    /// Collision for the redesigned Breach shrine stall (problem P3: the player walked straight through
    /// Daifuku's counter, the torii posts and Kinsuke's bowl). Small, separately callable entry points; the
    /// placement code calls them, this file never reaches into it.
    ///
    /// Everything is written in the COUNTER FRAME of art-spec.md section 5: origin = the counter's bottom-centre
    /// anchor, x right, y up, px (16 px = 1 tile). Our props are placed LowerCenter and end with their transform
    /// at the sprite's LOWER-LEFT (measured, archaeology 3.5), and a Manual PixelCollider's offset is measured
    /// from the rigidbody's transform (inferred, archaeology 3.1). So every Manual offset below is "pixels from
    /// the prop sprite's lower-left corner". Boxes are half-open [x0, x1) x [y0, y1).
    ///
    ///     counter lower-left = (-CounterWidthPx/2, 0)                 = (-52,  0)
    ///     torii   lower-left = (-ToriiWidthPx/2, ToriiAnchorAbove...) = (-68, 24)
    ///     Daifuku lower-left = (21 - 26/2, 21)                        = (  8, 21)
    ///
    /// Resulting boxes (counter frame):
    ///     counter      HighObstacle   [-52, 52) x [ 0,  9)   ground footprint of the whole counter
    ///     left post    HighObstacle   [-61,-52) x [24, 28)   stone base only
    ///     right post   HighObstacle   [ 53, 62) x [24, 28)   stone base only
    ///     back fill    PlayerBlocker  [-61, 62) x [ 9, 28)   seals the floor behind the counter, between the posts
    ///     Daifuku      LowObstacle    [ 13, 33) x [21, 39)   Alexandria's own 20x18 @ (5,0), untouched
    /// Nothing reaches below y = 0, so the approach strip in front of the counter stays walkable and the player's
    /// feet can touch the counter's front ground line: as close to the items and to Daifuku as the art allows.
    ///
    /// Kinsuke's bowl gets NO collider of its own: it rests on the counter top (bowl x [36, 48) lies inside the
    /// counter's [-52, 52)), so the counter body already keeps the player away from it. A box at the bowl's own
    /// height would float in mid-air behind the counter's footprint. Same for the three items on the counter:
    /// their own shop colliders ignore the player anyway (archaeology 1.5).
    ///
    /// Collision-matrix semantics are INFERRED (the game assembly here is a stub): HighObstacle blocks players,
    /// enemies and projectiles; PlayerBlocker blocks only players. LogBodies prints every layer and world box so
    /// the tester can confirm them by walking into each piece.
    /// </summary>
    internal static class ShrineStallCollision
    {
        // ---- Final art (user-approved 2026-09-18, art-spec.md sections 5-7). Change these only with the art. ----
        private const int CounterWidthPx = 104;            // stall.png 104 x 23, anchor (52, 23) = counter frame (0, 0)
        private const int CounterHeightPx = 23;
        private const int CounterTopFaceRows = 9;          // rows 0-8 = top face (back outline + 8 surface rows);
                                                           // rows 9-22 = the 14-px front face
        private const int ToriiWidthPx = 136;              // torii.png 136 x 56, anchor (68, 56) = counter frame (0, +24)
        private const int ToriiHeightPx = 56;
        private const int ToriiAnchorAboveCounterPx = 24;
        private const int ToriiLeftPostCol = 8;            // posts: canvas cols 8-14 and 122-128 (7 wide), rows 12-51
        private const int ToriiRightPostCol = 122;         //   = counter frame x -60..-54 and +54..+60
        private const int ToriiPostWidthPx = 7;
        private const int ToriiLeftBaseCol = 7;            // stone bases: canvas cols 7-15 and 121-129 (9 wide),
        private const int ToriiRightBaseCol = 121;         //   rows 52-55 = the bottom 4 rows of the canvas
        private const int ToriiBaseWidthPx = 9;
        private const int ToriiBaseRows = 4;
        private const int DaifukuWidthPx = 26;             // daifuku_*.png 26 x 32, anchor (13, 32) = counter frame (+21, +21)
        private const int DaifukuHeightPx = 32;
        private const int DaifukuAnchorXPx = 21;
        private const int DaifukuAnchorYPx = 21;
        private const int DaifukuHitboxOffsetXPx = 5;      // Alexandria's LowObstacle box, as SetUpFoyerShop is called
        private const int DaifukuHitboxOffsetYPx = 0;      //   in ShrineStall.cs (hitboxSize 20x18, hitboxOffset 5,0)
        private const int DaifukuHitboxWidthPx = 20;
        private const int DaifukuHitboxHeightPx = 18;
        private const int BowlWidthPx = 12;                // kinsuke_idle_*.png 12 x 14, anchor (6, 14) = counter frame
        private const int BowlHeightPx = 14;               //   (+42, +17), ON the counter top: covered by the counter body
        private const int BowlAnchorXPx = 42;
        private const int BowlAnchorYPx = 17;

        // ---- Derived frames (counter frame, px) ----
        private const int CounterLeftPx = -CounterWidthPx / 2;                      // -52: counter transform x
        private const int ToriiLeftPx = -ToriiWidthPx / 2;                          // -68: torii transform x
        private const int ToriiBottomPx = ToriiAnchorAboveCounterPx;                // +24: torii transform y
        private const int DaifukuLeftPx = DaifukuAnchorXPx - DaifukuWidthPx / 2;    //  +8: Daifuku transform x
        private const int DaifukuBottomPx = DaifukuAnchorYPx;                       // +21: Daifuku transform y

        // ---- Counter: HighObstacle footprint, offsets from the counter sprite's lower-left ----
        // Full width (0..104 = counter frame -52..+52). Depth = the top face's depth: in the 3/4 view the top
        // face (rows 0-8, 9 px) IS the counter's ground depth seen from above, and vanilla furniture puts its
        // collider on that ground footprint, not on the drawn height (archaeology 3.3). 9 <= 14 front-face rows,
        // so the box stays inside the counter's bottom rows. Its front edge is the ground line (y 0), so the
        // player's feet stop exactly at the counter front; the depth does not move the player further away.
        private const int CounterBoxOffsetXPx = 0;
        private const int CounterBoxOffsetYPx = 0;
        private const int CounterBoxWidthPx = CounterWidthPx;                       // 104
        private const int CounterBoxHeightPx = CounterTopFaceRows;                  // 9 -> counter frame y 0..9

        // ---- Torii: one HighObstacle box per stone base, offsets from the torii sprite's lower-left ----
        // The bases are the posts' ground contact (9 px wide, 1 px wider than each 7-px post on both sides) and
        // are 4 rows deep; the drawn post above them is left free so the player can walk behind the gate and be
        // drawn behind it. Counter frame: left -68+7 = -61 .. -52, right -68+121 = 53 .. 62, y 24 .. 28.
        private const int LeftPostBoxOffsetXPx = ToriiLeftBaseCol;                  // 7
        private const int RightPostBoxOffsetXPx = ToriiRightBaseCol;                // 121
        private const int PostBoxOffsetYPx = 0;                                     // bottom rows 52-55
        private const int PostBoxWidthPx = ToriiBaseWidthPx;                        // 9
        private const int PostBoxHeightPx = ToriiBaseRows;                          // 4

        // ---- Back fill: PlayerBlocker, offsets from the counter sprite's lower-left ----
        // The counter footprint ends at y 9 but the post bases start at y 24, so a 15-px band of open floor runs
        // behind the counter from one side of the gate to the other: the player could walk round a post and
        // stand behind Daifuku. This box fills that band from the left base's outer edge to the right base's
        // outer edge and from the counter footprint's back edge to the bases' back edge, so counter + fill +
        // bases are one continuous wall with no seam. PlayerBlocker, not HighObstacle, because it is an
        // invisible wall: it must not eat shots aimed over the counter (Daifuku has his own BulletBlocker).
        //   x: (CounterWidthPx/2 - ToriiWidthPx/2) + ToriiLeftBaseCol = 52 - 68 + 7 = -9  (counter frame -61)
        //   w: (ToriiRightBaseCol + ToriiBaseWidthPx) - ToriiLeftBaseCol = 130 - 7 = 123 (counter frame -61..62)
        //   y: CounterBoxHeightPx = 9;  h: (24 + 4) - 9 = 19                               (counter frame 9..28)
        private const int BackBlockerOffsetXPx = CounterWidthPx / 2 - ToriiWidthPx / 2 + ToriiLeftBaseCol;
        private const int BackBlockerOffsetYPx = CounterBoxOffsetYPx + CounterBoxHeightPx;
        private const int BackBlockerWidthPx = ToriiRightBaseCol + ToriiBaseWidthPx - ToriiLeftBaseCol;
        private const int BackBlockerHeightPx = ToriiAnchorAboveCounterPx + ToriiBaseRows - BackBlockerOffsetYPx;

        private const float PixelsPerTile = 16f;

        internal static readonly CollisionLayer CounterLayer = CollisionLayer.HighObstacle;
        internal static readonly CollisionLayer PostLayer = CollisionLayer.HighObstacle;
        internal static readonly CollisionLayer BackBlockerLayer = CollisionLayer.PlayerBlocker;

        /// <summary>Gives the counter prop (stall.png, already positioned) its footprint body. Call right after the
        /// counter is placed. Returns the body, or null for a null prop.</summary>
        internal static SpeculativeRigidbody AttachCounterBody(GameObject counterProp)
        {
            return AddColliders(counterProp, "counter",
                Box(CounterLayer, CounterBoxOffsetXPx, CounterBoxOffsetYPx, CounterBoxWidthPx, CounterBoxHeightPx));
        }

        /// <summary>Gives the torii prop (torii.png, already positioned) one small box under each post.</summary>
        internal static SpeculativeRigidbody AttachToriiBody(GameObject toriiProp)
        {
            return AddColliders(toriiProp, "torii",
                Box(PostLayer, LeftPostBoxOffsetXPx, PostBoxOffsetYPx, PostBoxWidthPx, PostBoxHeightPx),
                Box(PostLayer, RightPostBoxOffsetXPx, PostBoxOffsetYPx, PostBoxWidthPx, PostBoxHeightPx));
        }

        /// <summary>Adds the invisible PlayerBlocker behind the counter, between the posts, to the COUNTER's body
        /// (so its seam with the counter footprint is exact whatever the torii's own rounding). Call after
        /// AttachCounterBody; if the counter has no body yet, one is created.</summary>
        internal static SpeculativeRigidbody AttachBackBlocker(GameObject counterProp)
        {
            return AddColliders(counterProp, "back fill",
                Box(BackBlockerLayer, BackBlockerOffsetXPx, BackBlockerOffsetYPx, BackBlockerWidthPx, BackBlockerHeightPx));
        }

        /// <summary>
        /// Re-registers every rigidbody under the live shop (Daifuku, the shop items) at its current transform.
        /// INFERRED (archaeology 3.2): a registered SpeculativeRigidbody does not follow a raw transform move, so
        /// after MoveStall / ReconcileLiveShopPosition moves the live clone, Daifuku's collider and talk region
        /// would stay at the old spot. Bodies on inactive objects are skipped (they register when they wake).
        /// Returns how many bodies were reinitialised.
        /// </summary>
        internal static int ReinitializeShopBodies(GameObject liveShop)
        {
            if (liveShop == null) return 0;
            int count = 0;
            foreach (SpeculativeRigidbody body in liveShop.GetComponentsInChildren<SpeculativeRigidbody>(true))
            {
                if (body == null || !body.gameObject.activeInHierarchy) continue;
                body.Reinitialize();
                count++;
            }
            Plugin.Log("shrine stall collision: reinitialised " + count + " live shop bod" + (count == 1 ? "y" : "ies")
                + " under '" + liveShop.name + "' at " + F(liveShop.transform.position));
            return count;
        }

        /// <summary>
        /// Diagnostic for the tester. Logs, for every body on the given props and under the live shop, each
        /// collider's layer, its Manual pixel box, the world box the physics engine reports
        /// (PixelCollider.UnitBottomLeft / UnitDimensions) next to the box expected from the transform (flagged
        /// STALE if they disagree: the "did not follow the move" case) and the sprite's world bounds. Then the
        /// reach numbers: from the counter-front standing point under each target to Daifuku's talk point and to
        /// each item centre, both straight-line and as the interactable itself measures it
        /// (GetDistanceToPoint) with its override radius; and, if a player exists, the same from the player's
        /// actual centre, so standing at the counter and re-running this settles the reach question.
        /// </summary>
        internal static void LogBodies(GameObject liveShop, GameObject counterProp, params GameObject[] otherProps)
        {
            LogObjectBodies(counterProp);
            if (otherProps != null)
                foreach (GameObject prop in otherProps) LogObjectBodies(prop);

            if (liveShop == null)
            {
                Plugin.Log("shrine stall collision: no live shop - Daifuku's body and reach not logged");
                return;
            }
            foreach (SpeculativeRigidbody body in liveShop.GetComponentsInChildren<SpeculativeRigidbody>(true))
                if (body != null) LogBody(body);

            LogReach(liveShop, counterProp);
        }

        // ------------------------------------------------------------------------------------------------------

        private static PixelCollider Box(CollisionLayer layer, int x, int y, int w, int h)
        {
            return new PixelCollider
            {
                ColliderGenerationMode = PixelCollider.PixelColliderGeneration.Manual,
                CollisionLayer = layer,
                IsTrigger = false,
                Enabled = true,
                ManualOffsetX = x,
                ManualOffsetY = y,
                ManualWidth = w,
                ManualHeight = h,
            };
        }

        /// <summary>The house idiom (ToiletPaperRollItem.CreateSegment): body on the prop's own GameObject,
        /// Manual colliders, then Reinitialize. Appends to an existing body instead of adding a second one.</summary>
        private static SpeculativeRigidbody AddColliders(GameObject prop, string what, params PixelCollider[] colliders)
        {
            if (prop == null)
            {
                Plugin.Log("shrine stall collision: no " + what + " prop to attach to - it stays walk-through");
                return null;
            }
            SpeculativeRigidbody body = prop.GetComponent<SpeculativeRigidbody>();
            if (body == null)
            {
                body = prop.AddComponent<SpeculativeRigidbody>();
                body.CollideWithTileMap = false;
                body.CollideWithOthers = true;
                body.CanBePushed = false;
                body.CanPush = false;
                body.PixelColliders = new List<PixelCollider>();
            }
            if (body.PixelColliders == null) body.PixelColliders = new List<PixelCollider>();
            body.PixelColliders.AddRange(colliders);
            body.Reinitialize();

            // pluto_stall here drops the stall on the player's own position, so a fresh body can spawn overlapping
            // the player. Ghost exceptions let anything already inside walk out instead of being stuck (INFERRED
            // from the name and signature; vanilla uses it when spawning solid objects).
            if (PhysicsEngine.HasInstance)
                PhysicsEngine.Instance.RegisterOverlappingGhostCollisionExceptions(body);

            Plugin.Log("shrine stall collision: attached " + what + " (" + colliders.Length + " box"
                + (colliders.Length == 1 ? "" : "es") + ") to '" + prop.name + "'");
            return body;
        }

        private static void LogObjectBodies(GameObject go)
        {
            if (go == null) return;
            SpeculativeRigidbody body = go.GetComponent<SpeculativeRigidbody>();
            if (body == null)
            {
                Plugin.Log("shrine stall collision: '" + go.name + "' has NO body (walk-through)");
                return;
            }
            LogBody(body);
        }

        private static void LogBody(SpeculativeRigidbody body)
        {
            Renderer renderer = body.GetComponent<Renderer>();
            string spriteBounds = renderer != null
                ? F(renderer.bounds.min) + " .. " + F(renderer.bounds.max)
                : "no renderer";
            Vector2 origin = body.transform.position;
            Plugin.Log("shrine stall collision: body '" + body.name + "' transform " + F(origin)
                + " body box " + F(body.UnitBottomLeft) + " size " + F(body.UnitDimensions)
                + " active=" + body.gameObject.activeInHierarchy + " sprite bounds " + spriteBounds);
            if (body.PixelColliders == null) return;

            for (int i = 0; i < body.PixelColliders.Count; i++)
            {
                PixelCollider c = body.PixelColliders[i];
                if (c == null) continue;
                Vector2 expected = origin + new Vector2(c.ManualOffsetX, c.ManualOffsetY) / PixelsPerTile;
                Vector2 actual = c.UnitBottomLeft;
                bool stale = (actual - expected).sqrMagnitude > (0.5f / PixelsPerTile) * (0.5f / PixelsPerTile);
                Plugin.Log("shrine stall collision:   collider " + i + " layer=" + c.CollisionLayer
                    + " mode=" + c.ColliderGenerationMode + " trigger=" + c.IsTrigger + " enabled=" + c.Enabled
                    + " manual px (" + c.ManualOffsetX + "," + c.ManualOffsetY + " " + c.ManualWidth + "x" + c.ManualHeight + ")"
                    + " world " + F(actual) + " size " + F(c.UnitDimensions)
                    + " expected " + F(expected)
                    + (c.ColliderGenerationMode == PixelCollider.PixelColliderGeneration.Manual && stale
                        ? " STALE (physics box did not follow the transform - call ReinitializeShopBodies)" : ""));
            }
        }

        private static void LogReach(GameObject liveShop, GameObject counterProp)
        {
            // The standing line is the counter body's front edge (its ground line): the player's feet cannot pass
            // it, so a point on it directly under a target is the closest the player can get to that target.
            float frontY = counterProp != null
                ? counterProp.transform.position.y + CounterBoxOffsetYPx / PixelsPerTile
                : liveShop.transform.position.y;
            Plugin.Log("shrine stall collision: counter front line y=" + F1(frontY)
                + (counterProp == null ? " (no counter prop - using the shop root's y)" : ""));
            if (counterProp != null)
            {
                // Where art-spec section 5 puts Daifuku's Alexandria box if he is placed at (+21, +21): compare
                // with his own collider line above. A mismatch means placement drifted, not collision.
                Vector2 anchor = (Vector2)counterProp.transform.position + new Vector2(-CounterLeftPx, 0f) / PixelsPerTile;
                Vector2 daifukuBox = anchor + new Vector2(DaifukuLeftPx + DaifukuHitboxOffsetXPx,
                    DaifukuBottomPx + DaifukuHitboxOffsetYPx) / PixelsPerTile;
                Plugin.Log("shrine stall collision: art spec expects Daifuku's LowObstacle box at " + F(daifukuBox)
                    + " size " + F(new Vector2(DaifukuHitboxWidthPx, DaifukuHitboxHeightPx) / PixelsPerTile)
                    + " (counter anchor " + F(anchor) + ")");
            }

            PlayerController player = GameManager.HasInstance ? GameManager.Instance.PrimaryPlayer : null;
            if (player != null)
                Plugin.Log("shrine stall collision: player center " + F(player.CenterPosition)
                    + (player.specRigidbody != null ? " feet " + F(player.specRigidbody.UnitBottomCenter) : ""));

            TalkDoerLite talker = liveShop.GetComponentInChildren<TalkDoerLite>(true);
            if (talker == null)
                Plugin.Log("shrine stall collision: no TalkDoerLite under the live shop - Daifuku reach not logged");
            else
            {
                Vector2 talk = talker.speakPoint != null ? (Vector2)talker.speakPoint.position : (Vector2)talker.transform.position;
                LogReachTo("Daifuku talk point" + (talker.speakPoint != null ? "" : " (no speakPoint; NPC transform)"),
                    talk, frontY, player, talker.GetDistanceToPoint, talker.GetOverrideMaxDistance());
            }

            CustomShopItemController[] items = liveShop.GetComponentsInChildren<CustomShopItemController>(true);
            if (items.Length == 0) Plugin.Log("shrine stall collision: no shop items under the live shop - item reach not logged");
            for (int i = 0; i < items.Length; i++)
            {
                CustomShopItemController item = items[i];
                if (item == null) continue;
                Vector2 centre = item.sprite != null ? item.sprite.WorldCenter : (Vector2)item.transform.position;
                LogReachTo("item " + i + " '" + item.name + "' centre", centre, frontY, player,
                    item.GetDistanceToPoint, item.GetOverrideMaxDistance());
            }
        }

        private delegate float DistanceTo(Vector2 point);

        private static void LogReachTo(string label, Vector2 target, float frontY, PlayerController player,
            DistanceTo measure, float overrideMax)
        {
            Vector2 stand = new Vector2(target.x, frontY);
            string line = "shrine stall collision: reach to " + label + " " + F(target)
                + ": from counter front " + F(stand) + " straight " + F1(Vector2.Distance(stand, target))
                + " tiles, interactable says " + F1(measure(stand));
            if (player != null)
                line += "; from player center straight " + F1(Vector2.Distance(player.CenterPosition, target))
                    + ", interactable says " + F1(measure(player.CenterPosition));
            line += "; override max distance " + F1(overrideMax) + " (<= 0 = game default)";
            Plugin.Log(line);
        }

        private static string F(Vector2 v)
        {
            return F1(v.x) + "," + F1(v.y);
        }

        private static string F(Vector3 v)
        {
            return F(new Vector2(v.x, v.y));
        }

        private static string F1(float f)
        {
            return f.ToString("0.###", CultureInfo.InvariantCulture);
        }
    }
}
