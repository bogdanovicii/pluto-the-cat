using System.Linq;
using UnityEngine;
using Alexandria.ItemAPI;

namespace PlutoTheCat
{
    /// <summary>
    /// Cone of Shame (2.19): while ready, destroys the first hostile player-colliding projectile in a short arc
    /// in front of its wearer. A single overhead spark announces each cooldown-to-ready transition.
    /// </summary>
    public class ConeOfShameItem : PassiveItem
    {
        public const string ID = "pluto:cone_of_shame";
        private PlayerController wearer;
        private float lastBlock = float.NegativeInfinity;
        private bool wasReady = true;

        public static void Init()
        {
            string name = "Cone of Shame";
            GameObject obj = new GameObject(name);
            ConeOfShameItem item = obj.AddComponent<ConeOfShameItem>();
            ItemBuilder.AddSpriteToObject(name, Plugin.ITEM_ROOT + "/cone_of_shame_icon", obj);
            ItemBuilder.SetupItem(item, "Recovery Position",
                "Every few seconds, the cone catches the next enemy bullet in front of Pluto with a plastic thok. " +
                "A glint over his head means it is ready again.\n\n" +
                "A souvenir from the Vet's clinic. Pluto hated every second of it. Then a bullet bounced off it, " +
                "and he started to see its point. Bogdan and Bianca still keep the original in a cupboard.",
                "pluto");
            item.quality = PickupObject.ItemQuality.B;
        }

        public override void Pickup(PlayerController player)
        {
            base.Pickup(player);
            wearer = player;
            lastBlock = float.NegativeInfinity;
            wasReady = true; // already ready on pickup; no fake cooldown transition and therefore no pickup glint
        }

        public override void Update()
        {
            base.Update();
            if (wearer == null || wearer.healthHaver == null || wearer.healthHaver.IsDead) return;

            bool ready = CatSetRules.ConeReady(Time.time, lastBlock, PlutoConfig.ConeCooldown);
            if (!wasReady && ready)
            {
                PlutoVFX.Spawn(PlutoVFX.BlockSpark, wearer.CenterPosition + new Vector2(0f, 1.1f));
                AkSoundEngine.PostEvent("Play_OBJ_dice_bless_01", wearer.gameObject);
            }
            wasReady = ready;
            if (!ready) return;

            Vector2 center = wearer.CenterPosition;
            Vector2 aim = wearer.unadjustedAimPoint.XY() - center;
            if (aim.sqrMagnitude < 0.0001f) aim = Vector2.right;

            // DieInAir may synchronously remove a projectile from the global collection, so never scan it directly.
            Projectile[] projectiles = StaticReferenceManager.AllProjectiles != null
                ? StaticReferenceManager.AllProjectiles.ToArray()
                : new Projectile[0];
            for (int i = 0; i < projectiles.Length; i++)
            {
                Projectile projectile = projectiles[i];
                // collidesWithPlayer is the player-hostile semantic: allied/charmed AI shots do not qualify.
                if (!CatItemKit.IsEnemyBullet(projectile) || !projectile.collidesWithPlayer || projectile.HasDiedInAir)
                    continue;
                Vector2 position = projectile.specRigidbody != null
                    ? projectile.specRigidbody.UnitCenter
                    : (Vector2)projectile.transform.position;
                Vector2 delta = position - center;
                if (!CatSetRules.InCone(delta.x, delta.y, aim.x, aim.y,
                    PlutoConfig.ConeRadius, PlutoConfig.ConeArcDegrees))
                    continue;

                projectile.DieInAir(false, true, true, false);
                lastBlock = Time.time;
                wasReady = false;
                PlutoVFX.Spawn(PlutoVFX.BlockSpark, position);
                AkSoundEngine.PostEvent("Play_OBJ_item_throw_01", wearer.gameObject);
                Plugin.Log("cone of shame: thok");
                break;
            }
        }

        public override void DisableEffect(PlayerController player)
        {
            Unhook();
            base.DisableEffect(player);
        }

        public override DebrisObject Drop(PlayerController player)
        {
            Unhook();
            return base.Drop(player);
        }

        public override void OnDestroy()
        {
            Unhook();
            base.OnDestroy();
        }

        private void Unhook()
        {
            wearer = null;
            lastBlock = float.NegativeInfinity;
            wasReady = true;
        }
    }
}
