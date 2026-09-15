using System;

namespace PlutoTheCat
{
    /// <summary>Nine Lives wording and counts, kept engine-free so they can be tested with Mono.</summary>
    internal static class NineLivesRules
    {
        public const int LastLife = 9;
        private static readonly string[] Ordinal = { "", "first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth" };
        private static readonly string[] Count = { "No", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight" };

        public static int ClampLife(int life) { return Math.Max(1, Math.Min(LastLife, life)); }
        public static int SavesLeft(int life) { return LastLife - ClampLife(life); }

        /// <summary>"Seventh Life": the item subtitle, shown in the pickup notice and the Ammonomicon.</summary>
        public static string Title(int life) { return Capital(Ordinal[ClampLife(life)]) + " Life"; }

        /// <summary>"Seventh life. Two to spare." The ninth keeps its original line.</summary>
        public static string Status(int life)
        {
            int saves = SavesLeft(life);
            string head = Capital(Ordinal[ClampLife(life)]) + " life.";
            return saves == 0 ? head + " The last one." : head + " " + Count[saves] + " to spare.";
        }

        private static string Capital(string word) { return char.ToUpper(word[0]) + word.Substring(1); }
    }

    /// <summary>
    /// Timing for Puffed Up's samurai cue. The kimono hides the fur layer, so the anger shows as a red
    /// flash on the hit, a slow red pulse while it lasts, and anger marks repeating over his head.
    /// </summary>
    internal static class AngerCueRules
    {
        public const float MarkInterval = 0.9f;
        public const float FlashAlpha = 0.55f, FlashSeconds = 0.2f;
        public const float PulseMin = 0.18f, PulseMax = 0.32f;
        public const float FadeSeconds = 0.3f;
        private const float PulseRate = 15.7f;   // radians per second: 2.5 pulses a second

        public static float TintAlpha(float elapsed, float timeLeft)
        {
            if (float.IsNaN(elapsed) || float.IsNaN(timeLeft) || elapsed < 0f || timeLeft <= 0f) return 0f;
            float pulse = PulseMin + (PulseMax - PulseMin) * (0.5f + 0.5f * (float)Math.Cos(elapsed * PulseRate));
            float alpha = elapsed < FlashSeconds ? Math.Max(pulse, FlashAlpha * (1f - elapsed / FlashSeconds)) : pulse;
            return alpha * Math.Min(1f, timeLeft / FadeSeconds);
        }

        /// <summary>Counts the mark timer down; a long frame yields one mark and a fresh interval, never a burst.</summary>
        public static float NextMarkTimer(float timer, float dt, out bool spawn)
        {
            timer -= dt;
            spawn = timer <= 0f;
            if (!spawn) return timer;
            timer += MarkInterval;
            return timer > 0f ? timer : MarkInterval;
        }
    }
}
