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

            // Squire: the gold plumed knight helmet (knight_) for every Junkan form.
            // Like Ser Junkan's armour clips, these are swapped in by name (SetHelmet).
            foreach (string helmet in new[] { "knight_" })
            {
                AddHelmetClip(helmet, "idle", 4, tk2dSpriteAnimationClip.WrapMode.Loop);
                AddHelmetClip(helmet, "move", 9, tk2dSpriteAnimationClip.WrapMode.Loop);
                AddHelmetClip(helmet, "pet", 6, tk2dSpriteAnimationClip.WrapMode.Loop);
                AddHelmetClip(helmet, "block", 12, tk2dSpriteAnimationClip.WrapMode.Once);
                AddHelmetClip(helmet, "ko", 4, tk2dSpriteAnimationClip.WrapMode.Loop);
            }
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

        private static void AddHelmetClip(string helmet, string clip, int fps, tk2dSpriteAnimationClip.WrapMode wrap)
        {
            prefab.AddAnimation(helmet + clip, Plugin.COMPANION_ROOT + "/" + helmet + clip, fps, CompanionBuilder.AnimationType.Other,
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
            private RoomHandler decoyRoom;
            private readonly HashSet<AIActor> ownedTargets = new HashSet<AIActor>();
            private Vector2 dodgeTarget, lastFleePosition;
            private bool hasDodgeTarget;
            private float legAge;
            private readonly float[] legX = new float[CompanionKitRules.DecoyCandidateCount], legY = new float[CompanionKitRules.DecoyCandidateCount];
            private readonly float[] legThreat = new float[CompanionKitRules.DecoyCandidateCount], legJitter = new float[CompanionKitRules.DecoyCandidateCount];
            private readonly CompanionOwnedValue<bool> decoyFollow = new CompanionOwnedValue<bool>();
            private readonly CompanionOwnedValue<float> decoySpeed = new CompanionOwnedValue<float>();

            // stuffing: how many bullets he can take before he is knocked out for a while
            private CocoShieldCharges charges = new CocoShieldCharges(0);
            private bool ko;
            private float koLeft, regenTimer;

            public PlayerController OwnerPlayer { get { return m_owner; } }
            public bool IsDecoy { get { return decoy; } }
            public bool IsKnockedOut { get { return ko; } }
            public int Stuffing { get { return charges.Remaining; } }

            /// <summary>Squire: +1 stuffing per Ser Junkan form, capped at the Holy Knight's +6 (Mecha is form 8 from one gold junk).</summary>
            public int MaxStuffing
            {
                get
                {
                    SackKnightController junkan = CocoFriends.SquireJunkan(m_owner);
                    return PlutoConfig.CocoStuffing + (junkan != null ? Mathf.Min((int)junkan.CurrentForm, 6) : 0);
                }
            }

            private string helmet = "";

            /// <summary>
            /// Squire: point the idle/move/pet/block/ko slots at the helmeted clip set ("knight_", the gold plumed
            /// helmet) or back to the plain clips (""), like Junkan swaps his armour clips.
            /// </summary>
            public void SetHelmet(string prefix)
            {
                if (prefix == null) prefix = "";
                if (prefix == helmet || aiAnimator == null) return;
                helmet = prefix;
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

            // A Single-direction animation plays its Prefix (DirectionalAnimation.GetInfo(0) returns Prefix for
            // DirectionType.Single and never reads AnimNames); Junkan's two-way clips read AnimNames. Write both.
            private static void SetClip(DirectionalAnimation anim, string clip)
            {
                if (anim == null) return;
                anim.Prefix = clip;
                if (anim.AnimNames != null && anim.AnimNames.Length > 0) anim.AnimNames[0] = clip;
            }

            public static CocoBlueController For(PlayerController player)
            {
                for (int i = 0; i < Instances.Count; i++)
                    if (Instances[i] != null && Instances[i].m_owner == player) return Instances[i];
                return null;
            }

            private void OnEnable() { if (!Instances.Contains(this)) Instances.Add(this); }
            private void OnDisable() { EndDecoy(); Instances.Remove(this); }

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
                    charges.Refill(MaxStuffing);
                    BuildShield();
                }
                if (shield != null)
                {
                    shield.transform.position = transform.position;   // keep the shield on Coco
                    shield.Reinitialize();
                }
                float dt = BraveTime.DeltaTime;
                cooldown -= dt; blockCooldown -= dt;
                charges.ForgetDestroyed(delegate(object shot) { return (Projectile)shot == null; });
                if (ko)
                {
                    koLeft -= dt;
                    if (IsBeingPet || koLeft <= 0f) Recover();     // a pet brings him round early
                }
                else
                {
                    int max = MaxStuffing;                          // grows and shrinks with Squire
                    if (charges.Remaining > max) charges.Clamp(max);
                    else if (charges.Remaining < max)
                    {
                        regenTimer -= dt;
                        if (regenTimer <= 0f) { regenTimer = PlutoConfig.CocoStuffingRegenSeconds; charges.Regenerate(max); }
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
                EndDecoy();
                Instances.Remove(this);
                base.OnDestroy();
            }

            private void OnOwnerDamaged(float resultValue, float maxValue, CoreDamageTypes damageTypes, DamageCategory damageCategory, Vector2 damageDirection)
            {
                if (cooldown > 0f || watched == null) return;
                cooldown = 1.5f;
                KibbleSackGun.SpawnCrumb(transform.position, watched);
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
                // Account for each distinct projectile, even inside the cosmetic cooldown.
                if (!charges.TryBlock(p)) return;
                regenTimer = PlutoConfig.CocoStuffingRegenSeconds;
                if (blockCooldown <= 0f)
                {
                    blockCooldown = 0.15f;
                    if (aiAnimator != null) aiAnimator.PlayUntilFinished("block", true);
                    PlutoVFX.Spawn(PlutoVFX.BlockSpark, other.UnitCenter);
                }
                if (charges.Remaining <= 0) KnockOut();
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
                charges.Refill(MaxStuffing);
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
                decoyRoom = CurrentRoom();
                hasDodgeTarget = false;
                lastFleePosition = specRigidbody != null ? specRigidbody.UnitCenter : (Vector2)transform.position;
                retargetTimer = 0f; fleeTimer = 0f;
                CompanionFollowPlayerBehavior follow = Follow();
                if (follow != null)
                {
                    decoyFollow.Record(follow.TemporarilyDisabled, true);
                    follow.TemporarilyDisabled = true;
                }
                if (aiActor != null)
                {
                    decoySpeed.Record(aiActor.MovementSpeed, normalSpeed * 1.4f);
                    aiActor.MovementSpeed = normalSpeed * 1.4f;
                }
                PlutoVFX.Spawn(PlutoVFX.AngerMarks, (Vector2)transform.position + new Vector2(0.5f, 1f));
            }

            private void EndDecoy()
            {
                foreach (AIActor enemy in ownedTargets)
                    if (enemy != null && enemy.OverrideTarget == specRigidbody) enemy.OverrideTarget = null;
                ownedTargets.Clear();
                if (!decoy) return;
                decoy = false;
                decoyRoom = null;
                hasDodgeTarget = false;
                CompanionFollowPlayerBehavior follow = Follow();
                if (follow != null) follow.TemporarilyDisabled = decoyFollow.Restore(follow.TemporarilyDisabled);
                if (aiActor != null)
                {
                    aiActor.MovementSpeed = decoySpeed.Restore(aiActor.MovementSpeed);
                    aiActor.ClearPath();
                }
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
            private void SetOverrides(RoomHandler room)
            {
                List<AIActor> enemies = room.GetActiveEnemies(RoomHandler.ActiveEnemyType.All);
                if (enemies == null) return;
                for (int i = 0; i < enemies.Count; i++)
                {
                    AIActor e = enemies[i];
                    if (e == null || e == aiActor || e.CompanionOwner != null || ownedTargets.Contains(e)) continue;
                    if (e.OverrideTarget == null)
                    {
                        ownedTargets.Add(e);
                        e.OverrideTarget = specRigidbody;
                    }
                }
            }

            private void DecoyUpdate(float dt)
            {
                decoyLeft -= dt; retargetTimer -= dt; fleeTimer -= dt; legAge += dt;
                RoomHandler room = CurrentRoom();
                if (decoyLeft <= 0f || room == null || room != decoyRoom || m_owner == null || (m_owner.CurrentRoom != null && m_owner.CurrentRoom != room))
                {
                    EndDecoy();
                    return;
                }
                if (retargetTimer <= 0f)
                {
                    retargetTimer = 0.5f;
                    SetOverrides(room);
                }
                if (fleeTimer <= 0f)
                {
                    fleeTimer = 0.35f;
                    Flee(room);
                }
            }

            /// <summary>
            /// Keep running: always a leg to a floor spot 2.5-3.5 tiles away (random spin and jitter so it reads as panicky),
            /// scored against incoming bullets and nearby enemies and kept within reach of the owner (CompanionKitRules).
            /// A new leg starts on arrival, after a stall, after DecoyMaxLegSeconds, or when a bullet crosses the current one.
            /// </summary>
            private void Flee(RoomHandler room)
            {
                if (aiActor == null || m_owner == null || GameManager.Instance == null || GameManager.Instance.Dungeon == null) return;
                Vector2 me = specRigidbody != null ? specRigidbody.UnitCenter : (Vector2)transform.position;
                Vector2 owner = m_owner.CenterPosition;
                DungeonData data = GameManager.Instance.Dungeon.data;
                float moved = Vector2.Distance(me, lastFleePosition);
                lastFleePosition = me;

                CompanionKitRules.DecoyCandidates(me.x, me.y, owner.x, owner.y, Random.value * Mathf.PI * 2f, Random.Range(2.5f, 3.5f), legX, legY);
                for (int i = 0; i < legX.Length; i++)
                {
                    Vector2 target = new Vector2(legX[i], legY[i]);
                    legJitter[i] = Random.value * 1.5f;
                    if (!WalkableSpot(data, room, target)) { legX[i] = me.x; legY[i] = me.y; legThreat[i] = 0f; continue; }  // too short: rejected
                    legThreat[i] = DodgeScore(room, me, target, owner);
                }
                int best = CompanionKitRules.PickDecoyLeg(me.x, me.y, owner.x, owner.y, legX, legY, legThreat, legJitter);
                float bestScore = best >= 0
                    ? CompanionKitRules.DecoyLegScore(me.x, me.y, legX[best], legY[best], owner.x, owner.y, legThreat[best], legJitter[best])
                    : float.MaxValue;
                float currentThreat = hasDodgeTarget ? DodgeScore(room, me, dodgeTarget, owner) : 0f;
                if (!CompanionKitRules.NeedsNewDecoyLeg(hasDodgeTarget, Vector2.Distance(me, dodgeTarget), legAge, moved, currentThreat, bestScore)) return;

                Vector2 next;
                if (best >= 0) next = new Vector2(legX[best], legY[best]);
                else
                {
                    // Boxed in (corner, narrow corridor): any open cell in the room, or back to the owner if that strays too far.
                    IntVector2? alt = room.GetRandomAvailableCell(new IntVector2(1, 1), CellTypes.FLOOR, false, null);
                    next = alt != null ? alt.Value.ToCenterVector2() : owner;
                    if (Vector2.Distance(next, owner) > CompanionKitRules.DecoyLeash) next = owner;
                }
                dodgeTarget = next;
                hasDodgeTarget = true;
                legAge = 0f;
                aiActor.PathfindToPosition(next);
            }

            private float DodgeScore(RoomHandler room, Vector2 me, Vector2 target, Vector2 owner)
            {
                Vector2 delta = target - me;
                float travel = Mathf.Max(0.05f, delta.magnitude / Mathf.Max(1f, aiActor.MovementSpeed));
                Vector2 velocity = delta / travel;
                float score = 0f;   // owner distance is scored by CompanionKitRules.DecoyLegScore
                // Avoid pulling Coco's pursuers through Pluto's body.
                float along = delta.sqrMagnitude < 0.01f ? 0f : Mathf.Clamp01(Vector2.Dot(owner - me, delta) / delta.sqrMagnitude);
                score += Mathf.Max(0f, 1.5f - Vector2.Distance(owner, me + delta * along)) * 8f;
                var shots = StaticReferenceManager.AllProjectiles;
                if (shots != null)
                    for (int i = 0; i < shots.Count; i++)
                    {
                        Projectile p = shots[i];
                        if (p == null || p.Owner is PlayerController || p.specRigidbody == null) continue;
                        Vector2 position = p.specRigidbody.UnitCenter;
                        Vector2 bulletVelocity = p.specRigidbody.Velocity;
                        if (Vector2.Distance(position, me) > 12f) continue;
                        Vector2 relative = position - me, speed = bulletVelocity - velocity;
                        score += CompanionKitRules.ProjectileRisk(relative.x, relative.y, speed.x, speed.y, travel);
                        relative = position + bulletVelocity * travel - target;
                        score += CompanionKitRules.ProjectileRisk(relative.x, relative.y, bulletVelocity.x, bulletVelocity.y, 0.4f);
                    }
                List<AIActor> enemies = room.GetActiveEnemies(RoomHandler.ActiveEnemyType.All);
                if (enemies != null)
                    for (int i = 0; i < enemies.Count; i++)
                    {
                        AIActor enemy = enemies[i];
                        if (enemy == null || enemy == aiActor || enemy.CompanionOwner != null) continue;
                        score += Mathf.Max(0f, 3f - Vector2.Distance(target, enemy.CenterPosition)) * 4f;
                    }
                return score;
            }

            // The spot itself must fit Coco's footprint on floor in this room; the pathfinder handles the route and any detour.
            private static bool WalkableSpot(DungeonData data, RoomHandler room, Vector2 spot)
            {
                for (int corner = 0; corner < 5; corner++)
                {
                    Vector2 point = corner == 4 ? spot : spot + new Vector2((corner % 2 == 0 ? -1f : 1f) * 0.4f, (corner < 2 ? -1f : 1f) * 0.3f);
                    IntVector2 cell = point.ToIntVector2(VectorConversions.Floor);
                    if (!data.CheckInBoundsAndValid(cell) || !data[cell].IsPassable || data[cell].type != CellType.FLOOR || data[cell].parentRoom != room) return false;
                }
                return true;
            }
        }
    }
}
