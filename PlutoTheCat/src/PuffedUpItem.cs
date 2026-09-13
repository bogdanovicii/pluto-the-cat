using System.Collections;
using UnityEngine;
using Alexandria.ItemAPI;

namespace PlutoTheCat
{
    /// <summary>
    /// Puffed Up: Pluto's anger passive. Every hit (including one Nine Lives cancels) makes him bristle
    /// for a few seconds: the body sprite scales up, a ring of standing fur is drawn behind him, anger
    /// marks pop over his head, and he hits harder, fires faster and moves faster until he calms down.
    /// </summary>
    public class PuffedUpItem : PassiveItem
    {
        public const string ID = "pluto:puffed_up";
        public static int HaloSpriteA = -1, HaloSpriteB = -1;

        public static void Init()
        {
            string name = "Puffed Up";
            GameObject obj = new GameObject(name);
            PuffedUpItem item = obj.AddComponent<PuffedUpItem>();
            ItemBuilder.AddSpriteToObject(name, Plugin.ITEM_ROOT + "/puffed_up_icon", obj);
            ItemBuilder.SetupItem(item, "Do Not Touch",
                "Hit Pluto and he puffs up: fur on end, twice the cat, and furious. While angry he hits harder, " +
                "fires faster and moves faster. It wears off once he has decided you have learned your lesson.\n\n" +
                "The vacuum cleaner has seen this face. So has the neighbour's dog.",
                "pluto");
            item.quality = PickupObject.ItemQuality.EXCLUDED;
            item.CanBeDropped = false;

            HaloSpriteA = SpriteBuilder.AddSpriteToCollection(Plugin.ITEM_ROOT + "/fur_halo_001.png", SpriteBuilder.itemCollection);
            HaloSpriteB = SpriteBuilder.AddSpriteToCollection(Plugin.ITEM_ROOT + "/fur_halo_002.png", SpriteBuilder.itemCollection);
        }

        public override void Pickup(PlayerController player)
        {
            base.Pickup(player);
            if (player.gameObject.GetComponent<AngerDoer>() == null) player.gameObject.AddComponent<AngerDoer>();
            player.healthHaver.OnDamaged += OnDamaged;
        }

        public override DebrisObject Drop(PlayerController player)
        {
            player.healthHaver.OnDamaged -= OnDamaged;
            return base.Drop(player);
        }

        public override void OnDestroy()
        {
            if (Owner != null && Owner.healthHaver != null) Owner.healthHaver.OnDamaged -= OnDamaged;
            base.OnDestroy();
        }

        private void OnDamaged(float resultValue, float maxValue, CoreDamageTypes damageTypes, DamageCategory damageCategory, Vector2 damageDirection)
        {
            if (Owner != null) Trigger(Owner);
        }

        /// <summary>Called on a real hit, and by Nine Lives when it cancels a lethal one.</summary>
        public static void Trigger(PlayerController player)
        {
            try
            {
                if (player == null || PlutoConfig.AngrySeconds <= 0f) return;
                if (!Gungeon.Game.Items.ContainsID(ID)) return;                       // item failed to load: nothing to do
                if (!player.HasPickupID(Gungeon.Game.Items[ID].PickupObjectId)) return;
                AngerDoer doer = player.gameObject.GetComponent<AngerDoer>() ?? player.gameObject.AddComponent<AngerDoer>();
                doer.GetAngry();
            }
            catch (System.Exception e) { Plugin.Log("Puffed Up trigger failed: " + e.Message); }
        }

        /// <summary>Per-player anger state: scale, fur halo, stat modifiers, timer.</summary>
        public class AngerDoer : MonoBehaviour
        {
            private PlayerController player;
            private float timeLeft;
            private bool angry;
            private GameObject halo;
            private tk2dSprite haloSprite;
            private float flicker;
            private StatModifier damageMod, fireMod;

            private void Start() { player = GetComponent<PlayerController>(); }

            public void GetAngry()
            {
                if (player == null) player = GetComponent<PlayerController>();
                if (player == null) return;
                timeLeft = PlutoConfig.AngrySeconds;
                if (angry) return;   // refresh only
                angry = true;

                damageMod = new StatModifier { statToBoost = PlayerStats.StatType.Damage, modifyType = StatModifier.ModifyMethod.MULTIPLICATIVE, amount = PlutoConfig.AngryDamageMultiplier, ignoredForSaveData = true };
                fireMod = new StatModifier { statToBoost = PlayerStats.StatType.RateOfFire, modifyType = StatModifier.ModifyMethod.MULTIPLICATIVE, amount = PlutoConfig.AngryFireRateMultiplier, ignoredForSaveData = true };
                player.ownerlessStatModifiers.Add(damageMod);
                player.ownerlessStatModifiers.Add(fireMod);
                player.stats.RecalculateStats(player, false, false);
                StartCoroutine(CatTricks.TimedSpeed(player, 1f, PlutoConfig.AngrySeconds));

                if (player.sprite != null) player.sprite.scale = new Vector3(PlutoConfig.AngryScale, PlutoConfig.AngryScale, 1f);
                ShowHalo(true);
                PlutoVFX.Spawn(PlutoVFX.AngerMarks, player.CenterPosition + new Vector2(0f, 1.2f));
                PlutoVFX.Spawn(PlutoVFX.FurPuff, player.CenterPosition);
                AkSoundEngine.PostEvent("Play_OBJ_dice_bless_01", player.gameObject);
            }

            private void CalmDown()
            {
                angry = false;
                if (player != null)
                {
                    player.ownerlessStatModifiers.Remove(damageMod);
                    player.ownerlessStatModifiers.Remove(fireMod);
                    player.stats.RecalculateStats(player, false, false);
                    if (player.sprite != null) player.sprite.scale = Vector3.one;
                }
                ShowHalo(false);
            }

            private void ShowHalo(bool on)
            {
                if (!on)
                {
                    if (halo != null) Destroy(halo);
                    halo = null; haloSprite = null;
                    return;
                }
                if (HaloSpriteA < 0 || player == null || player.sprite == null) return;
                halo = new GameObject("pluto_fur_halo");
                halo.transform.parent = player.transform;
                haloSprite = halo.AddComponent<tk2dSprite>();
                haloSprite.SetSprite(SpriteBuilder.itemCollection, HaloSpriteA);
                haloSprite.HeightOffGround = -0.6f;              // behind the body, like a hat set to "always behind"
                player.sprite.AttachRenderer(haloSprite);
                PositionHalo();
            }

            private void PositionHalo()
            {
                if (halo == null || player == null || player.sprite == null) return;
                Vector2 c = player.sprite.WorldCenter;
                halo.transform.position = new Vector3(c.x - 1.125f, c.y - 1.125f, halo.transform.position.z);   // 36 px halo centred on the body
                haloSprite.UpdateZDepth();
            }

            private void Update()
            {
                if (!angry) return;
                timeLeft -= BraveTime.DeltaTime;
                if (timeLeft <= 0f || player == null || player.healthHaver == null || player.healthHaver.IsDead)
                {
                    CalmDown();
                    return;
                }
                flicker += BraveTime.DeltaTime;
                if (haloSprite != null)
                {
                    haloSprite.SetSprite(SpriteBuilder.itemCollection, ((int)(flicker * 8f) % 2 == 0) ? HaloSpriteA : HaloSpriteB);
                    PositionHalo();
                }
            }

            private void OnDestroy()
            {
                if (angry) CalmDown();
            }
        }
    }
}
