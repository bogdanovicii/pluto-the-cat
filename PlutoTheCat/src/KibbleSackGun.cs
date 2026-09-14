using System.Collections;
using UnityEngine;
using Gungeon;
using Alexandria.ItemAPI;
using Alexandria.Misc;

namespace PlutoTheCat
{
    /// <summary>
    /// Royal Kibble Sack: Pluto's starter gun. Two kibble per pawful at a small spread, each
    /// bouncing once. 1 in 20 is a big chunk. Kibble that lands sometimes leaves crumbs the
    /// player can walk over for +1 ammo in the other gun. With Complete Feline Nutrition the kibble homes.
    /// </summary>
    public class KibbleSackGun : GunBehaviour
    {
        public const string ID = "pluto:kibble_sack";
        public static int PickupId;
        public static int RedDotSpriteId = -1;
        public static int CrumbSpriteId = -1;
        public static int HairballSpriteId = -1;
        private static Projectile hairballPrefab;

        public static void Add()
        {
            Gun gun = ETGMod.Databases.Items.NewGun("Royal Kibble Sack", "pluto_kibble_sack");
            Game.Items.Rename("outdated_gun_mods:royal_kibble_sack", ID);
            gun.gameObject.AddComponent<KibbleSackGun>();
            gun.SetShortDescription("Feline Health Nutrition");
            gun.SetLongDescription(
                "A 2 kg bag of ROYAL CANIN Sterilised 37, the dry food Pluto has eaten every day of his life. " +
                "Thrown two kibble at a time. Each kibble bounces once, because kibble always ends up under the fridge, " +
                "and one in twenty is a big chunk from the bottom of the bag. Kibble that lands leaves crumbs; " +
                "walk over them to top up whatever else you are carrying.\n\n" +
                "Pluto was a small, hungry tabby when the vet first handed him a sample of this stuff. " +
                "He has defended the bag ever since: from the dog next door, from the vacuum cleaner, and now " +
                "from the Gundead. He would much rather eat it, but the Gungeon is not going to feed itself.\n\n" +
                "Some walls sound hollow. A few pawfuls of kibble against a suspicious wall will crack it, and " +
                "a few more open it.");

            gun.SetupSprite(null, "pluto_kibble_sack_idle_001", 10);
            gun.SetAnimationFPS(gun.shootAnimation, 14);
            gun.SetAnimationFPS(gun.reloadAnimation, 8);

            gun.AddProjectileModuleFrom("klobb", true, false);
            gun.gunSwitchGroup = (PickupObjectDatabase.GetById(31) as Gun).gunSwitchGroup; // Klobbe sounds
            gun.DefaultModule.shootStyle = ProjectileModule.ShootStyle.SemiAutomatic;
            gun.DefaultModule.sequenceStyle = ProjectileModule.ProjectileSequenceStyle.Random;
            gun.DefaultModule.ammoType = GameUIAmmoType.AmmoType.SMALL_BULLET;
            gun.DefaultModule.ammoCost = 1;
            gun.DefaultModule.cooldownTime = 0.20f;
            gun.DefaultModule.angleVariance = 5f;
            gun.DefaultModule.angleFromAim = -4f;
            gun.DefaultModule.numberOfShotsInClip = PlutoConfig.KibbleClip;
            gun.reloadTime = 1.0f;
            gun.SetBaseMaxAmmo(350);
            gun.gunClass = GunClass.PISTOL;
            gun.gunHandedness = GunHandedness.OneHanded;

            // Kibble leaves the torn-open zip top of the bag (right end of the 32x18 sprite). Units: pixels / 16.
            gun.barrelOffset.transform.localPosition = new Vector3(29f / 16f, 9f / 16f, 0f);

            // Starter-gun flags.
            gun.InfiniteAmmo = true;
            gun.PreventStartingOwnerFromDropping = true;
            gun.quality = PickupObject.ItemQuality.EXCLUDED;

            Projectile kibble = ProjectileUtility.SetupProjectile(56); // clone the .38 Special bullet
            kibble.gameObject.name = "pluto_kibble_projectile";
            kibble.baseData.damage = PlutoConfig.KibbleDamage;   // x2 kibble per shot, a notch above the Pilot's 5
            kibble.baseData.speed = 17f;
            kibble.baseData.range = 20f;
            kibble.baseData.force = 6f;
            kibble.shouldRotate = true;      // pointy end forward, like a thrown kibble
            kibble.SetProjectileSpriteRight("pluto_kibble_001", 8, 8, false, tk2dBaseSprite.Anchor.MiddleCenter, 6, 6);

            BounceProjModifier bounce = kibble.gameObject.GetOrAddComponent<BounceProjModifier>();
            bounce.numberOfBounces = 1;
            bounce.percentVelocityToLoseOnBounce = 0.5f;
            kibble.gameObject.AddComponent<KibbleCrumbDropper>();

            gun.DefaultModule.projectiles[0] = kibble;

            // Second kibble per pawful: a free clone of the module, angled the other way.
            ProjectileModule second = ProjectileModule.CreateClone(gun.DefaultModule, false);
            second.ammoCost = 0;
            second.angleFromAim = 4f;
            second.projectiles[0] = kibble;
            gun.Volley.projectiles.Add(second);

            ETGMod.Databases.Items.Add(gun, null, "ANY");
            PickupId = gun.PickupObjectId;

            // Small sprites used by crumbs and the Laser Pointer decoy, added to the vanilla item collection.
            CrumbSpriteId = SpriteBuilder.AddSpriteToCollection(Plugin.ITEM_ROOT + "/kibble_crumb.png", SpriteBuilder.itemCollection);
            RedDotSpriteId = SpriteBuilder.AddSpriteToCollection(Plugin.ITEM_ROOT + "/laser_dot.png", SpriteBuilder.itemCollection);

            // Hairball: a slow, fat, stunning lump coughed up when reloading an empty clip.
            hairballPrefab = ProjectileUtility.SetupProjectile(56);
            hairballPrefab.gameObject.name = "pluto_hairball_projectile";
            hairballPrefab.baseData.damage = 6f;
            hairballPrefab.baseData.speed = 8f;
            hairballPrefab.baseData.range = 9f;
            hairballPrefab.baseData.force = 14f;
            hairballPrefab.shouldRotate = false;
            hairballPrefab.SetProjectileSpriteRight("pluto_hairball_001", 10, 10, false, tk2dBaseSprite.Anchor.MiddleCenter, 8, 8);
            hairballPrefab.gameObject.AddComponent<HairballStun>();
        }

        /// <summary>Fires for every reload that starts from an empty clip (manual or automatic).</summary>
        public override void OnAutoReload(PlayerController player, Gun gun)
        {
            base.OnAutoReload(player, gun);
            if (!PlutoConfig.HairballEnabled || player == null || gun == null || hairballPrefab == null) return;
            Vector2 dir = (player.unadjustedAimPoint.XY() - player.CenterPosition).normalized;
            float angle = BraveMathCollege.Atan2Degrees(dir);
            GameObject go = SpawnManager.SpawnProjectile(hairballPrefab.gameObject, gun.barrelOffset.position, Quaternion.Euler(0f, 0f, angle), true);
            Projectile p = go.GetComponent<Projectile>();
            if (p == null) return;
            p.Owner = player;
            p.Shooter = player.specRigidbody;
            player.DoPostProcessProjectile(p);
            AkSoundEngine.PostEvent("Play_ENM_bulletking_vomit_01", player.gameObject);
        }

        /// <summary>Hairball hits stun for 1.5 s.</summary>
        public class HairballStun : MonoBehaviour
        {
            private void Start()
            {
                Projectile p = GetComponent<Projectile>();
                if (p != null) p.OnHitEnemy += (proj, rb, fatal) =>
                {
                    if (!fatal && rb != null && rb.aiActor != null && rb.aiActor.behaviorSpeculator != null)
                        rb.aiActor.behaviorSpeculator.Stun(1.5f, true);
                };
            }
        }

        // ---- Secret walls. Only infinite-ammo guns may damage a cracked secret-room wall (Projectile
        // .OnRigidbodyCollision), and the sack has infinite ammo; each kibble also adds a bite on top of
        // its own damage so the wall cracks after a few pawfuls (walls have 100 hit points, cracks show
        // at 50 % and 10 %, then it gives way).
        private static void SecretDoorBite(SpeculativeRigidbody myBody, PixelCollider myCollider, SpeculativeRigidbody other, PixelCollider otherCollider)
        {
            if (other == null) return;
            MajorBreakable wall = other.majorBreakable;
            if (wall == null || !wall.IsSecretDoor) return;
            Vector2 dir = myBody != null ? myBody.Velocity.normalized : Vector2.zero;
            wall.ApplyDamage(PlutoConfig.SecretDoorDamage, dir, false, false, true);
            AkSoundEngine.PostEvent("Play_OBJ_rock_break_01", other.gameObject);
        }

        public override void PostProcessProjectile(Projectile projectile)
        {
            base.PostProcessProjectile(projectile);
            if (projectile == null) return;
            PlayerController owner = projectile.Owner as PlayerController;

            if (PlutoConfig.SecretDoorDamage > 0f && projectile.specRigidbody != null)
                projectile.specRigidbody.OnPreRigidbodyCollision += SecretDoorBite;

            if (Random.value < PlutoConfig.KibbleCritChance)
            {
                projectile.baseData.damage *= 3.5f;          // big chunk: ~12 damage
                projectile.AdditionalScaleMultiplier = 1.7f;
                projectile.baseData.force *= 2f;
            }

            if (owner != null && owner.PlayerHasActiveSynergy(PlutoSynergies.FelineNutrition))
            {
                HomingModifier homing = projectile.gameObject.GetOrAddComponent<HomingModifier>();
                homing.HomingRadius = 7f;
                homing.AngularVelocity = 420f;
            }
        }

        /// <summary>When a kibble dies against something, 25 % of the time it leaves crumbs for 8 s.</summary>
        public class KibbleCrumbDropper : MonoBehaviour
        {
            private void Start()
            {
                Projectile p = GetComponent<Projectile>();
                if (p != null) p.OnDestruction += OnGone;
            }

            private void OnGone(Projectile p)
            {
                if (p == null || Random.value > 0.25f) return;
                if (!(p.Owner is PlayerController)) return;
                SpawnCrumb(p.transform.position);
            }
        }

        public static void SpawnCrumb(Vector3 position)
        {
            if (CrumbSpriteId < 0) return;
            GameObject crumb = new GameObject("pluto_kibble_crumb");
            crumb.transform.position = position;
            tk2dSprite sprite = crumb.AddComponent<tk2dSprite>();
            sprite.SetSprite(SpriteBuilder.itemCollection, CrumbSpriteId);
            crumb.AddComponent<KibbleCrumb>();
        }

        /// <summary>Walk over crumbs: +1 ammo to the held gun if it is not the sack itself.</summary>
        public class KibbleCrumb : MonoBehaviour
        {
            private float life = 8f;

            private void Update()
            {
                life -= BraveTime.DeltaTime;
                if (life <= 0f) { Destroy(gameObject); return; }
                for (int i = 0; i < GameManager.Instance.AllPlayers.Length; i++)
                {
                    PlayerController player = GameManager.Instance.AllPlayers[i];
                    if (player == null || player.healthHaver.IsDead) continue;
                    if (Vector2.Distance(player.CenterPosition, transform.position) > 0.6f) continue;
                    Gun gun = player.CurrentGun;
                    if (gun != null && !gun.InfiniteAmmo && gun.PickupObjectId != PickupId && gun.ammo < gun.AdjustedMaxAmmo)
                        gun.GainAmmo(1);
                    AkSoundEngine.PostEvent("Play_OBJ_ammo_pickup_01", player.gameObject);
                    Destroy(gameObject);
                    return;
                }
            }
        }
    }
}
