using UnityEngine;
using Gungeon;
using Alexandria.ItemAPI;
using Alexandria.Misc;

namespace PlutoTheCat
{
    /// <summary>A short-ranged mist gun whose first enemy impact leaves conductive vanilla water.</summary>
    public class SprayBottleGun : GunBehaviour
    {
        public const string ID = "pluto:spray_bottle";
        private const float WaterRadius = 0.65f;
        private const float WaterSpreadSeconds = 0.2f;

        internal static GoopDefinition WaterGoop;
        private static bool loggedImpact;
        private static bool loggedFlinch;
        private static bool loggedBathTime;

        public static void Add()
        {
            Gun gun = ETGMod.Databases.Items.NewGun("Spray Bottle", "pluto_spray_bottle");
            Game.Items.Rename("outdated_gun_mods:spray_bottle", ID);
            gun.gameObject.AddComponent<SprayBottleGun>();
            gun.SetShortDescription("Counter Intelligence");
            gun.SetLongDescription(
                "Bogdan and Bianca bought this bottle to keep Pluto off the kitchen counter. It has never worked. " +
                "The water only made the counter more interesting, and the warning noise became his cue to jump down " +
                "exactly half a second before anyone reached him.\n\n" +
                "Pluto has decided to see whether it works on other people. The answer is still uncertain, but they " +
                "do flinch when the mist catches them in the face.");

            gun.SetupSprite(null, "pluto_spray_bottle_idle_001", 10);
            // The approved sprite set supplies two fire frames and three reload frames.
            gun.SetAnimationFPS(gun.shootAnimation, 12);
            gun.SetAnimationFPS(gun.reloadAnimation, 3);

            gun.AddProjectileModuleFrom("klobb", true, false);
            gun.gunSwitchGroup = (PickupObjectDatabase.GetById(31) as Gun).gunSwitchGroup;
            gun.DefaultModule.shootStyle = ProjectileModule.ShootStyle.SemiAutomatic;
            gun.DefaultModule.sequenceStyle = ProjectileModule.ProjectileSequenceStyle.Random;
            gun.DefaultModule.ammoType = GameUIAmmoType.AmmoType.SMALL_BULLET;
            gun.DefaultModule.ammoCost = 1;
            gun.DefaultModule.cooldownTime = PlutoConfig.SprayCooldown;
            gun.DefaultModule.angleVariance = 5f;
            gun.DefaultModule.numberOfShotsInClip = PlutoConfig.SprayClip;
            gun.reloadTime = PlutoConfig.SprayReloadSeconds;
            gun.SetBaseMaxAmmo(240);
            gun.gunClass = GunClass.PISTOL;
            gun.gunHandedness = GunHandedness.OneHanded;
            gun.barrelOffset.transform.localPosition = new Vector3(
                WeaponLayout.SPRAY_BOTTLE_MUZZLE_X / 16f,
                WeaponLayout.SPRAY_BOTTLE_MUZZLE_Y / 16f,
                0f);
            gun.quality = PickupObject.ItemQuality.C;

            Projectile mist = ProjectileUtility.SetupProjectile(56); // clone the known .38 Special player projectile
            mist.gameObject.name = "pluto_spray_mist_projectile";
            mist.baseData.damage = PlutoConfig.SprayDamage;
            mist.baseData.speed = 15f;
            mist.baseData.range = PlutoConfig.SprayRange;
            mist.baseData.force = PlutoConfig.SprayKnockback;
            mist.shouldRotate = false;
            mist.SetProjectileSpriteRight("pluto_spray_mist_001", 10, 8, false, tk2dBaseSprite.Anchor.MiddleCenter, 8, 6);
            mist.gameObject.AddComponent<SprayImpact>();
            gun.DefaultModule.projectiles[0] = mist;

            CacheWaterGoop();
            ETGMod.Databases.Items.Add(gun, null, "ANY");
        }

        /// <summary>Mega Douser (vanilla pickup 10) is the canonical non-damaging water-goop source.</summary>
        private static void CacheWaterGoop()
        {
            Gun megaDouser = PickupObjectDatabase.GetById(10) as Gun;
            Projectile waterProjectile = megaDouser != null && megaDouser.DefaultModule != null
                && megaDouser.DefaultModule.projectiles != null && megaDouser.DefaultModule.projectiles.Count > 0
                ? megaDouser.DefaultModule.projectiles[0]
                : null;
            GoopModifier modifier = waterProjectile != null ? waterProjectile.GetComponent<GoopModifier>() : null;
            WaterGoop = modifier != null ? modifier.goopDefinition : null;
            if (WaterGoop == null) Plugin.Log("spray bottle: vanilla Mega Douser water goop was not found");
        }

        /// <summary>One instance is cloned with each projectile; its guard permits exactly one actual enemy impact.</summary>
        public class SprayImpact : MonoBehaviour
        {
            private Projectile projectile;
            private bool impactHandled;

            private void Start()
            {
                projectile = GetComponent<Projectile>();
                if (projectile != null && projectile.specRigidbody != null)
                    projectile.specRigidbody.OnRigidbodyCollision += OnCollision;
            }

            private void OnDestroy()
            {
                if (projectile != null && projectile.specRigidbody != null)
                    projectile.specRigidbody.OnRigidbodyCollision -= OnCollision;
            }

            private void OnCollision(CollisionData collision)
            {
                if (impactHandled || projectile == null || collision == null || collision.OtherRigidbody == null) return;
                AIActor enemy = collision.OtherRigidbody.aiActor;
                PixelCollider mine = collision.MyPixelCollider;
                if (enemy == null || enemy.healthHaver == null || enemy.healthHaver.IsDead || mine == null) return;
                if (!CatItemKit.HitboxOverlaps(enemy, mine.UnitBottomLeft, mine.UnitTopRight)) return;
                impactHandled = true;

                AddWater(collision.Contact);
                PlayerController owner = projectile.Owner as PlayerController;
                bool eligibleActor = enemy.healthHaver != null
                    && !enemy.healthHaver.IsDead
                    && !enemy.IsHarmlessEnemy
                    && !enemy.healthHaver.IsBoss;

                // Bath Time is deliberately checked before ValidEnemy rejects an already charmed target.
                if (eligibleActor && owner != null && owner.PlayerHasActiveSynergy(PlutoSynergies.BathTime)
                    && PlutoCharmEffect.ExtendOwned(enemy, PlutoConfig.SprayCharmBonusSeconds))
                {
                    if (!loggedBathTime)
                    {
                        loggedBathTime = true;
                        Plugin.Log("spray bottle: Bath Time extended Pluto's charm by "
                            + PlutoConfig.SprayCharmBonusSeconds + " seconds");
                    }
                }

                if (!CatItemKit.ValidEnemy(enemy) || enemy.healthHaver.IsBoss) return;
                if (!CatSetRules.RollFlinch(Random.value, PlutoConfig.SprayFlinchChance)) return;
                // A flinch only cancels the current attack; it must never disable the behavior speculator.
                if (enemy.behaviorSpeculator != null) enemy.behaviorSpeculator.Interrupt();
                CatItemKit.Stun(enemy, PlutoConfig.SprayFlinchSeconds);
                if (!loggedFlinch)
                {
                    loggedFlinch = true;
                    Plugin.Log("spray bottle: first flinch interrupted and stunned a non-boss enemy for "
                        + PlutoConfig.SprayFlinchSeconds + " seconds");
                }
            }

            private static void AddWater(Vector2 point)
            {
                if (WaterGoop == null) return;
                DeadlyDeadlyGoopManager manager = DeadlyDeadlyGoopManager.GetGoopManagerForGoopType(WaterGoop);
                if (manager == null) return;
                manager.TimedAddGoopCircle(point, WaterRadius, WaterSpreadSeconds, false);
                if (!loggedImpact)
                {
                    loggedImpact = true;
                    Plugin.Log("spray bottle: first hit left vanilla water at " + point
                        + " (radius " + WaterRadius + ")");
                }
            }
        }
    }
}
