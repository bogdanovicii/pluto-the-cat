using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Alexandria.ItemAPI;
using Dungeonator;

namespace PlutoTheCat
{
    /// <summary>
    /// Wet Food Can: Pluto's starter active. Lobbed like a Molotov; where it lands,
    /// every enemy within CharmRadius falls in love with Pluto (PlutoCharmEffect).
    /// Built on the vanilla SpawnObjectPlayerItem + Alexandria's CustomThrowableObject
    /// (the same pattern Once More Into The Breach uses for Jarate).
    /// </summary>
    public class WetFoodCanItem : SpawnObjectPlayerItem
    {
        public const string ID = "pluto:wet_food_can";

        public static void Init()
        {
            string name = "Wet Food Can";
            GameObject obj = new GameObject(name);
            WetFoodCanItem item = obj.AddComponent<WetFoodCanItem>();
            ItemBuilder.AddSpriteToObject(name, Plugin.ITEM_ROOT + "/wet_food_can_icon", obj);
            ItemBuilder.SetupItem(item, "Thin Slices In Gravy",
                "A gold tin of ROYAL CANIN Kitten, thin slices in gravy. Lob it: it bursts open where it lands and " +
                "every enemy nearby falls hopelessly in love with Pluto for a while. Lovestruck enemies are distracted " +
                "and take more damage. Bosses are too proud to fall in love, but the smell stops them in their tracks " +
                "for a few seconds.\n\n" +
                "Pluto only gets the wet food on special occasions, which is why the sound of the lid peeling back " +
                "makes him appear from anywhere in the house. It turns out the Gundead feel exactly the same way.",
                "pluto");
            ItemBuilder.SetCooldownType(item, ItemBuilder.CooldownType.Damage, PlutoConfig.CanCooldownDamage);
            item.consumable = false;
            item.quality = PickupObject.ItemQuality.EXCLUDED;

            item.objectToSpawn = BuildThrownPrefab();
            item.tossForce = 12f;
            item.canBounce = false;
            item.IsCigarettes = false;
            item.RequireEnemiesInRoom = false;
            item.SpawnRadialCopies = false;
            item.RadialCopiesToSpawn = 0;
            item.AudioEvent = null;
            item.IsKageBunshinItem = false;
        }

        private static GameObject BuildThrownPrefab()
        {
            string root = Plugin.ITEM_ROOT + "/";
            GameObject can = SpriteBuilder.SpriteFromResource(root + "wet_food_can_toss_001.png", new GameObject("PlutoWetFoodCan"));
            FakePrefab.MakeFakePrefab(can); // marks it, DontDestroyOnLoad, and deactivates it; Alexandria re-activates Instantiate() copies

            tk2dSpriteAnimator animator = can.AddComponent<tk2dSpriteAnimator>();
            // Reuse the Bomb's (id 108) throwable sprite collection so the can lives with other thrown objects.
            tk2dSpriteCollectionData collection = (PickupObjectDatabase.GetById(108) as SpawnObjectPlayerItem)
                .objectToSpawn.GetComponent<tk2dSpriteAnimator>().Library.clips[0].frames[0].spriteCollection;

            List<int> tossIds = new List<int>();
            for (int i = 1; i <= 4; i++)
                tossIds.Add(SpriteBuilder.AddSpriteToCollection(root + "wet_food_can_toss_00" + i + ".png", collection));
            List<int> splashIds = new List<int>();
            for (int i = 1; i <= 3; i++)
                splashIds.Add(SpriteBuilder.AddSpriteToCollection(root + "wet_food_can_splash_00" + i + ".png", collection));

            tk2dSpriteAnimationClip toss = SpriteBuilder.AddAnimation(animator, collection, tossIds, "toss", tk2dSpriteAnimationClip.WrapMode.Loop);
            toss.fps = 12f;
            tk2dSpriteAnimationClip splash = SpriteBuilder.AddAnimation(animator, collection, splashIds, "splash", tk2dSpriteAnimationClip.WrapMode.Once);
            splash.fps = 10f;

            CustomThrowableObject throwable = can.AddComponent<CustomThrowableObject>();
            throwable.DefaultAnim = "toss";
            throwable.OnThrownAnimation = "toss";
            throwable.OnHitGroundAnimation = "splash";
            throwable.doEffectOnHitGround = true;
            throwable.destroyOnHitGround = false;
            throwable.thrownSoundEffect = "Play_OBJ_item_throw_01";
            throwable.effectSoundEffect = "Play_OBJ_enemy_charmed_01";

            can.AddComponent<WetFoodSplashEffect>();
            return can;
        }

        /// <summary>Runs when the can lands: charm everything nearby, then clean up.</summary>
        public class WetFoodSplashEffect : CustomThrowableEffectDoer
        {
            public override void OnEffect(GameObject obj)
            {
                tk2dBaseSprite sprite = obj.GetComponent<tk2dBaseSprite>();
                Vector2 center = sprite != null ? sprite.WorldCenter : (Vector2)obj.transform.position;

                PlutoVFX.Spawn(PlutoVFX.LoveBurst, center);
                RoomHandler room = center.GetAbsoluteRoom();
                if (room != null)
                {
                    List<AIActor> enemies = room.GetActiveEnemies(RoomHandler.ActiveEnemyType.All);
                    if (enemies != null)
                    {
                        // Dinner Time synergy: longer, wider.
                        PlayerController thrower = GameManager.Instance.PrimaryPlayer;
                        bool dinner = thrower != null && thrower.PlayerHasActiveSynergy(PlutoSynergies.DinnerTime);
                        float radius = dinner ? PlutoConfig.CharmRadius * 1.5f : PlutoConfig.CharmRadius;
                        PlutoCharmEffect love = PlutoCharmEffect.Create(dinner ? PlutoConfig.CharmDuration * 2f : PlutoConfig.CharmDuration);
                        for (int i = 0; i < enemies.Count; i++)
                        {
                            AIActor enemy = enemies[i];
                            if (enemy == null || enemy.healthHaver == null || enemy.healthHaver.IsDead) continue;
                            if (Vector2.Distance(enemy.CenterPosition, center) > radius) continue;
                            if (enemy.healthHaver.IsBoss)
                            {
                                // Predictable boss behaviour: a fixed stun instead of AI-dependent charm.
                                if (enemy.behaviorSpeculator != null) enemy.behaviorSpeculator.Stun(PlutoConfig.BossStunSeconds, true);
                                continue;
                            }
                            enemy.ApplyEffect(love, 1f, null);
                        }
                    }
                }
                StartCoroutine(DestroyAfter(obj, 1.2f));
            }

            private IEnumerator DestroyAfter(GameObject obj, float seconds)
            {
                yield return new WaitForSeconds(seconds);
                if (obj != null) Object.Destroy(obj);
            }
        }
    }
}
