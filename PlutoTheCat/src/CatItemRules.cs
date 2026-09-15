using System;

namespace PlutoTheCat
{
    /// <summary>
    /// Timing and range decisions for the 2.17 cat items (Ball of Yarn, Catnip Pouch, Jingle Bell Collar, Hairball,
    /// Scratching Post), kept engine-free so they can be tested with Mono. The item classes only wire these to the game.
    /// </summary>
    internal static class CatItemRules
    {
        /// <summary>An enemy can be tangled again once its previous tangle (root + slow) has fully worn off.</summary>
        public static bool CanTangle(float sinceLastTangle, float rootSeconds, float slowSeconds)
        {
            return float.IsNaN(sinceLastTangle) || sinceLastTangle >= rootSeconds + slowSeconds;
        }

        public enum CatnipPhase { Zoomies, Catnap, Done }

        /// <summary>Catnip: zoomies first, then a short catnap, then back to normal.</summary>
        public static CatnipPhase Catnip(float elapsed, float zoomiesSeconds, float catnapSeconds)
        {
            if (float.IsNaN(elapsed) || elapsed < 0f) return CatnipPhase.Done;
            if (elapsed < zoomiesSeconds) return CatnipPhase.Zoomies;
            if (elapsed < zoomiesSeconds + catnapSeconds) return CatnipPhase.Catnap;
            return CatnipPhase.Done;
        }

        /// <summary>The bell jingles on a roll only when its cooldown has passed (the first roll always jingles).</summary>
        public static bool BellReady(float now, float lastJingle, float cooldownSeconds)
        {
            if (float.IsNaN(lastJingle) || float.IsNegativeInfinity(lastJingle)) return true;
            return now - lastJingle >= cooldownSeconds;
        }

        /// <summary>True when a point at squared distance sqrDistance is inside a circle of the given radius (edge counts).</summary>
        public static bool Inside(float sqrDistance, float radius)
        {
            return radius > 0f && sqrDistance <= radius * radius;
        }

        /// <summary>
        /// Speed an enemy bullet should have inside the hairball's fur cloud: its own speed times the factor, never below a
        /// crawl so the bullet still leaves the cloud. A bullet already slowed keeps its lower speed.
        /// </summary>
        public static float CloudBulletSpeed(float originalSpeed, float currentSpeed, float factor)
        {
            const float Crawl = 1f;
            float target = Math.Max(Crawl, originalSpeed * Clamp01(factor));
            if (originalSpeed <= Crawl) target = originalSpeed;
            return Math.Min(currentSpeed, target);
        }

        /// <summary>The cloud thins out in its last second: the drawn radius shrinks to 60 % as it ends.</summary>
        public static float CloudVisualScale(float timeLeft)
        {
            if (float.IsNaN(timeLeft) || timeLeft <= 0f) return 0f;
            return timeLeft >= 1f ? 1f : 0.6f + 0.4f * timeLeft;
        }

        /// <summary>Scratching Post: the bonus is on while Pluto stands within the radius of a standing post.</summary>
        public static bool Sharpened(bool postStanding, float sqrDistance, float radius)
        {
            return postStanding && Inside(sqrDistance, radius);
        }

        private static float Clamp01(float v)
        {
            if (float.IsNaN(v)) return 0f;
            return v < 0f ? 0f : (v > 1f ? 1f : v);
        }
    }
}
