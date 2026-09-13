using System.Collections.Generic;
using System.Collections;
using UnityEngine;
using Alexandria.Misc;

namespace PlutoTheCat
{
    /// <summary>
    /// Small cat behaviours attached to every player (they only act on Pluto):
    /// Tail whip: rolling through an enemy hurts it. Zoomies: a short speed burst after clearing a room.
    /// </summary>
    public static class CatTricks
    {
        public static void Init()
        {
            CustomActions.OnNewPlayercontrollerSpawned += OnPlayerSpawned;
        }

        private static void OnPlayerSpawned(PlayerController player)
        {
            if (player == null || player.gameObject.GetComponent<CatTricksDoer>() != null) return;
            player.gameObject.AddComponent<CatTricksDoer>();
        }

        public static bool IsPluto(PlayerController p)
        {
            return p != null && p.name != null && p.name.Contains("Pluto");
        }

        // Speed modifiers created by Pluto's own effects (zoomies, anger, petting), so they can be summed and capped.
        private static readonly System.Collections.Generic.HashSet<StatModifier> ourSpeedBoosts = new System.Collections.Generic.HashSet<StatModifier>();

        /// <summary>Total movement-speed bonus currently granted by Pluto's own effects.</summary>
        public static float CurrentSpeedBonus(PlayerController p)
        {
            float total = 0f;
            if (p == null || p.ownerlessStatModifiers == null) return total;
            for (int i = 0; i < p.ownerlessStatModifiers.Count; i++)
            {
                StatModifier m = p.ownerlessStatModifiers[i];
                if (m != null && ourSpeedBoosts.Contains(m)) total += m.amount;
            }
            return total;
        }

        /// <summary>Adds a timed speed boost, capped so all of Pluto's boosts together never exceed the config maximum.</summary>
        public static IEnumerator TimedSpeed(PlayerController p, float amount, float seconds)
        {
            if (p == null) yield break;
            float room = PlutoConfig.MaxSpeedBonus - CurrentSpeedBonus(p);
            amount = Mathf.Min(amount, room);
            if (amount <= 0f) yield break;
            StatModifier boost = new StatModifier
            {
                statToBoost = PlayerStats.StatType.MovementSpeed,
                modifyType = StatModifier.ModifyMethod.ADDITIVE,
                amount = amount,
                ignoredForSaveData = true,
            };
            ourSpeedBoosts.Add(boost);
            p.ownerlessStatModifiers.Add(boost);
            p.stats.RecalculateStats(p, false, false);
            yield return new WaitForSeconds(seconds);
            ourSpeedBoosts.Remove(boost);
            if (p != null && p.ownerlessStatModifiers.Remove(boost))
                p.stats.RecalculateStats(p, false, false);
        }

        public class CatTricksDoer : MonoBehaviour
        {
            private PlayerController player;

            // Lands on his feet: the game fires OnPitfall when the player drops into a pit and, after the
            // respawn, applies a fixed half heart ("#PITFALL", DamageCategory.Environment). Pluto is
            // invulnerable while falling, so the first damage event after OnPitfall is that pit damage;
            // it is cancelled (within a generous window) and no life is spent on it.
            private static readonly Dictionary<PlayerController, float> landingUntil = new Dictionary<PlayerController, float>();

            public static bool IsLandingOnFeet(PlayerController p)
            {
                float until;
                return p != null && landingUntil.TryGetValue(p, out until) && Time.time < until;
            }

            private void Start()
            {
                player = GetComponent<PlayerController>();
                if (player == null) return;
                player.OnRolledIntoEnemy += TailWhip;
                player.OnRoomClearEvent += Zoomies;
                player.OnPitfall += Pitfall;
                if (player.healthHaver != null) player.healthHaver.ModifyDamage += LandOnFeet;
            }

            private void OnDestroy()
            {
                if (player == null) return;
                player.OnRolledIntoEnemy -= TailWhip;
                player.OnRoomClearEvent -= Zoomies;
                player.OnPitfall -= Pitfall;
                if (player.healthHaver != null) player.healthHaver.ModifyDamage -= LandOnFeet;
                landingUntil.Remove(player);
            }

            private void Pitfall()
            {
                if (!IsPluto(player) || !PlutoConfig.NoFallDamage) return;
                landingUntil[player] = Time.time + 8f;
            }

            private void LandOnFeet(HealthHaver hh, HealthHaver.ModifyDamageEventArgs args)
            {
                if (!IsLandingOnFeet(player) || args.ModifiedDamage <= 0f) return;
                if (args.InitialDamage > 0.51f) return;            // pit damage is exactly half a heart
                landingUntil.Remove(player);
                args.ModifiedDamage = 0f;
                PlutoVFX.Spawn(PlutoVFX.FurPuff, player.CenterPosition);
                Plugin.Log("landed on his feet: pit damage cancelled");
            }

            private void TailWhip(PlayerController p, AIActor enemy)
            {
                if (!IsPluto(p) || PlutoConfig.TailWhipDamage <= 0f) return;
                if (enemy == null || enemy.healthHaver == null || enemy.healthHaver.IsDead) return;
                Vector2 dir = (enemy.CenterPosition - p.CenterPosition).normalized;
                enemy.healthHaver.ApplyDamage(PlutoConfig.TailWhipDamage, dir, "Tail whip", CoreDamageTypes.None, DamageCategory.Normal, false, null, false);
                if (enemy.knockbackDoer != null) enemy.knockbackDoer.ApplyKnockback(dir, 12f, false);
                PlutoVFX.Spawn(PlutoVFX.FurPuff, enemy.CenterPosition);
            }

            private void Zoomies(PlayerController p)
            {
                if (!IsPluto(p) || PlutoConfig.ZoomiesSeconds <= 0f) return;
                StartCoroutine(TimedSpeed(p, PlutoConfig.ZoomiesSpeedBonus, PlutoConfig.ZoomiesSeconds));
            }
        }
    }
}
