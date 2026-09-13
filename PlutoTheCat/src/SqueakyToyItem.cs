using UnityEngine;
using Alexandria.ItemAPI;

namespace PlutoTheCat
{
    /// <summary>
    /// Squeaky Toy: press it and Coco Blue goes decoy for a few seconds. Enemies in the room
    /// turn on him, and he runs around dodging their fire (he cannot be hurt). Second starting active.
    /// </summary>
    public class SqueakyToyItem : PlayerItem
    {
        public const string ID = "pluto:squeaky_toy";

        public static void Init()
        {
            string name = "Squeaky Toy";
            GameObject obj = new GameObject(name);
            SqueakyToyItem item = obj.AddComponent<SqueakyToyItem>();
            ItemBuilder.AddSpriteToObject(name, Plugin.ITEM_ROOT + "/squeaker_icon", obj);
            ItemBuilder.SetupItem(item, "Go, Coco!",
                "Squeeze it and Coco Blue springs into action: every enemy in the room turns on him while he " +
                "zips around dodging their shots. He cannot be hurt, and he loves it.\n\n" +
                "The squeaker came out of a different toy. Nobody remembers which.",
                "pluto");
            ItemBuilder.SetCooldownType(item, ItemBuilder.CooldownType.Damage, PlutoConfig.DecoyCooldownDamage);
            item.consumable = false;
            item.quality = PickupObject.ItemQuality.EXCLUDED;
            item.CanBeDropped = false;
        }

        public override bool CanBeUsed(PlayerController user)
        {
            CocoBlueItem.CocoBlueController coco = CocoBlueItem.CocoBlueController.For(user);
            return coco != null && !coco.IsKnockedOut;
        }

        public override void DoEffect(PlayerController user)
        {
            CocoBlueItem.CocoBlueController coco = CocoBlueItem.CocoBlueController.For(user);
            if (coco == null) return;
            coco.StartDecoy(PlutoConfig.DecoySeconds);
            AkSoundEngine.PostEvent("Play_OBJ_item_throw_01", user.gameObject);
        }
    }
}
