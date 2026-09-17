using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Dungeonator;
using Gungeon;
using HarmonyLib;
using Alexandria.ItemAPI;
using Alexandria.Misc;

namespace PlutoTheCat
{
    /// <summary>A charged, piercing lure. Each gun owns at most one lure until it returns or is cleaned up.</summary>
    public class FeatherTeaserGun : GunBehaviour
    {
        public const string ID = "pluto:feather_teaser";
        private const string IdleClip = "pluto_feather_teaser_idle";
        private const string ChargeClip = "pluto_feather_teaser_charge";
        private const string FireClip = "pluto_feather_teaser_fire";
        private const string EmptyClip = "pluto_feather_teaser_empty";
        private const string ReturnClip = "pluto_feather_teaser_return";
        private FeatherLure activeLure;
        private bool ownsGunState, previousAnimations;
        private float previousReloadTime;
        private static bool guardsInstalled;

        public static void Add()
        {
            Gun gun = ETGMod.Databases.Items.NewGun("Feather Teaser", "pluto_feather_teaser");
            Game.Items.Rename("outdated_gun_mods:feather_teaser", ID);
            gun.gameObject.AddComponent<FeatherTeaserGun>();
            gun.SetShortDescription("Definitely A Bird");
            gun.SetLongDescription("Charge to cast a feather lure that flies out and returns. Enemies it catches " +
                "follow the feather; bosses are briefly slowed.\n\n" +
                "Every cat alive knows the feather is not real. Every cat alive chases it anyway. " +
                "Gundead, it turns out, are no smarter.");
            gun.SetupSprite(null, "pluto_feather_teaser_idle_001", 10);
            // GunExt combines gun.name + '_' + the suffix and loads the numbered resource frames.
            gun.idleAnimation = gun.UpdateAnimation("idle", null, true);
            gun.chargeAnimation = gun.UpdateAnimation("charge", null, true);
            gun.shootAnimation = gun.UpdateAnimation("fire", null, false);
            gun.emptyAnimation = gun.UpdateAnimation("empty", null, true);
            gun.UpdateAnimation("return", null, true);
            gun.reloadAnimation = IdleClip;
            gun.SetAnimationFPS(ChargeClip, 10);
            gun.SetAnimationFPS(FireClip, 10);
            gun.AddProjectileModuleFrom("klobb", true, false);
            gun.gunSwitchGroup = (PickupObjectDatabase.GetById(31) as Gun).gunSwitchGroup;
            gun.DefaultModule.shootStyle = ProjectileModule.ShootStyle.Charged;
            gun.DefaultModule.sequenceStyle = ProjectileModule.ProjectileSequenceStyle.Ordered;
            gun.DefaultModule.ammoCost = 1;
            gun.DefaultModule.cooldownTime = 0.1f;
            gun.DefaultModule.angleVariance = 0f;
            gun.DefaultModule.numberOfShotsInClip = PlutoConfig.FeatherClip;
            gun.reloadTime = PlutoConfig.FeatherReloadSeconds;
            gun.SetBaseMaxAmmo(120);
            gun.gunClass = GunClass.CHARGE;
            gun.gunHandedness = GunHandedness.OneHanded;
            gun.barrelOffset.transform.localPosition = new Vector3(
                WeaponLayout.FEATHER_TEASER_MUZZLE_X / 16f, WeaponLayout.FEATHER_TEASER_MUZZLE_Y / 16f, 0f);
            gun.quality = PickupObject.ItemQuality.B;

            Projectile lure = ProjectileUtility.SetupProjectile(56);
            lure.gameObject.name = "pluto_feather_lure_projectile";
            lure.baseData.damage = PlutoConfig.FeatherDamage;
            lure.baseData.speed = FeatherLure.Speed;
            lure.baseData.range = 1000f;
            lure.shouldRotate = false;
            lure.SetProjectileSpriteRight("pluto_feather_lure_001", 12, 12, false, tk2dBaseSprite.Anchor.MiddleCenter, 8, 8);
            lure.ManualControl = true;
            lure.SkipDistanceElapsedCheck = true;
            // Travel and damage are owned below. Disabling engine collisions prevents a second damage path.
            lure.specRigidbody.CollideWithOthers = false;
            lure.specRigidbody.CollideWithTileMap = false;
            lure.gameObject.AddComponent<FeatherLure>();
            gun.DefaultModule.projectiles[0] = lure;
            gun.DefaultModule.chargeProjectiles = new List<ProjectileModule.ChargeProjectile>
            {
                new ProjectileModule.ChargeProjectile { Projectile = lure, ChargeTime = PlutoConfig.FeatherChargeSeconds }
            };
            InstallGuards();
            ETGMod.Databases.Items.Add(gun, null, "ANY");
        }

        private static void InstallGuards()
        {
            if (guardsInstalled) return;
            Harmony harmony = new Harmony(Plugin.GUID + ".feather_teaser");
            harmony.Patch(AccessTools.Method(typeof(Gun), "Attack", new[] { typeof(ProjectileData), typeof(GameObject) }),
                prefix: new HarmonyMethod(typeof(FeatherTeaserGun), "GuardAttack"));
            harmony.Patch(AccessTools.Method(typeof(Gun), "ContinueAttack", new[] { typeof(bool), typeof(ProjectileData) }),
                prefix: new HarmonyMethod(typeof(FeatherTeaserGun), "GuardContinue"));
            harmony.Patch(AccessTools.Method(typeof(Gun), "CeaseAttack", new[] { typeof(bool), typeof(ProjectileData) }),
                prefix: new HarmonyMethod(typeof(FeatherTeaserGun), "GuardCease"));
            // ForceImmediateReload (including inventory reloads) bypasses Reload; guard the common completion path.
            harmony.Patch(AccessTools.Method(typeof(Gun), "FinishReload", new[] { typeof(bool), typeof(bool), typeof(bool) }),
                prefix: new HarmonyMethod(typeof(FeatherTeaserGun), "GuardFinishReload"));
            guardsInstalled = true;
        }

        private static bool LureOut(Gun target)
        {
            FeatherTeaserGun teaser = target != null ? target.GetComponent<FeatherTeaserGun>() : null;
            return teaser != null && teaser.ownsGunState;
        }

        private static bool GuardAttack(Gun __instance, ref Gun.AttackResult __result)
        {
            if (!LureOut(__instance)) return true;
            __result = Gun.AttackResult.Fail;
            return false;
        }

        private static bool GuardContinue(Gun __instance, ref bool __result)
        {
            if (!LureOut(__instance)) return true;
            __result = false;
            return false;
        }

        private static void GuardCease(Gun __instance, ref bool canAttack)
        {
            if (LureOut(__instance)) canAttack = false;
        }

        private static bool GuardFinishReload(Gun __instance) { return !LureOut(__instance); }

        public override void PostProcessProjectile(Projectile projectile)
        {
            base.PostProcessProjectile(projectile);
            if (projectile == null) return;
            // Multi-projectile passives must not create a second lure during the same charged shot.
            if (ownsGunState) { projectile.DieInAir(false, true, true, false); return; }
            PlayerController owner = projectile.Owner as PlayerController;
            if (owner == null || gun == null) { projectile.DieInAir(false, true, true, false); return; }
            activeLure = projectile.GetComponent<FeatherLure>();
            if (activeLure == null) activeLure = projectile.gameObject.AddComponent<FeatherLure>();
            previousReloadTime = gun.reloadTime;
            previousAnimations = gun.OverrideAnimations;
            ownsGunState = true;
            // Negative reloadTime is the vanilla Reload() veto. ClipShotsRemaining is left to the firing code.
            gun.reloadTime = -1f;
            activeLure.Bind(this, projectile, owner);
        }

        public override void Update()
        {
            base.Update();
            if (!ownsGunState) return;
            if (activeLure == null) { RestoreGunState(); return; }
            if (gun == null || activeLure.Owner == null || activeLure.Owner.CurrentGun != gun)
                CancelLure();
        }

        internal void ShowLure(bool returning)
        {
            if (gun == null || !ownsGunState) return;
            gun.OverrideAnimations = true;
            string clip = returning ? ReturnClip : EmptyClip;
            if (gun.spriteAnimator != null && !gun.spriteAnimator.IsPlaying(clip)) gun.spriteAnimator.Play(clip);
        }

        internal void LureFinished(FeatherLure lure)
        {
            if (activeLure != lure) return;
            activeLure = null;
            RestoreGunState();
        }

        private void RestoreGunState()
        {
            if (!ownsGunState) return;
            ownsGunState = false;
            if (gun != null)
            {
                if (gun.reloadTime == -1f) gun.reloadTime = previousReloadTime;
                if (gun.OverrideAnimations) gun.OverrideAnimations = previousAnimations;
                if (!gun.OverrideAnimations && gun.spriteAnimator != null) gun.spriteAnimator.Play(IdleClip);
                // Start the real 0.4 s reload only now. A larger configured clip keeps its unused shots.
                if (gun.CurrentOwner != null && gun.CurrentOwner.CurrentGun == gun && gun.ClipShotsRemaining == 0)
                    gun.Reload();
            }
            Plugin.Log("feather teaser: cleanup restored gun; lure gate released");
        }

        private void CancelLure()
        {
            if (activeLure != null) activeLure.Finish();
            activeLure = null;
            RestoreGunState();
        }

        public override void OnSwitchedAwayFrom(GameActor owner, GunInventory inventory, Gun newGun, bool isNewGun)
        {
            CancelLure();
            base.OnSwitchedAwayFrom(owner, inventory, newGun, isNewGun);
        }

        public override void OnDropped() { CancelLure(); base.OnDropped(); }
        public override void OnDestroy() { CancelLure(); base.OnDestroy(); }
        private void OnDisable() { CancelLure(); }

        /// <summary>Manual, substepped travel gives one hit per enemy per leg, including large hitboxes.</summary>
        public class FeatherLure : MonoBehaviour
        {
            internal const float Speed = 18f;
            private const float MaxStep = 0.125f;
            private FeatherTeaserGun teaser;
            private Projectile projectile;
            public PlayerController Owner { get; private set; }
            private RoomHandler room;
            private Vector2 origin, position, direction;
            private float distance, age, frameTimer;
            private int[] sprites;
            private int frame;
            private bool returning, finished;
            private readonly HashSet<AIActor> outwardHits = new HashSet<AIActor>();
            private readonly HashSet<AIActor> returnHits = new HashSet<AIActor>();
            private readonly Dictionary<AIActor, Distraction> distractions = new Dictionary<AIActor, Distraction>();

            private class Distraction
            {
                public AIActor enemy;
                public bool previousOverride;
                public Vector2 previousVelocity, appliedVelocity;
                public Coroutine routine;
            }

            internal void Bind(FeatherTeaserGun source, Projectile p, PlayerController owner)
            {
                teaser = source;
                projectile = p;
                Owner = owner;
                room = owner.CurrentRoom;
                origin = p.specRigidbody.UnitCenter;
                position = origin;
                direction = p.Direction.sqrMagnitude > 0.0001f ? p.Direction.normalized : Vector2.right;
                p.ManualControl = true;
                p.SkipDistanceElapsedCheck = true;
                p.specRigidbody.CollideWithOthers = false;
                p.specRigidbody.CollideWithTileMap = false;
                p.specRigidbody.Velocity = Vector2.zero;
            }

            private void Start()
            {
                if (projectile == null || teaser == null) { Finish(); return; }
                if (projectile.sprite != null && projectile.sprite.Collection != null)
                    sprites = new[] { projectile.sprite.Collection.GetSpriteIdByName("pluto_feather_lure_001", -1),
                        projectile.sprite.Collection.GetSpriteIdByName("pluto_feather_lure_002", -1) };
                Plugin.Log("feather teaser: outward leg, range " + PlutoConfig.FeatherRange);
            }

            private bool OwnerValid()
            {
                return Owner != null && Owner.healthHaver != null && !Owner.healthHaver.IsDead
                    && teaser != null && teaser.gun != null && Owner.CurrentGun == teaser.gun
                    && Owner.CurrentRoom == room && room != null;
            }

            private void Update()
            {
                if (finished) return;
                if (projectile == null || projectile.specRigidbody == null || !OwnerValid()) { Finish(); return; }
                float dt = BraveTime.DeltaTime;
                age += dt;
                if (age > 10f) { Finish(); return; } // A teleported owner cannot leave a permanent lure behind.
                projectile.specRigidbody.Velocity = Vector2.zero;
                float travel = Speed * dt;
                while (travel > 0f && !finished)
                {
                    // Keep subpixel travel here: rigidbody hitbox centers are rounded to the physics grid.
                    Vector2 target = returning ? Owner.CenterPosition : origin + direction * PlutoConfig.FeatherRange;
                    Vector2 delta = target - position;
                    float step = Mathf.Min(MaxStep, Mathf.Min(travel, delta.magnitude));
                    Vector2 move = delta.normalized * step;
                    position += move;
                    transform.position += (Vector3)move;
                    projectile.specRigidbody.Reinitialize();
                    ScanHits();
                    travel -= step;
                    if (!returning) distance += step;
                    float remaining = (target - position).magnitude;
                    if (returning && remaining <= 0.001f) { Finish(); return; }
                    if (!returning && (distance >= PlutoConfig.FeatherRange - 0.001f || remaining <= 0.001f))
                    {
                        returning = true;
                        Plugin.Log("feather teaser: return leg");
                    }
                    if (step <= 0f) break;
                }
                if (finished) return;
                // Let the single fire frame show briefly before the rod becomes empty.
                if (age >= 0.1f) teaser.ShowLure(returning);
                frameTimer += dt;
                if (frameTimer >= 0.08f && sprites != null && sprites[0] >= 0 && sprites[1] >= 0 && projectile.sprite != null)
                {
                    frameTimer = 0f;
                    frame = 1 - frame;
                    projectile.sprite.SetSprite(sprites[frame]);
                }
            }

            private void ScanHits()
            {
                List<AIActor> active = room.GetActiveEnemies(RoomHandler.ActiveEnemyType.All);
                PixelCollider hitbox = projectile.specRigidbody.HitboxPixelCollider;
                if (active == null || hitbox == null) return;
                AIActor[] enemies = active.ToArray();
                HashSet<AIActor> hits = returning ? returnHits : outwardHits;
                for (int i = 0; i < enemies.Length; i++)
                {
                    AIActor enemy = enemies[i];
                    // ValidEnemy excludes dead, IsHarmlessEnemy and charmed actors on both legs.
                    if (!CatItemKit.ValidEnemy(enemy) || hits.Contains(enemy)) continue;
                    if (!CatItemKit.HitboxOverlaps(enemy, hitbox.UnitBottomLeft, hitbox.UnitTopRight)) continue;
                    hits.Add(enemy);
                    enemy.healthHaver.ApplyDamage(PlutoConfig.FeatherDamage, direction, "Feather Teaser",
                        CoreDamageTypes.None, DamageCategory.Normal, false, enemy.specRigidbody.HitboxPixelCollider, false);
                    if (!CatItemKit.ValidEnemy(enemy)) continue;
                    if (enemy.healthHaver.IsBoss)
                    {
                        CatItemKit.Slow(enemy, PlutoConfig.FeatherBossSlowSeconds, 0.5f, "pluto_feather_slow");
                        Plugin.Log("feather teaser: boss slow for " + PlutoConfig.FeatherBossSlowSeconds + " s");
                    }
                    else BeginDistraction(enemy);
                }
            }

            private void BeginDistraction(AIActor enemy)
            {
                if (distractions.ContainsKey(enemy) || enemy.behaviorSpeculator == null) return;
                Distraction state = new Distraction { enemy = enemy, previousOverride = enemy.BehaviorOverridesVelocity,
                    previousVelocity = enemy.BehaviorVelocity };
                enemy.behaviorSpeculator.Interrupt();
                state.appliedVelocity = ChaseVelocity(enemy);
                enemy.BehaviorOverridesVelocity = true;
                enemy.BehaviorVelocity = state.appliedVelocity;
                distractions.Add(enemy, state);
                state.routine = StartCoroutine(Distract(state));
                Plugin.Log("feather teaser: distract for " + PlutoConfig.FeatherDistractSeconds + " s");
                if (Owner.PlayerHasActiveSynergy(PlutoSynergies.Playtime))
                {
                    BallOfYarnItem.ApplyTangle(enemy);
                    Plugin.Log("feather teaser: Playtime shared yarn tangle");
                }
            }

            private Vector2 ChaseVelocity(AIActor enemy)
            {
                Vector2 delta = projectile.specRigidbody.UnitCenter - enemy.CenterPosition;
                return delta.sqrMagnitude < 0.0625f ? Vector2.zero : delta.normalized * enemy.MovementSpeed;
            }

            private IEnumerator Distract(Distraction state)
            {
                float elapsed = 0f;
                while (elapsed < PlutoConfig.FeatherDistractSeconds)
                {
                    yield return null;
                    AIActor enemy = state.enemy;
                    List<AIActor> enemies = room != null ? room.GetActiveEnemies(RoomHandler.ActiveEnemyType.All) : null;
                    if (finished || projectile == null || !OwnerValid() || !CatItemKit.ValidEnemy(enemy)
                        || enemy.healthHaver.IsBoss || enemies == null || !enemies.Contains(enemy)) break;
                    // If another behavior took the velocity, relinquish it without overwriting its state.
                    if (!OwnsVelocity(state)) break;
                    state.appliedVelocity = ChaseVelocity(enemy);
                    enemy.BehaviorVelocity = state.appliedVelocity;
                    elapsed += BraveTime.DeltaTime;
                }
                RestoreDistraction(state, false);
            }

            private static bool OwnsVelocity(Distraction state)
            {
                return state.enemy != null && state.enemy.BehaviorOverridesVelocity
                    && state.enemy.BehaviorVelocity.Equals(state.appliedVelocity);
            }

            private void RestoreDistraction(Distraction state, bool stopRoutine)
            {
                if (stopRoutine && state.routine != null) StopCoroutine(state.routine);
                state.routine = null;
                if (OwnsVelocity(state))
                {
                    state.enemy.BehaviorOverridesVelocity = state.previousOverride;
                    state.enemy.BehaviorVelocity = state.previousVelocity;
                }
                distractions.Remove(state.enemy);
                Plugin.Log("feather teaser: cleanup distraction");
            }

            internal void Finish()
            {
                if (finished) return;
                finished = true;
                List<Distraction> states = new List<Distraction>(distractions.Values);
                for (int i = 0; i < states.Count; i++) RestoreDistraction(states[i], true);
                if (teaser != null) teaser.LureFinished(this);
                if (projectile != null) projectile.DieInAir(false, true, true, false);
            }

            private void OnDestroy() { Finish(); }
            private void OnDisable() { Finish(); }
        }
    }
}
