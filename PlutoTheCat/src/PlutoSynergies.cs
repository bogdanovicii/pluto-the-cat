using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Alexandria.ItemAPI;
using Alexandria.Misc;

namespace PlutoTheCat
{
    /// <summary>
    /// Synergies registered through Alexandria's CustomSynergies. Effects are applied by
    /// KibbleSackGun (homing), WetFoodCanItem (longer charm) and the hooks below (decoy, box).
    /// </summary>
    public static class PlutoSynergies
    {
        public const string FelineNutrition = "Complete Feline Nutrition";
        public const string DinnerTime = "Dinner Time";
        public const string LaserPointer = "Laser Pointer";
        public const string BoxFort = "Box Fort";
        public const string Playdate = "Playdate";
        public const string Squire = "Squire";
        // Knighted is a tier of Squire, not a registered synergy: Alexandria cannot require six junk, so CocoFriends
        // turns it on while Squire is active and Ser Junkan is a Holy (or Angelic) Knight.
        public const string Knighted = "Knighted";

        // Vanilla console ids below are verified against docs/research/gungeon_items_idmap.txt (tools/validate.py checks them).
        public static void Init()
        {
            Register(FelineNutrition, new List<string> { KibbleSackGun.ID },
                new List<string> { "orange", "meatbun", "gungeon_pepper", "partially_eaten_cheese", "ration", "friendship_cookie" });
            Register(DinnerTime, new List<string> { WetFoodCanItem.ID },
                new List<string> { "charming_rounds", "charm_horn", "yellow_chamber" });
            Register(LaserPointer, new List<string> { KibbleSackGun.ID },
                new List<string> { "laser_rifle", "science_cannon", "laser_lotus", "prototype_railgun" });
            Register(BoxFort, new List<string> { NineLivesItem.ID, "box" });   // "box" is the Cardboard Box
            Register(Playdate, new List<string> { SqueakyToyItem.ID, "dog" }); // the toy sends Coco out; effects in CocoFriends
            Register(Squire, new List<string> { CocoBlueItem.ID, "junkan" }); // "junkan" is Ser Junkan

            CustomActions.OnNewPlayercontrollerSpawned += OnPlayerSpawned;
        }

        /// <summary>One bad item id must never take the whole mod down: each synergy registers on its own.</summary>
        private static void Register(string name, List<string> mandatory, List<string> optional = null)
        {
            try
            {
                CustomSynergies.Add(name, mandatory, optional);
            }
            catch (System.Exception e)
            {
                Plugin.Log("synergy \"" + name + "\" not registered: " + e.Message);
            }
        }

        private static void OnPlayerSpawned(PlayerController player)
        {
            if (player == null || player.gameObject.GetComponent<SynergyDoer>() != null) return;
            player.gameObject.AddComponent<SynergyDoer>();
        }

        /// <summary>
        /// Per-player component. Laser Pointer: every dodge roll drops a red dot that enemies chase
        /// for a few seconds. Box Fort: once a second, strip every cooldown from a carried Cardboard Box.
        /// </summary>
        public class SynergyDoer : MonoBehaviour
        {
            private PlayerController player;
            private static GameObject decoyPrefab;
            private float boxTimer;

            private void Start()
            {
                player = GetComponent<PlayerController>();
                if (player != null) player.OnPreDodgeRoll += OnRoll;
            }

            private void Update()
            {
                if (player == null || player.activeItems == null) return;
                boxTimer -= BraveTime.DeltaTime;
                if (boxTimer > 0f) return;
                boxTimer = 1f;
                if (!player.PlayerHasActiveSynergy(BoxFort)) return;
                for (int i = 0; i < player.activeItems.Count; i++)
                {
                    PlayerItem item = player.activeItems[i];
                    if (item == null || item.GetComponent<CardboardBoxItem>() == null) continue;
                    item.timeCooldown = 0f;
                    item.roomCooldown = 0;
                    item.damageCooldown = 0f;
                    if (item.IsOnCooldown) item.ClearCooldowns();
                }
            }

            private void OnDestroy()
            {
                if (player != null) player.OnPreDodgeRoll -= OnRoll;
            }

            private void OnRoll(PlayerController p)
            {
                if (p == null || !p.PlayerHasActiveSynergy(LaserPointer)) return;
                if (p.CurrentRoom == null || !p.IsInCombat) return;
                if (decoyPrefab == null)
                {
                    SpawnObjectPlayerItem decoy = PickupObjectDatabase.GetById(201) as SpawnObjectPlayerItem; // Decoy
                    if (decoy != null) decoyPrefab = decoy.objectToSpawn;
                }
                if (decoyPrefab == null) return;
                GameObject dot = Object.Instantiate(decoyPrefab, p.CenterPosition, Quaternion.identity);
                tk2dSprite sprite = dot.GetComponent<tk2dSprite>();
                if (sprite != null && KibbleSackGun.RedDotSpriteId >= 0)
                    sprite.SetSprite(SpriteBuilder.itemCollection, KibbleSackGun.RedDotSpriteId);
                StartCoroutine(Expire(dot, 3f));
            }

            private IEnumerator Expire(GameObject dot, float seconds)
            {
                yield return new WaitForSeconds(seconds);
                if (dot != null) Object.Destroy(dot);
            }
        }
    }
}
