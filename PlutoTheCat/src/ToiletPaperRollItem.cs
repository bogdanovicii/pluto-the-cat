using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Alexandria.ItemAPI;
using Dungeonator;

namespace PlutoTheCat
{
    /// <summary>
    /// Toilet Paper Roll: stretches a four-tile paper streamer across Pluto's aim. Its small, independent
    /// BulletBlocker bodies stop enemy projectiles but never block players or enemies. Shredder turns a naturally
    /// expired streamer into a damaging confetti burst.
    /// </summary>
    public class ToiletPaperRollItem : PlayerItem
    {
        public const string ID = "pluto:toilet_paper_roll";
        private const string EffectRoot = "PlutoTheCat/Resources/Effects/cat_set";
        private const float FrontDistance = 1f;
        private const float SegmentHalfWidth = 3f / 16f;

        private static int streamerSpriteId = -1;
        private static int bitsSpriteId = -1;
        private static int confettiSpriteId = -1;
        // Shared across co-op item instances so overlapping streamers cannot both count one projectile.
        private static readonly HashSet<Projectile> ClaimedProjectiles = new HashSet<Projectile>();

        private readonly List<Segment> segments = new List<Segment>();
        private PlayerController owner;
        private RoomHandler room;
        private Coroutine lifetime;
        private float born;
        private int hits;
        private bool active;
        private Vector2 streamerCenter;
        private Vector2 perpendicular;

        private sealed class Segment
        {
            public GameObject gameObject;
            public SpeculativeRigidbody body;
            public Vector2 position;
            public bool live;
        }

        /// <summary>Short-lived sprite used for torn bits and the Shredder confetti burst.</summary>
        public sealed class PaperEffect : MonoBehaviour
        {
            private float remaining;

            public void Begin(float seconds) { remaining = seconds; }

            private void Update()
            {
                remaining -= BraveTime.DeltaTime;
                if (remaining <= 0f) Destroy(gameObject);
            }
        }

        public static void Init()
        {
            string name = "Toilet Paper Roll";
            GameObject obj = new GameObject(name);
            ToiletPaperRollItem item = obj.AddComponent<ToiletPaperRollItem>();
            ItemBuilder.AddSpriteToObject(name, Plugin.ITEM_ROOT + "/toilet_paper_roll_icon", obj);
            ItemBuilder.SetupItem(item, "Home Defence",
                "Unrolls a paper streamer across Pluto's aim. The paper stops enemy bullets until it is torn apart " +
                "or falls down on its own. Everyone can walk straight through it.\n\n" +
                "Some cats unroll the toilet paper for fun. Pluto does it for home defence. Bogdan and Bianca " +
                "keep putting the roll back on the holder. Pluto keeps improving it.",
                "pluto");
            ItemBuilder.SetCooldownType(item, ItemBuilder.CooldownType.Damage, PlutoConfig.TPRechargeDamage);
            item.consumable = false;
            item.quality = PickupObject.ItemQuality.C;

            streamerSpriteId = SpriteBuilder.AddSpriteToCollection(EffectRoot + "/toilet_paper_streamer_001.png", SpriteBuilder.itemCollection);
            bitsSpriteId = SpriteBuilder.AddSpriteToCollection(EffectRoot + "/toilet_paper_bits_001.png", SpriteBuilder.itemCollection);
            confettiSpriteId = SpriteBuilder.AddSpriteToCollection(EffectRoot + "/toilet_paper_confetti_001.png", SpriteBuilder.itemCollection);
        }

        public override bool CanBeUsed(PlayerController user)
        {
            return user != null && user.CurrentRoom != null && base.CanBeUsed(user);
        }

        public override void DoEffect(PlayerController user)
        {
            if (user == null || user.CurrentRoom == null || streamerSpriteId < 0) return;
            Teardown(false);

            owner = user;
            room = user.CurrentRoom;
            Vector2 aim = user.unadjustedAimPoint.XY() - user.CenterPosition;
            if (aim.sqrMagnitude < 0.0001f) aim = Vector2.right;
            aim.Normalize();
            perpendicular = new Vector2(-aim.y, aim.x);
            streamerCenter = user.CenterPosition + aim * FrontDistance;
            born = Time.time;
            hits = 0;
            active = true;

            float halfLength = PlutoConfig.TPLength * 0.5f;
            int segmentCount = Mathf.Max(1, PlutoConfig.TPHits);
            float centerSpan = Mathf.Max(0f, halfLength - SegmentHalfWidth);
            for (int i = 0; i < segmentCount; i++)
            {
                float along = segmentCount == 1 ? 0f : -centerSpan + centerSpan * 2f * i / (segmentCount - 1);
                CreateSegment(streamerCenter + perpendicular * along, perpendicular);
            }

            lifetime = StartCoroutine(StreamerLifetime());
            AkSoundEngine.PostEvent("Play_OBJ_item_throw_01", user.gameObject);
            Plugin.Log("toilet paper roll: streamer placed for " + PlutoConfig.TPSeconds + " s / " + PlutoConfig.TPHits + " hits");
        }

        private void CreateSegment(Vector2 position, Vector2 along)
        {
            GameObject go = new GameObject("pluto_toilet_paper_segment");
            go.transform.position = position;
            GameObject visual = new GameObject("paper");
            tk2dSprite sprite = visual.AddComponent<tk2dSprite>();
            sprite.SetSprite(SpriteBuilder.itemCollection, streamerSpriteId);
            sprite.PlaceAtPositionByAnchor(position.ToVector3ZUp(0f), tk2dBaseSprite.Anchor.MiddleCenter);
            visual.transform.parent = go.transform;
            visual.transform.rotation = Quaternion.Euler(0f, 0f, BraveMathCollege.Atan2Degrees(along));
            sprite.HeightOffGround = 0.1f;
            sprite.UpdateZDepth();

            SpeculativeRigidbody body = go.AddComponent<SpeculativeRigidbody>();
            body.CollideWithTileMap = false;
            body.CollideWithOthers = true;
            body.PixelColliders = new List<PixelCollider>
            {
                new PixelCollider
                {
                    ColliderGenerationMode = PixelCollider.PixelColliderGeneration.Manual,
                    CollisionLayer = CollisionLayer.BulletBlocker,
                    IsTrigger = false,
                    ManualOffsetX = -3,
                    ManualOffsetY = -3,
                    ManualWidth = 6,
                    ManualHeight = 6,
                }
            };
            body.Reinitialize();
            body.OnPreRigidbodyCollision += OnPreRigidbodyCollision;
            segments.Add(new Segment { gameObject = go, body = body, position = position, live = true });
        }

        private IEnumerator StreamerLifetime()
        {
            while (active)
            {
                CleanupProjectileClaims();
                // Ownership invalidation wins over a timeout on the same frame: transitions never trigger Shredder.
                if (!OwnershipValid())
                {
                    lifetime = null;
                    Teardown(false);
                    yield break;
                }
                if (!CatSetRules.StreamerAlive(Time.time, born, PlutoConfig.TPSeconds, hits, PlutoConfig.TPHits))
                {
                    lifetime = null;
                    FinishNormally();
                    yield break;
                }
                yield return null;
            }
        }

        private bool OwnershipValid()
        {
            return owner != null && owner.healthHaver != null && !owner.healthHaver.IsDead && owner.CurrentRoom == room;
        }

        private void OnPreRigidbodyCollision(SpeculativeRigidbody myBody, PixelCollider myCollider,
            SpeculativeRigidbody other, PixelCollider otherCollider)
        {
            // BulletBlocker is intentionally the only collider layer. Actors pass through, and friendly shots do too.
            Projectile projectile = other != null ? other.projectile : null;
            if (!active || !OwnershipValid())
            {
                if (active) Teardown(false);
                PhysicsEngine.SkipCollision = true;
                return;
            }
            if (!CatItemKit.IsEnemyBullet(projectile) || !projectile.collidesWithPlayer || projectile.HasDiedInAir)
            {
                PhysicsEngine.SkipCollision = true;
                return;
            }
            if (!TryClaimProjectile(projectile))
            {
                PhysicsEngine.SkipCollision = true;
                return;
            }

            Vector2 impact = other.UnitCenter;
            PhysicsEngine.SkipCollision = true;
            bool destroyed = false;
            try
            {
                projectile.DieInAir(false, true, true, false);
                // Unity's overloaded null covers immediate native destruction; otherwise HasDiedInAir is the
                // referenced DLL's synchronous live-to-dead flag. Either outcome is an actual destroyed shot.
                destroyed = projectile == null || projectile.HasDiedInAir;
            }
            finally
            {
                // Releasing after the transition cannot permit a double count: future callbacks see null/dead.
                ClaimedProjectiles.Remove(projectile);
            }
            if (!destroyed) return;
            TearNearest(impact);
            hits++;
            Plugin.Log("toilet paper roll: blocked enemy bullet " + hits + "/" + PlutoConfig.TPHits);
            if (!CatSetRules.StreamerAlive(Time.time, born, PlutoConfig.TPSeconds, hits, PlutoConfig.TPHits))
                FinishNormally();
        }

        private static bool TryClaimProjectile(Projectile projectile)
        {
            CleanupProjectileClaims();
            if (projectile == null || projectile.HasDiedInAir || !projectile.isActiveAndEnabled) return false;
            return ClaimedProjectiles.Add(projectile);
        }

        private static void CleanupProjectileClaims()
        {
            if (ClaimedProjectiles.Count == 0) return;
            List<Projectile> stale = new List<Projectile>();
            foreach (Projectile projectile in ClaimedProjectiles)
                if (projectile == null || projectile.HasDiedInAir || !projectile.isActiveAndEnabled) stale.Add(projectile);
            for (int i = 0; i < stale.Count; i++) ClaimedProjectiles.Remove(stale[i]);
        }

        private void TearNearest(Vector2 impact)
        {
            Segment nearest = null;
            float best = float.MaxValue;
            for (int i = 0; i < segments.Count; i++)
            {
                Segment candidate = segments[i];
                if (candidate == null || !candidate.live) continue;
                float distance = (candidate.position - impact).sqrMagnitude;
                if (distance < best) { best = distance; nearest = candidate; }
            }
            if (nearest == null) return;
            nearest.live = false;
            SpawnPaperEffect(bitsSpriteId, nearest.position, 0.25f);
            DestroySegment(nearest);
        }

        private void FinishNormally()
        {
            if (!active) return;
            Plugin.Log("toilet paper roll: streamer ended normally after " + hits + " hits");
            Teardown(true);
        }

        private void Teardown(bool normalCompletion)
        {
            if (lifetime != null)
            {
                StopCoroutine(lifetime);
                lifetime = null;
            }

            bool wasActive = active;
            bool shredder = normalCompletion && wasActive && owner != null
                && owner.PlayerHasActiveSynergy(PlutoSynergies.Shredder);
            active = false;
            if (normalCompletion && shredder) BurstConfetti();
            DestroyAllSegments();
            CleanupProjectileClaims();
            owner = null;
            room = null;
        }

        private void DestroyAllSegments()
        {
            for (int i = 0; i < segments.Count; i++) DestroySegment(segments[i]);
            segments.Clear();
        }

        private void DestroySegment(Segment segment)
        {
            if (segment == null) return;
            segment.live = false;
            if (segment.body != null) segment.body.OnPreRigidbodyCollision -= OnPreRigidbodyCollision;
            if (segment.gameObject != null) Destroy(segment.gameObject);
            segment.body = null;
            segment.gameObject = null;
        }

        private void BurstConfetti()
        {
            for (int i = 0; i < 7; i++)
            {
                float along = -PlutoConfig.TPLength * 0.5f + PlutoConfig.TPLength * i / 6f;
                SpawnPaperEffect(confettiSpriteId, streamerCenter + perpendicular * along, 0.45f);
            }
            AkSoundEngine.PostEvent("Play_OBJ_silenceblank_small_01", gameObject);

            List<AIActor> activeEnemies = room != null ? room.GetActiveEnemies(RoomHandler.ActiveEnemyType.All) : null;
            if (activeEnemies == null) return;
            AIActor[] enemies = activeEnemies.ToArray();
            for (int i = 0; i < enemies.Length; i++)
            {
                AIActor enemy = enemies[i];
                if (!CatItemKit.ValidEnemy(enemy)) continue;
                if (enemy.specRigidbody == null || enemy.specRigidbody.HitboxPixelCollider == null) continue;
                PixelCollider hitbox = enemy.specRigidbody.HitboxPixelCollider;
                Vector2 min = hitbox.UnitBottomLeft;
                Vector2 max = hitbox.UnitTopRight;
                if (!CatSetRules.StreamerStripOverlapsAabb(streamerCenter.x, streamerCenter.y,
                    perpendicular.x, perpendicular.y, PlutoConfig.TPLength, SegmentHalfWidth * 2f,
                    min.x, min.y, max.x, max.y)) continue;
                Vector2 direction = enemy.CenterPosition - streamerCenter;
                if (direction.sqrMagnitude < 0.0001f) direction = Vector2.right;
                enemy.healthHaver.ApplyDamage(PlutoConfig.TPConfettiDamage, direction.normalized, "Shredder",
                    CoreDamageTypes.None, DamageCategory.Normal, false, null, false);
            }
            Plugin.Log("toilet paper roll: Shredder confetti burst for " + PlutoConfig.TPConfettiDamage + " damage");
        }

        private static void SpawnPaperEffect(int spriteId, Vector2 position, float seconds)
        {
            if (spriteId < 0) return;
            GameObject go = new GameObject("pluto_toilet_paper_effect");
            tk2dSprite sprite = go.AddComponent<tk2dSprite>();
            sprite.SetSprite(SpriteBuilder.itemCollection, spriteId);
            sprite.PlaceAtPositionByAnchor(position.ToVector3ZUp(0f), tk2dBaseSprite.Anchor.MiddleCenter);
            sprite.HeightOffGround = 0.2f;
            sprite.UpdateZDepth();
            go.AddComponent<PaperEffect>().Begin(seconds);
        }

        public override void OnPreDrop(PlayerController user)
        {
            Teardown(false);
            base.OnPreDrop(user);
        }

        public override void OnDestroy()
        {
            Teardown(false);
            base.OnDestroy();
        }
    }
}
