# Custom Playable Character for Enter the Gungeon (BepInEx / Thunderstore, state as of 2026-09)

Everything below was pulled from live sources during this session (GitHub trees/raw files, Thunderstore API, NuGet registration feeds). Items I could not verify are flagged inline and collected at the end.

---

## 1. Current toolchain

| Component | Thunderstore package (dependency string) | Latest | GitHub | Notes |
|---|---|---|---|---|
| BepInEx | `BepInEx-BepInExPack_EtG-5.4.2101` | 5.4.2101 (last updated 2022-07-27) | https://github.com/BepInEx/BepInEx | "Preconfigured and includes unstripped Unity DLLs". NuGet libs are `BepInEx.BaseLib 5.4.21` / `BepInEx.Core 5.4.21`. |
| Mod the Gungeon API (MtG API) | `MtG_API-Mod_the_Gungeon_API-1.9.2` | 1.9.2 | https://github.com/SpecialAPI/ModTheGungeonAPI | BepInEx plugin GUID `etgmodding.etg.mtgapi`; exposes `ETGModMainBehaviour.GUID`, `ETGModMainBehaviour.WaitForGameManagerStart`, `ETGModConsole`, `ETGMod.Assets.Packer`. Every EtG mod depends on it. |
| Alexandria | `Alexandria-Alexandria-0.5.10` | 0.5.10 (updated 2026-08-17) | https://github.com/Nevernamed22/Alexandria | Plugin GUID `alexandria.etgmod.alexandria`. Contains `Alexandria.CharacterAPI` (namespace) in `CharApi/CharacterBuilding/*`. Depends on `MtG_API-Mod_the_Gungeon_API-1.9.1`. |
| Custom Characters Mod (CCM) | `KyleTheScientist-Custom_Characters_Mod-2.2.8` | 2.2.8 (updated 2024-10-17) | https://github.com/KyleTheScientist/GungeonCharacters (branch `master`, last push 2024-10-20) | Plugin GUID `kyle.etg.CCM`. Deps: `MtG_API-Mod_the_Gungeon_API-1.8.7`, `Alexandria-Alexandria-0.4.14`, `BepInEx-BepInExPack_EtG-5.4.2101`. Credits: "KyleTheScientist - original mod for Mod the Gungeon. An3s - original port to BepInEx. SpecialAPI - minor bug fixes and updates. Captain Pretzel - minor bug fixes and updates." A re-upload `Fih-Custom_Characters_Mod-2.2.8` (2026-05-06) points at the same GitHub repo. |

**Two distinct ways to make a character today:**

- **Route A – data-only (no C#): Custom Characters Mod.** You ship a folder containing `characterdata.txt` + PNGs. CCM scans `BepInEx/plugins` recursively for `characterdata.txt` (`Directory.GetFiles(BepInEx.Paths.PluginPath, "characterdata.txt", SearchOption.AllDirectories)` in `Loader.cs`). Sprites *replace* the base character's existing tk2d sprite definitions by name. This is what nearly all Thunderstore character packages use (55 of 456 EtG packages have "character" in the name; the most downloaded ones — The Captain, The Afflicted, Kirby, The Banker, Omicron, dax — all depend on `KyleTheScientist-Custom_Characters_Mod`).
- **Route B – C# plugin: Alexandria `CharacterAPI`.** Same `characterdata.txt` grammar (superset), but files are **embedded resources** in your DLL and you call `Alexandria.CharacterAPI.Loader.BuildCharacter(...)`. Gives a real new `PlayableCharacters` enum value (`ETGModCompatibility.ExtendEnum<PlayableCharacters>(guid, nameShort)`), brand-new sprite collections/animation clips (`newspritesetup/` folders), alt skins, alt guns, custom breach idles, win pics, coop death icon, glow shaders, Hegemony cost, custom past. Used by Once More Into The Breach (Shade), Enter the Beyond (Lost), Frost & Gunfire, Knife to a Gunfight.

The CCM 2.2.8 changelog: "Added Alexandria dependency for helping coordinate UI sprite usage with other mods" — CCM now calls `Alexandria.CharacterAPI.ToolsCharApi.AddUISprite(...)` for face cards.

Sources: Thunderstore experimental API (`/api/experimental/package/{ns}/{name}/`), https://thunderstore.io/c/enter-the-gungeon/p/KyleTheScientist/Custom_Characters_Mod/ , https://thunderstore.io/c/enter-the-gungeon/p/Alexandria/Alexandria/ , https://thunderstore.io/c/enter-the-gungeon/p/BepInEx/BepInExPack_EtG/ , https://thunderstore.io/c/enter-the-gungeon/p/MtG_API/Mod_the_Gungeon_API/

---

## 2. Character definition format

It is a **plain text file named `characterdata.txt`** (not JSON, not C#) plus sprite folders. Parser: `CustomCharacters/CharacterBuilding/Loader.cs` (CCM) and `CharApi/CharacterBuilding/Loader.cs` (Alexandria, superset).

### Grammar (verbatim from `Loader.ParseCharacterData`)
- Lines are lowercased/trimmed for key matching; empty lines and lines starting with `#` are skipped.
- `key: value` lines. Recognised keys:
  - `base:` — vanilla character to clone. Matched case-insensitively against `PlayableCharacters` enum names with `coop` stripped; aliases: `marine`→`Soldier`, `hunter`→`Guide`, `paradox`→`Eevee`. Unknown → falls back to `Pilot`. If base is `Robot`, `armor` defaults to 6.
  - `name:` — display name (`#PLAYER_NAME_<NAMESHORT>` string table).
  - `name short:` — spaces replaced by `_`; internal object name becomes `"Player" + nameShort`.
  - `nickname:` — `#PLAYER_NICK_<NAMESHORT>`.
  - `armor:` — float.
  - `punchout sprite fix: true|false` — (2.2.6+) stretches replacement punchout frames to match original size.
  - Anything else with a `:` → logged as "did not meet any expected criteria" (so `Armor: 0` at file end in Frost & Gunfire is silently ignored... actually `armor:` matches after lowercasing, so it works).
- Blocks:
  - `<loadout>` … `</loadout>` — one item per line: `<item_id> [infinite]`. `item_id` is resolved with `Gungeon.Game.Items[args[0]]` (MtG API item registry — vanilla console names like `shades_revolver`, or modded `prefix:name` like `nn:elder_magnum`, `kp:icepick`, `bot:lost_sidearm`). `infinite` only valid on guns; sets `InfiniteAmmo`, `PersistsOnDeath`, `CanBeDropped=false`, `PreventStartingOwnerFromDropping`.
  - `<stats>` … `</stats>` — `StatName: float`, name matched against `PlayerStats.StatType` enum. Applied via `player.stats.SetBaseStatValue`. `DodgeRollDistanceMultiplier`/`DodgeRollSpeedMultiplier` also modify `rollStats`.
  - `<altGuns>` … `</altGuns>` — **Alexandria only** (alternate-costume starting guns, same syntax as loadout).
- **There is no `health:` key.** Health is set through `Health:` inside `<stats>` (StatType.Health). `CustomCharacterData.health` defaults to 3.

### Real example 1 — Thunderstore-packaged CCM character (verbatim)
https://github.com/kio-stdioh/gungeon-custom-character-kotonoha/blob/main/plugins/kio-stdioh-custom-character-akane-kotkonoha/characterdata.txt
```
base: rogue
name: Akane.K
name short: Akane
nickname: Red sis

<loadout>
	shades_revolver infinite
	hot_lead
	blue_guon_stone
</loadout>

<stats>
	Accuracy: 0.7
	AdditionalBlanksPerFloor: 0
	AdditionalClipCapacityMultiplier: 1
	AdditionalGunCapacity: 0
	AdditionalItemCapacity: 0
	AdditionalShotBounces: 0
	AdditionalShotPiercing: 0
	AmmoCapacityMultiplier: 1
	ChargeAmountMultiplier: 1
	Coolness: 0
	Curse: 0
	Damage: 1
	DamageToBosses: 1
	DodgeRollDamage: 1
	DodgeRollDistanceMultiplier: 1
	DodgeRollSpeedMultiplier: 1
	EnemyProjectileSpeedMultiplier: 1
	ExtremeShadowBulletChance: 0
	GlobalPriceMultiplier: 1
	Health: 2
	KnockbackMultiplier: 1
	MoneyMultiplierFromEnemies: 1
	MovementSpeed: 6.5
	PlayerBulletScale: 1
	ProjectileSpeed: 1
	RangeMultiplier: 1
	RateOfFire: 1
	ReloadSpeed: 1.1
	ShadowBulletChance: 0
	TarnisherClipCapacityMultiplier: 1
	ThrownGunDamage: 1
</stats>
```
(That `<stats>` block is the full list of `PlayerStats.StatType` names modders use; vanilla MovementSpeed is 7, Pilot 7.)

### Real example 2 — Alexandria route (Enter the Beyond, "The Lost"), verbatim
https://github.com/bobot-dev/enter-the-beyond/blob/HEAD/Characters/Lost/characterdata.txt
```
#Lines starting with hashtags and empty lines are not read by the character loader

#You HAVE to include these
base: guide
name short: Lost
name: The Lost

nickname: Hunted

#Set starting armor
armor: 0

<loadout>
	bot:lost_sidearm
	bot:wand
	bot:lost_robe
</loadout>

<altGuns>
	bot:lost_sidearm_alt
	bot:wand
</altGuns>

#This is an all-inclusive list of the stats available for changing
#The default values are in the guide. It's in the workshop page downloads.
<stats>

</stats>
```

### Loose files/folders the loader looks for (next to `characterdata.txt`)
CCM (`Loader.LoadFromDirectory`):
- `sprites/` — individual PNGs named exactly like base-character sprite definitions (see §3); **or** a single `playersheet.png` (full sheet replacement of the base atlas material's `mainTexture`; mutually exclusive, sheet wins).
- `foyercard/` — breach select-card animation frames.
- `icon.png` — minimap icon.
- `bosscard.png` — boss intro card (replaces every entry in `player.BosscardSprites`).
- `facecard.png` — HUD/conversation portrait (`player.uiPortraitName = nameInternal + "_facecard"`).
- `punchout/facecard1.png`, `facecard2.png`, `facecard3.png` — Punch-Out minigame health portraits.
- `punchout/sprites/` — Punch-Out player frames.

Alexandria additionally: `newspritesetup/`, `newaltspritesetup/`, `alt_sprites/`, `loadoutsprites/`, `coop_page_death.png`, `bosscard_001.png` (name must *contain* `bosscard_`; multiple allowed), `win_pic.png`, `win_pic_junkan.png`, `alt_skin_obj_sprite_001.png`/`_002.png`, `hand_001.png` / `hand_alt_001.png`.

---

## 3. Sprite names, frame counts, sizes

### Route A (CCM): names must match the base character's tk2d collection
`SpriteHandler.HandleAnimations`: for each PNG, `copyCollection.GetSpriteDefinition(tex.name)`; if found it is replaced, otherwise ignored. So the required names are exactly the vanilla sprite names of your `base:`. Observed prefixes per base (from real repos): Pilot → `rogue_`, Convict → `convict_` (+ `jailbird_` for 8 sprites), Soldier/Marine → `marine_`, Hunter/Guide → `guide_`, Robot → `robot_`. (Bullet/Eevee/Gunslinger prefixes not observed — unverified.)

Full **Pilot (`rogue_`) set** shipped by the Kotonoha mod (94 animations; frame numbers are `_001`…; counts are what they shipped and appear to mirror the vanilla clip lengths):

```
rogue_chest_recover x7        rogue_death x9                rogue_dodge_back x9
rogue_dodge_front x9          rogue_dodge_left x6 (+ rogue_dodge_left_001_02/_002_02/_004_02 hand-layer frames)
rogue_dodge_left_back x9      rogue_ghost_back x4           rogue_ghost_back_left x4
rogue_ghost_back_right x4     rogue_ghost_front x4          rogue_ghost_front_left x4
rogue_ghost_front_right x4    rogue_ghost_sneeze_front_left x4  rogue_ghost_sneeze_front_right x4
rogue_hand x1                 rogue_idle x4                 rogue_idle_back x6
rogue_idle_back_hand_left x6  rogue_idle_back_hand_right x6 rogue_idle_back_hands x6
rogue_idle_backwards x4       rogue_idle_backwards_hands2 x4
rogue_idle_front x6           rogue_idle_front_hand_left x6 rogue_idle_front_hand_right x6
rogue_idle_front_hands x6     rogue_idle_hands2 x4          rogue_idle_hands x4
rogue_jetpack_back x2         rogue_jetpack_back_right x2   rogue_jetpack_front x2
rogue_jetpack_front_hand x2   rogue_jetpack_front_right x2  rogue_jetpack_front_right_hand x2
rogue_pet_right x2            rogue_pit_return x6           rogue_pitfall x6
rogue_pitfall_down x6         rogue_run_back x6             rogue_run_back_doorway x10
rogue_run_back_hands2 x6      rogue_run_back_hands x6       rogue_run_back_hands_left x6
rogue_run_backward x6         rogue_run_backward_hands2 x6  rogue_run_forward x6
rogue_run_forward_hands2 x6   rogue_run_forward_hands x6    rogue_run_front x6
rogue_run_front_hands2 x6     rogue_run_front_hands x6      rogue_run_front_hands_left x6
rogue_select_choose x9        rogue_select_crouch x4        rogue_select_crouch_draw x4
rogue_select_idle x5          rogue_select_pose x5          rogue_select_pose_dance x3
rogue_select_thumbs_up x7     rogue_shot_death x10          rogue_slide_altright x1
rogue_slide_right x1          rogue_slide_up x1             rogue_spaceflail x8
rogue_spin x6                 rogue_tablekick x4            rogue_tablekick_down x3
rogue_tablekick_down_hands x3 rogue_tablekick_down_twohands x3  rogue_tablekick_hands x4
rogue_tablekick_twohands x4   rogue_tablekick_up x3         rogue_tablekick_up_twohand x3
rogue_tarnisher x6            rogue_weaponget x6
```
Hands variants: yes — vanilla uses `_hands`, `_hand_left`, `_hand_right`, `_hands2`, `_twohands`, `_hand` suffixes (used when a gun is held one-/two-handed; the no-suffix version is the "no gun" pose). The hand sprite itself is `rogue_hand_001` (4x4 px). Source tree: https://github.com/kio-stdioh/gungeon-custom-character-kotonoha/tree/main/plugins/kio-stdioh-custom-character-akane-kotkonoha/sprites

**Measured pixel sizes** (read from PNG headers in that repo): every body frame (`rogue_idle_001`, `rogue_run_front_001`, `rogue_dodge_front_001`, `rogue_death_001`, `rogue_pitfall_001`, `rogue_select_idle_001`) = **23x24**; `rogue_hand_001` = 4x4. CCM converts at **16 px per world unit** (`nw = tex.width/16f`) and, for non-Gunslinger bases, re-packs the texture via `ETGMod.Assets.Packer.Pack(tex)` with new quad bounds — so replacement frames may differ in size from the original; for Gunslinger it does `def.ReplaceTexture(tex)` (size must match).

### Route B (Alexandria `newspritesetup/`): folder-per-animation
`SpriteHandler.playerAnimInfo` (verbatim keys → WrapMode, fps). Folder name = clip name; PNGs inside are any name ending `_###`; clip sprites are registered as `<nameShort>_<folder><index>`:

```
chest_recover Once 12 | death Once 12 | death_coop Once 16 | death_shot Once 12
dodge Once 12 | dodge_bw Once 12 | dodge_left Once 12 | dodge_left_bw Once 12
doorway Once 10
ghost_idle_back/back_left/back_right/front/left/right Loop 4 | ghost_sneeze_left/right Once 8
idle, idle_backward, idle_backward_hand, idle_backward_twohands, idle_bw, idle_bw_twohands,
idle_forward, idle_forward_hand, idle_forward_twohands, idle_hand, idle_twohands  Loop 6
item_get Once 9
jetpack_down, jetpack_down_hand, jetpack_right, jetpack_right_bw, jetpack_right_hand, jetpack_up Loop 6
pet Loop 6
pitfall Once 15 | pitfall_down Once 15 | pitfall_return Once 11
run_down, run_down_hand, run_down_twohands, run_right, run_right_hand, run_right_twohands,
run_right_bw, run_right_bw_twohands, run_up, run_up_hand, run_up_twohands  Loop 9
slide_right, slide_up, slide_down Loop 2
spinfall Loop 16 | spit_out Once 12
tablekick_down, tablekick_down_hand, tablekick_right, tablekick_right_hand, tablekick_up Once 8
timefall Loop 8
```
Plus `breach_idles/<custom_name>/` (foyer idle phases, Loop 8 fps; `select_idle` and `select_choose` are referenced by `CharacterSelectIdleDoer`), `custom/<name>/` for arbitrary extra clips, `hand_001.png` at the root of `newspritesetup` (hand quad forced to 0.25x0.25 units), and `_armorless` suffixed folders when `hasArmourlessAnimations`. A folder containing only `cc_sprite_placeholder.png` makes `_hand`/`_twohands` fall back to the base folder and `death_coop` to `death`. Dodge: first half of frames get `invulnerableFrame=true, groundedFrame=false`; tablekick/slide all frames invulnerable. Shade's shipped frame counts: idle 4, run 6, dodge 9, death 8, death_shot 6, pitfall 5, pitfall_return 8, item_get 9, timefall 8, spinfall 6, jetpack 2, tablekick 2–4, ghost idle 3, sneeze 4.

Measured sizes for the Shade (Robot base, Alexandria route): body frames **17x19** (`robot_idle_001`) / **16x19** (`robot_run_front_001`); `hand_001` 4x4.

### UI art sizes (measured)
| Asset | Kotonoha (CCM, Pilot) | Shade (Alexandria, Robot) | Code constraint |
|---|---|---|---|
| `foyercard/*` frames (`rogue_alt_facecard_idle_###` x4, `rogue_alt_facecard_appearance_###` x5 / `robot_facecard_idle_###` x5, `robot_facecard_appear_###` x5) | 38x38 | 38x38 | — |
| `facecard.png` | 34x34 | 38x38 | `faceCardSizeInPixels = new Vector2(34, 34)`; UI atlas region `Rect(0,1235,2048,813)` |
| `punchout/facecard1..3.png` | — | 34x34 | atlas region `Rect(128,71,128,186)` |
| `bosscard.png` / `bosscard_001.png` | 427x240 | 427x240 | — |
| `icon.png` (minimap) | 9x9 | 9x9 | — |
| `win_pic.png`, `win_pic_junkan.png` | — | 115x71 | Alexandria only |
| `coop_page_death.png` | — | 11x13 | Alexandria only |
| punchout body frame (`shade_punch_idle_001`) | — | 23x57 | Alexandria punchout clips: `idle, punch_right/left, punch_left/right_miss(_far), hit_right/left, super(star), dodge_left/right, block, block_hit, duck, ...` with explicit frame-index arrays in `punchoutPlayerAnimInfo` |
| `loadoutsprites/*.png` | — | 20x13 | Alexandria only |
| `alt_skin_obj_sprite_001/002.png` | — | 32x32 | Alexandria only |

Note the `rogue_alt_facecard_appearance_001.png` in the Kotonoha repo is not a valid PNG (header check failed) — a real-world gotcha, and evidence CCM silently tolerates a bad file.

---

## 4. Thunderstore / r2modman packaging

**Required zip root files** (Thunderstore docs, verbatim): `icon.png` "PNG icon for the mod, must be 256x256 resolution."; `README.md`; `manifest.json`; optional `CHANGELOG.md`. "File naming is case-sensitive and must match the above exactly!" Zip *the files*, not a containing folder.

**manifest.json fields** (verbatim from docs): `name` — "Name of the mod, no spaces. Allowed characters: a-z A-Z 0-9 _" (max 128; underscores render as spaces); `description` — "Max 250 characters."; `version_number` — "Major.Minor.Patch"; `dependencies` — list of `{team name}-{package name}-{package version}` strings; `website_url` — "Can be left an empty string." Validator: https://thunderstore.io/c/enter-the-gungeon/tools/manifest-v1-validator/

Thunderstore's own example:
```json
{
    "name": "TestMod",
    "version_number": "1.1.0",
    "website_url": "https://github.com/thunderstore-io",
    "description": "This is a description for a mod. 250 characters max",
    "dependencies": [
        "MythicManiac-TestMod-1.1.0"
    ]
}
```

Real character manifest (kio-stdioh, verbatim):
```json
{
    "name": "Custom_Character_Kotonoha_Sisters",
    "version_number": "1.0.0",
    "website_url": "https://github.com/kio-stdioh/gungeon-custom-character-kotonoha",
    "description": "Adds Kotonoha Sisters(琴葉姉妹), two characters with accurate aim or high rate of fire.",
    "dependencies": [
        "MtG_API-Mod_the_Gungeon_API-1.8.7",
        "BepInEx-BepInExPack_EtG-5.4.2101",
        "KyleTheScientist-Custom_Characters_Mod-2.2.7"
    ]
}
```
For a Route-B (C#) mod today you'd declare `BepInEx-BepInExPack_EtG-5.4.2101`, `MtG_API-Mod_the_Gungeon_API-1.9.2`, `Alexandria-Alexandria-0.5.10`.

**r2modman install rules for EtG** (thunderstore-io/ecosystem-schema `games/data/generated/enter-the-gungeon.yml`, verbatim excerpt):
```yaml
packageLoader: "bepinex"
installRules:
  - route: "BepInEx/plugins"
    defaultFileExtensions: [".dll"]
    trackingMethod: "subdir"
    isDefaultLocation: true
  - route: "BepInEx/core"     ...
  - route: "BepInEx/patchers" ...
  - route: "BepInEx/monomod"  defaultFileExtensions: [".mm.dll"] ...
  - route: "BepInEx/config"   trackingMethod: "none"
```
`internalFolderName: "ETG"`, `dataFolderName: "EtG_Data"`, `exeNames: ["EtG.exe"]`. Meaning: a top-level `plugins/` folder in the zip is copied into `BepInEx/plugins/<Author>-<Name>/…` preserving structure; loose files are dumped there too but subfolders may be flattened. The community guide says: "these folders in your mod will put them in the files from your mod into the corresponding bepInEx folder when installed via the mod manager, and will also keep the file structure … if the mod went plugins/all the files then all the stuff like sprites etc. would have come out the same."

**CCM's official packaging instructions (README 2.2.8, verbatim):**
> 1. Make a folder for your custom character. 2. Inside that folder, make another folder named `plugins`. 3. Put all of the files for your custom character into the `plugins` folder. 4. Inside of your custom character folders (not `plugins`) make the following files: `manifest.json` … `README.md` … `icon.png`: … Must be 256x256 pixels. `CHANGELOG.md` (optional) … 5. Make a zip of all the files in your custom character folder (NOT a zip of the folder itself) and upload it.

Resulting zip layout (Route A, exactly what the Kotonoha repo is):
```
manifest.json
README.md
CHANGELOG.md
icon.png                      (256x256)
plugins/
  <your-character-folder>/
    characterdata.txt
    icon.png                  (9x9 minimap)
    facecard.png
    bosscard.png
    foyercard/*.png
    sprites/*.png
    punchout/facecard1..3.png
    punchout/sprites/*.png
  sprites/<CollectionName>/*.png   (optional MtG-API sprite replacements for other collections)
```
Route B: same root files + `plugins/YourMod.dll` (all art embedded in the DLL).

Sources: https://thunderstore.io/package/create/docs/ , https://mtgmodders.gitbook.io/etg-modding-guide/getting-started/uploading-a-mod.md , https://github.com/thunderstore-io/ecosystem-schema/blob/master/games/data/generated/enter-the-gungeon.yml

---

## 5. Open-source repos to model after

1. **https://github.com/kio-stdioh/gungeon-custom-character-kotonoha** — best Route-A template: the repo *is* the Thunderstore zip (root: `manifest.json`, `README.md`, `CHANGELOG.md`, `icon.png`; `plugins/<char>/{characterdata.txt, icon.png, facecard.png, bosscard.png, foyercard/, sprites/}` for two Pilot-based characters, plus `plugins/sprites/WeaponCollection/` gun reskins). Published as `kio_stdioh-Custom_Character_Kotonoha_Sisters-1.0.0`.
2. **https://github.com/Nevernamed22/OnceMoreIntoTheBreach** (`MakingAnItem/Characters/Shade/`, `Acolyte/`) — Route-B reference: every Alexandria folder (`newspritesetup/<anim>/`, `breach_idles/`, `punchout/sprites/`, `loadoutsprites/`, `win_pic*`, `coop_page_death`, `alt_skin_obj_sprite_*`), embedded via `<EmbeddedResource Include="Characters\\Shade\\..." />` in `NevernamedsItems.csproj`, built in `Class1.cs`:
   ```csharp
   [BepInPlugin(GUID, "Once More Into The Breach", "1.32.0")]
   [BepInDependency(ETGModMainBehaviour.GUID)]
   [BepInDependency("etgmodding.etg.mtgapi")]
   [BepInDependency("alexandria.etgmod.alexandria")]
   ...
   var data = Loader.BuildCharacter("NevernamedsItems/Characters/Shade",
      "nevernamed.etg.omitb",
       new Vector3(12.3f, 21.3f),   // foyer position
       false,                       // hasAltSkin
        new Vector3(13.1f, 19.1f),  // altSwapperPos
        false, false, true,
        true,  //Sprites used by paradox
        false, //Glows
        null,  //Glow Mat
        null,  //Alt Skin Glow Mat
        0,     //Hegemony Cost
        false, //HasPast
        "");   //Past ID String
   ```
   Full signature (Alexandria `Loader.cs`): `BuildCharacter(string filePath, string guid, Vector3 foyerPos, bool hasAltSkin, Vector3 altSwapperPos, bool removeFoyerExtras = true, bool hasArmourlessAnimations = false, bool usesArmourNotHealth = false, bool paradoxUsesSprites = true, bool useGlow = false, GlowMatDoer glowVars = null, GlowMatDoer altGlowVars = null, int metaCost = 0, bool hasCustomPast = false, string customPast = "")`. `filePath` is the embedded-resource path (`RootNamespace/Characters/Name`, slashes become dots).
3. **https://github.com/bobot-dev/enter-the-beyond** (`Characters/Lost/`, `Characters/Shade/`) and **https://github.com/Neighborin0/FrostAndGunfire** (`Resources/characters/Wanderer/`, Marine base, CCM-style `sprites/` with 588 `marine_*` PNGs) — extra Route-A/B references; the Lost `characterdata.txt` is the best-commented one.
4. **https://github.com/Hotklou2404/ChaosMarine** — README/CHANGELOG only (art lives in Releases zips; pre-BepInEx `CustomCharacterData` era). Useful as a stats-tuning changelog, not as a layout model.

---

## 6. Reference assemblies without the game installed

Yes — NuGet, from the **BepInEx feed, not nuget.org**. `EtG.GameLibs` on nuget.org is a *placeholder* ("Placeholder package to protect the users of nuget.bepinex.dev against CVE-2021-24105", version `0.0.0-placeholder.0`). The real package is on `https://nuget.bepinex.dev/v3/index.json`:

- `EtG.GameLibs 2.1.9.1` (net35; ships `Assembly-CSharp.dll`, `Assembly-CSharp-firstpass.dll`, `PlayMaker.dll`) — published 2022-08-13, still the current one.
- `EtG.UnityEngine 1.0.0` — "Stripped unity dlls for EtG modding." (`UnityEngine.dll` + all `UnityEngine.*Module.dll`).
- `EtG.ModTheGungeonAPI 1.9.2` (also on nuget.org) — deps `BepInEx.BaseLib/Core 5.4.21`, `EtG.GameLibs 2.1.9.1`, `EtG.UnityEngine 1.0.0`, `Newtonsoft.Json 13.0.1`.
- `EtG.Alexandria 0.5.10` (nuget.org; deps `BepInEx.BaseLib >=5.4.21`, `EtG.ModTheGungeonAPI >=1.9.0`).

**Target framework: `net35` (`<TargetFrameworkVersion>v3.5</TargetFrameworkVersion>`)** — old-style (non-SDK) csproj with `packages.config` is what every real project uses (CCM, Alexandria, OMITB, and SpecialAPI's official starter). Alexandria itself sets `<LangVersion>13.0</LangVersion>`, the starter uses `<LangVersion>latest</LangVersion>` — modern C# syntax compiles fine against net35.

Official starter template: https://github.com/SpecialAPI/BepInExExampleModItems (`Mod.sln`, `Mod.csproj`, `Plugin.cs`, `nuget.config`, `packages.config`). Its `nuget.config`:
```xml
<configuration>
	<packageSources>
		<add key="BepInEx" value="https://nuget.bepinex.dev/v3/index.json" />
	</packageSources>
</configuration>
```
Its `packages.config` (verbatim):
```xml
<packages>
  <package id="BepInEx.BaseLib" version="5.4.21" targetFramework="net35" />
  <package id="BepInEx.Core" version="5.4.21" targetFramework="net35" />
  <package id="EtG.Alexandria" version="0.4.25" targetFramework="net35" />
  <package id="EtG.GameLibs" version="2.1.9.1" targetFramework="net35" />
  <package id="EtG.ModTheGungeonAPI" version="1.9.2" targetFramework="net35" />
  <package id="EtG.UnityEngine" version="1.0.0" targetFramework="net35" />
  <package id="HarmonyX" version="2.7.0" targetFramework="net35" />
  <package id="Mono.Cecil" version="0.10.4" targetFramework="net35" />
  <package id="MonoMod.RuntimeDetour" version="21.12.13.1" targetFramework="net35" />
  <package id="MonoMod.Utils" version="21.12.13.1" targetFramework="net35" />
  <package id="Newtonsoft.Json" version="13.0.1" targetFramework="net35" />
</packages>
```
csproj reference pattern (from the same template):
```xml
<TargetFrameworkVersion>v3.5</TargetFrameworkVersion>
...
<Reference Include="Assembly-CSharp"><HintPath>packages\\EtG.GameLibs.2.1.9.1\\lib\\net35\\Assembly-CSharp.dll</HintPath></Reference>
<Reference Include="Assembly-CSharp-firstpass"><HintPath>packages\\EtG.GameLibs.2.1.9.1\\lib\\net35\\Assembly-CSharp-firstpass.dll</HintPath></Reference>
<Reference Include="BepInEx"><HintPath>packages\\BepInEx.BaseLib.5.4.21\\lib\\net35\\BepInEx.dll</HintPath></Reference>
<Reference Include="ModTheGungeonAPI"><HintPath>packages\\EtG.ModTheGungeonAPI.1.9.2\\lib\\net35\\ModTheGungeonAPI.dll</HintPath></Reference>
<Reference Include="Alexandria"><HintPath>packages\\EtG.Alexandria.0.4.25\\lib\\net35\\Alexandria.dll</HintPath></Reference>
<Reference Include="0Harmony"><HintPath>packages\\HarmonyX.2.7.0\\lib\\net35\\0Harmony.dll</HintPath></Reference>
<Reference Include="MonoMod.RuntimeDetour"/> <Reference Include="MonoMod.Utils"/> <Reference Include="Mono.Cecil*"/>
<Reference Include="Newtonsoft.Json"><HintPath>packages\\Newtonsoft.Json.13.0.1\\lib\\net35\\Newtonsoft.Json.dll</HintPath></Reference>
<Reference Include="PlayMaker"><HintPath>packages\\EtG.GameLibs.2.1.9.1\\lib\\net35\\PlayMaker.dll</HintPath></Reference>
<Reference Include="UnityEngine"><HintPath>packages\\EtG.UnityEngine.1.0.0\\lib\\UnityEngine.dll</HintPath></Reference>
<!-- + one <Reference> per UnityEngine.*Module.dll from EtG.UnityEngine.1.0.0\\lib -->
<EmbeddedResource Include="Resources\\example_item_sprite.png" />
```
Plugin skeleton (template `Plugin.cs`, verbatim core):
```csharp
[BepInDependency(Alexandria.Alexandria.GUID)]
[BepInDependency(ETGModMainBehaviour.GUID)]
[BepInPlugin(GUID, NAME, VERSION)]
public class Plugin : BaseUnityPlugin
{
    public const string GUID = "creator.etg.modname";
    public const string NAME = "MOD NAME";
    public const string VERSION = "0.0.0";
    public void Start() { ETGModMainBehaviour.WaitForGameManagerStart(GMStart); }
    public void GMStart(GameManager g) { /* build items / Loader.BuildCharacter(...) here */ }
}
```
The gitbook guide (https://mtgmodders.gitbook.io/etg-modding-guide/getting-started/setting-up-visual-studio.md) says to add the `https://nuget.bepinex.dev/v3/index.json` source in VS, enable .NET 3.5, and note "Version should ALWAYS consist of ONLY 2 decimal points". On macOS/Linux, `msbuild`/`mono` (or `dotnet build` with `Microsoft.NETFramework.ReferenceAssemblies.net35`) works since everything is HintPath-based — I did not test a build in this session.

---

## Not verified / caveats
- The full `PlayableCharacters` enum member list (Pilot, Convict, Robot, Ninja, Cosmonaut, Soldier, Guide, CoopCultist, Bullet, Eevee, Gunslinger) is from memory; only the aliases in `Loader.GetCharacterFromString` and `GetPlayerPrefab` (`Soldier→"marine"`, `Pilot→"rogue"`, else lowercase enum name) are verified from code.
- Sprite prefixes for Bullet/Eevee(Paradox)/Gunslinger bases were not observed in any repo.
- Frame counts listed for Route A are what the Kotonoha mod ships; I did not dump the vanilla tk2d collection to confirm they equal the vanilla clip lengths (CCM ignores extra names and keeps vanilla frames for missing ones, so mismatches degrade gracefully).
- Kyle's original Google-Doc guide (linked from the gitbook "Creating A Standalone Custom Character" page: https://docs.google.com/document/d/135ntlWancU6Mw6o2fevZQVtaIEMWL8TNu9Hd8-Bgng4) and the two CCM README screenshots of folder layout were not fetched (Google Docs / image content). ModWorkshop pages (Kyle's mod #24802, Bama sprite tool #31073) returned HTTP 403.
- I did not download any Thunderstore zip to inspect installed layout; the layout above is inferred from the Kotonoha repo (which mirrors the zip) plus the ecosystem-schema install rules.
- No Alexandria wiki exists (the `/wiki` fetch returned the repo page); CharacterAPI behavior above is taken directly from `CharApi/CharacterBuilding/{Loader,SpriteHandler,CharacterBuilder}.cs` on `main` (last push 2026-08-17).

Local copies of the fetched sources (for grepping) are in `/private/tmp/claude-501/-Users-bogdanionescu-Claude-Code-Projects-Enter-the-gungeon-pluto-mod/fa922dc9-23fc-4070-96c3-4970efbdaa7d/scratchpad/` (`Loader.cs`, `SpriteHandler.cs`, `CharacterBuilder.cs`, `alex_*.cs`, `omitb_Class1.cs`, `alex.csproj`).
