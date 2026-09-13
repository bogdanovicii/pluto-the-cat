using UnityEngine;
using Gungeon;
using Alexandria.ItemAPI;
using Alexandria.Misc;

namespace PlutoTheCat
{
    /// <summary>
    /// Royal Canin Gravy Pouch: Wet Pluto's alt-costume starter gun. Squirts slow gravy globs that
    /// hit harder than kibble and have a small chance to make the target fall in love.
    /// </summary>
    public class GravyPouchGun : GunBehaviour
    {
        public const string ID = "pluto:gravy_pouch";
        public const float CharmChance = 0.2f;
        public const float CharmSeconds = 4f;

        public static void Add()
        {
            Gun gun = ETGMod.Databases.Items.NewGun("Royal Canin Gravy Pouch", "pluto_gravy_pouch");
            Game.Items.Rename("outdated_gun_mods:royal_canin_gravy_pouch", ID);
            gun.gameObject.AddComponent<GravyPouchGun>();
            gun.SetShortDescription("Thin Slices In Gravy");
            gun.SetLongDescription(
                "A torn-open pouch of ROYAL CANIN Kitten. Squeeze, and gravy flies. Anything hit has a small chance " +
                "to decide it loves Pluto after all.\n\n" +
                "Wet Pluto only carries this because the kibble bag got soaked in the bath. He is not happy about it.");

            gun.SetupSprite(null, "pluto_gravy_pouch_idle_001", 10);
            gun.SetAnimationFPS(gun.shootAnimation, 12);
            gun.SetAnimationFPS(gun.reloadAnimation, 8);

            gun.AddProjectileModuleFrom("klobb", true, false);
            gun.gunSwitchGroup = (PickupObjectDatabase.GetById(31) as Gun).gunSwitchGroup;
            gun.DefaultModule.shootStyle = ProjectileModule.ShootStyle.SemiAutomatic;
            gun.DefaultModule.sequenceStyle = ProjectileModule.ProjectileSequenceStyle.Random;
            gun.DefaultModule.ammoType = GameUIAmmoType.AmmoType.SMALL_BULLET;
            gun.DefaultModule.ammoCost = 1;
            gun.DefaultModule.cooldownTime = 0.28f;
            gun.DefaultModule.angleVariance = 4f;
            gun.DefaultModule.numberOfShotsInClip = 6;
            gun.reloadTime = 1.1f;
            gun.SetBaseMaxAmmo(300);
            gun.gunClass = GunClass.PISTOL;
            gun.gunHandedness = GunHandedness.OneHanded;
            gun.barrelOffset.transform.localPosition = new Vector3(22f / 16f, 6f / 16f, 0f);   // pouch spout, 24x14 sprite

            gun.InfiniteAmmo = true;
            gun.PreventStartingOwnerFromDropping = true;
            gun.quality = PickupObject.ItemQuality.EXCLUDED;

            Projectile gravy = ProjectileUtility.SetupProjectile(56);
            gravy.gameObject.name = "pluto_gravy_projectile";
            gravy.baseData.damage = 7f;
            gravy.baseData.speed = 12f;
            gravy.baseData.range = 14f;
            gravy.baseData.force = 8f;
            gravy.shouldRotate = false;
            gravy.SetProjectileSpriteRight("pluto_gravy_001", 7, 7, false, tk2dBaseSprite.Anchor.MiddleCenter, 6, 6);
            gravy.gameObject.AddComponent<GravyCharm>();
            gun.DefaultModule.projectiles[0] = gravy;

            ETGMod.Databases.Items.Add(gun, null, "ANY");
        }

        public class GravyCharm : MonoBehaviour
        {
            private void Start()
            {
                Projectile p = GetComponent<Projectile>();
                if (p != null) p.OnHitEnemy += (proj, rb, fatal) =>
                {
                    if (fatal || rb == null || rb.aiActor == null || rb.aiActor.healthHaver == null) return;
                    if (rb.aiActor.healthHaver.IsBoss || Random.value > CharmChance) return;
                    rb.aiActor.ApplyEffect(PlutoCharmEffect.Create(CharmSeconds), 1f, null);
                };
            }
        }
    }
}
