# 2.19.0 cat set: in-game checklist

Test build `Pluto_The_Cat-2.19.0.zip` from `main`. Nothing below has been run in game yet: the build Mac has no game,
so every line is still open. Spawn pieces with the console (`give pluto:<id>`). Every piece logs `[Pluto]` lines;
copy them into the report. Numbers are the defaults from config section `Cat Set 2.19`.

## Load
- [ ] The BepInEx log has no `step "spray bottle"/"feather teaser"/"toilet paper roll"/"cone of shame"/"coffee mug" failed` lines, no `synergy "..." not registered` lines and no `spray bottle: vanilla Mega Douser water goop was not found`.
- [ ] `give pluto:spray_bottle`, `pluto:feather_teaser`, `pluto:toilet_paper_roll`, `pluto:cone_of_shame`, `pluto:coffee_mug` all work.
- [ ] Qualities in the Ammonomicon/loot: Spray Bottle C (gun), Feather Teaser B (gun), Toilet Paper Roll C (active), Cone of Shame B (passive), Coffee Mug C (active).
- [ ] Play as the Pilot (not Pluto): the five pieces turn up in chests and shops over a few runs.
- [ ] Ammonomicon pages show the right picture, name, subtitle and story: Spray Bottle "Counter Intelligence" (24x32 bottle icon), Feather Teaser "Definitely A Bird" (24x32 teaser icon), Toilet Paper Roll "Home Defence", Cone of Shame "Recovery Position", Coffee Mug "Off The Table". The stories mention Bogdan and Bianca (the teaser's does not) and read naturally.

## Spray Bottle (`pluto:spray_bottle`, gun, C)
- [ ] At 1x in Pluto's paw: the grip sits on the bottle neck and the mist leaves just right of the nozzle. **Deferred (Task 8):** the sprayer head touches the neck at 1x but looked slightly detached in the enlarged preview; check it doesn't read as a gap in game.
- [ ] Semi-automatic, 8 shots per clip, one spray every 0.35 s, 5° spread, 240 max ammo. Fire plays 2 frames (mist puff); reload plays the 3-frame head-off/drip/head-back clip over 1.0 s.
- [ ] Mist cloud flies at speed 15 for 6 tiles, deals 4 damage and 25 knockback.
- [ ] The first enemy a mist hits gets a 0.65-tile vanilla water puddle at the contact point (spreads over 0.2 s). Exactly one puddle per mist. Log once per session: `spray bottle: first hit left vanilla water at (x, y) (radius 0.65)`.
- [ ] The water conducts: shoot an electric gun or step an electrified enemy into it and it zaps like normal water.
- [ ] About 35 % of hits on a normal enemy make it flinch: its current attack is cancelled and it is stunned for 0.5 s, then it acts normally again (AI not disabled). Log once: `spray bottle: first flinch interrupted and stunned a non-boss enemy for 0.5 seconds`.
- [ ] Bosses never flinch (they still take damage and get wet).
- [ ] Harmless and charmed enemies are passed straight through: the mist does not damage, push, wet or flinch them, and it keeps flying to whatever is behind them.
- [ ] **Bath Time** (Spray Bottle + Wet Food Can): mist an enemy already charmed by the can: the mist still passes through it (no damage, no knockback, no puddle) and its charm lasts 2 s longer (no second charm is applied, no fresh hearts burst). Log once: `spray bottle: Bath Time extended Pluto's charm by up to 2 seconds (at most 6 s added per charm)`. Bosses and harmless enemies are not extended. Without the synergy the charm is unchanged.
- [ ] Bath Time budget: keep misting the same charmed enemy. Bath Time adds at most `SprayCharmMaxBonusSeconds` (6 s) to that charm however long it already was (a 10 s Wet Food Can charm tops out at 16 s, a 20 s Dinner Time charm at 26 s); the fourth mist adds nothing and logs nothing. Re-charming the enemy with the can gives it a fresh 6 s budget.

## Feather Teaser (`pluto:feather_teaser`, gun, B)
- [ ] At 1x: grip in the pink handle, idle shows the dangling feather; charge plays at 10 fps; fire frame shows briefly (0.1 s), then the rod is `empty` (no feather) while the lure is out and switches to `return` as it comes back.
- [ ] Hold to charge for 0.6 s; releasing early does not cast. Clip 1, 120 max ammo.
- [ ] The lure (2-frame feather bunch) flies 7 tiles at speed 18, then flies back to Pluto, following him if he moves. It passes through walls and enemies. Logs: `feather teaser: outward leg, range 7`, `feather teaser: return leg`.
- [ ] Each enemy takes 7 damage once on the way out and once on the way back (big enemies are not hit repeatedly).
- [ ] While the lure is out you cannot fire again and the gun does not reload (also not via inventory reload). When it returns, a 0.4 s reload starts. Log: `feather teaser: cleanup restored gun; lure gate released`.
- [ ] A normal enemy the lure touches chases the feather for 1.5 s and does not shoot during that time, then goes back to normal (including after the lure has already returned). Logs: `feather teaser: distract for 1.5 s`, `feather teaser: cleanup distraction`.
- [ ] A boss is only slowed to half speed for 0.5 s. Log: `feather teaser: boss slow for 0.5 s`. Harmless and charmed enemies are ignored (no damage, no distraction).
- [ ] Switching guns, leaving the room, or dying with the lure out removes the lure, ends every distraction immediately and gives the gun back. A lure that somehow never returns ends by itself after 10 s.
- [ ] Co-op: both players cast lures through the same enemy; it ends up moving normally afterwards (never frozen or stuck sliding).
- [ ] **Playtime** (Feather Teaser + Ball of Yarn): each distracted enemy is also tangled like the yarn (stunned 1.5 s, then slowed; same cooldown as the ball). Log: `feather teaser: Playtime shared yarn tangle`.
- [ ] Playtime precedence: the tangle wins over the feather. A tangled enemy visibly **stops** where it is (it never slides after the lure) for the tangle's 1.5 s. If the distraction still has time left when the tangle ends, it starts chasing the feather again; if the distraction ran out first, it simply goes back to normal. The enemy is never left frozen or sliding afterwards.
- [ ] Playtime resume (cannot be checked outside the game): raise `FeatherDistractSeconds` to about 6 s so the
  distraction clearly outlives the 1.5 s tangle, then catch one enemy. It must stop for the tangle and then
  **visibly chase the lure again** once the stun ends, not stand still or walk off on its own. Repeat in co-op
  with both players lure-ing the same enemy: the handover must not leave it frozen. Afterwards it moves normally.

## Toilet Paper Roll (`pluto:toilet_paper_roll`, active, C)
- [ ] Icon at 1x reads as a roll. Recharges after 400 damage.
- [ ] Use: a 4-tile paper streamer appears 1 tile in front of Pluto, across his aim (perpendicular). Sound plays. Log: `toilet paper roll: streamer placed for 5 s / 12 hits`.
- [ ] Enemy bullets that touch it are destroyed; each block tears away the nearest piece of paper with torn bits. Log per block: `toilet paper roll: blocked enemy bullet N/12`.
- [ ] Pluto, co-op partner and enemies walk straight through it; Pluto's own bullets and charmed enemies' bullets pass through.
- [ ] It ends after 5 s or 12 blocked bullets, whichever first. Log: `toilet paper roll: streamer ended normally after N hits`.
- [ ] **Deferred (Task 5):** the drawn streamer is about 4.375 tiles long while the collider chain is exactly 4 tiles; check at 1x that bullets aren't visibly passing through the tips.
- [ ] Leaving the room, dying or dropping the roll removes the streamer immediately, with no confetti.
- [ ] Co-op: two overlapping streamers never both count the same bullet.
- [ ] **Shredder** (Toilet Paper Roll + Scratching Post): when the streamer ends normally (timeout or 12 hits), it bursts into confetti along its length and deals 10 damage to every valid enemy whose hitbox touches the 4-tile paper strip (a diagonal streamer does not hit enemies beside it). Log: `toilet paper roll: Shredder confetti burst for 10 damage`. No burst on room change, death or drop.

## Cone of Shame (`pluto:cone_of_shame`, passive, B)
- [ ] Icon at 1x reads as a cone.
- [ ] While ready, the first enemy bullet within 1.5 tiles of Pluto's center and inside a 70° arc toward his aim is destroyed, with a spark at the bullet and a plastic thok sound. Log: `cone of shame: thok`.
- [ ] Only one bullet per block; the cone then needs 3 s. Bullets from behind or outside the arc are never blocked. Charmed enemies' shots are not blocked.
- [ ] When the 3 s cooldown ends a single glint (block spark) appears over Pluto's head (1.1 tiles above) with a chime. No glint on pickup.
- [ ] **Deferred (Task 6):** dropping and picking the cone up again resets its cooldown (it is ready at once). Decide whether that is acceptable.
- [ ] **Matching Cones** (Cone of Shame + Coco Blue): Coco wears a cone in idle, move, pet, block and knocked-out clips (the cone lies beside him when knocked out). He holds one extra bullet (9 instead of 8 by default).
- [ ] **Deferred (Task 6):** gaining the synergy adds the extra charge at once, not just the capacity; dropping and re-picking the cone can top Coco up by one charge per cycle. Decide whether that is fine.

## Coffee Mug (`pluto:coffee_mug`, active, C)
- [ ] Icon at 1x reads as a mug with the red heart; the flying mug uses the same picture. Recharges after 300 damage.
- [ ] Use: the mug flies toward the aim at speed 12, deals no damage, and shatters at 3 tiles or at the first wall/enemy it hits. Logs: `coffee mug: thrown 3 tiles`, `coffee mug: shattered into 10 shards at (x, y)`.
- [ ] **Deferred (Task 7):** check the shatter sound (`Play_OBJ_rock_break_01`) sounds like a mug breaking.
- [ ] 10 shards fly out in an even ring (every 36°), speed 14, 4 tiles, 5 damage each, cycling the four shard pictures (one with the heart).
- [ ] **Deferred (Task 7):** when the mug hits an enemy, shards spawn inside its body; check they still hit it (or at least don't vanish silently) and that shards spawned against a wall behave.
- [ ] A coffee puddle stays for 3 s. Enemies standing in it move at half speed and speed up again as soon as they leave; everything returns to normal when the puddle ends.
- [ ] **Deferred (Task 7):** the slow zone is the 12x8 px puddle sprite (about 0.75x0.5 tiles); check it doesn't feel too small. Check the puddle draws under enemies and Pluto (depth).
- [ ] **Deferred (Task 7):** two overlapping puddles (co-op): an enemy leaving one can briefly (up to 0.1 s) lose its slow while still in the other; check for visible speed flicker.
- [ ] A mug thrown through a doorway slows enemies in the room where it lands. The puddle ends when the thrower leaves their room or dies (also in co-op while the partner lives: deferred note), or when the mug is dropped.
- [ ] Harmless and charmed enemies: mug and shards pass through them; the puddle does not slow them.
- [ ] **Espresso** (Coffee Mug + Catnip Pouch): using the mug during zoomies adds 2 s to them (the active bar grows, the catnap waits). Logs: `coffee mug: Espresso extended zoomies by 2 s`, `catnip pouch: zoomies extended by 2 s (N s left)`. Using it with an idle or napping pouch logs `coffee mug: Espresso had no running zoomies to extend` and changes nothing.
- [ ] **Deferred user decision (Task 7):** both pieces are actives. Most Gungeoneers carry one active, and Pluto's two slots are taken by his Wet Food Can and Squeaky Toy, so Espresso needs extra active capacity (e.g. Backpack) to hold both. A co-op partner's pouch is not used.
- [ ] **Catnip Pouch change:** dropping the pouch mid-zoomies now ends the speed boost at once (before 2.19.0 the speed boost kept running). Fire rate, trail and catnap still stop as before.

## Shared checks
- [ ] Charmed/harmless: none of the five pieces damages, flinches, distracts, slows or confetti-hits a charmed or harmless enemy. The Spray Bottle's mist and the Coffee Mug's mug and shards visibly pass through them and carry on. Bath Time is the one exception, and it only lengthens an existing charm.
- [ ] Bosses: Spray never flinches a boss, Feather only slows a boss 0.5 s, Shredder and shards damage bosses normally, the puddle slows bosses.
- [ ] Coco precedence: with Coco Blue + Ser Junkan (Squire) + Cone of Shame, Coco wears the **cone** (not the knight helmet) and still gets the Squire stuffing bonus plus 1. Drop the cone: the knight helmet comes back on the next frame and the extra charge goes. Drop Junkan too: plain Coco.
- [ ] Config clamping (set in `BepInEx/config`, restart): `SprayFlinchChance = 1.5` logs `[Pluto] config: SprayFlinchChance = 1.5 is outside 0 to 1; using 1.`; `TPHits = 0` logs `... TPHits = 0 is outside 1 to 99; using 1.`; `ConeArcDegrees = 360` logs `... is outside 1 to 180; using 180.`; `SprayCharmMaxBonusSeconds = 0` logs `... is outside 0.1 to 60; using 0.1.` The game uses the clamped values.
- [ ] Co-op: each player's pieces act for their owner only (their own aim, room and synergies); dropping a piece on one player never ends the other player's streamer, puddle or distraction.
- [ ] Deferred (Task 4): no duplicate Feather Teaser behaviour after a normal game restart (Harmony guards are process-lifetime; plugin hot-reload is unsupported).
