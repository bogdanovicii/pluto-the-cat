# The Vet Visit v2 — a past with the depth of a vanilla one (design)

> **Historical: v2 design draft (2026-09-14), built out across Vet Visit 0.5.0-0.13.0.** Current behaviour: `PlutoVetVisit/thunderstore/CHANGELOG.md`.

Status: DRAFT for the user's approval (2026-09-14). Builds on `2026-09-13-vet-visit-past-design.md` (v0.1–0.4, one room,
one boss) and the research in `docs/research/04a-vanilla-pasts-structure.md` and `04b-alexandria-past-building-apis.md`.

## 1. What "vanilla depth" actually is

The research settles how the six vanilla pasts are built: **one large hand-made room with zones** (Convict 64x71,
Hunter 46x85, Marine 69x64), a scripted controller (fade-in, locked camera, two or three conversations, NPCs that walk,
one set piece), a boss with an intro card and reinforcements, an epilogue conversation, freeze frame, credits. Only the
Bullet's past chains four small rooms with warps. Depth comes from scripting, cast and set pieces, not from door-and-corridor
dungeon generation. v2 therefore keeps ONE room, made three times bigger, with three zones and sealed passages between them.

## 2. Story (three acts)

Pluto's regret is the day he was taken to the vet to be neutered. He has eaten "Sterilised 37" ever since.

**Act 1 — The waiting room (south zone, no combat).** Fade in on the carrier by the chairs. The Owner sets it down and
talks to the Receptionist: "Name?" "Pluto. Here for the... procedure." "Take a seat." The room is full of patients:
Rex, the neighbour's dog (took Pluto's third life), trembling; Grandma Cat, ancient and unimpressed; critters loose
on the floor (a chick, a rabbit and a squirrel — vanilla ambient critters). Bubbles: Rex "They said it wouldn't hurt."
Grandma Cat "It didn't. Not for long." The intercom: "Pluto?" The Owner opens the carrier: "Be good." and walks out.
Pluto steps out; the camera unlocks; the door to the ward slides open.

**Act 2 — The ward (middle zone, two waves).** Kennels along both walls, a nurse station, a "Prep" sign.
Wave 1: three Vet Techs (custom enemy: teal scrubs, syringe pistol, Bullet-Kin AI) come out of the side doors.
Wave 2: the kennel doors open: two more Techs plus escaped patients (vanilla `rat` and `parrot` enemies, and two
`mutant_bullet_kin` "patients" in cones). Clearing the zone opens the far door. A treat jar and two cat-bowl hearts sit
on the nurse station.

**Act 3 — The operating theatre (north zone, boss).** Surgical light, monitors, the table with straps, the vaccine fridge.
The Vet waits behind the table: "Right on time, Pluto. Just a little snip. You won't feel a thing." Pluto: "HSSSSSSS!"
Boss card, health bar, music. Below half health he calls the Nurse in (mini-boss add: twice a Tech's size, droplet fans,
a net throw) and two Techs. Death: freeze frame, the credits tube, the win page (existing).

Epilogue line (over the credits, config): "Pluto was never taken to the vet again. He is still on Sterilised 37."

## 3. Cast

| Character | Kind | Look | Behaviour |
|---|---|---|---|
| The Owner | NPC (intro) | human, hoodie, jeans; the Vet's pose pipeline recoloured | walks in with the carrier, two lines, walks out |
| The Receptionist | NPC | office-kin style human at the desk | one line in the intro; interact later for a comment |
| Rex | NPC | dog on a chair (custom 24x20) | trembles; one bubble |
| Grandma Cat | NPC | Pluto's loaf pose, grey recolour | one bubble |
| Critters | ambient | vanilla chick / rabbit / squirrel critters | run around the waiting room, harmless |
| Vet Tech | enemy | human in teal scrubs, syringe pistol; 24x32 | seek + aimed syringe; 15 HP; 5 per run |
| Escaped patients | enemy | vanilla `rat`, `parrot`, `mutant_bullet_kin` | their own AI |
| The Nurse | mini-boss add | the Tech scaled up, cap, shotgun syringe; 120 HP | droplet fans, net throw |
| The Vet | boss | existing | existing three phases + reinforcements at half |

## 4. Room

One room, 30 x 52 cells (the lab tileset), three zones stacked south to north, separated by wall segments with a
door gap that a **door prop** (custom object with a high collider and an open/closed animation) blocks until the zone
is cleared. Zone layouts are ASCII maps in `tools/clinic_room.py` as today; the current clinic becomes the operating
theatre with an OR dressing. New props: kennel cage (open/closed), nurse station, "Prep" sign, surgical light, monitor
cart, vaccine fridge, straps table, door (closed/open), intercom speaker, waiting-room TV.

## 5. Implementation (from the API research, `04b-alexandria-past-building-apis.md`)

- **One room, our own gates.** The flow stays one node; the room grows to 30x52 with wall segments between zones. The
  gap in each wall is blocked by a door prop (custom object, `HighObstacle` collider) whose rigidbody the controller
  disables when the zone is clear, then swaps the sprite to "open". No generator hallways, no vanilla door objects,
  no room-seal events: everything is in the controller, like the Marine past's `AreaDoor`.
- **Waves.** The controller spawns each wave with `AIActor.Spawn(prefab, worldCell, room, true, AwakenAnimationType.Spawn,
  autoEngage:false)` at named positions, sets `HasBeenEngaged`, keeps the list, and opens the door when every actor is
  dead. Vanilla enemies come from `EnemyDatabase.GetOrLoadByGuid` (rat `6ad1cafc268f4214a101dca7af61bc91`,
  parrot `4b21a913e8c54056bc05cafecf9da880`, mutant kin `d4a9836f8ab14f3fadd0f597438b1f1f`; critters
  `95ea1a31…`, `42432592…`, `4254a93f…`). No `.newroom` enemy arrays (their five parallel arrays crash into a fallback
  room when uneven).
- **Vet Tech and Nurse.** `EnemyBuilder.BuildPrefab(name, guid, idlePath, hitboxOffset, hitboxSize, HasAiShooter:false)`
  (Rubber Kin template) then, as for the Vet: `EnemyHitBox` collider, real health, speed, `AddShadowToAIActor` with the
  Bullet Kin's shadow, `BuildAnimation` clips (idle, move, tell, fire, die) with a directional "death", a bullet bank with
  the syringe/droplet entries, and a Bullet-Kin brain: `TargetPlayerBehavior` + `SeekTargetBehavior` + `ShootBehavior`
  with a bullet script (no `AIShooter`/gun object: the syringe is drawn on the sprite). `Game.Enemies.Add` for the console.
- **NPCs.** A `BraveBehaviour : IPlayerInteractable` on a placed sprite, registered with `room.RegisterInteractable`;
  lines via `TextBoxManager.ShowTextBox(point, transform, -1, text, "owl", false, ..., true)` and the advance key.
  The intro is a controller coroutine: `PastCameraUtility.LockConversation`, timed boxes, the Owner walks by a transform
  tween, `UnlockConversation`. Critters are spawned by GUID and left alone.
- **Boss adds.** `healthHaver.OnDamaged` on the Vet: at 50 % spawn the Nurse and two Techs once (theatre positions).
- **Loadout, name keys, watchdog, ending**: as in 0.3.0.

## 6. Milestones (each ends with a GitHub release + drop page zip)

1. **0.5.0 Room and gates**: the 30x52 room with three zones, door props, the walk from waiting room to theatre,
   waves of vanilla enemies only (rat, parrot, mutant kin) to prove spawning/sealing, boss at the end.
2. **0.6.0 Cast**: Vet Tech and Nurse enemies (art + AI), boss reinforcements.
3. **0.7.0 Story**: intro cutscene with the Owner, Receptionist, Rex, Grandma Cat, critters; bubbles; epilogue line.
4. **0.8.0 Dressing and balance**: new props for the three zones, hearts, sounds, difficulty pass.
5. **1.0**: merge into the main DLL (the old milestone 5), after in-game verification.

## 7. Reuse (per the user's request)
Vanilla: lab tileset, critters, rat/parrot/mutant kin enemies, heart pickups, boss card/health bar/credits systems,
the Marine-style sealed-area pattern. Ours: the Vet pose pipeline for every human, Pluto's poses for Grandma Cat,
the boss pipeline for the Nurse, the object pipeline for every prop.
