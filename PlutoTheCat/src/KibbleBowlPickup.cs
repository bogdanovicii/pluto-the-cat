using UnityEngine;
using Alexandria.ItemAPI;

namespace PlutoTheCat
{
    /// <summary>
    /// A bowl of kibble that heals half a heart when walked over. Dropped sometimes by enemies that
    /// die while in love with Pluto. Same pickup mechanics as the kibble crumbs.
    /// </summary>
    public class KibbleBowlPickup : MonoBehaviour
    {
        public const float DropChance = 0.2f;
        public const float HealAmount = 0.5f;
        private static int spriteA = -1, spriteB = -1;
        private float life = 25f;
        private float bob;
        private tk2dSprite sprite;

        public static void Init()
        {
            spriteA = SpriteBuilder.AddSpriteToCollection(Plugin.ITEM_ROOT + "/kibble_bowl_001.png", SpriteBuilder.itemCollection);
            spriteB = SpriteBuilder.AddSpriteToCollection(Plugin.ITEM_ROOT + "/kibble_bowl_002.png", SpriteBuilder.itemCollection);
        }

        public static void MaybeSpawn(Vector2 position)
        {
            if (spriteA < 0 || Random.value > DropChance) return;
            GameObject bowl = new GameObject("pluto_kibble_bowl");
            bowl.transform.position = position;
            tk2dSprite s = bowl.AddComponent<tk2dSprite>();
            s.SetSprite(SpriteBuilder.itemCollection, spriteA);
            bowl.AddComponent<KibbleBowlPickup>();
        }

        private void Start()
        {
            sprite = GetComponent<tk2dSprite>();
        }

        private void Update()
        {
            life -= BraveTime.DeltaTime;
            if (life <= 0f) { Destroy(gameObject); return; }
            bob += BraveTime.DeltaTime;
            if (sprite != null && spriteB >= 0) sprite.SetSprite(SpriteBuilder.itemCollection, ((int)(bob * 2f) % 2 == 0) ? spriteA : spriteB);

            for (int i = 0; i < GameManager.Instance.AllPlayers.Length; i++)
            {
                PlayerController player = GameManager.Instance.AllPlayers[i];
                if (player == null || player.healthHaver == null || player.healthHaver.IsDead) continue;
                if (Vector2.Distance(player.CenterPosition, transform.position) > 0.8f) continue;
                if (player.healthHaver.GetCurrentHealth() >= player.healthHaver.GetMaxHealth()) continue;   // leave it for later
                player.healthHaver.ApplyHealing(HealAmount);
                AkSoundEngine.PostEvent("Play_OBJ_item_throw_01", player.gameObject);
                Destroy(gameObject);
                return;
            }
        }
    }

    /// <summary>Marks an enemy whose death is already wired to drop a bowl.</summary>
    public class CharmedDropMarker : MonoBehaviour { }
}
