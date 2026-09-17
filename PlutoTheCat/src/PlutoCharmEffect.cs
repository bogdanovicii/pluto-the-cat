using UnityEngine;

namespace PlutoTheCat
{
    /// <summary>
    /// A charm that works on every enemy, bosses included.
    ///
    /// GameActor.ApplyEffect silently drops any effect whose runtime type is
    /// GameActorCharmEffect when the target has a boss health bar. This class
    /// therefore derives from GameActorEffect directly and replicates the four
    /// lines that make vanilla charm work: the enemy targets other enemies and
    /// stops targeting players until the effect expires.
    /// </summary>
    public class PlutoCharmEffect : GameActorEffect
    {
        public const float VulnerabilityMultiplier = 1.2f;

        public static PlutoCharmEffect Create(float durationSeconds)
        {
            // Borrow the vanilla Charming Rounds visuals (pink tint + heart VFX).
            GameActorCharmEffect vanilla = null;
            PickupObject charmingRounds = PickupObjectDatabase.GetById(527);
            if (charmingRounds != null)
            {
                BulletStatusEffectItem bsi = charmingRounds.GetComponent<BulletStatusEffectItem>();
                if (bsi != null) vanilla = bsi.CharmModifierEffect;
            }

            PlutoCharmEffect effect = new PlutoCharmEffect
            {
                effectIdentifier = "pluto_love",
                resistanceType = EffectResistanceType.None, // not the "charm" identifier, so charm resistance is skipped
                AffectsEnemies = true,
                AffectsPlayers = false,
                stackMode = EffectStackingMode.Refresh,
                duration = durationSeconds,
                maxStackedDuration = -1f,
                AppliesTint = true,
                TintColor = new Color(1f, 0.55f, 0.75f, 0.6f),
                AppliesDeathTint = false,
                AppliesOutlineTint = false,
                PlaysVFXOnActor = true,
            };
            if (vanilla != null)
            {
                effect.OverheadVFX = vanilla.OverheadVFX;
                effect.TintColor = vanilla.TintColor;
                effect.AppliesTint = vanilla.AppliesTint;
                effect.PlaysVFXOnActor = vanilla.PlaysVFXOnActor;
            }
            return effect;
        }

        /// <summary>
        /// Seconds Bath Time has already added to this charm, and the duration it left behind. The budget lives on
        /// the effect instance, so it is per enemy and shared by both co-op players, and a charm applied afresh
        /// (a new instance, or an existing one whose duration someone else rewrote) starts over.
        /// </summary>
        public float bonusAdded, bonusDuration;

        /// <summary>
        /// Extends only the live Pluto effect instance owned by this enemy, by at most maxBonus seconds in total over
        /// the length that charm had when Bath Time first touched it. Keeping the two engine lists paired avoids
        /// touching a stale definition and, unlike ApplyEffect, cannot apply vulnerability or another charm twice.
        /// Returns whether the duration actually grew: an exhausted budget changes nothing and reports false.
        /// </summary>
        public static bool ExtendOwned(AIActor enemy, float bonus, float maxBonus)
        {
            if (enemy == null || enemy.m_activeEffects == null || enemy.m_activeEffectData == null) return false;
            int count = Mathf.Min(enemy.m_activeEffects.Count, enemy.m_activeEffectData.Count);
            for (int i = 0; i < count; i++)
            {
                RuntimeGameActorEffectData data = enemy.m_activeEffectData[i];
                PlutoCharmEffect effect = enemy.m_activeEffects[i] as PlutoCharmEffect;
                if (data == null || effect == null) continue;
                if (effect.effectIdentifier == "pluto_love")
                {
                    // Anything but our own last extension means a fresh charm (or a longer Dinner Time one), which
                    // gets its own budget rather than inheriting a spent one.
                    if (effect.duration != effect.bonusDuration) effect.bonusAdded = 0f;
                    float added = CatSetRules.AllowedBonus(effect.bonusAdded, bonus, maxBonus);
                    if (added <= 0f) return false;
                    effect.duration = CatSetRules.ExtendBudgeted(effect.duration, effect.bonusAdded, bonus, maxBonus);
                    effect.bonusAdded += added;
                    effect.bonusDuration = effect.duration;
                    return true;
                }
            }
            return false;
        }

        public override void OnEffectApplied(GameActor actor, RuntimeGameActorEffectData effectData, float partialAmount = 1f)
        {
            AIActor enemy = actor as AIActor;
            if (enemy == null) return;
            bonusAdded = 0f; // a freshly applied charm gets a fresh Bath Time budget
            bonusDuration = duration;
            AkSoundEngine.PostEvent("Play_OBJ_enemy_charmed_01", GameManager.Instance.gameObject);
            enemy.CanTargetEnemies = true;
            enemy.CanTargetPlayers = false;
            if (enemy.healthHaver != null) enemy.healthHaver.AllDamageMultiplier *= VulnerabilityMultiplier; // distracted
            if (enemy.healthHaver != null && enemy.GetComponent<CharmedDropMarker>() == null)
            {
                enemy.gameObject.AddComponent<CharmedDropMarker>();
                AIActor captured = enemy;
                enemy.healthHaver.OnPreDeath += (Vector2 dir) => KibbleBowlPickup.MaybeSpawn(captured.CenterPosition);
            }
        }

        public override void OnEffectRemoved(GameActor actor, RuntimeGameActorEffectData effectData)
        {
            AIActor enemy = actor as AIActor;
            if (enemy == null) return;
            enemy.CanTargetEnemies = false;
            enemy.CanTargetPlayers = true;
            if (enemy.healthHaver != null) enemy.healthHaver.AllDamageMultiplier /= VulnerabilityMultiplier;
        }
    }
}
