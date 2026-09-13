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

            private void Start()
            {
                player = GetComponent<PlayerController>();
                if (player == null) return;
                player.OnRolledIntoEnemy += TailWhip;
                player.OnRoomClearEvent += Zoomies;
            }

            private void OnDestroy()
            {
                if (player == null) return;
                player.OnRolledIntoEnemy -= TailWhip;
                player.OnRoomClearEvent -= Zoomies;
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
