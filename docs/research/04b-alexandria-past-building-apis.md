# 04b — Building out the past: multi-room flows, enemy waves, custom enemies, talking NPCs, cutscenes

Companion to `04-past-level-and-dungeonapi.md` (level plumbing, one-room flow) and `05-custom-boss-research.md`
(BossBuilder). Written 2026-09-14 against Alexandria 0.5.10 / MtG API 1.9.2 / BepInEx 5.4.21.

Tags: **[SRC]** Alexandria source (GitHub `main` @ d88fe7a, 2026-08-16) *and* the member name exists in the shipped 0.5.10 DLL
(`strings` check). **[VAN]** vanilla method bodies from the AssetRipper export `github.com/fedes1to/EtG-source` (copies in
`scratchpad/vanilla/`). **[MOD]** a reference mod does it (Modular, Enter the Beyond = ETB, OMITB, Planetside, ExpandTheGungeon = ETG;
`scratchpad/repos/`). **[INF]** inferred, not verified — test on the Steam machine.

---

## 1. Multi-room flows (DungeonAPI + Dungeonator)

### 1.1 The flow graph [VAN `DungeonFlow.cs`, `DungeonFlowNode.cs`]

```csharp
new DungeonFlowNode(DungeonFlow parentFlow)   // flow, childNodeGuids = new List<string>(), guidAsString = Guid.NewGuid()
void DungeonFlow.Initialize()                  // m_nodes/m_nodeGuids lists (AddNodeToFlow calls it lazily)
void DungeonFlow.AddNodeToFlow(DungeonFlowNode newNode, DungeonFlowNode parent)
    // no-op if guid already present; parent != null -> parent.childNodeGuids.Add(guid), newNode.parentNodeGuid = parent.guid; parent == null -> ""
void ConnectNodes(parent, child); void LoopConnectNodes(chainEnd, loopTarget);  DungeonFlowNode FirstNode { get; set; } // stores the guid
```
Node fields that matter: `roomCategory`, `overrideExactRoom`, `priority = MANDATORY`, `percentChance = 1`, `nodeType = ROOM`,
`forcedDoorType` (`LOCKED` -> `RuntimeRoomExitData.isLockedDoor` -> `Dungeon.lockedDoorObjects`; `ONE_WAY` -> one-way door +
pressure plate [VAN `LoopFlowBuilder.cs:1649-1657`]). `UsesGlobalBossData` is false whenever `overrideExactRoom` is set, so a
BOSS node with an exact room never pulls vanilla boss data. The `GenerateDefaultNode(...)` helper already in
`PlutoVetVisit/src/VetFlow.cs` is the one Modular/ETB/ETG/Planetside ship (Alexandria does not) [MOD]. A chain is just:

```csharp
DungeonFlow flow = SampleFlow.CreateNewFlow(template);   // [SRC] template's fallback/phantom/evolved tables, empty injections, Initialize()
var entrance = GenerateDefaultNode(flow, RoomCategory.ENTRANCE, WaitingRoom);    flow.AddNodeToFlow(entrance, null); flow.FirstNode = entrance;
var hall     = GenerateDefaultNode(flow, RoomCategory.NORMAL,   Corridor);       flow.AddNodeToFlow(hall, entrance);
var clinic   = GenerateDefaultNode(flow, RoomCategory.BOSS,     ClinicRoom.Room); flow.AddNodeToFlow(clinic, hall);
```
Modular's past is this shape (ENTRANCE -> NORMAL x N -> HUB -> ... -> BOSS, `fallbackRoomTable` from `Base_Mines`, `phantomRoomTable =
null`, empty injection lists) [MOD `Past/OtherFloor/Assets/CustomFlow.cs`]; ETB's Lost past is ENTRANCE -> BOSS [MOD]. No EXIT room
is needed (neither vanilla pasts nor the mod pasts have one; `DungeonData.Exit` is null-guarded [VAN `DungeonData.cs:318`]).

### 1.2 Exits in `.newroom`, hallways, doors

- `exitPositions[i]` (`{"x","y"}` cells) + `exitDirections[i]` -> `RoomFactory.AddExit(room, pos, dir, exitType)` [SRC]. The
  string is scanned for `west/east/north/south` (case-insensitive) and `exitonly`/`entryonly` (`EXIT_ONLY`/`ENTRANCE_ONLY`).
  **Gotcha:** for `ENTRANCE_ONLY` the direction is *inverted* (`DetermineDirectionType`, `RoomFactory.cs:258-291`).
- `AddExit` builds `PrototypeRoomExit(dir, pos) { exitType, containsDoor = true, containedCells = [pos, pos + (1,0) for N/S | (0,1) for E/W] }`
  (2 cells wide). Placement convention from `CreateEmptyRoom` [SRC]: SOUTH `(x, 0)`, NORTH `(x, Height)`, WEST `(0, y)`, EAST
  `(Width, y)` — N/E one cell outside the grid, S/W on the edge row/column. Null `exitPositions` = four mid-side exits.
  Call `room.UpdatePrecalculatedData()` after adding exits in code [INF].
- Pairing [VAN `LoopFlowBuilder.cs:975-985`]: a child room qualifies only if it has an exit facing the *opposite* side of one of
  the parent's non-EXIT_ONLY exits; each exit pair is tried with `SemioticLayoutManager.PathfindHallway(start, end)`, the shortest
  wins and `LoopBuilderComposite.PlaceProceduralPathRoom` carves the corridor [VAN `:1425-1466`]. Rooms never touch; give
  every room an exit on the side facing its neighbour (the clinic's unused SOUTH exit is harmless).
- Door choice per exit [VAN `RuntimeExitDefinition.cs:1290-1400`]: one-way -> `Dungeon.oneWayDoorObjects` + `oneWayDoorPressurePlate`;
  `isLockedDoor` -> `Dungeon.lockedDoorObjects`; `PrototypeRoomExit.specifiedDoor` (downstream, then upstream); else
  `Dungeon.doorObjects` (`alternateDoorObjectsNakatomi` for visual subtype 7/8). `containsDoor = false` -> no door. Needs
  `Dungeon.PlaceDoors` (Soldier prefab: `PlaceDoors: 1`, doc 04 §2.1). Whether `FinalScenario_Soldier.doorObjects` is set is
  **[INF]**: if no doors appear, copy `doorObjects`, `oneWayDoorObjects`, `oneWayDoorPressurePlate`, `phantomBlockerDoorObjects`,
  `lockedDoorObjects` from `DungeonDatabase.GetOrLoadByName("Base_Castle")` in `PastLevel.BuildDungeon` (Modular assigns these) [MOD].

### 1.3 Room categories, the boss room, the boss door

- JSON `category`/`normalSubCategory`/`bossSubCategory`/`specialSubCategory` -> `room.category` etc. [SRC]. `DungeonHandler.Register`
  (called by every `Build*FromResource`) only pushes BOSS+FLOOR_BOSS rooms into vanilla boss tables *per `floors` tileset
  prerequisite* — with `floors: []` nothing is registered anywhere [SRC `DungeonHandler.cs:89-470`].
- BOSS effects: the boss pedestal (`HandleRoomClearReward`) is only for BOSS+FLOOR_BOSS **and returns early in
  `LevelOverrideState.CHARACTER_PAST`** [VAN `RoomHandler.cs:1679-1690`]; the parent of a BOSS child becomes the "boss foyer" but
  keeps its `overrideExactRoom` [VAN `LoopFlowBuilder.cs:936-960`]; minimap icon: set `room.associatedMinimapIcon =
  RoomIcons.BossRoomIcon` yourself. BOSS is optional — Modular's boss room is NORMAL [MOD].
- Boss door [VAN `DungeonDoorController.cs`]: `Mode { COMPLEX, BOSS_DOOR_ONLY_UNSEALS, SINGLE_DOOR, ONE_WAY_DOOR_ONLY_UNSEALS,
  FINAL_BOSS_DOOR }`; `Open()` refuses for `BOSS_DOOR_ONLY_UNSEALS`/`FINAL_BOSS_DOOR` (line 636) — they only unseal. It reaches a
  room via `PrototypeRoomExit.specifiedDoor` on the vanilla boss-room prototypes [INF; room assets not dumped]. `RoomFactory` never
  sets `specifiedDoor`, so a custom room gets a normal door unless you assign one (a `DungeonPlaceable` whose
  `variantTiers[0].nonDatabasePlaceable` has a `DungeonDoorController` with that `Mode`, harvestable from a vanilla boss room) [INF].
- Per-room extras after `Build` [MOD Modular]: `UseCustomMusic/CustomMusicEvent/UseCustomMusicSwitch/CustomMusicSwitch`,
  `usesCustomAmbientLight/customAmbientLight`, `overrideRoomVisualType` (already used by `ClinicRoom`).

### 1.4 Sealing during combat [VAN `RoomHandler.cs`, `DungeonDoorController.cs`]

`room.roomEvents : List<RoomEventDefinition(condition, action)>`, actions `SEAL_ROOM, UNSEAL_ROOM, BECOME_TERRIFYING_AND_DARK,
END_TERRIFYING_AND_DARK`. `RoomFactory.AddEnemyToRoom` adds `(ON_ENTER_WITH_ENEMIES, SEAL_ROOM)` + `(ON_ENEMIES_CLEARED,
UNSEAL_ROOM)` **only when the JSON has enemies** [SRC]; for code-spawned fights add them yourself (ETG's RoomBuilder does [MOD]) or
seal manually. `OnEntered` fires `ON_ENTER`, then `ON_ENTER_WITH_ENEMIES` only if a living `RoomClear` enemy exists, starts TIMER
layers, then `Entered(p)` (lines 604-626). API: `SealRoom()` (every `connectedDoors[i].DoSeal(this)`, `standaloneBlockers`,
connected secret rooms, `OnSealChanged(true)`), `UnsealRoom()`, `IsSealed`, `npcSealState` (`SealNone/SealNext/SealPrior/SealAll`);
doors: `DoSeal(room)`, `DoUnseal(room)`, `SetSealedSilently(bool)`, `Open()`, `Close()` (the Marine past locks its cell door with
`SetSealedSilently(true)` then `Open()`). Vanilla's NPC-started fight is the PlayMaker `SpawnEnemies` action:
`ParentRoom.TriggerReinforcementLayersOnEvent(trigger, instant); ParentRoom.SealRoom();` — copy those two calls after a dialogue.

---

## 2. Enemy waves in a custom room

### 2.1 `.newroom` fields [SRC `RoomFactory.cs:295-345, 2081-2200, 2409-2461`]

| Field | Type | Meaning |
|---|---|---|
| `enemyPositions[i]` | `{"x","y"}` cells | `PrototypePlacedObjectData.contentsBasePosition`; 1x1 `DungeonPlaceable` with `variantTiers[0].enemyPlaceableGuid = enemyGUIDs[i]` |
| `enemyGUIDs[i]` | string | vanilla GUID or your `EnemyBuilder` GUID (`EnemyDatabase.GetOrLoadByGuid` is prefixed with Alexandria's `Dictionary`) |
| `enemyAttributes[i]` | JSON or `""` | only `{"j": true}` is read -> `forceBlackPhantom` |
| `enemyReinforcementLayers[i]` | int | `0` = initial spawn (`room.placedObjects`); `n > 0` = `room.additionalObjectLayers[n-1]` |
| `waveTriggers[i]` | string | `ON_ENEMIES_CLEARED` (default), `ON_ENTER`, `ON_ENTER_WITH_ENEMIES`, `ON_HALF_ENEMY_HP_DEPLETED`, `ON_ONE_QUARTER_…`, `ON_THREE_QUARTERS_…`, `ON_NINETY_PERCENT_ENEMY_HP_DEPLETED`, `TIMER`, `NPC_TRIGGER_A/B/C`, `SHRINE_WAVE_A/B/C`, `ENEMY_BEHAVIOR`, `SEQUENTIAL_WAVE_TRIGGER` (`ReturnTrigger`) |
| `randomizeEnemyPositions` | bool | layer `shuffle` |

Gotchas: (1) `enemyReinforcementLayers[i]` and `waveTriggers[i]` are indexed without length checks (`JsonUtility` turns `[]` into an
empty array), so **all five enemy arrays need one entry per enemy** or `Build` throws, is caught, and you get the silent 12x12 fallback
room (`ClinicRoom.Load` catches that by size). (2) A layer's trigger is fixed when the layer is *created*, i.e. by the first enemy
listed for it. (3) Layer object [VAN]: `PrototypeRoomObjectLayer { placedObjects, placedObjectBasePositions, layerIsReinforcementLayer,
shuffle, randomize = 2, suppressPlayerChecks, delayTime = 15f (TIMER), reinforcementTriggerCondition, probability = 1f,
numberTimesEncounteredRequired }`; Modular retunes after loading: `foreach (var l in room.additionalObjectLayers)
l.reinforcementTriggerCondition = ON_HALF_ENEMY_HP_DEPLETED;` [MOD]. For `clinic_room.py`: `WAVES = [(x, y, guid, layer, trigger)]`.

### 2.2 Runtime API [VAN `RoomHandler.cs`, `AIActor.cs`, `DungeonPlaceableUtility.cs`]

```csharp
// RoomHandler — layers copied at room init from area.runtimePrototypeData.additionalObjectLayers (probability/encounter filters; empty layers skipped)
public List<PrototypeRoomObjectLayer> remainingReinforcementLayers;
public bool TriggerReinforcementLayer(int index, bool removeLayer = true, bool disableDrops = false, int specifyObjectIndex = -1, int specifyObjectCount = -1, bool instant = false);
public void TriggerNextReinforcementLayer();  public bool TriggerReinforcementLayersOnEvent(RoomEventTriggerCondition c, bool instant = false); public void ClearReinforcementLayers();
public void AddSpecificEnemyToRoomProcedurally(string enemyGuid, bool reinforcementSpawn = false, Vector2? goalPosition = null); // free cell, Spawn anim, autoEngage false, optional drop-in
public Action OnEnemiesCleared;   // pre-populated with HandleRoomClearReward in the ctor: always +=      (no RegisterRoomEnemyClearedCallback exists)
public Action<AIActor> OnEnemyRegistered; public Func<bool> PreEnemiesCleared; // return true = "more coming" -> suppresses the clear
public event OnEnteredEventHandler Entered /*(PlayerController)*/; public event OnExitedEventHandler Exited; public Action<bool> OnSealChanged;
public bool HasActiveEnemies(ActiveEnemyType t); public List<AIActor> GetActiveEnemies(ActiveEnemyType t); public bool EverHadEnemies;
public IntVector2? GetRandomAvailableCell(IntVector2? footprint = null, CellTypes? passable = null, bool canPassOccupied = false, CellValidator v = null);
// AIActor
public static AIActor Spawn(AIActor prefabActor, IntVector2 position, RoomHandler source, bool correctForWalls = false, AwakenAnimationType awakenAnimType = Default, bool autoEngage = true);
public static AIActor Spawn(AIActor prefabActor, Vector2 position, RoomHandler source, /* same */);   // floors to a cell; WORLD cells (basePosition subtracted inside)
public enum AwakenAnimationType { Default, Awaken, Spawn }
public bool HasBeenEngaged { get; set; }            // setter -> OnEngaged(): spawn/awaken clip, boss-bar registration (the Vet Visit's Wake() uses it)
public void HandleReinforcementFallIntoRoom(float delay = 0f);   // IsInReinforcementLayer, hides, drops in (reinforceType / CustomReinforceDoer)
public bool PathfindToPosition(Vector2 targetPosition, Vector2? overridePathEnd = null, bool smooth = true, CellValidator cellValidator = null, ...);
```
- Clear order in `DeregisterEnemy` (line 4261): last `RoomClear` enemy gone -> `TriggerReinforcementLayersOnEvent(ON_ENEMIES_CLEARED)`
  -> sequential/timed waves -> `PreEnemiesCleared()` -> if nothing spawned: `ProcessRoomEvents(ON_ENEMIES_CLEARED)` (unseal),
  `OnEnemiesCleared()`, `GameManager.BroadcastRoomTalkDoerFsmEvent("roomCleared")`. `IgnoreForRoomClear` enemies never count.
- `Spawn` -> `DungeonPlaceableUtility.InstantiateDungeonPlaceable(prefab, room, cell, deferConfiguration: false, awakenAnimType,
  autoEngage)`: instantiates, calls `IPlaceConfigurable.ConfigureOnPlacement(room)`, then `ObjectVisibilityManager.Initialize(room,
  autoEngage)` which sets `HasBeenEngaged = true` immediately for non-bosses in a visible room [VAN `ObjectVisibilityManager.cs:127`].
  `AIActor.Start` registers itself (`parentRoom.RegisterEnemy(this)`), so spawned enemies count for room clear. Spawning after the
  player is inside does **not** seal — call `room.SealRoom()`.
- Scripted waves (Modular's placed `CombatTriggerBehavior` does `room.Entered += ...; room.SealRoom(); room.TriggerNextReinforcementLayer();` [MOD]):

```csharp
IEnumerator RunWaves(RoomHandler room, List<List<(string guid, Vector2 cell)>> waves) {
    room.SealRoom();
    foreach (var wave in waves) {
        foreach (var (guid, cell) in wave) {
            AIActor a = AIActor.Spawn(EnemyDatabase.GetOrLoadByGuid(guid), room.area.basePosition + cell.ToIntVector2(), room, true, AIActor.AwakenAnimationType.Spawn, false);
            a.HandleReinforcementFallIntoRoom(0.2f);          // drop-in poof; or a.HasBeenEngaged = true for an instant start
        }
        while (room.HasActiveEnemies(RoomHandler.ActiveEnemyType.RoomClear)) yield return null;
        yield return new WaitForSeconds(0.75f);
    }
    room.UnsealRoom();
}
```
  Alexandria extra: `RoomUtility.GetXEnemiesInRoom(room, n, reqForRoomClear = true, canReturnBosses = true)` [SRC].

---

## 3. Custom regular enemies

### 3.1 `EnemyBuilder.BuildPrefab` [SRC `EnemyAPI/EnemyBuilder.cs`]

`GameObject BuildPrefab(string name, string guid, string defaultSpritePath, IntVector2 hitboxOffset, IntVector2 hitBoxSize, bool HasAiShooter)`
clones a stripped **Rubber Kin** (`6b7ef9e5…`; only `BehaviorSpeculator`, `SpeculativeRigidbody`, `GunAttachPoint` survive) and adds
`tk2dSprite` (PNG from `Assembly.GetCallingAssembly()`), rigidbody with **one `EnemyCollider`** (px from the sprite's lower-left),
`tk2dSpriteAnimator`, `AIAnimator`, `KnockbackDoer(weight 1)`, `HealthHaver` (**15000 HP**), `AIActor { EnemyGuid }`, empty behaviour
lists, `AIBulletBank`, `EnemyDatabaseEntry { placeableWidth/Height 2, isNormalEnemy true }`, `EnemyBuilder.Dictionary[guid]` (served by
a Harmony prefix on `EnemyDatabase.GetOrLoadByGuid`), fake prefab + `SetActive(false)`. Returns null (and logs) for a reused GUID.
**`HasAiShooter = true` adds no `AIShooter`** — it only swaps the static template to a stripped Bullet Kin for later builds; pass
`false` and add the shooter yourself (3.4). Mandatory fixes: `hh.SetHealthMaximum(x); hh.ForceSetCurrentHealth(x)`, an `EnemyHitBox`
`PixelCollider` (player bullets only hit `EnemyHitBox`), `aiActor.MovementSpeed`, `CollisionDamage`, `knockbackDoer.weight` (kin ≈
50-100), `PreventFallingInPitsEver`, `procedurallyOutlined = true`, `ActorName`, `EnemySwitchState = "Metal_Bullet_Man"` (hit sounds [MOD]).

### 3.2 Clips, hit, death, shadow [SRC + VAN]

- Clips: `EnemyBuilder.BuildAnimation(aiAnimator, clipName, "Root/enemy/idle", fps, asm)` (one folder = one clip, zero-padded
  names) as `VetBoss.Clip` does; `aiAnimator.IdleAnimation`/`MoveAnimation` are mandatory `DirectionalAnimation`s (`TwoWayHorizontal`,
  `AnimNames = {right, right}`, `Flipped = {None, Flip}` mirrors right-facing art), `HitAnimation` optional (`HitReactChance`, `HitType`),
  extras via `EnemyBuildingTools.AddNewDirectionAnimation(anim, prefix, names, flips, type)`. An empty `AnimNames[i]` is filled from
  `Prefix` (`GetDefaultName`) [VAN `DirectionalAnimation.cs:375`] — why NPC code passes `Prefix = clip, AnimNames = {""}`.
- Death [VAN `HealthHaver.cs:663-775`]: `overrideDeathAnimation` (raw clip) wins; else the directional animation named **`"death"`**;
  else clips `die_right`/`die_left`, `death`, `die`. So `AddNewDirectionAnimation(anim, "death", {"kin_die","kin_die"}, {None, Flip},
  TwoWayHorizontal)`. Corpse: `aiActor.CorpseObject = EnemyDatabase.GetOrLoadByGuid(BULLET_KIN).CorpseObject` [MOD ETB] or
  `BreakableAPIToolbox.GenerateDebrisObject(shardSpritePath, ...)` [SRC] + `CorpseShadow = true` [MOD OMITB].
- Shadow: `EnemyBuildingTools.AddShadowToAIActor(actor, EnemyDatabase.GetOrLoadByGuid(BULLET_KIN).ShadowObject, attachPoint, name)` [SRC,
  MOD ETB]. Footsteps: `clip.frames[i].triggerEvent = true; eventInfo = "footstep"; eventAudio = "Play_FS_ENM"` on move clips [MOD OMITB].

### 3.3 Bullet-Kin brain [VAN `ShootGunBehavior.cs`; MOD ETB `BeyondKin.cs`, OMITB `BouncerBulletKin.cs`]

```csharp
BehaviorSpeculator kin = EnemyDatabase.GetOrLoadByGuid("01972dee89fc4404a5c408d50007dad5").behaviorSpeculator;   // Bullet Kin
bs.OverrideBehaviors = kin.OverrideBehaviors; bs.OtherBehaviors = kin.OtherBehaviors;                             // ETB copies these lists
bs.TargetBehaviors   = new List<TargetBehaviorBase> { new TargetPlayerBehavior { Radius = 35f, LineOfSight = true, ObjectPermanence = true, SearchInterval = 0.25f, PauseOnTargetSwitch = false, PauseTime = 0.25f } };
bs.MovementBehaviors = new List<MovementBehaviorBase> { new SeekTargetBehavior { StopWhenInRange = true, CustomRange = 7f, LineOfSight = false, ReturnToSpawn = false, PathInterval = 0.5f, SpecifyRange = false } };
bs.AttackBehaviors   = new List<AttackBehaviorBase> { new ShootGunBehavior {
    WeaponType = WeaponType.AIShooterProjectile, OverrideBulletName = "default", LineOfSight = false, RequiresLineOfSight = true,
    RespectReload = true, MagazineCapacity = 6, ReloadSpeed = 0.78f, EmptiesClip = true, TimeBetweenShots = 0.3f, Cooldown = 0.07f, InitialCooldown = 1f,
    Range = 16, MinRange = 0, StopDuringAttack = true, FixTargetDuringAttack = true, LeadAmount = 0, LeadChance = 1, PreventTargetSwitching = true,
    MinHealthThreshold = 0, MaxHealthThreshold = 1, HealthThresholds = new float[0], AccumulateHealthThresholds = true, MaxUsages = 0 } };
bs.InstantFirstTick = kin.InstantFirstTick; bs.TickInterval = kin.TickInterval; bs.PostAwakenDelay = kin.PostAwakenDelay; bs.RemoveDelayOnReinforce = kin.RemoveDelayOnReinforce;
```
`WeaponType { AIShooterProjectile = 0, BulletScript = 2 }` [VAN]; for `BulletScript` set `BulletScript = new CustomBulletScriptSelector(typeof(MyScript))`
(a `Brave.BulletScript.Script` firing bank entries by name). `EnemyTools.DebugInformation(bs)` dumps any vanilla speculator [SRC].

### 3.4 A vanilla gun [SRC `EnemyBuilder.DuplicateAIShooterAndAIBulletBank`, VAN `AIShooter.cs`]

```csharp
AIActor kin = EnemyDatabase.GetOrLoadByGuid("01972dee89fc4404a5c408d50007dad5");
Transform gunPoint = prefab.transform.Find("GunAttachPoint"); gunPoint.localPosition = new Vector2(0f, 0.6f);      // hand height
EnemyBuilder.DuplicateAIShooterAndAIBulletBank(prefab, kin.aiShooter, kin.GetComponent<AIBulletBank>(), startingGunOverrideID: 38 /* any Gun id */,
    gunAttachPointOverride: gunPoint, bulletScriptAttachPointOverride: null, overrideHandObject: null);
EnemyBuildingTools.DestroyUnnecessaryHandObjects(prefab.transform);                                                  // removes "BulletSkeletonHand(Clone)"
```
Copies every bank entry (so `"default"` exists) and the shooter fields (`equippedGunId`, `gunAttachPoint`, `handObject`,
`shouldUseGunReload = true`). Firing [VAN `AIShooter.Shoot`]: with a gun equipped it calls `gun.Attack(entry.OverrideProjectile ?
entry.ProjectileData : null, entry.BulletObject)` — **the projectile is the bank entry's `BulletObject`** (`bulletName`/`OverrideBulletName`,
default `"default"`); the gun only supplies sprite, aim and muzzle. Change bullets by replacing the entry
(`EnemyBuildingTools.CopyBulletBankEntry(kinEntry, "default", "DNC")` + your sprite, as `VetBoss.Entry` does). Hand: the copied
`kin.aiShooter.handObject` is fine; a custom hand is OMITB's 40-line `EntityTools.AddAIShooter(...)` (`PlayerHandController {
handHeightFromGun = 0.05f, IsPlayerPrimary = false }` on a sprite) [MOD] — Alexandria ships **no** `AddAIShooter` (DLL check).

### 3.5 Registration and Ammonomicon [SRC + MOD OMITB/Planetside]

`BuildPrefab` already adds the `EnemyDatabaseEntry`; add `Gungeon.Game.Enemies.Add("pluto:cone_kin", actor)` for `spawn`. Journal page:
`EncounterTrackable t = prefab.AddComponent<EncounterTrackable>(); t.EncounterGuid = t.TrueEncounterGuid = guid; t.prerequisites = new
DungeonPrerequisite[0]; t.journalData = new JournalEntry { PrimaryDisplayName = "#KEY", NotificationPanelDescription = "#KEY_SHORT",
AmmonomiconFullEntry = "#KEY_LONG", AmmonomiconSprite = "<def name>", enemyPortraitSprite = Texture2D, IsEnemy = true }`, icon via
`SpriteBuilder.AddToAmmonomicon(tk2dSpriteDefinition, prefix = "")` [SRC], `EncounterDatabase.Instance.Entries.Add(new EncounterDatabaseEntry
{ myGuid = guid, path = guid, journalData = t.journalData, prerequisites = [] })`, then `EnemyDatabase.GetEntry(guid).encounterGuid = guid;
.isInBossTab = false; .ForcedPositionInAmmonomicon = n`; strings via `ETGMod.Databases.Strings.Enemies.Set`.

### 3.6 Reskinning a vanilla enemy [MOD ETG `ExpandWesternBrosPrefabBuilder.cs`]

`Instantiate(vanillaPrefab)` (deactivate the source first, as `BossBuilder.Init` does), `actor.EnemyGuid = newGuid`,
`sprite.SetSprite(newCollection, "x_idle_front_001")`, `spriteAnimator.Library = newLibrary`, destroy and re-add the `AIShooter` (its
cached inventory points at the old gun), new `EnemyDatabaseEntry` + `EnemyBuilder.Dictionary.Add(guid, clone)`, `FakePrefab.MarkAsFakePrefab`,
`DontDestroyOnLoad`, `SetActive(false)`. The new clips must keep the names the vanilla `DirectionalAnimation`s reference (read
`actor.aiAnimator.IdleAnimation.AnimNames` etc. at runtime first) [INF]. Tint-only: a copied material with `_EmissiveColor/_EmissivePower`
(Planetside's Fodder) [MOD]; a real palette change needs a replacement atlas texture [INF].

---

## 4. Talking NPCs

Alexandria's `NPCAPI` is shops plus these generic helpers, all present in the DLL [SRC]: `ShopAPI.SetUpNPC(name, prefix, idleSpritePaths,
idleFps, talkSpritePaths, talkFps, Vector3 talkPointOffset, Vector3 npcPosition, VoiceBoxes voiceBox = OLD_MAN, float fortunesFavorRadius = 2,
IntVector2? hitboxSize = null, IntVector2? hitboxOffset = null)` (sprite + animator + rigidbody + `TalkDoerLite` + `UltraFortunesFavor` +
blank `AIAnimator`, **no FSM**), `ShopAPI.GenerateBlankAIAnimator(go)`, `NpcAPI.CreateBlankPlayMakerFSM(go, name)`, `PlayMakerExtensions.AddState(
fsm, name, isStartState, isSequence)`, `AddTransition(state, eventName, toState, eventIsGlobal)`, `AddGlobalTransition(fsm.Fsm, ...)`,
`AddAction(state, FsmStateAction)`, `AddFsmString/Int/Bool/Float/Vector2/Vector3`, `AddEvent`, `GetState`. No "SimpleTalkDoer" exists.

### 4.1 What modders use: `IPlayerInteractable` + `TextBoxManager` (recommended)

`interface IPlayerInteractable { float GetDistanceToPoint(Vector2); void OnEnteredRange(PlayerController); void OnExitRange(PlayerController);
void Interact(PlayerController); string GetAnimationState(PlayerController, out bool shouldBeFlipped); float GetOverrideMaxDistance(); }` [VAN].
OMITB `GenericCultist`, ETG `ExpandNPCController`, Modular `QuickInterractableController` are all this [MOD]:
- Prefab: sprite + `tk2dSpriteAnimator` (idle clip, `playAutomatically`) + `SpeculativeRigidbody` (`SetUpSpeculativeRigidbody(offset, size)`,
  `CollideWithTileMap = false`) + child `talkpoint` ≈ 1.2 units above the head + the component; register in
  `StaticReferences.customObjects["pluto_nurse"]` (fake prefab) and place via `placeableGUIDs` (as the controller object is), or spawn with
  `DungeonPlaceableUtility.InstantiateDungeonPlaceable(prefab, room, cellRelativeToRoom, false)` [VAN].
- `Start()`: `m_room = transform.position.GetAbsoluteRoom()` (or implement `IPlaceConfigurable.ConfigureOnPlacement(RoomHandler)`),
  `m_room.RegisterInteractable(this)`, `SpriteOutlineManager.AddOutlineToSprite(sprite, Color.black)`; range callbacks swap white/black.
  `GetDistanceToPoint` = `Vector2.Distance(point, transform.position) / 1.5f` or `Vector2.Distance(point, BraveMathCollege.ClosestPointOnRectangle(
  point, specRigidbody.UnitBottomLeft, specRigidbody.UnitDimensions)) / 1.5f`; `GetOverrideMaxDistance` = -1 (default reach) or 1.5.
- `Interact`: `if (!TextBoxManager.HasTextBox(talkpoint)) StartCoroutine(...)` — `interactor.SetInputOverride("npcConversation")`,
  `Pixelator.Instance.LerpToLetterbox(0.35f, 0.25f)`, `MainCameraController.SetManualControl(true, true); OverridePosition = pos`; per line
  `TextBoxManager.ClearTextBox(talkpoint); ShowTextBox(talkpoint.position, talkpoint, -1f, line, "owl", instant: false, showContinueText: true)`
  and wait for `BraveInput.GetInstanceForPlayer(p.PlayerIDX).ActiveActions.GetActionFromType(GungeonActions.GungeonActionType.Interact).WasPressed`
  (or `BraveInput.GetInstanceForPlayer(0).WasAdvanceDialoguePressed()`); then `ClearTextBox`, `ClearInputOverride`, `LerpToLetterbox(1f, 0.25f)`,
  `SetManualControl(false, true)`. Choices: `GameUIRoot.Instance.DisplayPlayerConversationOptions(player, string[])` + poll
  `GameUIRoot.Instance.GetPlayerConversationResponse(out int)` under `SetInputOverride("dialogueResponse")` [VAN `AdvancedDialogueBox`].
- Mouth flap: `ShopAPI.GenerateBlankAIAnimator(go)`, `TalkAnimation = new DirectionalAnimation { Type = Single, Prefix = "nurse_talk",
  AnimNames = {""}, Flipped = {None} }`, then `aiAnimator.PlayUntilCancelled("talk")` / `EndAnimation()` around each line [MOD OMITB, VAN].
- Modular's 40-line minimum (`Past/Prefabs/Objects/QuickInterractable.cs`): `DungeonPlaceableBehaviour, IPlayerInteractable, IPlaceConfigurable`
  whose `Interact` is `TextBoxManager.ShowThoughtBubble(interactor.sprite.WorldCenter + (1,1), talkPoint, -1f, text, true, false)`.

### 4.2 The vanilla way: `TalkDoerLite` + PlayMaker (only for vanilla conversation UX)

`TalkDoerLite : DungeonPlaceableBehaviour, IPlayerInteractable` [VAN]: `speakPoint`, `audioCharacterSpeechTag` ("oldman", "owl", "golem"),
`playerApproachRadius`, `conversationBreakRadius`, `PreventInteraction`, `AllowPlayerToPassEventually`, `usesOverrideInteractionRegion` (+
offset/dimensions), `overrideInteractionRadius`, `MovementSpeed`, `PathableTiles`, `echo1/echo2`, `OnGenericFSMActionA..D`. `Interact` ->
`SendPlaymakerEvent("playerInteract")`; also `takePlayerDamage`, `playerEnteredRoom`, `playerExitedRoom`, and
`GameManager.BroadcastRoomTalkDoerFsmEvent("roomCleared")` for every NPC in the player's room. Gotcha: `GetDistanceToPoint` returns 1000
while `BestActivePlayer.IsInCombat` if the NPC has an `AIActor`. Vanilla actions (`HutongGames.PlayMaker.Actions`) [VAN]: `BeginConversation
{ conversationType Normal/Passive, locked }`, `DialogueBox { sequence Default/Sequential/SeqThenRepeatLast/SeqThenRemoveState/Mutliline/
PersistentSequential, dialogue FsmString[] ("#KEYS"), responses, events, forceCloseTime, zombieTime, SuppressDefaultAnims, OverrideTalkAnim,
PlayBoxOnInteractingPlayer, IsThoughtBubble, AlternativeTalker }`, `EndConversation`, `PlayBraveAnimation`, `Wait`, `SpawnEnemies {
roomEventTrigger }` (1.4), `CallGenericTalkDoerCallback { CallCallbackA..D }` (runs your C#), `WalkToPlayer`, `StartPathMoving`,
`SetNpcVisibility`, `BroadcastEventInRoom`, `SetCharacterSpecificSaveFlag`, `Teleport`. Multi-line keys: `ETGMod.Databases.Strings.Core.
AddComplex("#KEY", line)`. Planetside `NPC Stuff/Example Code/LilShit.cs` is the full worked example (Idle -> Greet -> Choice -> Accept/
Reject, ends with `playMakerFSM.Fsm.InitData()`); OMITB/ETB clone the `Merchant_Key` FSM via `JsonUtility` and patch its strings [MOD].

---

## 5. Cutscene tools [VAN]

```csharp
PastCameraUtility.LockConversation(Vector2 lockPos);  // SetInputOverride("past") both players, LerpToLetterbox(0.35f, 0.25f), DoFinalNonFadedLayer = true,
                                                      // ToggleLowerPanels(false)/HideCoreUI, MainCameraController.SetManualControl(true); OverridePosition = lockPos.ToVector3ZUp()
PastCameraUtility.UnlockConversation();               // inverse (letterbox 0.5f, ShowCoreUI, SetManualControl(false))
PlayerController: SetInputOverride(string reason) / ClearInputOverride(reason)  // ref-counted per reason; CurrentInputState / AcceptingAnyInput
    ForceIdleFacePoint(Vector2 dir, bool quadrantize = true); ForceStopDodgeRoll(); ToggleGunRenderers(bool, reason); ToggleHandRenderers(bool, reason)
    ForceMoveToPoint(Vector2 targetPosition, float initialDelay = 0f, float maximumTime = 2f)                                  // walks the player
    ForceMoveInDirectionUntilThreshold(Vector2 direction, float axialThreshold, float initialDelay = 0f, float maximumTime = 1f, List<SpeculativeRigidbody> passThrough = null)
    ForceWalkInDirectionWhilePaused(DungeonData.Direction direction, float thresholdValue); WarpToPoint(Vector2 p, bool useDefaultPoof = false, bool doFollowers = false)
CameraController (GameManager.Instance.MainCameraController): SetManualControl(bool manualControl, bool shouldLerp = true); Vector3 OverridePosition;
    UpdateOverridePosition(Vector3 newPos, float duration) /* pan */; DoScreenShake(ScreenShakeSettings, Vector2? origin)
Pixelator.Instance: TriggerPastFadeIn(); FadeToBlack(float duration, bool reverse = false, float holdTime = 0f); FadeToColor(float duration, Color c, bool reverse = false, float holdTime = 0f);
    LerpToLetterbox(float targetFraction, float duration); FreezeFrame(); TimedFreezeFrame(float duration, float hold); ClearFreezeFrame(); bool DoFinalNonFadedLayer
TextBoxManager: ShowTextBox(Vector3 worldPosition, Transform parent, float duration, string text, string audioTag = "", bool instant = true,
        BoxSlideOrientation slideOrientation = NO_ADJUSTMENT, bool showContinueText = false, bool useAlienLanguage = false)  // duration -1 = until ClearTextBox
    ShowThoughtBubble(worldPosition, parent, duration, text, bool instant = true, bool showContinueText = false, string overrideAudioTag = "")
    ShowInfoBox/ShowLetterBox/ShowStoneTablet/ShowWoodPanel/ShowNote(worldPosition, parent, duration, text, instant, showContinueText)
    ClearTextBox(Transform parent); ClearTextBoxImmediate(parent); HasTextBox(parent); TextBoxCanBeAdvanced(parent); AdvanceTextBox(parent); GetEstimatedReadingTime(text)
AIAnimator: PlayUntilCancelled(name, ...); PlayUntilFinished(name, ...); PlayForDuration(name, duration, ...); EndAnimation(); EndAnimationIf(name); IsPlaying(name)
tk2dSpriteAnimator: Play(name); PlayForDuration(name, duration, nextClip); IsPlaying(name); PlayAndDisableObject(name)
```
Vanilla usage: Robot past `ForceMoveInDirectionUntilThreshold(Vector2.down, p.CenterPosition.y - 5f, 0.25f)`; Pilot past
`UpdateOverridePosition(OverridePosition + (0, 8.5f, 0), 3f)` and `WarpToPoint`; Convict past `FadeToBlack(0.25f, true, 0.05f);
TriggerPastFadeIn();`; Marine past skips a timed line on `WasAdvanceDialoguePressed()`. Walking NPCs, three options:
1. **`TalkDoerLite` pathing** (Convict past, `WalkToPlayer` action): `npc.PathfindToPosition(Vector2 target, Vector2? overridePathEnd = null,
   CellValidator v = null)`, then per frame `npc.specRigidbody.Velocity = npc.GetPathVelocityContribution(lastPos, 16); lastPos =
   npc.specRigidbody.UnitCenter;` until `npc.CurrentPath == null`, then `Velocity = Vector2.zero` (needs a rigidbody, `MovementSpeed`,
   `PathableTiles`); `ForceTimedSpeech(words, initialDelay, duration, slideOrientation)` talks while walking; `SetNpcVisibility.SetVisible(npc, bool)`.
2. **`AIActor` pathing** (the Vet pacing in): `actor.PathfindToPosition(target)` with the speculator disabled, poll `actor.PathComplete`,
   `actor.ClearPath()`; the actor's own `Update` applies the velocity [INF].
3. **Plain tween**: coroutine lerping `transform.position` (z = y) or setting `specRigidbody.Velocity`, then `specRigidbody.Reinitialize()`
   — what `VetVisitController.Place` already does for the player.

## 6. Recommendation (one line each)

Flow: `CreateNewFlow` + `GenerateDefaultNode` chain, one facing exit per room, generator hallways, doors from the Soldier prefab or `Base_Castle`.
Waves: five equal-length enemy arrays in `clinic_room.py`; layer 0 auto-seals, later layers chain; scripted beats use `SealRoom()` + layers/`Spawn`.
Enemies: `EnemyBuilder.BuildPrefab(..., false)` + hitbox/HP + `BuildAnimation` clips + Bullet Kin behaviours + `DuplicateAIShooterAndAIBulletBank`.
NPCs: `IPlayerInteractable` + `TextBoxManager` as a custom object; PlayMaker only for vanilla-style choice dialogue.
Cutscenes: `PastCameraUtility` + `SetInputOverride("past")` + `ForceMoveToPoint` + `TalkDoerLite` pathing + `ShowTextBox(..., -1f, ...)` with a skip key.
