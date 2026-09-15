using System.Collections.Generic;
using UnityEngine;
using Alexandria.ItemAPI;
using Alexandria.Misc;
using Gungeon;

namespace PlutoTheCat
{
    /// <summary>
    /// Hairball (2.17 item, id pluto:hairball_item; unrelated to the Royal Kibble Sack's reload hairball). Thrown like
    /// the Wet Food Can; where it stops it bursts into a fur cloud for HairballItemSeconds. Enemy bullets inside the
    /// cloud move at HairballItemBulletSpeed of their speed: plain bullets through Projectile.Speed, bullet-script bullets
    /// through Bullet.TimeScale (so patterns keep their shape). Everything is restored when a bullet leaves the last cloud
    /// or the cloud ends. With Hack Attack (Wet Food Can) enemies caught in the burst fall in love.
    /// </summary>
    public class HairballItem : PlayerItem
    {
        public const string ID = "pluto:hairball_item";
        private const string SetupId = "pluto:hairball";
        private static Projectile hairballPrefab;

        public static void Init()
        {
            string name = "Hairball";
            GameObject obj = new GameObject(name);
            HairballItem item = obj.AddComponent<HairballItem>();
            ItemBuilder.AddSpriteToObject(name, Plugin.ITEM_ROOT + "/hairball_item_icon", obj);
            ItemBuilder.SetupItem(item, "Hack Hack Hack",
                "Coughs up a hairball that bursts into a cloud of fur. Enemy bullets inside the cloud can barely push through.\n\n" +
                "Not to be confused with the everyday hairball that comes up when the kibble sack runs dry. This one is " +
                "a whole winter coat, saved since October and delivered, as tradition demands, onto the good rug.\n\n" +
                "Gundead who have walked into one describe it as \"like a pillow, but angry\".",
                "pluto");
            if (Game.Items.ContainsID(SetupId) && !Game.Items.ContainsID(ID)) Game.Items.Rename(SetupId, ID);
            ItemBuilder.SetCooldownType(item, ItemBuilder.CooldownType.Damage, PlutoConfig.HairballItemCooldownDamage);
            item.consumable = false;
            item.quality = PickupObject.ItemQuality.C;

            hairballPrefab = ProjectileUtility.SetupProjectile(56);
            hairballPrefab.gameObject.name = "pluto_hairball_item_projectile";
            hairballPrefab.baseData.damage = 3f;
            hairballPrefab.baseData.speed = 12f;
            hairballPrefab.baseData.range = 8f;
            hairballPrefab.baseData.force = 8f;
            hairballPrefab.shouldRotate = false;
            hairballPrefab.SetProjectileSpriteRight("pluto_hairball_item_001", 12, 12, false, tk2dBaseSprite.Anchor.MiddleCenter, 10, 10);
            hairballPrefab.gameObject.AddComponent<Burst>();
        }

        public override void DoEffect(PlayerController user)
        {
            if (user == null || hairballPrefab == null) return;
            Vector2 dir = user.unadjustedAimPoint.XY() - user.CenterPosition;
            if (dir.sqrMagnitude < 0.0001f) dir = Vector2.right;
            GameObject go = SpawnManager.SpawnProjectile(hairballPrefab.gameObject, user.CenterPosition,
                Quaternion.Euler(0f, 0f, BraveMathCollege.Atan2Degrees(dir.normalized)), true);
            Projectile p = go.GetComponent<Projectile>();
            if (p == null) return;
            p.Owner = user;
            p.Shooter = user.specRigidbody;
            AkSoundEngine.PostEvent("Play_OBJ_item_throw_01", user.gameObject);
        }

        /// <summary>Spawns the fur cloud once, wherever the hairball stops.</summary>
        public class Burst : MonoBehaviour
        {
            private bool done;

            private void Start()
            {
                Projectile p = GetComponent<Projectile>();
                if (p != null) p.OnDestruction += OnDestruction;
            }

            private void OnDestruction(Projectile p)
            {
                if (done || p == null) return;
                done = true;
                Vector2 center = p.specRigidbody != null ? p.specRigidbody.UnitCenter : (Vector2)p.transform.position;
                GameObject cloud = new GameObject("pluto_fur_cloud");
                cloud.transform.position = center;
                cloud.AddComponent<FurCloud>();
                PlutoVFX.Spawn(PlutoVFX.FurPuff, center);
                AkSoundEngine.PostEvent("Play_OBJ_silenceblank_small_01", GameManager.Instance.gameObject);
                PlayerController owner = p.Owner as PlayerController;
                if (owner != null && owner.PlayerHasActiveSynergy(PlutoSynergies.HackAttack))
                {
                    foreach (AIActor enemy in CatItemKit.EnemiesNear(center, PlutoConfig.HairballItemRadius))
                    {
                        if (enemy.healthHaver.IsBoss) continue;
                        enemy.ApplyEffect(PlutoCharmEffect.Create(PlutoConfig.CharmDuration * 0.5f), 1f, null);
                    }
                    PlutoVFX.Spawn(PlutoVFX.LoveBurst, center);
                }
                Plugin.Log("hairball item: fur cloud at " + center);
            }
        }

        /// <summary>
        /// The cloud. Slowed bullets are tracked in one static table with a count of the clouds holding them, so
        /// overlapping clouds never restore a bullet early or slow it twice.
        /// </summary>
        public class FurCloud : MonoBehaviour
        {
            private class Slowed { public float speed; public float timeScale; public int clouds; }
            private static readonly Dictionary<Projectile, Slowed> slowed = new Dictionary<Projectile, Slowed>();
            private const float Tick = 0.1f;
            private readonly HashSet<Projectile> mine = new HashSet<Projectile>();
            private float timeLeft, tick, puff;
            private Vector2 center;

            private void Start()
            {
                center = transform.position;
                timeLeft = PlutoConfig.HairballItemSeconds;
            }

            private void Update()
            {
                float dt = BraveTime.DeltaTime;
                timeLeft -= dt; tick -= dt; puff -= dt;
                if (timeLeft <= 0f) { Destroy(gameObject); return; }
                float scale = CatItemRules.CloudVisualScale(timeLeft);
                if (puff <= 0f)
                {
                    puff = 0.2f;
                    PlutoVFX.Spawn(PlutoVFX.FurPuff, center + Random.insideUnitCircle * PlutoConfig.HairballItemRadius * scale);
                }
                if (tick > 0f) return;
                tick = Tick;
                Refresh();
            }

            private void Refresh()
            {
                List<Projectile> leaving = new List<Projectile>();
                foreach (Projectile p in mine)
                    if (p == null || !CatItemKit.IsEnemyBullet(p) || !Inside(p)) leaving.Add(p);
                foreach (Projectile p in leaving) Release(p);

                foreach (Projectile p in StaticReferenceManager.AllProjectiles)
                {
                    if (!CatItemKit.IsEnemyBullet(p) || mine.Contains(p) || !Inside(p)) continue;
                    Hold(p);
                }
            }

            private bool Inside(Projectile p)
            {
                Vector2 pos = p.specRigidbody != null ? p.specRigidbody.UnitCenter : (Vector2)p.transform.position;
                return CatItemRules.Inside((pos - center).sqrMagnitude, PlutoConfig.HairballItemRadius);
            }

            private void Hold(Projectile p)
            {
                mine.Add(p);
                Slowed s;
                if (slowed.TryGetValue(p, out s)) { s.clouds++; return; }
                s = new Slowed { speed = p.Speed, timeScale = 1f, clouds = 1 };
                slowed[p] = s;
                Brave.BulletScript.Bullet bullet = p.braveBulletScript != null ? p.braveBulletScript.bullet : null;
                if (bullet != null)
                {
                    s.timeScale = bullet.TimeScale;
                    bullet.TimeScale = s.timeScale * PlutoConfig.HairballItemBulletSpeed;
                }
                else
                {
                    p.Speed = CatItemRules.CloudBulletSpeed(s.speed, p.Speed, PlutoConfig.HairballItemBulletSpeed);
                }
            }

            private void Release(Projectile p)
            {
                mine.Remove(p);
                Slowed s;
                if (p == null || !slowed.TryGetValue(p, out s)) { if (p == null) Prune(); return; }
                if (--s.clouds > 0) return;
                slowed.Remove(p);
                Brave.BulletScript.Bullet bullet = p.braveBulletScript != null ? p.braveBulletScript.bullet : null;
                if (bullet != null) bullet.TimeScale = s.timeScale;
                else p.Speed = Mathf.Max(p.Speed, s.speed);
            }

            /// <summary>Destroyed bullets compare equal to null in Unity; drop their table entries.</summary>
            private static void Prune()
            {
                List<Projectile> dead = new List<Projectile>();
                foreach (Projectile p in slowed.Keys) if (p == null) dead.Add(p);
                foreach (Projectile p in dead) slowed.Remove(p);
            }

            private void OnDestroy()
            {
                foreach (Projectile p in new List<Projectile>(mine)) Release(p);
                mine.Clear();
                Prune();
            }
        }
    }
}
