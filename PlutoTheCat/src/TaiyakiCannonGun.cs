using System.Collections.Generic;
using UnityEngine;
using Gungeon;
using Dungeonator;
using Alexandria.ItemAPI;
using Alexandria.Misc;

namespace PlutoTheCat
{
    /// <summary>
    /// Taiyaki Cannon: the samurai costume's starter gun (2.16.0). A golden taiyaki held like a pistol fires mini taiyaki
    /// from its bean-filled mouth; every hit puffs bonito flakes. Reload squeezes a Churu tube into the tail, and a reload
    /// that started from an empty clip ends with a Churu drop spat toward the aim (the samurai answer to the hairball).
    /// Sprites: reference/art/taiyaki_cannon (pluto-artist, Gemini first; reload clip from reference/gemini/taiyaki_cannon/reload_v2.py),
    /// copied by tools/make_art.py.
    /// </summary>
    public class TaiyakiCannonGun : GunBehaviour
    {
        public const string ID = "pluto:taiyaki_cannon";

        // Churu drop finisher. Numbers stay small on purpose: one drop per empty-clip reload. A full cycle is 10 shots
        // (1.8-2.0 s) + 0.9 s reload, so 5 direct damage adds ~1.8 DPS to the gun's 40 against one target (~4 %);
        // the 3-damage splash only touches other enemies within 1.5 tiles.
        public const float ChuruDropDamage = 5f;
        public const float ChuruSplashDamage = 3f;
        public const float ChuruSplashRadius = 1.5f;

        private static Projectile churuDropPrefab;
        private static bool loggedDrop;

        public static void Add()
        {
            Gun gun = ETGMod.Databases.Items.NewGun("Taiyaki Cannon", "pluto_taiyaki_cannon");
            Game.Items.Rename("outdated_gun_mods:taiyaki_cannon", ID);
            gun.gameObject.AddComponent<TaiyakiCannonGun>();
            gun.SetShortDescription("Red Bean Inside");
            gun.SetLongDescription(
                "A golden taiyaki, the fish-shaped cake from the festival stall, filled with sweet red bean and pressed " +
                "into service as a sidearm. It spits mini taiyaki from its mouth, and whatever they hit is showered " +
                "in bonito flakes.\n\n" +
                "Samurai Pluto keeps it topped up with a Churu tube squeezed into the tail. He has been told this is " +
                "not how taiyaki work. He does not care.\n\n" +
                "Refill it from an empty clip and the last squeeze comes out of the mouth: a Churu drop flies toward " +
                "your aim for 5 damage and splashes 3 on enemies close to where it lands.");

            gun.SetupSprite(null, "pluto_taiyaki_cannon_idle_001", 10);
            gun.SetAnimationFPS(gun.shootAnimation, 12);
            // Reload clip: 9 frames at 10 fps = 0.9 s = reloadTime, so the drop leaves the mouth as the reload ends.
            gun.SetAnimationFPS(gun.reloadAnimation, 10);

            gun.AddProjectileModuleFrom("klobb", true, false);
            gun.gunSwitchGroup = (PickupObjectDatabase.GetById(31) as Gun).gunSwitchGroup;
            gun.DefaultModule.shootStyle = ProjectileModule.ShootStyle.SemiAutomatic;
            gun.DefaultModule.sequenceStyle = ProjectileModule.ProjectileSequenceStyle.Random;
            gun.DefaultModule.ammoType = GameUIAmmoType.AmmoType.SMALL_BULLET;
            gun.DefaultModule.ammoCost = 1;
            // 2.16.2 buff (user: "a little bit underpowered"): 8 dmg / 0.20 s = 40 DPS against the Kibble Sack's 35
            // (2 x 3.5 / 0.20 s). One precise shot instead of two spread kibble, so it sits a notch above.
            gun.DefaultModule.cooldownTime = 0.20f;
            gun.DefaultModule.angleVariance = 4f;
            gun.DefaultModule.numberOfShotsInClip = PlutoConfig.TaiyakiClip;
            gun.reloadTime = 0.9f;
            gun.SetBaseMaxAmmo(300);
            gun.gunClass = GunClass.PISTOL;
            gun.gunHandedness = GunHandedness.OneHanded;

            // Mini taiyaki leave the bean-filled mouth (WeaponLayout, generated from tools/weapon_layout.py).
            gun.barrelOffset.transform.localPosition = new Vector3(WeaponLayout.TAIYAKI_CANNON_MUZZLE_X / 16f, WeaponLayout.TAIYAKI_CANNON_MUZZLE_Y / 16f, 0f);

            // Starter-gun flags.
            gun.InfiniteAmmo = true;
            gun.PreventStartingOwnerFromDropping = true;
            gun.quality = PickupObject.ItemQuality.EXCLUDED;

            Projectile taiyaki = ProjectileUtility.SetupProjectile(56); // clone the .38 Special bullet
            taiyaki.gameObject.name = "pluto_mini_taiyaki_projectile";
            taiyaki.baseData.damage = PlutoConfig.TaiyakiDamage;
            taiyaki.baseData.speed = 17f;
            taiyaki.baseData.range = 18f;
            taiyaki.baseData.force = 8f;
            taiyaki.shouldRotate = true;
            taiyaki.SetProjectileSpriteRight("pluto_mini_taiyaki_001", 12, 6, false, tk2dBaseSprite.Anchor.MiddleCenter, 10, 5);
            taiyaki.gameObject.AddComponent<BonitoPuff>();
            gun.DefaultModule.projectiles[0] = taiyaki;

            ETGMod.Databases.Items.Add(gun, null, "ANY");

            // Churu drop: a short, slow lob (same cloned-projectile pattern as the Kibble Sack hairball).
            churuDropPrefab = ProjectileUtility.SetupProjectile(56);
            churuDropPrefab.gameObject.name = "pluto_churu_drop_projectile";
            churuDropPrefab.baseData.damage = ChuruDropDamage;
            churuDropPrefab.baseData.speed = 11f;
            churuDropPrefab.baseData.range = 7f;
            churuDropPrefab.baseData.force = 6f;
            churuDropPrefab.shouldRotate = false;
            churuDropPrefab.SetProjectileSpriteRight("pluto_churu_drop_001", 9, 10, false, tk2dBaseSprite.Anchor.MiddleCenter, 7, 8);
            churuDropPrefab.gameObject.AddComponent<ChuruSplash>();
        }

        /// <summary>A reload that starts from an empty clip (manual or automatic) earns the drop at its end.</summary>
        public override void OnAutoReload(PlayerController player, Gun gun)
        {
            base.OnAutoReload(player, gun);
            if (!PlutoConfig.ChuruDropEnabled || player == null || gun == null || churuDropPrefab == null) return;
            if (Time.time < busyUntil) return;                 // one drop per reload even if the hook fires twice
            busyUntil = Time.time + gun.AdjustedReloadTime + 1f;
            StartCoroutine(DropWhenReloaded(player, gun));
        }

        // GunBehaviour has no reload-ended hook (that is AdvancedGunBehavior's), so wait for Gun.IsReloading to clear.
        // A time window instead of a flag: switching guns deactivates this object and kills the coroutine mid-wait,
        // and a flag left set would block every later drop.
        private float busyUntil;

        private System.Collections.IEnumerator DropWhenReloaded(PlayerController player, Gun gun)
        {
            float deadline = busyUntil;
            yield return null;
            while (gun != null && gun.IsReloading && Time.time < deadline) yield return null;
            // A reload cancelled by a gun switch or a drop earns nothing: the gun must still be in hand and refilled.
            if (gun == null || player == null || gun.IsReloading || player.CurrentGun != gun || gun.ClipShotsRemaining <= 0) yield break;
            SpitDrop(player, gun);
        }

        private void SpitDrop(PlayerController player, Gun gun)
        {
            Vector2 dir = (player.unadjustedAimPoint.XY() - player.CenterPosition).normalized;
            float angle = BraveMathCollege.Atan2Degrees(dir);
            GameObject go = SpawnManager.SpawnProjectile(churuDropPrefab.gameObject, gun.barrelOffset.position, Quaternion.Euler(0f, 0f, angle), true);
            Projectile p = go != null ? go.GetComponent<Projectile>() : null;
            if (p == null)
            {
                Plugin.Log("taiyaki churu drop: projectile did not spawn");
                return;
            }
            p.Owner = player;
            p.Shooter = player.specRigidbody;
            player.DoPostProcessProjectile(p);
            AkSoundEngine.PostEvent("Play_OBJ_item_throw_01", player.gameObject);
            if (!loggedDrop)
            {
                loggedDrop = true;
                Plugin.Log("taiyaki churu drop: empty-clip reload ended, drop spawned (" + p.baseData.damage + " damage, splash "
                    + ChuruSplashDamage + " within " + ChuruSplashRadius + " tiles)");
            }
        }

        /// <summary>Every enemy hit puffs pale pink bonito flakes.</summary>
        public class BonitoPuff : MonoBehaviour
        {
            private void Start()
            {
                Projectile p = GetComponent<Projectile>();
                if (p == null) return;
                p.OnHitEnemy += (proj, body, fatal) =>
                {
                    if (body != null) PlutoVFX.Spawn(PlutoVFX.Bonito, body.UnitCenter);
                };
            }
        }

        /// <summary>Where the drop stops (enemy, wall or end of range) it splashes: bonito puff, small damage to the others nearby.</summary>
        public class ChuruSplash : MonoBehaviour
        {
            private static bool loggedSplash;
            private AIActor directHit;
            private bool splashed;

            private void Start()
            {
                Projectile p = GetComponent<Projectile>();
                if (p == null) return;
                p.OnHitEnemy += (proj, body, fatal) => { if (body != null) directHit = body.aiActor; };
                p.OnDestruction += Splash;
            }

            private void Splash(Projectile p)
            {
                if (splashed || p == null) return;
                splashed = true;
                Vector2 center = p.specRigidbody != null ? p.specRigidbody.UnitCenter : (Vector2)p.transform.position;
                PlutoVFX.Spawn(PlutoVFX.Bonito, center);
                RoomHandler room = center.GetAbsoluteRoom();
                List<AIActor> enemies = room != null ? room.GetActiveEnemies(RoomHandler.ActiveEnemyType.All) : null;
                int hits = 0;
                if (enemies != null)
                {
                    for (int i = enemies.Count - 1; i >= 0; i--)   // backwards: a kill can remove the enemy from the list
                    {
                        AIActor enemy = enemies[i];
                        if (enemy == null || enemy == directHit || enemy.healthHaver == null || enemy.healthHaver.IsDead) continue;
                        if (Vector2.Distance(enemy.CenterPosition, center) > ChuruSplashRadius) continue;
                        Vector2 push = (enemy.CenterPosition - center).normalized;
                        enemy.healthHaver.ApplyDamage(ChuruSplashDamage, push, "Churu splash", CoreDamageTypes.None, DamageCategory.Normal, false, null, false);
                        hits++;
                    }
                }
                if (!loggedSplash)
                {
                    loggedSplash = true;
                    Plugin.Log("taiyaki churu drop: first splash, direct hit " + (directHit != null) + ", splash hits " + hits);
                }
            }
        }
    }
}
