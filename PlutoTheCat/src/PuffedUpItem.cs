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

        /// <summary>Per-player anger state: stat modifiers, timer, and the fur overlay that follows every frame.</summary>
        public class AngerDoer : MonoBehaviour
        {
            private PlayerController player;
            private float timeLeft, elapsed, shudderTimer, particleTimer;
            private bool angry;
            private GameObject furObj;
            private tk2dSprite fur;
            private StatModifier damageMod, fireMod;

            private void Start() { player = GetComponent<PlayerController>(); }

            public void GetAngry()
            {
                if (player == null) player = GetComponent<PlayerController>();
                if (player == null) return;
                timeLeft = PlutoConfig.AngrySeconds;
                if (angry) return;   // refresh only
                angry = true;
                elapsed = 0f; shudderTimer = 1.2f; particleTimer = 0.8f;

                damageMod = new StatModifier { statToBoost = PlayerStats.StatType.Damage, modifyType = StatModifier.ModifyMethod.MULTIPLICATIVE, amount = PlutoConfig.AngryDamageMultiplier, ignoredForSaveData = true };
                fireMod = new StatModifier { statToBoost = PlayerStats.StatType.RateOfFire, modifyType = StatModifier.ModifyMethod.MULTIPLICATIVE, amount = PlutoConfig.AngryFireRateMultiplier, ignoredForSaveData = true };
                player.ownerlessStatModifiers.Add(damageMod);
                player.ownerlessStatModifiers.Add(fireMod);
                player.stats.RecalculateStats(player, false, false);
                StartCoroutine(CatTricks.TimedSpeed(player, 1f, PlutoConfig.AngrySeconds));

                if (player.sprite != null && PlutoConfig.AngryScale != 1f)
                    player.sprite.scale = new Vector3(PlutoConfig.AngryScale, PlutoConfig.AngryScale, 1f);
                ShowFur(true);
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
                ShowFur(false);
            }

            private void ShowFur(bool on)
            {
                if (!on)
                {
                    if (furObj != null) Destroy(furObj);
                    furObj = null; fur = null;
                    return;
                }
                if (PlutoFur.Collection == null || PlutoFur.Count == 0 || player == null || player.sprite == null) return;
                furObj = new GameObject("pluto_fur");
                furObj.transform.parent = player.transform;
                fur = furObj.AddComponent<tk2dSprite>();
                int first = PlutoFur.Lookup("idle", 0, 0);
                if (first >= 0) fur.SetSprite(PlutoFur.Collection, first);
                fur.HeightOffGround = -0.6f;      // behind the body, like a hat set to "always behind"
                player.sprite.AttachRenderer(fur);
                fur.renderer.enabled = false;
            }

            /// <summary>Which of the four fur variants to show right now: bristle up, shiver, settle.</summary>
            private int Variant()
            {
                if (elapsed < 0.10f) return 0;
                if (elapsed < 0.20f) return 1;
                if (timeLeft < 0.15f) return 0;
                if (timeLeft < 0.30f) return 1;
                return ((int)(elapsed * 8f) % 2 == 0) ? 2 : 3;
            }

            private void LateUpdate()
            {
                if (!angry) return;
                float dt = BraveTime.DeltaTime;
                timeLeft -= dt; elapsed += dt; shudderTimer -= dt; particleTimer -= dt;
                if (timeLeft <= 0f || player == null || player.healthHaver == null || player.healthHaver.IsDead)
                {
                    CalmDown();
                    return;
                }
                if (particleTimer <= 0f)
                {
                    particleTimer = 1.5f;
                    PlutoVFX.Spawn(PlutoVFX.FurPuff, player.CenterPosition + Random.insideUnitCircle * 0.5f);
                }
                if (fur == null || player.sprite == null || player.spriteAnimator == null) return;

                tk2dSpriteAnimationClip clip = player.spriteAnimator.CurrentClip;
                // The samurai kimono covers the fur: no fur layer while the costume is worn (the layers follow the normal frames).
                int id = clip == null || player.IsUsingAlternateCostume ? -1 : PlutoFur.Lookup(clip.name, player.spriteAnimator.CurrentFrame, Variant());
                if (id < 0)
                {
                    fur.renderer.enabled = false;     // pits, deaths, ghosts, samurai costume: no fur layer
                    return;
                }
                fur.renderer.enabled = true;
                if (fur.spriteId != id || fur.Collection != PlutoFur.Collection) fur.SetSprite(PlutoFur.Collection, id);
                fur.FlipX = player.sprite.FlipX;

                // Align the fur canvas to the body frame (works for any anchor: match lower-left corners, then
                // account for the 4 px margin on whichever side is leading after a flip).
                tk2dSpriteDefinition bd = player.sprite.GetCurrentSpriteDef();
                tk2dSpriteDefinition fd = fur.GetCurrentSpriteDef();
                Vector3 bp = player.sprite.transform.position;
                float m = PlutoFur.MarginX / 16f;
                float x = fur.FlipX ? bp.x - bd.position0.x + fd.position0.x + m
                                    : bp.x + bd.position0.x - fd.position0.x - m;
                float y = bp.y + bd.position0.y - fd.position0.y;
                if (shudderTimer <= 0f)
                {
                    x += (((int)(elapsed * 30f)) % 2 == 0) ? 1f / 16f : -1f / 16f;
                    if (shudderTimer < -0.12f) shudderTimer = 1.0f + Random.value;
                }
                furObj.transform.position = new Vector3(x, y, bp.z);
                fur.UpdateZDepth();
            }

            private void OnDestroy()
            {
                if (angry) CalmDown();
            }
        }
    }
}
