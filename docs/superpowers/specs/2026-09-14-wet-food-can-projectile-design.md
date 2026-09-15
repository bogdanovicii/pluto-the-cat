# Wet Food Can 2.0: thrown projectile — design

> **Historical: design shipped in Pluto the Cat 2.14.0.** Current behaviour: `thunderstore/CHANGELOG.md`.

Date: 2026-09-14 · Status: approved in chat · Main mod (PlutoTheCat), version after 2.13.0

## Goal
Pluto's starter active stops being a lobbed Molotov and becomes a tin he throws at an enemy. A direct hit
charms that enemy; the can always bursts where it stops and charms enemies in a small splash. New art based
on `reference/ideas/active_item_idea.png` (Royal Canin Kitten, thin slices in gravy).

## Behaviour
| Case | Effect |
|---|---|
| Use | Spawns the can projectile at Pluto's centre toward the aim point. Speed 14, range 10 tiles, no pierce, tumbles (4-frame animation). |
| Direct hit, regular enemy | `CanDamage` (5) damage, then `PlutoCharmEffect` for `CharmDuration` (10 s, +20 % damage taken). |
| Burst (enemy hit, wall, or max range) | Gravy burst VFX + love burst at the impact point; every non-boss enemy within `CanSplashRadius` (2 tiles) of it gets the same charm. The directly hit enemy is not charmed twice. |
| Boss (hit or splash) | `behaviorSpeculator.Stun(BossStunSeconds)` (3 s), no charm (unchanged). |
| Dinner Time synergy (owned by PlutoSynergies, read only) | Splash radius ×1.5, charm duration ×2 (unchanged rule). |
| Cooldown | Damage cooldown `CanCooldownDamage` (200), not consumable (unchanged). |

## Build
- `WetFoodCanItem` derives from `PlayerItem` (was `SpawnObjectPlayerItem`). `DoEffect(user)` spawns the prefab
  with `SpawnManager.SpawnProjectile`, sets `Owner`/`Shooter`, calls `user.DoPostProcessProjectile`, plays the
  throw sound. Same pattern as the hairball in `KibbleSackGun`.
- Prefab: `ProjectileUtility.SetupProjectile(56)` clone, damage `CanDamage`, speed 14, range 10,
  `shouldRotate = false`, animated sprite from the four `wet_food_can_toss_00N` frames.
- A `WetFoodCanBurst` component: `OnHitEnemy` charms/stuns the hit target and remembers it; `OnDestruction`
  runs the splash exactly once (guard flag) at the projectile's last position.
- Config: `CharmRadius` is replaced by `CanSplashRadius` (default 2.0); new `CanDamage` (default 5).
  `CharmDuration`, `BossStunSeconds`, `CanCooldownDamage` stay.
- Item id `pluto:wet_food_can`, GameObject name "Wet Food Can", loadout entry: unchanged, so the character data
  and the Dinner Time synergy keep working.

## Art (hand-drawn row strings in `tools/art_v3.py`)
- Icon / loadout sprite: short wide gold tin with a ring-pull lid, pink label around a white panel, crown over a
  red band, pink KITTEN strip, window of gravy chunks. Outlined (items keep drawn outlines).
- Toss (4 frames, 16x16, square so rotations never drift): label side, lid toward camera, other side, bottom.
- Burst VFX (3 frames): lid pops off, brown gravy splat with meat chunks, hearts rise.
- Checked at 1x and 10x in previews before the build.

## Coordination
Another session is editing synergies. This work does not touch `PlutoSynergies.cs`; it only reads
`PlutoSynergies.DinnerTime`. Files touched: `WetFoodCanItem.cs`, `PlutoConfig.cs`, `PlutoVFX.cs` (only if the
burst VFX needs registering), `tools/art_v3.py`, `tools/make_art.py`, `tools/validate.py`, changelog.

## Verification
`tools/validate.py`, `./build.sh` (log to file, check status), preview sheet. In-game checklist for the Steam
machine: hit charms, miss into wall bursts, splash radius, boss stun, cooldown refills, Dinner Time.
