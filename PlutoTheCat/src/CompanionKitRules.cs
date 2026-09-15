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

        // ------------------------------------------------------------ decoy run
        // A decoy Coco always runs a "leg" to a spot at least DecoyMinStep away (standing still is never a choice),
        // prefers legs that avoid incoming bullets (threat, from ProjectileRisk) and stays within reach of the owner.
        public const int DecoyCandidateCount = 9;           // eight directions around Coco plus one toward the owner
        public const float DecoyMinStep = 1.5f;
        public const float DecoyLeash = 8f;                 // past this he may only run back toward the owner
        public const float DecoyComfort = 5f;               // beyond this a leg costs more the further it strays
        public const float DecoyArrive = 0.6f;
        public const float DecoyMaxLegSeconds = 1.4f;
        public const float DecoySwerveMargin = 6f;

        /// <summary>Eight points on a ring of the given radius (rotated by spin radians) and one leg toward the owner.</summary>
        public static void DecoyCandidates(float meX, float meY, float ownerX, float ownerY, float spin, float radius, float[] xs, float[] ys)
        {
            for (int i = 0; i < 8; i++)
            {
                double angle = spin + i * Math.PI / 4.0;
                xs[i] = meX + (float)Math.Cos(angle) * radius;
                ys[i] = meY + (float)Math.Sin(angle) * radius;
            }
            float dx = ownerX - meX, dy = ownerY - meY;
            float d = (float)Math.Sqrt(dx * dx + dy * dy);
            float step = Math.Min(radius, d);
            xs[8] = d < 0.001f ? meX : meX + dx / d * step;
            ys[8] = d < 0.001f ? meY : meY + dy / d * step;
        }

        /// <summary>Lower is better; float.MaxValue when the leg is not allowed (too short, or strays past the leash).</summary>
        public static float DecoyLegScore(float meX, float meY, float x, float y, float ownerX, float ownerY, float threat, float jitter)
        {
            if (Distance(meX, meY, x, y) < DecoyMinStep) return float.MaxValue;
            float ownerDistance = Distance(x, y, ownerX, ownerY);
            if (ownerDistance > DecoyLeash && ownerDistance >= Distance(meX, meY, ownerX, ownerY)) return float.MaxValue;
            return threat + Math.Max(0f, ownerDistance - DecoyComfort) * 3f + jitter;
        }

        /// <summary>Index of the best allowed leg, or -1 when none is allowed.</summary>
        public static int PickDecoyLeg(float meX, float meY, float ownerX, float ownerY, float[] xs, float[] ys, float[] threat, float[] jitter)
        {
            int best = -1;
            float bestScore = float.MaxValue;
            for (int i = 0; i < xs.Length; i++)
            {
                float score = DecoyLegScore(meX, meY, xs[i], ys[i], ownerX, ownerY, threat[i], jitter[i]);
                if (score < bestScore) { bestScore = score; best = i; }
            }
            return best;
        }

        /// <summary>
        /// Whether to start a new leg now: none yet, arrived, stalled (moved less than 0.05 since the last check),
        /// ran too long, or the current leg's threat is clearly worse than the best alternative.
        /// </summary>
        public static bool NeedsNewDecoyLeg(bool hasLeg, float distanceToLeg, float legAge, float movedSinceCheck, float legThreat, float bestAlternative)
        {
            if (!hasLeg || distanceToLeg < DecoyArrive || legAge > DecoyMaxLegSeconds) return true;
            if (legAge > 0.3f && movedSinceCheck < 0.05f) return true;
            return legThreat > bestAlternative + DecoySwerveMargin;
        }

        /// <summary>Squire helmet clip prefix: none without Squire, pot helmet below Holy Knight, gold helmet from Holy Knight (6) up.</summary>
        public static string CocoHelmetPrefix(bool squire, int junkanForm)
        {
            if (!squire) return "";
            return junkanForm >= 6 ? "knight_" : "squire_";
        }

        private static float Distance(float ax, float ay, float bx, float by)
        {
            float dx = ax - bx, dy = ay - by;
            return (float)Math.Sqrt(dx * dx + dy * dy);
        }
    }
}
