# The Vet Visit — Pluto's custom past (design spec, DRAFT awaiting approval)

Status: draft, 2026-09-13. Nothing is built yet. Research behind every claim: `docs/research/03-alexandria-custom-past.md`,
`04-past-level-and-dungeonapi.md`, `05-custom-boss-research.md`.

## 1. Goal

Give Pluto a real past, like every vanilla Gungeoneer: after the Lich, the Gun That Can Kill The Past sends him to
**The Vet Visit**, one room (a veterinary clinic) with one boss (**The Vet**, a doctor with a syringe gun). Beating the Vet
"kills the past": the vanilla past-killed flag is set for Pluto, the credits tube plays, the win page shows a Pluto
win picture, and the Breach card shows Past Killed.

The work happens in a **separate project** (`PlutoVetVisit/`) that never touches `PlutoTheCat/`, `tools/`,
`thunderstore/` or `build.sh`. Another session is editing the main mod right now. The past is merged into the main mod
only when it is finished and verified in game (section 12).

## 2. Story

Pluto's regret is the day he was taken to the clinic as a kitten. He has eaten "Sterilised 37" ever since. In the past
he arrives in his carrier, The Vet greets him ("Just a little snip. You won't feel a thing."), and Pluto refuses.
Boss card: **THE VET — Doctor's Orders**. Win picture: Pluto sitting on the exam table, the Vet on the floor, the cone of
shame kicked into a corner. The dialogue lines are placeholders; they are the user's to rewrite (section 13).

## 3. How a custom past works (verified against the shipped Alexandria 0.5.10 DLL)

- `Loader.BuildCharacter(..., hasCustomPast, customPast)` only stores two public fields on the character prefab's
  `CustomCharacter` component (`past`, `hasPast`) and `CustomCharacterData.hasPast`. Nothing else in Alexandria uses them.
- `hasPast` makes the Blacksmith hand Pluto the Bullet That Can Kill The Past (Harmony prefix on `TalkDoerLite.Start`).
- When the Gun fires in the Ark, Alexandria's IL patch on `ArkController.HandleClockhair` calls
  `GameManager.Instance.LoadCustomLevel(cc.past)`. So `customPast` must be the `dungeonSceneName` of a
  `GameLevelDefinition` that the mod itself has added to `GameManager.customFloors`.
- `LoadCustomLevel` loads the dungeon through `DungeonDatabase.GetOrLoadByName(dungeonPrefabPath)`, which the mod hooks
  to return a runtime-built `Dungeon`.
- The ending is entirely the mod's job: set `KILLED_PAST` for Pluto's identity, register the stat, run the credits tube,
  open the win Ammonomicon. Modular (Some Bunny) and Enter the Beyond ship pasts exactly this way.
- Both fields are read lazily, so a second plugin can attach the past after the character is built:
  `CharacterBuilder.storedCharacters["playerpluto"]` gives the data and prefab. This is what makes the separate project possible.

## 4. Project layout

```
PlutoVetVisit/
  PlutoVetVisit.csproj      net35, RootNamespace/AssemblyName PlutoVetVisit, same package references as PlutoTheCat
  packages.config, nuget.config   copies; packages restore into PlutoVetVisit/packages
  build.sh                  art -> restore -> msbuild -> validate -> dist/Pluto_Vet_Visit-<version>.zip
  src/
    PastPlugin.cs           BepInEx plugin (GUID bogdan.etg.plutovetvisit). Depends on bogdan.etg.plutothecat at RUNTIME only.
    PastConfig.cs           BepInEx config: Enabled, BossHealth, BossDpsCap, BossMusic, RoomVisualSubtype, SkipIntro (debug)
    PastLevel.cs            GameLevelDefinition + Harmony patches (DungeonDatabase.GetOrLoadByName, GameManager.LoadCustomLevel)
    VetFlow.cs              the one-node DungeonFlow (+ GenerateDefaultNode helper)
    ClinicRoom.cs           loads Resources/Rooms/vet_clinic.newroom, forces category ENTRANCE, registers custom objects
    ClinicObjects.cs        carrier, exam table, cabinets, scale: sprite + collider prefabs in StaticReferences.customObjects
    VetBoss.cs              BossBuilder prefab, stats, hurtbox, clips, bullet bank, behaviours, intro doer, death handler
    VetAttacks.cs           Brave.BulletScript scripts: BoosterShot, SprayBottle, PillTime, ConeOfShame
    VetVisitController.cs   the past controller: fade-in, dialogue, boss trigger, ending sequence
  Resources/
    Rooms/vet_clinic.newroom            generated JSON (RoomFactory.RoomData)
    Boss/vet/{idle,move,tell,fire,intro,die}/vet_<clip>_NNN.png, Boss/vet_bosscard.png (427x240)
    Objects/*.png, Projectiles/*.png, past_win_pic.png (115x71)
  tools/
    palette.py              imports ../../tools/pixel.py read-only (same palette + helpers) and adds clinic colours
    vet_poses.py            ASCII pixel maps for The Vet (single source of truth, like tools/poses.py)
    clinic_room.py          ASCII cell map of the room -> vet_clinic.newroom + docs preview
    objects.py, cards.py    room objects, boss card, win pic
    make_art.py, validate.py
  thunderstore/manifest.json, README.md, CHANGELOG.md, icon.png   test package (depends on Pluto_The_Cat)
  docs/checklist.md         in-game test checklist per milestone, expected log lines
  vet_check.sh              greps the BepInEx log, prints PASS/FAIL (same idea as pluto_check.sh)
```

No compile-time reference to `PlutoTheCat.dll`. Pluto is found through Alexandria (`storedCharacters["playerpluto"]`,
`data.identity` for the `PlayableCharacters` value). If Pluto is missing the plugin logs one line and does nothing.

## 5. Level plumbing (`PastLevel`)

1. `Definition = new GameLevelDefinition { dungeonSceneName = "tt_pluto_past", dungeonPrefabPath = "base_pluto_past",
   priceMultiplier = 1, secretDoorHealthMultiplier = 1, enemyHealthMultiplier = 1, damageCap = -1, bossDpsCap = config,
   flowEntries = [], predefinedSeeds = [] }` — the vanilla `fs_soldier` row uses exactly these numbers (caps -1).
2. Added to `GameManager.Instance.customFloors` and to the `_GameManager` prefab's list (`brave_resources_001`), because a
   fresh GameManager copies its lists from the prefab when you return to the Breach. A Harmony prefix on
   `GameManager.LoadCustomLevel` re-adds it if missing (GungeonCraft's fix).
3. Harmony prefix on `DungeonDatabase.GetOrLoadByName`: for `base_pluto_past` it loads `FinalScenario_Soldier` (the
   Marine's Primerdyne lab: white clinical tiles, `LevelOverrideType = CHARACTER_PAST`, `tilesetId = FINALGEON`,
   `PrefabsToAutoSpawn = []`, ending music already set) through the original method and returns it with
   `PatternSettings.flows = [VetFlow]`, floor name strings replaced.
   Template hygiene: the loaded prefab is a shared asset, so the original `flows` list and names are saved and restored
   by a postfix whenever `FinalScenario_Soldier` itself is requested (playing the Marine past later in the same session
   must still work). Fallback if the Soldier prefab misbehaves: clone `Base_ResourcefulRat` and copy the Soldier's
   tile fields, as Modular does.
4. `tilesetId == FINALGEON` is what makes Alexandria show `CustomCharacterData.pastWinPic` on the win page.
5. The plugin sets on Pluto: `cc.past = "tt_pluto_past"; cc.hasPast = true; data.hasPast = true; data.pastWinPic = texture`.

## 6. Flow (`VetFlow`)

`SampleFlow.CreateNewFlow(template)` (Alexandria helper: fallback/phantom/evolved tables from the template's first flow,
empty injection lists, `Initialize()`), then one node from the copied `GenerateDefaultNode` helper:
`roomCategory = ENTRANCE, overrideExactRoom = ClinicRoom.Room, priority MANDATORY`, `FirstNode = node`.
Vanilla ships single-room flows (`Testing/Single Room Demonstration Flow`). If generation rejects one node, the fallback
is a second sealed node using the stock `exit_room_basic` room.

## 7. The room (`ClinicRoom`, `clinic_room.py`)

- Drawn as an ASCII cell map in Python (top row first, flipped on export because the loader indexes `tileInfo[x + y*width]`
  with y = 0 at the bottom). Legend follows Alexandria's `.newroom` reader: `2` wall, `1` floor, `3` pit, `X` floor with
  no pickups, `6-9` diagonal walls. About 26 x 18 cells: waiting area with the carrier at the south, exam table in the
  middle, cabinets along the north wall, a scale and a poster as decor.
- Exported to `Resources/Rooms/vet_clinic.newroom` with `category "ENTRANCE"`, `floors []` (so `DungeonHandler.Register`
  does not push it into any vanilla room table), `visualSubtype` from config, one south exit (unused, harmless) and
  the placeables list referencing custom object names.
- Loaded with `RoomFactory.BuildNewRoomFromResource(...)`, then `room.category = ENTRANCE` is forced in code (the guide's
  warning) and `room.name = "pluto_vet_clinic"`.
- Custom objects (`ClinicObjects`): GameObjects with a `tk2dSprite` from an embedded PNG and a `SpeculativeRigidbody`
  with one manual `PixelCollider`: cabinets and carrier on `HighObstacle` (block everything), exam table on `LowObstacle`
  (blocks walking, bullets fly over it, so the Vet shoots across it). Registered in `StaticReferences.customObjects`
  under `pluto_carrier`, `pluto_exam_table`, `pluto_cabinet`, `pluto_scale`; made fake prefabs with
  `FakePrefab.MakeFakePrefab` so they do not run until placed.
- The past controller is also a placed custom object (`pluto_past_controller`, empty GameObject + component), so it starts
  with the room and needs no extra hook.
- The boss is NOT placed by the room. The controller spawns it after the dialogue (section 9), which avoids a dormant
  boss acting before its intro.
- Player start: the game puts the player at the entrance room's centre cell; the controller moves him next to the carrier
  during the fade-in (`transform.position` + `specRigidbody.Reinitialize()`, the vanilla Marine past does the same).

## 8. The boss (`VetBoss`, `VetAttacks`)

Built with `BossBuilder.BuildPrefab("The Vet", GUID, idle frame, hitboxOffsetPx, hitboxSizePx, HasAiShooter: false)` and
the fixes the research found are mandatory in 0.5.10:
- real HP (`ForceSetCurrentHealth` + `SetHealthMaximum`, default 1200 from config), `bossHealthBar = MainBar`
  (health bar, kill cam, boss DPS rules), `overrideBossName = "The Vet"`, knockback weight 200;
- a second `PixelCollider` on `EnemyHitBox` (player bullets do not hit the `EnemyCollider` the builder makes);
- `bs.AttackBehaviors` replaced wholesale (the Fungun template's attacks survive otherwise).

Clips, one folder per clip, zero-padded, right-facing only, left = `FlipType.Flip` (TwoWayHorizontal):
`idle` 4f, `move` 6f, `tell` 3f, `fire` 3f, `intro` 8f, `die` 10f. Canvas 32 x 40 px, feet on the same row.
`HitReactChance = 0`, `overrideDeathAnimation = "die"`.

Bullet bank: `CopyBulletBankEntry(BulletKin "default", "syringe", "DNC")`, same for `droplet`, `pill`. Custom projectile
sprites are a polish step (section 11); until then the vanilla bullet sprite is used.

Behaviours: `TargetPlayerBehavior`; `MoveErraticallyBehavior` (the Vet paces behind the table); one `AttackBehaviorGroup`:

| Attack | Script | Pattern | Phase |
|---|---|---|---|
| Booster Shot | `BoosterShotScript` | 3 aimed syringes, 8 frames apart, fast | always |
| Spray Bottle | `SprayBottleScript` | 9-droplet fan over 80 degrees, twice, slow | always |
| Pill Time | `PillTimeScript` | 4 slow pills that split into 6 after 40 frames (bullet `Top()` fires children) | always |
| Cone of Shame | `ConeOfShameScript` | ring of 16 bullets, then a second ring offset by half a step | below 50 % HP (`MaxHealthThreshold = 0.5`) |

Below 50 % HP every cooldown is scaled by 0.7 (a second group item with a lower `MaxHealthThreshold`).

Intro: `GenericIntroDoer` with `triggerType = BossTriggerZone` (never auto-triggers), `introAnim = "vet_intro"`,
`BossMusicEvent` from config (default `Play_MUS_Boss_Theme_Beholster`), `portraitSlideSettings` with the 427 x 240 card,
`HideGunAndHand = true`. `OnIntroFinished` re-enables the AI.

Death: `ExplodeOnDeath` with a harmless force-only explosion, `die` clip, and `VetDeathHandler` (`healthHaver.OnPreDeath`
subscribed on the instance) that calls `VetVisitController.OnBossDied()`.

Console id `pluto:the_vet` (`Gungeon.Game.Enemies`) so the boss can be spawned in any room for testing.

## 9. Past controller and ending (`VetVisitController`)

Modelled on `PastLabMarineController` / `PilotPastController`:

```
Start():  wait Dungeon.IsGenerating; SaveManager.DeleteCurrentSlotMidGameSave()  (the Ark wrote a resume save the game
          cannot load for a custom character); move player(s) beside the carrier; Pixelator.TriggerPastFadeIn();
          SetInputOverride("past"); PastCameraUtility.LockConversation(table centre);
          spawn The Vet behind the table with AIActor.Spawn(prefab, pos, room, true, Default, autoEngage: false),
          AI disabled + PreventAllDamage while talking;
          TextBoxManager.ShowTextBox(...) x 2-3 lines (timed, skippable with SkipIntro config);
          PastCameraUtility.UnlockConversation(); ClearInputOverride;
          vet.GenericIntroDoer.TriggerSequence(player)  -> walk-in, card, health bar; OnIntroFinished enables the AI.
OnBossDied(): SetCharacterSpecificFlag(plutoIdentity, KILLED_PAST, true); RegisterStatChange(TIMES_KILLED_PAST, 1);
          wait 3.5 s (death clip + kill cam); lock camera on Pluto; one line; Pixelator.FreezeFrame + time scale 0
          for ConvictPastController.FREEZE_FRAME_DURATION; new TimeTubeCreditsController().ClearDebris();
          HandleTimeTubeCredits(player.sprite.WorldCenter, false, null, -1); AmmonomiconController.OpenAmmonomicon(true, true).
```

The flag must be set before the tube so it shows the "past complete" panel. Co-op: the second player is moved and
input-locked too; nothing else special. Alexandria has no save API in 0.5.10, so `KILLED_PAST` persistence for the
extended enum is a checklist item, not assumed.

## 10. Config and debugging

`BepInEx/config/bogdan.etg.plutovetvisit.cfg`: `Enabled`, `BossHealth`, `BossDpsCap`, `BossMusic`, `RoomVisualSubtype`,
`SkipIntro`, `IntroLines` (three strings). In-game shortcuts that need no code: MtG console `load_level tt_pluto_past`
jumps straight into the past from the Breach; `spawn pluto:the_vet` tests the boss anywhere. `vet_check.sh` greps the
log for `[VetVisit]` lines and prints a verdict.

## 11. Art (all ASCII maps, regenerated by `tools/make_art.py`)

The Vet (6 clips, ~34 frames at 32 x 40), boss card 427 x 240 (composed with PIL from a large face + text, like the
existing `boss_card()`), win picture 115 x 71, room objects (carrier 32 x 24, exam table 48 x 32, cabinet 32 x 40,
scale 16 x 16, poster 16 x 24), projectiles (syringe 8 x 4, droplet 4 x 4, pill 6 x 4) for the polish milestone, and a
room preview PNG rendered from the cell map in `PlutoVetVisit/docs/preview/`.

## 12. Milestones (each ends with a test zip for the Steam machine and a checklist)

1. **Plumbing.** Project builds. Blacksmith gives Pluto the Bullet. `load_level tt_pluto_past` loads an empty lab-tiled
   room, fades in, and a timer triggers the full ending: flag, credits tube, win page with Pluto's win picture, Breach
   card says Past Killed. This retires the three biggest unknowns (Ark hook, level loading, ending) before any art exists.
2. **Clinic.** ASCII room, custom objects, player start beside the carrier, intro dialogue.
3. **The Vet.** Boss with Booster Shot and Spray Bottle, intro card, health bar, death triggers the ending.
4. **Polish.** Pill Time, Cone of Shame and the phase-2 tempo, projectile sprites, final boss card and win picture,
   music choice, balance pass, mid-game save hygiene verified, README/CHANGELOG.
5. **Integration** (separate approval): either move `src/` and `Resources/` into `PlutoTheCat/` (namespace change, one
   `Step("past", ...)` in `GMStart`, `hasCustomPast: true, customPast: "tt_pluto_past"`) or ship `PlutoVetVisit.dll` as a
   second plugin in the same package. Recommendation: merge, one DLL.

## 13. Decisions for the user (defaults in bold)

1. Story and lines: **the snip** premise and the placeholder dialogue, or something else.
2. Attack set: **the four above**, or swap one (e.g. a thermometer, a towel-burrito grab).
3. Room look: **Marine lab tiles** (`FinalScenario_Soldier`) or the R&G Department office tiles (`Base_Nakatomi`).
4. Where the user wants to write code themselves (optional): the `Top()` of one bullet script, the room ASCII map, the lines.
5. Integration path at the end: **merge into one DLL** or second DLL.

## 14. Risks (from the research, with the mitigation in the plan)

- Alexandria's Ark IL patch silently falling through to the plain win screen on the user's build: milestone 1 tests it first.
- Lab tiles not looking like a clinic: `RoomVisualSubtype` config, objects carry the theme, Nakatomi as plan B.
- Mid-game save resume into nothing: deleted on arrival.
- `KILLED_PAST` for an extended enum not persisting: checked in milestone 1; if it fails, mirror the flag in the config file.
- Single-node flow rejected by the generator: two-node fallback.
- Nothing can be run on this Mac; every milestone needs the Steam machine loop.

## 15. Out of scope

Custom sounds, an Ammonomicon page for the Vet, Punch-Out, Hegemony cost, co-op-specific cutscene, a second room.
