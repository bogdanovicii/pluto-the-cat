using UnityEngine;
using Gungeon;
using Alexandria.ItemAPI;
using Alexandria.Misc;

namespace PlutoTheCat
{
    /// <summary>
    /// Katana: the samurai costume's second starter weapon (2.16.0). Blasphemy's rules through the vanilla IsHeroSword
    /// code path with a longer reach: the swing destroys enemy bullets, a piercing sakura wave flies out only at full
    /// health (Gun.HandleSlash), and reloading clears bullets around Pluto (Gun.Reload). Verified in the decompile;
    /// see docs/superpowers/plans/2026-09-14-samurai-pluto-2160.md, Task 5.
    /// </summary>
    public class KatanaGun : GunBehaviour
    {
        public const string ID = "pluto:katana";

        // Swing radius = 1.85 x |Casing - PrimaryHand| (Gun.HandleHeroSwordSlash). The jtk2d puts PrimaryHand on the
        // handle (6, 13) and Casing at the blade tip (41, 13); CasingReach below pushes Casing further out.
        private const float CasingReachUnits = 2.4f;

        public static void Add()
        {
            Gun gun = ETGMod.Databases.Items.NewGun("Katana", "pluto_katana");
            Game.Items.Rename("outdated_gun_mods:katana", ID);
            gun.gameObject.AddComponent<KatanaGun>();
            gun.SetShortDescription("Nine Lives, One Blade");
            gun.SetLongDescription(
                "A curved blade with a gold guard and a black-and-white wrapped handle. Its swing cuts enemy bullets out " +
                "of the air, and while Pluto is unhurt every swing sends a crescent of sakura petals flying ahead. " +
                "Reloading is a quick flourish that knocks nearby bullets away.\n\n" +
                "Samurai Pluto trained with it every morning on the laundry basket. The laundry basket did not survive.");

            gun.SetupSprite(null, "pluto_katana_idle_001", 12);
            gun.SetAnimationFPS(gun.shootAnimation, 16);
            gun.SetAnimationFPS(gun.reloadAnimation, 12);

            Gun blasphemy = PickupObjectDatabase.GetById(417) as Gun;
            gun.AddProjectileModuleFrom("blasphemy", true, false);
            gun.IsHeroSword = true;
            gun.HeroSwordDoesntBlank = false;          // keeps the full-health wave, the bullet destroy and the reload blank
            gun.blankReloadRadius = 2.5f;              // vanilla default is 1
            if (blasphemy != null)
            {
                gun.muzzleFlashEffects = blasphemy.muzzleFlashEffects;   // the slash VFX and sound
                gun.gunSwitchGroup = blasphemy.gunSwitchGroup;
                gun.gunScreenShake = blasphemy.gunScreenShake;
            }
            gun.DefaultModule.numberOfShotsInClip = 1000;
            gun.reloadTime = 0.6f;
            gun.SetBaseMaxAmmo(1000);
            gun.gunHandedness = GunHandedness.OneHanded;
            gun.barrelOffset.transform.localPosition = new Vector3(41f / 16f, 13f / 16f, 0f);

            // Starter flags.
            gun.InfiniteAmmo = true;
            gun.CanBeDropped = false;
            gun.PreventStartingOwnerFromDropping = true;
            gun.quality = PickupObject.ItemQuality.EXCLUDED;

            // The full-health wave: a copy of Blasphemy's projectile with the sakura crescent sprite, piercing.
            Projectile baseWave = gun.DefaultModule.projectiles.Count > 0 ? gun.DefaultModule.projectiles[0] : null;
            if (baseWave != null)
            {
                GameObject waveObj = Object.Instantiate(baseWave.gameObject);
                waveObj.SetActive(false);
                FakePrefab.MarkAsFakePrefab(waveObj);
                Object.DontDestroyOnLoad(waveObj);
                Projectile wave = waveObj.GetComponent<Projectile>();
                wave.baseData.damage = 10f;            // also the swing damage (HandleHeroSwordSlash reads the module projectile)
                wave.SetProjectileSpriteRight("pluto_katana_wave_001", 16, 16, false, tk2dBaseSprite.Anchor.MiddleCenter, 14, 14);
                wave.gameObject.GetOrAddComponent<PierceProjModifier>().penetration = 5;
                gun.DefaultModule.projectiles[0] = wave;
            }

            ETGMod.Databases.Items.Add(gun, null, "ANY");

            // Reach: push Casing outward after the sprite setup, then log what the game will use.
            Transform casing = gun.transform.Find("Casing");
            Transform hand = gun.transform.Find("PrimaryHand");
            if (casing != null)
            {
                casing.localPosition = new Vector3(CasingReachUnits, casing.localPosition.y, casing.localPosition.z);
                float handX = hand != null ? hand.localPosition.x : 0f;
                Plugin.Log("katana reach: Casing x=" + casing.localPosition.x.ToString("0.00") + ", PrimaryHand x=" + handX.ToString("0.00") +
                           ", swing radius ~" + (1.85f * Mathf.Abs(casing.localPosition.x - handX)).ToString("0.00") + " units");
            }
            else
            {
                Plugin.Log("katana reach: no Casing transform found; the swing uses the vanilla reach (plan Task 5 fallback)");
            }
        }
    }
}
