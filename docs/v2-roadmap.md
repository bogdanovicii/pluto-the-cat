# Pluto the Cat — version 2 roadmap

> **Historical (roadmap written after 1.0.1).** Kept for context; much of it shipped in a different form (Wet Pluto was later retired for Samurai Pluto). Current state: `README.md` and `thunderstore/CHANGELOG.md`.

Goal: make Pluto feel as complete as a vanilla Gungeoneer (starting passive, personality in the Breach,
alt skin, synergies, a past) while sitting a notch above the vanilla power curve. Everything below is
achievable with Alexandria 0.5.10 (CharacterAPI + ItemAPI) and MtG API; effort is estimated in build
sessions of a few hours.

## 1. The identity kit (what every vanilla character has)

| Vanilla feature | Pluto version | How | Effort |
|---|---|---|---|
| Starting passive | **Nine Lives** (see §2) | Alexandria `PassiveItem` + loadout line | S |
| Alt skin (paradox/costume swap in the Breach) | **Wet Pluto** (after a bath: flattened fur, grumpy face) or **Tuxedo Pluto** | `hasAltSkin = true`, `newaltspritesetup/` full clip set (art pipeline already generates clips, add a recolour pass) | M |
| Breach idle animations | stretch, loaf, groom, chase-a-fly, knock-something-off-a-table | `breach_idles/<name>/` folders (already supported; we ship 3 now) | S |
| Punch-Out (Rat fight) sprites | Pluto boxing the Resourceful Rat | `punchout/sprites/` with Alexandria's clip list; ~20 clips at 34x59 | L |
| Custom past | **The Vet Visit**: Pluto's past is the carrier crate and the examination table; boss is The Vet with a syringe gun | `hasCustomPast = true` needs a whole room + boss; realistic alternative: reuse the Pilot past with a custom win text | XL (or S for text only) |
| Win pictures | already have one; add the Junkan variant and an alt-skin variant | PNG only | S |
| Voice / sounds | cat meow on item pickup, purr on room clear, hiss on damage | `AkSoundEngine` custom banks are hard; MtG API can play WAVs via `ETGMod.Assets`? fallback: reuse vanilla dog/cat-like events | M |
| Unlock condition | "Feed the Dog five times" or "Beat the Rat as any character" (cat vs rat) | Alexandria `CustomDungeonFlags` + `SetupUnlockOnCustomFlag`; also `metaCost` in Hegemony credits | M |

## 2. Power budget: "balanced but a bit overpowered"

Vanilla baseline: 3 hearts, starter gun ~5 dmg, one passive or active. Overpowered-but-fair means one
extra strong mechanic, not everything at once. Suggested kit:

**Nine Lives (starting passive)** — Pluto starts with 3 hearts but has a hidden pool of 9 lives on the
first floor of each run: the first time he would die on a floor, he instead revives at 1 heart with a
puff of fur and loses one life. Lives do not refill. Shown as small paw icons under the health bar.
This is the "a bit OP" piece: it is a Clone/Elder Blank style safety net, but finite. Implementation:
`PassiveItem` with a hook on `HealthHaver.OnPreDeath` (Alexandria has `CustomActions.OnPlayerAboutToDie`
style hooks). Tunable: 9 → 3 lives per run if it feels too strong.

**Cat reflexes (stats)** — keep MovementSpeed 7.5 and roll speed 1.1, add `DodgeRollDistanceMultiplier 1.15`
and 2 extra invulnerable roll frames (Alexandria marks the first half of dodge frames; we can mark 6 of 9).
Pluto is the "get out of the way" character.

**Royal Kibble Sack upgrades**
- Fires 2 kibble per shot at slight spread (shotgun-lite) with damage 3.5 each: same DPS as now against
  single targets, better against groups.
- Kibble that lands on the floor stays as a pickup for 8 s; walking over it heals nothing but gives
  +1 ammo to the currently held non-starter gun ("crumbs"). Small, flavourful, not broken.
- Reload animation with a paw digging in the bag; a "critical kibble" 1-in-20 big chunk that does 12 dmg.

**Wet Food Can upgrades**
- Charmed enemies also take 20 % more damage from Pluto while charmed (they are distracted).
- Bosses: instead of a full charm, the can *stuns* a boss for 3 s and charms its minions (makes the
  boss-charm behaviour predictable rather than AI-dependent).
- Cooldown from 250 damage to 200.

**Synergies** (Alexandria `SynergyBuilder`, easy and very "vanilla"):
- *Complete Feline Nutrition*: Kibble Sack + any "food" item (Gungeon Pepper, Bloody Eye, Orange...) →
  kibble homing.
- *Dinner Time*: Wet Food Can + Charming Rounds or Charm Horn → charm lasts 20 s and spreads once.
- *Laser Pointer*: Kibble Sack + any laser gun → Pluto's dodge roll leaves a red dot that enemies chase.
- *Box Fort*: Pluto + Cardboard Box → the box is permanent and enemies never notice him inside.

## 3. Personality and polish

- **Breach dialogue**: custom idle lines when you stand next to him ("...") and a unique select sound.
- **Pet interaction**: Pluto can be petted by the other player in co-op (the `pet` clip exists) and
  refuses to be petted by the Convict.
- **Hurt/blank feedback**: unique blank VFX with a spray of fur; hiss sound on damage.
- **Cat things in rooms**: 2 % chance a room has a cardboard box Pluto can sit in for a free blank.
- **Ammonomicon bio** for Pluto himself (the game shows one per character; Alexandria supports it via
  the string table).
- **Art**: `_hand` / `_twohands` clip variants drawn properly (arm removed so the gun hand attaches
  cleanly), 2-frame tail sway on every clip, a proper `death_coop` (ghost hovering over the body).

## 4. Suggested order

1. Confirm 1.0.1 works in-game; fix hand attach points and foyer position from screenshots.
2. Nine Lives passive + stat tune (the power piece).
3. Synergies (cheap, high "vanilla feel").
4. Breach idles + alt skin (art pipeline already exists; mostly recolours and 3 new poses).
5. Unlock condition + Hegemony cost.
6. Punch-Out sprites, sounds, custom past — only if still hungry.
