using System;

namespace PlutoTheCat
{
    /// <summary>Engine-free timing, geometry and duration decisions shared by the 2.19 cat set.</summary>
    internal static class CatSetRules
    {
        private const double RadiusSquaredEpsilon = 0.000001;
        private const double AngleDegreesEpsilon = 0.0001;

        public static bool RollFlinch(float roll, float chance)
        {
            return !float.IsNaN(roll) && roll >= 0f && roll < Math.Max(0f, Math.Min(1f, chance));
        }

        public static float DistractSeconds(bool boss, float normalSeconds, float bossSeconds)
        {
            return Math.Max(0f, boss ? bossSeconds : normalSeconds);
        }

        public static bool StreamerAlive(float now, float born, float seconds, int hits, int maxHits)
        {
            return hits < maxHits && now - born < seconds;
        }

        public static bool ConeReady(float now, float lastBlock, float cooldown)
        {
            return now - lastBlock >= cooldown;
        }

        public static bool InCone(float dx, float dy, float aimX, float aimY, float radius, float degrees)
        {
            if (float.IsNaN(dx) || float.IsNaN(dy) || float.IsNaN(aimX) || float.IsNaN(aimY)
                || float.IsNaN(radius) || float.IsNaN(degrees)
                || radius <= 0f || degrees <= 0f)
                return false;

            double distanceSquared = dx * dx + dy * dy;
            double aimSquared = aimX * aimX + aimY * aimY;
            double radiusSquared = radius * radius;
            if (distanceSquared <= 0.0 || aimSquared <= 0.0 || distanceSquared > radiusSquared + RadiusSquaredEpsilon)
                return false;

            double dot = (dx * aimX + dy * aimY) / Math.Sqrt(distanceSquared * aimSquared);
            dot = Math.Max(-1.0, Math.Min(1.0, dot));
            return Math.Acos(dot) * 180.0 / Math.PI <= degrees * 0.5 + AngleDegreesEpsilon;
        }

        public static float ShardAngle(int index, int count)
        {
            return count <= 0 ? 0f : 360f * index / count;
        }

        public static float ExtendDuration(float duration, float bonus)
        {
            return Math.Max(0f, duration) + Math.Max(0f, bonus);
        }

        public static float ExtendRemaining(float remaining, float bonus, bool active)
        {
            return active ? Math.Max(0f, remaining) + Math.Max(0f, bonus) : remaining;
        }
    }
}
