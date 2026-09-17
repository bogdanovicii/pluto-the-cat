using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Alexandria.ItemAPI;
using Dungeonator;
using Gungeon;

namespace PlutoTheCat
{
    /// <summary>
    /// Yasupen (2.18.0): Donpen's twin brother, a loot-pool companion.
    /// - Follows the owner; in combat, belly-slides at the nearest enemy (YasupenSlideCooldown / Range / Damage / Knockback).
    /// - Shops are YasupenShopDiscount cheaper while he is with you (GlobalPriceMultiplier passive stat).
    /// - After a room is cleared, a YasupenBargainChance "miracle bargain": he cheers and 3-5 casings drop.
    /// - Pettable; petting him wiggles Coco and the other way round.
    /// Clips are DirectionType.Single (swap Prefix, never only AnimNames).
    /// </summary>
    public class YasupenItem : CompanionItem
    {
        public const string ID = "pluto:yasupen";
        public const string GUID = "bogdan.pluto.yasupen";
        // ItemBuilder.SetupItem (Alexandria) derives the registered item id from the GameObject's own name
        // (lowercased, spaces to underscores, apostrophes kept as-is), not from the ID constant above. The
        // display name below is "Yasupen's Price Tag", so the item actually registers as this id - never
        // "pluto:yasupen" - unless we rename it back right after SetupItem, same as HairballItem does.
        private const string SetupId = "pluto:yasupen's_price_tag";
        private const string ROOT = "PlutoTheCat/Resources/Companions/yasupen";
        private static GameObject prefab;

        public static void Init()
        {
            string name = "Yasupen's Price Tag";
            GameObject obj = new GameObject(name);
            YasupenItem item = obj.AddComponent<YasupenItem>();
            ItemBuilder.AddSpriteToObject(name, Plugin.ITEM_ROOT + "/yasupen_icon", obj);
            ItemBuilder.SetupItem(item, "Donpen's Twin Brother",
                "Yasupen follows you, belly-slides into enemies, and makes every shop a little cheaper. Now and then, after " +
                "a fight, he finds a miracle bargain lying on the floor.\n\n" +
                "Donpen got the store, the fame and the nightcap first. Yasupen got a price-tag sticker and a lifelong " +
                "grudge. He follows Pluto because a cat who knocks things off shelves is the best bargain hunter he has ever met.",
                "pluto");
            if (Game.Items.ContainsID(SetupId) && !Game.Items.ContainsID(ID))
            {
                Game.Items.Rename(SetupId, ID);
                Plugin.Log("yasupen: renamed " + SetupId + " to " + ID);
            }
            else if (!Game.Items.ContainsID(ID))
            {
                Plugin.Log("yasupen: expected setup id " + SetupId + " not found and " + ID +
                    " is not registered either; give pluto:yasupen and Penguin Pals will not work");
            }
            item.quality = PickupObject.ItemQuality.B;
            item.CompanionGuid = GUID;
            item.Synergies = new CompanionTransformSynergy[0];   // must not be null
            ItemBuilder.AddPassiveStatModifier(item, PlayerStats.StatType.GlobalPriceMultiplier,
                YasupenRules.PriceMultiplier(PlutoConfig.YasupenShopDiscount), StatModifier.ModifyMethod.MULTIPLICATIVE);
            BuildPrefab();
        }

        private PlayerController wearer;

        public override void Pickup(PlayerController player)
        {
            base.Pickup(player);
            wearer = player;
            if (player != null) player.OnRoomClearEvent += OnRoomClear;
        }

        public override void DisableEffect(PlayerController player)   // PassiveItem declares it public virtual (not protected)
        {
            Unhook();
            base.DisableEffect(player);
        }

        // PassiveItem.Drop and PassiveItem.OnDestroy are both public virtual (verified with ikdasm against
        // Assembly-CSharp.dll), same as JingleBellCollarItem's Unhook pattern.
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
            if (wearer != null) wearer.OnRoomClearEvent -= OnRoomClear;
            wearer = null;
        }

        private void OnRoomClear(PlayerController player)
        {
            int casings = YasupenRules.BargainCasings(Random.value, PlutoConfig.YasupenBargainChance, Random.value);
            if (casings <= 0) return;
            YasupenController pen = YasupenController.For(player);
            Vector2 at = pen != null && pen.specRigidbody != null ? pen.specRigidbody.UnitCenter : player.CenterPosition;
            if (pen != null) pen.Cheer();
            LootEngine.SpawnCurrency(at, casings);
            Plugin.Log("yasupen: miracle bargain, " + casings + " casings");
        }

        private static void BuildPrefab()
        {
            if (prefab != null || CompanionBuilder.companionDictionary.ContainsKey(GUID)) return;
            prefab = CompanionBuilder.BuildPrefab("Yasupen", GUID, ROOT + "/idle/yasupen_idle_001",
                new IntVector2(4, 2), new IntVector2(14, 10));   // frames carry a 1-px margin for the runtime outline
            YasupenController controller = prefab.AddComponent<YasupenController>();
            controller.CanBePet = true;
            prefab.GetComponent<AIActor>().MovementSpeed = 6.5f;

            prefab.AddAnimation("idle", ROOT + "/idle", 4, CompanionBuilder.AnimationType.Idle,
                DirectionalAnimation.DirectionType.Single).wrapMode = tk2dSpriteAnimationClip.WrapMode.Loop;
            prefab.AddAnimation("move", ROOT + "/move", 8, CompanionBuilder.AnimationType.Move,
                DirectionalAnimation.DirectionType.Single).wrapMode = tk2dSpriteAnimationClip.WrapMode.Loop;
            prefab.AddAnimation("slide", ROOT + "/slide", 10, CompanionBuilder.AnimationType.Other,
                DirectionalAnimation.DirectionType.Single).wrapMode = tk2dSpriteAnimationClip.WrapMode.Loop;
            prefab.AddAnimation("pet", ROOT + "/pet", 6, CompanionBuilder.AnimationType.Other,
                DirectionalAnimation.DirectionType.Single).wrapMode = tk2dSpriteAnimationClip.WrapMode.Loop;
            prefab.AddAnimation("cheer", ROOT + "/cheer", 6, CompanionBuilder.AnimationType.Other,
                DirectionalAnimation.DirectionType.Single).wrapMode = tk2dSpriteAnimationClip.WrapMode.Loop;

            BehaviorSpeculator bs = prefab.GetComponent<BehaviorSpeculator>();
            bs.MovementBehaviors.Add(new CompanionFollowPlayerBehavior
            {
                PathInterval = 0.25f,
                DisableInCombat = false,
                IdealRadius = 3f,
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

        /// <summary>Lives on the spawned companion: belly slides, the bargain cheer and the pet link with Coco.</summary>
        public class YasupenController : CompanionController
        {
            public static readonly List<YasupenController> Instances = new List<YasupenController>();
            private const float SlideSpeed = 14f, MaxSlideSeconds = 0.6f, BodyRadius = 0.6f;

            private float lastSlide = float.NegativeInfinity;
            private bool sliding, wasPet;
            private float lookTimer;
            private Coroutine slideCoroutine;

            public PlayerController OwnerPlayer { get { return m_owner; } }

            public static YasupenController For(PlayerController owner)
            {
                for (int i = 0; i < Instances.Count; i++)
                    if (Instances[i] != null && Instances[i].m_owner == owner) return Instances[i];
                return null;
            }

            private void OnEnable() { if (!Instances.Contains(this)) Instances.Add(this); }
            private void OnDisable() { StopSlide(); Instances.Remove(this); }

            public override void OnDestroy()
            {
                StopSlide();
                Instances.Remove(this);
                base.OnDestroy();
            }

            public override void Update()
            {
                base.Update();
                if (m_owner == null || aiActor == null) return;
                UpdatePets();
                lookTimer -= BraveTime.DeltaTime;
                if (sliding || IsBeingPet || lookTimer > 0f) return;
                lookTimer = 0.2f;
                AIActor target = PenguinPalsTarget(out float distance);
                if (target == null || distance > PlutoConfig.YasupenSlideRange) target = NearestEnemy(out distance);
                if (YasupenRules.SlideReady(Time.time, lastSlide, PlutoConfig.YasupenSlideCooldown, m_owner.IsInCombat,
                    target != null ? distance : float.NaN, PlutoConfig.YasupenSlideRange))
                    SlideAt(target);
            }

            public void SlideAt(AIActor target)
            {
                if (sliding || target == null || aiActor == null || specRigidbody == null) return;
                slideCoroutine = StartCoroutine(Slide(target));
            }

            public void Cheer()
            {
                if (aiAnimator != null && !sliding && !IsBeingPet) aiAnimator.PlayForDuration("cheer", 1.2f);
                PlutoVFX.Spawn(PlutoVFX.LoveBurst, (Vector2)transform.position + new Vector2(0.5f, 1.4f));
            }

            private IEnumerator Slide(AIActor target)
            {
                sliding = true;
                lastSlide = Time.time;
                Vector2 from = specRigidbody.UnitCenter;
                Vector2 to = (Vector2)target.CenterPosition;
                Vector2 dir = (to - from).normalized;
                if (dir.sqrMagnitude < 0.01f) dir = Vector2.right;
                // Travel a bit past the target instead of a fixed duration, so the slide reaches enemies near
                // the edge of YasupenSlideRange instead of stopping short of them.
                float duration = Mathf.Min(MaxSlideSeconds, (Vector2.Distance(from, to) + 1.5f) / SlideSpeed);
                aiActor.BehaviorOverridesVelocity = true;
                aiActor.BehaviorVelocity = dir * SlideSpeed;
                if (aiAnimator != null) aiAnimator.PlayForDuration("slide", duration + 0.1f);
                HashSet<AIActor> hit = new HashSet<AIActor>();
                float t = 0f;
                while (t < duration && aiActor != null)
                {
                    HitAlongSlide(dir, hit);
                    t += BraveTime.DeltaTime;
                    yield return null;
                }
                StopSlide();
            }

            // Hit on body overlap (Yasupen's centre against the enemy's own hitbox), not centre-to-centre distance,
            // so bosses and other large enemies actually get hit by the slide.
            private void HitAlongSlide(Vector2 dir, HashSet<AIActor> hit)
            {
                RoomHandler room = m_owner != null ? m_owner.CurrentRoom : null;
                List<AIActor> enemies = room != null ? room.GetActiveEnemies(RoomHandler.ActiveEnemyType.All) : null;
                if (enemies == null || specRigidbody == null) return;
                Vector2 me = specRigidbody.UnitCenter;
                for (int i = 0; i < enemies.Count; i++)
                {
                    AIActor e = enemies[i];
                    if (e == null || e == aiActor || e.CompanionOwner != null || hit.Contains(e) || e.healthHaver == null || e.healthHaver.IsDead) continue;
                    if (e.specRigidbody == null || e.specRigidbody.HitboxPixelCollider == null) continue;
                    PixelCollider box = e.specRigidbody.HitboxPixelCollider;
                    if (DistanceToBox(me, box.UnitBottomLeft, box.UnitTopRight) > BodyRadius) continue;
                    hit.Add(e);
                    e.healthHaver.ApplyDamage(PlutoConfig.YasupenSlideDamage, dir, "Yasupen", CoreDamageTypes.None, DamageCategory.Normal);
                    if (!e.healthHaver.IsBoss && e.knockbackDoer != null) e.knockbackDoer.ApplyKnockback(dir, PlutoConfig.YasupenSlideKnockback);
                }
            }

            /// <summary>Distance from a point to the closest point of an axis-aligned box (0 when the point is inside it).</summary>
            private static float DistanceToBox(Vector2 point, Vector2 bottomLeft, Vector2 topRight)
            {
                float dx = Mathf.Max(0f, Mathf.Max(bottomLeft.x - point.x, point.x - topRight.x));
                float dy = Mathf.Max(0f, Mathf.Max(bottomLeft.y - point.y, point.y - topRight.y));
                return Mathf.Sqrt(dx * dx + dy * dy);
            }

            private void StopSlide()
            {
                if (!sliding) return;
                sliding = false;
                if (slideCoroutine != null) { StopCoroutine(slideCoroutine); slideCoroutine = null; }
                if (aiActor != null)
                {
                    aiActor.BehaviorOverridesVelocity = false;
                    aiActor.BehaviorVelocity = Vector2.zero;
                }
            }

            private AIActor NearestEnemy(out float distance)
            {
                distance = float.MaxValue;
                RoomHandler room = m_owner.CurrentRoom;
                List<AIActor> enemies = room != null ? room.GetActiveEnemies(RoomHandler.ActiveEnemyType.All) : null;
                if (enemies == null || specRigidbody == null) return null;
                AIActor best = null;
                Vector2 me = specRigidbody.UnitCenter;
                for (int i = 0; i < enemies.Count; i++)
                {
                    AIActor e = enemies[i];
                    if (e == null || e.CompanionOwner != null || e.healthHaver == null || e.healthHaver.IsDead) continue;
                    float d = Vector2.Distance(me, e.CenterPosition);
                    if (d < distance) { distance = d; best = e; }
                }
                return best;
            }

            /// <summary>Penguin Pals: while Coco is a decoy, the nearest enemy targeting Coco.</summary>
            private AIActor PenguinPalsTarget(out float distance)
            {
                distance = float.MaxValue;
                if (!m_owner.PlayerHasActiveSynergy(PlutoSynergies.PenguinPals)) return null;
                CocoBlueItem.CocoBlueController coco = CocoBlueItem.CocoBlueController.For(m_owner);
                RoomHandler room = m_owner.CurrentRoom;
                if (coco == null || !coco.IsDecoy || coco.specRigidbody == null || room == null || specRigidbody == null) return null;
                List<AIActor> enemies = room.GetActiveEnemies(RoomHandler.ActiveEnemyType.All);
                if (enemies == null) return null;
                AIActor best = null;
                Vector2 me = specRigidbody.UnitCenter;
                for (int i = 0; i < enemies.Count; i++)
                {
                    AIActor e = enemies[i];
                    if (e == null || e.OverrideTarget != coco.specRigidbody || e.healthHaver == null || e.healthHaver.IsDead) continue;
                    float d = Vector2.Distance(me, e.CenterPosition);
                    if (d < distance) { distance = d; best = e; }
                }
                return best;
            }

            /// <summary>Petting Yasupen wiggles Coco; petting Coco wiggles Yasupen.</summary>
            private void UpdatePets()
            {
                bool pet = IsBeingPet;
                CocoBlueItem.CocoBlueController coco = CocoBlueItem.CocoBlueController.For(m_owner);
                if (pet && !wasPet && coco != null && !coco.IsKnockedOut && coco.aiAnimator != null)
                    coco.aiAnimator.PlayForDuration("pet", 1.5f);
                if (coco != null && coco.IsBeingPet && !pet && aiAnimator != null && !sliding && !aiAnimator.IsPlaying("pet"))
                    aiAnimator.PlayForDuration("pet", 1.5f);
                wasPet = pet;
            }
        }
    }
}
