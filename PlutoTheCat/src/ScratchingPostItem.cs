using System.Collections.Generic;
using UnityEngine;
using Alexandria.ItemAPI;
using Dungeonator;

namespace PlutoTheCat
{
    /// <summary>
    /// Scratching Post (2.17): places a post at Pluto's feet (one per player; placing again moves it). While he stands
    /// within PostRadius his claws are sharpened: damage times PostDamageMultiplier and PostPierce extra piercing
    /// (vanilla AdditionalShotPiercing stat). The post disappears when he leaves the room, changes floor or loses the
    /// item. With Whetstone (Katana) the damage bonus grows by another 0.2.
    /// </summary>
    public class ScratchingPostItem : PlayerItem
    {
        public const string ID = "pluto:scratching_post";
        private static int postSpriteId = -1;

        public static void Init()
        {
            string name = "Scratching Post";
            GameObject obj = new GameObject(name);
            ScratchingPostItem item = obj.AddComponent<ScratchingPostItem>();
            ItemBuilder.AddSpriteToObject(name, Plugin.ITEM_ROOT + "/scratching_post_icon", obj);
            ItemBuilder.SetupItem(item, "Sharpen Up",
                "Places a scratching post in the room. Standing next to it sharpens your claws: more damage, and shots " +
                "pierce through an extra enemy.\n\n" +
                "Pluto owns a very expensive scratching post. For three years he preferred the sofa, the curtains and " +
                "the doorframe.\n\n" +
                "The Gungeon has no sofa. He has grudgingly admitted the post has a point. Several, in fact.",
                "pluto");
            ItemBuilder.SetCooldownType(item, ItemBuilder.CooldownType.PerRoom, 1f);
            item.consumable = false;
            item.quality = PickupObject.ItemQuality.C;
            postSpriteId = SpriteBuilder.AddSpriteToCollection(Plugin.ITEM_ROOT + "/scratching_post_placed.png", SpriteBuilder.itemCollection);
        }

        public override bool CanBeUsed(PlayerController user)
        {
            return user != null && user.CurrentRoom != null && base.CanBeUsed(user);
        }

        public override void DoEffect(PlayerController user)
        {
            if (user == null || postSpriteId < 0) return;
            Post.Remove(user);
            GameObject go = new GameObject("pluto_scratching_post");
            tk2dSprite sprite = go.AddComponent<tk2dSprite>();
            sprite.SetSprite(SpriteBuilder.itemCollection, postSpriteId);
            Vector2 feet = user.specRigidbody != null ? user.specRigidbody.UnitBottomCenter : user.CenterPosition;
            sprite.PlaceAtPositionByAnchor(feet.ToVector3ZUp(0f), tk2dBaseSprite.Anchor.LowerCenter);
            go.transform.position = go.transform.position.Quantize(1f / 16f);
            sprite.HeightOffGround = 0f;
            sprite.UpdateZDepth();
            Post post = go.AddComponent<Post>();
            post.Place(user);
            PlutoVFX.Spawn(PlutoVFX.FurPuff, feet);
            AkSoundEngine.PostEvent("Play_OBJ_item_throw_01", user.gameObject);
            Plugin.Log("scratching post: placed in " + (user.CurrentRoom != null ? user.CurrentRoom.GetRoomName() : "?"));
        }

        public override void OnPreDrop(PlayerController user)
        {
            Post.Remove(user);
            base.OnPreDrop(user);
        }

        public override void OnDestroy()
        {
            if (LastOwner != null) Post.Remove(LastOwner);
            base.OnDestroy();
        }

        /// <summary>The placed post: owns the sharpened modifiers and removes them when it goes.</summary>
        public class Post : MonoBehaviour
        {
            private static readonly Dictionary<PlayerController, Post> posts = new Dictionary<PlayerController, Post>();
            private PlayerController owner;
            private RoomHandler room;
            private Vector2 center;
            private StatModifier damageMod, pierceMod;
            private bool sharpened;

            public static void Remove(PlayerController player)
            {
                Post p;
                if (player != null && posts.TryGetValue(player, out p))
                {
                    posts.Remove(player);
                    if (p != null) Destroy(p.gameObject);
                }
            }

            public void Place(PlayerController player)
            {
                owner = player;
                room = player.CurrentRoom;
                tk2dBaseSprite sprite = GetComponent<tk2dBaseSprite>();
                center = sprite != null ? sprite.WorldCenter : (Vector2)transform.position;
                posts[player] = this;
            }

            private void Update()
            {
                if (owner == null || owner.healthHaver == null || owner.healthHaver.IsDead || owner.CurrentRoom != room)
                {
                    if (owner != null && posts.ContainsKey(owner) && posts[owner] == this) posts.Remove(owner);
                    Destroy(gameObject);
                    return;
                }
                bool now = CatItemRules.Sharpened(true, (owner.CenterPosition - center).sqrMagnitude, PlutoConfig.PostRadius);
                if (now != sharpened) SetSharpened(now);
            }

            private void SetSharpened(bool on)
            {
                sharpened = on;
                if (on)
                {
                    float mult = PlutoConfig.PostDamageMultiplier + (owner.PlayerHasActiveSynergy(PlutoSynergies.Whetstone) ? 0.2f : 0f);
                    damageMod = CatItemKit.Mod(PlayerStats.StatType.Damage, StatModifier.ModifyMethod.MULTIPLICATIVE, mult);
                    pierceMod = CatItemKit.Mod(PlayerStats.StatType.AdditionalShotPiercing, StatModifier.ModifyMethod.ADDITIVE, PlutoConfig.PostPierce);
                    owner.ownerlessStatModifiers.Add(damageMod);
                    owner.ownerlessStatModifiers.Add(pierceMod);
                    PlutoVFX.Spawn(PlutoVFX.AngerMarks, owner.CenterPosition + new Vector2(0f, 1.2f));
                    AkSoundEngine.PostEvent("Play_OBJ_dice_bless_01", owner.gameObject);
                }
                else ClearMods();
                owner.stats.RecalculateStats(owner, false, false);
            }

            private void ClearMods()
            {
                if (owner != null)
                {
                    if (damageMod != null) owner.ownerlessStatModifiers.Remove(damageMod);
                    if (pierceMod != null) owner.ownerlessStatModifiers.Remove(pierceMod);
                }
                damageMod = null; pierceMod = null;
            }

            private void OnDestroy()
            {
                bool had = damageMod != null || pierceMod != null;
                ClearMods();
                if (had && owner != null && owner.stats != null) owner.stats.RecalculateStats(owner, false, false);
                if (owner != null && posts.ContainsKey(owner) && posts[owner] == this) posts.Remove(owner);
            }
        }
    }
}
