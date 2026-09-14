using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Alexandria.ItemAPI;
using Dungeonator;

namespace PlutoTheCat
{
    /// <summary>
    /// Coco Blue: Pluto's plush-cat companion (starting passive).
    /// - Follows him around; whenever Pluto takes a hit, Coco squeaks and drops a kibble crumb.
    /// - Can be petted (interact next to him): wiggle, hearts, a burst of speed.
    /// - Blocks enemy bullets that touch him, with a squish animation and a spark (he cannot be hurt).
    /// - Decoy mode (Squeaky Toy active): enemies in the room target him and he runs around dodging.
    /// Built with Alexandria's CompanionBuilder.
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
                "drops a kibble crumb to top up whatever else he is carrying. Bullets that hit Coco just stop. " +
                "Pet him (interact next to him) for a happy wiggle and a burst of zoomies, or squeeze the " +
                "Squeaky Toy to send him out as a decoy.\n\n" +
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
                new IntVector2(3, 2), new IntVector2(12, 8));   // frames carry a 1-px margin for the runtime outline
            CocoBlueController controller = prefab.AddComponent<CocoBlueController>();
            controller.CanBePet = true;                       // interact next to Coco to pet him (the Dog's mechanic)
            prefab.GetComponent<AIActor>().MovementSpeed = 6.5f;

            // Bullet blocking is done by a separate shield body created at runtime (see CocoBlueController):
            // the companion's own body has CollideWithOthers off so everyone can walk through him, and that
            // flag also makes the physics engine ignore projectiles against it.

            prefab.AddAnimation("idle", Plugin.COMPANION_ROOT + "/idle", 4, CompanionBuilder.AnimationType.Idle,
                DirectionalAnimation.DirectionType.Single).wrapMode = tk2dSpriteAnimationClip.WrapMode.Loop;
            prefab.AddAnimation("move", Plugin.COMPANION_ROOT + "/move", 9, CompanionBuilder.AnimationType.Move,
                DirectionalAnimation.DirectionType.Single).wrapMode = tk2dSpriteAnimationClip.WrapMode.Loop;
            prefab.AddAnimation("pet", Plugin.COMPANION_ROOT + "/pet", 6, CompanionBuilder.AnimationType.Other,
                DirectionalAnimation.DirectionType.Single).wrapMode = tk2dSpriteAnimationClip.WrapMode.Loop;
            prefab.AddAnimation("block", Plugin.COMPANION_ROOT + "/block", 12, CompanionBuilder.AnimationType.Other,
                DirectionalAnimation.DirectionType.Single).wrapMode = tk2dSpriteAnimationClip.WrapMode.Once;
            prefab.AddAnimation("ko", Plugin.COMPANION_ROOT + "/ko", 4, CompanionBuilder.AnimationType.Other,
                DirectionalAnimation.DirectionType.Single).wrapMode = tk2dSpriteAnimationClip.WrapMode.Loop;

            // Knighted: the helmeted set. Like Ser Junkan's armour clips, these are swapped in by name (SetKnighted).
            AddKnightClip("idle", 4, tk2dSpriteAnimationClip.WrapMode.Loop);
            AddKnightClip("move", 9, tk2dSpriteAnimationClip.WrapMode.Loop);
            AddKnightClip("pet", 6, tk2dSpriteAnimationClip.WrapMode.Loop);
            AddKnightClip("block", 12, tk2dSpriteAnimationClip.WrapMode.Once);
            AddKnightClip("ko", 4, tk2dSpriteAnimationClip.WrapMode.Loop);
            prefab.AddComponent<CocoFriends>();

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

        private static void AddKnightClip(string clip, int fps, tk2dSpriteAnimationClip.WrapMode wrap)
        {
            prefab.AddAnimation("knight_" + clip, Plugin.COMPANION_ROOT + "/knight_" + clip, fps, CompanionBuilder.AnimationType.Other,
                DirectionalAnimation.DirectionType.Single).wrapMode = wrap;
        }

        /// <summary>Lives on the spawned companion: crumbs on owner damage, petting, bullet blocking, decoy mode.</summary>
        public class CocoBlueController : CompanionController
        {
            public static readonly List<CocoBlueController> Instances = new List<CocoBlueController>();

            private PlayerController watched;
            private float cooldown, blockCooldown;
            private bool wasBeingPet;

            // decoy mode
            private bool decoy;
            private float decoyLeft, retargetTimer, fleeTimer;
            private float normalSpeed = 6.5f;

            // stuffing: how many bullets he can take before he is knocked out for a while
            private int stuffing;
            private bool ko;
            private float koLeft, regenTimer;

            public PlayerController OwnerPlayer { get { return m_owner; } }
            public bool IsDecoy { get { return decoy; } }
            public bool IsKnockedOut { get { return ko; } }
            public int Stuffing { get { return stuffing; } }

            /// <summary>Squire: +1 stuffing per Ser Junkan form, capped at the Holy Knight's +6 (Mecha is form 8 from one gold junk).</summary>
            public int MaxStuffing
            {
                get
                {
                    SackKnightController junkan = CocoFriends.SquireJunkan(m_owner);
                    return PlutoConfig.CocoStuffing + (junkan != null ? Mathf.Min((int)junkan.CurrentForm, 6) : 0);
                }
            }

            private bool knighted;

            /// <summary>Knighted: point the idle/move/pet/block/ko slots at the helmeted clips (or back), like Junkan does.</summary>
            public void SetKnighted(bool on)
            {
                if (on == knighted || aiAnimator == null) return;
                knighted = on;
                string prefix = on ? "knight_" : "";
                SetClip(aiAnimator.IdleAnimation, prefix + "idle");
                SetClip(aiAnimator.MoveAnimation, prefix + "move");
                if (aiAnimator.OtherAnimations != null)
                    for (int i = 0; i < aiAnimator.OtherAnimations.Count; i++)
                    {
                        AIAnimator.NamedDirectionalAnimation named = aiAnimator.OtherAnimations[i];
                        if (named.name == "pet" || named.name == "block" || named.name == "ko") SetClip(named.anim, prefix + named.name);
                    }
                // restart a held state so the helmet appears (or comes off) right away
                if (ko) aiAnimator.PlayUntilCancelled("ko", true);
                else if (IsBeingPet) aiAnimator.PlayUntilCancelled("pet", true);
                PlutoVFX.Spawn(PlutoVFX.LoveBurst, (Vector2)transform.position + new Vector2(0.5f, 1f));
            }

            private static void SetClip(DirectionalAnimation anim, string clip)
            {
                if (anim != null && anim.AnimNames != null && anim.AnimNames.Length > 0) anim.AnimNames[0] = clip;
            }

            public static CocoBlueController For(PlayerController player)
            {
                for (int i = 0; i < Instances.Count; i++)
                    if (Instances[i] != null && Instances[i].m_owner == player) return Instances[i];
                return null;
            }

            private void OnEnable() { if (!Instances.Contains(this)) Instances.Add(this); }
            private void OnDisable() { Instances.Remove(this); }

            private bool hooked;
            private SpeculativeRigidbody shield;

            /// <summary>A bullet-blocker body that rides on Coco. Only projectiles interact with that layer.</summary>
            private void BuildShield()
            {
                if (!PlutoConfig.CocoBlocksBullets || shield != null) return;
                GameObject go = new GameObject("coco_shield");
                go.transform.parent = transform;
                go.transform.localPosition = Vector3.zero;
                shield = go.AddComponent<SpeculativeRigidbody>();
                shield.CollideWithTileMap = false;
                shield.CollideWithOthers = true;
                shield.PixelColliders = new List<PixelCollider>
                {
                    new PixelCollider
                    {
                        ColliderGenerationMode = PixelCollider.PixelColliderGeneration.Manual,
                        CollisionLayer = CollisionLayer.BulletBlocker,
                        IsTrigger = false,
                        ManualOffsetX = 3, ManualOffsetY = 2,
                        ManualWidth = 12, ManualHeight = 10,
                    }
                };
                shield.Reinitialize();
                shield.OnPreRigidbodyCollision += OnPreCollision;
            }

            public override void Update()
            {
                base.Update();
                if (!hooked)
                {
                    // CompanionController's own Start is not virtual, so hook up on the first frame instead.
                    hooked = true;
                    if (aiActor != null) normalSpeed = aiActor.MovementSpeed;
                    stuffing = MaxStuffing;
                    BuildShield();
                }
                if (shield != null)
                {
                    shield.transform.position = transform.position;   // keep the shield on Coco
                    shield.Reinitialize();
                }
                float dt = BraveTime.DeltaTime;
                cooldown -= dt; blockCooldown -= dt;
                if (ko)
                {
                    koLeft -= dt;
                    if (IsBeingPet || koLeft <= 0f) Recover();     // a pet brings him round early
                }
                else
                {
                    int max = MaxStuffing;                          // grows and shrinks with Squire
                    if (stuffing > max) stuffing = max;
                    else if (stuffing < max)
                    {
                        regenTimer -= dt;
                        if (regenTimer <= 0f) { regenTimer = PlutoConfig.CocoStuffingRegenSeconds; stuffing++; }
                    }
                }
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
                    // A pet in the middle of a fight is the "go get them" signal: same as the Squeaky Toy.
                    if (petter != null && petter.IsInCombat && !ko) StartDecoy(PlutoConfig.DecoySeconds);
                }
                wasBeingPet = petting;

                if (decoy) DecoyUpdate(dt);
            }

            public override void OnDestroy()
            {
                if (watched != null && watched.healthHaver != null) watched.healthHaver.OnDamaged -= OnOwnerDamaged;
                if (shield != null) { shield.OnPreRigidbodyCollision -= OnPreCollision; Destroy(shield.gameObject); shield = null; }
                if (decoy) EndDecoy();
                Instances.Remove(this);
                base.OnDestroy();
            }

            private void OnOwnerDamaged(float resultValue, float maxValue, CoreDamageTypes damageTypes, DamageCategory damageCategory, Vector2 damageDirection)
            {
                if (cooldown > 0f || watched == null) return;
                cooldown = 1.5f;
                KibbleSackGun.SpawnCrumb(transform.position);
                AkSoundEngine.PostEvent("Play_OBJ_item_throw_01", gameObject);
            }

            // ---------------------------------------------------------------- bullet blocking
            private void OnPreCollision(SpeculativeRigidbody myBody, PixelCollider myCollider, SpeculativeRigidbody other, PixelCollider otherCollider)
            {
                if (other == null || other.projectile == null) return;
                Projectile p = other.projectile;
                if (p.Owner is PlayerController || !PlutoConfig.CocoBlocksBullets || ko)
                {
                    PhysicsEngine.SkipCollision = true;    // Pluto's own shots pass through; a knocked-out Coco blocks nothing
                    return;
                }
                // Enemy bullet: it dies against the blocker layer; Coco squishes and a spark pops.
                if (blockCooldown <= 0f)
                {
                    blockCooldown = 0.15f;
                    if (aiAnimator != null) aiAnimator.PlayUntilFinished("block", true);
                    PlutoVFX.Spawn(PlutoVFX.BlockSpark, other.UnitCenter);
                    stuffing--;
                    regenTimer = PlutoConfig.CocoStuffingRegenSeconds;
                    if (stuffing <= 0) KnockOut();
                }
            }

            // ---------------------------------------------------------------- knocked out
            private void KnockOut()
            {
                if (ko) return;
                ko = true;
                koLeft = PlutoConfig.CocoKnockoutSeconds;
                if (decoy) EndDecoy();
                CompanionFollowPlayerBehavior follow = Follow();
                if (follow != null) follow.TemporarilyDisabled = true;
                if (aiActor != null) aiActor.ClearPath();
                if (aiAnimator != null) aiAnimator.PlayUntilCancelled("ko", true);
                PlutoVFX.Spawn(PlutoVFX.FurPuff, (Vector2)transform.position + new Vector2(0.5f, 0.4f));
                AkSoundEngine.PostEvent("Play_OBJ_item_throw_01", gameObject);
            }

            private void Recover()
            {
                if (!ko) return;
                ko = false;
                stuffing = MaxStuffing;
                CompanionFollowPlayerBehavior follow = Follow();
                if (follow != null) follow.TemporarilyDisabled = false;
                if (aiAnimator != null)
                {
                    aiAnimator.EndAnimationIf("ko");
                    aiAnimator.PlayUntilFinished("block", true);   // a little spring back up
                }
                PlutoVFX.Spawn(PlutoVFX.LoveBurst, (Vector2)transform.position + new Vector2(0.5f, 0.8f));
            }

            // ---------------------------------------------------------------- decoy mode
            public void StartDecoy(float seconds)
            {
                if (ko) return;
                decoyLeft = seconds;
                if (decoy) return;
                decoy = true;
                retargetTimer = 0f; fleeTimer = 0f;
                CompanionFollowPlayerBehavior follow = Follow();
                if (follow != null) follow.TemporarilyDisabled = true;
                if (aiActor != null) aiActor.MovementSpeed = normalSpeed * 1.4f;
                PlutoVFX.Spawn(PlutoVFX.AngerMarks, (Vector2)transform.position + new Vector2(0.5f, 1f));
            }

            private void EndDecoy()
            {
                decoy = false;
                CompanionFollowPlayerBehavior follow = Follow();
                if (follow != null) follow.TemporarilyDisabled = false;
                if (aiActor != null)
                {
                    aiActor.MovementSpeed = normalSpeed;
                    aiActor.ClearPath();
                }
                RoomHandler room = CurrentRoom();
                if (room != null) SetOverrides(room, false);
            }

            private CompanionFollowPlayerBehavior Follow()
            {
                if (behaviorSpeculator == null) return null;
                for (int i = 0; i < behaviorSpeculator.MovementBehaviors.Count; i++)
                {
                    CompanionFollowPlayerBehavior f = behaviorSpeculator.MovementBehaviors[i] as CompanionFollowPlayerBehavior;
                    if (f != null) return f;
                }
                return null;
            }

            private RoomHandler CurrentRoom()
            {
                if (aiActor != null && aiActor.ParentRoom != null) return aiActor.ParentRoom;
                return ((Vector2)transform.position).GetAbsoluteRoom();
            }

            /// <summary>Same mechanism as the vanilla Decoy item: every enemy in the room targets Coco's body.</summary>
            private void SetOverrides(RoomHandler room, bool on)
            {
                List<AIActor> enemies = room.GetActiveEnemies(RoomHandler.ActiveEnemyType.All);
                if (enemies == null) return;
                for (int i = 0; i < enemies.Count; i++)
                {
                    AIActor e = enemies[i];
                    if (e == null || e == aiActor) continue;
                    if (on) { if (e.OverrideTarget == null) e.OverrideTarget = specRigidbody; }
                    else if (e.OverrideTarget == specRigidbody) e.OverrideTarget = null;
                }
            }

            private void DecoyUpdate(float dt)
            {
                decoyLeft -= dt; retargetTimer -= dt; fleeTimer -= dt;
                RoomHandler room = CurrentRoom();
                if (decoyLeft <= 0f || room == null || m_owner == null || (m_owner.CurrentRoom != null && m_owner.CurrentRoom != room))
                {
                    EndDecoy();
                    return;
                }
                if (retargetTimer <= 0f)
                {
                    retargetTimer = 0.5f;
                    SetOverrides(room, true);
                }
                if (fleeTimer <= 0f)
                {
                    fleeTimer = 0.35f;
                    Flee(room);
                }
            }

            /// <summary>Run away from nearby enemy bullets and enemies; wander if nothing is close.</summary>
            private void Flee(RoomHandler room)
            {
                if (aiActor == null) return;
                Vector2 me = specRigidbody != null ? specRigidbody.UnitCenter : (Vector2)transform.position;
                Vector2 away = Vector2.zero;
                System.Collections.ObjectModel.ReadOnlyCollection<Projectile> shots = StaticReferenceManager.AllProjectiles;
                if (shots != null)
                {
                    for (int i = 0; i < shots.Count; i++)
                    {
                        Projectile p = shots[i];
                        if (p == null || p.Owner is PlayerController) continue;
                        Vector2 d = me - (Vector2)p.transform.position;
                        float dist = d.magnitude;
                        if (dist < 0.05f || dist > 5f) continue;
                        away += d / (dist * dist);
                    }
                }
                List<AIActor> enemies = room.GetActiveEnemies(RoomHandler.ActiveEnemyType.All);
                if (enemies != null)
                {
                    for (int i = 0; i < enemies.Count; i++)
                    {
                        AIActor e = enemies[i];
                        if (e == null || e == aiActor) continue;
                        Vector2 d = me - e.CenterPosition;
                        float dist = d.magnitude;
                        if (dist < 0.05f || dist > 6f) continue;
                        away += 0.5f * d / (dist * dist);
                    }
                }
                Vector2 dir = away.sqrMagnitude > 0.0001f ? away.normalized : Random.insideUnitCircle.normalized;
                dir = (dir + Random.insideUnitCircle * 0.35f).normalized;      // a little wobble so it reads as panicky
                Vector2 target = me + dir * 3.5f;
                IntVector2 cell = target.ToIntVector2(VectorConversions.Floor);
                DungeonData data = GameManager.Instance.Dungeon.data;
                if (!data.CheckInBoundsAndValid(cell) || !data[cell].IsPassable || data[cell].parentRoom != room)
                {
                    IntVector2? alt = room.GetRandomAvailableCell(new IntVector2(1, 1), CellTypes.FLOOR, false, null);
                    if (alt == null) return;
                    target = alt.Value.ToCenterVector2();
                }
                aiActor.PathfindToPosition(target);
            }
        }
    }
}
