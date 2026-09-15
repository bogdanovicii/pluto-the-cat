using UnityEngine;
using Gungeon;
using Alexandria.ItemAPI;

namespace PlutoTheCat
{
    /// <summary>
    /// Squeaky Toy: press it and Coco Blue goes decoy for a few seconds. Enemies in the room
    /// turn on him, and he runs around dodging their fire (he cannot be hurt).
    /// Pluto starts with it and can never drop it. It is also in the loot pool (B quality): any
    /// Gungeoneer who picks it up gets Coco Blue as a companion, and loses him again if they drop the toy.
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
                "A squeaky toy shaped like Coco Blue. Whoever carries it is followed by Coco himself: he blocks " +
                "bullets, drops kibble crumbs when you get hurt, and can be petted. Squeeze the toy and Coco " +
                "springs into action: every enemy in the room turns on him while he zips around dodging their " +
                "shots. He cannot be hurt, and he loves it.\n\n" +
                "It squeaks at a pitch only cats, dogs and the Gundead can hear, which is why every Bullet Kin in the " +
                "room drops what it is doing. Pluto would never part with it. Anyone else who finds one gets a friend " +
                "for as long as they keep it.",
                "pluto");
            ItemBuilder.SetCooldownType(item, ItemBuilder.CooldownType.Damage, PlutoConfig.DecoyCooldownDamage);
            item.consumable = false;
            item.quality = PickupObject.ItemQuality.B;            // in chests and shops for every character
            item.CanBeDropped = true;                             // Pluto's own copy is locked on pickup (below)
            item.AddToSubShop(ItemBuilder.ShopType.Trorc);
        }

        private static int CocoId
        {
            get { return Game.Items.ContainsID(CocoBlueItem.ID) ? Game.Items[CocoBlueItem.ID].PickupObjectId : -1; }
        }

        public override void Pickup(PlayerController player)
        {
            base.Pickup(player);
            if (player == null) return;
            CanBeDropped = !CatTricks.IsPluto(player);          // Pluto cannot drop Coco; others can
            int cocoId = CocoId;
            if (cocoId >= 0 && !player.HasPickupID(cocoId))
                LootEngine.GivePrefabToPlayer(PickupObjectDatabase.GetById(cocoId).gameObject, player);   // Coco appears
        }

        public override void OnPreDrop(PlayerController user)
        {
            // Dropping the toy sends Coco away with it (never happens for Pluto: he cannot drop it).
            int cocoId = CocoId;
            if (user != null && cocoId >= 0 && !CatTricks.IsPluto(user) && user.HasPickupID(cocoId))
                user.RemovePassiveItem(cocoId);
            base.OnPreDrop(user);
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
