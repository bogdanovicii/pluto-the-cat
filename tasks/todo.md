# Pluto the Cat mod — task list

- [x] Research custom character creation (docs/research/01)
- [x] Research custom gun / active / charm (docs/research/02)
- [x] Verify Mono msbuild + NuGet toolchain compiles against EtG assemblies
- [x] Write design spec (docs/superpowers/specs/2026-09-13-pluto-the-cat-design.md)
- [x] Art generator: palette + base poses (idle side/front/back)
- [x] Art generator: run cycles, dodge roll, death, pitfall, item_get, misc clips
- [x] Art generator: ghost, jetpack, slide, tablekick, breach idles, hand
- [x] Art generator: facecard, foyercard, bosscard, minimap icon, win pic, coop death, loadout sprites
- [x] Art generator: gun sprites (idle/fire/reload) + .jtk2d attach points, kibble projectile
- [x] Art generator: wet food can icon, toss + splash frames
- [x] C#: csproj + packages + Plugin.cs
- [x] C#: KibbleSackGun.cs
- [x] C#: PlutoCharmEffect.cs + WetFoodCanItem.cs
- [x] characterdata.txt
- [x] build.sh + thunderstore manifest/README/icon → zip
- [x] Static validation script (folders, sizes, ids, embedded resources)
- [x] Round 2: better dodge roll + death poses, Royal Canin bag/can/kibble art from references, Ammonomicon page + story, stat pass
- [x] Round 3: white crown spot between the ears on every pose, face card and icons
- [x] Round 4: long raccoon-ringed tail with dark tip on a 24x20 canvas; sways on idle/run, flat on death
- [x] In-game test 1 (Steam Machine, SteamOS/Proton): DLL loads, character build failed (altGun NULL) → fixed in 1.0.1
- [ ] In-game test 2 with 1.0.1: character builds, Breach, gun, can
- [x] v2 phase 1: Nine Lives passive, cat reflexes, kibble x2 + crit + crumbs, can vulnerability + boss stun, 4 synergies
- [x] v2 phase 2: Wet Pluto alt skin, breach idles (loaf/groom/knock), co-op death ghost, bathtub swapper
- [x] 2.0.2: synergy id fix (guessed ids) + per-synergy try/catch + id validation
- [x] 2.0.3: run cycle on the vanilla hop rhythm, short trot stride
- [x] 2.1.0: BepInEx config file, isolated load steps, pluto_check.sh, tail whip / zoomies / hairball, hand-variant sprites
- [x] 2.1.1: v3 art pass (frame-filling shaded face, composed bag/can), hairball hook fix
- [x] 2.2.0: Coco Blue companion (CompanionBuilder), gravy pouch alt gun, kibble bowl drops, Nine Lives banner + fur puff, love burst VFX, select-card pop-in
- [x] 2.3.0: Puffed Up anger passive (scale + fur halo attached like a hat + anger marks + stat mods)
- [x] 2.3.1: bigger fur halo
- [x] 2.4.0: Coco Blue pettable (CanBePet + pet clip), hearts + 3 s speed on pet
- [x] 2.4.1: rim-shading pass on all body frames, Nine Lives mid-run save, capped speed boosts, guarded Puffed Up trigger
- [ ] 2.5: Punch-Out sprites once the Steam machine logs the Pilot's punchout sprite names
- [ ] git init + tag releases (user has not asked yet)
- [ ] v2 later: custom sounds (Alexandria SoundAPI needs Wwise soundbanks), custom past, Hegemony unlock cost

## Review

Built and validated on 2026-09-13. `./build.sh` → `dist/Pluto_The_Cat-1.0.0.zip` (DLL 132 KB, 267 embedded PNGs).

What was verified:
- Compiles against the real game assemblies (EtG.GameLibs 2.1.9.1, Alexandria 0.5.10, MtG API 1.9.2) with zero errors.
- Embedded resource names match what Alexandria CharacterAPI (`PlutoTheCat.Characters.Pluto.…`) and the MtG API sprite loader (`PlutoTheCat.Resources.SpriteRoot.<Collection>.<name>.png`) look for.
- All 61 animation clip folders present, every real frame 24x20, placeholders only where Alexandria has a fallback.
- Gun frames each have a `.jtk2d` with a PrimaryHand attach point (Gun.Initialize null-refs without one).
- Loadout ids in characterdata.txt match the ids registered in C#.

Not verified (needs the game): sprite anchoring in-game, foyer position, gun hand placement, charm on bosses.

Risks / notes:
- `PlutoCharmEffect` derives from `GameActorEffect` (not `GameActorCharmEffect`) to bypass the boss gate. Some boss AIs may ignore `CanTargetPlayers = false`; if a boss just idles, that is expected vanilla behaviour of charm on non-standard AI.
- Punch-Out (Rat fight) uses the base Pilot body sprites; only the face cards are Pluto's.
- Foyer position (14.6, 22.1) is a guess; tune in `Plugin.cs`.
