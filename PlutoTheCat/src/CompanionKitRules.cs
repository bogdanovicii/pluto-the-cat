using System;
using System.Collections.Generic;

namespace PlutoTheCat
{
    /// <summary>Per-projectile accounting; cosmetic cooldowns never change the shield's budget.</summary>
    internal sealed class CocoShieldCharges
    {
        private readonly HashSet<object> blocked = new HashSet<object>();
        public int Remaining { get; private set; }
        public CocoShieldCharges(int count) { Refill(count); }
        public void Refill(int count) { Remaining = Math.Max(0, count); blocked.Clear(); }
        public void Regenerate(int maximum) { Remaining = Math.Min(maximum, Remaining + 1); }
        public void Clamp(int maximum) { Remaining = Math.Min(maximum, Remaining); }
        public void ForgetDestroyed(Predicate<object> destroyed) { blocked.RemoveWhere(destroyed); }
        public bool TryBlock(object projectile)
        {
            if (Remaining <= 0 || projectile == null || !blocked.Add(projectile)) return false;
            Remaining--;
            return true;
        }
    }

    /// <summary>Restore what preceded our write only while our last value still owns the field.</summary>
    internal sealed class CompanionOwnedValue<T>
    {
        private T original, written;
        private bool held;
        public bool CanWrite(T current) { return !held || EqualityComparer<T>.Default.Equals(current, written); }
        public void Record(T before, T after)
        {
            if (!held) { original = before; held = true; }
            written = after;
        }
        /// <summary>For fields a behaviour we added writes (not our own code): claim a change seen since the baseline.</summary>
        public void Observe(T baseline, T current)
        {
            if (!EqualityComparer<T>.Default.Equals(current, baseline)) Record(baseline, current);
        }
        public T Restore(T current)
        {
            T result = held && EqualityComparer<T>.Default.Equals(current, written) ? original : current;
            held = false;
            return result;
        }
    }

    internal static class CompanionKitRules
    {
        public const int MaxOwnerCrumbs = 12;
        public static bool CanDropCrumb(bool earned, bool hasOwner, int liveCount)
        { return earned && hasOwner && liveCount < MaxOwnerCrumbs; }
        public static bool CanCollectCrumb(bool infiniteAmmo, int ammo, int maximum)
        { return !infiniteAmmo && ammo < maximum; }

        // Relative bullet position and velocity against a moving candidate. Closest approach over
        // the next horizon seconds distinguishes incoming shots, misses and shots already receding.
        public static float ProjectileRisk(float x, float y, float vx, float vy, float horizon)
        {
            float speed2 = vx * vx + vy * vy;
            float t = speed2 < 0.0001f ? 0f : Math.Max(0f, Math.Min(horizon, -(x * vx + y * vy) / speed2));
            float dx = x + vx * t, dy = y + vy * t;
            float distance2 = dx * dx + dy * dy;
            if (distance2 >= 1.44f) return 0f;
            return (1.44f - distance2) * 12f / (0.25f + t);
        }
    }
}
