using System;
using BepInEx;
using UnityEngine;
using Alexandria.CharacterAPI;

namespace PlutoTheCat
{
    /// <summary>
    /// BepInEx entry point. Order matters: sprites first, then the gun and the
    /// active item (so their string ids exist), then the character whose
    /// characterdata.txt loadout references those ids.
    /// </summary>
    [BepInDependency(ETGModMainBehaviour.GUID)]
    [BepInDependency(Alexandria.Alexandria.GUID)]
    [BepInPlugin(GUID, NAME, VERSION)]
    public class Plugin : BaseUnityPlugin
    {
        public const string GUID = "bogdan.etg.plutothecat";
        public const string NAME = "Pluto The Cat";
        public const string VERSION = "2.17.1";

        // Embedded-resource roots (RootNamespace + folder path, '/' separated).
        public const string SPRITE_ROOT = "PlutoTheCat/Resources/SpriteRoot";
        public const string ITEM_ROOT = "PlutoTheCat/Resources/Items";
        public const string CHARACTER_ROOT = "PlutoTheCat/Characters/Pluto";
        public const string COMPANION_ROOT = "PlutoTheCat/Resources/Companions/coco";
        public const string VFX_ROOT = "PlutoTheCat/Resources/VFX";


        public void Start()
        {
            PlutoConfig.Bind(Config);   // BepInEx/config/bogdan.etg.plutothecat.cfg
            ETGModMainBehaviour.WaitForGameManagerStart(GMStart);
        }

        /// <summary>Runs one load step in isolation so one broken feature cannot take the rest down.</summary>
        private static bool Step(string name, Action action)
        {
            try { action(); return true; }
            catch (Exception e)
            {
                Log("step \"" + name + "\" failed: " + e);
                Debug.LogError(e);
                return false;
            }
        }

        public void GMStart(GameManager gameManager)
        {
            // Essentials, each isolated. The character needs the items registered first (loadout ids).
            Step("sprites", () => ETGMod.Assets.SetupSpritesFromAssembly(typeof(Plugin).Assembly, SPRITE_ROOT));
            Step("vfx", PlutoVFX.Init);
            Step("fur", PlutoFur.Init);
            Step("gun", KibbleSackGun.Add);
            Step("taiyaki cannon", TaiyakiCannonGun.Add);   // samurai costume loadout (<altGuns>)
            Step("katana", KatanaGun.Add);
            Step("active", WetFoodCanItem.Init);
            Step("passive", NineLivesItem.Init);
            Step("coco blue", CocoBlueItem.Init);
            Step("squeaky toy", SqueakyToyItem.Init);
            Step("puffed up", PuffedUpItem.Init);
            Step("kibble bowl", KibbleBowlPickup.Init);
            // 2.17 cat items (loot pool for everyone)
            Step("ball of yarn", BallOfYarnItem.Init);
            Step("catnip pouch", CatnipPouchItem.Init);
            Step("jingle bell collar", JingleBellCollarItem.Init);
            Step("hairball item", HairballItem.Init);
            Step("scratching post", ScratchingPostItem.Init);

            CustomCharacterData built = null;
            Step("character", () =>
            {
                built = Loader.BuildCharacter(
                    CHARACTER_ROOT, GUID,
                    PlutoConfig.FoyerPosition,
                    true,                        // hasAltSkin (samurai costume, newaltspritesetup/)
                    PlutoConfig.BathtubPosition, // the kimono stand (costume swapper)
                    true,                        // removeFoyerExtras
                    false,                       // hasArmourlessAnimations
                    false,                       // usesArmourNotHealth
                    true,                        // paradoxUsesSprites
                    false,                       // useGlow
                    null, null,
                    0,                           // metaCost (free to unlock)
                    false, "");
            });
            // Alexandria catches its own exceptions, prints them as [CharAPI] and returns null.
            if (built == null)
            {
                Log("Pluto the Cat FAILED to build. See the [CharAPI] lines above this message.");
                return;
            }

            // Polish, each optional.
            Step("reflexes", () => CatReflexes(built));
            Step("patches", () => PlutoPatches.Apply(built));
            // The samurai costume's boss card (reference/art/bosscard/samurai.png). Not named bosscard_*, so Alexandria leaves
            // it out of the normal card list; PlutoPatches shows it while the costume is worn.
            Step("samurai card", () =>
            {
                const string res = "PlutoTheCat.Characters.Pluto.samuraicard_001.png";
                Texture2D tex = Alexandria.ItemAPI.ResourceExtractor.GetTextureFromResource(res, typeof(Plugin).Assembly);
                if (tex == null) throw new Exception("missing embedded resource " + res);
                tex.filterMode = FilterMode.Point;
                PlutoPatches.SamuraiCard = new System.Collections.Generic.List<Texture2D> { tex };
            });
            // The samurai costume stand appears only once Pluto's past is beaten: vanilla KILLED_PAST, which Vet Visit sets
            // when the Vet falls. UnlockSamuraiCostume forces it for testing.
            if (PlutoConfig.UnlockSamuraiCostume)
                Step("debug samurai unlock", () => GameStatsManager.Instance.SetCharacterSpecificFlag(built.identity, CharacterSpecificGungeonFlags.KILLED_PAST, true));
            if (PlutoConfig.LogPunchoutNames) Step("punchout dump", DumpPunchoutNames);
            Step("cat tricks", CatTricks.Init);
            Step("synergies", PlutoSynergies.Init);
            Log("Pluto the Cat is ready. Meow.");
        }

        /// <summary>Cat reflexes: 6 of the 9 dodge-roll frames are invulnerable (Alexandria marks the first half).</summary>
        private static void CatReflexes(CustomCharacterData data)
        {
            if (data == null || data.animator == null || data.animator.Library == null) return;
            foreach (tk2dSpriteAnimationClip clip in data.animator.Library.clips)
            {
                if (clip == null || clip.name == null || !clip.name.Contains("dodge")) continue;
                int n = Mathf.Clamp(PlutoConfig.InvulnerableRollFrames, 0, clip.frames.Length);
                for (int i = 0; i < n; i++) clip.frames[i].invulnerableFrame = true;
            }
        }

        /// <summary>Logs the Pilot's Punch-Out sprite and clip names so 2.1 can ship Pluto's boxing sprites.</summary>
        private static void DumpPunchoutNames()
        {
            try
            {
                PunchoutPlayerController player = ResourceManager.LoadAssetBundle("enemies_base_001").LoadAsset<GameObject>("MetalGearRat")
                    .GetComponent<MetalGearRatDeathController>().PunchoutMinigamePrefab.GetComponent<PunchoutController>().Player;
                tk2dSpriteAnimation lib = player.gameObject.GetComponent<tk2dSpriteAnimator>().Library;
                tk2dSpriteCollectionData coll = lib.clips[0].frames[0].spriteCollection;
                System.Text.StringBuilder sb = new System.Text.StringBuilder("[Pluto] punchout sprite defs (rogue): ");
                foreach (tk2dSpriteDefinition def in coll.spriteDefinitions)
                    if (def != null && def.name != null && def.name.Contains("rogue")) sb.Append(def.name).Append(' ');
                Debug.Log(sb.ToString());
                sb = new System.Text.StringBuilder("[Pluto] punchout clips (rogue): ");
                foreach (tk2dSpriteAnimationClip clip in lib.clips)
                    if (clip != null && clip.name != null && clip.name.Contains("rogue")) sb.Append(clip.name).Append('=').Append(clip.frames.Length).Append(' ');
                Debug.Log(sb.ToString());
            }
            catch (Exception e) { Debug.Log("[Pluto] punchout dump failed: " + e.Message); }
        }

        public static void Log(string text)
        {
            ETGModConsole.Log("[Pluto] " + text);
        }
    }
}
