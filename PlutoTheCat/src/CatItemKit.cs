using System.Collections.Generic;
using UnityEngine;
using Dungeonator;

namespace PlutoTheCat
{
    /// <summary>Engine helpers shared by the 2.17 cat items (decisions live in CatItemRules).</summary>
    public static class CatItemKit
    {
        /// <summary>A living hostile enemy. Charmed enemies target enemies without targeting players and are excluded.</summary>
        public static bool ValidEnemy(AIActor enemy)
        {
            return enemy != null
                && enemy.healthHaver != null
                && !enemy.healthHaver.IsDead
                && !enemy.IsHarmlessEnemy
                && (!enemy.CanTargetEnemies || enemy.CanTargetPlayers);
        }

        /// <summary>Inclusive world-space AABB test against the enemy's actual hitbox.</summary>
        public static bool HitboxOverlaps(AIActor enemy, Vector2 min, Vector2 max)
        {
            if (enemy == null || enemy.specRigidbody == null || enemy.specRigidbody.HitboxPixelCollider == null) return false;
            PixelCollider hitbox = enemy.specRigidbody.HitboxPixelCollider;
            Vector2 eMin = hitbox.UnitBottomLeft;
            Vector2 eMax = hitbox.UnitTopRight;
            return eMax.x >= min.x && eMin.x <= max.x
                && eMax.y >= min.y && eMin.y <= max.y;
        }

        /// <summary>Enemy bullets are the ones not owned by a player (same test as SilencerInstance).</summary>
        public static bool IsEnemyBullet(Projectile p)
        {
            return p != null && p.isActiveAndEnabled && !(p.Owner is PlayerController);
        }

        /// <summary>Living non-boss and boss enemies of the room around a point, within a radius.</summary>
        public static List<AIActor> EnemiesNear(Vector2 center, float radius)
        {
            List<AIActor> result = new List<AIActor>();
            RoomHandler room = center.GetAbsoluteRoom();
            List<AIActor> enemies = room != null ? room.GetActiveEnemies(RoomHandler.ActiveEnemyType.All) : null;
            if (enemies == null) return result;
            for (int i = 0; i < enemies.Count; i++)
            {
                AIActor e = enemies[i];
                if (e == null || e.healthHaver == null || e.healthHaver.IsDead) continue;
                if (!CatItemRules.Inside((e.CenterPosition - center).sqrMagnitude, radius)) continue;
                result.Add(e);
            }
            return result;
        }

        /// <summary>Stuns a non-boss enemy (BehaviorSpeculator.Stun already ignores bosses and stun-immune enemies).</summary>
        public static void Stun(AIActor enemy, float seconds)
        {
            if (enemy == null || seconds <= 0f || enemy.behaviorSpeculator == null) return;
            if (enemy.healthHaver != null && enemy.healthHaver.IsBoss) return;
            enemy.behaviorSpeculator.Stun(seconds, true);
        }

        /// <summary>Slows an enemy's movement with the vanilla speed effect (refreshes rather than stacks).</summary>
        public static void Slow(AIActor enemy, float seconds, float multiplier, string id)
        {
            if (enemy == null || seconds <= 0f || enemy.healthHaver == null || enemy.healthHaver.IsDead) return;
            GameActorSpeedEffect slow = new GameActorSpeedEffect
            {
                SpeedMultiplier = multiplier,
                CooldownMultiplier = 1f,
                AffectsPlayers = false,
                AffectsEnemies = true,
                effectIdentifier = id,
                stackMode = GameActorEffect.EffectStackingMode.Refresh,
                duration = seconds,
            };
            enemy.ApplyEffect(slow, 1f, null);
        }

        public static StatModifier Mod(PlayerStats.StatType stat, StatModifier.ModifyMethod method, float amount)
        {
            return new StatModifier { statToBoost = stat, modifyType = method, amount = amount, ignoredForSaveData = true };
        }
    }
}
