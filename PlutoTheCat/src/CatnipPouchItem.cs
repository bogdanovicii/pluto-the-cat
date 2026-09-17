using System.Collections;
using UnityEngine;
using Alexandria.ItemAPI;

namespace PlutoTheCat
{
    /// <summary>
    /// Catnip Pouch (2.17): a timed active. Zoomies for CatnipSeconds (movement speed through CatTricks.AcquireSpeed, so it
    /// shares the MaxSpeedBonus cap, plus a rate-of-fire multiplier, an afterimage trail and drifting catnip leaves), then a
    /// catnap for CatnapSeconds at 80 % speed. With Nip And Tuck (Puffed Up) the zoomies start with a free puff.
    /// One loop counts zoomiesRemaining down, so Espresso (Coffee Mug) can extend a running zoomies and the catnap waits.
    /// Dropping the pouch or losing it mid-effect removes every modifier.
    /// </summary>
    public class CatnipPouchItem : PlayerItem
    {
        public const string ID = "pluto:catnip_pouch";
        private const float CatnapSpeed = 0.8f, LeafInterval = 0.3f;
        private PlayerController buffed;
        private Coroutine running;
        private StatModifier speedMod, fireMod, napMod;
        private AfterImageTrailController trail;
        private float zoomiesRemaining;
        private bool zooming;

        public static void Init()
        {
            string name = "Catnip Pouch";
            GameObject obj = new GameObject(name);
            CatnipPouchItem item = obj.AddComponent<CatnipPouchItem>();
            ItemBuilder.AddSpriteToObject(name, Plugin.ITEM_ROOT + "/catnip_pouch_icon", obj);
            ItemBuilder.SetupItem(item, "Zoomies",
                "Grants a burst of movement speed and rate of fire, followed by a short, drowsy nap.\n\n" +
                "Grown in the windowsill pot that Bogdan swears is just basil. Pluto has never once chewed the basil.\n\n" +
                "A Gun Nut who confiscated a pouch reported seeing Kaliber. She was also doing laps.",
                "pluto");
            ItemBuilder.SetCooldownType(item, ItemBuilder.CooldownType.Damage, PlutoConfig.CatnipCooldownDamage);
            item.consumable = false;
            item.quality = PickupObject.ItemQuality.C;
        }

        public override bool CanBeUsed(PlayerController user)
        {
            return user != null && running == null && base.CanBeUsed(user);
        }

        public override void DoEffect(PlayerController user)
        {
            if (user == null || running != null) return;
            running = user.StartCoroutine(Zoomies(user));
        }

        /// <summary>
        /// Espresso: adds bonus seconds to the zoomies currently running for this wearer. Returns false and changes
        /// nothing when the pouch is idle, napping, or held by someone else.
        /// </summary>
        public bool ExtendZoomies(PlayerController user, float bonus)
        {
            bool active = user != null && running != null && buffed == user && zooming && zoomiesRemaining > 0f;
            if (!active) return false;
            zoomiesRemaining = CatSetRules.ExtendRemaining(zoomiesRemaining, bonus, active);
            m_activeDuration = CatSetRules.ExtendDuration(m_activeDuration, bonus);
            Plugin.Log("catnip pouch: zoomies extended by " + bonus + " s (" + zoomiesRemaining + " s left)");
            return true;
        }

        private IEnumerator Zoomies(PlayerController user)
        {
            buffed = user;
            zooming = true;
            zoomiesRemaining = PlutoConfig.CatnipSeconds;
            IsCurrentlyActive = true;
            m_activeElapsed = 0f;
            m_activeDuration = PlutoConfig.CatnipSeconds;
            AkSoundEngine.PostEvent("Play_OBJ_dice_bless_01", user.gameObject);
            Plugin.Log("catnip pouch: zoomies for " + PlutoConfig.CatnipSeconds + " s");

            speedMod = CatTricks.AcquireSpeed(user, PlutoConfig.CatnipSpeedBonus);
            fireMod = CatItemKit.Mod(PlayerStats.StatType.RateOfFire, StatModifier.ModifyMethod.MULTIPLICATIVE, PlutoConfig.CatnipFireRateMultiplier);
            user.ownerlessStatModifiers.Add(fireMod);
            user.stats.RecalculateStats(user, false, false);
            if (user.sprite != null)
            {
                trail = user.sprite.gameObject.AddComponent<AfterImageTrailController>();
                trail.spawnShadows = true;
                trail.shadowTimeDelay = 0.05f;
                trail.shadowLifetime = 0.3f;
                trail.minTranslation = 0.05f;
                trail.maxEmission = 0f;
                trail.minEmission = 0f;
                trail.dashColor = new Color(0.61f, 0.71f, 0.31f, 1f);   // catnip green
            }
            if (user.PlayerHasActiveSynergy(PlutoSynergies.NipAndTuck)) PuffedUpItem.Trigger(user);

            float leaf = 0f;
            while (user != null && zoomiesRemaining > 0f)
            {
                float dt = BraveTime.DeltaTime;
                zoomiesRemaining -= dt; leaf -= dt;
                if (leaf <= 0f)
                {
                    leaf = LeafInterval;
                    PlutoVFX.Spawn(PlutoVFX.Catnip, user.CenterPosition + Random.insideUnitCircle * 0.4f);
                }
                yield return null;
            }
            EndZoomies();

            if (user != null && PlutoConfig.CatnapSeconds > 0f)
            {
                napMod = CatItemKit.Mod(PlayerStats.StatType.MovementSpeed, StatModifier.ModifyMethod.MULTIPLICATIVE, CatnapSpeed);
                user.ownerlessStatModifiers.Add(napMod);
                user.stats.RecalculateStats(user, false, false);
                yield return new WaitForSeconds(PlutoConfig.CatnapSeconds);
            }
            EndNap();
            running = null;
            buffed = null;
        }

        /// <summary>Idempotent: every modifier and the trail are released once, then the references are cleared.</summary>
        private void EndZoomies()
        {
            zooming = false;
            zoomiesRemaining = 0f;
            IsCurrentlyActive = false;
            if (trail != null) { trail.spawnShadows = false; Destroy(trail); }
            trail = null;
            CatTricks.ReleaseSpeed(buffed, speedMod);
            speedMod = null;
            if (buffed != null && fireMod != null && buffed.ownerlessStatModifiers.Remove(fireMod))
                buffed.stats.RecalculateStats(buffed, false, false);
            fireMod = null;
        }

        private void EndNap()
        {
            if (buffed != null && napMod != null && buffed.ownerlessStatModifiers.Remove(napMod))
                buffed.stats.RecalculateStats(buffed, false, false);
            napMod = null;
        }

        /// <summary>Losing the pouch mid-effect must not leave the buff (or the nap) on forever.</summary>
        private void StopAll()
        {
            if (running != null && buffed != null) buffed.StopCoroutine(running);
            running = null;
            EndZoomies();
            EndNap();
            buffed = null;
        }

        public override void OnPreDrop(PlayerController user)
        {
            StopAll();
            base.OnPreDrop(user);
        }

        public override void OnDestroy()
        {
            StopAll();
            base.OnDestroy();
        }
    }
}
