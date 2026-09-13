# Enter the Gungeon — Custom Gun + Custom Active Item + Charm (BepInEx / MtG API / Alexandria), 2026

Everything below was verified against source cloned today (2026‑09‑13) into the scratchpad: Alexandria `main` (VERSION `0.5.10`), MtG API `main`, OnceMoreIntoTheBreach (OMITB), LichItems, GungeonCraft, ReturnUnusedCharacters, and the decompiled game source `fedes1to/EtG-source`. Items I could **not** verify are called out explicitly in §8.

---

## 0. The stack (names, versions, URLs)

| Layer | Name | Version (Thunderstore, live API) | Source |
|---|---|---|---|
| Loader | `BepInEx-BepInExPack_EtG` | 5.4.2101 | — |
| Base API | **Mod the Gungeon API** — Thunderstore `MtG_API/Mod_the_Gungeon_API`, plugin GUID `etgmodding.etg.mtgapi` | **1.9.2** (2025‑01‑21) | https://github.com/SpecialAPI/ModTheGungeonAPI |
| Library | **Alexandria** — Thunderstore `Alexandria/Alexandria`, plugin GUID `alexandria.etgmod.alexandria` | **0.5.10** (2026‑08‑17), depends on `MtG_API-Mod_the_Gungeon_API-1.9.1` | https://github.com/Nevernamed22/Alexandria (Thunderstore page: https://thunderstore.io/c/enter-the-gungeon/p/Alexandria/Alexandria/) |
| Game source (decompiled, for reference only) | — | — | https://github.com/fedes1to/EtG-source (`ExportedProject/Assets/MonoScript/Assembly-CSharp/*.cs`) |

Note: the GitHub URL commonly cited as `Apache-Thunder/Alexandria` does **not** exist; Thunderstore's `website_url` for the package is `https://github.com/Nevernamed22/Alexandria`. The repo has no wiki (`Alexandria.wiki.git` 404) and its README is two lines; the Thunderstore README is the only "docs" and just lists API areas. The real documentation is the XML `<summary>` comments in source, plus open‑source mods.

Build facts (from `Alexandria.csproj`, `LichItems.csproj`): `TargetFrameworkVersion v3.5`, `LangVersion latest/13.0`, NuGet packages `EtG.GameLibs 2.1.9.1`, `EtG.ModTheGungeonAPI 1.9.x`, `EtG.Alexandria 0.5.x`, `BepInEx.Core 5.4.21`, `HarmonyX 2.7.0`, `MonoMod.RuntimeDetour 21.12.13.1`.

Plugin boilerplate (verbatim, `LichItems/Plugin.cs`, https://github.com/SpecialAPI/LichItems/blob/main/LichItems/Plugin.cs):

```csharp
[BepInPlugin(MOD_GUID, "Lich Items", "1.0.10")]
[BepInDependency(ETGModMainBehaviour.GUID)]
[BepInDependency(Alexandria.Alexandria.GUID)]
public class Plugin : BaseUnityPlugin
{
    public const string MOD_GUID = "spapi.etg.lichitems";

    public void Start()
    {
        ETGModMainBehaviour.WaitForGameManagerStart(GMStart);
    }

    public void GMStart(GameManager gm)
    {
        new Harmony(MOD_GUID).PatchAll();
        ETGMod.Assets.SetupSpritesFromAssembly(typeof(Plugin).Assembly, "LichItems/Resources/MTGAPISpriteRoot");

        CrossChamber.Init();
        LichsBookItem.Init();
        LichsGun.Init();
        ...
```

---

## 1. Custom GUN

### 1.1 Which API does what

| Call | Lives in | Signature (verbatim) |
|---|---|---|
| `ETGMod.Databases.Items.NewGun` | MtG API `ETGMod/Databases/ItemDB.cs` | `public Gun NewGun(string gunName, string gunNameShort = null)` — clones Pea Shooter, calls `SetupItem`, sets `gun.gunSwitchGroup = gunNameShort`, empties the volley, `SetBaseMaxAmmo(300)`, `reloadTime = 0.625f`, then `Gungeon.Game.Items.Add($"outdated_gun_mods:{gunName.ToID()}", gun)` |
| `gun.SetupSprite(collection, "x_idle_001", fps)` | MtG API `GunExt.cs` (embedded PNGs) **or** `Alexandria.Assetbundle.GunInt.SetupSprite(gun, collection, defaultSprite, fps, ammonomiconSprite)` (assetbundle collections) | MtG: `public static void SetupSprite(this Gun gun, tk2dSpriteCollectionData collection = null, string defaultSprite = null, int fps = 0)` |
| `gun.AddProjectileModuleFrom(...)` | MtG API `GunExt.cs` | `public static ProjectileModule AddProjectileModuleFrom(this Gun gun, Gun other, bool cloned = false, bool clonedProjectiles = true)` and a `string other` overload (`"klobb"`) |
| `ETGMod.Databases.Items.Add(gun, null, "ANY")` | MtG API `ItemDB.cs` | `public int Add(Gun value, tk2dSpriteCollectionData collection = null, string floor = "ANY")` → `AddSpecific`: appends to `PickupObjectDatabase`, assigns `PickupObjectId`, adds `EncounterDatabaseEntry`, adds to `RewardManager.GunsLootTable` |
| `proj.SetProjectileSpriteRight(...)` | Alexandria `ItemAPI/GunTools.cs` | `public static tk2dSpriteDefinition SetProjectileSpriteRight(this Projectile proj, string name, int pixelWidth, int pixelHeight, bool lightened = true, tk2dBaseSprite.Anchor anchor = tk2dBaseSprite.Anchor.LowerLeft, int? overrideColliderPixelWidth = null, int? overrideColliderPixelHeight = null, bool anchorChangesCollider = true, bool fixesScale = false, int? overrideColliderOffsetX = null, int? overrideColliderOffsetY = null, Projectile overrideProjectileToCopyFrom = null)` — reads from `ETGMod.Databases.Items.ProjectileCollection` (i.e. your `sprites/ProjectileCollection/<name>.png`) |
| `ProjectileUtility.SetupProjectile(int gunId)` | Alexandria `Misc/ProjectileUtility.cs` | Instantiates `(PickupObjectDatabase.GetById(id) as Gun).DefaultModule.projectiles[0]`, `SetActive(false)`, `FakePrefab.MarkAsFakePrefab`, `DontDestroyOnLoad`, returns it |
| `gun.AddToSubShop(ItemBuilder.ShopType.X)` | Alexandria `ItemBuilder.cs` | adds a `WeightedGameObject` to the shop loot table |

`GunBuilder` does not exist in Alexandria (GungeonCraft has its own private `GunBuilder.cs`). `ProjectileUtility` exists (Alexandria/Misc) but is helpers, not a builder.

### 1.2 Sprite loading & naming conventions (verified in MtG API source)

`ETGMod.Assets.SetupSpritesFromAssembly(asm, "YourMod/Resources/SpriteRoot")` scans embedded resources with exactly three dot‑separated segments after the root: `<CollectionName>.<spriteName>.png` (folder = collection). So in the .csproj you embed:

```
Resources/SpriteRoot/WeaponCollection/pluto_kibble_sack_idle_001.png
Resources/SpriteRoot/WeaponCollection/pluto_kibble_sack_fire_001.png ... _fire_00N.png
Resources/SpriteRoot/WeaponCollection/pluto_kibble_sack_reload_001.png ...
Resources/SpriteRoot/ProjectileCollection/pluto_kibble_projectile_001.png
Resources/SpriteRoot/Ammonomicon Encounter Icon Collection/... (optional)
```

Animation clip discovery (`GunExt.UpdateAnimations`, verbatim excerpt):

```csharp
gun.idleAnimation = gun.UpdateAnimationAddClipsLater("idle", collection, clipsToAddLater: clips);
gun.dodgeAnimation = gun.UpdateAnimationAddClipsLater("dodge", ...);
gun.introAnimation = gun.UpdateAnimationAddClipsLater("intro", collection, true, ...);
gun.emptyAnimation = gun.UpdateAnimationAddClipsLater("empty", ...);
gun.shootAnimation = gun.UpdateAnimationAddClipsLater("fire", collection, true, ...);
gun.reloadAnimation = gun.UpdateAnimationAddClipsLater("reload", collection, true, ...);
gun.chargeAnimation = gun.UpdateAnimationAddClipsLater("charge", ...);
gun.outOfAmmoAnimation = gun.UpdateAnimationAddClipsLater("out_of_ammo", ...);
gun.dischargeAnimation = gun.UpdateAnimationAddClipsLater("discharge", ...);
gun.finalShootAnimation = gun.UpdateAnimationAddClipsLater("final_fire", collection, true, ...);
gun.emptyReloadAnimation = gun.UpdateAnimationAddClipsLater("empty_reload", collection, true, ...);
gun.criticalFireAnimation = gun.UpdateAnimationAddClipsLater("critical_fire", collection, true, ...);
gun.enemyPreFireAnimation = gun.UpdateAnimationAddClipsLater("enemy_pre_fire", ...);
gun.alternateShootAnimation = ... "alternate_shoot" ...; gun.alternateReloadAnimation = ... "alternate_reload" ...; gun.alternateIdleAnimation = ... "alternate_idle" ...;
```

and `GunAnimationSpriteCache`: `var prefix = $"{gunName}_{animationName}";` with frames matched by regex `^(?<prefix>.*)_(?<order>\\d+)$`. **`gunName` is `gun.name`, i.e. the `gunNameShort` you pass to `NewGun`.** So `NewGun("Kibble Sack", "pluto_kibble_sack")` ⇒ sprites must be `pluto_kibble_sack_idle_001`, `pluto_kibble_sack_fire_001`…, `pluto_kibble_sack_reload_001`…. Default clip fps is 15; `gun.SetAnimationFPS(gun.shootAnimation, 15)`.

Hand/casing attach points: MtG API also reads a `<spriteName>.json` or `.jtk2d` next to the PNG (`AssetSpriteData` struct with `attachPoints`). Verbatim `LichItems/Resources/MTGAPISpriteRoot/WeaponCollection/lichsgun_idle_001.jtk2d`:

```json
{
  "name": null, "x": 0, "y": 0, "width": 26, "height": 10, "flip": 1,
  "attachPoints": [
    { ".": "arraytype", "name": "array", "size": 2 },
    { "name": "PrimaryHand", "position": { "x": 0.125, "y": 0.1875, "z": 0.0 }, "angle": 0.0 },
    { "name": "Casing",      "position": { "x": 0.5625, "y": 0.375,  "z": 0.0 }, "angle": 0.0 }
  ]
}
```

Positions are in world units = pixels/16. `Gun.cs` looks up `transform.Find("PrimaryHand")`, `"SecondaryHand"`, `"Clip"`, `"Casing"` and the sprite‑definition attach point named `"PrimaryHand"`. GungeonCraft auto‑sets `gun.barrelOffset.transform.localPosition` from the `"Casing"` attach point (`Lazy.SetupGun`).

### 1.3 Complete real example gun — verbatim

`OnceMoreIntoTheBreach/MakingAnItem/Content/Items/Guns/LovePistol.cs` (https://github.com/Nevernamed22/OnceMoreIntoTheBreach/blob/main/MakingAnItem/Content/Items/Guns/LovePistol.cs) — a **charm gun**, using Alexandria 0.5.6:

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Collections;
using Gungeon;
using MonoMod;
using UnityEngine;
using Alexandria.ItemAPI;
using Alexandria.Misc;

namespace NevernamedsItems
{

    public class LovePistol : GunBehaviour
    {
        public static void Add()
        {
            Gun gun = ETGMod.Databases.Items.NewGun("Love Pistol", "lovepistol");
            Game.Items.Rename("outdated_gun_mods:love_pistol", "nn:love_pistol");
            gun.gameObject.AddComponent<LovePistol>();
            gun.SetShortDescription(";)");
            gun.SetLongDescription("A low powered pistol, formerly kept in the back pocket of Hespera, the Pride of Venus, for times of need.");

            Alexandria.Assetbundle.GunInt.SetupSprite(gun, Initialisation.gunCollection, "lovepistol_idle_001", 8, "lovepistol_ammonomicon_001");

            gun.SetAnimationFPS(gun.shootAnimation, 15);

            gun.AddProjectileModuleFrom(PickupObjectDatabase.GetById(86) as Gun, true, false);
            gun.gunSwitchGroup = (PickupObjectDatabase.GetById(199) as Gun).gunSwitchGroup;

            //GUN STATS
            gun.DefaultModule.ammoCost = 1;
            gun.DefaultModule.shootStyle = ProjectileModule.ShootStyle.SemiAutomatic;
            gun.DefaultModule.sequenceStyle = ProjectileModule.ProjectileSequenceStyle.Random;
            gun.reloadTime = 0.8f;
            gun.DefaultModule.cooldownTime = 0.2f;
            gun.DefaultModule.numberOfShotsInClip = 9;
            gun.SetBarrel(22, 12);
            gun.SetBaseMaxAmmo(400);
            gun.gunClass = GunClass.CHARM;

            //BULLET STATS
            Projectile projectile = ProjectileSetupUtility.MakeProjectile(86, 4f);
            gun.DefaultModule.projectiles[0] = projectile;
            projectile.baseData.speed *= 0.9f;
            projectile.AppliesCharm = true;
            projectile.CharmApplyChance = 1f;
            projectile.charmEffect = StaticStatusEffects.charmingRoundsEffect;
            projectile.SetProjectileSprite("lovepistol_projectile", 7, 6, true, tk2dBaseSprite.Anchor.MiddleCenter, 7, 6);

            gun.AddShellCasing(1, 0, 0, 0, "shell_pink");
            gun.AddClipSprites("lovepistol");

            gun.muzzleFlashEffects = VFXToolbox.CreateVFXPoolBundle("LovePistolMuzzle", false, 0, VFXAlignment.Fixed, 10, new Color32(250, 0, 0, 255));

            projectile.hitEffects.overrideMidairDeathVFX = SharedVFX.SmallHeartImpact;
            projectile.hitEffects.alwaysUseMidair = true;
          
            gun.quality = PickupObject.ItemQuality.B;
            ETGMod.Databases.Items.Add(gun, null, "ANY");

            gun.AddToSubShop(ItemBuilder.ShopType.Cursula);
            LovePistolID = gun.PickupObjectId;
        }
        public static int LovePistolID;
        public override void PostProcessProjectile(Projectile projectile)
        {
            if (projectile && projectile.ProjectilePlayerOwner())
            {
                if (projectile.ProjectilePlayerOwner().PlayerHasActiveSynergy("Toxic Love")) { projectile.baseData.damage *= 2; }
                if (projectile.ProjectilePlayerOwner().PlayerHasActiveSynergy("Everlasting Love"))
                {
                    projectile.charmEffect = GameManager.Instance.Dungeon.sharedSettingsPrefab.DefaultPermanentCharmEffect;
                }
            }
            base.PostProcessProjectile(projectile);
        }
    }
}
```

Which of those calls are **OMITB‑local helpers (not Alexandria)**: `SetBarrel` (= `gun.barrelOffset.transform.localPosition = new Vector3(x/16f, y/16f, 0)`), `ProjectileSetupUtility.MakeProjectile` (instantiate + fakeprefab + set damage), `SetProjectileSprite` (wraps Alexandria `SetProjectileSpriteRight`/`SetProjectileCollisionRight`), `AddShellCasing`, `AddClipSprites`, `VFXToolbox.CreateVFXPoolBundle`, `StaticStatusEffects` (see §4), and `Initialisation.gunCollection` (an assetbundle). `gun.SetBarrel(22,12)` is literally `barrelOffset = (22/16f, 12/16f)`.

A second verbatim example that uses **only MtG API + Alexandria with embedded PNGs** (no assetbundle): `LichItems/LichsGun.cs` (https://github.com/SpecialAPI/LichItems/blob/main/LichItems/LichsGun.cs). Core of `Init()`:

```csharp
var gun = ETGMod.Databases.Items.NewGun("Lich's Gun", "lichsgun");
Game.Items.Rename("outdated_gun_mods:lich's_gun", "spapi:lichs_gun");
gun.SetShortDescription("The Freeshooter");
gun.SetLongDescription("The gun of the Gungeon master. The bullets of this gun can be guided after being fired.");
gun.SetupSprite(null, "lichsgun_idle_001", 10);
gun.SetAnimationFPS(gun.shootAnimation, 12);

gun.AddProjectileModuleFrom("klobb", true, false);
var projectile = CopyFields<InputGuidedProjectile>(UnityEngine.Object.Instantiate((PickupObjectDatabase.GetById(183) as Gun).DefaultModule.projectiles[0]));
projectile.gameObject.SetActive(false);
FakePrefab.MarkAsFakePrefab(projectile.gameObject);
UnityEngine.Object.DontDestroyOnLoad(projectile);

projectile.baseData.damage = 5f;
projectile.shouldRotate = true;
projectile.name = "LichsGun_Projectile";
projectile.baseData.range = 18f;
projectile.baseData.speed = 22f;
projectile.trackingSpeed = 500f;
projectile.dumbfireTime = -1f;
GunTools.SetProjectileSpriteRight(projectile, "lichsgun_projectile_001", 6, 6, false, tk2dBaseSprite.Anchor.MiddleCenter, overrideProjectileToCopyFrom: (PickupObjectDatabase.GetById(183) as Gun).DefaultModule.projectiles[0]);
gun.DefaultModule.projectiles[0] = projectile;

gun.DefaultModule.shootStyle = ProjectileModule.ShootStyle.SemiAutomatic;
gun.DefaultModule.angleVariance = 0;
gun.DefaultModule.ammoType = GameUIAmmoType.AmmoType.MEDIUM_BULLET;
gun.DefaultModule.cooldownTime = 0.1f;
gun.DefaultModule.numberOfShotsInClip = 6;

gun.reloadClipLaunchFrame = 0;
gun.gunSwitchGroup = "SAA";
gun.reloadTime = 1.1f;
gun.SetBaseMaxAmmo(350);
gun.quality = PickupObject.ItemQuality.SPECIAL;
gun.barrelOffset.transform.localPosition = new Vector3(1.1875f, 0.5625f, 0f);
gun.gunClass = GunClass.PISTOL;
gun.InfiniteAmmo = true;
gun.PreventStartingOwnerFromDropping = true;
...
ETGMod.Databases.Items.Add(gun, null, "ANY");
```

Its sprites live at `LichItems/Resources/MTGAPISpriteRoot/WeaponCollection/lichsgun_idle_001.png`, `lichsgun_fire_001..004.png`, `lichsgun_reload_001..004.png`, `ProjectileCollection/lichsgun_projectile_001.png`, loaded by the single `SetupSpritesFromAssembly` call in `Plugin.cs`. `InfiniteAmmo` + `PreventStartingOwnerFromDropping` are the two flags starter guns use.

### 1.4 Minimal synthesized skeleton (NOT verbatim — assembled from the verified calls above)

```csharp
public class KibbleSack : GunBehaviour
{
    public static int ID;
    public static void Add()
    {
        Gun gun = ETGMod.Databases.Items.NewGun("Kibble Sack", "pluto_kibble_sack"); // sprites: pluto_kibble_sack_idle_001 etc.
        Game.Items.Rename("outdated_gun_mods:kibble_sack", "pluto:kibble_sack");     // final string ID
        gun.gameObject.AddComponent<KibbleSack>();
        gun.SetShortDescription("Good Boy");
        gun.SetLongDescription("Lobs kibble.");
        gun.SetupSprite(null, "pluto_kibble_sack_idle_001", 10);                     // MtG API GunExt; WeaponCollection
        gun.SetAnimationFPS(gun.shootAnimation, 12);
        gun.AddProjectileModuleFrom("klobb", true, false);
        gun.DefaultModule.shootStyle = ProjectileModule.ShootStyle.SemiAutomatic;
        gun.DefaultModule.cooldownTime = 0.25f;
        gun.DefaultModule.numberOfShotsInClip = 6;
        gun.reloadTime = 1f;
        gun.SetBaseMaxAmmo(200);
        gun.gunClass = GunClass.CHARM;
        gun.barrelOffset.transform.localPosition = new Vector3(20f/16f, 8f/16f, 0f); // pixels/16 from sprite lower-left
        gun.InfiniteAmmo = true; gun.PreventStartingOwnerFromDropping = true;        // starter-gun flags (LichsGun)

        Projectile p = Alexandria.Misc.ProjectileUtility.SetupProjectile(56);       // clone Winchester bullet
        p.baseData.damage = 3f; p.baseData.speed = 16f; p.baseData.range = 20f;
        p.SetProjectileSpriteRight("pluto_kibble_projectile_001", 8, 8, false, tk2dBaseSprite.Anchor.MiddleCenter); // ProjectileCollection
        p.AppliesCharm = true; p.CharmApplyChance = 1f;
        p.charmEffect = PickupObjectDatabase.GetById(527).GetComponent<BulletStatusEffectItem>().CharmModifierEffect;
        gun.DefaultModule.projectiles[0] = p;

        gun.quality = PickupObject.ItemQuality.EXCLUDED; // starter gun; not in loot
        ETGMod.Databases.Items.Add(gun, null, "ANY");
        ID = gun.PickupObjectId;
    }
}
```

---

## 2. "Thrown object" / lobbed projectile guns

What vanilla actually has (verified in decompiled source):

- `GrenadeProjectile : Projectile` — a real vanilla class: simulates a Z height with gravity `-10`, bounces on ground contact (flips `z` velocity), and the sprite is offset by height via `specRigidbody.Velocity = (vx, vy + z)`. Fields: `public float startingHeight = 1f;`. Full file is 54 lines (`GrenadeProjectile.cs`).
- `ArcProjectile : Projectile` — vanilla lob with `startingHeight`, `startingZSpeed`, `gravity = -10f`, `destroyOnGroundContact = true`, `groundAudioEvent`, `LandingTargetSprite`, `event Action OnGrounded`, `AdjustSpeedToHit(Vector2 target)`. Used by enemies (OMITB `MolotovKin.cs` casts `bullet.Projectile as ArcProjectile`); no player‑gun mod usage found.
- Vanilla Bee Hive / Bouncer are ordinary projectiles with `HomingModifier` / `BounceProjModifier`. Vanilla Molotov (id 366) is not a gun; it is a `SpawnObjectPlayerItem` that tosses a `DebrisObject` (see §3.3).

Real mod precedent for a lobbed gun: GungeonCraft `Crapshooter.cs` and `Flakseed.cs` build their projectile as `GrenadeProjectile` and attach `BounceProjModifier` (https://github.com/pcrain/GungeonCraft/blob/master/src/Cwaff-Guns/Crapshooter.cs):

```csharp
.InitSpecialProjectile<GrenadeProjectile>(GunData.New(clipSize: 12, cooldown: 0.16f,
  shootStyle: ShootStyle.Automatic, scale: 2.0f, damage: 3f, speed: 24f, force: 10f, range: 30f, customClip: true,
  sprite: "crapshooter_projectile", fps: 12, anchor: Anchor.MiddleCenter, shouldRotate: false, becomeDebris: true))
.Attach<GrenadeProjectile>(g => { g.startingHeight = 0.5f; })
.Attach<BounceProjModifier>(bounce => {
  bounce.percentVelocityToLoseOnBounce = 0.5f;
  bounce.numberOfBounces = Mathf.Max(bounce.numberOfBounces, 0) + 3; ... })
```

(`InitSpecialProjectile<T>` is GungeonCraft‑private; it does the same as LichsGun's `CopyFields<T>` — add the derived `Projectile` component, copy every field, destroy the base `Projectile`. LichsGun's `CopyFields<T>(Projectile)` is verbatim in §1.3's file and works with any `Projectile` subclass, so `CopyFields<GrenadeProjectile>(...)` then `.startingHeight = 0.5f` is the drop‑in recipe.)

**Recommendation (simplest robust):** ship the kibble as a **normal `Projectile` with a custom 8×8–10×10 sprite**, `shouldRotate = false`, moderate `speed` (~14–18) and short `range` (~12–20), plus `BounceProjModifier` if you want it to skitter. That is exactly what almost every charm/food gun in OMITB and GungeonCraft does; it needs no subclass. If you want the visible "arc", upgrade to `GrenadeProjectile` via `CopyFields<GrenadeProjectile>` + `startingHeight = 0.5f` — vanilla class, proven in GungeonCraft. Avoid `ArcProjectile` (enemy‑oriented, destroys on ground contact, no player‑gun precedent).

---

## 3. Custom ACTIVE item

### 3.1 The vanilla surface (decompiled `PlayerItem.cs`)

Fields: `consumable = true` (default! set false), `numberOfUses`, `UsesNumberOfUsesBeforeCooldown`, `roomCooldown`, `timeCooldown`, `damageCooldown`, `usableDuringDodgeRoll`, `PreventCooldownBar`, `IsOnCooldown`, `IsCurrentlyActive`. Virtuals: `public virtual bool CanBeUsed(PlayerController user)`, `protected virtual void DoEffect(PlayerController user)`, `protected virtual void AfterCooldownApplied`, `DoActiveEffect`, `DoOnCooldownEffect`, `protected virtual void OnPreDrop`, plus inherited `Pickup(PlayerController)`. `Use()` flow: `CanBeUsed` → (if active) `DoActiveEffect` → (if on cooldown) `DoOnCooldownEffect` → else **`DoEffect(user)`**, then `ApplyCooldown`/`AfterCooldownApplied`.

### 3.2 Alexandria ItemBuilder (verbatim signatures/bodies, `ItemAPI/ItemBuilder.cs`)

```csharp
public enum CooldownType { Timed, Damage, PerRoom, None }

public static GameObject AddSpriteToObject(string name, string resourcePath, GameObject obj = null, Assembly assembly = null)
{
    GameObject spriteObject = SpriteBuilder.SpriteFromResource(resourcePath, obj, assembly ?? Assembly.GetCallingAssembly());
    FakePrefab.MarkAsFakePrefab(spriteObject);
    spriteObject.SetActive(false);
    spriteObject.name = name;
    return spriteObject;
}

public static void SetupItem(this PickupObject item, string shortDesc, string longDesc, string idPool = "ItemAPI")
{
    ...
        item.encounterTrackable = null;
        ETGMod.Databases.Items.SetupItem(item, item.name);
        SpriteBuilder.AddToAmmonomicon(item.sprite.GetCurrentSpriteDef(), idPool);
        item.encounterTrackable.journalData.AmmonomiconSprite = item.sprite.GetCurrentSpriteDef().name;
        item.SetName(item.name);
        item.SetShortDescription(shortDesc);
        item.SetLongDescription(longDesc);
        if (item is PlayerItem) (item as PlayerItem).consumable = false;
        Gungeon.Game.Items.Add(idPool + ":" + item.name.ToLower().Replace(" ", "_"), item);
        ETGMod.Databases.Items.Add(item);
    ...
}

public static void SetCooldownType(this PlayerItem item, CooldownType cooldownType, float value)
{
    item.damageCooldown = -1; item.roomCooldown = -1; item.timeCooldown = -1;
    switch (cooldownType)
    {
        case CooldownType.Timed:   item.timeCooldown = value; break;
        case CooldownType.Damage:  item.damageCooldown = value; break;
        case CooldownType.PerRoom: item.roomCooldown = (int)value; break;
    }
}
```

Also present: `ItemBuilder.BuildItem<T>(string name, string prefix, string spritePath, string shortDesc, string longDesc, ItemBuilder.CooldownType cooldownType, float rechargeTime, bool consumable, PickupObject.ItemQuality quality, Assembly assembly = null) where T : PlayerItem` (one‑liner that does AddSpriteToObject+SetupItem+SetCooldownType). `resourcePath` for `AddSpriteToObject` is the **embedded resource path** (e.g. `"PlutoMod/Resources/kibble_icon"`, `.png` optional) — `SpriteFromResource` calls `ResourceExtractor.GetTextureFromResource` and adds the sprite to the vanilla `ItemCollection` (`PickupObjectDatabase.GetById(155).sprite.Collection`).

### 3.3 Complete real active — verbatim, `LovePotion.cs` (OMITB; charm goop active)

https://github.com/Nevernamed22/OnceMoreIntoTheBreach/blob/main/MakingAnItem/Content/Items/Actives/LovePotion.cs

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

using UnityEngine;
using Alexandria.ItemAPI;
using SaveAPI;

namespace NevernamedsItems
{
    class LovePotion : PlayerItem
    {
        public static void Init()
        {
            PlayerItem item = ItemSetup.NewItem<LovePotion>(
           "Love Potion",
           "The Sausage Principle",
           "This potent potion of love was made by the Three Witches as part of a dashing romantic plot that was doomed to fail" + "\\n\\nIf you like something, never learn how it was made",
           "lovepotion_icon") as PlayerItem;

            ItemBuilder.SetCooldownType(item, ItemBuilder.CooldownType.Damage, 150);
            item.consumable = false;
            item.quality = ItemQuality.D;
            item.AddToSubShop(ItemBuilder.ShopType.Goopton);
            item.AddToSubShop(ItemBuilder.ShopType.Cursula);
            item.SetupUnlockOnCustomFlag(CustomDungeonFlags.PURCHASED_LOVEPOTION, true);
            item.AddItemToGooptonMetaShop(10);
        }

        public override void DoEffect(PlayerController user)
        {
            float length = 13;
            float width = 2.5f;
            if (user.PlayerHasActiveSynergy("Ooh Eee Ooh Ah Ah!"))
            {
                length = 20;
                width = 4;
            }
                DeadlyDeadlyGoopManager goopManagerForGoopType = DeadlyDeadlyGoopManager.GetGoopManagerForGoopType(EasyGoopDefinitions.CharmGoopDef);
            Vector2 vector = user.CenterPosition;
            Vector2 normalized = (user.unadjustedAimPoint.XY() - vector).normalized;
            goopManagerForGoopType.TimedAddGoopLine(user.CenterPosition, user.CenterPosition + normalized * length, width, 0.5f);
            if (user.PlayerHasActiveSynergy("Number 9")) goopManagerForGoopType.TimedAddGoopLine(user.CenterPosition, user.CenterPosition + (normalized * -1) * length, width, 0.5f);
            //goopManagerForGoopType.gameObject.AddComponent<PurifiedWaterGoop>();
        }

        public override bool CanBeUsed(PlayerController user)
        {
            return true;
        }
    }
}
```

`ItemSetup.NewItem<T>` is an OMITB helper; its body (verbatim, `ItemSetupUtility.cs`) is just `GameObject obj = new GameObject(name); Component item = obj.AddComponent(typeof(T)); ItemBuilder.AddSpriteToObject(name, filepath, obj); ItemBuilder.SetupItem(item as PickupObject, subtitle, description, "nn");` (assetbundle branch omitted). `SetupUnlockOnCustomFlag`/`AddItemToGooptonMetaShop` are OMITB‑local. Note `EasyGoopDefinitions.CharmGoopDef` is Alexandria (`Misc/GoopUtility.cs`: `PickupObjectDatabase.GetById(310)?.GetComponent<WingsItem>()?.RollGoop` — Fairy Wings charm goop).

### 3.4 Complete real *thrown* active — verbatim, `Jarate.cs` (OMITB; Alexandria ThrowableAPI)

https://github.com/Nevernamed22/OnceMoreIntoTheBreach/blob/main/MakingAnItem/Content/Items/Actives/Jarate.cs — this is the canonical "lob a physical object in an arc, then do an effect on landing" pattern. It subclasses vanilla `SpawnObjectPlayerItem` (what the Molotov uses) and the tossed prefab gets Alexandria's `CustomThrowableObject`:

```csharp
class Jarate : SpawnObjectPlayerItem
{
    public static void Init()
    {
        Jarate item = ItemSetup.NewItem<Jarate>(
       "Jarate",
       "Good Job",
       "Throws a jar of miracle fluids which weakens the Gundead. \\n\\nGungeoneering can be a long and tedious process. The ancient art of Jarate was derived as an ingenious solution to both combat and excrement reprocessing.",
       "jarate_icon") as Jarate;
      
        ItemBuilder.SetCooldownType(item, ItemBuilder.CooldownType.Damage, 800);
        item.consumable = false;
        item.objectToSpawn = BuildPrefab();
        item.tossForce = 12;
        item.canBounce = false;
        item.IsCigarettes = false;
        item.RequireEnemiesInRoom = false;
        item.SpawnRadialCopies = false;
        item.RadialCopiesToSpawn = 0;
        item.AudioEvent = null;
        item.IsKageBunshinItem = false;
        item.quality = PickupObject.ItemQuality.C;
    }

    public static GameObject BuildPrefab()
    {
        var bomb = SpriteBuilder.SpriteFromResource("NevernamedsItems/Resources/ThrowableActives/Jarate/jarate_toss_001.png", new GameObject("JarateToss"));
        bomb.MakeFakePrefab();

        var animator = bomb.AddComponent<tk2dSpriteAnimator>();
        var collection = (PickupObjectDatabase.GetById(108) as SpawnObjectPlayerItem).objectToSpawn.GetComponent<tk2dSpriteAnimator>().Library.clips[0].frames[0].spriteCollection;

        //DEPLOYMENT
        var deployAnimation = SpriteBuilder.AddAnimation(animator, collection, new List<int>
        {
            SpriteBuilder.AddSpriteToCollection("NevernamedsItems/Resources/ThrowableActives/Jarate/jarate_toss_004.png", collection),
        }, "deploy", tk2dSpriteAnimationClip.WrapMode.Once);
        deployAnimation.fps = 12;

        var explodeAnimation = SpriteBuilder.AddAnimation(animator, collection, new List<int>
        {
            SpriteBuilder.AddSpriteToCollection("NevernamedsItems/Resources/ThrowableActives/Jarate/jarate_break_001.png", collection),
            SpriteBuilder.AddSpriteToCollection("NevernamedsItems/Resources/ThrowableActives/Jarate/jarate_break_002.png", collection),
            SpriteBuilder.AddSpriteToCollection("NevernamedsItems/Resources/ThrowableActives/Jarate/jarate_break_003.png", collection),
        }, "break", tk2dSpriteAnimationClip.WrapMode.Once);
        explodeAnimation.fps = 16;

        var armedAnimation = SpriteBuilder.AddAnimation(animator, collection, new List<int>
        {
            SpriteBuilder.AddSpriteToCollection("NevernamedsItems/Resources/ThrowableActives/Jarate/jarate_toss_001.png", collection),
            SpriteBuilder.AddSpriteToCollection("NevernamedsItems/Resources/ThrowableActives/Jarate/jarate_toss_002.png", collection),
            SpriteBuilder.AddSpriteToCollection("NevernamedsItems/Resources/ThrowableActives/Jarate/jarate_toss_003.png", collection),
            SpriteBuilder.AddSpriteToCollection("NevernamedsItems/Resources/ThrowableActives/Jarate/jarate_toss_004.png", collection)
        }, "toss", tk2dSpriteAnimationClip.WrapMode.LoopSection);
        armedAnimation.fps = 12f;
        armedAnimation.loopStart = 0;

        CustomThrowableObject throwable = new CustomThrowableObject
        {
            doEffectOnHitGround = true,
            OnThrownAnimation = "deploy",
            OnHitGroundAnimation = "break",
            DefaultAnim = "toss",
            destroyOnHitGround = false,
            thrownSoundEffect = "Play_OBJ_item_throw_01",
            effectSoundEffect = "Play_OBJ_glassbottle_shatter_01",
        };
        bomb.AddComponent<CustomThrowableObject>(throwable);
        bomb.AddComponent<JarateSmashEffect>();
        return bomb;
    }
    public class JarateSmashEffect : CustomThrowableEffectDoer
    {
        public override void OnEffect(GameObject obj)
        {
            tk2dBaseSprite sprite = obj.GetComponent<tk2dBaseSprite>();
            GameObject splash = SpawnManager.SpawnVFX(SharedVFX.JarateExplosion, sprite.WorldCenter, Quaternion.identity);
            ...
            if (sprite.WorldCenter.GetAbsoluteRoom() != null)
            {
                List<AIActor> activeEnemies = sprite.WorldCenter.GetAbsoluteRoom().GetActiveEnemies(RoomHandler.ActiveEnemyType.All);
                if (activeEnemies != null)
                {
                    for (int i = 0; i < activeEnemies.Count; i++)
                    {
                        AIActor aiactor = activeEnemies[i];
                        if (Vector2.Distance(aiactor.Position, sprite.WorldCenter) < 5)
                        {
                            if (aiactor.healthHaver)
                            {
                                aiactor.ApplyEffect(new GameActorJarateEffect() { ... });
                            }
                        }
                    }
                }
            }
            StartCoroutine(Kill(obj));
        }
        private IEnumerator Kill(GameObject obj)
        {
            yield return new WaitForSeconds(0.25f);
            UnityEngine.Object.Destroy(obj);
            yield break;
        }
    }
}
```

Alexandria `ItemAPI/ThrowableAPI.cs` (verbatim): `public class CustomThrowableObject : SpawnObjectItem` with fields `thrownSoundEffect, landedSoundEffect, effectSoundEffect, DefaultAnim, OnTimedEffectAnim, OnThrownAnimation, OnHitGroundAnimation, OnEffectAnim, destroyOnHitGround, doEffectOnHitGround, doEffectAfterTime, timeTillEffect` and `public Action<GameObject> OnEffectTriggered;`; it hooks `DebrisObject.OnGrounded`. `public class CustomThrowableEffectDoer : MonoBehaviour { public virtual void OnEffect(GameObject obj) {} }` subscribes itself in `Start()`.

How vanilla does the arc (decompiled `SpawnObjectPlayerItem.DoSpawn`, the `tossForce != 0` branch):

```csharp
Vector2 vector2 = user.unadjustedAimPoint - user.LockedApproximateSpriteCenter;
vector2 = Quaternion.Euler(0f, 0f, angleFromAim) * vector2;
DebrisObject debrisObject = LootEngine.DropItemWithoutInstantiating(gameObject2, gameObject2.transform.position, vector2, tossForce, false, false, true);
...
debrisObject.IsAccurateDebris = true;
debrisObject.Priority = EphemeralObject.EphemeralPriority.Critical;
debrisObject.bounceCount = (canBounce ? 1 : 0);
```

Also in `DoSpawn`: if `objectToSpawn` has a `Projectile` component it is instantiated at the aim angle instead (`Quaternion.Euler(0,0,Atan2Degrees(aim))`), and afterwards `componentInChildren.Owner = LastOwner;` is set on any child `Projectile`. `Projectile.Start()` sets `m_currentDirection = m_transform.right` (line 866), so an instantiated projectile prefab flies along its rotation.

---

## 4. HOW TO CHARM AN ENEMY (exact code path)

### 4.1 What charm *is* (decompiled, verbatim `GameActorCharmEffect.cs`, 26 lines)

```csharp
[Serializable]
public class GameActorCharmEffect : GameActorEffect
{
	public override void OnEffectApplied(GameActor actor, RuntimeGameActorEffectData effectData, float partialAmount = 1f)
	{
		if (actor is AIActor)
		{
			AkSoundEngine.PostEvent("Play_OBJ_enemy_charmed_01", GameManager.Instance.gameObject);
			AIActor aIActor = actor as AIActor;
			aIActor.CanTargetEnemies = true;
			aIActor.CanTargetPlayers = false;
		}
	}

	public override void OnEffectRemoved(GameActor actor, RuntimeGameActorEffectData effectData)
	{
		if (actor is AIActor)
		{
			AIActor aIActor = actor as AIActor;
			aIActor.CanTargetEnemies = false;
			aIActor.CanTargetPlayers = true;
		}
	}
}
```

`GameActorEffect` base fields: `AffectsPlayers = true, AffectsEnemies = true, effectIdentifier = "effect", resistanceType, stackMode (Refresh/Stack/Ignore/DarkSoulsAccumulate), duration = 10f, maxStackedDuration = -1f, AppliesTint, TintColor, AppliesDeathTint, DeathTintColor, AppliesOutlineTint, OutlineTintColor, OverheadVFX, PlaysVFXOnActor`.

### 4.2 The apply call and the **boss gate** (decompiled `GameActor.cs` lines 602–633, verbatim)

```csharp
public void ApplyEffect(GameActorEffect effect, float sourcePartialAmount = 1f, Projectile sourceProjectile = null)
{
	if (ImmuneToAllEffects || (!effect.AffectsPlayers && this is PlayerController) || (!effect.AffectsEnemies && this is AIActor))
	{
		return;
	}
	float num = sourcePartialAmount;
	EffectResistanceType effectResistanceType = effect.resistanceType;
	if (effectResistanceType == EffectResistanceType.None)
	{
		if (effect.effectIdentifier == "poison") { effectResistanceType = EffectResistanceType.Poison; }
		if (effect.effectIdentifier == "fire")   { effectResistanceType = EffectResistanceType.Fire; }
		if (effect.effectIdentifier == "freeze") { effectResistanceType = EffectResistanceType.Freeze; }
		if (effect.effectIdentifier == "charm")  { effectResistanceType = EffectResistanceType.Charm; }
	}
	num *= 1f - GetResistanceForEffectType(effectResistanceType);
	if (num == 0f || (effect is GameActorCharmEffect && base.healthHaver != null && base.healthHaver.IsBoss))
	{
		return;
	}
	...
```

So: `AIActor` inherits `ApplyEffect` from `GameActor` (there is no override in `AIActor.cs`), and **any `GameActorCharmEffect` is silently dropped on bosses**, and any effect is dropped if the actor's resistance for that type is 100 %. There is no `ignoreBosses` flag.

### 4.3 How projectiles apply it (decompiled `Projectile.cs`, verbatim lines 94–98, 2498–2501, 2522–2525)

```csharp
public bool AppliesCharm;
public float CharmApplyChance = 1f;
public GameActorCharmEffect charmEffect;
...
public Action<Projectile, SpeculativeRigidbody, bool> OnHitEnemy;
public List<GameActorEffect> statusEffectsToApply = new List<GameActorEffect>();
...
if (AppliesCharm && UnityEngine.Random.value < CharmApplyChance)
{
	rigidbody.gameActor.ApplyEffect(charmEffect);
}
...
for (int i = 0; i < statusEffectsToApply.Count; i++)
{
	rigidbody.gameActor.ApplyEffect(statusEffectsToApply[i]);
}
```

(both inside the `if (!killedTarget && rigidbody.gameActor != null)` block of `HandleDamage`). `OnHitEnemy(this, rigidbodyCollision.OtherRigidbody, killedTarget)` fires at line 1904.

### 4.4 Where mods get a ready‑made charm effect object (verbatim)

OMITB `APIs and Toolboxes/OMITB Storage Classes/StaticStatusEffects.cs`:
```csharp
public static GameActorCharmEffect charmingRoundsEffect = PickupObjectDatabase.GetById(527).GetComponent<BulletStatusEffectItem>().CharmModifierEffect;
```
Same thing by name (OMITB `PearlBracelet.cs`): `Gungeon.Game.Items["charming_rounds"].GetComponent<BulletStatusEffectItem>().CharmModifierEffect;`

Permanent charm (used all over OMITB and by vanilla `AIActor.cs:2630`): `GameManager.Instance.Dungeon.sharedSettingsPrefab.DefaultPermanentCharmEffect`.

Yellow Chamber's (GungeonCraft `SubMachineGun.cs`): `(ItemHelper.Get(Items.YellowChamber) as YellowChamberItem).CharmEffect` — ids: Charming Rounds **527** (`BulletStatusEffectItem`), Charm Horn **206** (`RadialCharmItem`), Yellow Chamber **570** (`YellowChamberItem`), Molotov **366**.

Building your own with a custom duration (OMITB `StatusEffectHelper.GenerateCharmEffect`, verbatim):
```csharp
public static GameActorCharmEffect GenerateCharmEffect(float duration)
{
    GameActorCharmEffect charmEffect = new GameActorCharmEffect
    {
        duration = duration,
        TintColor = StaticStatusEffects.charmingRoundsEffect.TintColor,
        AppliesDeathTint = StaticStatusEffects.charmingRoundsEffect.AppliesDeathTint,
        AppliesTint = StaticStatusEffects.charmingRoundsEffect.AppliesTint,
        effectIdentifier = StaticStatusEffects.charmingRoundsEffect.effectIdentifier,
        DeathTintColor = StaticStatusEffects.charmingRoundsEffect.DeathTintColor,
        OverheadVFX = StaticStatusEffects.charmingRoundsEffect.OverheadVFX,
        AffectsEnemies = StaticStatusEffects.charmingRoundsEffect.AffectsEnemies,
        AppliesOutlineTint = StaticStatusEffects.charmingRoundsEffect.AppliesOutlineTint,
        AffectsPlayers = StaticStatusEffects.charmingRoundsEffect.AffectsPlayers,
        maxStackedDuration = StaticStatusEffects.charmingRoundsEffect.maxStackedDuration,
        OutlineTintColor = StaticStatusEffects.charmingRoundsEffect.OutlineTintColor,
        PlaysVFXOnActor = StaticStatusEffects.charmingRoundsEffect.PlaysVFXOnActor,
        resistanceType = StaticStatusEffects.charmingRoundsEffect.resistanceType,
        stackMode = StaticStatusEffects.charmingRoundsEffect.stackMode,
    };
    return charmEffect;
}
```
GungeonCraft's minimal one (`SharedItemBehaviors.cs`, verbatim): `new GameActorCharmEffect(){ AffectsPlayers = false, AffectsEnemies = true, effectIdentifier = "replicant", resistanceType = 0, stackMode = GameActorEffect.EffectStackingMode.Refresh, duration = 36000f };`

### 4.5 The three mod idioms for "charm the enemy I hit"

(a) Projectile flag (LovePistol §1.3): `projectile.AppliesCharm = true; projectile.CharmApplyChance = 1f; projectile.charmEffect = <effect>;`

(b) Generic list: `projectile.statusEffectsToApply.Add(<any GameActorEffect>)` — applied verbatim by the loop in §4.3 (this is also what Alexandria's `ProjectileUtility.GetFullListOfStatusEffects` reads).

(c) `OnHitEnemy` component (OMITB `SimpleToolbox.cs`, verbatim `PermaCharmBulletBehaviour`):
```csharp
public class PermaCharmBulletBehaviour : MonoBehaviour
{
    public PermaCharmBulletBehaviour()
    {
        this.tintColour = ExtendedColours.pink;
        this.useSpecialTint = true;
        this.procChance = 1;
    }
    private void Start()
    {
        this.m_projectile = base.GetComponent<Projectile>();
        if (useSpecialTint)
        {
            m_projectile.AdjustPlayerProjectileTint(tintColour, 2);
        }
        m_projectile.OnHitEnemy += this.OnHitEnemy;
    }
    private void OnHitEnemy(Projectile bullet, SpeculativeRigidbody enemy, bool fatal)
    {
        if (UnityEngine.Random.value <= procChance)
        {
            if (enemy && enemy.aiActor) enemy.aiActor.ApplyEffect(GameManager.Instance.Dungeon.sharedSettingsPrefab.DefaultPermanentCharmEffect, 1f, null);
        }
    }
    private Projectile m_projectile;
    public Color tintColour;
    public bool useSpecialTint;
    public float procChance;
}
```

### 4.6 Spawning a projectile from an active item that charms on hit

Verbatim manual‑spawn idiom (OMITB `Content/NPCs/TarotCardGunModifier.cs` `FireIndiv`):
```csharp
GameObject spawnObj = SpawnManager.SpawnProjectile(reloadVolleyProjectile.gameObject, gun.barrelOffset.position, Quaternion.Euler(new Vector3(0f, 0f, angle)));
Projectile component = spawnObj.GetComponent<Projectile>();
if (component != null)
{
    component.Owner = owner;
    component.Shooter = owner.specRigidbody;
    component.baseData.speed *= (1f + UnityEngine.Random.Range(-5f, 5f) / 100f);
    component.UpdateSpeed();
    owner.DoPostProcessProjectile(component);
}
```

Synthesized `DoEffect` for the kibble active (NOT verbatim; each line is one of the verified calls above):
```csharp
public override void DoEffect(PlayerController user)
{
    Vector2 dir = (user.unadjustedAimPoint.XY() - user.CenterPosition).normalized;   // LovePotion / DoSpawn idiom
    float angle = BraveMathCollege.Atan2Degrees(dir);
    GameObject go = SpawnManager.SpawnProjectile(KibbleProjectilePrefab.gameObject, user.CenterPosition, Quaternion.Euler(0f, 0f, angle));
    Projectile p = go.GetComponent<Projectile>();
    p.Owner = user; p.Shooter = user.specRigidbody;
    p.SendInDirection(dir, true);                                                    // Projectile.SendInDirection(Vector2, bool resetDistance, bool updateRotation=true)
    p.OnHitEnemy += (proj, rb, fatal) => { if (rb && rb.aiActor) rb.aiActor.ApplyEffect(KibbleCharm, 1f, null); };
    // or simply: p.statusEffectsToApply.Add(KibbleCharm);  / p.AppliesCharm = true; p.charmEffect = KibbleCharm;
}
```
Alternatively, use the Jarate pattern (§3.4): `SpawnObjectPlayerItem` + `CustomThrowableObject` and apply the charm to enemies within a radius in `OnEffect` — that gives you the true lobbed arc, bounce and landing animation for free.

### 4.7 Making it work on bosses / "all characters"

- The block is the `effect is GameActorCharmEffect && healthHaver.IsBoss` test in `GameActor.ApplyEffect` (§4.2), plus resistance (`GetResistanceForEffectType`, keyed by `effect.resistanceType`, or by `effectIdentifier == "charm"` when `resistanceType == None`). `YellowChamberItem` additionally self‑filters `!aIActor.IsNormalEnemy || aIActor.healthHaver.IsBoss || aIActor.IsHarmlessEnemy`; `AffectEnemiesInRadiusItem` (Charm Horn base) filters `!aIActor.IsNormalEnemy`.
- Cleanest bypass without Harmony: derive from **`GameActorEffect`**, not `GameActorCharmEffect`, and replicate the 4 lines of `OnEffectApplied/OnEffectRemoved` (`CanTargetEnemies = true; CanTargetPlayers = false;` and back). Because the gate uses `is GameActorCharmEffect`, a sibling subclass passes; set `resistanceType = EffectResistanceType.None` and an `effectIdentifier` other than `"charm"` so charm resistance is not consulted; `AffectsEnemies = true`. (This is exactly what Jarate does with its own `GameActorJarateEffect`.) Synthesized:
```csharp
public class UniversalCharmEffect : GameActorEffect   // deliberately NOT GameActorCharmEffect: skips the IsBoss gate in GameActor.ApplyEffect
{
    public override void OnEffectApplied(GameActor actor, RuntimeGameActorEffectData d, float partial = 1f)
    { if (actor is AIActor a) { a.CanTargetEnemies = true; a.CanTargetPlayers = false; AkSoundEngine.PostEvent("Play_OBJ_enemy_charmed_01", GameManager.Instance.gameObject); } }
    public override void OnEffectRemoved(GameActor actor, RuntimeGameActorEffectData d)
    { if (actor is AIActor a) { a.CanTargetEnemies = false; a.CanTargetPlayers = true; } }
}
// new UniversalCharmEffect { effectIdentifier = "pluto_charm", resistanceType = EffectResistanceType.None, AffectsEnemies = true, AffectsPlayers = false, duration = 10f, stackMode = GameActorEffect.EffectStackingMode.Refresh, OverheadVFX = StaticStatusEffects.charmingRoundsEffect.OverheadVFX, AppliesTint = true, TintColor = ... }
```
- Otherwise: a Harmony prefix on `GameActor.ApplyEffect` that swaps the effect's runtime type, or the direct approach `aiActor.CanTargetEnemies = true; aiActor.CanTargetPlayers = false;` with your own timer. Also note `AIActor.ImmuneToAllEffects` short‑circuits everything.

---

## 5. Custom character starting loadout referencing your gun/item

### 5.1 IDs / names (verified)

- `ETGMod.Databases.Items.NewGun("Kibble Sack", "pluto_kibble_sack")` → `gun.name = "pluto_kibble_sack"`, `gunSwitchGroup = "pluto_kibble_sack"`, registered as `outdated_gun_mods:kibble_sack` (via `gunName.ToID()` = `ToLowerInvariant().Replace(" ", "_")` with `.`/`-`/quotes stripped). Every mod immediately does `Game.Items.Rename("outdated_gun_mods:kibble_sack", "pluto:kibble_sack")`.
- `ItemDB.SetupItem` sets `item.encounterTrackable.EncounterGuid = item.name;` and `journalData.AmmonomiconSprite = item.name.Replace(' ', '_') + "_idle_001"`; `AddSpecific` then runs `EncounterGuid.RemoveUnacceptableCharactersForGUID()`.
- Alexandria `ItemBuilder.SetupItem(item, short, long, idPool)` registers actives/passives as `Gungeon.Game.Items.Add(idPool + ":" + item.name.ToLower().Replace(" ", "_"), item)` — so `new GameObject("Kibble Bowl")` + `SetupItem(..., "pluto")` ⇒ `pluto:kibble_bowl`.
- `IDPool.Resolve`: ids without `:` become `gungeon:<id>`; more than one `:` throws.

### 5.2 characterdata.txt (Alexandria CharacterAPI) — verbatim OMITB `Characters/Acolyte/characterdata.txt`

```
base: Pilot
name: The Acolyte
name short: Acolyte
nickname: wiz

<loadout>
	nn:gunjurers_staff
</loadout>

<altGuns>
    nn:elder_magnum
</altGuns>

<stats>
	
</stats>
```

Loader (`CharApi/CharacterBuilding/Loader.cs`, verbatim core of `GetLoadout`):
```csharp
args = line.Split(' ');
if (!Gungeon.Game.Items.ContainsID(args[0]))
{
    ToolsCharApi.PrintError("Could not find item with ID: \\"" + args[0] + "\\"");
    continue;
}
var item = Gungeon.Game.Items[args[0]];
...
if (args.Length > 1 && args[1].Contains("infinite"))
{
    var gun = item.GetComponent<Gun>();
    if (gun != null)
    {
        if (!CharacterBuilder.guns.Contains(gun) && !gun.InfiniteAmmo)
            CharacterBuilder.guns.Add(gun);
        items.Add(new Tuple<PickupObject, bool>(item, true));
```
Lines are lower‑cased, so write `pluto:kibble_sack infinite` and `pluto:kibble_bowl`. `CharacterBuilder.HandleLoadout` then sorts by component: `PassiveItem` → `player.startingPassiveItemIds`, `PlayerItem` → `startingActiveItemIds`, `Gun` → `startingGunIds`, `<altguns>` → `startingAlternateGunIds`. Entry point: `Loader.BuildCharacter(string filePath, string guid, Vector3 foyerPos, bool hasAltSkin, Vector3 altSwapperPos, ...)` reads `Path.Combine(filePath, "characterdata.txt")` from embedded resources (plus `loadoutsprites/` folder for the select‑screen icons: OMITB has `a_eldermagnum.png, b_handofnight.png, c_shadeheart.png`). **Your items must be registered before `BuildCharacter` runs.**

Without CharacterAPI (ReturnUnusedCharacters `LameyCharacter.cs`, verbatim) it is just: `lameyPlayer.startingGunIds = new() { LameyGunId }; lameyPlayer.startingAlternateGunIds = new() { ItemIds["altlamey_gun"] }; lameyPlayer.startingActiveItemIds = new() { ItemIds["disguisehat"] }; lameyPlayer.startingPassiveItemIds = new() { ItemIds["magnifyingglass"] };`

---

## 6. Sprite requirements (measured from real mods)

| Asset | Measured sizes | Notes |
|---|---|---|
| Gun frames | LichsGun 19×11 / 19×13; GungeonCraft most common `_idle_001` 34×20, 18×14, 23×12; big guns 48–64 px wide | All frames of one gun same canvas size. `pixel → world = /16`. Ammonomicon icon optional (`ammonomiconSprite` param). |
| Projectiles | GungeonCraft: 8×8 (most), 5×5, 7×6, 9×6, 16×16, 15×15; OMITB lovepistol 7×6, dart 16×7; LichsGun 6×6 | Pass true width/height to `SetProjectileSpriteRight(name, w, h, lightened, anchor, colliderW, colliderH)`; `Anchor.MiddleCenter` is the norm for round bullets. |
| Item icons | OMITB: 20×20, 19×19, 16×16, 14×14 (tall potions 9×21–15×22); GungeonCraft 16×17, 15×15, 16×16 | `AddSpriteToObject` takes any size; ammonomicon scales. |
| Thrown object | Jarate 26×27, Lvl2Molotov 22×23 | tk2d animation frames added to Molotov's collection. |

`barrelOffset`: `gun.barrelOffset.transform.localPosition = new Vector3(px/16f, py/16f, 0f)` measured from the sprite's lower‑left (verbatim examples: `new Vector3(22f/16f, 11f/16f, 0f)` ARCPistol, `new Vector3(1.1875f, 0.5625f, 0f)` LichsGun, `new Vector3(2.12f, 0.56f, 0f)` DartRifle). Hand attach points: `"PrimaryHand"`, `"SecondaryHand"`, `"Casing"`, `"Clip"` via the `.jtk2d` next to each frame (§1.2); `gun.gunHandedness` ∈ `{AutoDetect, TwoHanded, OneHanded, HiddenOneHanded, NoHanded}`; `gun.carryPixelOffset = new IntVector2(x, y)` shifts the gun on the body.

---

## 7. Sources

- Alexandria: https://github.com/Nevernamed22/Alexandria — `Module.cs`, `Assetbundle/GunInt.cs`, `Assetbundle/ProjectileBuilders.cs`, `Assetbundle/JsonEmbedder.cs`, `ItemAPI/GunTools.cs`, `ItemAPI/ItemBuilder.cs`, `ItemAPI/ThrowableAPI.cs`, `ItemAPI/SpriteTools/SpriteBuilder.cs`, `Misc/ProjectileUtility.cs`, `Misc/GoopUtility.cs`, `CharApi/CharacterBuilding/Loader.cs`, `CharacterBuilder.cs`; Thunderstore https://thunderstore.io/c/enter-the-gungeon/p/Alexandria/Alexandria/ (README via `/api/experimental/package/Alexandria/Alexandria/0.5.10/readme/`)
- MtG API: https://github.com/SpecialAPI/ModTheGungeonAPI — `ModTheGungeonAPI/ETGMod/Extensions/GunExt.cs`, `Databases/ItemDB.cs`, `IDPool.cs`, `Assets/Assets.cs`, `Assets/Data.cs`, `GunAnimationSpriteCache.cs`, `Extensions/Extensions.cs`, `ETGModMainBehaviour.cs`; Thunderstore https://thunderstore.io/c/enter-the-gungeon/p/MtG_API/Mod_the_Gungeon_API/
- OMITB: https://github.com/Nevernamed22/OnceMoreIntoTheBreach — `MakingAnItem/Content/Items/Guns/LovePistol.cs`, `DartRifle.cs`, `Content/Items/Actives/LovePotion.cs`, `Jarate.cs`, `Lvl2Molotov.cs`, `SimpleToolbox.cs`, `APIs and Toolboxes/OMITB Storage Classes/StaticStatusEffects.cs`, `.../StatusEffectHelper.cs`, `.../ItemSetupUtility.cs`, `.../MiscTools.cs`, `Content/NPCs/TarotCardGunModifier.cs`, `Characters/Acolyte/characterdata.txt`
- LichItems: https://github.com/SpecialAPI/LichItems — `LichItems/LichsGun.cs`, `LichItems/Plugin.cs`, `Resources/MTGAPISpriteRoot/WeaponCollection/*.jtk2d`
- GungeonCraft: https://github.com/pcrain/GungeonCraft — `src/Cwaff-Guns/Crapshooter.cs`, `Bouncer.cs`, `SubMachineGun.cs`, `src/SharedItemBehaviors.cs`, `src/Lazy.cs`, `src/Extensions.cs`, `src/Databases.cs`, `RawResources/*`
- ReturnUnusedCharacters: https://github.com/SpecialAPI/ReturnUnusedCharacters — `Characters/Lamey/LameyCharacter.cs`
- Decompiled game: https://github.com/fedes1to/EtG-source — `GameActorCharmEffect.cs`, `GameActorEffect.cs`, `GameActor.cs`, `AIActor.cs`, `Projectile.cs`, `GrenadeProjectile.cs`, `ArcProjectile.cs`, `SpawnObjectPlayerItem.cs`, `PlayerItem.cs`, `RadialCharmItem.cs`, `AffectEnemiesInRadiusItem.cs`, `YellowChamberItem.cs`, `BulletStatusEffectItem.cs`, `Gun.cs`, `GunHandedness.cs`
- Also surfaced by search (not used for code): ModWorkshop "Basic Gun (With Custom Gun Tutorial)" https://modworkshop.net/mod/26038 ; wiki.gg Modding page https://enterthegungeon.wiki.gg/wiki/Modding

## 8. Could not verify / caveats

- No official Alexandria wiki/docs exist (GitHub wiki 404, README is 2 lines); everything above comes from source and mods. The Alexandria assembly version attribute is stale (`AssemblyVersion("0.1.2")`); `Module.VERSION = "0.5.10"` matches Thunderstore.
- I could not compile anything (no Windows/.NET 3.5 toolchain here) — the two **synthesized** snippets (§1.4, §4.6, §4.7) are assembled from verified calls but are not lifted from a shipping mod.
- `fedes1to/EtG-source` is a third‑party decompile; it matched the GameLibs 2.1.9.1 metadata I dumped with `monodis` (types `GameActorCharmEffect`, `ArcProjectile`, `GrenadeProjectile`, `RadialCharmItem` all present), but I did not diff every method body against the shipped DLL.
- Charming a boss via the `GameActorEffect`‑sibling trick bypasses the type gate, but I did not test side effects (boss room‑clear logic, boss‑specific AI that ignores `CanTargetPlayers`, `ImmuneToAllEffects`, per‑enemy `EffectResistanceType.Charm` values). Vanilla's own charm items (`YellowChamberItem`, `AffectEnemiesInRadiusItem`) explicitly exclude bosses/non‑`IsNormalEnemy`, which suggests the devs never exercised that path.
- OMITB and GungeonCraft use asset‑bundle sprite collections; the embedded‑PNG path (`SetupSpritesFromAssembly` + `gun.SetupSprite(null, …)`) is verified via LichItems only. GungeonCraft's `Lazy.SetupGun` and `.jtk2d` files are produced by its own build tooling (`pcrain/gungeon-modding-tools`), which I did not inspect.
- Sprite "typical sizes" are empirical from the three mods measured, not a documented constraint; tk2d accepts any size.

## 9. Verification addendum (second pass, 2026-09-13)

Re-verified every claim in §§1–6 against the scratchpad copies (Alexandria `d88fe7a`, 0.5.10; MtG API 1.9.2; LichItems; OMITB; GungeonCraft; decompiled game). Corrections/additions:

- **`DoEffect`/`CanBeUsed`/`OnPreDrop` are `public` in the shipped GameLibs.** `EtG.GameLibs 2.1.9.1` is a publicized reference assembly (all method bodies are `ldnull; throw`; `ikdasm` shows `.method public hidebysig newslot virtual` for `PlayerItem::DoEffect`, `::CanBeUsed`, `::OnPreDrop`). So write `public override void DoEffect(PlayerController user)` exactly as LichItems/OMITB do; `protected override` will not compile against GameLibs even though the decompile says `protected virtual`.
- **A `PrimaryHand` attach point on the gun's default sprite is mandatory, not optional.** Decompiled `Gun.Initialize(GameActor)` (`Gun.cs:1471-1473`) does `attachPoints = m_sprite.Collection.GetAttachPoints(m_defaultSpriteID); attachPoint = attachPoints == null ? null : Array.Find(..., a => a.name == "PrimaryHand"); m_defaultLocalPosition = -attachPoint.position;` with no null guard, and `tk2dSpriteCollectionData.GetAttachPoints` returns `null` when the sprite has no attach data (`SpriteIDsWithAttachPoints.IndexOf(spriteId) < 0`). Neither MtG API nor Alexandria patches `Gun.Initialize`. Ship `<gun>_idle_001.jtk2d` (or `.json`) next to the PNG with at least `PrimaryHand` (LichItems ships them for idle/fire/reload frames). MtG API reads it via `JSONHelper.ReadJSON<AssetSpriteData>` (`Assets.cs:424/520`, extension constant `DEFINITION_METADATA_EXTENSION = "jtk2d"`).
- **`GetAttachPoints`/`SetAttachPoints` are on `tk2dSpriteCollectionData`** (Assembly-CSharp, not firstpass); `SetAttachPoints(id, aps)` with empty `aps` clears.
- Vanilla IDs re-confirmed from ETGMod `gungeon_id_map/items.txt` (copy in scratchpad): `charming_rounds` 527, `charm_horn` 206, `charmed_bow` 200, `yellow_chamber` 570, `molotov` 366, `molotov_launcher` 292, `bee_hive` 14, `grenade_launcher` 19, `lower_case_r` 340, `klobbe` 31, `magnum` 38, `38_special` 56, `marine_sidearm` 86, `ser_manuels_revolver` 183, `pea_shooter` 197, `fairy_wings` 310.
- `GunExt.AddProjectileModuleFrom(gun, other)` in MtG API 1.9.2 always deep-clones the module (`ProjectileModule.CreateClone(module, false)` + new `projectiles`/`chargeProjectiles` lists); the `cloned`/`clonedProjectiles` booleans are no-ops kept for compatibility. `AddProjectileFrom` does **not** clone the projectile (adds the vanilla prefab reference) — use `ProjectileUtility.SetupProjectile(id)` for a mutable copy.
- `ItemDB.NewGun` registers `outdated_gun_mods:{gunName.ToID()}` where `ToID()` = `ToLowerInvariant().Replace("\n","").Replace("\\","").Replace("\"","").Replace(" ","_").Replace(".","").Replace("-","")` (`Extensions.cs:58`) — apostrophes survive (hence `"outdated_gun_mods:lich's_gun"` in LichsGun).
- `CharApi Loader.GetLoadout` lower-cases each line before lookup, so the registered ID must already be all-lowercase (`pluto:kibble_sack`); `IDPool.Resolve` prefixes `gungeon:` when no colon is present.
- Scratchpad copies for grepping: `scratchpad/alexandria/` (full clone), `scratchpad/ModTheGungeonAPI/`, `scratchpad/LichItems/`, `scratchpad/OnceMoreIntoTheBreach/`, `scratchpad/GungeonCraft/`, `scratchpad/enter-the-beyond/`, `scratchpad/etgsrc/*.cs` (decompiled game files incl. `tk2dSpriteCollectionData.cs`), `scratchpad/gungeon_items_idmap.txt`, `scratchpad/asm_ikdasm.il` (GameLibs Assembly-CSharp disassembly).
