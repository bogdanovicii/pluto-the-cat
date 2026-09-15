# Pluto the Cat — Enter the Gungeon character mod (design spec / master prompt)

> **Historical: 1.0 design spec (2026-09-13).** The mod has moved on since; current behaviour is in `thunderstore/CHANGELOG.md` (2.16.2).

Date: 2026-09-13. Status: approved for implementation (autonomous session; user asked for research → prompt → build).

## 1. Goal

A Thunderstore/r2modman-installable mod that adds **Pluto the Cat** as a new playable Gungeoneer:

- Pixel art modelled on the real Pluto (photos in `reference/photos/`): a chunky brown-grey tabby-and-white cat. White muzzle, chest, belly and paws; grey-brown tabby cap on the head with a white blaze down the nose; striped back and tail; green eyes; pink nose and ear insides; and his defining mark, a white oval spot on the very top of the head, centred between the ears and separate from the muzzle white (see `reference/photos/white_spot_on_head.jpeg`).
- Starter gun: **Royal Kibble Sack** — a sack of Royal Canin style dry food that lobs kibble at enemies.
- Active item: **Wet Food Can** — a thrown can of wet food that makes every enemy near where it lands fall in love with Pluto (charmed: they fight for him). Must work on *all* enemy types, including bosses, which vanilla charm skips.

## 2. Research summary (details in `docs/research/`)

| Layer | Package | Version |
|---|---|---|
| Loader | BepInEx-BepInExPack_EtG | 5.4.2101 |
| Base API | MtG_API-Mod_the_Gungeon_API | 1.9.2 |
| Library | Alexandria-Alexandria | 0.5.10 |

Two ways to add a character exist. The **Custom Characters Mod** route is data-only but cannot add custom guns/items. Pluto needs both, so we use **Alexandria CharacterAPI** (C# plugin, art embedded in the DLL, `Loader.BuildCharacter`). Reference implementation: Once More Into The Breach's "Shade" character.

Reference assemblies come from the BepInEx NuGet feed (`EtG.GameLibs 2.1.9.1`, `EtG.UnityEngine 1.0.0`, `EtG.ModTheGungeonAPI 1.9.2`, `EtG.Alexandria 0.5.10`). Target `.NET 3.5`, old-style csproj. Verified: Mono 6.12 `msbuild` on this Mac compiles a plugin against them.

## 3. Architecture

```
PlutoTheCat/                      C# project (PlutoTheCat.csproj, net35)
  src/Plugin.cs                   BepInEx entry: registers gun + item, then builds character
  src/KibbleSackGun.cs            Gun definition (GunBehaviour)
  src/WetFoodCanItem.cs           Active item (SpawnObjectPlayerItem + CustomThrowableObject)
  src/PlutoCharmEffect.cs         Boss-proof charm effect
  Characters/Pluto/               characterdata.txt + all character art (embedded)
  Resources/SpriteRoot/           WeaponCollection/, ProjectileCollection/ (MtG API auto-load)
  Resources/Items/                wet_food_can icon + toss/splash frames
thunderstore/                     manifest.json, README.md, icon.png (256x256), CHANGELOG.md
tools/                            Python pixel-art generator (single source of truth for all art)
build.sh                          restore + msbuild + assemble thunderstore zip
```

Load order inside `GMStart`: sprites (`ETGMod.Assets.SetupSpritesFromAssembly`) → gun → item → `Loader.BuildCharacter`. Items must exist before the character's loadout is parsed.

## 4. Character

`characterdata.txt`:

```
base: Pilot
name: Pluto the Cat
name short: Pluto
nickname: Pluto
armor: 0

<loadout>
	pluto:kibble_sack infinite
	pluto:wet_food_can
</loadout>

<stats>
	Health: 3
	MovementSpeed: 7.5
	DodgeRollSpeedMultiplier: 1.1
</stats>
```

Base Pilot (no armor mechanics, standard 3 hearts). Slightly faster and a quicker roll because he is a cat. Foyer position: next to the other Gungeoneers (use the Shade's coordinates as a starting value; tune after in-game check).

### 4.1 Art spec

Canvas: **24 x 20 px** body frames: the 18-px-wide body sits at x=3 and the 3-px margins on each side hold the tail (Robot reference is 17x19; Pilot 23x24 includes gun). Pluto faces right in side sprites; the game mirrors for left. 16 px = 1 world unit.

Palette (hex): outline `1E1614`, white `FAF6EE`, white shade `D8D0C4`, tabby base `8E7150`, tabby dark `5A4028`, tabby light `B39473`, eye green `7DB447`, pupil `1B2A1B`, pink `E8A0B0`, tongue `D46A7A`.

Design: upright "Gungeoneer" proportions (big head, short body) but unmistakably Pluto: tabby cap with two ears, the white crown spot between the ears (present in every pose, including the roll ball, death poses, face card and icons), a white blaze, white cheeks and chest bib, tabby back, white paws, chunky belly, and a long raccoon-ringed tail (alternating light/dark bands, dark tip) that curls up behind him: on the left in side/front views, on the right in the back view, stretched flat on the floor when dead. The tail tip sways between two positions on idle and run frames.

Required animation folders (Alexandria `playerAnimInfo`) and how each is produced:

| Folder | Frames | Source |
|---|---|---|
| idle, idle_forward (front), idle_backward (back), idle_bw | 4 | hand-drawn key poses + breathing bob |
| *_hand, *_twohands (all) | placeholder | `cc_sprite_placeholder.png` → falls back to base folder |
| run_right, run_right_bw, run_down, run_up | 6 | key poses with leg cycle + bob |
| dodge, dodge_bw, dodge_left, dodge_left_bw | 9 | wind-up crouch, ball with ears+tail in four 90° tumbles, landing squash |
| death, death_shot | 8 / 6 | hit (mouth open), knees buckle, tip over, flat on side with X eyes |
| death_coop | placeholder | falls back to death |
| pitfall, pitfall_down, pitfall_return | 5 / 5 / 8 | shrink/drop and climb back |
| item_get, chest_recover | 9 / 7 | paws-up celebration |
| spinfall, timefall, spit_out, doorway | 6 / 8 / 6 / 5 | rotations / reuse of idle |
| ghost_idle_* (6 dirs), ghost_sneeze_left/right | 3 / 4 | desaturated translucent idle |
| jetpack_* (6, incl. hand placeholders), pet, slide_*, tablekick_* | 2-4 | idle/run derivatives |
| breach_idles/select_idle, select_choose | 4 / 6 | foyer idle + thumbs-up |
| hand_001.png | 4x4 | white paw |

UI art: `facecard.png` 34x34, `foyercard/` 38x38 (idle x4, appear x5), `bosscard_001.png` 427x240, `icon.png` 9x9, `win_pic_001.png` 115x71, `coop_page_death.png` 11x13, `loadoutsprites/a_kibblesack.png`, `b_wetfoodcan.png`. Punch-Out sprites are optional and skipped (the Rat fight will use base Pilot sprites).

All art is generated from ASCII pixel maps by `tools/make_art.py` so it is reproducible and editable.

## 5. Gun — Royal Kibble Sack (`pluto:kibble_sack`)

- Built with `ETGMod.Databases.Items.NewGun("Royal Kibble Sack", "pluto_kibble_sack")`, renamed to `pluto:kibble_sack`.
- Sprites: `pluto_kibble_sack_idle_001`, `_fire_001..003`, `_reload_001..004` in `WeaponCollection`, 26x16 px, each with a `.jtk2d` (PrimaryHand + Casing attach points; mandatory or `Gun.Initialize` null-refs). The bag is a Royal Canin Sterilised dry-food bag held sideways (white/silver body, five-dot crown, red ROYAL CANIN band, purple label with the grey cat), zip opening to the right with kibble spilling out. An upright 20x26 bag with the same sprite name in `Ammonomicon Encounter Icon Collection` is the Ammonomicon page picture; the long description carries Pluto's backstory with the bag. `barrelOffset` at the zip opening.
- Module cloned from Klobb (`AddProjectileModuleFrom("klobb", true, false)`) then overridden: semi-automatic, clip 10, cooldown 0.20 s, reload 1.0 s, angle variance 6, infinite ammo, `PreventStartingOwnerFromDropping`, `quality = EXCLUDED`, `gunClass = PISTOL`.
- Projectile: cloned via `ProjectileUtility.SetupProjectile(56)`, 8x8 triangular brown kibble sprite (`ProjectileCollection/pluto_kibble_001`), damage 5 (same per-shot as the Pilot's starter), speed 17, range 20, `shouldRotate = true` (pointy end forward), plus `BounceProjModifier` (1 bounce, 50 % speed loss) so kibble skitters like real kibble. No arc subclass: simplest robust path per research.

## 6. Active — Wet Food Can (`pluto:wet_food_can`)

- Class derives `SpawnObjectPlayerItem` (the vanilla Molotov pattern), registered with `ItemBuilder.AddSpriteToObject` + `SetupItem(..., "pluto")`. Icon 16x16.
- `objectToSpawn` = prefab with `CustomThrowableObject` (Alexandria ThrowableAPI): toss animation (spinning gold Royal Canin Kitten can with pink label, 4 frames), landing "splash" animation (burst can, gravy, hearts, 3 frames), `doEffectOnHitGround = true`, `tossForce = 12`. Prefab is made inactive with `FakePrefab.MakeFakePrefab`.
- On landing (`CustomThrowableEffectDoer.OnEffect`): for every `AIActor` in the room within 4 units, apply `PlutoCharmEffect` (duration 10 s, refresh stacking, pink tint, charm overhead VFX borrowed from Charming Rounds). Also play the charm sound.
- Cooldown: `ItemBuilder.CooldownType.Damage`, 250. Quality EXCLUDED (starter only), `consumable = false`.

### 6.1 Charming everything

`GameActor.ApplyEffect` silently drops any `GameActorCharmEffect` when the target `healthHaver.IsBoss`. `PlutoCharmEffect` therefore derives from **`GameActorEffect`** directly and replicates charm's four lines (`CanTargetEnemies = true; CanTargetPlayers = false;` and the reverse on removal). `effectIdentifier = "pluto_love"`, `resistanceType = None`, so charm resistance is not consulted either. Radius application is used instead of on-hit so the can does not need to physically hit a target. Known limit (from research, untested): some boss AIs may not honour `CanTargetPlayers`; that is accepted.

## 7. Packaging

`thunderstore/manifest.json`:

```json
{
  "name": "Pluto_The_Cat",
  "version_number": "1.0.0",
  "website_url": "",
  "description": "Adds Pluto the Cat as a playable Gungeoneer, with his Royal Kibble Sack and a Wet Food Can that makes enemies fall in love.",
  "dependencies": [
    "BepInEx-BepInExPack_EtG-5.4.2101",
    "MtG_API-Mod_the_Gungeon_API-1.9.2",
    "Alexandria-Alexandria-0.5.10"
  ]
}
```

Zip layout: `manifest.json`, `README.md`, `CHANGELOG.md`, `icon.png` (256x256), `plugins/PlutoTheCat.dll`. `build.sh` produces `dist/Pluto_The_Cat-1.0.0.zip`. r2modman: Settings → Import local mod → pick the zip.

## 8. Testing

- Build passes on Mono msbuild (verified toolchain).
- Static checks: every required animation folder present; every PNG dimension matches spec; `characterdata.txt` item ids match the registered ids; embedded resource paths match the loader's expected `RootNamespace/Characters/Pluto/...` layout.
- In-game verification cannot happen on this Mac (game not installed). The README documents a checklist: character appears in the Breach, sprites render in all directions, gun fires kibble, can charms a boss, no red errors in the BepInEx console.

## 8b. Version 2 additions (2.0.0 – 2.1.0)

Nine Lives passive (`pluto:nine_lives`, ModifyDamage hook cancels a lethal hit while Pluto is not yet on his ninth life; he starts on his seventh, `StartingLife` in config, so two saves per run); cat reflexes (roll distance 1.15, 6 invulnerable frames, DodgeRollDamage 3); Royal Kibble Sack fires two kibble with a 1-in-20 chunk and floor crumbs; Wet Food Can applies 1.2x damage vulnerability, stuns bosses for 3 s; synergies via `CustomSynergies` (ids validated against `docs/research/gungeon_items_idmap.txt`); Wet Pluto alt skin (recolour, bathtub swapper); breach idles loaf/groom/knock; co-op death ghost; tail whip on `OnRolledIntoEnemy`; zoomies StatModifier after `OnRoomClearEvent`; hairball on empty-clip reload; hand-variant clips with an extended arm. All tunables live in `PlutoConfig` bound to `BepInEx/config/bogdan.etg.plutothecat.cfg`. Every load step runs through `Plugin.Step` so optional features cannot block the character. `pluto_check.sh` ships in the package for log verdicts.

## 8c. Version 2.2 additions

Coco Blue (`pluto:coco_blue`, `CompanionItem` + `CompanionBuilder` prefab, `CompanionFollowPlayerBehavior`, drops a crumb on owner damage); Royal Canin Gravy Pouch (`pluto:gravy_pouch`, the `<altGuns>` entry, 20 % charm on hit); kibble bowl pickup (20 % drop from enemies that die charmed, heals 0.5); Nine Lives banner via `UINotificationController.DoCustomNotification` + fur-puff `VFXPool` (Alexandria `VFXBuilder`); love-burst pool at the can splash; select-card pop-in frames. Art sources: `tools/art_v3.py` (face, bag, can) and `tools/art_v4.py` (Coco, pouch, bowl, VFX). No Hegemony cost.

## 8d. Art passes A–C (2.9.0 – 2.10.1)

Driven by `docs/research/03-hand-drawn-art-improvement-plan.md`. Body frames ship without a baked
outline (the game adds it at runtime; verified in the decompiled `PlayerController.Start`, which calls
`SpriteOutlineManager.AddOutlineToSprite` with the "Brave/Internal/SinglePassOutline" shader). Canvas
24x26 with the pose at (3, 4): 4 px headroom for the vanilla 4-px run hop, feet fill on row 24, 1-px
margin on every side for the outline. Palette re-tuned from the photos (grey-brown taupe, hue-shifted
ramps, near-black stripes/rings, hazel eyes); one head part per view (side, front, back, back-view
side) with the tabby mask, blaze and crown spot; hand-placed shadows instead of the rim pass.
Animation keys: idle squash + ear flick, run with head lag and ears back, dodge with stretched leap
and overshoot, death with the tail dropping last, vanilla pit blips, hand-drawn slide; hand variants
show the free paw(s) per the game's `_hand`/`_twohands` semantics. Tooling: strict `pad`/`overlay`,
`tools/lint_art.py` in the build, `tools/preview.py` with the runtime outline simulated,
`tools/import_png.py`, project skill `.claude/skills/pluto-pixel-art/`.

## 9. Out of scope

Alt skin, custom past, Punch-Out sprites, synergies, custom sounds, localisation.
