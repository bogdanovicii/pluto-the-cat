using System.Collections.Generic;
using UnityEngine;
using Alexandria.ItemAPI;
using Alexandria.Misc;

namespace PlutoTheCat
{
    /// <summary>
    /// Ball of Yarn (2.17): thrown at the aim point, the ball bounces around the room for YarnSeconds and passes
    /// through enemies. Every enemy it touches is tangled: stunned for YarnTangleSeconds (bosses cannot be stunned),
    /// then slowed. Walking into the ball bats it again toward the aim. With Cat's Cradle (Coco Blue) it lasts twice as long.
    /// </summary>
    public class BallOfYarnItem : PlayerItem
    {
        public const string ID = "pluto:ball_of_yarn";
        public const float Speed = 15f;
        private const float SlowMultiplier = 0.5f;
        private static Projectile yarnPrefab;
        private static readonly Dictionary<AIActor, float> tangledAt = new Dictionary<AIActor, float>();

        /// <summary>Both toys share the original tangle cooldown, stun, slow and puff.</summary>
        public static void ApplyTangle(AIActor enemy)
        {
            if (enemy == null || enemy.healthHaver == null || enemy.healthHaver.IsDead) return;
            // Discard expired entries so the shared cooldown never retains enemies across floors.
            List<AIActor> expired = new List<AIActor>();
            foreach (KeyValuePair<AIActor, float> entry in tangledAt)
                if (entry.Key == null || Time.time - entry.Value >= PlutoConfig.YarnTangleSeconds + PlutoConfig.YarnSlowSeconds)
                    expired.Add(entry.Key);
            for (int i = 0; i < expired.Count; i++) tangledAt.Remove(expired[i]);
            float last;
            float since = tangledAt.TryGetValue(enemy, out last) ? Time.time - last : float.NaN;
            if (!CatItemRules.CanTangle(since, PlutoConfig.YarnTangleSeconds, PlutoConfig.YarnSlowSeconds)) return;
            tangledAt[enemy] = Time.time;
            CatItemKit.Stun(enemy, PlutoConfig.YarnTangleSeconds);
            CatItemKit.Slow(enemy, PlutoConfig.YarnTangleSeconds + PlutoConfig.YarnSlowSeconds, SlowMultiplier, "pluto_yarn_tangle");
            PlutoVFX.Spawn(PlutoVFX.FurPuff, enemy.CenterPosition);
        }

        public static void Init()
        {
            string name = "Ball of Yarn";
            GameObject obj = new GameObject(name);
            BallOfYarnItem item = obj.AddComponent<BallOfYarnItem>();
            ItemBuilder.AddSpriteToObject(name, Plugin.ITEM_ROOT + "/ball_of_yarn_icon", obj);
            ItemBuilder.SetupItem(item, "Batted Under The Couch",
                "Throws a ball of yarn that bounces around the room. Enemies it touches get tangled up: stuck in place, " +
                "then slowed. Walk into the ball to bat it again.\n\n" +
                "The Gundead have no natural predators, and so no instinct at all for string. They learn one ankle at a time.\n\n" +
                "Pluto found his first ball in Bianca's knitting basket. Since then he has unravelled two scarves, a jumper " +
                "and most of a hat, and he considers every one of them a gift.",
                "pluto");
            ItemBuilder.SetCooldownType(item, ItemBuilder.CooldownType.Damage, PlutoConfig.YarnCooldownDamage);
            item.consumable = false;
            item.quality = PickupObject.ItemQuality.C;

            yarnPrefab = ProjectileUtility.SetupProjectile(56); // clone the .38 Special bullet
            yarnPrefab.gameObject.name = "pluto_ball_of_yarn_projectile";
            yarnPrefab.baseData.damage = PlutoConfig.YarnDamage;
            yarnPrefab.baseData.speed = Speed;
            yarnPrefab.baseData.range = 1000f;
            yarnPrefab.baseData.force = 6f;
            yarnPrefab.shouldRotate = false;   // the tumble is drawn
            yarnPrefab.SetProjectileSpriteRight("pluto_yarn_ball_001", 10, 10, false, tk2dBaseSprite.Anchor.MiddleCenter, 8, 8);
            BounceProjModifier bounce = yarnPrefab.gameObject.GetOrAddComponent<BounceProjModifier>();
            bounce.numberOfBounces = 9999;
            bounce.percentVelocityToLoseOnBounce = 0f;
            bounce.chanceToDieOnBounce = 0f;
            PierceProjModifier pierce = yarnPrefab.gameObject.GetOrAddComponent<PierceProjModifier>();
            pierce.penetration = 9999;
            pierce.penetratesBreakables = true;
            yarnPrefab.gameObject.AddComponent<YarnBall>();
        }

        public override void DoEffect(PlayerController user)
        {
            if (user == null || yarnPrefab == null) return;
            Vector2 dir = user.unadjustedAimPoint.XY() - user.CenterPosition;
            if (dir.sqrMagnitude < 0.0001f) dir = Vector2.right;
            GameObject go = SpawnManager.SpawnProjectile(yarnPrefab.gameObject, user.CenterPosition,
                Quaternion.Euler(0f, 0f, BraveMathCollege.Atan2Degrees(dir.normalized)), true);
            Projectile p = go.GetComponent<Projectile>();
            if (p == null) return;
            p.Owner = user;
            p.Shooter = user.specRigidbody;
            p.SkipDistanceElapsedCheck = true;   // lives for a time, not a distance
            AkSoundEngine.PostEvent("Play_OBJ_item_throw_01", user.gameObject);
        }

        /// <summary>Tumble, lifetime, tangling and batting for one thrown ball.</summary>
        public class YarnBall : MonoBehaviour
        {
            private const float FrameSeconds = 0.08f, BatDistance = 1.1f, BatCooldown = 0.4f, BatGrace = 0.5f;
            private Projectile projectile;
            private int[] ids;
            private int frame;
            private float frameTimer, life, lastBat = -10f;

            private void Start()
            {
                projectile = GetComponent<Projectile>();
                if (projectile == null) { enabled = false; return; }
                projectile.OnHitEnemy += OnHitEnemy;
                PlayerController owner = projectile.Owner as PlayerController;
                bool cradle = owner != null && owner.PlayerHasActiveSynergy(PlutoSynergies.CatsCradle);
                life = cradle ? PlutoConfig.YarnSeconds * 2f : PlutoConfig.YarnSeconds;
                tk2dBaseSprite sprite = projectile.sprite;
                if (sprite != null && sprite.Collection != null)
                {
                    ids = new[] { sprite.Collection.GetSpriteIdByName("pluto_yarn_ball_001", -1), sprite.Collection.GetSpriteIdByName("pluto_yarn_ball_002", -1) };
                    if (ids[0] < 0 || ids[1] < 0) ids = null;
                }
                Plugin.Log("ball of yarn: thrown, lives " + life + " s" + (cradle ? " (Cat's Cradle)" : ""));
            }

            private void OnDestroy()
            {
                if (projectile != null) projectile.OnHitEnemy -= OnHitEnemy;
            }

            private void Update()
            {
                if (projectile == null) return;
                float dt = BraveTime.DeltaTime;
                life -= dt;
                if (life <= 0f)
                {
                    PlutoVFX.Spawn(PlutoVFX.FurPuff, projectile.specRigidbody != null ? projectile.specRigidbody.UnitCenter : (Vector2)transform.position);
                    projectile.DieInAir(false, true, true, false);
                    return;
                }
                frameTimer += dt;
                if (ids != null && frameTimer >= FrameSeconds && projectile.sprite != null)
                {
                    frameTimer = 0f;
                    frame = 1 - frame;
                    projectile.sprite.SetSprite(ids[frame]);
                }
                Bat();
            }

            /// <summary>Walking into the ball sends it off again toward the owner's aim.</summary>
            private void Bat()
            {
                PlayerController owner = projectile.Owner as PlayerController;
                if (owner == null || owner.healthHaver == null || owner.healthHaver.IsDead) return;
                if (projectile.ElapsedTime < BatGrace || Time.time - lastBat < BatCooldown) return;
                Vector2 ball = projectile.specRigidbody != null ? projectile.specRigidbody.UnitCenter : (Vector2)transform.position;
                if (!CatItemRules.Inside((ball - owner.CenterPosition).sqrMagnitude, BatDistance)) return;
                Vector2 dir = owner.unadjustedAimPoint.XY() - ball;
                if (dir.sqrMagnitude < 0.0001f) dir = ball - owner.CenterPosition;
                if (dir.sqrMagnitude < 0.0001f) dir = Vector2.right;
                lastBat = Time.time;
                projectile.SendInDirection(dir.normalized, true, false);
                projectile.baseData.speed = Speed;
                projectile.UpdateSpeed();
                AkSoundEngine.PostEvent("Play_OBJ_item_throw_01", owner.gameObject);
            }

            private void OnHitEnemy(Projectile p, SpeculativeRigidbody body, bool fatal)
            {
                if (fatal || body == null || body.aiActor == null) return;
                BallOfYarnItem.ApplyTangle(body.aiActor);
            }
        }
    }
}
