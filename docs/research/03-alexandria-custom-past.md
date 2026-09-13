# Alexandria 0.5.10 `hasCustomPast` / `customPast` — how a custom past actually works

Researched 2026-09-13 against the **shipped 0.5.10 DLL** (`PlutoTheCat/packages/EtG.Alexandria.0.5.10/lib/net35/Alexandria.dll`, disassembled with `monodis` into `scratchpad/il/alexandria.il`, 218 569 lines) and cross-checked with Alexandria `main` on GitHub (https://github.com/Nevernamed22/Alexandria, last push 2026-08-17 — the same day 0.5.10 was published; the relevant code is byte-for-byte equivalent between IL and `main`). Vanilla game behaviour comes from the decompiled game source https://github.com/fedes1to/EtG-source (commit `c49b17a`, MIT-licensed dump of `Assembly-CSharp`), because the NuGet `EtG.GameLibs 2.1.9.1` DLL is a **reference stub** — every method body is `ldnull; throw` (verified: `GameManager::LoadCustomLevel` at `game.il` line 493262 is `IL_0000: ldnull / IL_0001: throw`). MtG API 1.9.2 IL (`mtg.il`) is real code and was used as a second witness for what `LoadCustomLevel` expects.

Everything not verified is collected in §9.

---

## 0. The mechanism in five lines

1. `Loader.BuildCharacter(..., hasCustomPast, customPast)` just stores the two values on the character **prefab**: `customCharacter.past = customPast; customCharacter.hasPast = hasCustomPast; data.hasPast = hasCustomPast;` (`CharacterBuilder.cs:109-111`). `CustomCharacter` is a `MonoBehaviour` Alexandria adds to the cloned base-character prefab.
2. `hasPast` is used **only** to register the character in the Blacksmith's PlayMaker FSM so she will hand out the *Bullet That Can Kill The Past* (`CustomCharacterBlackSmithHandler.cs:74`). Without the bullet `PlayerController.PastAccessible` never becomes `true` and the Gun That Can Kill The Past ends the run with the win Ammonomicon instead of a past.
3. When the Gun is fired in the Ark, Alexandria's Harmony **IL manipulator on `ArkController.HandleClockhair` (the coroutine's `MoveNext`)** inserts one call right after the vanilla `switch (shotPlayer.characterIdentity)`: `DoCustomPastChecks(ark, shotPlayer)`.
4. `DoCustomPastChecks` reads `shotPlayer.GetComponent<CustomCharacter>().past` from the **live player**; if it is non-empty it does `ark.ResetPlayers(false); GameManager.Instance.LoadCustomLevel(cc.past);` and jumps to the vanilla "past is loading" branch (`GameUIRoot.Instance.ToggleUICamera(false)`).
5. `customPast` is therefore a **`GameLevelDefinition.dungeonSceneName`** (e.g. vanilla `"fs_pilot"`, Modular's `"tt_modular_past"`, Enter the Beyond's `"botfs_lost"`). `GameManager.LoadCustomLevel` looks that string up in `GameManager.dungeonFloors` / `GameManager.customFloors` and loads `dungeonPrefabPath` through `DungeonDatabase.GetOrLoadByName` (an asset bundle `dungeons/<name>`). **Alexandria registers no level, sets no `KILLED_PAST` flag and plays no ending** — everything after `LoadCustomLevel` is the mod's job.

---

## 1. Public API surface (0.5.10 IL, verbatim signatures)

`Alexandria.CharacterAPI.Loader` (`alexandria.il` 169414 / 169508):

```il
default class Alexandria.CharacterAPI.CustomCharacterData BuildCharacter (string filePath, string guid,
    valuetype UnityEngine.Vector3 foyerPos, bool hasAltSkin, valuetype UnityEngine.Vector3 altSwapperPos,
    [opt] bool removeFoyerExtras, [opt] bool hasArmourlessAnimations, [opt] bool usesArmourNotHealth,
    [opt] bool paradoxUsesSprites, [opt] bool useGlow, [opt] class GlowMatDoer glowVars, [opt] class GlowMatDoer altGlowVars,
    [opt] int32 metaCost, [opt] bool hasCustomPast, [opt] string customPast)

default class Alexandria.CharacterAPI.CustomCharacterData BuildCharacterBundle (string filePath,
    class tk2dSpriteCollectionData d1, class tk2dSpriteAnimation SteveData1, class tk2dSpriteCollectionData d2,
    class tk2dSpriteAnimation SteveData2, string guid, valuetype UnityEngine.Vector3 foyerPos, bool hasAltSkin,
    valuetype UnityEngine.Vector3 altSwapperPos, [opt] bool removeFoyerExtras, [opt] bool hasArmourlessAnimations,
    [opt] bool usesArmourNotHealth, [opt] bool paradoxUsesSprites, [opt] bool useGlow, [opt] class GlowMatDoer glowVars,
    [opt] class GlowMatDoer altGlowVars, [opt] int32 metaCost, [opt] bool hasCustomPast, [opt] string customPast,
    [opt] class UnityEngine.Texture2D BossCard)
```

C# (`CharApi/CharacterBuilding/Loader.cs:109-117`, https://github.com/Nevernamed22/Alexandria/blob/main/CharApi/CharacterBuilding/Loader.cs):

```csharp
public static CustomCharacterData BuildCharacter(string filePath, string guid, Vector3 foyerPos, bool hasAltSkin, Vector3 altSwapperPos, bool removeFoyerExtras = true, bool hasArmourlessAnimations = false, bool usesArmourNotHealth = false, bool paradoxUsesSprites = true,
    bool useGlow = false, GlowMatDoer glowVars = null, GlowMatDoer altGlowVars = null, int metaCost = 0, bool hasCustomPast = false, string customPast = "")
{
    ...
        CharacterBuilder.BuildCharacter(data, hasAltSkin, paradoxUsesSprites, removeFoyerExtras, hasArmourlessAnimations, usesArmourNotHealth, hasCustomPast, customPast, metaCost, useGlow, glowVars, altGlowVars, Assembly.GetCallingAssembly());
```

`Loader` → `CharacterBuilder.BuildCharacter` → `CharacterBuilder.BuildCharacterCommon` (IL 164578). `Alexandria.xml` (the NuGet doc file) has **no** `<param>` entry for `customPast`/`hasCustomPast` — the feature is undocumented.

---

## 2. Q1 — What is the `customPast` string, and where is it consumed?

### 2.1 Where it is stored (build time)

`CharApi/CharacterBuilding/CharacterBuilder.cs` (`main`; identical order in IL 164578-164902):

```csharp
private static void BuildCharacterCommon(CustomCharacterData data, bool hasAltSkin, bool paradoxUsesSprites, bool removeFoyerExtras,
    bool hasArmourlessAnimations, bool usesArmourNotHealth, bool hasCustomPast, string customPast, int metaCost, bool useGlow,
    GlowMatDoer glowVars, GlowMatDoer altGlowVars, tk2dSpriteCollectionData d1, tk2dSpriteAnimation SteveData1, tk2dSpriteCollectionData d2,
    tk2dSpriteAnimation SteveData2, Assembly assembly, bool isBundle)
{
    var basePrefab = GetPlayerPrefab(data.baseCharacter);
    ...
    GameObject gameObject = GameObject.Instantiate(basePrefab);          // line 41
    playerController = gameObject.GetComponent<PlayerController>();
    var customCharacter = gameObject.AddComponent<CustomCharacter>();     // line 44
    customCharacter.data = data;
    data.characterID = storedCharacters.Count;
    ...
    storedCharacters.Add(data.nameInternal.ToLower(), new Tuple<CustomCharacterData, GameObject>(data, gameObject)); // line 107

    customCharacter.past = customPast;        // line 109
    customCharacter.hasPast = hasCustomPast;  // line 110
    data.hasPast = hasCustomPast;             // line 111
```

IL confirmation (`alexandria.il` 164871-164878):

```il
IL_0318:  ldarg.s 7
IL_031a:  stfld string Alexandria.CharacterAPI.CustomCharacter::past
IL_0320:  ldarg.s 6
IL_0322:  stfld bool Alexandria.CharacterAPI.CustomCharacter::hasPast
IL_0328:  ldarg.s 6
IL_032a:  stfld bool Alexandria.CharacterAPI.CustomCharacterData::hasPast
```

Fields (IL 165932-165944 and `CustomCharacter.cs:100-109`):

```il
.class public auto ansi beforefieldinit CustomCharacter        // : MonoBehaviour
  .field  public  class Alexandria.CharacterAPI.CustomCharacterData data
  .field  public  string past
  .field  public  string overrideAnimation
  .field  public  bool hasPast
.class public auto ansi serializable beforefieldinit CustomCharacterData
  .field  public  int32 metaCost
  .field  public  bool hasPast          // no string on the data object
  .field  public  class UnityEngine.Texture2D pastWinPic
```

### 2.2 Where it is consumed (run time) — the only consumer

`Alexandria.CharacterAPI.Hooks/CustomPastHandlerPatches::DoCustomPastChecks` (IL 183363-183408, complete body):

```il
.method private static hidebysig
       default bool DoCustomPastChecks (class ['Assembly-CSharp']ArkController ark, class ['Assembly-CSharp']PlayerController shotPlayer)  cil managed
{
    .locals init (class Alexandria.CharacterAPI.CustomCharacter V_0, bool V_1, bool V_2)
    IL_0001:  ldarg.1
    IL_0002:  callvirt instance !!0 class [UnityEngine.CoreModule]UnityEngine.Component::GetComponent<class Alexandria.CharacterAPI.CustomCharacter> ()
    IL_0007:  stloc.0
    IL_0008:  ldloc.0
    IL_0009:  brfalse.s IL_0018
    IL_000b:  ldloc.0
    IL_000c:  ldfld string Alexandria.CharacterAPI.CustomCharacter::past
    IL_0011:  call bool string::IsNullOrEmpty(string)
    IL_0016:  br.s IL_0019
    IL_0018:  ldc.i4.1
    IL_0019:  stloc.1
    IL_001a:  ldloc.1
    IL_001b:  brfalse.s IL_0021
    IL_001d:  ldc.i4.0            // return false  -> vanilla continues (OpenAmmonomicon)
    IL_001e:  stloc.2
    IL_001f:  br.s IL_003e
    IL_0021:  ldarg.0
    IL_0022:  ldc.i4.0
    IL_0023:  callvirt instance void class ['Assembly-CSharp']ArkController::ResetPlayers(bool)
    IL_0029:  call class ['Assembly-CSharp']GameManager class ['Assembly-CSharp']GameManager::get_Instance()
    IL_002e:  ldloc.0
    IL_002f:  ldfld string Alexandria.CharacterAPI.CustomCharacter::past
    IL_0034:  callvirt instance void class ['Assembly-CSharp']GameManager::LoadCustomLevel(string)
    IL_003a:  ldc.i4.1            // return true   -> jump to ToggleUICamera(false)
    ...
```

C# (`CharApi/Tools/CharApiHooks.cs:151-181`, https://github.com/Nevernamed22/Alexandria/blob/main/CharApi/Tools/CharApiHooks.cs):

```csharp
[HarmonyPatch]
private static class CustomPastHandlerPatches
{
    [HarmonyPatch(typeof(ArkController), nameof(ArkController.HandleClockhair), MethodType.Enumerator)]
    [HarmonyILManipulator]
    private static void ArkControllerHandleClockhairPatchIL(ILContext il, MethodBase original)
    {
        ILCursor cursor = new ILCursor(il);
        ILLabel toggleUICameraLabel = null; // executed if past is valid
        if (!cursor.TryGotoNext(MoveType.After,
          instr => instr.MatchLdloc(8), // flag
          instr => instr.MatchBrtrue(out toggleUICameraLabel)
          ))
          return;
        cursor.Emit(OpCodes.Ldarg_0); // load enumerator type
        cursor.Emit(OpCodes.Ldfld, original.DeclaringType.GetEnumeratorField("$this")); // load actual "$this" field
        cursor.Emit(OpCodes.Ldarg_0); // load enumerator type
        cursor.Emit(OpCodes.Ldfld, original.DeclaringType.GetEnumeratorField("shotPlayer")); // load shotPlayer field
        cursor.CallPrivate(typeof(CustomPastHandlerPatches), nameof(DoCustomPastChecks));
        cursor.Emit(OpCodes.Brtrue, toggleUICameraLabel);
    }

    private static bool DoCustomPastChecks(ArkController ark, PlayerController shotPlayer)
    {
      if (shotPlayer.GetComponent<CustomCharacter>() is not CustomCharacter cc || string.IsNullOrEmpty(cc.past))
        return false;
      ark.ResetPlayers(false);
      GameManager.Instance.LoadCustomLevel(cc.past);
      return true;
    }
}
```

Note that **`hasPast` is not consulted here** — only a non-empty `past` string matters at run time. `grep -n LoadCustomLevel alexandria.il` yields exactly one hit (IL 183400); there is no other Alexandria code path that loads or maps a past.

### 2.3 What `GameManager.LoadCustomLevel(string)` does with it

Vanilla (`GameManager.cs`, EtG-source; also witnessed by MtG API's `ETGModConsole.LoadLevel(string level, bool ignoreDictionary, bool glitched)`, `mtg.il` 14066-14214, which compares the argument against `GameManager.dungeonFloors[i].dungeonSceneName` and `customFloors[i].dungeonSceneName` before calling `LoadCustomLevel`):

```csharp
public void LoadCustomLevel(string custom)
{
    ...
    m_loadingLevel = true;
    FlushAudio();
    ClearPerLevelData();
    GameLevelDefinition gameLevelDefinition2 = null;
    int num = -1;
    for (int i = 0; i < dungeonFloors.Count; i++)
        if (dungeonFloors[i].dungeonSceneName == custom) { gameLevelDefinition2 = dungeonFloors[i]; num = i + 1; break; }
    if (gameLevelDefinition2 == null)
        for (int j = 0; j < customFloors.Count; j++)
            if (customFloors[j].dungeonSceneName == custom) { gameLevelDefinition2 = customFloors[j]; break; }
    if (gameLevelDefinition2 != null && gameLevelDefinition2.dungeonPrefabPath == string.Empty) { /* MainMenu / Foyer / plain SceneManager.LoadScene */ }
    else
    {
        StartCoroutine(LoadNextLevelAsync_CR(gameLevelDefinition2));   // NRE if the name is unknown
        ...
    }
}
```

`LoadNextLevelAsync_CR(GameLevelDefinition gld)` then loads the `dungeon_scene_001` bundle scene, sets `m_lastLoadedLevelDefinition = gld`, and

```csharp
if (!string.IsNullOrEmpty(gld.dungeonPrefabPath))
    CurrentlyGeneratingDungeonPrefab = DungeonDatabase.GetOrLoadByName(gld.dungeonPrefabPath);
```

`DungeonDatabase.cs` (complete):

```csharp
public static Dungeon GetOrLoadByName(string name)
{
    AssetBundle assetBundle = ResourceManager.LoadAssetBundle("dungeons/" + name.ToLower());
    Dungeon component = assetBundle.LoadAsset<GameObject>(name).GetComponent<Dungeon>();
    return component;
}
```

The flow used is `InjectedFlowPath` if set, else `gld.flowEntries` (`LovinglySelectDungeonFlow`), else the `Dungeon` prefab's own `PatternSettings.flows`.

`GameLevelDefinition` (stub IL, `game.il` 491923):

```il
.class public auto ansi serializable beforefieldinit GameLevelDefinition
  .field  public  string dungeonSceneName
  .field  public  string dungeonPrefabPath
  .field  public  float32 priceMultiplier
  .field  public  float32 secretDoorHealthMultiplier
  .field  public  float32 enemyHealthMultiplier
  .field  public  float32 damageCap
  .field  public  float32 bossDpsCap
  .field  public  class List`1<class DungeonFlowLevelEntry> flowEntries
  .field  public  class List`1<int32> predefinedSeeds
  .field  public notserialized  class DungeonFlowLevelEntry lastSelectedFlowEntry
```

`GameManager.dungeonFloors` / `customFloors` (`game.il` 492083-492084) are **copied from the `_GameManager` prefab** whenever the manager (re)initialises — `GameManager.LoadDungeonFloorsFromTargetPrefab`: `dungeonFloors = component.dungeonFloors; customFloors = component.customFloors;`. That is why every mod below adds its definition to *both* `GameManager.Instance.customFloors` and `ResourceManager.LoadAssetBundle("brave_resources_001").LoadAsset<GameObject>("_GameManager").GetComponent<GameManager>().customFloors`.

**Answer to Q1:** `customPast` is neither a Unity scene name nor a DungeonFlow name nor a prefab name; it is the `dungeonSceneName` key of a `GameLevelDefinition` that must exist in `GameManager.customFloors` (or `dungeonFloors`), consumed exactly once, in `Alexandria.CharacterAPI.Hooks.CustomPastHandlerPatches.DoCustomPastChecks` → `GameManager.LoadCustomLevel(string)`. Known vanilla values (from `ArkController.HandleClockhair` and `GameManager.DelayedLoadMidgameSave`): `fs_convict`, `fs_pilot`, `fs_guide`, `fs_soldier`, `fs_robot`, `fs_bullet`, `fs_coop`, and `tt_bullethell` (Gunslinger past). The vanilla past `Dungeon` prefabs are `Finalscenario_Soldier` etc. (Modular and Enter the Beyond clone `DungeonDatabase.GetOrLoadByName("Finalscenario_Soldier")`; the `fs_*` → `Finalscenario_*` mapping is inferred, see §9).

---

## 3. Q2 — Which vanilla methods does Alexandria hook for this?

### 3.1 The past redirect: one IL hook, `ArkController.HandleClockhair` (enumerator)

Harmony attribute blob on `ArkControllerHandleClockhairPatchIL` (IL 183263-183270), decoded:

```
HarmonyPatch(Type, string, MethodType) = "ArkController, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null", "HandleClockhair", 05 00 00 00
HarmonyILManipulator
```

`05` = `HarmonyLib.MethodType.Enumerator` (verified in `0Harmony.dll` IL: `Enumerator = int32(0x00000005)`), so the patched method is `ArkController/'<HandleClockhair>c__Iterator3'::MoveNext` (`game.il` 432569-432671). That iterator declares the fields the hook loads: `.field public class ArkController $this` and `.field public class PlayerController '<shotPlayer>__0'` (resolved through `Alexandria.Misc.Shared.GetEnumeratorField`, IL 160565, which uses `HarmonyLib.AccessTools.GetDeclaredFields(type).Find(...)`). `TryGotoNext(MoveType.After, ...)` uses `ldc.i4.2` = `MonoMod.Cil.MoveType.After` (verified in `MonoMod.Utils.dll`).

All patches in the DLL are applied by Alexandria's own plugin via `new Harmony("alexandria.etgmod.alexandria").PatchAll(Assembly.GetExecutingAssembly())` (IL 36200-36204); nothing needs to be initialised by the character mod.

Where the code lands in vanilla (`ArkController.cs`, decompiled; short quotes only). After the time-tube credits the coroutine does:

```csharp
bool isShortTunnel = didShootHellTrigger || shotPlayer.characterIdentity == PlayableCharacters.CoopCultist || CharacterStoryComplete(shotPlayer.characterIdentity);
yield return StartCoroutine(ttcc.HandleTimeTubeCredits(clockhair.sprite.WorldCenter, isShortTunnel, clockhair.spriteAnimator, (!didShootHellTrigger) ? shotPlayer.PlayerIDX : 0));
if (didShootHellTrigger)            { GameManager.DoMidgameSave(HELLGEON); LoadCustomLevel("tt_bullethell"); }
else if (identity == CoopCultist)   { GameManager.IsCoopPast = true; ResetPlayers(); LoadCustomLevel("fs_coop"); }
else if (CharacterStoryComplete(identity) && identity == Gunslinger) { DoMidgameSave(FINALGEON); IsGunslingerPast = true; ResetPlayers(true); LoadCustomLevel("tt_bullethell"); }
else if (CharacterStoryComplete(shotPlayer.characterIdentity))
{
    bool flag = false;
    GameManager.DoMidgameSave(GlobalDungeonData.ValidTilesets.FINALGEON);
    switch (shotPlayer.characterIdentity)
    {
        case PlayableCharacters.Convict: flag = true; ResetPlayers(); GameManager.Instance.LoadCustomLevel("fs_convict"); break;
        case Pilot: ... "fs_pilot";  case Guide: ... "fs_guide";  case Soldier: ... "fs_soldier";
        case Robot: ... "fs_robot";  case Bullet: ... "fs_bullet";
    }
    if (!flag)  { AmmonomiconController.Instance.OpenAmmonomicon(true, true); }   // <-- Alexandria injects just before this
    else        { GameUIRoot.Instance.ToggleUICamera(false); }                    // <-- toggleUICameraLabel
}
else { AmmonomiconController.Instance.OpenAmmonomicon(true, true); }
while (true) yield return null;
```

`flag` is local 8 of `MoveNext`; the injected `if (DoCustomPastChecks($this, shotPlayer)) goto toggleUICameraLabel;` sits between `brtrue` and the `!flag` Ammonomicon call. Consequences:

- The custom past is only reachable when `CharacterStoryComplete(identity)` is true: `GameStatsManager.Instance.GetFlag(GungeonFlags.BLACKSMITH_BULLET_COMPLETE) && GameManager.Instance.PrimaryPlayer.PastAccessible` (`ArkController.CharacterStoryComplete`). `PastAccessible` is a `[NonSerialized] public bool` on `PlayerController` set only by `BulletThatCanKillThePast.Pickup` (`GameManager.Instance.PrimaryPlayer.PastAccessible = true;`).
- The time tube already ran with `skipCredits = true` (short tunnel) and vanilla already wrote a **mid-game save tagged `FINALGEON` with the custom identity** (`GameManager.DoMidgameSave(FINALGEON)` executes before the `switch`). See §9 for the resume caveat.
- `ArkController.ResetPlayers(false)` (called by Alexandria) does `ResetToFactorySettings(true, true)`, clears `CharacterUsesRandomGuns`, sets `IsVisible = true` and clears the `"ark"` input override for every living player — the same as vanilla pasts.

### 3.2 The blacksmith gate: `TalkDoerLite.Start` prefix

`CharApi/CustomCharacterBlackSmithHandler.cs` (IL 178797 `BlackSmithFix`, attribute target `TalkDoerLite::Start`, `HarmonyPrefix`):

```csharp
[HarmonyPatch(typeof(TalkDoerLite), nameof(TalkDoerLite.Start))]
[HarmonyPrefix]
public static void BlackSmithFix(TalkDoerLite __instance)
{
    ...
    if (!__instance.gameObject.GetComponent<PlayMakerFSM>() || !__instance.gameObject.name.Contains("NPC_Blacksmith")) return;
    foreach (var character in CharacterBuilder.storedCharacters)
    {
        if (character.Value.First.hasPast) __instance.gameObject.AddNewCharacter(character.Value.First.nameShort.Replace(" ", ""), character.Value.First.identity);
```

`AddNewCharacter` adds an `Is<NameShort>` event to the blacksmith FSM and, for every state containing a `CharacterClassSwitch`, appends the custom `PlayableCharacters` value to `compareTo` and routes it to the same state `IsBullet` goes to. This is the **only** place `hasPast` is read (IL usages: 164875/164878 store, 179003 read). It runs every time a blacksmith `TalkDoerLite` starts (each Breach load), so `hasPast` can be flipped later and takes effect on the next Breach visit.

### 3.3 The win picture: `AmmonomiconDeathPageController.SetWinPic` postfix

```csharp
[HarmonyPatch(typeof(AmmonomiconDeathPageController), nameof(AmmonomiconDeathPageController.SetWinPic))]
[HarmonyPostfix]
private static void AmmonomiconDeathPageControllerSetWinPicPatch(AmmonomiconDeathPageController __instance)
{
    GlobalDungeonData.ValidTilesets tilesetId = GameManager.Instance.Dungeon.tileIndices.tilesetId;
    PlayerController player = GameManager.Instance.PrimaryPlayer;
    if (GameManager.Instance.CurrentGameMode == GameManager.GameMode.BOSSRUSH || player.GetComponent<CustomCharacter>() is not CustomCharacter cc || cc.data == null)
        return;
    if (tilesetId != GlobalDungeonData.ValidTilesets.FINALGEON && __instance.ShouldUseJunkPic()) { ... junkanWinPic ... }
    else if (tilesetId == GlobalDungeonData.ValidTilesets.FINALGEON && cc.data.pastWinPic)
        __instance.photoSprite.Texture = cc.data.pastWinPic;
}
```

So `CustomCharacterData.pastWinPic` is shown only if the past `Dungeon`'s `tileIndices.tilesetId == FINALGEON` (vanilla pasts are; a custom `Dungeon` must set it, or `pastWinPic` is ignored — Enter the Beyond uses a custom tileset id and therefore never shows it).

### 3.4 Every Harmony target in `Alexandria.CharacterAPI.Hooks` (decoded from the 0.5.10 attribute blobs)

| Vanilla target | Kind | Purpose (from patch-method name) |
|---|---|---|
| `PlayerController.ResetToFactorySettings`, `PlayerController.TriggerDarkSoulsReset` | ILManipulator | zero-health (armour-only) characters treated like Robot |
| `PlayerController.HandleCloneEffect`, `PlayerController.CoopResurrectInternal` (Enumerator) | ILManipulator | same |
| `PlayerController.SwapToAlternateCostume` | Prefix | alt skin |
| `Foyer.ProcessPlayerEnteredFoyer` | Postfix | foyer setup |
| `PlayerController.LocalShaderName` (Getter) | Prefix | glow shader |
| `PunchoutPlayerController.UpdateUI`, `.HandleAnimationCompletedSwap`, `.SwapPlayer` (×2) | ILManipulator | Punch-Out names / no Paradox |
| `PunchoutController.Init` | Prefix | Punch-Out sprites |
| `AmmonomiconDeathPageController.GetDeathPortraitName` | Postfix | death portrait |
| `PlayerController.ChangeSpecialShaderFlag`, `.GetBaseAnimationName`, `.DoGhostBlank` | Prefix/Postfix/Prefix | visuals / coop blank |
| `CharacterSelectIdleDoer.Update`, `.OnEnable` | Prefix | Breach idle |
| `FoyerCharacterSelectFlag.OnSelectedCharacterCallback` (Postfix), `.CanBeSelected` (Prefix) | | Breach select |
| `dfLanguageManager.GetValue`, `dfControl.getLocalizedValue` | Prefix | string table |
| `Foyer.SetUpCharacterCallbacks` (Postfix), `Foyer.PlayerCharacterChanged` (Prefix) | | Breach |
| `BraveResources.Load(string,string)` | Postfix | resource redirect |
| `GameManager.ClearSecondaryPlayer` | Postfix | coop |
| `AmmonomiconDeathPageController.SetWinPic` | Postfix | `pastWinPic` / `junkanWinPic` (§3.3) |
| `MidGameSaveData.GetPlayerOnePrefab` | Prefix | elevator save/continue with a custom prefab |
| **`ArkController.HandleClockhair` (Enumerator)** | **ILManipulator** | **custom past redirect (§3.1)** |
| `TalkDoerLite.Start` (in `CustomCharacterBlackSmithHandler`) | Prefix | blacksmith bullet (§3.2) |

**Not hooked anywhere in Alexandria 0.5.10** (grep of the whole IL): `GameManager.LoadCustomLevel` / `DelayedLoadCustomLevel` / `DelayedLoadMidgameSave`, `DungeonDatabase.GetOrLoadByName`, `TimeTubeCreditsController.*`, `GameStatsManager.SetCharacterSpecificFlag` / `GetCharacterSpecificFlag` (Alexandria only calls `GetFlag`/`SetFlag`/`RegisterStatChange`), any `PlayerController.characterIdentity` comparison in the past code, `Foyer`'s character→past mapping (there is none in vanilla; the mapping *is* the `switch` in `ArkController`). Alexandria's `DungeonAPI` contains no `GameLevelDefinition`/`customFloors` registration helper either (the only `GameLevelDefinition` reference in the IL is a `priceMultiplier` read at IL 60961).

Thunderstore changelog note (https://thunderstore.io/c/enter-the-gungeon/p/Alexandria/Alexandria/changelog/): an older version "removed a hook that was completely overriding `ArkController.HandleClockhair()` and replaced it with an ILManipulator" — i.e. earlier Alexandria versions replaced the whole coroutine; 0.5.10 only injects the check.

---

## 4. Q3 — Ending, credits and the `KILLED_PAST` flag

**Alexandria does none of it.** Once `LoadCustomLevel` returns, the past level is an ordinary custom floor. In vanilla every past has its own controller that finishes the run; all six do the same five things (`PilotPastController.EndPastSuccess`, `RobotPastController`, `PastLabMarineController`, `ConvictPastController`, `GuidePastController`, `BulletPastRoomController`, `CoopPastController`):

1. `GameStatsManager.Instance.SetCharacterSpecificFlag(PlayableCharacters.<Identity>, CharacterSpecificGungeonFlags.KILLED_PAST, true);` — Pilot/Robot/Soldier/Convict/Guide/CoopCultist pass their **hard-coded** identity; only `BulletPastRoomController` uses the session overload `SetCharacterSpecificFlag(KILLED_PAST, true)`.
2. `GameStatsManager.Instance.RegisterStatChange(TrackedStats.TIMES_KILLED_PAST, 1f);`
3. (optional) freeze frame, `PastCameraUtility.LockConversation(...)`, `Pixelator.Instance.FadeToColor(0.15f, Color.white, true, 0.15f)`.
4. `TimeTubeCreditsController ttcc = new TimeTubeCreditsController(); ttcc.ClearDebris(); yield return StartCoroutine(ttcc.HandleTimeTubeCredits(GameManager.Instance.PrimaryPlayer.sprite.WorldCenter, false, null, -1));` — `skipCredits = false` here, so the real credits + "PastGameCompletePanel" play.
5. `AmmonomiconController.Instance.OpenAmmonomicon(true, true);` — the win page; `AmmonomiconDeathPageController` shows `#DEATH_PASTKILLED` when `GetCharacterSpecificFlag(PrimaryPlayer.characterIdentity, KILLED_PAST)` is true, else `#DEATH_PASTHAUNTS`, and calls `SetWinPic()` (→ Alexandria postfix, §3.3).

The mod-side template, verbatim from Enter the Beyond (`Floors/LostPastController.cs`, https://github.com/bobot-dev/enter-the-beyond/blob/main/Floors/LostPastController.cs):

```csharp
private IEnumerator HandleBossKilled()
{
    GameStatsManager.Instance.SetCharacterSpecificFlag((PlayableCharacters)CustomPlayableCharacters.Lost, CharacterSpecificGungeonFlags.KILLED_PAST, true);
    SaveAPI.SaveAPIManager.SetFlag(SaveAPI.CustomDungeonFlags.BOT_BOSSKILLED_LOST_PAST, true);
    GameStatsManager.Instance.RegisterStatChange(TrackedStats.TIMES_KILLED_PAST, 1f);

    PlayerController m_lost = GameManager.Instance.PrimaryPlayer;
    GameManager.Instance.MainCameraController.OverridePosition = m_lost.CenterPosition;
    yield return new WaitForSeconds(0.5f);
    Pixelator.Instance.FreezeFrame();
    BraveTime.RegisterTimeScaleMultiplier(0f, this.gameObject);
    float ela = 0f;
    while (ela < ConvictPastController.FREEZE_FRAME_DURATION) { ela += GameManager.INVARIANT_DELTA_TIME; yield return null; }
    BraveTime.ClearMultiplier(this.gameObject);
    TimeTubeCreditsController ttcc = new TimeTubeCreditsController();
    ttcc.ClearDebris();
    yield return this.StartCoroutine(ttcc.HandleTimeTubeCredits(m_lost.sprite.WorldCenter, false, null, -1, false));
    AmmonomiconController.Instance.OpenAmmonomicon(true, true);
    yield break;
}
```

Modular does the same split across two files: the boss (`Code/Enemies/Bosses/ModularPrime.cs:1253-1257`) sets `KILLED_PAST` (and `KILLED_PAST_ALTERNATE_COSTUME` when `player.IsUsingAlternateCostume`) on `ETGModCompatibility.ExtendEnum<PlayableCharacters>(Module.GUID, Module.Modular_Character_Data.nameShort)` and mirrors it into its own SaveAPI flag `CustomDungeonFlags.PAST`; the escape interactable (`Past/Prefabs/Objects/Solid Objects/Spaceship.cs:195-200`) runs `ttcc.HandleTimeTubeCredits(..., false, null, -1, false)` then `AmmonomiconController.Instance.OpenAmmonomicon(true, true)`.

Flag plumbing facts (vanilla `GameStatsManager.cs`):

- `SetCharacterSpecificFlag(PlayableCharacters character, ...)` auto-creates the entry: `if (!m_characterStats.ContainsKey(character)) m_characterStats.Add(character, new GameStats());` — a custom (extended) enum value is a valid key. `m_characterStats` is `[fsProperty] Dictionary<PlayableCharacters, GameStats>` and is persisted with the normal save.
- Setting `KILLED_PAST` also sets `KILLED_PAST_ALTERNATE_COSTUME` when `PrimaryPlayer.IsUsingAlternateCostume` (and then `GungeonFlags.ITEMSPECIFIC_ALTERNATE_GUNS_UNLOCKED`).
- Consumers: `AmmonomiconDeathPageController` (win text), `TimeTubeCreditsController` (line 287: shows `Global Prefabs/PastGameCompletePanel` when the flag is set), `CharacterCostumeSwapper` (alt-costume unlock; Enter the Beyond re-hooks it at `Hooks.cs:1966`), `FoyerAlternateGunShrineController`, `GameStatsManager` "all pasts killed" checks (hard-coded to the six vanilla identities — a custom identity never counts towards those).
- Alexandria's Breach card only touches the `PastKilledLabel` when `metaCost != 0` (`FoyerCharacterHandler.cs:354-361`), rewriting it to `"(Past Killed) (<metaCost>[sprite "hbux_text_icon"])`; with `metaCost == 0` (Pluto's current call) the vanilla label logic is left alone.

The level itself should be a `Dungeon` whose `LevelOverrideType == GameManager.LevelOverrideState.CHARACTER_PAST` (`GameManager.CurrentLevelOverrideState` simply returns the current/generating `Dungeon.LevelOverrideType`). That state is what makes the game behave like a past: `PlayerController` skips the gun-game/`DIE_IN_PAST` paths, `GameStatsManager` skips session stat recording (`GameStatsManager.cs:101`), `Minimap`, `DungeonFloorMusicController`, `ChallengeManager`, `RoomHandler`, `AIActor`, `PickupObject` etc. all check it. Enter the Beyond sets `dungeon.LevelOverrideType = GameManager.LevelOverrideState.CHARACTER_PAST; dungeon.PlayerIsLight = true; dungeon.BossMasteryTokenItemId = -1;` on its cloned `Dungeon`.

---

## 5. Q4 — Can a separate plugin set the past after `BuildCharacter`?

Yes. Both values are plain public fields, read lazily:

- `CustomCharacter.past` / `CustomCharacter.hasPast` live on the **prefab** `GameObject` stored in `CharacterBuilder.storedCharacters` (`public static Dictionary<string, Tuple<CustomCharacterData, GameObject>>`, key `data.nameInternal.ToLower()`, where `Loader.cs:324` sets `data.nameInternal = "Player" + data.nameShort`). The live `PlayerController` is a Unity `Instantiate` of that prefab, so the serialized `string past` / `bool hasPast` are copied to each run's player; Alexandria reads `shotPlayer.GetComponent<CustomCharacter>().past` at Ark time.
- `CustomCharacterData.hasPast` is read on every `TalkDoerLite.Start` of the blacksmith (§3.2).

So a second plugin (or the same plugin, later) can do:

```csharp
var tuple = Alexandria.CharacterAPI.CharacterBuilder.storedCharacters["playerpluto"]; // nameInternal.ToLower()
var cc = tuple.Second.GetComponent<Alexandria.CharacterAPI.CustomCharacter>();
cc.past = "tt_pluto_past";      // any registered GameLevelDefinition.dungeonSceneName
cc.hasPast = true;              // informational only
tuple.First.hasPast = true;     // what the blacksmith handler reads
```

before the Breach is first loaded (prefab edits only reach players instantiated afterwards; the blacksmith registration happens on the next Breach load). Even later, `GameManager.Instance.PrimaryPlayer.GetComponent<CustomCharacter>().past = "..."` on the live player works up to the moment the Gun is fired. Nothing is consumed inside `BuildCharacter` except the assignment. Caveat: `storedCharacters` is filled only after `BuildCharacterCommon` succeeded, and Alexandria catches its own exceptions and returns `null` from `Loader.BuildCharacter`.

---

## 6. Q5 — Open-source mods that ship a real custom past

### 6.1 Modular Remastered (TeamPlanetside / Some Bunny) — uses Alexandria's CharacterAPI, `hasCustomPast = true`

- Thunderstore `TeamPlanetside-Modular_Remastered` 1.3.20 (updated 2026-07-19), deps `MtG_API-Mod_the_Gungeon_API-1.6.2`, `HellfireJune-JuneLib-1.0.7`, `Alexandria-Alexandria-0.5.6`, `TeamPlanetside-Ammonomicon_API-1.0.1`; description "...Complete with new sprites, new gameplay mechanics, unlocks and a Past to beat!". Source https://github.com/Some-Bunny/Modular (branch `master`).
- Character build (`Module.cs:232-251`), positional args — `0 //Hegemony Cost, true //HasPast, "tt_modular_past"`:

```csharp
var data = Loader.BuildCharacterBundle(
             "ModularMod/Sprites/Modular",
             StaticCollections.Modular_Character_Collection,
             Module.ModularAssetBundle.LoadAsset<GameObject>("ModularSpriteAnimation").GetComponent<tk2dSpriteAnimation>(),
             StaticCollections.Modular_Character_Alt_Collection,
             Module.ModularAssetBundle.LoadAsset<GameObject>("Modular_Alt_Animation").GetComponent<tk2dSpriteAnimation>(),
             "somebunny.etg.modularcharacter",
             new Vector3(30.125f, 29.5f),
             true,
             new Vector3(30.625f, 28.5f),
             false, false, true,
             true, //Sprites used by paradox
             true, //Glows
             new GlowMatDoer(new Color32(121, 234, 255, 255), 14, 10), //Glow Mat
             new GlowMatDoer(new Color32(0, 255, 54, 255), 5, 3), //Alt Skin Glow Mat
             0, //Hegemony Cost
             true, //HasPast
             "tt_modular_past",
             Module.ModularAssetBundle.LoadAsset<Texture2D>("modular_bosscard_001")); //Past ID String
Modular_Character_Data = data;
Modular_Character_Data.pastWinPic = Module.ModularAssetBundle.LoadAsset<Texture2D>("win_pic_001");
```

- Level registration (`Past/PastFloorSetup.cs:48-77`, called from `Module.Start`-time code at line 63 and again in `PastDungeon.Init()` after the character build at line 266):

```csharp
public static void InitCustomDungeon()
{
    getOrLoadByName_Hook = new Hook(
        typeof(DungeonDatabase).GetMethod("GetOrLoadByName", BindingFlags.Static | BindingFlags.Public),
        typeof(PastDungeon).GetMethod("GetOrLoadByNameHook", BindingFlags.Static | BindingFlags.Public)
    );
    AssetBundle braveResources = ResourceManager.LoadAssetBundle("brave_resources_001");
    GameManagerObject = braveResources.LoadAsset<GameObject>("_GameManager");

    PastDefinition = new GameLevelDefinition()
    {
        dungeonSceneName = "tt_modular_past", //this is the name we will use whenever we want to load our dungeons scene
        dungeonPrefabPath = "based_modular_past", //this is what we will use when we want to acess our dungeon prefab
        priceMultiplier = 1.5f,
        secretDoorHealthMultiplier = 1,
        enemyHealthMultiplier = 1.6f,
        damageCap = 300,
        bossDpsCap = 78,
        flowEntries = new List<DungeonFlowLevelEntry>(0),
        predefinedSeeds = new List<int>(0)
    };
    foreach (GameLevelDefinition levelDefinition in GameManager.Instance.customFloors)
        if (levelDefinition.dungeonSceneName == "tt_modular_past") { PastDefinition = levelDefinition; }

    GameManager.Instance.customFloors.Add(PastDefinition);
    GameManagerObject.GetComponent<GameManager>().customFloors.Add(PastDefinition);
}

public static Dungeon GetOrLoadByNameHook(Func<string, Dungeon> orig, string name)
{
    if (!GameManager.Instance.customFloors.Contains(PastDefinition))
        GameManager.Instance.customFloors.Add(PastDefinition);
    bool flag = name.ToLower() == "based_modular_past";
    Dungeon result;
    if (flag)
        result = PastDungeon.AbyssGeon(GetOrLoadByName_Orig("Base_ResourcefulRat"));   // runtime-built Dungeon
    else
        result = orig(name);
    return result;
}
```

`AbyssGeon` clones `Base_ResourcefulRat`, borrows tiles from `DungeonDatabase.GetOrLoadByName("Finalscenario_Soldier")`, replaces `PatternSettings.flows` with `CustomFlow.Default_Flow`, and the rooms/flows are built with Alexandria's `DungeonAPI` (`RoomFactory`, `DungeonHandler` in `Past/Prefabs/FloorRoomInitialisation.cs`, `StaticReferences` in the prefab scripts). A debug console command `pstmdl load` calls `GameManager.Instance.LoadCustomLevel(PastDefinition.dungeonSceneName)` directly for testing. At start-up Modular re-applies the vanilla flag from its own save: `GameStatsManager.Instance.SetCharacterSpecificFlag(ExtendEnum<PlayableCharacters>(GUID, nameShort), KILLED_PAST, AdvancedGameStatsManager.Instance.GetFlag(CustomDungeonFlags.PAST));` (`Module.cs:326-329`).

### 6.2 Enter the Beyond (N0tAB0t / bobot-dev) — the "Lost" character, `customPast = "botfs_lost"`

Source https://github.com/bobot-dev/enter-the-beyond (branch `main`, last push 2022-06-30; ModWorkshop page https://modworkshop.net/mod/30849 "adds a new floor, a new boss, a new character"). It embeds its own older copy of the Character API (`Character Api/` — same `hasCustomPast`/`customPast` parameters, but `guid` is an enum), so it is the same design, not literally Alexandria.dll.

```csharp
// Module.cs:562
var data = Loader.BuildCharacter("BotsMod/Characters/Lost", CustomPlayableCharacters.Lost,
    new Vector3(15.8f, 26.6f, 27.1f), true, new Vector3(15.3f, 24.8f, 25.3f), true, false, false, true, true,
    new GlowMatDoer(new Color32(255, 0, 38, 255), 4.55f, 55), new GlowMatDoer(new Color32(255, 69, 248, 255), 1.55f, 55),
    0, true, "botfs_lost");
```

`Floors/LostPastDungeon.cs:30-50`: `dungeonSceneName = "botfs_lost"`, `dungeonPrefabPath = "Base_LostPast"`, `priceMultiplier = 1.5f`, `damageCap = 300`, `bossDpsCap = 78`, added to both `customFloors` lists; `FloorHooks.GetOrLoadByNameHook` returns `LostPastDungeon.LostPastGeon(GetOrLoadByName_Orig("Base_ResourcefulRat"))` for `"base_lostpast"`; the clone sets `LevelOverrideType = CHARACTER_PAST`, a custom `tilesetId`, `PatternSettings.flows = { BeyondDungeonFlows.F1b_LostPast_flow_01() }`, `BossMasteryTokenItemId = -1`, `PlayerIsLight = true`. `Module.cs:757-762` hooks `GameManager.Awake` and calls `LostPastDungeon.InitCustomDungeon()` again because the manager's `customFloors` list is reset from the prefab. The ending is `LostPastController.HandleBossKilled` (§4).

### 6.3 Related patterns

- **GungeonCraft** (`src/Cwaff-Flows/CwaffDungeons.cs`, https://github.com/pcrain/GungeonCraft): the same three pieces as Harmony patches — `GameManager.LoadCustomLevel` prefix that re-adds the `GameLevelDefinition` ("fixes a bug where returning to the breach deletes the floor, thanks Bunny!"), `DungeonDatabase.GetOrLoadByName` prefix building the dungeon from a template, `FlowDatabase.GetOrLoadByName` prefix for custom flows. Not a past, but the cleanest registration code.
- **ExpandTheGungeon** (`ExpandComponents/ExpandArkController.cs`) replaces the whole Ark with its own copy of the vanilla `switch`; it has no custom-identity handling and is not a CharacterAPI consumer.
- **Once More Into The Breach, Frost & Gunfire, Planetside of Gunymede, Knife to a Gunfight**: no `hasCustomPast = true` / `customFloors` usage found by GitHub code search (`hasCustomPast` matches only Alexandria itself and the Enter the Beyond copy; `customFloors` matches Modular, Planetside's *TheAbyss* floor (not a past), GungeonCraft, ChildrenOfKaliber, Fallen-Items, ExpandTheGungeon, Enter the Beyond).

---

## 7. What this means for Pluto (`PlutoTheCat/src/Plugin.cs:64-77` currently passes `0, false, ""`)

Two viable routes:

**A. Reuse a vanilla past** — `Loader.BuildCharacter(..., metaCost: 0, hasCustomPast: true, customPast: "fs_pilot")` (or `fs_bullet`, etc.).
- Works mechanically: the blacksmith hands out the Bullet (§3.2), Alexandria redirects to `LoadCustomLevel("fs_pilot")`, the vanilla `PilotPastController` uses `GameManager.Instance.PrimaryPlayer` (no identity check), and `pastWinPic` shows because vanilla pasts are `FINALGEON`.
- But the vanilla controller sets `KILLED_PAST` for `PlayableCharacters.Pilot`, **not** for Pluto (only the Bullet past uses the session character), so the win page says "the past haunts you", the credits panel is skipped, and the alt-costume unlock never fires. Fix with a small Harmony postfix (e.g. on `PilotPastController.EndPastSuccess`'s `MoveNext`, or on `GameStatsManager.SetCharacterSpecificFlag(PlayableCharacters, ...)` guarded by `CurrentLevelOverrideState == CHARACTER_PAST && PrimaryPlayer is Pluto`) that mirrors the flag onto Pluto's identity and calls `RegisterStatChange(TIMES_KILLED_PAST, 1f)`.
- Pilot-specific branches remain: `Dungeon.cs:1624` swaps the coop partner prefab to `PlayerCoopShip` only when the identity is Pilot; `Dungeon.cs:1660` has Convict-only logic; harmless for a solo run.

**B. A real Pluto past** — do what Modular/Beyond do: `GameLevelDefinition { dungeonSceneName = "tt_pluto_past", dungeonPrefabPath = "base_pluto_past", ... }` added to both `customFloors` lists in `GMStart` (and re-added on `GameManager.Awake` or via GungeonCraft's `LoadCustomLevel` prefix); a `DungeonDatabase.GetOrLoadByName` hook that returns a runtime-cloned `Dungeon` (e.g. from `Finalscenario_Soldier` or `Base_ResourcefulRat`) with `LevelOverrideType = CHARACTER_PAST`, `tileIndices.tilesetId = FINALGEON` (for `pastWinPic`), custom `PatternSettings.flows` built with Alexandria `DungeonAPI.RoomFactory`; a boss/room controller that ends with the five steps in §4; then `customPast = "tt_pluto_past"`.

Either way pass `hasCustomPast: true`; with `false` the blacksmith never registers Pluto, `PastAccessible` stays `false`, and the Ark just opens the win Ammonomicon. For testing, the MtG console command `load_level <dungeonSceneName>` (`ETGModConsole.LoadLevel`) jumps straight to any registered level.

---

## 8. Files consulted

- IL dumps (scratchpad `il/`): `alexandria.il` (0.5.10), `game.il` (GameLibs 2.1.9.1 stub), `mtg.il` (MtG API 1.9.2), plus `0Harmony.dll` / `MonoMod.Utils.dll` for enum values.
- Alexandria `main`: `CharApi/Tools/CharApiHooks.cs`, `CharApi/CharacterBuilding/{CharacterBuilder,Loader,CustomCharacter,FoyerCharacterHandler}.cs`, `CharApi/CustomCharacterBlackSmithHandler.cs`.
- fedes1to/EtG-source `c49b17a`: `ArkController.cs`, `GameManager.cs`, `DungeonDatabase.cs`, `GameStatsManager.cs`, `TimeTubeCreditsController.cs`, `AmmonomiconDeathPageController.cs`, `PilotPastController.cs`, `RobotPastController.cs`, `PastLabMarineController.cs`, `ConvictPastController.cs`, `GuidePastController.cs`, `CoopPastController.cs`, `BulletPastRoomController.cs`, `BulletThatCanKillThePast.cs`, `PlayerController.cs`, `Dungeonator/Dungeon.cs`.
- Mods: Some-Bunny/Modular `Module.cs`, `Past/PastFloorSetup.cs`, `Past/OtherFloor/PDashTwo.cs`, `Past/Prefabs/Objects/Solid Objects/Spaceship.cs`, `Code/Enemies/Bosses/ModularPrime.cs`; bobot-dev/enter-the-beyond `Module.cs`, `Floors/LostPastDungeon.cs`, `Floors/LostPastController.cs`, `Floors/ToolsForFloors/FloorHooks.cs`, `ToolsAndStuff/Hooks.cs`; pcrain/GungeonCraft `src/Cwaff-Flows/CwaffDungeons.cs`; ApacheThunder/ExpandTheGungeon `ExpandComponents/ExpandArkController.cs`.
- Thunderstore: Alexandria changelog, `api/experimental/package/TeamPlanetside/Modular_Remastered/`.

---

## 9. Not verified / caveats

1. **Nothing was run in-game** (no game install on this machine). Everything is static analysis of IL and source.
2. **Mid-game save on resume.** Vanilla writes `DoMidgameSave(FINALGEON)` *before* Alexandria's check runs. `GameManager.DelayedLoadMidgameSave` has a `switch` over `playerOneData.CharacterIdentity` with no `default` for the `FINALGEON` case, so a custom identity yields no level load if the player quits inside the past and presses "continue" at the Breach elevator. I did not find code in Alexandria, Modular or Beyond that invalidates or handles that save; whether the elevator prompt even appears for it is unverified.
3. **`fs_*` → `Finalscenario_*` mapping** of the vanilla past definitions (they live in the serialized `_GameManager` prefab, not in code) is inferred from the mods loading `Finalscenario_Soldier`; the exact `dungeonPrefabPath` strings for the other pasts were not read.
4. **`Shared.GetEnumeratorField` matching rule**: it uses `AccessTools.GetDeclaredFields(type).Find(predicate)`; the predicate body (how `"shotPlayer"` matches the game's `<shotPlayer>__0`) was not read, but the hook demonstrably works for Modular/Beyond.
5. **Blacksmith FSM for unregistered identities**: what the PlayMaker `CharacterClassSwitch` does when the identity is absent from `compareTo` (i.e. `hasPast == false`) was not traced; the assumption "no bullet" follows from Alexandria only adding `hasPast` characters and from `PastAccessible` being set solely by the bullet pickup.
6. **Persistence of `KILLED_PAST` for extended enum values** across sessions: `m_characterStats` is `[fsProperty]` (FullSerializer) with `PlayableCharacters` keys; both Modular and Beyond also mirror the flag into their own SaveAPI flags and re-apply it at start-up, which suggests (but does not prove) vanilla persistence of custom keys is unreliable or load-order dependent.
7. **Breach card label** for `metaCost == 0`: vanilla `FoyerCharacterSelectFlag`/`FoyerInfoPanelController` visibility logic for `PastKilledLabel` with a custom identity was not read.
8. **Time tube for custom identities**: `TimeTubeCreditsController` only branches on `Convict` (decay power) and `IsGunslingerPast` (diorama), so no crash is expected, but this is inferred, not observed.
9. Thunderstore claims "Custom Pasts (You still have to make the Past yourself)" in the Alexandria package description — consistent with the code, quoted from a search snippet rather than the page itself.
