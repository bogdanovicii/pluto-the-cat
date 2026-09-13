using System.Collections.Generic;
using UnityEngine;
using Alexandria.ItemAPI;

namespace PlutoTheCat
{
    /// <summary>
    /// Nine Lives: Pluto's starting passive. Cats get nine lives and Pluto has already spent six, so a
    /// run starts on his seventh (PlutoConfig.StartingLife). While he is not yet on his ninth, a hit
    /// that would kill him is cancelled: he stands back up with one full heart, gets a short
    /// invulnerability window and moves on to the next life. On the ninth life there is no next one.
    /// </summary>
    public class NineLivesItem : PassiveItem
    {
        public const string ID = "pluto:nine_lives";
        public const int LastLife = 9;
        public int CurrentLife;
        public int LivesLeft { get { return LastLife - CurrentLife; } }   // saves still available

        private static readonly string[] Ordinal = { "", "first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth" };

        public static void Init()
        {
            string name = "Nine Lives";
            GameObject obj = new GameObject(name);
            NineLivesItem item = obj.AddComponent<NineLivesItem>();
            ItemBuilder.AddSpriteToObject(name, Plugin.ITEM_ROOT + "/nine_lives_icon", obj);
            ItemBuilder.SetupItem(item, "Seventh Life",
                "Cats get nine lives. Pluto has been careless with his.\n\n" +
                "The first went to the balcony railing, the second to the washing machine (spin cycle), " +
                "the third to the neighbour's dog, the fourth to a whole rubber band, the fifth to the bathtub " +
                "(he does not talk about it), and the sixth to the Gungeon's elevator door, which he walked " +
                "into at speed.\n\n" +
                "He is on his seventh. When a hit would end it, he simply declines: the hit is cancelled, " +
                "he stands back up with one full heart, and the next life begins. Only the eighth and the " +
                "ninth are left, and the ninth is the last one. He knows it.",
                "pluto");
            item.quality = PickupObject.ItemQuality.EXCLUDED;
            item.CanBeDropped = false;
        }

        public override void Pickup(PlayerController player)
        {
            if (!m_pickedUpThisRun) CurrentLife = Mathf.Clamp(PlutoConfig.StartingLife, 1, LastLife);
            base.Pickup(player);
            player.healthHaver.ModifyDamage += OnModifyDamage;
        }

        // Keep the count across a mid-run save and continue.
        public override void MidGameSerialize(List<object> data)
        {
            base.MidGameSerialize(data);
            data.Add(CurrentLife);
        }

        public override void MidGameDeserialize(List<object> data)
        {
            base.MidGameDeserialize(data);
            if (data != null && data.Count > 0 && data[data.Count - 1] is int saved) CurrentLife = saved;
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
            if (CurrentLife >= LastLife || args.ModifiedDamage <= 0f) return;   // the ninth life is the last one
            PlayerController player = hh.gameActor as PlayerController;
            if (player == null) return;
            if (hh.Armor > 0f) return;                                  // armor absorbs this hit; not lethal
            if (CatTricks.CatTricksDoer.IsLandingOnFeet(player)) return;  // pit damage: cancelled by CatTricks, no life spent
            if (args.ModifiedDamage < hh.GetCurrentHealth()) return;    // survivable hit

            // Decline the hit: this life ends, the next one begins.
            args.ModifiedDamage = 0f;
            CurrentLife++;
            hh.ForceSetCurrentHealth(Mathf.Max(hh.GetCurrentHealth(), 1f));
            hh.TriggerInvulnerabilityPeriod(2.0f);
            AkSoundEngine.PostEvent("Play_OBJ_dice_bless_01", player.gameObject);
            player.ForceBlank(4f, 0.5f, false, true, null, false, -1f);   // small blank to clear nearby bullets
            PlutoVFX.Spawn(PlutoVFX.FurPuff, player.CenterPosition);
            PuffedUpItem.Trigger(player);   // guarded internally
            try
            {
                string life = Ordinal[Mathf.Clamp(CurrentLife, 1, LastLife)];
                GameUIRoot.Instance.notificationController.DoCustomNotification("Nine Lives",
                    CurrentLife >= LastLife ? "Ninth life. The last one." : char.ToUpper(life[0]) + life.Substring(1) + " life.",
                    sprite.Collection, sprite.spriteId, UINotificationController.NotificationColor.PURPLE, true, false);
            }
            catch (System.Exception e) { Plugin.Log("notification failed: " + e.Message); }
            Plugin.Log("Nine Lives: now on life " + CurrentLife + " of " + LastLife + ".");
        }
    }
}
