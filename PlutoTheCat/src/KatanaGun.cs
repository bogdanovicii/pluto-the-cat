using System.Collections.Generic;
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
        // handle and Casing at the blade tip (WeaponLayout, generated from tools/weapon_layout.py); CasingReach below
        // pushes Casing further out.
        private const float CasingReachUnits = WeaponLayout.KATANA_CASING_REACH_UNITS;

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
                "Samurai Pluto trained with it every morning on the laundry basket. The laundry basket did not survive. " +
                "Neither did the curtains, which he says were an accident, or the Blasphemy's pride, which he says was not.");

            gun.SetupSprite(null, "pluto_katana_idle_001", 12);
            gun.SetAnimationFPS(gun.shootAnimation, 20);   // 8-frame swing = 0.4 s, inside the 0.5 s hero sword cooldown
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
            gun.barrelOffset.transform.localPosition = new Vector3(WeaponLayout.KATANA_MUZZLE_X / 16f, WeaponLayout.KATANA_MUZZLE_Y / 16f, 0f);

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
            ShiftSwingFrames(gun);
            CopySwingAudio(gun, blasphemy);

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

        // The fire clip is the swing (2.16.1): the blade rotates around the grip, so its frames sit on a taller canvas
        // (WeaponLayout.KATANA_SWING_*) than idle/reload (KATANA_W/H, grip KATANA_HAND_*). Gun sprites are drawn from their
        // bottom-left corner, so each fire frame is moved down by the difference to keep the grip in Pluto's paw.
        private const int SwingGripOffsetPixels = WeaponLayout.KATANA_SWING_GRIP_OFFSET;

        /// <summary>
        /// Swing sound. Gun.Attack's IsHeroSword branch only starts the slash and plays the shoot clip; it never reaches the
        /// fire-audio code (HandleSpecificInitialGunShoot). Blasphemy's sound comes from audio events on its shoot clip frames,
        /// which tk2dSpriteAnimator.ProcessEvents posts. The Katana's clip is built from our own frames and had none, so the
        /// swing was silent. Copy Blasphemy's events onto the matching frames; if there are none, fall back to the normal
        /// gun-shot event on frame 0 (Attack has already set the WPN_Guns switch to Blasphemy's group on the gun object).
        /// </summary>
        private static void CopySwingAudio(Gun gun, Gun blasphemy)
        {
            tk2dSpriteAnimationClip ours = gun.spriteAnimator != null ? gun.spriteAnimator.GetClipByName(gun.shootAnimation) : null;
            if (ours == null || ours.frames == null || ours.frames.Length == 0)
            {
                Plugin.Log("katana sound: no fire clip found, swing stays silent");
                return;
            }
            tk2dSpriteAnimator theirAnim = blasphemy != null ? blasphemy.GetComponent<tk2dSpriteAnimator>() : null;
            tk2dSpriteAnimationClip theirs = theirAnim != null ? theirAnim.GetClipByName(blasphemy.shootAnimation) : null;
            List<string> copied = new List<string>();
            if (theirs != null && theirs.frames != null)
            {
                for (int i = 0; i < theirs.frames.Length; i++)
                {
                    tk2dSpriteAnimationFrame f = theirs.frames[i];
                    if (f == null || string.IsNullOrEmpty(f.eventAudio)) continue;
                    int j = Mathf.Min(ours.frames.Length - 1, Mathf.RoundToInt(i * (float)ours.frames.Length / theirs.frames.Length));
                    ours.frames[j].eventAudio = f.eventAudio;
                    ours.frames[j].triggerEvent = true;
                    copied.Add(f.eventAudio + "@" + j);
                }
            }
            if (copied.Count == 0)
            {
                ours.frames[0].eventAudio = "Play_WPN_gun_shot_01";
                ours.frames[0].triggerEvent = true;
                Plugin.Log("katana sound: Blasphemy's shoot clip has no audio events (" + (theirs == null ? "clip not found" : theirs.frames.Length + " frames") + "); using Play_WPN_gun_shot_01 on frame 0");
                return;
            }
            Plugin.Log("katana sound: copied Blasphemy swing audio " + string.Join(", ", copied.ToArray()));
        }

        private static void ShiftSwingFrames(Gun gun)
        {
            tk2dSpriteAnimationClip clip = gun.spriteAnimator != null ? gun.spriteAnimator.GetClipByName(gun.shootAnimation) : null;
            if (clip == null || clip.frames == null)
            {
                Plugin.Log("katana swing: no fire clip found, frames not shifted");
                return;
            }
            float dy = -SwingGripOffsetPixels / 16f;
            HashSet<int> shifted = new HashSet<int>();
            foreach (tk2dSpriteAnimationFrame frame in clip.frames)
            {
                if (!shifted.Add(frame.spriteId)) continue;          // a held frame reuses its definition
                tk2dSpriteDefinition def = frame.spriteCollection.spriteDefinitions[frame.spriteId];
                def.position0.y += dy;
                def.position1.y += dy;
                def.position2.y += dy;
                def.position3.y += dy;
            }
            Plugin.Log("katana swing: " + clip.frames.Length + " fire frames, grip shifted by " + SwingGripOffsetPixels + " px");
        }
    }
}
