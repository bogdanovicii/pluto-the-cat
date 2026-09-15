using UnityEngine;
using Alexandria.ItemAPI;
using Alexandria.Misc;
using Dungeonator;

namespace PlutoTheCat
{
    /// <summary>
    /// Coco Blue's friends. Lives on the Coco companion next to CocoBlueController and only reads its state.
    /// - Playdate (Squeaky Toy + Dog): while Coco is a decoy the Dog fights like the vanilla Wolf: it gets the Wolf
    ///   companion's SeekTargetBehavior + WolfCompanionAttackBehavior (bark, leap, bite) aimed at the enemy chasing
    ///   Coco, and loses them when the decoy ends (vanilla Dog has no attack behaviours at all; 2.16.2).
    ///   Petting either one makes the other happy too.
    /// - Squire (Coco + Ser Junkan): +1 stuffing per Junkan form (CocoBlueController.MaxStuffing); while Coco
    ///   is a decoy, Junkan's OverrideTarget (which wins over PlayerTarget) is the enemy chasing him.
    /// - Knighted (Squire tier): while Junkan is a Holy or Angelic Knight, Coco plays his helmeted clips.
    /// </summary>
    public class CocoFriends : MonoBehaviour
    {
        public const int DogId = 300;
        public const int JunkanId = 580;
        private CocoBlueItem.CocoBlueController coco;
        private float lookTimer;
        private AIActor chaser;                      // the enemy the friends go after while Coco is a decoy
        private AIActor heldDog;                     // the Dog fighting as a Wolf (follow paused, attack behaviours added)
        private SeekTargetBehavior dogSeek;
        private WolfCompanionAttackBehavior dogBite;
        private AIActor aimedJunkan;                 // the Junkan pointed at the chaser
        private SpeculativeRigidbody aimedBody;
        private bool cocoWasPet, dogWasPet, wasDecoy;

        /// <summary>The live companion spawned by the owner's passive item with this pickup id, or null.</summary>
        public static AIActor CompanionFrom(PlayerController player, int itemId)
        {
            if (player == null || player.passiveItems == null) return null;
            for (int i = 0; i < player.passiveItems.Count; i++)
            {
                CompanionItem item = player.passiveItems[i] as CompanionItem;
                if (item == null || item.PickupObjectId != itemId || item.ExtantCompanion == null) continue;
                return item.ExtantCompanion.GetComponent<AIActor>();
            }
            return null;
        }

        /// <summary>Ser Junkan's form when Squire is active, or null.</summary>
        public static SackKnightController SquireJunkan(PlayerController player)
        {
            if (player == null || !player.PlayerHasActiveSynergy(PlutoSynergies.Squire)) return null;
            AIActor junkan = CompanionFrom(player, JunkanId);
            return junkan != null ? junkan.GetComponent<SackKnightController>() : null;
        }

        private void Start()
        {
            coco = GetComponent<CocoBlueItem.CocoBlueController>();
        }

        private void Update()
        {
            if (coco == null) return;
            PlayerController owner = coco.OwnerPlayer;
            if (owner == null) return;
            lookTimer -= BraveTime.DeltaTime;

            AIActor dog = owner.PlayerHasActiveSynergy(PlutoSynergies.Playdate) ? CompanionFrom(owner, DogId) : null;
            SackKnightController knight = SquireJunkan(owner);
            AIActor junkan = knight != null ? knight.aiActor : null;

            coco.SetKnighted(knight != null && (knight.CurrentForm == SackKnightController.SackKnightPhase.HOLY_KNIGHT
                                             || knight.CurrentForm == SackKnightController.SackKnightPhase.ANGELIC_KNIGHT));

            if (coco.IsDecoy && (dog != null || junkan != null))
            {
                if (lookTimer <= 0f || !Alive(chaser)) { lookTimer = 0.5f; chaser = FindChaser(owner); }
            }
            else chaser = null;
            if (coco.IsDecoy && !wasDecoy)
                Plugin.Log("Coco decoy: Playdate " + owner.PlayerHasActiveSynergy(PlutoSynergies.Playdate) + " (dog " + (dog != null) +
                    "), Squire " + (knight != null) + ", chaser " + (chaser != null ? chaser.GetActorName() : "none"));
            wasDecoy = coco.IsDecoy;

            UpdateDog(dog);
            UpdateJunkan(junkan);
            UpdatePets(owner, dog);
        }

        private void OnDisable()
        {
            ReleaseDog();
            ReleaseJunkan();
        }

        private static bool Alive(AIActor a)
        {
            return a != null && a.healthHaver != null && !a.healthHaver.IsDead;
        }

        /// <summary>The nearest enemy targeting Coco; failing that, the nearest enemy to him within 8 tiles.</summary>
        private AIActor FindChaser(PlayerController owner)
        {
            // A companion's ParentRoom is never set (CompanionItem.CreateCompanion instantiates it without
            // ConfigureOnPlacement), so look the room up like vanilla TargetEnemiesBehavior does.
            RoomHandler room = owner.CurrentRoom != null ? owner.CurrentRoom : ((Vector2)coco.transform.position).GetAbsoluteRoom();
            if (room == null) return null;
            System.Collections.Generic.List<AIActor> enemies = room.GetActiveEnemies(RoomHandler.ActiveEnemyType.All);
            if (enemies == null) return null;
            Vector2 me = coco.specRigidbody != null ? coco.specRigidbody.UnitCenter : (Vector2)coco.transform.position;
            AIActor best = null, near = null;
            float bestD = float.MaxValue, nearD = 8f;
            for (int i = 0; i < enemies.Count; i++)
            {
                AIActor e = enemies[i];
                if (!Alive(e) || e.CompanionOwner != null) continue;
                float d = Vector2.Distance(me, e.CenterPosition);
                if (e.OverrideTarget == coco.specRigidbody && d < bestD) { best = e; bestD = d; }
                if (d < nearD) { near = e; nearD = d; }
            }
            return best != null ? best : near;
        }

        // ---------------------------------------------------------------- Playdate
        private void UpdateDog(AIActor dog)
        {
            if (dog == null || !Alive(chaser))
            {
                ReleaseDog();
                return;
            }
            if (heldDog != dog)
            {
                ReleaseDog();
                if (dog.behaviorSpeculator == null) return;
                heldDog = dog;
                SetFollow(dog, false);
                // The vanilla Wolf's (Dog_Past) combat behaviours, fresh instances with its prefab values. The Dog has no
                // "attack" clip, so the leap plays its roll; the bite is WolfCompanionAttackBehavior's own 5 damage.
                dogSeek = new SeekTargetBehavior { StopWhenInRange = false, LineOfSight = true, ReturnToSpawn = false, PathInterval = 0.25f, CustomRange = -1f };
                dogBite = new WolfCompanionAttackBehavior
                {
                    minLeapDistance = 1f, leapDistance = 2f, maxTravelDistance = 5f, leadAmount = 1f,
                    leapTime = 0.3f, maximumChargeTime = 0.25f, chargeAnim = "bark", leapAnim = "roll"
                };
                dog.behaviorSpeculator.MovementBehaviors.Add(dogSeek);
                dog.behaviorSpeculator.AttackBehaviors.Add(dogBite);
                dog.behaviorSpeculator.RefreshBehaviors();
                Plugin.Log("Playdate: the Dog fights like a Wolf, target " + chaser.GetActorName());
            }
            // OverrideTarget wins over the companion's own nearest-enemy pick, so the Wolf bite goes to Coco's chaser.
            if (chaser.specRigidbody != null) dog.OverrideTarget = chaser.specRigidbody;
        }

        private void ReleaseDog()
        {
            if (heldDog == null) { heldDog = null; dogSeek = null; dogBite = null; return; }
            BehaviorSpeculator bs = heldDog.behaviorSpeculator;
            if (bs != null)
            {
                bs.Interrupt();                              // a leap in progress would keep its velocity override
                if (dogSeek != null) bs.MovementBehaviors.Remove(dogSeek);
                if (dogBite != null) bs.AttackBehaviors.Remove(dogBite);
                bs.RefreshBehaviors();
            }
            heldDog.BehaviorOverridesVelocity = false;
            if (heldDog.aiAnimator != null) heldDog.aiAnimator.LockFacingDirection = false;
            heldDog.PathableTiles = CellTypes.FLOOR;
            heldDog.OverrideTarget = null;
            SetFollow(heldDog, true);
            heldDog.ClearPath();
            Plugin.Log("Playdate: the Dog is a Dog again");
            heldDog = null;
            dogSeek = null;
            dogBite = null;
        }

        private static void SetFollow(AIActor actor, bool on)
        {
            if (actor.behaviorSpeculator == null) return;
            for (int i = 0; i < actor.behaviorSpeculator.MovementBehaviors.Count; i++)
            {
                CompanionFollowPlayerBehavior f = actor.behaviorSpeculator.MovementBehaviors[i] as CompanionFollowPlayerBehavior;
                if (f != null) f.TemporarilyDisabled = !on;
            }
        }

        /// <summary>Petting one friend makes the other wiggle with hearts; petting the Dog also gives Coco's speed burst.</summary>
        private void UpdatePets(PlayerController owner, AIActor dog)
        {
            CompanionController dogCtl = dog != null ? dog.GetComponent<CompanionController>() : null;
            bool cocoPet = coco.IsBeingPet;
            bool dogPet = dogCtl != null && dogCtl.IsBeingPet;
            if (dog != null && cocoPet && !cocoWasPet) Wiggle(dog);
            if (dogPet && !dogWasPet && !coco.IsKnockedOut)
            {
                Wiggle(coco.aiActor);
                PlayerController petter = dogCtl.m_pettingDoer != null ? dogCtl.m_pettingDoer : owner;
                coco.StartCoroutine(CatTricks.TimedSpeed(petter, 2f, 3f));
            }
            cocoWasPet = cocoPet;
            dogWasPet = dogPet;
        }

        private static void Wiggle(AIActor actor)
        {
            if (actor == null) return;
            PlutoVFX.Spawn(PlutoVFX.LoveBurst, actor.CenterPosition + new Vector2(0f, 0.6f));
            if (actor.aiAnimator != null) actor.aiAnimator.PlayForDuration("pet", 1.5f);
        }

        // ---------------------------------------------------------------- Squire
        private void UpdateJunkan(AIActor junkan)
        {
            SpeculativeRigidbody want = junkan != null && Alive(chaser) ? chaser.specRigidbody : null;
            if (aimedJunkan != junkan || want == null) ReleaseJunkan();
            if (want == null) return;
            junkan.OverrideTarget = want;
            aimedJunkan = junkan;
            aimedBody = want;
        }

        private void ReleaseJunkan()
        {
            if (aimedJunkan != null && aimedJunkan.OverrideTarget == aimedBody) aimedJunkan.OverrideTarget = null;
            aimedJunkan = null;
            aimedBody = null;
        }
    }
}
