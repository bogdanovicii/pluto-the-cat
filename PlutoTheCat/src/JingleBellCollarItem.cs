using UnityEngine;
using Alexandria.ItemAPI;

namespace PlutoTheCat
{
    /// <summary>
    /// Jingle Bell Collar (2.17): a passive. A dodge roll rings the bell (at most once every BellCooldownSeconds): enemy
    /// bullets within BellRadius are erased like a small blank and non-boss enemies inside the ring are startled
    /// (stunned) for BellStunSeconds. With Squeaky Clean (Squeaky Toy) the ring is half as wide again.
    /// </summary>
    public class JingleBellCollarItem : PassiveItem
    {
        public const string ID = "pluto:jingle_bell_collar";
        private float lastJingle = float.NegativeInfinity;
        private PlayerController wearer;

        public static void Init()
        {
            string name = "Jingle Bell Collar";
            GameObject obj = new GameObject(name);
            JingleBellCollarItem item = obj.AddComponent<JingleBellCollarItem>();
            ItemBuilder.AddSpriteToObject(name, Plugin.ITEM_ROOT + "/jingle_bell_collar_icon", obj);
            ItemBuilder.SetupItem(item, "Belled",
                "Dodge rolling rings the bell, erasing nearby enemy bullets and startling the Gundead around you. " +
                "The bell needs a few seconds to settle between jingles.\n\n" +
                "Bought to warn the birds. Pluto learned to walk without making a sound within the week, and the birds " +
                "remain unwarned.\n\n" +
                "In the Gungeon he rings it on purpose. Bullets, it turns out, are far more nervous than birds.",
                "pluto");
            item.quality = PickupObject.ItemQuality.B;
        }

        public override void Pickup(PlayerController player)
        {
            base.Pickup(player);
            if (player == null) return;
            wearer = player;
            player.OnRollStarted += OnRollStarted;
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
            if (wearer != null) wearer.OnRollStarted -= OnRollStarted;
            wearer = null;
        }

        private void OnRollStarted(PlayerController player, Vector2 direction)
        {
            try
            {
                if (player == null || PlutoConfig.BellRadius <= 0f) return;
                if (!CatItemRules.BellReady(Time.time, lastJingle, PlutoConfig.BellCooldownSeconds)) return;
                lastJingle = Time.time;
                float radius = player.PlayerHasActiveSynergy(PlutoSynergies.SqueakyClean) ? PlutoConfig.BellRadius * 1.5f : PlutoConfig.BellRadius;
                Vector2 center = player.CenterPosition;
                SilencerInstance.DestroyBulletsInRange(center, radius, true, false, player, false, null, false, null);
                if (PlutoConfig.BellStunSeconds > 0f)
                {
                    foreach (AIActor enemy in CatItemKit.EnemiesNear(center, radius))
                        CatItemKit.Stun(enemy, PlutoConfig.BellStunSeconds);
                }
                PlutoVFX.Spawn(PlutoVFX.Jingle, center);
                AkSoundEngine.PostEvent("Play_OBJ_metronome_jingle_01", player.gameObject);
            }
            catch (System.Exception e) { Plugin.Log("jingle bell collar failed: " + e.Message); }
        }
    }
}
