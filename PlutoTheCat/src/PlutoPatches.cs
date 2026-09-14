using System;
using System.Collections.Generic;
using HarmonyLib;
using UnityEngine;
using Alexandria.CharacterAPI;

namespace PlutoTheCat
{
    /// <summary>
    /// Harmony patches for the samurai costume (2.16.0), each limited to Pluto:
    /// - the costume decides the starting guns (Taiyaki Cannon + katana vs the Royal Kibble Sack);
    /// - the Breach alt-gun shrine does nothing for Pluto (it toggles the same flag);
    /// - the boss intro card shows the samurai bust while the costume is worn.
    /// Vanilla has no costume-bound guns or cards; see docs/superpowers/plans/2026-09-14-samurai-pluto-2160.md.
    /// </summary>
    public static class PlutoPatches
    {
        public static PlayableCharacters Identity;
        public static bool HasIdentity;
        public static List<Texture2D> NormalCard;
        public static List<Texture2D> SamuraiCard;

        public static void Apply(CustomCharacterData built)
        {
            Identity = built.identity;
            HasIdentity = true;
            NormalCard = built.bossCard;

            Harmony harmony = new Harmony(Plugin.GUID + ".patches");
            harmony.Patch(AccessTools.Method(typeof(PlayerController), "SwapToAlternateCostume"),
                postfix: new HarmonyMethod(typeof(PlutoPatches), "CostumeLoadout"));
            harmony.Patch(AccessTools.Method(typeof(FoyerAlternateGunShrineController), "DoEffect"),
                prefix: new HarmonyMethod(typeof(PlutoPatches), "BlockShrine"));
            harmony.Patch(AccessTools.Method(typeof(BossCardUIController), "ToggleCoreVisiblity"),
                prefix: new HarmonyMethod(typeof(PlutoPatches), "PickCard"));
        }

        private static bool IsPluto(PlayerController player)
        {
            return HasIdentity && player != null && player.characterIdentity == Identity;
        }

        /// <summary>
        /// The costume decides the starting guns. The swap also runs before Start (inventory still null) at character
        /// select, quick restart and save-continue: there only the flag is set and Start -> InitializeInventory picks
        /// the list. Guns are rebuilt only in the Breach, like the shrine does, so a run's guns are never wiped.
        /// </summary>
        private static void CostumeLoadout(PlayerController __instance)
        {
            try
            {
                if (!IsPluto(__instance)) return;
                if (__instance.UsingAlternateStartingGuns == __instance.IsUsingAlternateCostume) return;
                __instance.UsingAlternateStartingGuns = __instance.IsUsingAlternateCostume;
                if (__instance.inventory != null && GameManager.HasInstance && GameManager.Instance.IsFoyer)
                    __instance.ReinitializeGuns();
            }
            catch (Exception e)
            {
                Plugin.Log("costume loadout: " + e.Message);
            }
        }

        /// <summary>For Pluto the costume is the only switch between the two loadouts (vanilla skips Gunslinger and Eevee here too).</summary>
        private static bool BlockShrine(PlayerController interactor)
        {
            return !IsPluto(interactor);
        }

        /// <summary>Stateless: reads the costume at the moment the card shows, so it can never drift out of step with the toggle.</summary>
        private static void PickCard()
        {
            try
            {
                PlayerController player = GameManager.HasInstance ? GameManager.Instance.PrimaryPlayer : null;
                if (!IsPluto(player) || NormalCard == null || NormalCard.Count == 0) return;
                bool samurai = player.IsUsingAlternateCostume && SamuraiCard != null && SamuraiCard.Count > 0;
                player.BosscardSprites = samurai ? SamuraiCard : NormalCard;
            }
            catch (Exception e)
            {
                Plugin.Log("boss card: " + e.Message);
            }
        }
    }
}
