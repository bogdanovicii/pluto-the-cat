using System.Collections.Generic;
using UnityEngine;
using Alexandria.ItemAPI;

namespace PlutoTheCat
{
    /// <summary>
    /// Nine Lives: Pluto's starting passive. A finite pool of lives per run. The first time a hit
    /// would kill him, the hit is cancelled, he is set to one full heart, gets a short
    /// invulnerability window and loses one life. Lives never refill during the run.
    /// </summary>
    public class NineLivesItem : PassiveItem
    {
        public const string ID = "pluto:nine_lives";
        public int LivesLeft;

        public static void Init()
        {
            string name = "Nine Lives";
            GameObject obj = new GameObject(name);
            NineLivesItem item = obj.AddComponent<NineLivesItem>();
            ItemBuilder.AddSpriteToObject(name, Plugin.ITEM_ROOT + "/nine_lives_icon", obj);
            ItemBuilder.SetupItem(item, "Not Today",
                "Cats get nine. Pluto is a cat. The first time a hit would finish him, he simply declines: " +
                "the hit is cancelled, he stands back up with one full heart, and one life is spent. " +
                "Lives do not come back this run.\n\n" +
                "Pluto has used at least four of his at home: the balcony railing, the washing machine, " +
                "the neighbour's dog, and the time he ate a whole rubber band.",
                "pluto");
            item.quality = PickupObject.ItemQuality.EXCLUDED;
            item.CanBeDropped = false;
        }

        public override void Pickup(PlayerController player)
        {
            if (!m_pickedUpThisRun) LivesLeft = PlutoConfig.NineLives;
            base.Pickup(player);
            player.healthHaver.ModifyDamage += OnModifyDamage;
        }

        // Keep the count across a mid-run save and continue.
        public override void MidGameSerialize(List<object> data)
        {
            base.MidGameSerialize(data);
            data.Add(LivesLeft);
        }

        public override void MidGameDeserialize(List<object> data)
        {
            base.MidGameDeserialize(data);
            if (data != null && data.Count > 0 && data[data.Count - 1] is int saved) LivesLeft = saved;
        }

        public override DebrisObject Drop(PlayerController player)
        {
            player.healthHaver.ModifyDamage -= OnModifyDamage;
            return base.Drop(player);
        }

        public override void OnDestroy()
        {
            if (Owner != null && Owner.healthHaver != null)
                Owner.healthHaver.ModifyDamage -= OnModifyDamage;
            base.OnDestroy();
        }

        private void OnModifyDamage(HealthHaver hh, HealthHaver.ModifyDamageEventArgs args)
        {
            if (LivesLeft <= 0 || args.ModifiedDamage <= 0f) return;
            PlayerController player = hh.gameActor as PlayerController;
            if (player == null) return;
            if (hh.Armor > 0f) return;                                  // armor absorbs this hit; not lethal
            if (args.ModifiedDamage < hh.GetCurrentHealth()) return;    // survivable hit

            // Decline the hit.
            args.ModifiedDamage = 0f;
            LivesLeft--;
            hh.ForceSetCurrentHealth(Mathf.Max(hh.GetCurrentHealth(), 1f));
            hh.TriggerInvulnerabilityPeriod(2.0f);
            AkSoundEngine.PostEvent("Play_OBJ_dice_bless_01", player.gameObject);
            player.ForceBlank(4f, 0.5f, false, true, null, false, -1f);   // small blank to clear nearby bullets
            PlutoVFX.Spawn(PlutoVFX.FurPuff, player.CenterPosition);
            PuffedUpItem.Trigger(player);   // guarded internally
            try
            {
                GameUIRoot.Instance.notificationController.DoCustomNotification("Nine Lives",
                    LivesLeft == 1 ? "Last one." : LivesLeft + " left",
                    sprite.Collection, sprite.spriteId, UINotificationController.NotificationColor.PURPLE, true, false);
            }
            catch (System.Exception e) { Plugin.Log("notification failed: " + e.Message); }
            Plugin.Log("Nine Lives: " + LivesLeft + " left this run.");
        }
    }
}
