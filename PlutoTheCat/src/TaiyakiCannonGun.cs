using UnityEngine;
using Gungeon;
using Alexandria.ItemAPI;
using Alexandria.Misc;

namespace PlutoTheCat
{
    /// <summary>
    /// Taiyaki Cannon: the samurai costume's starter gun (2.16.0). A golden taiyaki held like a pistol fires mini taiyaki
    /// from its bean-filled mouth; every hit puffs bonito flakes. Reload squeezes a Churu tube into the tail.
    /// Sprites: reference/art/taiyaki_cannon (pluto-artist, Gemini first), copied by tools/make_art.py.
    /// </summary>
    public class TaiyakiCannonGun : GunBehaviour
    {
        public const string ID = "pluto:taiyaki_cannon";

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
                "not how taiyaki work. He does not care.");

            gun.SetupSprite(null, "pluto_taiyaki_cannon_idle_001", 10);
            gun.SetAnimationFPS(gun.shootAnimation, 12);
            gun.SetAnimationFPS(gun.reloadAnimation, 8);

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
    }
}
