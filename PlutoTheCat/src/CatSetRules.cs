using System;

namespace PlutoTheCat
{
    /// <summary>Engine-free timing, geometry and duration decisions shared by the 2.19 cat set.</summary>
    internal static class CatSetRules
    {
        private const double RadiusSquaredRelativeEpsilon = 0.000001;
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

        /// <summary>
        /// Separating-axis test between the streamer (an oriented rectangle) and an enemy hitbox AABB.
        /// The strip axis may be scaled; length and width are full dimensions. Touching counts as overlap.
        /// </summary>
        public static bool StreamerStripOverlapsAabb(float centerX, float centerY, float axisX, float axisY,
            float length, float width, float minX, float minY, float maxX, float maxY)
        {
            if (!Finite(centerX) || !Finite(centerY) || !Finite(axisX) || !Finite(axisY)
                || !Finite(length) || !Finite(width) || !Finite(minX) || !Finite(minY)
                || !Finite(maxX) || !Finite(maxY) || length <= 0f || width <= 0f
                || minX > maxX || minY > maxY)
                return false;

            double axisSquared = (double)axisX * axisX + (double)axisY * axisY;
            if (axisSquared <= 0.0) return false;
            double inverseAxisLength = 1.0 / Math.Sqrt(axisSquared);
            double ux = axisX * inverseAxisLength;
            double uy = axisY * inverseAxisLength;
            double vx = -uy;
            double vy = ux;

            double boxCenterX = ((double)minX + maxX) * 0.5;
            double boxCenterY = ((double)minY + maxY) * 0.5;
            double boxHalfX = ((double)maxX - minX) * 0.5;
            double boxHalfY = ((double)maxY - minY) * 0.5;
            double dx = boxCenterX - centerX;
            double dy = boxCenterY - centerY;
            double halfLength = length * 0.5;
            double halfWidth = width * 0.5;
            const double epsilon = 0.0000001;

            // AABB world X/Y axes.
            if (Math.Abs(dx) > boxHalfX + halfLength * Math.Abs(ux) + halfWidth * Math.Abs(vx) + epsilon) return false;
            if (Math.Abs(dy) > boxHalfY + halfLength * Math.Abs(uy) + halfWidth * Math.Abs(vy) + epsilon) return false;
            // Streamer longitudinal/normal axes.
            if (Math.Abs(dx * ux + dy * uy) > halfLength + boxHalfX * Math.Abs(ux) + boxHalfY * Math.Abs(uy) + epsilon) return false;
            if (Math.Abs(dx * vx + dy * vy) > halfWidth + boxHalfX * Math.Abs(vx) + boxHalfY * Math.Abs(vy) + epsilon) return false;
            return true;
        }

        private static bool Finite(float value)
        {
            return !float.IsNaN(value) && !float.IsInfinity(value);
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
            double radiusTolerance = RadiusSquaredRelativeEpsilon * Math.Max(1.0, radiusSquared);
            if (distanceSquared <= 0.0 || aimSquared <= 0.0 || distanceSquared > radiusSquared + radiusTolerance)
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
