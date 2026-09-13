# Custom PAST level for Enter the Gungeon + Alexandria 0.5.10 DungeonAPI (state as of 2026-09-13)

Goal: one custom room (vet clinic: carrier crate, examination table) containing a custom boss, entered through the Gun That Can Kill The Past, and ending with the normal "past killed" sequence (credits tube, Ammonomicon victory page, return to Breach).

How this was researched (important for trust):

* `PlutoTheCat/packages/EtG.GameLibs.2.1.9.1/lib/net35/Assembly-CSharp.dll` is a **publicized stub**: `monodis` shows 38,800 of 40,507 methods with a 2-byte body (`ldnull; throw`) and zero `ldstr`. It is good for **signatures, fields and enum values only**. IL dumps: `scratchpad/il2/game.il` (692k lines), `scratchpad/il2/game.types`.
* Method **bodies** quoted below come from an AssetRipper export of the real game on GitHub: `https://github.com/fedes1to/EtG-source/tree/main/ExportedProject/Assets/MonoScript/Assembly-CSharp/` (copies in `scratchpad/src/decomp/`). Every signature quoted from there was cross-checked against the 2.1.9.1 stub IL.
* `packages/EtG.Alexandria.0.5.10/lib/net35/Alexandria.dll` is a real assembly (`scratchpad/il2/alex.il`, 218k lines, 4,783 `ldstr`). Its public DungeonAPI surface was diffed against GitHub `main` (`https://github.com/Nevernamed22/Alexandria`, last DungeonAPI commit 2026-01-28); every method quoted in §3 is present in the shipped 0.5.10 DLL unless flagged.
* Mods: GungeonCraft (pcrain), Modular (Some-Bunny — ships a **custom past for a custom character**, the closest precedent), Planetside, ExpandTheGungeon (BepInEx port), OnceMoreIntoTheBreach, SpecialAPI/Load-Level, MtG API, the mtgmodders "Making a floor" guide.

---

## 1. Vanilla past pipeline

### 1.1 Prerequisite flags

`BulletThatCanKillThePast : PassiveItem` (`decomp/BulletThatCanKillThePast.cs`):

```csharp
public override void Pickup(PlayerController player)
{
    ...
    GameManager.Instance.PrimaryPlayer.PastAccessible = true;
    Shader.SetGlobalFloat("_MapActive", 1f);
    base.Pickup(player);
}
```

`ArkController.CharacterStoryComplete` (`decomp/ArkController.cs:523`):

```csharp
private bool CharacterStoryComplete(PlayableCharacters shotCharacter)
{
    return GameStatsManager.Instance.GetFlag(GungeonFlags.BLACKSMITH_BULLET_COMPLETE) && GameManager.Instance.PrimaryPlayer.PastAccessible;
}
```

### 1.2 The gun is fired inside `ArkController` (the "Cache of the Ammulich" after the Dragun)

`ArkController : MonoBehaviour, IPlayerInteractable` (stub IL confirms `Interact`, `Open`, `HandleClockhair`, `ResetPlayers([opt] bool isGunslingerPast)`, `CharacterStoryComplete`). `Interact` → `Open` → `yield return StartCoroutine(HandleClockhair(interactor));`. The tail of `HandleClockhair` (`decomp/ArkController.cs:406-486`) is the **PlayableCharacters → past-scene mapping**:

```csharp
TimeTubeCreditsController ttcc = new TimeTubeCreditsController();
bool isShortTunnel = didShootHellTrigger || shotPlayer.characterIdentity == PlayableCharacters.CoopCultist || CharacterStoryComplete(shotPlayer.characterIdentity);
UnityEngine.Object.Destroy(m_heldPastGun.gameObject);
interactor.ToggleGunRenderers(true, "ark");
GameCursorController.CursorOverride.RemoveOverride("ark");
Pixelator.Instance.LerpToLetterbox(0.35f, 0.25f);
yield return StartCoroutine(ttcc.HandleTimeTubeCredits(clockhair.sprite.WorldCenter, isShortTunnel, clockhair.spriteAnimator, (!didShootHellTrigger) ? shotPlayer.PlayerIDX : 0));
if (isShortTunnel)
{
    Pixelator.Instance.FadeToBlack(1f);
    yield return new WaitForSeconds(1f);
}
if (didShootHellTrigger)
{
    GameManager.DoMidgameSave(GlobalDungeonData.ValidTilesets.HELLGEON);
    GameManager.Instance.LoadCustomLevel("tt_bullethell");
}
else if (shotPlayer.characterIdentity == PlayableCharacters.CoopCultist)
{
    GameManager.IsCoopPast = true;
    ResetPlayers();
    GameManager.Instance.LoadCustomLevel("fs_coop");
}
else if (CharacterStoryComplete(shotPlayer.characterIdentity) && shotPlayer.characterIdentity == PlayableCharacters.Gunslinger)
{
    GameManager.DoMidgameSave(GlobalDungeonData.ValidTilesets.FINALGEON);
    GameManager.IsGunslingerPast = true;
    ResetPlayers(true);
    GameManager.Instance.LoadCustomLevel("tt_bullethell");
}
else if (CharacterStoryComplete(shotPlayer.characterIdentity))
{
    bool flag = false;
    GameManager.DoMidgameSave(GlobalDungeonData.ValidTilesets.FINALGEON);
    switch (shotPlayer.characterIdentity)
    {
    case PlayableCharacters.Convict: flag = true; ResetPlayers(); GameManager.Instance.LoadCustomLevel("fs_convict"); break;
    case PlayableCharacters.Pilot:   flag = true; ResetPlayers(); GameManager.Instance.LoadCustomLevel("fs_pilot");   break;
    case PlayableCharacters.Guide:   flag = true; ResetPlayers(); GameManager.Instance.LoadCustomLevel("fs_guide");   break;
    case PlayableCharacters.Soldier: flag = true; ResetPlayers(); GameManager.Instance.LoadCustomLevel("fs_soldier"); break;
    case PlayableCharacters.Robot:   flag = true; ResetPlayers(); GameManager.Instance.LoadCustomLevel("fs_robot");   break;
    case PlayableCharacters.Bullet:  flag = true; ResetPlayers(); GameManager.Instance.LoadCustomLevel("fs_bullet");  break;
    }
    if (!flag) { AmmonomiconController.Instance.OpenAmmonomicon(true, true); }
    else       { GameUIRoot.Instance.ToggleUICamera(false); }
}
else
{
    AmmonomiconController.Instance.OpenAmmonomicon(true, true);
}
while (true) { yield return null; }
```

(The `switch` cases are collapsed to one line each here; the original has them on separate lines.) The same mapping is duplicated in `GameManager.DelayedLoadMidgameSave` (`decomp/GameManager.cs:1685-1712`) for resuming a mid-game save with `levelSaved == FINALGEON`. Note that the vanilla code never gives a custom `PlayableCharacters` value a past: `flag` stays `false` and the plain victory Ammonomicon opens.

### 1.3 Scene / prefab names (authoritative table from the `_GameManager` prefab)

`https://github.com/fedes1to/EtG-source/blob/main/ExportedProject/Assets/Asset_Bundles/brave_resources_001/resourcesbundle/_GameManager.prefab` (`scratchpad/src/decomp/_GameManager.prefab`, lines 67-320). `dungeonFloors` holds the critical path (`tt_foyer/Base_Foyer`, `tt_castle/Base_Castle`, `tt5/Base_Gungeon`, `tt_mines/Base_Mines`, `tt_catacombs/Base_Catacombs`, `tt_forge/Base_Forge`, `tt_bullethell/Base_BulletHell`); `customFloors` holds everything else, including all pasts:

| `dungeonSceneName` | `dungeonPrefabPath` | Character | `flowEntries` |
|---|---|---|---|
| `fs_pilot` | `FinalScenario_Pilot` | Pilot | `[]` |
| `fs_convict` | `FinalScenario_Convict` | Convict | `[]` |
| `fs_soldier` | `FinalScenario_Soldier` | Marine (`PlayableCharacters.Soldier`) | `[]` |
| `fs_guide` | `FinalScenario_Guide` | Hunter (`PlayableCharacters.Guide`) | `[]` |
| `fs_coop` | `FinalScenario_Coop` | Cultist | `[]` |
| `fs_robot` | `FinalScenario_Robot` | Robot | `[]` |
| `fs_bullet` | `FinalScenario_Bullet` | Bullet | `[]` |
| `tt_bullethell` (+`GameManager.IsGunslingerPast`) | `Base_BulletHell` | Gunslinger | (normal) |

Asset-bundle names are `dungeons/finalscenario_<x>` (lower-case; `DungeonDatabase.GetOrLoadByName` lower-cases the bundle name). Mods list them verbatim, e.g. MtG API `ModTheGungeonAPI/LoadHelper.cs:148-154` and Alexandria `CharApi/Tools/Tools.cs:56-62`. `PlayableCharacters` in 2.1.9.1: `Pilot=0, Convict=1, Robot=2, Ninja=3, Cosmonaut=4, Soldier=5, Guide=6, CoopCultist=7, Bullet=8, Eevee=9, Gunslinger=10`.

### 1.4 `GameManager.LoadCustomLevel` and what it does with the name

`decomp/GameManager.cs:1529` (signature confirmed in stub IL: `instance default void LoadCustomLevel (string 'custom')`):

```csharp
public void LoadCustomLevel(string custom)
{
    if (dungeonFloors == null || dungeonFloors.Count == 0) { ... }
    m_loadingLevel = true;
    FlushAudio();
    ClearPerLevelData();
    GameLevelDefinition gameLevelDefinition2 = null;
    int num = -1;
    for (int i = 0; i < dungeonFloors.Count; i++)
    {
        if (dungeonFloors[i].dungeonSceneName == custom) { gameLevelDefinition2 = dungeonFloors[i]; num = i + 1; break; }
    }
    if (gameLevelDefinition2 == null)
    {
        for (int j = 0; j < customFloors.Count; j++)
        {
            if (customFloors[j].dungeonSceneName == custom) { gameLevelDefinition2 = customFloors[j]; break; }
        }
    }
    if (gameLevelDefinition2 != null && gameLevelDefinition2.dungeonPrefabPath == string.Empty)
    {
        ... "MainMenu" / "Foyer" / SceneManager.LoadScene(...)
    }
    else
    {
        StartCoroutine(LoadNextLevelAsync_CR(gameLevelDefinition2));
        ...
    }
}
```

So **a "level" is just a `GameLevelDefinition` found by `dungeonSceneName`**; the scene itself is always the shared `dungeon_scene_001` bundle scene. `LoadNextLevelAsync_CR` (`decomp/GameManager.cs:2183-2275`):

```csharp
SceneManager.LoadScene("LoadingDungeon");
...
AssetBundle assetBundle2 = ResourceManager.LoadAssetBundle("dungeon_scene_001");
async = ResourceManager.LoadSceneAsyncFromBundle(assetBundle2, LoadSceneMode.Additive);
...
m_lastLoadedLevelDefinition = gld;
if (!string.IsNullOrEmpty(gld.dungeonPrefabPath))
{
    CurrentlyGeneratingDungeonPrefab = DungeonDatabase.GetOrLoadByName(gld.dungeonPrefabPath);
}
if (CurrentlyGeneratingDungeonPrefab != null)
{
    int dungeonSeed = CurrentlyGeneratingDungeonPrefab.GetDungeonSeed();
    ...
    DungeonFlow targetFlow = null;
    if (!string.IsNullOrEmpty(InjectedFlowPath)) { targetFlow = FlowDatabase.GetOrLoadByName(InjectedFlowPath); InjectedFlowPath = null; }
    if (gld.flowEntries.Count > 0)
    {
        flowEntry = gld.LovinglySelectDungeonFlow();
        if (flowEntry != null)
        {
            DungeonFlow orLoadByName = FlowDatabase.GetOrLoadByName(flowEntry.flowPath);
            if (orLoadByName == null) orLoadByName = FlowDatabase.GetOrLoadByName("Boss Rooms/" + flowEntry.flowPath);
            if (orLoadByName == null) orLoadByName = FlowDatabase.GetOrLoadByName("Boss Rush Flows/" + flowEntry.flowPath);
            if (orLoadByName == null) orLoadByName = FlowDatabase.GetOrLoadByName("Testing/" + flowEntry.flowPath);
            if (targetFlow == null) targetFlow = orLoadByName;
        }
    }
    LoopDungeonGenerator ldg = new LoopDungeonGenerator(CurrentlyGeneratingDungeonPrefab, dungeonSeed);
    if (targetFlow != null) { ldg.AssignFlow(targetFlow); }
    gld.lastSelectedFlowEntry = flowEntry;
    IEnumerator tracker = ldg.GenerateDungeonLayoutDeferred().GetEnumerator();
    while (tracker.MoveNext()) { yield return null; }
    ...
    PregeneratedDungeonData = ldg.DeferredGeneratedData;
    DungeonToAutoLoad = CurrentlyGeneratingDungeonPrefab;
```

Flow precedence: `GameManager.InjectedFlowPath` > `gld.flowEntries` > (nothing assigned ⇒ `LoopDungeonGenerator` ctor picks `m_patternSettings.GetRandomFlow()` from the **Dungeon prefab's own `PatternSettings.flows`**, `decomp/Dungeonator/LoopDungeonGenerator.cs:35`). The pasts have `flowEntries: []`, so their flow comes from the `FinalScenario_*` prefab. `Dungeon.Start` then consumes `GameManager.Instance.PregeneratedDungeonData` (`decomp/Dungeonator/Dungeon.cs:426-434`) and assembles tiles with `TK2DDungeonAssembler.Initialize(tileIndices)`.

`DungeonDatabase.GetOrLoadByName` / `FlowDatabase.GetOrLoadByName` (both `public static`, confirmed in stub IL) — these are the two hook points every custom-floor mod uses:

```csharp
public static Dungeon GetOrLoadByName(string name)
{
    AssetBundle assetBundle = ResourceManager.LoadAssetBundle("dungeons/" + name.ToLower());
    Dungeon component = assetBundle.LoadAsset<GameObject>(name).GetComponent<Dungeon>();
    return component;
}
public static DungeonFlow GetOrLoadByName(string name)   // FlowDatabase
{
    if (!m_assetBundle) m_assetBundle = ResourceManager.LoadAssetBundle("flows_base_001");
    string text = name;
    if (text.Contains("/")) text = name.Substring(name.LastIndexOf("/") + 1);
    DungeonFlow result = m_assetBundle.LoadAsset<DungeonFlow>(text);
    return result;
}
```

`GameManager.LoadCustomFlowForDebug` (`decomp/GameManager.cs:1467`; stub IL: `LoadCustomFlowForDebug (string flowpath, [opt] string dungeonPrefab, [opt] string sceneName)`) builds a throw-away `GameLevelDefinition`:

```csharp
DungeonFlow orLoadByName = FlowDatabase.GetOrLoadByName(flowpath);
... ("Boss Rooms/", "Boss Rush Flows/", "Testing/" fallbacks) ...
if (orLoadByName == null) return;
m_loadingLevel = true; FlushAudio(); ClearPerLevelData();
float priceMultiplier = 1f; float enemyHealthMultiplier = 1f;
if (!string.IsNullOrEmpty(sceneName)) { /* copies multipliers from customFloors/dungeonFloors entry with that dungeonSceneName */ }
GameLevelDefinition gameLevelDefinition = new GameLevelDefinition();
gameLevelDefinition.dungeonPrefabPath = ((!string.IsNullOrEmpty(dungeonPrefab)) ? dungeonPrefab : "Base_Gungeon");
gameLevelDefinition.dungeonSceneName = ((!string.IsNullOrEmpty(sceneName)) ? sceneName : "BB_Beholster");
...
DungeonFlowLevelEntry dungeonFlowLevelEntry = new DungeonFlowLevelEntry();
dungeonFlowLevelEntry.flowPath = flowpath;
dungeonFlowLevelEntry.forceUseIfAvailable = true;
dungeonFlowLevelEntry.prerequisites = new DungeonPrerequisite[0];
dungeonFlowLevelEntry.weight = 1f;
gameLevelDefinition.flowEntries.Add(dungeonFlowLevelEntry);
StartCoroutine(LoadNextLevelAsync_CR(gameLevelDefinition));
```

It only works for a **custom** flow if `FlowDatabase.GetOrLoadByName` is hooked to return it (ExpandTheGungeon, GungeonCraft and Planetside all do this; see §4).

### 1.5 How a custom (CharacterAPI) character gets a past — Alexandria's hook

`https://github.com/Nevernamed22/Alexandria/blob/main/CharApi/Tools/CharApiHooks.cs:152-181` (IL-manipulator on the `HandleClockhair` enumerator). **Verified in the shipped 0.5.10 DLL**: `alex.types:380` lists `Alexandria.CharacterAPI.Hooks/CustomPastHandlerPatches`, and the IL of `DoCustomPastChecks` (`alex.il:~183300`) contains `callvirt ... ArkController::ResetPlayers(bool)` followed by `callvirt ... GameManager::LoadCustomLevel(string)`:

```csharp
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
    cursor.Emit(OpCodes.Ldarg_0);
    cursor.Emit(OpCodes.Ldfld, original.DeclaringType.GetEnumeratorField("$this"));
    cursor.Emit(OpCodes.Ldarg_0);
    cursor.Emit(OpCodes.Ldfld, original.DeclaringType.GetEnumeratorField("shotPlayer"));
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
```

`CustomCharacter.past` / `hasPast` are set by `CharacterBuilder.BuildCharacter` (`CharApi/CharacterBuilding/CharacterBuilder.cs:109-111`: `customCharacter.past = customPast; customCharacter.hasPast = hasCustomPast; data.hasPast = hasCustomPast;`), which is what `Loader.BuildCharacter(..., int metaCost = 0, bool hasCustomPast = false, string customPast = "")` forwards (signature already recorded in `docs/research/01-custom-character-research.md`). **So for Pluto the whole "trigger" is: pass `customPast: "<our dungeonSceneName>"` to `BuildCharacter`, and make `GameManager.Instance.LoadCustomLevel("<our dungeonSceneName>")` resolve to our level.** The branch runs after `CharacterStoryComplete(...)` (i.e. after the `BLACKSMITH_BULLET_COMPLETE` flag + `PastAccessible`), inside the `else if (CharacterStoryComplete(...))` block, so the mid-game save with `FINALGEON` has already been written. The victory-photo hook (`CharApiHooks.cs:511-512`) uses `cc.data.pastWinPic` when `tilesetId == FINALGEON`.

### 1.6 The ending: what happens after the past boss dies

Per-past controllers (`PilotPastController`, `ConvictPastController`, `GuidePastController`, `RobotPastController`, `PastLabMarineController`, `BulletPastRoomController`, `CoopPastController`) all follow the same shape. Simplest one, `decomp/PastLabMarineController.cs:249-302`:

```csharp
public void OnBossKilled()
{
    m_inCombat = false;
    GameStatsManager.Instance.SetCharacterSpecificFlag(PlayableCharacters.Soldier, CharacterSpecificGungeonFlags.KILLED_PAST, true);
    GameStatsManager.Instance.RegisterStatChange(TrackedStats.TIMES_KILLED_PAST, 1f);
    GameStatsManager.Instance.SetFlag(GungeonFlags.BOSSKILLED_SOLDIER_PAST, true);
    StartCoroutine(HandleBossKilled());
}

private IEnumerator HandleBossKilled()
{
    yield return new WaitForSeconds(3.5f);
    GameManager.Instance.PrimaryPlayer.transform.position = AreaDoor.transform.position + new Vector3(0f, 11f, 0f);
    GameManager.Instance.PrimaryPlayer.specRigidbody.Reinitialize();
    ...
    VictoryTalkDoer.gameObject.SetActive(true);
    PlayerController m_soldier = GameManager.Instance.PrimaryPlayer;
    PastCameraUtility.LockConversation(m_soldier.CenterPosition);
    GameManager.Instance.MainCameraController.SetManualControl(true, false);
    GameManager.Instance.MainCameraController.OverridePosition = m_soldier.CenterPosition;
    yield return new WaitForSeconds(0.5f);
    ...
    Pixelator.Instance.FadeToColor(2f, Color.white, true);
    yield return new WaitForSeconds(2f);
    VictoryTalkDoer.Interact(GameManager.Instance.PrimaryPlayer);
    GameManager.Instance.MainCameraController.OverridePosition = m_soldier.CenterPosition;
    while (VictoryTalkDoer.IsTalking) { yield return null; }
    yield return new WaitForSeconds(0.5f);
    Pixelator.Instance.FreezeFrame();
    BraveTime.RegisterTimeScaleMultiplier(0f, base.gameObject);
    float ela = 0f;
    while (ela < ConvictPastController.FREEZE_FRAME_DURATION) { ela += GameManager.INVARIANT_DELTA_TIME; yield return null; }
    BraveTime.ClearMultiplier(base.gameObject);
    TimeTubeCreditsController ttcc = new TimeTubeCreditsController();
    ttcc.ClearDebris();
    yield return StartCoroutine(ttcc.HandleTimeTubeCredits(m_soldier.sprite.WorldCenter, false, null, -1));
    AmmonomiconController.Instance.OpenAmmonomicon(true, true);
}
```

Key facts:

* **Flag**: `CharacterSpecificGungeonFlags.KILLED_PAST = 1000 (0x3e8)`, `KILLED_PAST_ALTERNATE_COSTUME = 1001`; stat `TrackedStats.TIMES_KILLED_PAST = 50`. `GameStatsManager.SetCharacterSpecificFlag(PlayableCharacters, flag, bool)` (`decomp/GameStatsManager.cs:505-545`) additionally sets `KILLED_PAST_ALTERNATE_COSTUME` and `GungeonFlags.ITEMSPECIFIC_ALTERNATE_GUNS_UNLOCKED` when `playerController.IsUsingAlternateCostume`, and `FLAG_EEVEE_UNLOCKED` for a temporary Eevee. Modular calls it with the extended enum: `GameStatsManager.Instance.SetCharacterSpecificFlag(ETGModCompatibility.ExtendEnum<PlayableCharacters>(Module.GUID, Modular_Character_Data.nameShort), CharacterSpecificGungeonFlags.KILLED_PAST, ...)` (`Modular/Module.cs:328`).
* **Credits**: `TimeTubeCreditsController.HandleTimeTubeCredits(Vector2 decayCenter, bool skipCredits, tk2dSpriteAnimator optionalAnimatorToDisable, int shotPlayerID, bool quickEndShatter = false)` (a plain `new TimeTubeCreditsController()` — it is not a MonoBehaviour). With `skipCredits == false` it scrolls the credits, shatters the tube and adds `"Global Prefabs/PastGameCompletePanel"` if `GetCharacterSpecificFlag(PrimaryPlayer.characterIdentity, KILLED_PAST)` is already true, otherwise `"Global Prefabs/StandardGameCompletePanel"` (`decomp/TimeTubeCreditsController.cs:285-300`) — so set the flag **before** starting the tube. Static `IsTimeTubing` is true during it. It spawns `"GungeonPastDiorama"` (or `"GungeonTruePastDiorama"` when `IsGunslingerPast`).
* **Victory page**: `AmmonomiconController.OpenAmmonomicon(bool isDeath, bool isVictory)` with `(true, true)` opens the death/victory pages; `AmmonomiconDeathPageController.SetWinPic` switches on `GameManager.Instance.Dungeon.tileIndices.tilesetId` — `case FINALGEON:` picks `Win_Pic_Convict_001`/`Pilot`/`Marine`/`Hunter`/`Robot`/`Bullet`, default `Win_Pic_Gun_Get_001` (`decomp/AmmonomiconDeathPageController.cs:524-546`). Alexandria overrides that to `cc.data.pastWinPic` for custom characters. The page's "main menu" button → `SaveManager.DeleteCurrentSlotMidGameSave(); ... GameManager.Instance.LoadCharacterSelect(true);` (`decomp/AmmonomiconDeathPageController.cs:611-656`) — that is the return to the Breach.
* **Who calls `OnBossKilled`**: the boss's own controller, e.g. `BossFinalRogueController.Start`: `m_pastController = UnityEngine.Object.FindObjectOfType<PilotPastController>();`. For a custom boss the equivalent is subscribing to `aiActor.healthHaver.OnPreDeath` (GungeonCraft Sans: `base.aiActor.healthHaver.OnPreDeath += OnPreDeath;`, with `healthHaver.forcePreventVictoryMusic = true`).
* **Camera/cutscene helpers** (`decomp/PastCameraUtility.cs`, static, both in stub IL):

```csharp
public static void LockConversation(Vector2 lockPos)
{
    GameManager.Instance.PrimaryPlayer.SetInputOverride("past");
    if (GameManager.Instance.CurrentGameType == GameManager.GameType.COOP_2_PLAYER) GameManager.Instance.SecondaryPlayer.SetInputOverride("past");
    Pixelator.Instance.LerpToLetterbox(0.35f, 0.25f);
    Pixelator.Instance.DoFinalNonFadedLayer = true;
    GameUIRoot.Instance.ToggleLowerPanels(false, false, string.Empty);
    GameUIRoot.Instance.HideCoreUI(string.Empty);
    CameraController mainCameraController = GameManager.Instance.MainCameraController;
    mainCameraController.SetManualControl(true);
    mainCameraController.OverridePosition = lockPos.ToVector3ZUp();
}
public static void UnlockConversation() { ... ClearInputOverride("past") ... LerpToLetterbox(0.5f, 0.25f) ... ShowCoreUI ... SetManualControl(false); }
```

* **Intro**: `PilotPastController.Start` waits `while (Dungeon.IsGenerating) yield return null;`, calls `Pixelator.Instance.TriggerPastFadeIn();`, runs `TalkDoerLite` conversations, and triggers the boss with `GenericIntroDoer.TriggerSequence(GameManager.Instance.PrimaryPlayer)` on the `HealthHaver` that `IsBoss` and whose `GenericIntroDoer.triggerType == GenericIntroDoer.TriggerType.BossTriggerZone` (`TriggerType { PlayerEnteredRoom = 10, BossTriggerZone = 20 }`).

Modular's custom past reproduces exactly this ending inside a placed room object (`Modular/Past/Prefabs/Objects/Solid Objects/Spaceship.cs:174-201`):

```csharp
Pixelator.Instance.FreezeFrame();
BraveTime.RegisterTimeScaleMultiplier(0f, base.gameObject);
float ela = 0f;
while (ela < ConvictPastController.FREEZE_FRAME_DURATION) { ela += GameManager.INVARIANT_DELTA_TIME; yield return null; }
...
BraveTime.ClearMultiplier(base.gameObject);
TimeTubeCreditsController ttcc = new TimeTubeCreditsController();
Pixelator.Instance.FadeToColor(0.15f, Color.white, true, 0.15f);
ttcc.ClearDebris();
yield return base.StartCoroutine(ttcc.HandleTimeTubeCredits(GameManager.Instance.PrimaryPlayer.sprite.WorldCenter, false, null, -1, false));
AmmonomiconController.Instance.OpenAmmonomicon(true, true);
```

---

## 2. What a past dungeon contains

### 2.1 It is an ordinary Dungeonator dungeon with a fixed flow, not a hand-placed Unity scene

Evidence: every past goes through `LoadNextLevelAsync_CR` → `DungeonDatabase.GetOrLoadByName("FinalScenario_*")` → `LoopDungeonGenerator` (§1.4); the controllers wait on `Dungeon.IsGenerating`; the boss's `GenericIntroDoer` has `triggerType == BossTriggerZone`.

The exported Dungeon prefab YAML (`https://github.com/fedes1to/EtG-source/blob/main/ExportedProject/Assets/Asset_Bundles/dungeons/finalscenario_soldier/data/dungeons/FinalScenario_Soldier.prefab`, copy in `scratchpad/src/decomp/`) shows, for the Marine past:

```yaml
m_Name: FinalScenario_Soldier
DungeonShortName: '#SCIENCELAB_SHORTNAME'
DungeonFloorName: '#SCIENCELAB_NAME'
DungeonFloorLevelTextOverride: '#SCIENCELAB_SECONDLINE'
LevelOverrideType: 5            # GameManager.LevelOverrideState.CHARACTER_PAST
PatternSettings: mandatoryExtraRooms: []  MAX_GENERATION_ATTEMPTS: 250  (flows: one guid-referenced DungeonFlow)
tileIndices:  tilesetId: 16384  # GlobalDungeonData.ValidTilesets.FINALGEON
              dungeonCollection: {guid: 0729565a2b6877d438f3b47b84e61997}
              placeBorders: 1   placePits: 0
UsesCustomFloorIdea: 0
PlaceDoors: 1
StripPlayerOnArrival: 0   SuppressEmergencyCrates: 0   PlayerIsLight: 0
PrefabsToAutoSpawn: []
musicEventName: Play_MUS_Ending_Marine_01
```

`FinalScenario_Guide` is identical except `'#NAZICASTLE_*'` names and `Play_MUS_Ending_Guide_01`, and it references the **same** `dungeonCollection` guid `0729565a...` — i.e. one shared "FINALGEON" sprite collection is used by (at least) the Marine and Hunter pasts, with per-room material/visual-type selecting the look (see caveats).

`GameManager.LevelOverrideState { NONE, FOYER, TUTORIAL, RESOURCEFUL_RAT, END_TIMES, CHARACTER_PAST, DEBUG_TEST }`; `GameManager.CurrentLevelOverrideState` simply returns `Dungeon.LevelOverrideType` (or the generating prefab's while loading). `CHARACTER_PAST` gates a few things in `Dungeon.cs` (Pilot coop ship prefab at :1624, Convict shadow-caster layers at :1660) and, via `tilesetId == FINALGEON`, the win-pic switch; `CurrentLevelOverrideState != NONE` disables normal-floor extras (glitch chests, sherpa, etc. — `Dungeon.cs:860/913/1232/1289/1438`).

The vanilla rooms of each past are `PrototypeDungeonRoom` assets placed by the flow, with the boss (`enemyBehaviourGuid`) and the `*PastController`/`TalkDoerLite` NPCs as placed objects; the flow/room YAML itself was not retrievable (the export's tree listing is truncated at 52k entries), so the exact node list per past is **not verified** — but the loading code above proves nothing else can supply the layout.

### 2.2 Minimum component set for our own past

| Vanilla piece | Our equivalent |
|---|---|
| `GameLevelDefinition` row in `customFloors` (`fs_x` → `FinalScenario_X`) | our row `{ dungeonSceneName = "tt_pluto_past", dungeonPrefabPath = "base_pluto_past", flowEntries = [] }` |
| `FinalScenario_X` Dungeon prefab (`LevelOverrideType = CHARACTER_PAST`, `tilesetId = FINALGEON`, `PatternSettings.flows = [flow]`) | hook `DungeonDatabase.GetOrLoadByName("base_pluto_past")` → clone a template prefab and set the same fields (Modular sets both `LevelOverrideType = CHARACTER_PAST` and `tilesetId = FINALGEON`, `Modular/Past/OtherFloor/PDashTwo.cs:248,389`) |
| Fixed flow with the past rooms | `DungeonFlow` with ENTRANCE node = clinic room (`overrideExactRoom`), optionally a second BOSS node |
| `*PastController` placed object | a `DungeonPlaceableBehaviour`/`BraveBehaviour` placed in the room (or added to the boss) that: waits `Dungeon.IsGenerating`, `Pixelator.TriggerPastFadeIn()`, runs intro, subscribes `healthHaver.OnPreDeath`, then runs the §1.6 ending |
| Boss with `GenericIntroDoer.triggerType = BossTriggerZone` | custom boss (Alexandria EnemyAPI / BuildABoss pattern); `GetGenericBossRoom` below sets `p.category = BOSS`, `UseCustomMusicState`, unseal-on-clear |

---

## 3. Alexandria 0.5.10 DungeonAPI — exact public API

Namespace `Alexandria.DungeonAPI`; classes in 0.5.10: `DungeonHandler`, `DungeonHooks`, `DungeonPatches`, `MasteryOverrideHandler`, `OfficialFlows` (**internal**: `.class private auto ansi beforefieldinit OfficialFlows`), `RoomFactory` (+ nested `RoomData` struct), `RoomIcons`, `RoomUtility`, `RuntimeDungeonEditing`, `SampleFlow`, `SetupExoticObjects`, `ShrineTools`, `SpecialComponents`, `StaticInjections`, `StaticReferences` (`scratchpad/il2/alex.types` lines 128-143). Initialised by `Alexandria.Module`: `StaticReferences.Init(); DungeonHandler.Init();` (`Module.cs:49-50`), so the asset bundles `shared_auto_001`, `shared_auto_002`, `brave_resources_001` (`StaticReferences.assetBundleNames`) and the room tables are ready before your plugin's `Start` if you depend on Alexandria.

### 3(a) Building a room

**From a `.room` file (RoomArchitectTool format).** RAT = "RoomArchitectTool" 3.0.10 on Thunderstore (`https://thunderstore.io/c/enter-the-gungeon/p/Alexandria/RoomArchitectTool/`, "Tool for creating custom room files, which can be put into the game to generate new rooms", exports "a unique file type which can be read by Alexandrias DungeonAPI"; the guide links a "RAT with custom enemy support" build at `https://modworkshop.net/mod/30432`). Format as read by Alexandria:

* `.room` = a **PNG** (tile colours) followed by the literal header `***DATA***` and a **JSON** `RoomData` (`RoomFactory.cs:39` `private static readonly string dataHeader = "***DATA***";`; `ExtractRoomData` scans backwards for the header and `JsonUtility.FromJson<RoomData>(...)`; the texture is `ImageConversion.LoadImage`d from the same bytes by `ResourceExtractor.GetTextureFromResource`, `ItemAPI/SpriteTools/ResourceExtractor.cs:145`).
* `.newroom` = JSON only; cells come from `RoomData.tileInfo`, one char per cell: `"1"` floor, `"2"` wall, `"3"` pit, `"4"` ice floor, `"5"` fire-goop floor, `"X"` floor, `"G"` grass, anything else wall (`TypeFromNumber`, `ReturnCellFloorType`, `RoomFactory.cs:576-680`).

```csharp
public struct RoomData
{
    public string tileInfo;
    public Vector2Int roomSize;
    public string[] waveTriggers;
    public string[] nodeTypes; public string[] nodeWrapModes; public Vector2[] nodePositions; public int[] nodePaths; public int[] nodeOrder;
    public string category; public string normalSubCategory; public string specialSubCategory; public string bossSubCategory;
    public Vector2[] enemyPositions; public string[] enemyGUIDs; public string[] enemyAttributes;
    public Vector2[] placeablePositions; public string[] placeableGUIDs; public string[] placeableAttributes;
    public int[] enemyReinforcementLayers;
    public Vector2[] exitPositions; public string[] exitDirections;
    public string[] floors;
    public float weight;
    public bool isSpecialRoom; public bool randomizeEnemyPositions; public bool doFloorDecoration; public bool doWallDecoration; public bool doLighting; public bool darkRoom;
    [NonSerialized] public string name;
    [NonSerialized] public PrototypeDungeonRoom room;
    public int visualSubtype;
    public string superSpecialRoomType;
    public float AmbientLight_R; public float AmbientLight_G; public float AmbientLight_B; public bool usesAmbientLight;
    public bool[] nodePathVisible;
    public string specialRoomPool;
    public float[] additionalPauseDelay;
}
```

(`RoomFactory.cs:2409-2461`; the 0.5.10 IL has the same nested `RoomFactory/RoomData`.) `exitDirections` strings are matched case-insensitively for `west/east/north/south` plus optional `exitonly` / `entryonly` (`DetermineExitType`, `DetermineDirectionType`, `RoomFactory.cs:258-291`). `category` etc. are parsed with `ShrineTools.GetEnumValue<PrototypeDungeonRoom.RoomCategory>(...)`; `floors` entries are `GlobalDungeonData.ValidTilesets` names and become `DungeonPrerequisite { prerequisiteType = TILESET, requiredTileset }` on the room.

Entry points (all `public static`, verified in `alex.il`):

```csharp
RoomFactory.RoomData BuildFromResource(string roomPath, Assembly assembly = null)      // embedded resource "Namespace/Folder/x.room"; builds, adds to RoomFactory.rooms, calls DungeonHandler.Register(roomData)
RoomFactory.RoomData BuildNewRoomFromResource(string roomPath, Assembly assembly = null) // same for .newroom (JSON only)
Dictionary<string, RoomData> LoadRoomsFromRoomDirectory(string modPrefix, string roomDirectory) // loose files on disk, both formats, registered
PrototypeDungeonRoom Build(RoomData roomData)                 // .newroom path, NOT registered
PrototypeDungeonRoom Build(Texture2D texture, RoomData roomData) // .room path, NOT registered
void ApplyRoomData(PrototypeDungeonRoom room, RoomData roomData)
```

Usage precedent (Modular's past, `Modular/Past/Prefabs/FloorRoomInitialisation.cs`):

```csharp
StartRoom = Alexandria.DungeonAPI.RoomFactory.BuildFromResource("ModularMod/Past/Rooms/ships_co.room").room;
StartRoom.customAmbientLight = new Color(0.3f, 0.3f, 0.3f, 1);
StartRoom.usesCustomAmbientLight = true;
StartRoom.overrideRoomVisualType = 1;
...
BossRoom = Alexandria.DungeonAPI.RoomFactory.BuildFromResource("ModularMod/Past/Rooms/past_boss_room.room").room;
BossRoom.overrideRoomVisualType = 2;
```

**Programmatically** (no editor):

```csharp
PrototypeDungeonRoom GetNewPrototypeDungeonRoom(int width = 12, int height = 12) // empty ScriptableObject with all lists initialised, RoomId random
PrototypeDungeonRoom CreateEmptyRoom(int width = 12, int height = 12)            // all-FLOOR cells (Stone) + 4 centred exits, UpdatePrecalculatedData()
RoomData CreateEmptyRoomData(int width = 12, int height = 12)                     // category "SECRET", weight 9999
```

Then set `room.FullCellData` / `room.m_cellData` yourself if you need walls/pits (Alexandria is publicised, so `m_cellData` is writable as `CreateEmptyRoom` does). GungeonCraft's minimal boss room (`https://github.com/pcrain/GungeonCraft/blob/master/src/Cwaff-Enemies/Bosses/BuildABoss.cs:1128-1164`, default branch):

```csharp
public static PrototypeDungeonRoom GetGenericBossRoom(int width, int height, bool exitOnBottom)
{
    PrototypeDungeonRoom p = Alexandria.DungeonAPI.RoomFactory.CreateEmptyRoom(width, height);
    p.category = PrototypeDungeonRoom.RoomCategory.BOSS;
    if (exitOnBottom)
    {
        p.exitData.exits.Clear();
        Alexandria.DungeonAPI.RoomFactory.AddExit(p, new Vector2(p.Width / 2, 0), DungeonData.Direction.SOUTH, PrototypeRoomExit.ExitType.ENTRANCE_ONLY);
        Alexandria.DungeonAPI.RoomFactory.AddExit(p, new Vector2(p.Width / 2, p.Height), DungeonData.Direction.NORTH, PrototypeRoomExit.ExitType.EXIT_ONLY);
    }
    p.UseCustomMusicState = true;
    p.OverrideMusicState = DungeonFloorMusicController.DungeonMusicState.CALM;
    p.roomEvents.Add(new RoomEventDefinition(RoomEventTriggerCondition.ON_ENEMIES_CLEARED, RoomEventTriggerAction.UNSEAL_ROOM));
    return p;
}
public static PrototypeDungeonRoom CreateStandaloneBossRoom(this GameObject self, BuildABoss bb, int width, int height, bool exitOnBottom)
{
    PrototypeDungeonRoom p = GetGenericBossRoom(width: width, height: height, exitOnBottom: exitOnBottom);
    Vector2 roomCenter = new Vector2(0.5f*p.Width, 0.5f*p.Height);
    tk2dBaseSprite anySprite = self.GetComponent<tk2dSpriteAnimator>().GetAnySprite();
    Vector2 spritePos = roomCenter - 2f * anySprite.GetRelativePositionFromAnchor(bb.spriteAnchor);
    AddObjectToRoom(p, spritePos.Quantize(C.PIXEL_SIZE), EnemyBehaviourGuid: bb.guid);
    AddObjectToRoom(p, roomCenter, NonEnemyBehaviour: bb.bossController);
    return p;
}
```

(`AddObjectToRoom` there builds a `PrototypePlacedObjectData { placeableContents | nonenemyBehaviour | enemyBehaviourGuid, contentsBasePosition, layer, ... }` and appends to `room.placedObjects` / `room.placedObjectPositions`, `BuildABoss.cs:1083-1120`. Sans is used as `overrideExactRoom` in a 3-node flow.)

### 3(b) Placing enemies / objects / exits

```csharp
void AddExit(PrototypeDungeonRoom room, Vector2 location, DungeonData.Direction direction, PrototypeRoomExit.ExitType exitType = PrototypeRoomExit.ExitType.NO_RESTRICTION)
    // creates PrototypeRoomExit(direction, location) { exitType, containsDoor = true, containedCells = [location + (0,1)|(1,0)] } and appends to room.exitData.exits
void AddEnemyToRoom(PrototypeDungeonRoom room, Vector2 location, string guid, string attributes, int layer, bool shuffle, RoomEventTriggerCondition reinforcementType)
    // DungeonPlaceable 1x1 with variantTiers[0].enemyPlaceableGuid = guid (attributes JSON "j": forceBlackPhantom); layer 0 -> room.placedObjects, layer>0 -> reinforcement layer;
    // ALWAYS adds ON_ENTER_WITH_ENEMIES→SEAL_ROOM and ON_ENEMIES_CLEARED→UNSEAL_ROOM room events
void AddEnemyToRoomLegecy(PrototypeDungeonRoom room, Vector2 location, string guid, int layer, bool shuffle)
void AddObjectDataToReinforcementLayer(PrototypeDungeonRoom room, PrototypePlacedObjectData objectData, int layer, Vector2 location, bool shuffle, RoomEventTriggerCondition reinforcementType)
void AddPlaceableToRoom(PrototypeDungeonRoom room, Vector2 location, string assetPath, string attributes, Dictionary<int, PrototypeEventTriggerArea> prototypeEventTriggerAreas)
void AddPlaceableToRoomLegecy(PrototypeDungeonRoom room, Vector2 location, string assetPath)
void AddNodeToRoom(PrototypeDungeonRoom room, Vector2 location, string guid, int layer, SerializedPath.SerializedPathWrapMode wrapMode, bool modifyTilemap, float delay)  // path nodes (saws, carts)
```

`AddPlaceableToRoom` resolves `assetPath` in this order (`RoomFactory.cs:787-1830`): a `GameObject` from the three Alexandria asset bundles (`GetGameObjectFromBundles`) → special-cased names (`godray`, `saw_blade_pathing`, `customsetupdeadblow`, chests via `MaybeModifyAsset` with JSON attrs `dI` item id, `jI` junk id, `mC` mimic chance, `cL` locked, `pV` prevent fuse, `isGlitched`) → `StaticReferences.customObjects[assetPath]` → `SetupExoticObjects.objects[assetPath]` → then `DungeonPlaceable`s: `GetPlaceableFromBundles`, `StaticReferences.customPlaceables[assetPath]`, `StoredRoomObjects`/`StoredDungeonPlaceables`. A resolved `GameObject` is wrapped as `DungeonPlaceable { width = 2, height = 2, variantTiers = [{ nonDatabasePlaceable = gameObject }] }`. Missing assets are aggregated and printed as `Unable to find asset in asset bundles: <name>`.

**Custom objects (carrier crate, examination table)**: register a prefab under a name and reference it by that name from the `.room`/code:

```csharp
public static Dictionary<string, GameObject> customObjects = new Dictionary<string, GameObject>();          // StaticReferences.cs:47
public static Dictionary<string, DungeonPlaceable> customPlaceables = new Dictionary<string, DungeonPlaceable>(); // :48
```

Planetside: `Alexandria.DungeonAPI.StaticReferences.customObjects.Add("abbeyButton", b);` (`Planetside/DungeonPlaceables/InitNewPlaceables.cs:62`). `RoomFactory.OnCustomProperty` (`Func<string, GameObject, JObject, GameObject>`) lets you post-process by attributes. The `Alexandria.xml` doc that ships with 0.5.10 documents only `LoadRoomsFromRoomDirectory`, `BuildFromResource`, `StoredRoomObjects`, `StoredDungeonPlaceables` for this API.

**Registration side-effects** (`DungeonHandler.Register(RoomData)`, `DungeonHandler.cs:89-470`): `BuildFromResource` always registers. With `category == BOSS && subCategoryBoss == FLOOR_BOSS` the room is added to vanilla boss tables **per `floors` prerequisite** (`gull/triggertwins/bulletking` for CASTLEGEON, `blobby` for SEWERGEON, `gorgun/beholster/ammoconda` for GUNGEON, ...), `specialRoomPool` routes into `StaticReferences.RoomTables[...]`. For a past-only room leave `floors` empty (no prerequisites ⇒ no table insertion) or use `Build(...)` and skip `Register`.

### 3(c) Building a custom `DungeonFlow`

Vanilla API (`decomp/DungeonFlow.cs`, `decomp/DungeonFlowNode.cs`; all fields public):

```csharp
DungeonFlow : ScriptableObject { GenericRoomTable fallbackRoomTable; GenericRoomTable phantomRoomTable; List<DungeonFlowSubtypeRestriction> subtypeRestrictions; GenericRoomTable evolvedRoomTable;
    List<ProceduralFlowModifierData> flowInjectionData; List<SharedInjectionData> sharedInjectionData; List<DungeonFlowNode> AllNodes {get;} DungeonFlowNode FirstNode {get;set;}
    void Initialize(); void AddNodeToFlow(DungeonFlowNode newNode, DungeonFlowNode parent); void ConnectNodes(parent, child); void LoopConnectNodes(chainEnd, loopTarget); ... }
DungeonFlowNode(DungeonFlow parentFlow) { nodeType (ControlNodeType.ROOM), roomCategory, percentChance = 1, priority (NodePriority.MANDATORY), overrideExactRoom, overrideRoomTable,
    guidAsString, parentNodeGuid, childNodeGuids, loopTargetNodeGuid, loopTargetIsOneWay, minChainLength = 3, maxChainLength = 8, minChildrenToBuild = 1, maxChildrenToBuild = 1, handlesOwnWarping, isWarpWingEntrance, forcedDoorType, ... }
```

`AddNodeToFlow` requires `Initialize()` to have been called (it lazily calls it), dedupes on `guidAsString`, and links `parent.childNodeGuids`/`newNode.parentNodeGuid`.

Alexandria 0.5.10 helpers (`SampleFlow`, all `public static`, verified in IL):

```csharp
DungeonFlow CreateNewFlow(Dungeon dungeon)     // CreateInstance<DungeonFlow>(); subtypeRestrictions = [new DungeonFlowSubtypeRestriction()]; flowInjectionData/sharedInjectionData = empty;
                                               // fallbackRoomTable = evolvedRoomTable = phantomRoomTable = dungeon.PatternSettings.flows[0].fallbackRoomTable; Initialize();
DungeonFlow CreateEntranceExitFlow(Dungeon dungeon) // "elevator entrance" -> "exit_room_basic"
DungeonFlow CreateDebugFlow(Dungeon dungeon)   // entrance, then every RoomFactory.rooms value alternating with empty hubs
DungeonFlowNode NodeFromAssetName(DungeonFlow flow, string name) // new DungeonFlowNode(flow) { overrideExactRoom = RoomFromAssetName(name) }
PrototypeDungeonRoom RoomFromAssetName(string name) // StaticReferences.GetAsset<PrototypeDungeonRoom>(name) across the 3 bundles
void ListNodes(this DungeonFlow flow)
```

```csharp
public static DungeonFlow CreateMazeFlow(Dungeon dungeon)
{
    var flow = CreateNewFlow(dungeon);
    flow.name = "maze_flow";
    var entrance = NodeFromAssetName(flow, "elevator entrance");
    flow.FirstNode = entrance;
    flow.AddNodeToFlow(entrance, null);
    var maze = new DungeonFlowNode(flow) { overrideExactRoom = RoomFactory.BuildFromResource("resource/rooms/maze.room").room };
    flow.AddNodeToFlow(maze, entrance);
    flow.AddNodeToFlow(NodeFromAssetName(flow, "exit_room_basic"), maze);
    dungeon = null;
    return flow;
}
```

Stock rooms usable as nodes: `"elevator entrance"` and `"exit_room_basic"` (`shared_auto_002`; GungeonCraft `FlowPrefabs.cs:149-153`). Alexandria does **not** ship the `GenerateDefaultNode(...)` helper — it lives in ExpandTheGungeon (`ExpandDungeonFlows.cs:146`), Modular (`Past/Prefabs/CustomFlow.cs:44`), Planetside (`AbyssFloorSetup.cs:993`) and the guide, all identical:

```csharp
public static DungeonFlowNode GenerateDefaultNode(DungeonFlow targetflow, PrototypeDungeonRoom.RoomCategory roomType, PrototypeDungeonRoom overrideRoom = null, GenericRoomTable overrideTable = null, bool oneWayLoopTarget = false, bool isWarpWingNode = false, string nodeGUID = null, DungeonFlowNode.NodePriority priority = DungeonFlowNode.NodePriority.MANDATORY, float percentChance = 1, bool handlesOwnWarping = true)
{
    if (string.IsNullOrEmpty(nodeGUID)) { nodeGUID = Guid.NewGuid().ToString(); }
    DungeonFlowNode m_CachedNode = new DungeonFlowNode(targetflow) {
        isSubchainStandin = false, nodeType = DungeonFlowNode.ControlNodeType.ROOM, roomCategory = roomType, percentChance = percentChance, priority = priority,
        overrideExactRoom = overrideRoom, overrideRoomTable = overrideTable, capSubchain = false, subchainIdentifier = string.Empty, limitedCopiesOfSubchain = false, maxCopiesOfSubchain = 1,
        subchainIdentifiers = new List<string>(0), receivesCaps = false, isWarpWingEntrance = isWarpWingNode, handlesOwnWarping = handlesOwnWarping,
        forcedDoorType = DungeonFlowNode.ForcedDoorType.NONE, loopForcedDoorType = DungeonFlowNode.ForcedDoorType.NONE, nodeExpands = false, initialChainPrototype = "n",
        chainRules = new List<ChainRule>(0), minChainLength = 3, maxChainLength = 8, minChildrenToBuild = 1, maxChildrenToBuild = 1, canBuildDuplicateChildren = false,
        guidAsString = nodeGUID, parentNodeGuid = string.Empty, childNodeGuids = new List<string>(0), loopTargetNodeGuid = string.Empty, loopTargetIsOneWay = oneWayLoopTarget, flow = targetflow };
    return m_CachedNode;
}
```

Modular's past flow is literally three nodes (`Modular/Past/Prefabs/CustomFlow.cs:20-87`): `entranceNode = GenerateDefaultNode(flow, RoomCategory.ENTRANCE, FloorRoomInitialisation.StartRoom); AddNodeToFlow(entranceNode, null); FirstNode = entranceNode;` → `firstroom (NORMAL, FirstRoom)` → `bossRoom (NORMAL, BossRoom)`, with `fallbackRoomTable = MinesDungeonPrefab.PatternSettings.flows[0].fallbackRoomTable`. GungeonCraft Sans: `elevator_entrance (CONNECTOR) → SansBossRoom (CONNECTOR) → exit_room_basic (EXIT)`, `fallbackRoomTable = SewersRoomTable`, `subtypeRestrictions/flowInjectionData/sharedInjectionData = empty`, `Initialize()`, `FirstNode = Node_00`. **The guide warns: the entrance room's `category` must be `ENTRANCE` "set via code, not rat"** (`making-the-flow.md`, last line).

### 3(d) Loading the flow/dungeon at runtime

Three patterns, in order of robustness:

1. **Custom `GameLevelDefinition` + `DungeonDatabase.GetOrLoadByName` hook + `LoadCustomLevel`** — what GungeonCraft, Planetside, Fallen-Items, Modular and the guide do; it is the only one that makes a *named level* that `LoadCustomLevel(cc.past)` (Alexandria's ark hook) can find. GungeonCraft `https://github.com/pcrain/GungeonCraft/blob/master/src/Cwaff-Flows/CwaffDungeons.cs`:

```csharp
public static CwaffDungeons Register(string internalName, string floorName, Func<Dungeon, Dungeon> dungeonGenerator,
    string dungeonPrefabTemplate = null, GameLevelDefinition gameLevelDefinition = null, string floorMusic = null, int loopPoint = -1, int rewindAmount = -1)
{
    if (Flows.ContainsKey(internalName)) return Flows[internalName];
    foreach (GameLevelDefinition levelDefinition in GameManager.Instance.customFloors)
        if (levelDefinition.dungeonSceneName == internalName) gameLevelDefinition = levelDefinition;
    GameManager.Instance.customFloors.Add(gameLevelDefinition);
    ResourceManager.LoadAssetBundle("brave_resources_001").LoadAsset<GameObject>("_GameManager").GetComponent<GameManager>().customFloors.Add(gameLevelDefinition);
    Flows[internalName] = new CwaffDungeons() { internalName = internalName, ..., dungeonPrefabTemplate = dungeonPrefabTemplate, gameLevelDefinition = gameLevelDefinition, dungeonGenerator = dungeonGenerator };
    return Flows[internalName];
}

/// <summary>Fixes a bug where returning to the breach deletes the floor, thanks Bunny!</summary>
[HarmonyPatch(typeof(GameManager), nameof(GameManager.LoadCustomLevel))]
private class ReregisterOurCustomLevelIfNecessaryPatch
{
    static void Prefix(GameManager __instance, string custom)
    {
        if (!Flows.TryGetValue(custom, out CwaffDungeons dungeonData)) return;
        if (dungeonData.gameLevelDefinition == null || GameManager.Instance.customFloors.Contains(dungeonData.gameLevelDefinition)) return;
        GameManager.Instance.customFloors.Add(dungeonData.gameLevelDefinition);
    }
}

[HarmonyPatch(typeof(DungeonDatabase), nameof(DungeonDatabase.GetOrLoadByName))]
private class GetOrLoadCustomDungeonPatch
{
    static bool Prefix(string name, ref Dungeon __result)
    {
        if (!Flows.TryGetValue(name, out CwaffDungeons dungeonData)) return true;
        if (dungeonData.gameLevelDefinition != null && !GameManager.Instance.customFloors.Contains(dungeonData.gameLevelDefinition))
            GameManager.Instance.customFloors.Add(dungeonData.gameLevelDefinition);
        Dungeon dungeon = null;
        if (name.ToLower() == dungeonData.internalName)
        {
            try { dungeon = dungeonData.dungeonGenerator(GetOrLoadByName_Orig(dungeonData.dungeonPrefabTemplate ?? "Base_Gungeon")); }
            catch (Exception e) { Lazy.DebugLog($"  exception: {e}"); }
        }
        if (!dungeon) return true;
        __result = dungeon;
        return false;
    }
}

public static Dungeon GetOrLoadByName_Orig(string name)
{
    AssetBundle assetBundle = ResourceManager.LoadAssetBundle("dungeons/" + name.ToLower());
    return assetBundle.LoadAsset<GameObject>(name).GetComponent<Dungeon>();
}

[HarmonyPatch(typeof(FlowDatabase), nameof(FlowDatabase.GetOrLoadByName))]
private class LoadCustomFlowPatch
{
    static bool Prefix(string name, ref DungeonFlow __result)
    {
        if (_KnownFlows == null || _KnownFlows.Count <= 0) return true;
        string flowName = name.ToLower();
        if (flowName.Contains("/")) flowName = flowName.Substring(flowName.LastIndexOf("/") + 1);
        foreach (DungeonFlow flow in _KnownFlows)
            if (!string.IsNullOrEmpty(flow.name) && flowName == flow.name.ToLower()) { __result = flow; return false; }
        return true;
    }
}
```

The generator (`SansDungeon.SansGeon(Dungeon dungeon)`, `SansDungeon.cs:41-219`) receives the **template prefab instance** (`Base_ResourcefulRat`) and overwrites: `roomMaterialDefinitions` (7× an `Instantiate`d `DungeonMaterial` from another floor), `tileIndices = new TileIndices { tilesetId, dungeonCollection, aoTileIndices, patternIndexGrid, placeBorders, placePits, ... }`, `pathGridDefinitions`, `dungeonDustups`, `PatternSettings = new SemioticDungeonGenSettings { flows = new List<DungeonFlow> { SansDungeonFlow.Init() }, mandatoryExtraRooms = ..., optionalExtraRooms = ..., MAX_GENERATION_ATTEMPTS = 250 }`, `stampData`, `FloorIdea`, `doorObjects`/`oneWayDoorObjects`/`oneWayDoorPressurePlate`/`phantomBlockerDoorObjects`, `baseChestContents`, `SecretRoom*`, `sharedSettingsPrefab`, `BossMasteryTokenItemId`, `defaultPlayerPrefab`, `PlayerIsLight`/`PlayerLightColor`/`Intensity`/`Radius`, `PrefabsToAutoSpawn = new GameObject[0]`, `musicEventName`. `GameLevelDefinition` fields (2.1.9.1): `dungeonSceneName, dungeonPrefabPath, priceMultiplier = 1, secretDoorHealthMultiplier = 1, enemyHealthMultiplier = 1, damageCap = -1, bossDpsCap = -1, List<DungeonFlowLevelEntry> flowEntries, List<int> predefinedSeeds`. The guide's own load command is simply `GameManager.Instance.LoadCustomLevel(FloorNameDungeon.FloorNameDefinition.dungeonSceneName);` and it re-registers the definition in a `GameManager.Awake` hook (`making-the-flow.md`), because a new `GameManager` instance is created when returning to the Breach.

2. **`GameManager.Instance.LoadCustomFlowForDebug(flowName, dungeonPrefab, sceneName)`** with a `FlowDatabase.GetOrLoadByName` hook (ExpandTheGungeon `DungeonFlowModule.LoadFlowFunction`, Alexandria `Misc/Commands.cs:71` `LoadCustomFlowForDebug("NPCParadise", "Base_Castle", "tt_castle")`, OMITB's item `GTCWTVRP.cs` `LoadCustomFlowForDebug(level[2], level[1], level[0])`). Fine for a debug console command; not what the ark calls.

3. **`Alexandria.DungeonAPI.DungeonHooks.OnPreDungeonGeneration`** (`event Action<LoopDungeonGenerator, Dungeon, DungeonFlow, int>`, Harmony postfix on the `LoopDungeonGenerator(Dungeon, int)` ctor) + `generator.AssignFlow(flow)` — swaps the flow at generation time without touching `FlowDatabase`. `DungeonHandler.OnPreDungeonGen` does exactly this when `DungeonHandler.debugFlow` is true (`flow = SampleFlow.CreateDebugFlow(dungeon); generator.AssignFlow(flow);`). Also `DungeonHooks.OnPostDungeonGeneration` (`GameManager.OnNewLevelFullyLoaded`) and `OnFoyerAwake`. `GameManager.InjectedFlowPath` is the vanilla equivalent (used by OMITB for the glitch floor).

Other useful 0.5.10 members: `StaticReferences.GetAsset<T>(string assetName)`, `StaticReferences.RoomTables` (`Dictionary<string, GenericRoomTable>`, keys `castle, gungeon, mines, catacombs, forge, sewer, cathedral, bullethell, resourcefulrat, special, shop, secret, winchester, gull, triggertwins, bulletking, blobby, gorgun, beholster, ammoconda, oldking, tank, cannonballrog, flayer, priest, pillars, monger, doorlord, blockner, shadeagunim, oldred, cursula, flynt, trorc, goopton, ...`), `StaticReferences.GetRoomTable(GlobalDungeonData.ValidTilesets)`, `OfficialFlows.dungeonPrefabNames`/`dungeonSceneNamesInOrder` (internal class), `RoomUtility.EnableDebugLogging`.

### 3(e) Tilesets available for reuse

`GlobalDungeonData.ValidTilesets` (flags, 2.1.9.1): `GUNGEON=1, CASTLEGEON=2, SEWERGEON=4, CATHEDRALGEON=8, MINEGEON=0x10, CATACOMBGEON=0x20, FORGEGEON=0x40, HELLGEON=0x80, SPACEGEON=0x100, PHOBOSGEON=0x200, WESTGEON=0x400, OFFICEGEON=0x800, BELLYGEON=0x1000, JUNGLEGEON=0x2000, FINALGEON=0x4000, RATGEON=0x8000`.

Dungeon prefabs loadable with `DungeonDatabase.GetOrLoadByName` (from `_GameManager.prefab` + `LoadHelper.cs`): `Base_Foyer, Base_Castle, Base_Sewer, Base_Gungeon, Base_Cathedral, Base_Mines, Base_ResourcefulRat, Base_Catacombs, Base_Forge, Base_BulletHell, Base_Nakatomi, Base_Tutorial, Base_Belly, Base_Future, Base_Jungle, Base_Phobos, Base_West` (the last five are unfinished/unused tilesets; `tt_belly`, `tt_future`, `tt_jungle`, `tt_phobos` use `Testing/Single Room Demonstration Flow`), plus `FinalScenario_Pilot, _Convict, _Soldier, _Guide, _Coop, _Robot, _Bullet`.

For an **indoor vet clinic** the candidates, best first:

1. `FinalScenario_Soldier` — Primerdyne R&D lab (`#SCIENCELAB_*`): clinical white/grey lab tiles, sci-fi doors; `tilesetId = FINALGEON`. Modular's custom past takes `oneWayDoorObjects`, `oneWayDoorPressurePlate`, `phantomBlockerDoorObjects` and `musicEventName` from it (`PDashTwo.cs:193,382-384`, `PastFloorSetup.cs:264`) and Planetside loads it for its Abyss floor. Using `tilesetId = FINALGEON` on our dungeon also makes the game treat the level as a past for the win-pic (`Win_Pic_*`/`pastWinPic`) and disables shared injections (`RetrieveSharedInjectionDataListFromCurrentFloor` returns empty for FINALGEON).
2. `FinalScenario_Pilot` — ExpandTheGungeon builds a whole custom "Space" dungeon from `FinalScenarioPilotPrefab.tileIndices.dungeonCollection` + `FinalScenarioBulletPrefab.tileIndices.aoTileIndices/patternIndexGrid` with `tilesetId = SPACEGEON` (`ExpandCustomDungeonPrefabs.cs:198-452`) — proof the past collections can be re-targeted.
3. `Base_Nakatomi` (OFFICEGEON, R&G Dept.): carpets, office walls — plausible "waiting room"; Modular takes `alternateDoorObjectsNakatomi` from it.
4. `Base_ResourcefulRat` (RATGEON) — the standard template that GungeonCraft/Modular/Planetside clone because it is small and has no injections; Gungeon Proper/Hollow/Forge are stone dungeons and look nothing like a clinic.

---

## 4. How an existing open-source mod loads a fully custom level/flow

* **Modular (custom character + custom past)** — `https://github.com/Some-Bunny/Modular/blob/master/Past/PastFloorSetup.cs`:

```csharp
public static void Init()
{
    InitObjects.Init();
    TilesetSetup.InitCustomTileset();
    DungeonMaterialSetup.InitCustomDungeonMaterial();
    DungeonMaterialSetupSecond.InitCustomDungeonMaterial();
    DungeonStampDataSetup.InitCustomDungeonStampData();
    FloorRoomInitialisation.InitCustomRooms(); //Init Rooms Before Flows
    CustomFlow.GenerateFlows(); //Flows
    ...
    InitCustomDungeon();
}
private static void LoadFloor(string[] obj)
{
    if (!GameManager.Instance.customFloors.Contains(PastDefinition)) { GameManager.Instance.customFloors.Add(PastDefinition); }
    GameManager.Instance.LoadCustomLevel(PastDungeon.PastDefinition.dungeonSceneName);
}
public static void InitCustomDungeon()
{
    getOrLoadByName_Hook = new Hook(
        typeof(DungeonDatabase).GetMethod("GetOrLoadByName", BindingFlags.Static | BindingFlags.Public),
        typeof(PastDungeon).GetMethod("GetOrLoadByNameHook", BindingFlags.Static | BindingFlags.Public));
    AssetBundle braveResources = ResourceManager.LoadAssetBundle("brave_resources_001");
    GameManagerObject = braveResources.LoadAsset<GameObject>("_GameManager");
    PastDefinition = new GameLevelDefinition()
    {
        dungeonSceneName = "tt_modular_past", //this is the name we will use whenever we want to load our dungeons scene
        dungeonPrefabPath = "based_modular_past", //this is what we will use when we want to acess our dungeon prefab
        priceMultiplier = 1.5f, secretDoorHealthMultiplier = 1, enemyHealthMultiplier = 1.6f, damageCap = 300, bossDpsCap = 78,
        flowEntries = new List<DungeonFlowLevelEntry>(0), predefinedSeeds = new List<int>(0)
    };
    foreach (GameLevelDefinition levelDefinition in GameManager.Instance.customFloors)
        if (levelDefinition.dungeonSceneName == "tt_modular_past") { PastDefinition = levelDefinition; }
    GameManager.Instance.customFloors.Add(PastDefinition);
    GameManagerObject.GetComponent<GameManager>().customFloors.Add(PastDefinition);
}
public static Dungeon GetOrLoadByNameHook(Func<string, Dungeon> orig, string name)
{
    if (!GameManager.Instance.customFloors.Contains(PastDefinition)) { GameManager.Instance.customFloors.Add(PastDefinition); }
    bool flag = name.ToLower() == "based_modular_past";
    Dungeon result;
    if (flag) { ... result = PastDungeon.AbyssGeon(GetOrLoadByName_Orig("Base_ResourcefulRat")); }
    else { result = orig(name); }
    return result;
}
```

  and in the generator: `dungeon.LevelOverrideType = GameManager.LevelOverrideState.CHARACTER_PAST;` (`PastFloorSetup.cs:164`), `dungeon.PatternSettings = new SemioticDungeonGenSettings() { flows = new List<DungeonFlow>() { CustomFlow.Default_Flow }, ... }` (`:230-235`), `dungeon.musicEventName = MarinePastPrefab.musicEventName;` (`:264`). Its `characterdata.txt`-based character is built with the same Alexandria `Loader` (see caveats on how it wires `customPast`).
* **GungeonCraft** — full excerpt in §3(d); flow in `src/Cwaff-Flows/SansDungeon.cs:221-348`.
* **ExpandTheGungeon (BepInEx)** — `https://github.com/ApacheThunder/ExpandTheGungeon_BepInEX/blob/main/ExpandTheGungeon/DungeonFlowModule.cs` (`load_flow` console command → `GameManager.Instance.LoadCustomFlowForDebug(flowName[, tilesetName[, sceneName]])`, with a fallback `LoadCustomFlowForDebug("npcparadise", "Base_Castle", "tt_castle")`) and `ExpandDungeonFlows/ExpandDungeonFlows.cs:65-92` (`LoadCustomFlow(Func<string, DungeonFlow> orig, string target)` MonoMod hook on `FlowDatabase.GetOrLoadByName` matching `KnownFlows` by name).
* **Guide** — `https://mtgmodders.gitbook.io/etg-modding-guide/making-a-floor/making-the-flow.md` (flow skeleton, init order `ModPrefabs.InitCustomPrefabs(); ModRoomPrefabs.InitCustomRooms(); FloorNameDungeonFlows.InitDungeonFlows(); FloorNameDungeon.InitCustomDungeon();` + `GameManager.Awake` hook + `GameManager.Instance.LoadCustomLevel(FloorNameDungeon.FloorNameDefinition.dungeonSceneName)`), `.../rooms.md` (`RoomFactory.BuildFromResource("Mod/Resources/ModRooms/floorEntrance.room")`, `Mod_Entrance_Room.category = PrototypeDungeonRoom.RoomCategory.ENTRANCE`), `.../making-the-dungeon.md`, `.../making-the-entrance.md` (`KeepEntrancePitController.LevelToLoadOnPitfall = "tt_floorname"`). Raw markdown copies: `scratchpad/guide/*.md`.
* **SpecialAPI/Load-Level** — `https://github.com/SpecialAPI/Load-Level/blob/main/LoadLevelModule.cs`: console `load_level` alias table (`{ "marinepast", "fs_soldier" }, ... { "gunslingerpast", "tt_bullethell" }`) and `if (sceneName == "fs_coop") GameManager.IsCoopPast = true; GameManager.Instance.LoadCustomLevel(sceneName);` — handy for testing vanilla pasts.

---

## 5. Recommended build for Pluto's past (derived from the above)

1. **Room**: draw the clinic in RAT (or `CreateEmptyRoom` + custom cells), export `pluto_clinic.room` as an embedded resource, load with `RoomFactory.BuildFromResource(...)`, then in code force `room.category = PrototypeDungeonRoom.RoomCategory.ENTRANCE` (the flow's first node must be an entrance) and leave `floors`/`category BOSS` out so `Register` does not push it into vanilla tables. Crate/table: prefabs registered in `StaticReferences.customObjects["pluto_crate"]` etc. (sprite + `MajorBreakable`/`SpeculativeRigidbody` as needed) and referenced by that name in RAT, or appended with `AddPlaceableToRoom`. Boss: `AddEnemyToRoom(room, pos, bossGuid, "", 0, false, RoomEventTriggerCondition.ON_ENEMIES_CLEARED)` or a `PrototypePlacedObjectData { enemyBehaviourGuid }` as GungeonCraft does; give the boss a `GenericIntroDoer` (`triggerType = BossTriggerZone` if you want to trigger it from the controller after an intro, `PlayerEnteredRoom` otherwise).
2. **Flow**: `CreateInstance<DungeonFlow>()`, one `GenerateDefaultNode(flow, ENTRANCE, clinicRoom)` (optionally a second BOSS node), `fallbackRoomTable` borrowed from the template prefab, empty injection lists, `Initialize()`, `AddNodeToFlow`, `FirstNode`.
3. **Dungeon**: hook `DungeonDatabase.GetOrLoadByName` (Harmony prefix, as GungeonCraft) for `"base_pluto_past"` → clone `Base_ResourcefulRat` (or `FinalScenario_Soldier` directly), set `PatternSettings.flows = [flow]`, `LevelOverrideType = CHARACTER_PAST`, `tileIndices.tilesetId = FINALGEON` (or keep the template's), materials/doors/music from `FinalScenario_Soldier`, `PrefabsToAutoSpawn = new GameObject[0]`, `StripPlayerOnArrival = false`.
4. **Level**: `GameLevelDefinition { dungeonSceneName = "tt_pluto_past", dungeonPrefabPath = "base_pluto_past", flowEntries = [] }` added to `GameManager.Instance.customFloors` **and** the `_GameManager` prefab's `customFloors`, re-added in a `GameManager.LoadCustomLevel` prefix (GungeonCraft) or `GameManager.Awake` hook (guide).
5. **Trigger**: `Loader.BuildCharacter(..., hasCustomPast: true, customPast: "tt_pluto_past")` — Alexandria's ark hook then calls `ark.ResetPlayers(false); GameManager.Instance.LoadCustomLevel("tt_pluto_past")`. Debug: console command calling `LoadCustomLevel("tt_pluto_past")`.
6. **Ending**: a room-placed controller mirrors `PastLabMarineController`: on `healthHaver.OnPreDeath` → `SetCharacterSpecificFlag(ETGModCompatibility.ExtendEnum<PlayableCharacters>(GUID, nameShort), KILLED_PAST, true)`, `RegisterStatChange(TIMES_KILLED_PAST, 1f)`, `PastCameraUtility.LockConversation`, optional `TalkDoerLite`, freeze frame, `new TimeTubeCreditsController().HandleTimeTubeCredits(player.sprite.WorldCenter, false, null, -1)`, `AmmonomiconController.Instance.OpenAmmonomicon(true, true)`; supply `pastWinPic` in the character data.

---

## 6. Not verified / caveats

* **Stub DLL**: nothing in `EtG.GameLibs.2.1.9.1` has bodies; all behaviour quotes are from the fedes1to AssetRipper export of an unknown-but-recent game version (it contains `Gunslinger`, `IsGunslingerPast`, A Farewell to Arms content). Signatures were cross-checked against 2.1.9.1, bodies were not diffed line-by-line against the live game.
* **Alexandria version skew**: the GitHub `main` DungeonAPI (commits through 2026-01-28) matches the 0.5.10 DLL for every method listed in §3, and `CustomPastHandlerPatches`/`DoCustomPastChecks` are present in the shipped DLL (IL verified). What was *not* verified is that its IL match (`ldloc 8` + `brtrue` inside the `HandleClockhair` enumerator) still finds its target against the game build you run; if the manipulator silently `return`s, a custom character's shot falls through to `OpenAmmonomicon(true, true)` (plain victory) — test in game first.
* **Past flow/room assets**: the `FinalScenario_*` prefabs reference their `DungeonFlow`/`PrototypeDungeonRoom`s by GUID; those YAML files were not found (the GitHub tree API truncated at 52,429 entries), so the exact vanilla node/room list per past is inferred, not read. Likewise the guid-shared `dungeonCollection 0729565a...` being one atlas for several pasts is an inference from two prefabs.
* **Which "look" the FINALGEON collection gives a *new* room** depends on `roomMaterialDefinitions[...]`/`overrideRoomVisualType`; the vet-clinic suitability of `FinalScenario_Soldier`'s tiles is a visual judgment that must be checked in-game (Modular and Planetside eventually replaced the material with their own).
* `Loader.BuildCharacter`'s `customPast` value is assumed to be a `dungeonSceneName` because `DoCustomPastChecks` passes it straight to `LoadCustomLevel`; Modular's `characterdata.txt` has no past key (its `BuildCharacter` call could not be retrieved — GitHub API quota was exhausted), so how Modular wires `cc.past` was not confirmed.
* `GameManager.DoMidgameSave(FINALGEON)` is written by the ark before `LoadCustomLevel`; resuming that save goes through `DelayedLoadMidgameSave`, whose `switch` has no case for a custom character (falls into the empty `Ninja/Cosmonaut/CoopCultist/Eevee` group ⇒ nothing loads). A custom past should either invalidate the mid-game save or patch `DelayedLoadMidgameSave`.
* `RoomFactory.Register` side-effects for `category == ENTRANCE`/`NORMAL` with empty `floors` were read but not executed; confirm no console "Unable to find asset" spam for custom object names.
* Web pages were fetched through a summarising fetcher for the Thunderstore/RAT page and wiki pages; the guide pages were fetched raw (`scratchpad/guide/`).
