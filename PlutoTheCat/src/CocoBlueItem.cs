using System.Collections;
using UnityEngine;
using Alexandria.ItemAPI;

namespace PlutoTheCat
{
    /// <summary>
    /// Coco Blue: Pluto's plush-cat companion (starting passive). Follows him around; every time Pluto
    /// takes a hit, Coco squeaks and drops a kibble crumb (ammo for the other gun). Cannot be hurt.
    /// Built with Alexandria's CompanionBuilder (the same path Once More Into The Breach uses).
    /// </summary>
    public class CocoBlueItem : CompanionItem
    {
        public const string ID = "pluto:coco_blue";
        public const string GUID = "bogdan.pluto.cocoblue";
        private static GameObject prefab;

        public static void Init()
        {
            string name = "Coco Blue";
            GameObject obj = new GameObject(name);
            CocoBlueItem item = obj.AddComponent<CocoBlueItem>();
            ItemBuilder.AddSpriteToObject(name, Plugin.ITEM_ROOT + "/coco_blue_icon", obj);
            ItemBuilder.SetupItem(item, "Squeaks Back",
                "Pluto's plush. Coco Blue follows him everywhere and, whenever Pluto gets hurt, squeaks and " +
                "drops a kibble crumb to top up whatever else he is carrying. Pet him (interact next to him) " +
                "for a happy wiggle and a burst of zoomies.\n\n" +
                "Coco has been chewed, carried up the stairs by the ear, and left in the water bowl twice. " +
                "Still smiling.",
                "pluto");
            item.quality = PickupObject.ItemQuality.EXCLUDED;
            item.CanBeDropped = false;
            item.CompanionGuid = GUID;
            item.Synergies = new CompanionTransformSynergy[0];   // must not be null
            BuildPrefab();
        }

        private static void BuildPrefab()
        {
            if (prefab != null || CompanionBuilder.companionDictionary.ContainsKey(GUID)) return;
            prefab = CompanionBuilder.BuildPrefab("Coco Blue", GUID, Plugin.COMPANION_ROOT + "/idle/coco_idle_001",
                new IntVector2(2, 1), new IntVector2(12, 8));
            CocoBlueController controller = prefab.AddComponent<CocoBlueController>();
            controller.CanBePet = true;                       // interact next to Coco to pet him (the Dog's mechanic)
            prefab.GetComponent<AIActor>().MovementSpeed = 6.5f;

            prefab.AddAnimation("idle", Plugin.COMPANION_ROOT + "/idle", 4, CompanionBuilder.AnimationType.Idle,
                DirectionalAnimation.DirectionType.Single).wrapMode = tk2dSpriteAnimationClip.WrapMode.Loop;
            prefab.AddAnimation("move", Plugin.COMPANION_ROOT + "/move", 9, CompanionBuilder.AnimationType.Move,
                DirectionalAnimation.DirectionType.Single).wrapMode = tk2dSpriteAnimationClip.WrapMode.Loop;
            prefab.AddAnimation("pet", Plugin.COMPANION_ROOT + "/pet", 6, CompanionBuilder.AnimationType.Idle,
                DirectionalAnimation.DirectionType.Single).wrapMode = tk2dSpriteAnimationClip.WrapMode.Loop;

            BehaviorSpeculator bs = prefab.GetComponent<BehaviorSpeculator>();
            bs.MovementBehaviors.Add(new CompanionFollowPlayerBehavior
            {
                PathInterval = 0.25f,
                DisableInCombat = false,
                IdealRadius = 2.5f,
                CatchUpRadius = 6f,
                CatchUpAccelTime = 2f,
                CatchUpSpeed = 6f,
                CatchUpMaxSpeed = 10f,
                CatchUpAnimation = "",
                CatchUpOutAnimation = "",
                IdleAnimations = new[] { "idle" },
                CanRollOverPits = false,
                RollAnimation = "",
            });
        }

        /// <summary>Lives on the spawned companion; watches its owner for hits and rewards petting.</summary>
        public class CocoBlueController : CompanionController
        {
            private PlayerController watched;
            private float cooldown;
            private bool wasBeingPet;

            public override void Update()
            {
                base.Update();
                cooldown -= BraveTime.DeltaTime;
                if (watched == null && m_owner != null)
                {
                    watched = m_owner;
                    watched.healthHaver.OnDamaged += OnOwnerDamaged;
                }
                // Petting: hearts over Coco and a short burst of speed for whoever is petting him.
                bool petting = IsBeingPet;
                if (petting && !wasBeingPet)
                {
                    PlutoVFX.Spawn(PlutoVFX.LoveBurst, (Vector2)transform.position + new Vector2(0.5f, 0.8f));
                    AkSoundEngine.PostEvent("Play_OBJ_item_throw_01", gameObject);
                    PlayerController petter = m_pettingDoer != null ? m_pettingDoer : m_owner;
                    if (petter != null) StartCoroutine(CatTricks.TimedSpeed(petter, 2f, 3f));
                }
                wasBeingPet = petting;
            }

            public override void OnDestroy()
            {
                if (watched != null && watched.healthHaver != null) watched.healthHaver.OnDamaged -= OnOwnerDamaged;
                base.OnDestroy();
            }

            private void OnOwnerDamaged(float resultValue, float maxValue, CoreDamageTypes damageTypes, DamageCategory damageCategory, Vector2 damageDirection)
            {
                if (cooldown > 0f || watched == null) return;
                cooldown = 1.5f;
                KibbleSackGun.SpawnCrumb(transform.position);
                AkSoundEngine.PostEvent("Play_OBJ_item_throw_01", gameObject);
            }
        }
    }
}
