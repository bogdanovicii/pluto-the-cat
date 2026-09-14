using System.Collections.Generic;
using UnityEngine;
using Alexandria.ItemAPI;
using Dungeonator;
using Alexandria.Misc;

namespace PlutoTheCat
{
    /// <summary>
    /// Wet Food Can: Pluto's starter active. Thrown straight at the aim point as a tumbling tin (a cloned
    /// .38 Special projectile, same pattern as the hairball). The enemy it hits falls in love with Pluto, and
    /// the tin always bursts where it stops (enemy, wall or end of range): every enemy in the gravy splash
    /// falls in love too. Bosses are stunned instead of charmed.
    /// </summary>
    public class WetFoodCanItem : PlayerItem
    {
        public const string ID = "pluto:wet_food_can";
        public const float Speed = 14f;
        public const float Range = 10f;
        private static Projectile canPrefab;

        public static void Init()
        {
            string name = "Wet Food Can";
            GameObject obj = new GameObject(name);
            WetFoodCanItem item = obj.AddComponent<WetFoodCanItem>();
            ItemBuilder.AddSpriteToObject(name, Plugin.ITEM_ROOT + "/wet_food_can_icon", obj);
            ItemBuilder.SetupItem(item, "Thin Slices In Gravy",
                "A gold tin of ROYAL CANIN Kitten, thin slices in gravy. Throw it at something: whatever it hits falls " +
                "hopelessly in love with Pluto, and the tin bursts open, so everything standing in the gravy falls in love " +
                "too. Lovestruck enemies fight for Pluto and take more damage. Bosses are too proud to fall in love, but " +
                "the smell stops them in their tracks for a few seconds.\n\n" +
                "Pluto only gets the wet food on special occasions, which is why the sound of the lid peeling back " +
                "makes him appear from anywhere in the house. It turns out the Gundead feel exactly the same way.",
                "pluto");
            ItemBuilder.SetCooldownType(item, ItemBuilder.CooldownType.Damage, PlutoConfig.CanCooldownDamage);
            item.consumable = false;
            item.quality = PickupObject.ItemQuality.EXCLUDED;

            canPrefab = BuildProjectile();
        }

        private static Projectile BuildProjectile()
        {
            Projectile can = ProjectileUtility.SetupProjectile(56); // clone the .38 Special bullet
            can.gameObject.name = "pluto_wet_food_can_projectile";
            can.baseData.damage = PlutoConfig.CanDamage;
            can.baseData.speed = Speed;
            can.baseData.range = Range;
            can.baseData.force = 10f;
            can.shouldRotate = false; // the tumble is drawn in the four frames
            can.SetProjectileSpriteRight("pluto_wet_food_can_001", 16, 16, false, tk2dBaseSprite.Anchor.MiddleCenter, 12, 10);
            can.gameObject.AddComponent<CanTumble>();
            can.gameObject.AddComponent<CanBurst>();
            return can;
        }

        public override void DoEffect(PlayerController user)
        {
            if (user == null || canPrefab == null) return;
            Vector2 dir = user.unadjustedAimPoint.XY() - user.CenterPosition;
            if (dir.sqrMagnitude < 0.0001f) dir = Vector2.right;
            float angle = BraveMathCollege.Atan2Degrees(dir.normalized);
            GameObject go = SpawnManager.SpawnProjectile(canPrefab.gameObject, user.CenterPosition, Quaternion.Euler(0f, 0f, angle), true);
            Projectile p = go.GetComponent<Projectile>();
            if (p == null) return;
            p.Owner = user;
            p.Shooter = user.specRigidbody;
            AkSoundEngine.PostEvent("Play_OBJ_item_throw_01", user.gameObject);
        }

        /// <summary>Cycles the four tumble sprites (label side, lid, upside down, bottom) while the tin flies.</summary>
        public class CanTumble : MonoBehaviour
        {
            private const float FrameSeconds = 0.07f;
            private tk2dBaseSprite sprite;
            private int[] ids;
            private int frame;
            private float timer;

            private void Start()
            {
                Projectile p = GetComponent<Projectile>();
                sprite = p != null ? p.sprite : null;
                if (sprite == null || sprite.Collection == null) { enabled = false; return; }
                ids = new int[4];
                for (int i = 0; i < ids.Length; i++)
                {
                    ids[i] = sprite.Collection.GetSpriteIdByName("pluto_wet_food_can_00" + (i + 1), -1);
                    if (ids[i] < 0) { enabled = false; return; }
                }
            }

            private void Update()
            {
                timer += BraveTime.DeltaTime;
                if (timer < FrameSeconds) return;
                timer = 0f;
                frame = (frame + 1) % ids.Length;
                sprite.SetSprite(ids[frame]);
            }
        }

        /// <summary>Charms (or stuns) the enemy hit, then bursts once where the tin stops and charms the splash.</summary>
        public class CanBurst : MonoBehaviour
        {
            private AIActor directHit;
            private bool burst;

            private void Start()
            {
                Projectile p = GetComponent<Projectile>();
                if (p == null) return;
                p.OnHitEnemy += OnHitEnemy;
                p.OnDestruction += OnDestruction;
            }

            private void OnHitEnemy(Projectile p, SpeculativeRigidbody body, bool fatal)
            {
                if (body == null || body.aiActor == null) return;
                directHit = body.aiActor;
                if (!fatal) FallInLove(directHit, CharmSeconds(p));
            }

            private void OnDestruction(Projectile p)
            {
                if (burst || p == null) return;
                burst = true;
                Vector2 center = p.specRigidbody != null ? p.specRigidbody.UnitCenter : (Vector2)p.transform.position;
                PlutoVFX.Spawn(PlutoVFX.GravyBurst, center);
                PlutoVFX.Spawn(PlutoVFX.LoveBurst, center);
                AkSoundEngine.PostEvent("Play_OBJ_enemy_charmed_01", GameManager.Instance.gameObject);

                RoomHandler room = center.GetAbsoluteRoom();
                List<AIActor> enemies = room != null ? room.GetActiveEnemies(RoomHandler.ActiveEnemyType.All) : null;
                if (enemies == null) return;
                bool dinner = DinnerTime(p);
                float radius = dinner ? PlutoConfig.CanSplashRadius * 1.5f : PlutoConfig.CanSplashRadius;
                float seconds = CharmSeconds(p);
                for (int i = 0; i < enemies.Count; i++)
                {
                    AIActor enemy = enemies[i];
                    if (enemy == null || enemy == directHit) continue;
                    if (Vector2.Distance(enemy.CenterPosition, center) > radius) continue;
                    FallInLove(enemy, seconds);
                }
            }

            private static bool DinnerTime(Projectile p)
            {
                PlayerController thrower = p != null ? p.Owner as PlayerController : null;
                return thrower != null && thrower.PlayerHasActiveSynergy(PlutoSynergies.DinnerTime);
            }

            private static float CharmSeconds(Projectile p)
            {
                return DinnerTime(p) ? PlutoConfig.CharmDuration * 2f : PlutoConfig.CharmDuration;
            }

            private static void FallInLove(AIActor enemy, float seconds)
            {
                if (enemy == null || enemy.healthHaver == null || enemy.healthHaver.IsDead) return;
                if (enemy.healthHaver.IsBoss)
                {
                    // Predictable boss behaviour: a fixed stun instead of AI-dependent charm.
                    if (enemy.behaviorSpeculator != null) enemy.behaviorSpeculator.Stun(PlutoConfig.BossStunSeconds, true);
                    return;
                }
                enemy.ApplyEffect(PlutoCharmEffect.Create(seconds), 1f, null);
            }
        }
    }
}
