# 05 — Custom boss research: "The Vet" (Alexandria 0.5.10 EnemyAPI)

Goal: a custom boss (veterinarian with a syringe gun; 2–3 attacks, intro card, boss health bar,
death sequence) built with Alexandria 0.5.10 and placed in a custom room / Pluto's custom past.

How each claim was verified (tags used throughout):

| Tag | Meaning |
|-----|---------|
| **[IL]** | Read from `monodis` dumps of the exact DLLs in `PlutoTheCat/packages/` (`EtG.Alexandria.0.5.10/lib/net35/Alexandria.dll`, `EtG.GameLibs.2.1.9.1/lib/net35/Assembly-CSharp.dll`). Dumps live in the scratchpad `il3/` (`alex.il`, `game.il`). |
| **[SRC]** | Alexandria source, `Nevernamed22/Alexandria` branch `main` (the Thunderstore-linked repo). The EnemyAPI files there match the 0.5.10 IL signature-for-signature; `BossBuilder.cs` there contains the same template GUIDs as the 0.5.10 IL. |
| **[MOD]** | Usage in open-source mods (Frost & Gunfire, Expand The Gungeon, modding guide). |
| **[DECOMP]** | Behaviour of the *game* that only decompiled game code would prove. **The GameLibs `Assembly-CSharp.dll` in `packages/` is a reference stub — every method body is `ldnull; throw`** (checked on `HealthHaver::EndBossState`), so from it I can only quote signatures, fields and enum values, never call graphs. |

---

## 0. TL;DR recipe (8 steps)

1. **Do not call `EnemyBuilder.Init()`/`BossBuilder.Init()`** — Alexandria's own plugin calls `EnemyTools.Init()`, `EnemyBuilder.Init()`, `BossBuilder.Init()` at startup [IL: `Alexandria.Alexandria`, il3/alex.il lines 36236–36240]. Just `[BepInDependency(Alexandria.Alexandria.GUID)]` (already in `Plugin.cs`).
2. `GameObject prefab = BossBuilder.BuildPrefab("The Vet", GUID, "PlutoTheCat/Resources/Bosses/vet/idle/vet_idle_001", hitboxOffsetPx, hitboxSizePx, HasAiShooter: false);` — gives you a stripped Fungun clone with `tk2dSprite`, `SpeculativeRigidbody` (one `EnemyCollider`), `tk2dSpriteAnimator`, `AIAnimator`, `KnockbackDoer`, `HealthHaver` (15000 HP!), `AIActor`, `BehaviorSpeculator`, `AIBulletBank` and an `EnemyDatabaseEntry` (§1.3).
3. Fix the template quirks (§1.3.2): set real HP, `hh.bossHealthBar = HealthHaver.BossBarType.MainBar`, `hh.overrideBossName`, **add an `EnemyHitBox` `PixelCollider`** (bullets do not hit `EnemyCollider`), and **replace `bs.AttackBehaviors`** (the Fungun's attack list survives).
4. Build clips with `EnemyBuilder.BuildAnimation(aiAnimator, "vet_idle", ROOT + "/idle", fps, asm)` (one folder = one clip, PNGs zero-padded), then wrap them in `DirectionalAnimation`s: `aiAnimator.IdleAnimation`/`MoveAnimation` for the two mandatory ones, `EnemyBuildingTools.AddNewDirectionAnimation(...)` for `tell`, `fire`, `intro`, `die` (§3).
5. Bullet bank: `bank.Bullets.Add(EnemyBuildingTools.CopyBulletBankEntry(EnemyDatabase.GetOrLoadByGuid(BULLET_KIN).bulletBank.GetBullet("default"), "syringe", "DNC"))`; attacks = `ShootBehavior { ShootPoint, BulletScript = new CustomBulletScriptSelector(typeof(MyScript)), TellAnimation = "tell", FireAnimation = "fire", Cooldown… }` inside an `AttackBehaviorGroup`; phases via `MaxHealthThreshold`/`MinHealthThreshold`/`HealthThresholds` on each attack (§2.4, §6).
6. Intro + card + music: `GenericIntroDoer` component (`triggerType = PlayerEnteredRoom`, `introAnim`, `BossMusicEvent`, `portraitSlideSettings = new PortraitSlideSettings { bossNameString, bossSubtitleString, bossArtSprite = Texture2D … }`). Health bar comes from `HealthHaver.bossHealthBar = MainBar`; kill-cam/boss-death handling comes from `HealthHaver.IsBoss` (§4).
7. Death: `ExplodeOnDeath` component (`deathType = OnDeathBehavior.DeathType.Death`, `explosionData = …`) plus a small `BraveBehaviour` on the prefab whose `Start()` does `healthHaver.OnPreDeath += …` (events are per-instance, never copied from the prefab) (§4.3).
8. Room: a `.room`/`.newroom` from Room Architect Tool with `category = "BOSS"`, `bossSubCategory = "FLOOR_BOSS"` and the boss GUID in `enemyGUIDs`, loaded with `RoomFactory.BuildNewRoomFromResource(...)` + `DungeonHandler.Register(...)` — or in code: `RoomFactory.CreateEmptyRoom` + `AddExit` + `AddEnemyToRoom(...)` (which adds the seal/unseal room events) + `room.category = BOSS` + push into `StaticReferences.RoomTables[...]`. **In a past nothing ends automatically** — vanilla pasts have per-past controller classes; we hook `OnPreDeath`, set `CharacterSpecificGungeonFlags.KILLED_PAST` and leave the level ourselves (§5.4).

---

## 1. What is (and is not) in Alexandria 0.5.10 `Alexandria.EnemyAPI`

### 1.1 Type list [IL]

`monodis --typedef Alexandria.dll` → namespace `Alexandria.EnemyAPI` contains exactly:

```
Alexandria.EnemyAPI.HealthHaverExt          (MonoBehaviour)
Alexandria.EnemyAPI.AIActorUtility          (static)
Alexandria.EnemyAPI.AttackBehaviourUtility  (static)
Alexandria.EnemyAPI.EnemyBuildingTools      (static)
Alexandria.EnemyAPI.BossBuilder             (static)  + nested enum AnimationType
Alexandria.EnemyAPI.EnemyBuilder            (static)  + nested enum AnimationType
Alexandria.EnemyAPI.EnemyTools              (static)
Alexandria.EnemyAPI.Hooks                   (static; only Init())
Alexandria.EnemyAPI.OverrideBehavior        (abstract)
Alexandria.EnemyAPI.CustomBulletScriptSelector : BulletScriptSelector
```

**Not present in 0.5.10** (names that float around in older tutorials): `BehaviorBuilder`, `EnemyToolbox`,
`BossBuilder.AddAnimation`, `BossBuilder.SetupBasicIntro`, `AddEnemyToDatabase`, `AddCustomBulletBank`.
`SetupBasicIntro`/`AddEnemyToDatabase` are Frost & Gunfire's *vendored* helpers (their own `EnemyAPI/BossBuilder.cs`), not Alexandria's. What they do is reproduced verbatim in §4.1 so we can inline it.

### 1.2 `Alexandria.EnemyAPI.EnemyBuilder` [IL — il3/alex.il line 211851]

```csharp
public static Dictionary<string, GameObject> Dictionary;   // guid -> prefab; consulted by a Harmony prefix on EnemyDatabase.GetOrLoadByGuid
public static void Init();                                 // called by Alexandria itself

public static GameObject BuildPrefab(string name, string guid, string defaultSpritePath,
                                     IntVector2 hitboxOffset, IntVector2 hitBoxSize, bool HasAiShooter);

// single clip: every PNG whose manifest name starts with spriteDirectory (slashes -> dots)
public static tk2dSpriteAnimationClip AddAnimation(this GameObject obj, string name, string spriteDirectory, int fps,
        EnemyBuilder.AnimationType type,
        DirectionalAnimation.DirectionType directionType = DirectionType.None,
        DirectionalAnimation.FlipType flipType = FlipType.None,
        Assembly assembly = null);

// one clip per direction suffix: files "<dir>.<enemyName>_<name>_<suffix>_0*.png"
public static tk2dSpriteAnimationClip[] AddAnimation(this GameObject obj, string enemyName, string name, string spriteDirectory, int fps,
        EnemyBuilder.AnimationType type,
        DirectionalAnimation.DirectionType directionType = DirectionType.None,
        DirectionalAnimation.FlipType flipType = FlipType.None,
        tk2dSpriteAnimationClip.WrapMode wrapMode = WrapMode.Once);

public static tk2dSpriteAnimationClip[] BuildAnimations(AIAnimator aiAnimator, string name, string enemyName,
        DirectionalAnimation.DirectionType directionType, string spriteDirectory, int fps,
        tk2dSpriteAnimationClip.WrapMode wrapMode, Assembly assembly = null);
public static tk2dSpriteAnimationClip  BuildAnimation (AIAnimator aiAnimator, string name, string spriteDirectory, int fps, Assembly assembly = null);

public static DirectionalAnimation GetDirectionalAnimation(this AIAnimator aiAnimator, string name, DirectionalAnimation.DirectionType directionType, EnemyBuilder.AnimationType type);
public static void AssignDirectionalAnimation(this AIAnimator aiAnimator, string name, DirectionalAnimation animation, EnemyBuilder.AnimationType type);

public static void DuplicateAIShooterAndAIBulletBank(GameObject targetObject, AIShooter sourceShooter, AIBulletBank sourceBulletBank,
        int startingGunOverrideID = 0, Transform gunAttachPointOverride = null,
        Transform bulletScriptAttachPointOverride = null, PlayerHandController overrideHandObject = null);

public enum AnimationType { Move = 0, Idle = 1, Fidget = 2, Flight = 3, Hit = 4, Talk = 5, Other = 6 }
```

(The IL shows the static form `AddAnimation(GameObject obj, …)`; the `this` extension form is from [SRC] `EnemyAPI/EnemyBuilder.cs`.)

`AssignDirectionalAnimation` semantics [SRC, matches IL]: `Idle → aiAnimator.IdleAnimation`, `Move → MoveAnimation`, `Flight → FlightAnimation`, `Hit → HitAnimation`, `Talk → TalkAnimation`, `Fidget → IdleFidgetAnimations.Add`, **anything else (`Other`) → `aiAnimator.OtherAnimations.Add(new AIAnimator.NamedDirectionalAnimation { name = name, anim = animation })`**. `GetDirectionalAnimation` returns `null` for `Other`, so every `AddAnimation(..., AnimationType.Other, ...)` call creates a *new* named directional animation.

### 1.3 `Alexandria.EnemyAPI.BossBuilder` [IL — il3/alex.il line 211255]

```csharp
public static Dictionary<string, GameObject> Dictionary;
public static void Init();
public static GameObject BuildPrefab(string name, string guid, string defaultSpritePath,
                                     IntVector2 hitboxOffset, IntVector2 hitBoxSize,
                                     bool HasAiShooter, bool UsesAttackGroup = false);
public enum AnimationType { Move, Idle, Fidget, Flight, Hit, Talk, Other }   // identical to EnemyBuilder's
```

There is **no** `AddAnimation` on `BossBuilder` in 0.5.10; use `EnemyBuilder.AddAnimation`/`BuildAnimation` on the boss prefab (they only need an `AIAnimator`).

#### 1.3.1 What `BossBuilder.BuildPrefab` actually does [IL body + SRC `EnemyAPI/BossBuilder.cs`]

Verbatim from [SRC] (identical call sequence in the 0.5.10 IL):

```csharp
public static GameObject BuildPrefab(string name, string guid, string defaultSpritePath, IntVector2 hitboxOffset, IntVector2 hitBoxSize, bool HasAiShooter, bool UsesAttackGroup = false)
{
    if (BossBuilder.Dictionary.ContainsKey(guid)) { ETGModConsole.Log("BossBuilder: Yea something went wrong. Complain to Neighborino about it."); return null; }
    var prefab = GameObject.Instantiate(behaviorSpeculatorPrefab);          // Init(): Fungun "f905765488874846b7ff257ff81d6d0c", children except "GunAttachPoint" and all components except BehaviorSpeculator/Transform/SpeculativeRigidbody/MeshFilter/MeshRenderer destroyed
    prefab.name = name;
    var sprite = SpriteBuilder.SpriteFromResource(defaultSpritePath, prefab, Assembly.GetCallingAssembly()).GetComponent<tk2dSprite>();
    sprite.SetUpSpeculativeRigidbody(hitboxOffset, hitBoxSize).CollideWithOthers = true;   // ONE PixelCollider on CollisionLayer.EnemyCollider
    prefab.AddComponent<tk2dSpriteAnimator>();
    AIAnimator aiAnimator = prefab.AddComponent<AIAnimator>();
    aiAnimator.OtherVFX = new List<AIAnimator.NamedVFXPool>(0);
    var knockback = prefab.AddComponent<KnockbackDoer>(); knockback.weight = 1;
    var healthHaver = prefab.AddComponent<HealthHaver>();
    healthHaver.RegisterBodySprite(sprite); healthHaver.PreventAllDamage = false;
    healthHaver.SetHealthMaximum(15000); healthHaver.FullHeal();
    var aiActor = prefab.AddComponent<AIActor>();
    aiActor.State = AIActor.ActorState.Normal; aiActor.EnemyGuid = guid; aiActor.HasShadow = false;
    var bs = prefab.GetComponent<BehaviorSpeculator>();
    bs.MovementBehaviors = new List<MovementBehaviorBase>();
    bs.TargetBehaviors   = new List<TargetBehaviorBase>();
    bs.OverrideBehaviors = new List<OverrideBehaviorBase>();
    bs.OtherBehaviors    = new List<BehaviorBase>();
    bs.AttackBehaviorGroup.AttackBehaviors = new List<AttackBehaviorGroup.AttackGroupItem>();   // NOTE: bs.AttackBehaviors itself is NOT reset
    if (HasAiShooter) { /* re-creates the *template* from Bullet Kin 01972dee89fc4404a5c408d50007dad5 — affects the NEXT call, not this prefab */ }
    else { AIBulletBank aibulletBank = prefab.AddComponent<AIBulletBank>(); aibulletBank.Bullets = new List<AIBulletBank.Entry>(); }
    EnemyDatabase.Instance.Entries.Add(new EnemyDatabaseEntry() { myGuid = guid, placeableWidth = 2, placeableHeight = 2, isNormalEnemy = true });
    BossBuilder.Dictionary.Add(guid, prefab);
    GameObject.DontDestroyOnLoad(prefab); FakePrefab.MarkAsFakePrefab(prefab); prefab.SetActive(false);
    StaticReferenceManager.AllHealthHavers.Remove(healthHaver);
    return prefab;
}
```

`EnemyBuilder.BuildPrefab` differs only in: template is the Bullet Kin, it also sets `bs.AttackBehaviors = new List<AttackBehaviorBase>()`, does not touch `HasShadow`, and adds the `AIBulletBank` unconditionally [IL].

#### 1.3.2 Quirks you must handle after `BossBuilder.BuildPrefab`

| Quirk | Consequence | Fix |
|-------|-------------|-----|
| `HasAiShooter = true` does not add an `AIShooter`; it rebuilds the *static template* and skips the `AIBulletBank` for this prefab. | No bullet bank → `ShootBehavior`/bullet scripts have nothing to fire. | Pass `false`; if the Vet must visibly hold a gun, call `EnemyBuilder.DuplicateAIShooterAndAIBulletBank(prefab, bulletKin.aiShooter, bulletKin.GetComponent<AIBulletBank>(), gunId, prefab.transform.Find("GunAttachPoint"))` afterwards (that method returns early if both components already exist [SRC]). |
| Template is the **Fungun** (`f905765488874846b7ff257ff81d6d0c` → `EnemyGUIDs.Fungun_GUID` [IL]); `bs.AttackBehaviors` is inherited. | The boss keeps the Fungun's attack list (only the group's *item list* is emptied). | Always assign `bs.AttackBehaviors = new List<AttackBehaviorBase> { new AttackBehaviorGroup { … } }`. (`bs.AttackBehaviorGroup` is a getter that finds a group inside `AttackBehaviors` [DECOMP]; after replacing the list it points at *your* group.) |
| `SetHealthMaximum(15000)` | 15000 HP boss. | `hh.ForceSetCurrentHealth(x); hh.SetHealthMaximum(x);` |
| `SetUpSpeculativeRigidbody` creates only `CollisionLayer.EnemyCollider` [SRC `SpriteBuilder.cs`: `body.AddCollider(CollisionLayer.EnemyCollider, offset, dimensions)`]. | Player bullets collide with `EnemyHitBox`; without one the boss cannot be damaged (Frost & Gunfire adds both layers by hand). | Add a second manual `PixelCollider` on `CollisionLayer.EnemyHitBox` (§3.4). |
| `EnemyDatabaseEntry.isNormalEnemy = true`, `isInBossTab` unset, no `EncounterTrackable`. | Fine for gameplay; no Ammonomicon page. | Optional: `entry.isInBossTab = true`, add `EncounterTrackable` (F&G `SetupEntry`). |
| `knockback.weight = 1` | Boss gets shoved around. | `actor.knockbackDoer.weight = 200f` (or `float.MaxValue`). |
| `HasShadow = false`, `aiActor.IsNormalEnemy` untouched. | Cosmetic; `IsNormalEnemy` effect on bosses unverified. | `EnemyBuildingTools.AddShadowToAIActor` if wanted. |

### 1.4 Other 0.5.10 EnemyAPI helpers [IL]

```csharp
// Alexandria.EnemyAPI.EnemyBuildingTools (il3/alex.il line 210730)
public static AIBeamShooter AddAIBeamShooter(AIActor enemy, Transform transform, string name, Projectile beamProjectile, ProjectileModule beamModule = null, float angle = 0);
public static DirectionalAnimation AddNewDirectionAnimation(AIAnimator animator, string Prefix, string[] animationNames, DirectionalAnimation.FlipType[] flipType, DirectionalAnimation.DirectionType directionType = DirectionType.Single);
public static void DestroyUnnecessaryHandObjects(Transform transform);           // kills "BulletSkeletonHand(Clone)" children
public static void AddShadowToAIActor(AIActor actor, GameObject shadowObject, Vector2 attachpoint, string name = "shadowPosition");
public static GameObject GenerateShootPoint(GameObject attacher, Vector2 attachpoint, string name = "shootPoint");
public static AIBulletBank.Entry CopyBulletBankEntry(AIBulletBank.Entry entryToCopy, string Name, string AudioEvent = null, VFXPool muzzleflashVFX = null, bool ChangeMuzzleFlashToEmpty = true);
//   ^ AudioEvent: "DNC" keeps the original sound, null = silent [SRC doc comment]

// Alexandria.EnemyAPI.CustomBulletScriptSelector : BulletScriptSelector (line 215556)
public Type bulletType;
public CustomBulletScriptSelector(Type _bulletType);
public Brave.BulletScript.Bullet CreateInstance();  public bool IsNull { get; }  public BulletScriptSelector Clone();

// Alexandria.EnemyAPI.AttackBehaviourUtility (line 209908)
public static bool IsAttackBehaviorGroup(AttackBehaviorBase self, out List<AttackBehaviorBase> groupItems);
public static List<T> FindAttackBehaviorsInGroup<T>(AttackBehaviorGroup group) where T : AttackBehaviorBase;
public static List<T> FindAttackBehaviorsInSequentialGroup<T>(SequentialAttackBehaviorGroup group);
public static List<T> FindAttackBehaviorsInSimultaneousGroup<T>(SimultaneousAttackBehaviorGroup group);
public static List<T> FindAttackBehaviors<T>(BehaviorSpeculator spec);
public static AIActor GetAttackBehaviourOwner(BehaviorBase behav);

// Alexandria.EnemyAPI.EnemyTools (line 213718)
public static HealthHaverExt Ext(HealthHaver hh);                 // hh.Ext().ModifyProjectileDamage / OnDamagedContext callbacks
public static void ManualAddOB(Type ob);                          // register an OverrideBehavior subclass
public static void DebugInformation(BehaviorSpeculator behavior, string path = null);      // dumps a vanilla enemy's behaviours to a file — use it to copy a boss's numbers
public static void DebugBulletBank(AIBulletBank bank, string path = null);

// Alexandria.EnemyAPI.OverrideBehavior (abstract, line 215393) — patch an EXISTING enemy's speculator at Awake
public abstract string OverrideAIActorGUID { get; }
public void SetupOB(AIActor actor);  public virtual bool ShouldOverride();  public abstract void DoOverride();
protected void SetupBehavior(AttackBehaviorBase behavior);  protected void SetupBehaviorABG(AttackBehaviorBase behavior, string name = null, int probability = ?);
protected AIActor actor; protected BehaviorSpeculator behaviorSpec; protected AIBulletBank bulletBank; protected HealthHaver healthHaver;

// Alexandria.EnemyAPI.AIActorUtility (line 208110)
public static void DeleteOwnedBullets(GameActor enemy, float chancePerProjectile = ?, bool deleteBulletLimbs = ?);
public static void DoCorrectForWalls(AIActor enemy);  public static Vector2 ClosestPointOnEnemy(AIActor target, Vector2 pointComparison);
public static AIActor AdvancedTransmogrify(AIActor startEnemy, AIActor EnemyPrefab, GameObject EffectVFX, string audioEvent = ?, ...);
```

### 1.5 `Alexandria.ItemAPI.SpriteBuilder` / `ResourceExtractor` bits that matter [IL line ~80800, SRC `ItemAPI/SpriteTools/*.cs`]

```csharp
public static GameObject SpriteFromResource(string spriteName, GameObject obj = null, Assembly assembly = null);   // ".png" appended if missing; sprite goes into the shared item collection
public static SpeculativeRigidbody SetUpSpeculativeRigidbody(this tk2dSprite sprite, IntVector2 offset, IntVector2 dimensions);  // EnemyCollider only
public static tk2dSpriteCollectionData ConstructCollection(GameObject obj, string name, bool destroyOnLoad = false);
public static int AddSpriteToCollection(string resourcePath, tk2dSpriteCollectionData collection, Assembly assembly = null);
public static tk2dSpriteAnimationClip AddAnimation(tk2dSpriteAnimator animator, tk2dSpriteCollectionData collection, List<int> spriteIDs, string clipName, tk2dSpriteAnimationClip.WrapMode wrapMode = ?, float fps = ?);
public static Texture2D ResourceExtractor.GetTextureFromResource(string resourceName, Assembly assembly = null);   // boss card art
public static string[]  ResourceExtractor.GetResourceNames(Assembly assembly = null);
```

`Shared.SortedResourceNames(Assembly)` is `internal` [IL: `.method assembly static`] — it caches `GetManifestResourceNames().OrderBy(x => x)` per assembly. That ordering is what decides frame order (§3.2).

---

## 2. Game-side types the boss needs (stubbed DLL → fields / signatures / enums only) [IL: il3/game.il]

### 2.1 Intro: `GenericIntroDoer`, `PortraitSlideSettings`, `SpecificIntroDoer`

`GenericIntroDoer : TimeInvariantMonoBehaviour, IPlaceConfigurable` (game.il line 411432). Public fields, verbatim:

```
GenericIntroDoer.TriggerType triggerType      // PlayerEnteredRoom = 10, BossTriggerZone = 20
float  initialDelay
float  cameraMoveSpeed
AIAnimator specifyIntroAiAnimator
string BossMusicEvent                          // Wwise event, e.g. "Play_MUS_Boss_Theme_Beholster" (F&G default)
bool   PreventBossMusic
bool   InvisibleBeforeIntroAnim
string preIntroAnim,  preIntroDirectionalAnim
string introAnim,     introDirectionalAnim     // raw clip name vs. directional (OtherAnimations) name
bool   continueAnimDuringOutro
GameObject cameraFocus;  Vector2 roomPositionCameraFocus
bool   restrictPlayerMotionToRoom
bool   fusebombLock
float  AdditionalHeightOffset
bool   SkipBossCard
PortraitSlideSettings portraitSlideSettings
bool   HideGunAndHand
Action OnIntroFinished
// properties: Vector2 BossCenter {get}; bool SkipFinalizeAnimation {get;set}; bool SuppressSkipping {get;set}; static bool SkipFrame
// methods: void ConfigureOnPlacement(RoomHandler room) [IPlaceConfigurable]; void PlayerEntered(PlayerController); void TriggerSequence(PlayerController);
//          IEnumerator WaitForBossCard(); void EndSequence(bool isChildSequence = false); void OnDeath(Vector2 deathDir); void ModifyCamera(bool); void RestrictMotion(bool)
```

`PortraitSlideSettings` (serializable class, line 410622):

```
string bossNameString; string bossSubtitleString; string bossQuoteString;
Texture bossArtSprite;                 // the big boss picture on the card (Texture2D works)
IntVector2 bossSpritePxOffset; IntVector2 topLeftTextPxOffset; IntVector2 bottomRightTextPxOffset;
Color bgColor;
```

`SpecificIntroDoer : BraveBehaviour` (abstract, line 412147) — optional companion component for custom choreography; everything virtual:

```csharp
public virtual IntVector2 OverrideExitBasePosition(DungeonData.Direction directionToWalk, IntVector2 exitBaseCenter);
public virtual Vector2? OverrideIntroPosition { get; }   public virtual Vector2? OverrideOutroPosition { get; }
public virtual string  OverrideBossMusicEvent { get; }
public virtual void PlayerWalkedIn(PlayerController player, List<tk2dSpriteAnimator> animators);
public virtual void OnCameraIntro();  public virtual void StartIntro(List<tk2dSpriteAnimator> animators);
public virtual bool IsIntroFinished { get; }
public virtual void OnBossCard();  public virtual void OnCameraOutro();  public virtual void OnCleanup();  public virtual void EndIntro();
public IEnumerator TimeInvariantWait(float duration);
```
Mods that use it (`[RequireComponent(typeof(GenericIntroDoer))]`): Frost & Gunfire `Enemies/RoomMimicIntro.cs` (just plays a sound in `PlayerWalkedIn`), Expand The Gungeon `ExpandComponents/ExpandWesternBroIntroDoer.cs` (plays "intro"/"intro2" clips in `StartIntro`, sets `finished`, re-enables the AIAnimator in `EndIntro`). Not needed for a plain "walk in, play intro clip, show card" boss.

Boss UI: `GameUIRoot.Instance.bossController` (`GameUIBossHealthController`, also `bossController2`, `bossControllerSide`) with `RegisterBossHealthHaver(HealthHaver healthHaver, string bossName = null)`, `DeregisterBossHealthHaver(HealthHaver)`, `ForceUpdateBossHealth(float current, float max, string bossName = null)`, `TriggerBossPortraitCR(PortraitSlideSettings pss)`, `EndBossPortraitEarly()`; `BossCardUIController` does the card animation (`CoreSequence(PortraitSlideSettings)`). You never call these directly — the intro doer / HealthHaver do [DECOMP].

### 2.2 `HealthHaver` boss fields (line ~423700)

```
HealthHaver.BossBarType bossHealthBar     // None=0, MainBar=1, SecondaryBar=2, CombinedBar=3, SecretBar=4, VerticalBar=5, SubbossBar=6
string overrideBossName                   // text on the bar
bool   OnlyAllowSpecialBossDamage
string overrideDeathAudioEvent, overrideDeathAnimation, overrideDeathAnimBulletScript
bool   flashesOnDamage, PreventAllDamage, persistsOnDeath
const float c_bossDpsCapWindow = 3f;  float m_bossDpsCap   // bosses get a DPS cap (GameLevelDefinition.bossDpsCap)
event Action<Vector2> OnPreDeath;  event Action<Vector2> OnDeath;
bool IsBoss {get}; bool IsSubboss {get}; bool UsesSecondaryBossBar {get}; bool UsesVerticalBossBar {get}; bool HasHealthBar {get}
void SetHealthMaximum(float targetValue, float? amountOfHealthToGain = null, bool keepHealthPercentage = false);
void ForceSetCurrentHealth(float h);  void RegisterBodySprite(tk2dBaseSprite sprite, bool flashIndependentlyOnDamage = false, int flashPixelCollider = ?);
void ApplyDamage(float damage, Vector2 direction, string sourceName, CoreDamageTypes damageTypes = ?, DamageCategory damageCategory = ?, bool ignoreInvulnerabilityFrames = ?, PixelCollider hitPixelCollider = null, bool ignoreDamageCaps = ?);
bool BossHealthSanityCheck(float rawDamage);  void EndBossState(bool triggerKillCam);  tk2dSpriteAnimationClip GetDeathClip(float damageAngle);
```

`BossKillCam : TimeInvariantMonoBehaviour` (line 622639): `static bool BossDeathCamRunning; float trackToBossTime, returnToPlayerTime; void TriggerSequence(Projectile p, SpeculativeRigidbody bossSRB); void EndSequence(); void KillAllEnemies(); void ForceCancelSequence();` plus `GameUIRoot.m_bossKillCamActive`. It is driven by `HealthHaver.EndBossState(true)` when an `IsBoss` haver dies [DECOMP]; community bosses (F&G Room Mimic, ETG Western Bros) get the slow-mo kill cam just by having `bossHealthBar = MainBar`.

### 2.3 Death components

```
OnDeathBehavior : BraveBehaviour (abstract, line 426899)
  OnDeathBehavior.DeathType deathType     // PreDeath=0, Death=1, DeathAnimTrigger=2
  float preDeathDelay; string triggerName   // triggerName = animation event name for DeathAnimTrigger
  abstract void OnTrigger(Vector2 dirVec)

ExplodeOnDeath : OnDeathBehavior (line 422567)
  ExplosionData explosionData; bool immuneToIBombApp;
  bool LinearChainExplosion; float ChainDuration; float ChainDistance; int ChainNumExplosions; bool ChainIsReversed; GameObject ChainTargetSprite; ExplosionData LinearChainExplosionData

SpawnEnemyOnDeath : OnDeathBehavior (line ~424800)
  float chanceToSpawn; string spawnVfx; EnemySelection enemySelection; string[] enemyGuidsToSpawn; int minSpawnCount, maxSpawnCount; SpawnPosition spawnPosition; ...

ExplosionData (line 597262)
  bool useDefaultExplosion, doDamage, forceUseThisRadius; float damageRadius, damageToPlayer, damage;
  bool breakSecretWalls; float secretWallsRadius; bool forcePreventSecretWallDamage; bool doDestroyProjectiles;
  bool doForce; float pushRadius, force, debrisForce; bool preventPlayerForce; float explosionDelay; bool usesComprehensiveDelay; float comprehensiveDelay;
  GameObject effect; bool doScreenShake; ScreenShakeSettings ss; bool doStickyFriction; bool doExplosionRing;
  bool isFreezeExplosion; float freezeRadius; GameActorFreezeEffect freezeEffect; bool playDefaultSFX; bool IsChandelierExplosion
```
Ready-made `ExplosionData` instances live on `ExplosiveModifier.explosionData` (any explosive gun projectile, e.g. RPG id 19), `ExplodeOnDeath.explosionData` of vanilla exploding enemies, `MinorBreakable.explosionData`, etc. [IL field scan]. Copy the `effect`/`ss` references into your own `new ExplosionData { doDamage = false, … }` rather than mutating the shared one.

### 2.4 Behaviour classes (line numbers in game.il)

```
BehaviorSpeculator : FullInspector.BaseBehavior<FullSerializerSerializer> (333734)
  bool InstantFirstTick; float TickInterval; float PostAwakenDelay; bool RemoveDelayOnReinforce;
  bool OverrideStartingFacingDirection; float StartingFacingDirection; bool SkipTimingDifferentiator;
  List<OverrideBehaviorBase> OverrideBehaviors; List<TargetBehaviorBase> TargetBehaviors; List<MovementBehaviorBase> MovementBehaviors;
  List<AttackBehaviorBase> AttackBehaviors; List<BehaviorBase> OtherBehaviors;
  AttackBehaviorGroup AttackBehaviorGroup {get}; float AttackCooldown/GlobalCooldown/CooldownScale {get;set}; GameActor PlayerTarget {get;set}; bool PreventMovement {get;set}
  void Stun(float duration, bool createVFX = true); void Interrupt(); void InterruptAndDisable(); void RefreshBehaviors();
  void SetGroupCooldown(string groupName, float newCooldown); float GetGroupCooldownTimer(string groupName)

BasicAttackBehavior : AttackBehaviorBase (abstract, 332962) — base of ShootBehavior, TeleportBehavior, ShootGunBehavior...
  float Cooldown, CooldownVariance, AttackCooldown, GlobalCooldown, InitialCooldown, InitialCooldownVariance;
  string GroupName; float GroupCooldown;
  float MinRange, Range, MinWallDistance, MaxEnemiesInRoom;
  float MinHealthThreshold, MaxHealthThreshold; float[] HealthThresholds; bool AccumulateHealthThresholds;   // <- phases
  ShootBehavior.FiringAreaStyle targetAreaStyle; bool IsBlackPhantom; ResetCooldownOnDamage resetCooldownOnDamage { bool Cooldown, AttackCooldown, GlobalCooldown, GroupCooldown; float ResetCooldown };
  bool RequiresLineOfSight; int MaxUsages

ShootBehavior : BasicAttackBehavior (328418)
  GameObject ShootPoint; BulletScriptSelector BulletScript; string BulletName; float LeadAmount;
  ShootBehavior.StopType StopDuring   // None=0, Tell=1, Attack=2, Charge=3, TellOnly=4
  bool ImmobileDuringStop; float MoveSpeedModifier; bool LockFacingDirection, ContinueAimingDuringTell, ReaimOnFire, MultipleFireEvents, RequiresTarget, PreventTargetSwitching, Uninterruptible;
  bool ClearGoop; float ClearGoopRadius; bool ShouldOverrideFireDirection; float OverrideFireDirection; AIAnimator SpecifyAiAnimator;
  string ChargeAnimation; float ChargeTime; string TellAnimation; string FireAnimation; string PostFireAnimation;
  bool HideGun; bool OverrideBaseAnims; string OverrideIdleAnim, OverrideMoveAnim; bool UseVfx; string ChargeVfx, TellVfx, FireVfx, Vfx; GameObject[] EnabledDuringAttack

TeleportBehavior : BasicAttackBehavior (331316)
  bool AttackableDuringAnimation, AvoidWalls, StayOnScreen; float MinDistanceFromPlayer, MaxDistanceFromPlayer, GoneTime; bool OnlyTeleportIfPlayerUnreachable;
  BulletScriptSelector teleportOutBulletScript, teleportInBulletScript; AttackBehaviorBase goneAttackBehavior; bool AllowCrossRoomTeleportation;
  string teleportOutAnim, teleportInAnim; bool teleportRequiresTransparency, hasOutlinesDuringAnim; ShadowSupport shadowSupport (None/Fade/Animate); string shadowOutAnim, shadowInAnim; bool ManuallyDefineRoom; Vector2 roomMin, roomMax

AttackBehaviorGroup : AttackBehaviorBase (322596)
  bool ShareCooldowns; List<AttackBehaviorGroup.AttackGroupItem> AttackBehaviors;
  class AttackGroupItem { string NickName; float Probability; AttackBehaviorBase Behavior; }
SequentialAttackBehaviorGroup : AttackBehaviorBase (327451): bool RunInClass; List<AttackBehaviorBase> AttackBehaviors; List<float> OverrideCooldowns
SimultaneousAttackBehaviorGroup : AttackBehaviorBase (329545): List<AttackBehaviorBase> AttackBehaviors

BulletScriptSelector (64453): string scriptTypeName; Bullet CreateInstance(); bool IsNull; BulletScriptSelector Clone()   // vanilla picks by type name; Alexandria's CustomBulletScriptSelector picks by System.Type
```

### 2.5 Target / movement behaviours

```
TargetPlayerBehavior : TargetBehaviorBase (347369): float Radius; bool LineOfSight; bool ObjectPermanence; float SearchInterval; bool PauseOnTargetSwitch; float PauseTime
SeekTargetBehavior : RangedMovementBehavior (345217): bool StopWhenInRange; float CustomRange; bool LineOfSight; bool ReturnToSpawn; float SpawnTetherDistance; float PathInterval
MoveErraticallyBehavior : MovementBehaviorBase (344879): float PathInterval; float PointReachedPauseTime; bool PreventFiringWhileMoving; float InitialDelay; bool StayOnScreen; bool AvoidTarget; bool UseTargetsRoom
```

### 2.6 Bullet scripts (`Brave.BulletScript`, game.il 64964–66700)

```csharp
public class Bullet {
  public Bullet(string bankName = ?, bool suppressVfx = ?, bool firstBulletOfAttack = ?, bool forceBlackBullet = ?);
  public string BankName; public string SpawnTransform; public float Direction; public float Speed; public Vector2 Velocity; public bool AutoRotation; public float TimeScale;
  public IBulletManager BulletManager; public GameObject Parent; public Projectile Projectile; public bool DontDestroyGameObject;
  public AIBulletBank BulletBank {get}; public Vector2 Position {get}; public int Tick {get};
  public virtual void Initialize();  protected/public virtual IEnumerator Top();
  public virtual void OnBulletDestruction(DestroyType destroyType, SpeculativeRigidbody hitRigidbody, bool preventSpawningProjectiles);   // DestroyType: DieInAir=0, HitRigidbody=1, HitTile=2
  public virtual void OnForceEnded(); public virtual void OnForceRemoved();
  public void Fire(Bullet bullet = null);
  public void Fire(Offset offset = null, Bullet bullet = null);
  public void Fire(Offset offset = null, Speed speed = null, Bullet bullet = null);
  public void Fire(Offset offset = null, Direction direction = null, Bullet bullet = null);
  public void Fire(Direction direction = null, Bullet bullet = null);
  public void Fire(Direction direction = null, Speed speed = null, Bullet bullet = null);
  public void Fire(Offset offset = null, Direction direction = null, Speed speed = null, Bullet bullet = null);
  public void ChangeSpeed(Speed speed, int term = ?); public void ChangeDirection(Direction direction, int term = ?); public void StartTask(IEnumerator enumerator);
  public int Wait(int frames); public int Wait(float frames);        // yield return Wait(n): n frames at 60 fps
  public void Vanish(bool suppressInAirEffects = ?);
  public float GetAimDirection(float leadAmount, float speed); public float GetAimDirection(string transform); public Vector2 GetPredictedTargetPosition(float leadAmount, float speed);
  public float RandomAngle(); public float SubdivideArc(float startAngle, float sweepAngle, int numBullets, int i, bool offset = ?); public float SubdivideCircle(float startAngle, int numBullets, int i, float direction = ?, bool offset = ?); public float SubdivideRange(float startValue, float endValue, int numDivisions, int i, bool offset = ?);
  public void PostWwiseEvent(string AudioEvent, string SwitchName = null);
}
public class Script : Bullet { }                 // your scripts derive from this and override IEnumerator Top()
public class Direction { public Direction(float direction = ?, DirectionType type = ?, float maxFrameDelta = ?); public DirectionType type; public float direction; public float maxFrameDelta; }
public class Speed     { public Speed(float speed = ?, SpeedType type = ?); public SpeedType type; public float speed; }
public class Offset    { public Offset(Vector2 offset, float rotation = ?, string transform = null, DirectionType directionType = ?); public Offset(string transform); public static Offset OverridePosition(Vector2 overridePosition); }
public enum DirectionType { Aim = 0, Absolute = 1, Relative = 2, Sequence = 3 }
public enum SpeedType     { Absolute = 0, Relative = 1, Sequence = 2 }
```
`AIBulletBank` (392797): `List<AIBulletBank.Entry> Bullets; bool useDefaultBulletIfMissing; List<Transform> transforms; Action<Projectile> OnProjectileCreated; Action<string, Projectile> OnProjectileCreatedWithSource; Entry GetBullet(string bulletName = null); GameObject CreateProjectileFromBank(Vector2 position, float direction, string bulletName, ...); Transform GetTransform(string transformName)`.
`AIBulletBank.Entry` (393424): `string Name; GameObject BulletObject; bool OverrideProjectile; ProjectileData ProjectileData; bool PlayAudio; string AudioSwitch, AudioEvent; bool AudioLimitOncePerFrame, AudioLimitOncePerAttack; VFXPool MuzzleFlashEffects; bool MuzzleLimitOncePerFrame, MuzzleInheritsTransformDirection; bool SpawnShells; Transform ShellTransform; GameObject ShellPrefab; float ShellForce, ShellForceVariance; bool DontRotateShell; …`.
`AIShooter` (393675): `ProjectileVolleyData volley; int equippedGunId; bool shouldUseGunReload; Transform gunAttachPoint, bulletScriptAttachPoint; PlayerHandController handObject; bool AllowTwoHands, ForceGunOnTop, IsReallyBigBoy, BackupAimInMoveDirection; Action<Projectile> PostProcessProjectile; …` — only needed if the boss physically holds a gun (`ShootGunBehavior`).

### 2.7 Animation / actor / database

```
AIAnimator : BraveBehaviour (391006)
  AIAnimator.FacingType facingType (Default/Target/Movement/SlaveDirection); AIAnimator.DirectionalType directionalType; bool faceSouthWhenStopped, faceTargetWhenStopped;
  DirectionalAnimation IdleAnimation, MoveAnimation, FlightAnimation, HitAnimation, TalkAnimation; float HitReactChance, MinTimeBetweenHitReacts;
  List<AIAnimator.NamedDirectionalAnimation> OtherAnimations; List<NamedVFXPool> OtherVFX; List<NamedScreenShake> OtherScreenShake; List<DirectionalAnimation> IdleFidgetAnimations
DirectionalAnimation (serializable, 421788)
  DirectionType Type; string Prefix; string[] AnimNames; FlipType[] Flipped;
  enum DirectionType { None=0, Single=1, TwoWayHorizontal=2, TwoWayVertical=3, FourWay=4, SixWay=5, EightWay=6, SixteenWay=7, SixteenWayTemp=8, FourWayCardinal=9, EightWayOrdinal=10 }
  enum FlipType { None=0, Flip=1, Unused=2, Mirror=3 }
  nested SingleAnimation { string suffix; float minAngle, maxAngle, artAngle; int? mirrorIndex }   // static table m_combined[DirectionType][] — NOT in the stub (see §3.3)
AIActor (386420) — useful public fields
  string EnemyGuid; int EnemyId; bool IsNormalEnemy, IsSignatureEnemy, IsHarmlessEnemy; float MovementSpeed; CellTypes PathableTiles;
  bool DiesOnCollison; float CollisionDamage, CollisionKnockbackStrength; VFXPool CollisionVFX; bool HitByEnemyBullets;
  bool CanDropCurrency, CanDropItems; GenericLootTable CustomLootTable; bool IgnoreForRoomClear; List<PickupObject> AdditionalSimpleItemDrops, AdditionalSafeItemDrops;
  GameObject CorpseObject; bool CorpseShadow; bool PreventDeathKnockback; bool invisibleUntilAwaken, procedurallyOutlined; AIActor.ReinforceType reinforceType (FullVfx/SkipVfx/Instant);
  bool PreventFallingInPitsEver; Texture2D optionalPalette; List<HealthOverride> HealthOverrides; bool CanTargetPlayers {get;set}; RoomHandler ParentRoom {get}
  static AIActor Spawn(AIActor prefabActor, IntVector2 position, RoomHandler source, bool correctForWalls = ?, AwakenAnimationType awakenAnimType = ?, bool autoEngage = ?);
  static AIActor Spawn(AIActor prefabActor, Vector2   position, RoomHandler source, bool correctForWalls = ?, AwakenAnimationType awakenAnimType = ?, bool autoEngage = ?);   // AwakenAnimationType: Default=0, Awaken=1, Spawn=2
  void SetIsFlying(bool value, string reason, bool adjustShadow = ?, bool modifyPathing = ?)
EnemyDatabaseEntry : AssetBundleDatabaseEntry (550717): PlaceableDifficulty difficulty; int placeableWidth, placeableHeight; bool isNormalEnemy; bool isInBossTab; string encounterGuid; int ForcedPositionInAmmonomicon  (+ inherited string myGuid, string path)
PixelCollider (see §3.4) — fields ColliderGenerationMode (Manual=0, BagelCollider=2, Circle=3, Line=4), CollisionLayer, IsTrigger, ManualOffsetX/Y, ManualWidth/Height, ManualDiameter, ManualLeftX/Y, ManualRightX/Y; void Regenerate(Transform transform, bool allowRotation = ?, bool allowScale = ?)
CollisionLayer: PlayerHitBox=0, PlayerCollider=1, EnemyHitBox=2, EnemyCollider=3, Projectile=4, LowObstacle=5, HighObstacle=6, ... BulletBlocker=8, EnemyBlocker=9, ...
```

---

## 3. Sprite / animation requirements

### 3.1 Which clips are mandatory

| Clip | Where the game looks | Mandatory? |
|------|----------------------|-----------|
| idle | `AIAnimator.IdleAnimation` (DirectionalAnimation) | **Yes** — BossBuilder leaves it null; a null idle NREs in `AIAnimator`. |
| move | `AIAnimator.MoveAnimation` | **Yes if the boss moves** (any `MovementBehaviors`); for a stationary boss point it at the idle clip. |
| hit | `AIAnimator.HitAnimation` + `HitReactChance` | No (set `HitReactChance = 0`). |
| die | Directional animation named `die` in `OtherAnimations` (default death lookup), or whatever `HealthHaver.overrideDeathAnimation` names | Strongly recommended — without one the boss just vanishes. F&G/Humphrey both register `"die"` via `AssignDirectionalAnimation("die", ..., AnimationType.Other)`. |
| attack tell / fire | `ShootBehavior.TellAnimation` / `FireAnimation` / `ChargeAnimation` / `PostFireAnimation` (directional names) | Optional per attack. |
| intro | `GenericIntroDoer.introAnim` (raw clip) or `introDirectionalAnim` (directional) | Optional; F&G uses `introAnim = "intro_right"` (raw clip name). |
| awaken | reinforcement spawns only (`AwakenAnimationType.Awaken`) | Not for a placed boss. |

Directional variants: vanilla bosses mostly use `TwoWayHorizontal` (right/left) — the simplest that still looks right. A `Single` directional animation is legal too.

### 3.2 How frames are found (naming rules) [SRC `EnemyAPI/EnemyBuilder.cs`, IL confirmed for `BuildAnimations`]

All art is **embedded PNGs**; manifest name = `RootNamespace.Folder.Sub.file.png` (this project: `PlutoTheCat.Resources.….png`, csproj already embeds `Resources\**\*.png`). `spriteDirectory` is written with `/` and converted with `Replace('/', '.')`.

* **Single-clip builders** (`EnemyBuilder.BuildAnimation`, and the 8-arg `AddAnimation` which delegates to `CompanionBuilder.BuildAnimation` [IL]): every resource whose name **`StartsWith(spriteDirectory.Replace('/', '.'))`** becomes a frame, in **sorted manifest-name order** (`EnemyBuilder.BuildAnimation` sorts; `CompanionBuilder.BuildAnimation` uses raw `GetManifestResourceNames()` order [IL] — prefer `EnemyBuilder.BuildAnimation`). Consequences: one folder per clip; **zero-pad frame numbers** (`vet_idle_001.png … vet_idle_012.png`); **no folder may be a prefix of another** (`…/fire` would swallow `…/fire_big`).
* **Multi-clip builder** (`AddAnimation(obj, enemyName, name, dir, fps, type, directionType, flipType, wrapMode)` → `BuildAnimations`), verbatim:

```csharp
string prefix = $"{spriteDirectory.Replace('/', '.')}.{enemyName}_{name.ToLower()}";
foreach (var a in DirectionalAnimation.m_combined[(int)directionType])
{
    List<int> indices = new List<int>();
    for (int i = 0; i < sortedList.Count; i++)
        if (sortedList[i].Contains($"{prefix}_{a.suffix}_0", false))          // case-insensitive
            indices.Add(SpriteBuilder.AddSpriteToCollection(sortedList[i], collection, assembly ?? Assembly.GetCallingAssembly()));
    if (indices.Count == 0) continue;
    tk2dSpriteAnimationClip clip = SpriteBuilder.AddAnimation(aiAnimator.spriteAnimator, collection, indices, $"{name.ToLower()}_{a.suffix}", wrapMode);
    clip.fps = fps;
    animList.Add(clip);
}
```
  i.e. files must be `<dir>/<enemyName>_<name>_<suffix>_0NN.png` (the literal `_0` means numbering must start with a 0: `_001`, `_01`, `_000`), and clips are named `<name>_<suffix>`. The directional animation it registers has `AnimNames = new string[m_combined[dir].Length + 1]` with only `name` appended — the per-suffix clip names are **not** written into `AnimNames`, so this overload is only convenient for `Single`; for two-way clips build the `DirectionalAnimation` yourself (§6 does).

* Sprite collection: `"<prefab name>_collection"` created on the prefab by `ConstructCollection` on first use; the `defaultSpritePath` frame given to `BuildPrefab` goes into the shared *item* collection instead (`SpriteFromTexture` → `itemCollection`) — harmless.
* The `assembly` parameter: pass `typeof(Plugin).Assembly` explicitly wherever a builder accepts one; the builders otherwise use `Assembly.GetCallingAssembly()`, which is fine when called straight from the mod but wrong through helper lambdas/inlining.

### 3.3 Direction suffix order (what is verified)

`DirectionalAnimation.m_combined` (the suffix/angle table) is a static initializer that the stubbed GameLibs does not contain (`grep "back_right" game.il` → 0 hits), so the exact order per `DirectionType` is **[DECOMP]**. What the examples establish:

* `TwoWayHorizontal` = `[right, left]` — Frost & Gunfire builds `AnimNames = { "die_right", "die_left" }, Flipped = { None, None }, Type = TwoWayHorizontal` by hand and the clips play correctly [MOD `Enemies/RoomMimic.cs`, `ExampleEnemies/Humphrey.cs`].
* `FourWay` clip names seen in the wild: `idle_back_right`, `idle_front_left`, `idle_front_right`, `idle_back_left` [MOD Humphrey]; `EightWayOrdinal` names: `..._north`, `_north_east`, `_east`, `_south_east`, `_south`, `_south_west`, `_west`, `_north_west` [MOD Humphrey comment]. Order not verified.
* The modding guide only shows the order as images (https://mtgmodders.gitbook.io/etg-modding-guide/misc/making-an-enemy — "these have to be in a VERY specific order").
* `Flipped[i] = FlipType.Flip` lets one right-facing clip serve both directions (AIAnimator mirrors the sprite) — this is how §6 avoids drawing left-facing art.

### 3.4 Size, pivot, hitbox

* 16 px = 1 world unit. Humanoid boss ~ 40–64 px tall is plenty (Bullet King ≈ 90 px). All frames of a clip should share canvas size so the pivot does not jump; tk2d anchors at the sprite's lower-left/center as built by `ConstructDefinition` (bottom-center pivot is what enemies expect — keep feet at the same y in every frame). [recommendation, not verified]
* `BuildPrefab(hitboxOffset, hitBoxSize)` are **pixels** relative to the sprite's lower-left and produce one `EnemyCollider` (walking/body collision). Add the hurtbox yourself, exactly as Frost & Gunfire does:

```csharp
actor.specRigidbody.PixelColliders.Add(new PixelCollider {
    ColliderGenerationMode = PixelCollider.PixelColliderGeneration.Manual,
    CollisionLayer = CollisionLayer.EnemyHitBox, IsTrigger = false,
    ManualOffsetX = 2, ManualOffsetY = 0, ManualWidth = 20, ManualHeight = 26 });
```
  (F&G RoomMimic clears `PixelColliders` and re-adds both `EnemyCollider` and `EnemyHitBox` with the same rect; Expand The Gungeon calls `collider.Regenerate(transform)` after moving offsets.)

### 3.5 Boss card art

`PortraitSlideSettings.bossArtSprite` is a `Texture` — load with `ResourceExtractor.GetTextureFromResource(ROOT + "/vet_bosscard.png", asm)` [F&G does exactly this]. The player-side card art already in this project (`Characters/Pluto/bosscard_001.png`) is **427×240 px**; draw the boss card at the same scale (the card slides the boss art in from the right, player art from the left). `bgColor` tints the background; text offsets can stay `IntVector2.Zero`.

---

## 4. Intro card, health bar, music, door lock, death — how they are wired

### 4.1 Reference implementation: Frost & Gunfire `EnemyAPI/BossBuilder.cs` → `SetupBasicIntro` [MOD, verbatim]

https://github.com/Neighborin0/FrostAndGunfire/blob/master/EnemyAPI/BossBuilder.cs

```csharp
public static void SetupBasicIntro(this AIActor enemy,string BossName, string SubTitle, string BossCard, Color BossCardColor, string IntroAnimation = null ,string Quote = "", string BossMusic = "Play_MUS_Boss_Theme_Beholster", bool IsInvisible = true)
{
    Texture2D BossCardTexture = ResourceExtractor.GetTextureFromResource(BossCard + ".png");
    FrostandGunFireItems.Strings.Enemies.Set("#" + BossName.ToUpper(), BossName);
    FrostandGunFireItems.Strings.Enemies.Set("#" + SubTitle.ToUpper(), SubTitle);
    FrostandGunFireItems.Strings.Enemies.Set("#" + Quote.ToUpper(), Quote);
    enemy.aiActor.healthHaver.overrideBossName = "#" + BossName.ToUpper();
    enemy.aiActor.OverrideDisplayName = "#" + BossName.ToUpper();
    enemy.aiActor.ActorName = "#" + BossName.ToUpper();
    enemy.aiActor.name = "#" + BossName.ToUpper();
    enemy.name = enemy.aiActor.OverrideDisplayName;
    try
    {
        GenericIntroDoer miniBossIntroDoer = enemy.gameObject.AddComponent<GenericIntroDoer>();
        miniBossIntroDoer.triggerType = GenericIntroDoer.TriggerType.PlayerEnteredRoom;
        miniBossIntroDoer.initialDelay = 0.15f;
        miniBossIntroDoer.cameraMoveSpeed = 14;
        miniBossIntroDoer.specifyIntroAiAnimator = null;
        miniBossIntroDoer.BossMusicEvent = BossMusic;
        miniBossIntroDoer.PreventBossMusic = false;
        miniBossIntroDoer.InvisibleBeforeIntroAnim = IsInvisible;
        miniBossIntroDoer.preIntroAnim = string.Empty;
        miniBossIntroDoer.preIntroDirectionalAnim = string.Empty;
        miniBossIntroDoer.introAnim = IntroAnimation;
        miniBossIntroDoer.introDirectionalAnim = string.Empty;
        miniBossIntroDoer.continueAnimDuringOutro = false;
        miniBossIntroDoer.cameraFocus = null;
        miniBossIntroDoer.roomPositionCameraFocus = Vector2.zero;
        miniBossIntroDoer.restrictPlayerMotionToRoom = false;
        miniBossIntroDoer.fusebombLock = false;
        miniBossIntroDoer.AdditionalHeightOffset = 0;
        miniBossIntroDoer.portraitSlideSettings = new PortraitSlideSettings()
        {
            bossNameString = "#" + BossName.ToUpper(),
            bossSubtitleString = "#" + SubTitle.ToUpper(),
            bossQuoteString = "#" + Quote.ToUpper(),
            bossSpritePxOffset = IntVector2.Zero,
            topLeftTextPxOffset = IntVector2.Zero,
            bottomRightTextPxOffset = IntVector2.Zero,
            bgColor = BossCardColor
        };
        if (BossCardTexture)
        {
            miniBossIntroDoer.portraitSlideSettings.bossArtSprite = BossCardTexture;
            miniBossIntroDoer.SkipBossCard = false;
            enemy.aiActor.healthHaver.bossHealthBar = HealthHaver.BossBarType.MainBar;
        }
        else
        {
            miniBossIntroDoer.SkipBossCard = true;
            enemy.aiActor.healthHaver.bossHealthBar = HealthHaver.BossBarType.SubbossBar;
        }
        miniBossIntroDoer.SkipFinalizeAnimation = true;
        miniBossIntroDoer.RegenerateCache();
    }
    catch(Exception e) { Tools.PrintNoID(e); }
}
```
Strings: F&G routes texts through MtG's string table (`ETGMod.Databases.Strings.Enemies.Set("#KEY", "Text")` — `ETGMod/Databases::Strings` is a `StringDB` in ModTheGungeonAPI.dll [IL]); Expand The Gungeon writes plain strings (`portraitSlideSettings.bossNameString = "Western Bros"`, `healthHaver.overrideBossName = "Western Bros"`) [MOD `ExpandPrefab/ExpandWesternBrosPrefabBuilder.cs`]. Use plain strings first; fall back to `#KEY` + string table if the UI prints the raw key.

### 4.2 Who triggers what [DECOMP unless noted]

| Effect | Trigger |
|--------|---------|
| Door lock / unlock | Room events `ON_ENTER_WITH_ENEMIES → SEAL_ROOM` and `ON_ENEMIES_CLEARED → UNSEAL_ROOM`, which `RoomFactory.AddEnemyToRoom` adds to every room that gets an enemy [SRC, §5.2]. The room seals on entry regardless of `category`. |
| Intro sequence | `GenericIntroDoer` implements `IPlaceConfigurable.ConfigureOnPlacement(RoomHandler)` [IL]; the room calls it when the placed boss is instantiated, the doer subscribes to the room's `Entered` event (`triggerType = PlayerEnteredRoom`) and runs `TriggerSequence` → walk-in, camera pan (`cameraMoveSpeed`), `introAnim`, boss card (`WaitForBossCard`, unless `SkipBossCard`), boss music (`BossMusicEvent` unless `PreventBossMusic`), then `EndSequence` re-enables the actor. The actor is frozen until then. |
| Health bar | `HealthHaver.bossHealthBar == MainBar` — the game registers the haver with `GameUIRoot.Instance.bossController` (`RegisterBossHealthHaver(hh, overrideBossName)`) as part of the boss intro; `SubbossBar` gives the small mini-boss bar without card. Nothing to call manually. |
| Kill cam + boss death rules (DPS cap, `BossHealthSanityCheck`, `EndBossState(true)` → `BossKillCam.TriggerSequence`) | `HealthHaver.IsBoss` (derived from `bossHealthBar`). Automatic. |
| Boss reward pedestal/chest | `RoomHandler.HandleBossClearReward()` for rooms whose `area.PrototypeRoomCategory == BOSS` (`OverrideBossRewardTable`, `OverrideBossPedestalLocation`). Automatic in a normal floor; irrelevant in a past. |
| Ammonomicon page / kill notification | Needs an `EncounterTrackable` + `EncounterDatabaseEntry` (F&G `SetupEntry`/`AddEnemyToDatabase`). Optional. |

### 4.3 Death sequence

1. `HealthHaver` hits 0 → `OnPreDeath(Vector2)` → death clip (`overrideDeathAnimation` or directional `die`) → `OnDeath(Vector2)`; `OnDeathBehavior` components fire at `PreDeath`, `Death`, or on an animation event named `triggerName` (`DeathAnimTrigger`) [IL enum].
2. `ExplodeOnDeath` gives the explosion (`explosionData`, `immuneToIBombApp`; chain explosions via `LinearChainExplosion…`). `SpawnEnemyOnDeath` if the Vet should release "patients".
3. `HealthHaver.OnPreDeath/OnDeath` are plain C# events on the *instance*: subscribe from a component's `Start()` (Expand The Gungeon `ExpandWesternBroDeathController : BraveBehaviour { void Start() { healthHaver.OnPreDeath += OnDeath; } }` [MOD]). Subscribing on the prefab does nothing for spawned copies.
4. Kill cam runs by itself for `IsBoss` actors; `BossKillCam.KillAllEnemies()` clears adds.

---

## 5. Placing the boss in a room

### 5.1 `RoomFactory` API and the `.room` format [IL 0.5.10 + SRC `DungeonAPI/RoomFactory.cs`]

```csharp
public static Dictionary<string, RoomFactory.RoomData> LoadRoomsFromRoomDirectory(string modPrefix, string roomDirectory); // *.room files on disk, each Register()ed
public static RoomFactory.RoomData BuildFromResource(string roomPath, Assembly assembly = null);      // legacy: PNG (cell colours) + "***DATA***" + JSON tail; calls DungeonHandler.Register
public static RoomFactory.RoomData BuildNewRoomFromResource(string roomPath, Assembly assembly = null); // RAT ".newroom": pure JSON with tileInfo; does NOT register
public static PrototypeDungeonRoom Build(RoomFactory.RoomData roomData);
public static void ApplyRoomData(PrototypeDungeonRoom room, RoomFactory.RoomData roomData);          // exits, enemies, placeables, nodes
public static PrototypeDungeonRoom CreateEmptyRoom(int width = 12, int height = 12);
public static PrototypeDungeonRoom GetNewPrototypeDungeonRoom(int width = 12, int height = 12);
public static void AddExit(PrototypeDungeonRoom room, Vector2 location, DungeonData.Direction direction, PrototypeRoomExit.ExitType exitType = NO_RESTRICTION);
public static void AddEnemyToRoom(PrototypeDungeonRoom room, Vector2 location, string guid, string attributes, int layer, bool shuffle, RoomEventTriggerCondition reinforcementType);
public static void AddPlaceableToRoom(PrototypeDungeonRoom room, Vector2 location, string assetPath, string attributes, Dictionary<int, PrototypeEventTriggerArea> prototypeEventTriggerAreas);
public static void AddInjection(PrototypeDungeonRoom protoroom, string injectionAnnotation, List<ProceduralFlowModifierData.FlowModifierPlacementType> placementRules, float chanceToLock, List<DungeonPrerequisite> prerequisites, string injectorName, float selectionWeight = 1, float chanceToSpawn = 1, GameObject addSingularPlaceable = null, float XFromCenter = 0, float YFromCenter = 0);
public static void DungeonHandler.Register(RoomFactory.RoomData roomData);
```

`RoomFactory.RoomData` fields [IL]: `string tileInfo; Vector2Int roomSize; string[] waveTriggers, nodeTypes, nodeWrapModes; Vector2[] nodePositions; int[] nodePaths, nodeOrder; string category; string normalSubCategory, specialSubCategory, bossSubCategory; Vector2[] enemyPositions; string[] enemyGUIDs; string[] enemyAttributes; Vector2[] placeablePositions; string[] placeableGUIDs, placeableAttributes; int[] enemyReinforcementLayers; Vector2[] exitPositions; string[] exitDirections; string[] floors; float weight; bool isSpecialRoom, randomizeEnemyPositions, doFloorDecoration, doWallDecoration, doLighting, darkRoom; int visualSubtype; string superSpecialRoomType; float AmbientLight_R/G/B; bool usesAmbientLight; string specialRoomPool; float[] additionalPauseDelay; [NonSerialized] string name; PrototypeDungeonRoom room`.

`category`/`bossSubCategory` are parsed with `ShrineTools.GetEnumValue<PrototypeDungeonRoom.RoomCategory>(roomData.category)`: `RoomCategory { CONNECTOR, HUB, NORMAL, BOSS, REWARD, SPECIAL, SECRET, ENTRANCE, EXIT }`, `RoomBossSubCategory { FLOOR_BOSS, MINI_BOSS }` [IL enums]. Put the boss GUID in `enemyGUIDs` (layer 0) — the Room Architect Tool (Thunderstore `Alexandria/RoomArchitectTool`) writes all of this for you; the enemy id you type there is our `GUID` string.

### 5.2 `AddEnemyToRoom` — where the door lock comes from [SRC verbatim]

```csharp
private static RoomEventDefinition sealOnEnterWithEnemies = new RoomEventDefinition(RoomEventTriggerCondition.ON_ENTER_WITH_ENEMIES, RoomEventTriggerAction.SEAL_ROOM);
private static RoomEventDefinition unsealOnRoomClear     = new RoomEventDefinition(RoomEventTriggerCondition.ON_ENEMIES_CLEARED, RoomEventTriggerAction.UNSEAL_ROOM);

public static void AddEnemyToRoom(PrototypeDungeonRoom room, Vector2 location, string guid, string attributes, int layer, bool shuffle, RoomEventTriggerCondition reinforcementType)
{
    ... DungeonPlaceable dungeonPlaceable = ScriptableObject.CreateInstance<DungeonPlaceable>();
    dungeonPlaceable.variantTiers = new List<DungeonPlaceableVariant> { new DungeonPlaceableVariant { percentChance = 1f, prerequisites = array, forceBlackPhantom = forceBlackPhantom, enemyPlaceableGuid = guid, materialRequirements = new DungeonPlaceableRoomMaterialRequirement[0] } };
    PrototypePlacedObjectData prototypePlacedObjectData = new PrototypePlacedObjectData { contentsBasePosition = location, fieldData = new List<PrototypePlacedObjectFieldData>(), instancePrerequisites = array, linkedTriggerAreaIDs = new List<int>(), placeableContents = dungeonPlaceable };
    if (layer > 0) RoomFactory.AddObjectDataToReinforcementLayer(room, prototypePlacedObjectData, layer - 1, location, shuffle, reinforcementType);
    else { room.placedObjects.Add(prototypePlacedObjectData); room.placedObjectPositions.Add(location); }
    if (!room.roomEvents.Contains(RoomFactory.sealOnEnterWithEnemies)) room.roomEvents.Add(RoomFactory.sealOnEnterWithEnemies);
    if (!room.roomEvents.Contains(RoomFactory.unsealOnRoomClear))     room.roomEvents.Add(RoomFactory.unsealOnRoomClear);
}
```
(`attributes` is JSON; `{"j":true}` forces a jammed spawn.) The enemy is resolved at generation through `EnemyDatabase.GetOrLoadByGuid(enemyPlaceableGuid)` — which is exactly what Alexandria's Harmony prefix intercepts for our GUID [IL `BossBuilder.EnemyDatabaseGetOrLoadByGuidPatch`].

### 5.3 Getting the room into a floor: `DungeonHandler.Register` [SRC]

* `roomData.specialRoomPool` set → the room goes straight into `StaticReferences.RoomTables[specialRoomPool]`; if `category == BOSS` it also gets `associatedMinimapIcon = RoomIcons.BossRoomIcon`.
* `category == BOSS` + `subCategoryBoss == FLOOR_BOSS` + `floors` → the room is added to that floor's vanilla boss pools (tables keyed `"gull"`, `"triggertwins"`, `"bulletking"`, `"blobby"`, `"gorgun"`, `"beholster"`, `"ammoconda"`, `"oldking"`, `"tank"`, `"cannonballrog"`, `"flayer"`, `"priest"`, `"pillars"`, `"monger"`, `"doorlord"` → `bosstable_01_gatlinggull` … [SRC `StaticReferences.cs`]; 0.5.10 exposes `StaticReferences.BossRoomTableMap` / `MiniBossRoomTableMap` [IL]). Being in a vanilla boss pool means the floor's boss door, boss foyer, reward pedestal and exit all wrap around our room — the easiest way to **test** the fight in a normal run: `StaticReferences.RoomTables["bulletking"].includedRooms.Add(new WeightedRoom { room = room, weight = 5f, additionalPrerequisites = new DungeonPrerequisite[0] })`.
* Programmatic alternative: build with `CreateEmptyRoom`/`AddExit`/`AddEnemyToRoom`, set `room.category = BOSS`, `room.subCategoryBoss = FLOOR_BOSS`, `room.associatedMinimapIcon = RoomIcons.BossRoomIcon`, and push into a table yourself.

The intro/health bar/kill cam do **not** depend on the room category — they hang off the boss prefab's components. The category matters for flow placement, boss doors and the reward pedestal.

### 5.4 The custom past: what happens on death

How Alexandria enters a custom past [IL `Alexandria.CharacterAPI.Hooks/CustomPastHandlerPatches::DoCustomPastChecks(ArkController ark, PlayerController shotPlayer)`]: it reads `shotPlayer.GetComponent<CustomCharacter>().past` (set from `Loader.BuildCharacter(..., hasCustomPast: true, customPast: "<name>")`), calls `ark.ResetPlayers(bool)` and then **`GameManager.Instance.LoadCustomLevel(cc.past)`**. So `customPast` must be the `dungeonSceneName` of a `GameLevelDefinition` the game can find (`GameManager.dungeonFloors` / `GameManager.customFloors` [IL fields]) — i.e. a whole custom floor whose flow contains our BOSS room (Alexandria `DungeonAPI.DungeonHandler.CreateSpecialFlowFlow`, `OfficialFlows`, `SampleFlow` are the helpers; separate research). While inside it, `GameManager.Instance.CurrentLevelOverrideState == GameManager.LevelOverrideState.CHARACTER_PAST` (enum `NONE, FOYER, TUTORIAL, RESOURCEFUL_RAT, END_TIMES, CHARACTER_PAST, DEBUG_TEST` [IL]).

**Nothing fires automatically when a boss dies in a past.** Each vanilla past has its own controller that watches its boss: `ConvictPastController.OnBossKilled(Transform)`, `GuidePastController.OnBossKilled()`, `PastLabMarineController.OnBossKilled()`, `PilotPastController.OnBossKilled()` / `EndPastSuccess()`, `RobotPastController.OnBossKilled(Transform)` / `OnBossKilled_CR` [IL method list]. The generic ending machinery they use: `GameStatsManager.Instance.SetCharacterSpecificFlag(CharacterSpecificGungeonFlags.KILLED_PAST, true)` (flag values `KILLED_PAST = 1000`, `KILLED_PAST_ALTERNATE_COSTUME = 1001`, `CLEARED_BULLET_HELL = 1100` [IL]; `ArkController.CharacterStoryComplete(PlayableCharacters)` reads it) and the credits tube `TimeTubeCreditsController.HandleTimeTubeCredits(Vector2 decayCenter, bool skipCredits, tk2dSpriteAnimator optionalAnimatorToDisable, int shotPlayerID, bool quickEndShatter = false)` (+ `static AcquireTunnelInstanceInAdvance()`, `AcquirePastDioramaInAdvance()`, `static bool IsTimeTubing`) [IL]. For our mod the minimum is: hook `OnPreDeath` on the boss instance, set the flag, wait for the death/kill-cam, then leave the level (`GameManager.Instance.ReturnToFoyer()` or `LoadCustomLevel(...)` [IL]). Running the real credits tube needs the prefab/instance wiring that only a decompile shows (§7).

Practical v2 note (from `docs/v2-roadmap.md`): reusing the Pilot past with custom text stays the cheap path; the boss can still be tested on floor 1 via §5.3.

### 5.5 Debug spawning

```csharp
Gungeon.Game.Enemies.Add("pluto:the_vet", actor);   // MtG API IDPool<AIActor>: console `spawn pluto:the_vet` [MOD F&G, IL ModTheGungeonAPI.dll]
AIActor.Spawn(Prefab.GetComponent<AIActor>(), player.CenterPosition + new Vector2(4f, 0f), player.CurrentRoom, true, AIActor.AwakenAnimationType.Default, true);
```
Spawning this way skips the intro (no `ConfigureOnPlacement`), but exercises animations, hitboxes, attacks and the health bar.

---

## 6. End-to-end code sketch (C#, net35, Alexandria 0.5.10)

Files: `PlutoTheCat/src/TheVetBoss.cs` (below), art under `PlutoTheCat/Resources/Bosses/vet/{idle,move,tell,fire,intro,die}/vet_<clip>_001.png…` plus `vet_bosscard.png` (427×240). Register from `Plugin.GMStart` **before** the character: `Step("the vet", TheVetBoss.Init);`.

```csharp
using System;
using System.Collections;
using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using Alexandria.EnemyAPI;
using Alexandria.ItemAPI;
using Alexandria.DungeonAPI;
using Brave.BulletScript;
using Dungeonator;
using DirType = DirectionalAnimation.DirectionType;
using FlipType = DirectionalAnimation.FlipType;

namespace PlutoTheCat
{
    /// <summary>The Vet: syringe-gun boss for Pluto's past. Built with Alexandria 0.5.10 BossBuilder.</summary>
    public static class TheVetBoss
    {
        public const string GUID = "bogdan.pluto.thevet";                 // unique string; also the room-editor enemy id
        public const string ROOT = "PlutoTheCat/Resources/Bosses/vet";     // embedded PNG root (RootNamespace/…)
        private const string BULLET_KIN = "01972dee89fc4404a5c408d50007dad5";
        public static GameObject Prefab;

        public static void Init()
        {
            if (Prefab != null || BossBuilder.Dictionary.ContainsKey(GUID)) return;
            Assembly asm = typeof(Plugin).Assembly;

            // 1) Prefab. HasAiShooter:false => we get an (empty) AIBulletBank. Hitbox args are pixels (16 px = 1 unit) -> ONE EnemyCollider.
            Prefab = BossBuilder.BuildPrefab("The Vet", GUID, ROOT + "/idle/vet_idle_001",
                                             new IntVector2(2, 0), new IntVector2(20, 26), false);
            AIActor actor = Prefab.GetComponent<AIActor>();
            HealthHaver hh = actor.healthHaver;
            AIAnimator anim = actor.aiAnimator;
            BehaviorSpeculator bs = Prefab.GetComponent<BehaviorSpeculator>();

            // 2) Stats (BuildPrefab left 15000 HP, knockback weight 1, HasShadow = false).
            hh.ForceSetCurrentHealth(900f);
            hh.SetHealthMaximum(900f);
            hh.overrideBossName = "The Vet";
            hh.bossHealthBar = HealthHaver.BossBarType.MainBar;   // boss bar + IsBoss rules (kill cam, boss DPS cap)
            actor.MovementSpeed = 3f;
            actor.CollisionDamage = 1f;
            actor.CollisionKnockbackStrength = 5f;
            actor.knockbackDoer.weight = 200f;
            actor.IgnoreForRoomClear = false;
            actor.PreventFallingInPitsEver = true;
            actor.CanDropCurrency = false;
            actor.procedurallyOutlined = true;
            actor.specRigidbody.CollideWithOthers = true;
            actor.specRigidbody.CollideWithTileMap = true;

            // 3) Hurtbox: player projectiles collide with EnemyHitBox, which SetUpSpeculativeRigidbody did not create.
            actor.specRigidbody.PixelColliders.Add(new PixelCollider
            {
                ColliderGenerationMode = PixelCollider.PixelColliderGeneration.Manual,
                CollisionLayer = CollisionLayer.EnemyHitBox,
                IsTrigger = false,
                ManualOffsetX = 2, ManualOffsetY = 0, ManualWidth = 20, ManualHeight = 26,
            });

            // 4) Clips: one folder per clip, every PNG in it in sorted name order (zero-pad!). Right-facing art only.
            EnemyBuilder.BuildAnimation(anim, "vet_idle",  ROOT + "/idle",  6, asm).wrapMode = tk2dSpriteAnimationClip.WrapMode.Loop;
            EnemyBuilder.BuildAnimation(anim, "vet_move",  ROOT + "/move",  8, asm).wrapMode = tk2dSpriteAnimationClip.WrapMode.Loop;
            EnemyBuilder.BuildAnimation(anim, "vet_tell",  ROOT + "/tell",  8, asm);
            EnemyBuilder.BuildAnimation(anim, "vet_fire",  ROOT + "/fire", 12, asm);
            EnemyBuilder.BuildAnimation(anim, "vet_intro", ROOT + "/intro", 8, asm);
            EnemyBuilder.BuildAnimation(anim, "vet_die",   ROOT + "/die",   8, asm);
            // Directional wrappers (order right, left; left = mirrored right).
            anim.IdleAnimation = TwoWay("vet_idle");
            anim.MoveAnimation = TwoWay("vet_move");
            anim.HitReactChance = 0f;
            EnemyBuildingTools.AddNewDirectionAnimation(anim, "tell",  new[] { "vet_tell",  "vet_tell"  }, new[] { FlipType.None, FlipType.Flip }, DirType.TwoWayHorizontal);
            EnemyBuildingTools.AddNewDirectionAnimation(anim, "fire",  new[] { "vet_fire",  "vet_fire"  }, new[] { FlipType.None, FlipType.Flip }, DirType.TwoWayHorizontal);
            EnemyBuildingTools.AddNewDirectionAnimation(anim, "intro", new[] { "vet_intro", "vet_intro" }, new[] { FlipType.None, FlipType.Flip }, DirType.TwoWayHorizontal);
            EnemyBuildingTools.AddNewDirectionAnimation(anim, "die",   new[] { "vet_die",   "vet_die"   }, new[] { FlipType.None, FlipType.Flip }, DirType.TwoWayHorizontal);
            hh.overrideDeathAnimation = "die";

            // 5) Bullet bank: the Bullet Kin's "default" projectile under our own name (keeps its sound: "DNC").
            AIBulletBank bank = Prefab.GetComponent<AIBulletBank>();
            AIBulletBank.Entry kin = EnemyDatabase.GetOrLoadByGuid(BULLET_KIN).bulletBank.GetBullet("default");
            bank.Bullets.Add(EnemyBuildingTools.CopyBulletBankEntry(kin, "syringe", "DNC"));

            // 6) Behaviours. Replace bs.AttackBehaviors: the Fungun template's own attacks are still in it.
            GameObject shootPoint = EnemyBuildingTools.GenerateShootPoint(Prefab, actor.sprite.WorldCenter + new Vector2(0.5f, 0.6f), "syringe_tip");
            bs.TargetBehaviors = new List<TargetBehaviorBase>
            {
                new TargetPlayerBehavior { Radius = 35f, LineOfSight = false, ObjectPermanence = true, SearchInterval = 0.25f, PauseOnTargetSwitch = false, PauseTime = 0.25f }
            };
            bs.MovementBehaviors = new List<MovementBehaviorBase>
            {
                new MoveErraticallyBehavior { PathInterval = 0.3f, PointReachedPauseTime = 0.35f, PreventFiringWhileMoving = false, InitialDelay = 0.5f, StayOnScreen = true, AvoidTarget = false, UseTargetsRoom = true }
            };
            bs.AttackBehaviors = new List<AttackBehaviorBase>
            {
                new AttackBehaviorGroup
                {
                    ShareCooldowns = false,
                    AttackBehaviors = new List<AttackBehaviorGroup.AttackGroupItem>
                    {
                        new AttackBehaviorGroup.AttackGroupItem { NickName = "aimed burst",   Probability = 1f, Behavior = Shoot(typeof(VetAimedBurstScript),   shootPoint, 1.6f, 1.0f) },
                        new AttackBehaviorGroup.AttackGroupItem { NickName = "spread",        Probability = 1f, Behavior = Shoot(typeof(VetSpreadScript),       shootPoint, 2.0f, 1.0f) },
                        // Phase 2: only usable below 50 % HP (MaxHealthThreshold) and twice as likely.
                        new AttackBehaviorGroup.AttackGroupItem { NickName = "double spread", Probability = 2f, Behavior = Shoot(typeof(VetDoubleSpreadScript), shootPoint, 1.2f, 0.5f) },
                    }
                }
            };
            bs.InstantFirstTick = false; bs.TickInterval = 0.1f; bs.PostAwakenDelay = 0.5f; bs.RemoveDelayOnReinforce = false;
            bs.OverrideStartingFacingDirection = false; bs.StartingFacingDirection = -90f; bs.SkipTimingDifferentiator = false;

            // 7) Intro card + music. GenericIntroDoer.ConfigureOnPlacement is called by the room that places the boss.
            GenericIntroDoer intro = Prefab.AddComponent<GenericIntroDoer>();
            intro.triggerType = GenericIntroDoer.TriggerType.PlayerEnteredRoom;
            intro.initialDelay = 0.15f;
            intro.cameraMoveSpeed = 14f;
            intro.specifyIntroAiAnimator = null;
            intro.BossMusicEvent = "Play_MUS_Boss_Theme_Beholster";
            intro.PreventBossMusic = false;
            intro.InvisibleBeforeIntroAnim = false;
            intro.preIntroAnim = string.Empty; intro.preIntroDirectionalAnim = string.Empty;
            intro.introAnim = "vet_intro";                 // raw clip (F&G style); or introDirectionalAnim = "intro"
            intro.introDirectionalAnim = string.Empty;
            intro.continueAnimDuringOutro = false;
            intro.cameraFocus = null; intro.roomPositionCameraFocus = Vector2.zero;
            intro.restrictPlayerMotionToRoom = false; intro.fusebombLock = false; intro.AdditionalHeightOffset = 0f;
            intro.HideGunAndHand = true;
            intro.SkipBossCard = false;
            intro.portraitSlideSettings = new PortraitSlideSettings
            {
                bossNameString = "The Vet",
                bossSubtitleString = "Time For Your Shots",
                bossQuoteString = string.Empty,
                bossArtSprite = ResourceExtractor.GetTextureFromResource(ROOT + "/vet_bosscard.png", asm),
                bossSpritePxOffset = IntVector2.Zero, topLeftTextPxOffset = IntVector2.Zero, bottomRightTextPxOffset = IntVector2.Zero,
                bgColor = new Color(0.12f, 0.45f, 0.55f),
            };
            intro.SkipFinalizeAnimation = true;

            // 8) Death: harmless explosion (borrow the RPG's effect) + instance-side hook for the past ending.
            ExplosionData src = ((Gun)PickupObjectDatabase.GetById(19)).DefaultModule.projectiles[0].GetComponent<ExplosiveModifier>().explosionData;
            ExplodeOnDeath boom = Prefab.AddComponent<ExplodeOnDeath>();
            boom.deathType = OnDeathBehavior.DeathType.Death;
            boom.immuneToIBombApp = true;
            boom.explosionData = new ExplosionData
            {
                useDefaultExplosion = false, doDamage = false, damage = 0f, damageToPlayer = 0f, damageRadius = 3f,
                doForce = true, pushRadius = 4f, force = 40f, debrisForce = 20f, preventPlayerForce = false,
                doDestroyProjectiles = true, breakSecretWalls = false, explosionDelay = 0f,
                effect = src.effect, doScreenShake = true, ss = src.ss, doStickyFriction = true, doExplosionRing = true,
                playDefaultSFX = true, isFreezeExplosion = false,
            };
            Prefab.AddComponent<VetDeathHandler>();

            Gungeon.Game.Enemies.Add("pluto:the_vet", actor);   // console: spawn pluto:the_vet
        }

        private static DirectionalAnimation TwoWay(string clip)
        {
            return new DirectionalAnimation { Type = DirType.TwoWayHorizontal, Prefix = clip,
                                              AnimNames = new[] { clip, clip }, Flipped = new[] { FlipType.None, FlipType.Flip } };
        }

        private static ShootBehavior Shoot(Type script, GameObject shootPoint, float cooldown, float maxHealthFraction)
        {
            return new ShootBehavior
            {
                ShootPoint = shootPoint,
                BulletScript = new CustomBulletScriptSelector(script),
                LeadAmount = 0f,
                StopDuring = ShootBehavior.StopType.Attack,
                ImmobileDuringStop = true,
                LockFacingDirection = false, ContinueAimingDuringTell = true, ReaimOnFire = false,
                RequiresTarget = true, PreventTargetSwitching = true, Uninterruptible = false,
                TellAnimation = "tell", FireAnimation = "fire",
                HideGun = false, UseVfx = false,
                // BasicAttackBehavior
                Cooldown = cooldown, CooldownVariance = 0.25f, AttackCooldown = 0.4f, GlobalCooldown = 0f,
                InitialCooldown = 1f, InitialCooldownVariance = 0f, GroupName = null, GroupCooldown = 0f,
                MinRange = 0f, Range = 40f, MinWallDistance = 0f, MaxEnemiesInRoom = 0f,
                MinHealthThreshold = 0f, MaxHealthThreshold = maxHealthFraction, HealthThresholds = new float[0], AccumulateHealthThresholds = true,
                targetAreaStyle = null, IsBlackPhantom = false, resetCooldownOnDamage = null, RequiresLineOfSight = false, MaxUsages = 0,
            };
        }
    }

    /// <summary>Lives on the spawned boss. Events are per instance, so subscribe in Start().</summary>
    public class VetDeathHandler : BraveBehaviour
    {
        private void Start() { healthHaver.OnPreDeath += OnPreDeath; }

        private void OnPreDeath(Vector2 dir)
        {
            healthHaver.OnPreDeath -= OnPreDeath;
            if (GameManager.Instance.CurrentLevelOverrideState != GameManager.LevelOverrideState.CHARACTER_PAST) return;
            GameStatsManager.Instance.SetCharacterSpecificFlag(CharacterSpecificGungeonFlags.KILLED_PAST, true);
            GameManager.Instance.StartCoroutine(EndPast());
        }

        private static IEnumerator EndPast()
        {
            float t = 0f;                                  // let the death clip / kill cam play out
            while (t < 5f) { t += BraveTime.DeltaTime; yield return null; }
            // TODO: real credits tube = TimeTubeCreditsController.HandleTimeTubeCredits(...) once its prefab lookup is confirmed (see caveats).
            GameManager.Instance.ReturnToFoyer();
        }
    }

    // ---- Bullet scripts. Wait(n) = n frames at 60 fps. Fire(direction, speed, bullet). ----
    public class SyringeBullet : Bullet
    {
        public SyringeBullet() : base("syringe", false, false, false) { }   // (bankName, suppressVfx, firstBulletOfAttack, forceBlackBullet)
    }

    /// Attack 1: three shots straight at the player, 8 frames apart.
    public class VetAimedBurstScript : Script
    {
        protected override IEnumerator Top()
        {
            for (int i = 0; i < 3; i++)
            {
                Fire(new Direction(0f, Brave.BulletScript.DirectionType.Aim), new Speed(9f, SpeedType.Absolute), new SyringeBullet());
                yield return Wait(8);
            }
        }
    }

    /// Attack 2: 9-bullet fan over 80 degrees centred on the player.
    public class VetSpreadScript : Script
    {
        protected override IEnumerator Top()
        {
            float aim = GetAimDirection(0f, 7f);
            const int n = 9;
            for (int i = 0; i < n; i++)
                Fire(new Direction(SubdivideArc(aim - 40f, 80f, n, i), Brave.BulletScript.DirectionType.Absolute), new Speed(7f, SpeedType.Absolute), new SyringeBullet());
            yield return Wait(20);
        }
    }

    /// Phase 2: two fans, the second offset by half a step.
    public class VetDoubleSpreadScript : Script
    {
        protected override IEnumerator Top()
        {
            const int n = 9;
            for (int wave = 0; wave < 2; wave++)
            {
                float aim = GetAimDirection(0f, 7f);
                for (int i = 0; i < n; i++)
                    Fire(new Direction(SubdivideArc(aim - 40f, 80f, n, i, wave == 1), Brave.BulletScript.DirectionType.Absolute), new Speed(7f, SpeedType.Absolute), new SyringeBullet());
                yield return Wait(25);
            }
        }
    }

    // ---- Room ----
    public static class VetRoom
    {
        /// Option A: Room Architect Tool export (.newroom JSON) embedded under Resources/Rooms/, boss placed in the tool by GUID,
        /// category BOSS / bossSubCategory FLOOR_BOSS / floors ["Gungeon"] or specialRoomPool.
        public static void InitFromResource()
        {
            RoomFactory.RoomData data = RoomFactory.BuildNewRoomFromResource("PlutoTheCat/Resources/Rooms/vet_clinic.newroom", typeof(Plugin).Assembly);
            DungeonHandler.Register(data);
        }

        /// Option B: entirely in code, dropped into the floor-1 Bullet King boss pool for testing.
        public static PrototypeDungeonRoom InitInCode()
        {
            PrototypeDungeonRoom room = RoomFactory.CreateEmptyRoom(24, 18);
            room.name = "vet_clinic";
            RoomFactory.AddExit(room, new Vector2(12, 0), DungeonData.Direction.SOUTH);
            RoomFactory.AddEnemyToRoom(room, new Vector2(12, 11), TheVetBoss.GUID, "", 0, false, RoomEventTriggerCondition.ON_ENTER_WITH_ENEMIES);
            room.category = PrototypeDungeonRoom.RoomCategory.BOSS;
            room.subCategoryBoss = PrototypeDungeonRoom.RoomBossSubCategory.FLOOR_BOSS;
            room.associatedMinimapIcon = RoomIcons.BossRoomIcon;
            StaticReferences.RoomTables["bulletking"].includedRooms.Add(new WeightedRoom { room = room, weight = 5f, additionalPrerequisites = new DungeonPrerequisite[0] });
            return room;
        }
    }
}
```

Points where the sketch deliberately deviates from the samples: it never calls `BossBuilder.Init()`; it uses `EnemyBuilder.BuildAnimation` + hand-built `DirectionalAnimation`s instead of the 0.5.10 `AddAnimation` overloads (whose `Other`/multi-direction bookkeeping is awkward, §3.2); it replaces `bs.AttackBehaviors` wholesale (§1.3.2); and it hooks death on the instance.

---

## 7. Not verified / caveats

1. **GameLibs is a stub.** Every "who calls what" statement about the game (`ConfigureOnPlacement` subscribing to `RoomHandler.Entered`, health-bar registration during the intro, `HealthHaver.IsBoss` ⇒ kill cam, `bs.AttackBehaviorGroup` being a lookup into `AttackBehaviors`, `overrideDeathAnimation` resolving directional names) is [DECOMP] knowledge, consistent with the field/method surface in the IL and with what F&G / Expand The Gungeon rely on, but not provable from `packages/`. Confirm with dnSpy on the real `Assembly-CSharp.dll` or by testing.
2. **`DirectionalAnimation.m_combined` suffix order** (§3.3) is not in the stub; only `TwoWayHorizontal = [right, left]` is example-proven. Anything beyond two directions needs a dnSpy check of `DirectionalAnimation`'s static constructor.
3. **`BossBuilder.BuildPrefab` quirks** (§1.3.2) are real in 0.5.10 (IL): `HasAiShooter=true` skips the bullet bank and only rebuilds the static template; the Fungun's `AttackBehaviors` survive; HP is 15000; only an `EnemyCollider` is created. The `UsesAttackGroup` parameter is unused.
4. **`Alexandria.EnemyAPI.EnemyBuilder.AddAnimation` (multi-clip overload)** allocates `AnimNames` of size `m_combined.Length + 1` and appends only `name`, so its directional animation does not list the per-suffix clips it created — treat it as `Single`-only or build `DirectionalAnimation`s yourself.
5. **Past ending**: `LoadCustomLevel(customPast)` is verified [IL of Alexandria]; that the string must match a `GameLevelDefinition.dungeonSceneName` in `GameManager.customFloors`, and the exact `TimeTubeCreditsController` instantiation (prefab path / `HandleTimeTubeCredits` arguments) are not. `ReturnToFoyer()`/`DoGameOver(string)` exist on `GameManager` [IL]; which one vanilla pasts use after the credits is unverified. Building the past *floor* (flow with entrance + our BOSS room) is a separate, larger task (Alexandria DungeonAPI `SampleFlow`/`OfficialFlows`/`DungeonHandler.CreateSpecialFlowFlow`).
6. **Boss-pool table keys** (`"bulletking"` etc.) come from the current source's `StaticReferences.BossRoomGrabage`; 0.5.10 has `StaticReferences.BossRoomTableMap` [IL] — verify the key names at runtime (`StaticReferences.RoomTables.Keys`).
7. **Boss card strings**: plain strings (Expand The Gungeon) vs `#KEY` + `ETGMod.Databases.Strings.Enemies.Set` (F&G) — pick whichever renders correctly; `StringTableManager.GetEnemiesString(string key, int index = -1)` is the lookup [IL].
8. **`BraveBehaviour.OnDestroy` accessibility** differs between publicized and stock GameLibs (`public virtual` in this stub); the sketch avoids overriding it.
9. **Enemy projectile damage** to the player is governed by the game's per-hit rules; `ProjectileData.damage` on a copied bank entry is not a knob for "half vs full heart" (unverified). Speed/range are.
10. **`ExplosionData` copy** relies on RPG (id 19) having an `ExplosiveModifier` on `DefaultModule.projectiles[0]` — true in vanilla but unverified here; any `ExplosiveModifier` will do.
11. Sprite pivot/anchor specifics of `ConstructDefinition` (bottom-center vs lower-left) not re-verified; keep every frame the same size and feet-aligned.
12. `GenericIntroDoer.introAnim` (raw clip) vs `introDirectionalAnim` (directional) — F&G uses the raw clip name; the sketch follows that.

---

## 8. Sources

* Local IL dumps (scratchpad `il3/`): `alex.il` (Alexandria 0.5.10), `game.il` (GameLibs 2.1.9.1); line numbers quoted above.
* Alexandria current source (matches 0.5.10 EnemyAPI): https://github.com/Nevernamed22/Alexandria — `EnemyAPI/BossBuilder.cs`, `EnemyAPI/EnemyBuilder.cs`, `EnemyAPI/EnemyBuildingTools.cs`, `EnemyAPI/AttackBehaviourUtility.cs`, `EnemyAPI/EnemyTools.cs`, `EnemyAPI/OverrideBehavior.cs`, `ItemAPI/SpriteTools/SpriteBuilder.cs`, `ItemAPI/SpriteTools/ResourceExtractor.cs`, `DungeonAPI/RoomFactory.cs`, `DungeonAPI/DungeonHandler.cs`, `DungeonAPI/StaticReferences.cs`, `CharApi/CharacterBuilding/Loader.cs` (Thunderstore page: https://thunderstore.io/c/enter-the-gungeon/p/Alexandria/Alexandria/ , latest 0.5.10). The older fork https://github.com/nota8ot/Alexandria (namespace `EnemyAPI`) is pre-0.5 and was only used for comparison.
* Modding guide "Creating An Enemy": https://mtgmodders.gitbook.io/etg-modding-guide/misc/making-an-enemy (markdown: append `.md`); index: https://mtgmodders.gitbook.io/etg-modding-guide/llms.txt (no boss page exists).
* Frost & Gunfire (Neighborin0, author of Alexandria's EnemyBuilder): https://github.com/Neighborin0/FrostAndGunfire — `Enemies/RoomMimic.cs` (boss via BossBuilder + intro + custom bullet scripts), `Enemies/RoomMimicIntro.cs` (SpecificIntroDoer), `EnemyAPI/BossBuilder.cs` (`SetupBasicIntro`, `AddEnemyToDatabase`, `SetupEntry`), `ExampleEnemies/Humphrey.cs` (gun-holding enemy, `DuplicateAIShooterAndAIBulletBank`, `ShootGunBehavior`), `ExampleEnemies/Milton.cs`.
* Expand The Gungeon (BepInEx port): https://github.com/ApacheThunder/ExpandTheGungeon_BepInEX — `ExpandTheGungeon/ExpandPrefab/ExpandWesternBrosPrefabBuilder.cs` (GenericIntroDoer/PortraitSlideSettings on a cloned vanilla boss), `ExpandComponents/ExpandWesternBroIntroDoer.cs` (SpecificIntroDoer), `ExpandComponents/ExpandWesternBroDeathController.cs` (OnPreDeath hook), `ExpandComponents/ExpandGungeoneerMimicIntroDoer.cs`, `ExpandPrefab/ExpandGungeoneerMimicBossPlacable.cs`.
* Planetside of Gunymede source: https://github.com/Some-Bunny/Planetside (vendors its own `APIs/EnemyBuilders/BossBuilder.cs`; its boss code is not in the public tree — nothing further usable).
* Room Architect Tool: https://enter-the-gungeon.thunderstore.io/package/Alexandria/RoomArchitectTool/
* Project files referenced: `PlutoTheCat/src/Plugin.cs` (`GMStart` step order, resource roots), `PlutoTheCat/src/CocoBlueItem.cs` (CompanionBuilder usage), `PlutoTheCat/PlutoTheCat.csproj` (embeds `Resources\**\*.png`), `docs/research/01-custom-character-research.md` (`Loader.BuildCharacter(... hasCustomPast, customPast)`), `docs/v2-roadmap.md` (past plan).
