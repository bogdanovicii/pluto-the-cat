using System.Collections.Generic;
using UnityEngine;
using Alexandria.ItemAPI;
using Alexandria.Misc;
using Dungeonator;

namespace PlutoTheCat
{
    /// <summary>
    /// Coffee Mug (2.19): Pluto pushes a mug off an invisible table. It flies CoffeeRange tiles toward the aim (or stops
    /// at the first thing it hits) and shatters once into a ring of CoffeeShardCount player-owned shards, leaving a
    /// coffee puddle for CoffeeSlowSeconds that slows valid enemies standing in it. The slow is the vanilla speed effect
    /// (no goop); the puddle removes it from every enemy it slowed on exit, end and teardown. With Espresso (Catnip
    /// Pouch) using the mug during zoomies extends them.
    /// </summary>
    public class CoffeeMugItem : PlayerItem
    {
        public const string ID = "pluto:coffee_mug";
        public const string SlowId = "pluto_coffee_slow";
        private const string EffectRoot = "PlutoTheCat/Resources/Effects/cat_set";
        private const float MugSpeed = 12f;
        private const float ShardSpeed = 14f;
        private const float ShardRange = 4f;
        private const float SlowMultiplier = 0.5f;
        private const float ScanInterval = 0.1f;
        // The slow zone is the approved 12x8 px puddle sprite's footprint.
        private const float PuddleHalfWidth = 6f / 16f, PuddleHalfHeight = 4f / 16f;

        private static Projectile mugPrefab;
        private static Projectile shardPrefab;
        private static int mugSpriteId = -1;
        private static int puddleSpriteId = -1;
        private static readonly int[] shardSpriteIds = { -1, -1, -1, -1 };

        private readonly List<MugThrow> flying = new List<MugThrow>();
        private readonly List<CoffeePuddle> puddles = new List<CoffeePuddle>();

        public static void Init()
        {
            string name = "Coffee Mug";
            GameObject obj = new GameObject(name);
            CoffeeMugItem item = obj.AddComponent<CoffeeMugItem>();
            ItemBuilder.AddSpriteToObject(name, Plugin.ITEM_ROOT + "/coffee_mug_icon", obj);
            ItemBuilder.SetupItem(item, "Off The Table",
                "Pushes a mug off the table toward Pluto's aim. It shatters into a ring of sharp shards and leaves a " +
                "coffee puddle that slows any enemy standing in it.\n\n" +
                "Bianca's favourite mug, the one with the red heart. Pluto looked her in the eye the whole time. " +
                "Bogdan swept up the pieces and bought her a new one. Pluto has already found the table it lives on.",
                "pluto");
            ItemBuilder.SetCooldownType(item, ItemBuilder.CooldownType.Damage, PlutoConfig.CoffeeRechargeDamage);
            item.consumable = false;
            item.quality = PickupObject.ItemQuality.C;

            mugSpriteId = SpriteBuilder.AddSpriteToCollection(Plugin.ITEM_ROOT + "/coffee_mug_icon.png", SpriteBuilder.itemCollection);
            puddleSpriteId = SpriteBuilder.AddSpriteToCollection(EffectRoot + "/coffee_puddle_001.png", SpriteBuilder.itemCollection);
            for (int i = 0; i < shardSpriteIds.Length; i++)
                shardSpriteIds[i] = SpriteBuilder.AddSpriteToCollection(EffectRoot + "/coffee_shard_00" + (i + 1) + ".png", SpriteBuilder.itemCollection);

            mugPrefab = ProjectileUtility.SetupProjectile(56); // clone the .38 Special bullet, like the Wet Food Can
            mugPrefab.gameObject.name = "pluto_coffee_mug_projectile";
            mugPrefab.baseData.damage = 0f;   // the shards do the damage
            mugPrefab.baseData.speed = MugSpeed;
            mugPrefab.baseData.range = PlutoConfig.CoffeeRange;
            mugPrefab.baseData.force = 0f;
            mugPrefab.shouldRotate = false;
            mugPrefab.gameObject.AddComponent<CoffeeTargetFilter>();
            mugPrefab.gameObject.AddComponent<MugThrow>();

            shardPrefab = ProjectileUtility.SetupProjectile(56);
            shardPrefab.gameObject.name = "pluto_coffee_shard_projectile";
            shardPrefab.baseData.damage = PlutoConfig.CoffeeShardDamage;
            shardPrefab.baseData.speed = ShardSpeed;
            shardPrefab.baseData.range = ShardRange;
            shardPrefab.baseData.force = 4f;
            shardPrefab.gameObject.AddComponent<CoffeeTargetFilter>();
        }

        public override void DoEffect(PlayerController user)
        {
            if (user == null || mugPrefab == null) return;
            if (user.PlayerHasActiveSynergy(PlutoSynergies.Espresso)) Espresso(user);

            Vector2 aim = user.unadjustedAimPoint.XY() - user.CenterPosition;
            if (aim.sqrMagnitude < 0.0001f) aim = Vector2.right;
            GameObject go = SpawnManager.SpawnProjectile(mugPrefab.gameObject, user.CenterPosition,
                Quaternion.Euler(0f, 0f, BraveMathCollege.Atan2Degrees(aim.normalized)), true);
            Projectile p = go != null ? go.GetComponent<Projectile>() : null;
            if (p == null) return;
            p.Owner = user;
            p.Shooter = user.specRigidbody;
            p.baseData.range = PlutoConfig.CoffeeRange;
            MugThrow mug = go.GetComponent<MugThrow>();
            if (mug != null)
            {
                mug.Arm(this, user);
                flying.Add(mug);
            }
            AkSoundEngine.PostEvent("Play_OBJ_item_throw_01", user.gameObject);
            Plugin.Log("coffee mug: thrown " + PlutoConfig.CoffeeRange + " tiles");
        }

        /// <summary>Espresso: extends the user's own running zoomies. An idle pouch returns false and nothing changes.</summary>
        private static void Espresso(PlayerController user)
        {
            if (user.activeItems == null) return;
            for (int i = 0; i < user.activeItems.Count; i++)
            {
                CatnipPouchItem pouch = user.activeItems[i] as CatnipPouchItem;
                if (pouch == null) continue;
                bool extended = pouch.ExtendZoomies(user, PlutoConfig.CoffeeZoomiesBonusSeconds);
                Plugin.Log(extended
                    ? "coffee mug: Espresso extended zoomies by " + PlutoConfig.CoffeeZoomiesBonusSeconds + " s"
                    : "coffee mug: Espresso had no running zoomies to extend");
                return;
            }
        }

        private void Shatter(PlayerController owner, Vector2 center)
        {
            AkSoundEngine.PostEvent("Play_OBJ_rock_break_01", GameManager.Instance.gameObject);
            if (shardPrefab != null)
            {
                int count = PlutoConfig.CoffeeShardCount;
                for (int i = 0; i < count; i++)
                {
                    float angle = CatSetRules.ShardAngle(i, count);
                    GameObject go = SpawnManager.SpawnProjectile(shardPrefab.gameObject, center, Quaternion.Euler(0f, 0f, angle), true);
                    Projectile shard = go != null ? go.GetComponent<Projectile>() : null;
                    if (shard == null) continue;
                    shard.Owner = owner;
                    shard.Shooter = owner.specRigidbody;
                    shard.baseData.damage = PlutoConfig.CoffeeShardDamage;
                    shard.baseData.range = ShardRange;
                    int spriteId = shardSpriteIds[i % shardSpriteIds.Length];
                    if (shard.sprite != null && spriteId >= 0) shard.sprite.SetSprite(SpriteBuilder.itemCollection, spriteId);
                }
            }

            if (PlutoConfig.CoffeeSlowSeconds > 0f && owner.CurrentRoom != null)
            {
                GameObject go = new GameObject("pluto_coffee_puddle");
                go.transform.position = center;
                if (puddleSpriteId >= 0)
                {
                    tk2dSprite sprite = go.AddComponent<tk2dSprite>();
                    sprite.SetSprite(SpriteBuilder.itemCollection, puddleSpriteId);
                    sprite.PlaceAtPositionByAnchor(center.ToVector3ZUp(0f), tk2dBaseSprite.Anchor.MiddleCenter);
                    sprite.HeightOffGround = -0.5f;
                    sprite.UpdateZDepth();
                }
                CoffeePuddle puddle = go.AddComponent<CoffeePuddle>();
                puddle.Begin(this, owner, center);
                puddles.Add(puddle);
            }
            Plugin.Log("coffee mug: shattered into " + PlutoConfig.CoffeeShardCount + " shards at " + center);
        }

        /// <summary>Ends every owned puddle (releasing its slows) and disarms mugs still in flight.</summary>
        private void Teardown()
        {
            MugThrow[] mugs = flying.ToArray();
            flying.Clear();
            for (int i = 0; i < mugs.Length; i++) if (mugs[i] != null) mugs[i].Disarm();
            CoffeePuddle[] owned = puddles.ToArray();
            puddles.Clear();
            for (int i = 0; i < owned.Length; i++) if (owned[i] != null) owned[i].End();
        }

        public override void OnPreDrop(PlayerController user)
        {
            Teardown();
            base.OnPreDrop(user);
        }

        public override void OnDestroy()
        {
            Teardown();
            base.OnDestroy();
        }

        /// <summary>Mug and shards pass through harmless and charmed enemies instead of hitting them.</summary>
        public sealed class CoffeeTargetFilter : MonoBehaviour
        {
            private SpeculativeRigidbody body;

            private void Start()
            {
                body = GetComponent<SpeculativeRigidbody>();
                if (body != null) body.OnPreRigidbodyCollision += Filter;
            }

            private static void Filter(SpeculativeRigidbody myBody, PixelCollider myCollider,
                SpeculativeRigidbody other, PixelCollider otherCollider)
            {
                AIActor enemy = other != null ? other.aiActor : null;
                if (enemy != null && !CatItemKit.ValidEnemy(enemy)) PhysicsEngine.SkipCollision = true;
            }

            private void OnDestroy()
            {
                if (body != null) body.OnPreRigidbodyCollision -= Filter;
            }
        }

        /// <summary>The flying mug. Shatters exactly once where the projectile stops, unless its item disarmed it.</summary>
        public sealed class MugThrow : MonoBehaviour
        {
            private Projectile projectile;
            private CoffeeMugItem item;
            private PlayerController thrower;
            private bool armed;
            private bool hooked;

            public void Arm(CoffeeMugItem source, PlayerController user)
            {
                projectile = GetComponent<Projectile>();
                if (projectile == null) return;
                if (!hooked) { projectile.OnDestruction += OnDestruction; hooked = true; }
                if (projectile.sprite != null && mugSpriteId >= 0)
                    projectile.sprite.SetSprite(SpriteBuilder.itemCollection, mugSpriteId);
                item = source;
                thrower = user;
                armed = true;
            }

            public void Disarm()
            {
                armed = false;
                item = null;
                thrower = null;
            }

            private void OnDestruction(Projectile p)
            {
                if (!armed || p == null) return;
                armed = false;
                CoffeeMugItem source = item;
                PlayerController owner = thrower;
                item = null;
                thrower = null;
                if (source == null || owner == null) return;
                source.flying.Remove(this);
                Vector2 center = p.specRigidbody != null ? p.specRigidbody.UnitCenter : (Vector2)p.transform.position;
                source.Shatter(owner, center);
            }

            private void OnDestroy()
            {
                if (hooked && projectile != null) projectile.OnDestruction -= OnDestruction;
                hooked = false;
            }
        }

        /// <summary>
        /// The coffee puddle. Every scan slows valid enemies whose hitbox overlaps the puddle and removes the slow from
        /// enemies it slowed that left, died, or became charmed/harmless. End (timeout, owner left the room, item
        /// teardown or destruction) removes the slow from everything it still holds.
        /// </summary>
        public sealed class CoffeePuddle : MonoBehaviour
        {
            private CoffeeMugItem item;
            private PlayerController owner;
            private RoomHandler room;
            private Vector2 center;
            private float remaining;
            private float scan;
            private bool ended;
            private HashSet<AIActor> slowed = new HashSet<AIActor>();

            public void Begin(CoffeeMugItem source, PlayerController user, Vector2 at)
            {
                item = source;
                owner = user;
                room = user != null ? user.CurrentRoom : null;
                center = at;
                remaining = PlutoConfig.CoffeeSlowSeconds;
                scan = 0f;
            }

            private void Update()
            {
                if (ended) return;
                if (owner == null || owner.healthHaver == null || owner.healthHaver.IsDead || owner.CurrentRoom != room)
                {
                    End();
                    return;
                }
                float dt = BraveTime.DeltaTime;
                remaining -= dt;
                if (remaining <= 0f)
                {
                    End();
                    return;
                }
                scan -= dt;
                if (scan > 0f) return;
                scan = ScanInterval;
                Refresh();
            }

            private void Refresh()
            {
                Vector2 min = center - new Vector2(PuddleHalfWidth, PuddleHalfHeight);
                Vector2 max = center + new Vector2(PuddleHalfWidth, PuddleHalfHeight);
                HashSet<AIActor> inside = new HashSet<AIActor>();
                List<AIActor> activeEnemies = room != null ? room.GetActiveEnemies(RoomHandler.ActiveEnemyType.All) : null;
                if (activeEnemies != null)
                {
                    AIActor[] enemies = activeEnemies.ToArray();
                    for (int i = 0; i < enemies.Length; i++)
                    {
                        AIActor enemy = enemies[i];
                        if (!CatItemKit.ValidEnemy(enemy) || !CatItemKit.HitboxOverlaps(enemy, min, max)) continue;
                        CatItemKit.Slow(enemy, remaining + ScanInterval, SlowMultiplier, SlowId);
                        inside.Add(enemy);
                    }
                }
                foreach (AIActor enemy in slowed)
                    if (!inside.Contains(enemy)) Release(enemy);
                slowed = inside;
            }

            private static void Release(AIActor enemy)
            {
                if (enemy != null) enemy.RemoveEffect(SlowId);
            }

            public void End()
            {
                if (ended) return;
                ended = true;
                ReleaseAll();
                if (item != null) item.puddles.Remove(this);
                item = null;
                owner = null;
                room = null;
                Destroy(gameObject);
            }

            private void ReleaseAll()
            {
                foreach (AIActor enemy in slowed) Release(enemy);
                slowed.Clear();
            }

            private void OnDestroy()
            {
                ReleaseAll();
                if (item != null) item.puddles.Remove(this);
                ended = true;
                item = null;
            }
        }
    }
}
