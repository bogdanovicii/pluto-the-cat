# Changelog

## 2.16.5
- **Coco's knight helmet really shows with Ser Junkan**: the helmet swap wrote the animation name the game ignores for Coco's one-direction clips, so he never changed (the Knighted helmet had never shown since 2.15.0). He now wears the gold plumed helmet at every Junkan form.
- **Ammonomicon pages for the Taiyaki Cannon and Katana** show the gun's picture (they were blank).
- **Samurai Puffed Up is fluffy again**: the samurai costume gets its own standing-fur ring that stays off the kimono, alongside the red anger cue.
- **The Katana makes a sound when it swings** (it borrows Blasphemy's swing sound).

## 2.16.4 (test build, not released)
- **Coco runs again during the Squeaky Toy decoy**: 2.16.3 let him stand still when no bullet threatened him. Every decoy leg now runs 2.5-3.5 tiles in a panicky zigzag, still steering away from incoming bullets and staying within about 8 tiles of Pluto.
- **Coco wears the gold knight helmet** whenever Ser Junkan is with him (Squire), whatever Junkan's form; it comes off when the synergy ends and lies beside him when he is knocked out.
- **Taiyaki Cannon reload redrawn**: 9 frames over the full 0.9 s reload. The Churu tube pushes into the tail, is squeezed flat, and a bead swells in the mouth.
- **Churu drop** (like the Kibble Sack's hairball): finishing a reload from an empty clip flings a Churu drop toward your aim for 5 damage, with a 3-damage bonito splash within 1.5 tiles. Config `Balance/ChuruDrop` (on by default).

## 2.16.3 (test build, not released)
- **Coco** spends one stuffing per enemy bullet (several bullets at once cost several), dodges by where bullets are heading instead of running at random, and his decoy only releases the enemies it retargeted.
- **Crumbs** drop only after a kibble damages an enemy (not on walls), at most 12 per player, and are left on the floor when the gun cannot take ammo.
- **Nine Lives** shows the current life in the item subtitle and a short notice on each new floor ("Seventh life. Two to spare.").
- **Samurai Pluto** gets a red flash, pulse and repeating anger marks while Puffed Up (the fur ring stays hidden for that costume). Damage and fire rate unchanged.
- **Playdate/Squire**: the Dog and Junkan get back exactly what they had before a decoy instead of assumed defaults.
- Config values out of range are clamped with a warning in the log. Weapon grip/muzzle numbers come from one generated table (no change in game).

## 2.16.2
- **Taiyaki Cannon** is stronger: 8 damage per mini taiyaki (was 6), one shot every 0.20 s (was 0.24), 10 per clip (was 8), 0.9 s reload (was 1.1), faster taiyaki. About 40 damage per second against the Royal Kibble Sack's 35. New config keys `TaiyakiDamage` and `TaiyakiClip`.
- **Playdate** (Squeaky Toy + Dog) fixed: while Coco is out as a decoy, the Dog now fights like the vanilla Wolf. It runs at the enemy chasing Coco, barks, leaps and bites, then goes back to being a normal Dog when the decoy ends. Before, the Dog never visibly attacked.

## 2.16.1
- The **Katana** now swings like Blasphemy: the blade sweeps from raised to low around Pluto's paw over 8 frames, with a thin steel-white crescent trailing it. Before, the fire animation held the blade still and only showed a crescent.

## 2.16.0
- **Samurai Pluto**: a new alternate costume replaces Wet Pluto. Crimson hachimaki with trailing tails, indigo haori with a white paw crest and an open collar, crimson obi, charcoal hakama, on every animation (rolls and death included).
- The costume unlocks the vanilla way: beat Pluto's past (the Vet Visit) and a kimono stand appears in the Breach next to him. The old forced unlock is gone. Testing key `UnlockSamuraiCostume` (Debug, default false) shows the stand anyway.
- The costume decides the loadout: Samurai Pluto starts with the **Taiyaki Cannon** (mini taiyaki from a bean-filled mouth, bonito flakes on hit, a Churu tube squeezed in on reload) and the **Katana** (Blasphemy's rules with a longer reach: the swing cuts bullets, a sakura crescent flies out at full health, reloading knocks nearby bullets away). Normal Pluto keeps the Royal Kibble Sack. The Breach alt-gun shrine does nothing for Pluto; the costume is the switch.
- New boss-intro cards: a detailed bust of Pluto with the kibble sack, and a samurai bust with the katana while the costume is worn. Both are transparent cut-outs, so the boss art stays visible.
- Puffed Up shows no fur while the kimono is worn.
- Retired: Wet Pluto, the bathtub and the Royal Canin Gravy Pouch. Config key `BathtubOffset` keeps its name and now places the kimono stand.
- Art: every new picture is generated with Gemini first and converted into pixel-perfect art with the project's pluto-artist skill.

## 2.15.3
- Playdate works: squeeze the Squeaky Toy while carrying the Dog and the Dog runs at the enemy chasing Coco and bites it (6 damage every 1.2 s). It did nothing before, because Coco looked for enemies in a room companions never have. The same fix makes Ser Junkan (Squire) charge the enemy chasing Coco.
- Playdate is now Squeaky Toy + Dog (was Coco Blue + Dog). Petting either friend still makes the other wiggle.
- Boss intros show the boss again: Pluto's boss card was a fully opaque 427x240 panel drawn over the boss art; it is now a transparent cut-out with Pluto in the bottom-left corner.
- Squeezing the toy logs the synergy state, e.g. `[Pluto] Coco decoy: Playdate True (dog True), Squire False, chaser Bullet Kin`.

## 2.15.1
- Coco Blue keeps his ears when he hops: the move frames used to cut off the top of his head (up to 25 pixels on the highest hop), and the last frame of the pet wiggle lost his right edge. His frames now have room above and to the side.

## 2.15.0
- Coco Blue has friends. **Playdate** (Coco Blue + Dog): while Coco is a decoy the Dog runs at the enemy chasing him and bites it (6 damage every 1.2 s). Petting either one makes the other wiggle with hearts, and petting the Dog gives Pluto Coco's burst of speed.
- **Squire** (Coco Blue + Ser Junkan): Coco holds one more bullet per Junkan rank (up to +6 at Holy Knight), and while Coco is a decoy Junkan charges the enemy chasing him.
- **Knighted**: once Ser Junkan is a Holy Knight (6 junk) or Angelic, Coco wears a tin helmet with a gold band and a red plume in every animation. When he is knocked out, the helmet lies on the floor beside him.

## 2.14.0
- Wet Food Can reworked: Pluto throws the tin straight at what he aims at instead of lobbing it. The enemy it hits takes 5 damage and falls in love with him, and the tin always bursts where it stops (enemy, wall or end of range), charming every enemy in a 2-tile gravy splash. Bosses are stunned for 3 seconds instead. Still recharges after 200 damage; Dinner Time still widens the splash and doubles the charm.
- New can art from the real Royal Canin Kitten tin: gold ring-pull lid, pink label, crown on the red band, gravy window; it tumbles end over end in flight and bursts into gravy and hearts.
- Config: `CharmRadius` is replaced by `CanSplashRadius` (default 2); new `CanDamage` (default 5).

## 2.13.0
- Running no longer does the splits: legs stay straight under the hips on every frame (a 1-px stride instead of two diagonal legs), front and back runs plant one foot while the other lifts.
- Dodge roll redone the way the Gungeoneers roll: four direction clips instead of one ball. Sideways Pluto dives and somersaults with his head, ears and tail visible in every tumble; rolling down he tucks his head, goes over on his back and comes round; rolling up he shows his belly and face upside down; the up-diagonal roll turns his face away.
- The Royal Kibble Sack in Pluto's paw is now the same Royal Canin bag as its Ammonomicon page, lying on its side: purple label with the grey cat, red band with white dots, the crown, the zip seam, and a torn-open top where the kibble comes out. Firing squeezes the bag and sprays kibble from the top; reloading folds the top shut, shakes the bag and tears it open again.

## 2.12.0
- Pluto lands on his feet: falling into a pit costs no health (config `NoFallDamage`), and Nine Lives never spends a life on a pit.
- The Royal Kibble Sack cracks secret-room walls: shoot a suspicious wall and each kibble bites 15 extra damage out of it (walls have 100), so the crack shows after a few pawfuls and the wall opens soon after. Config key `SecretDoorDamage`.

## 2.11.0
- Nine Lives rewritten as lore: Pluto has already spent six of his nine lives (balcony railing, washing machine, the neighbour's dog, a rubber band, the bathtub, the Gungeon's elevator door) and starts every run on his **seventh**. A lethal hit ends the current life and starts the next; the ninth is the last one, with no save. That is two saves per run instead of nine.
- Banner now names the life ("Eighth life.", "Ninth life. The last one."). Config key `NineLives` replaced by `StartingLife` (default 7).

## 2.10.2
- Coco Blue lost his double outline: companions are AIActors and the game outlines them at runtime, so his frames ship without a drawn outline (same as Pluto since 2.9.0).

## 2.10.1
- The Royal Canin bag has a real silhouette now: pinched sealed end at the paw, rounded belly, torn spout with kibble spilling out; the crown and cat stay on the Ammonomicon page where they fit.
- Pipeline: PNG-to-rows importer for editor touch-ups, orphan-pixel and stray-flicker lint checks, and a project skill (.claude/skills/pluto-pixel-art) that captures the palette, specs, timing and checklist.

## 2.10.0
- Art pass B, animation keys. Idle is a real squash (head sinks into the shoulders, feet and belly stay put) with an ear flick; in the run the head lags a row and the ears blow back on the airborne frames.
- Dodge roll: crouch, stretched leap, three tumbles, low ball, landing squash, 1-px overshoot, idle.
- Death: the flat tail drops last. Pit fall: crouch, two shrinks, then the two single-colour blips like vanilla; climbing out mirrors it with an overshoot. Table slide is a hand-drawn low pose with wide eyes.
- New back-view side poses for aiming up-diagonally (idle_bw, run_right_bw, jetpack_right_bw): back of the head, one pink ear, striped flank.
- Hand variants follow the game's meaning: with a one-handed gun the body shows the free paw on the chest (the paw on the gun is the game's hand sprite); with no gun both paws show.

## 2.9.0
- Art pass A. Pluto's body frames no longer carry a baked outline: the game draws the black outline itself, so he had a double outline before. He now matches the Gungeoneers' line weight.
- New palette from the photos: grey-brown taupe fur with hue-shifted shading, near-black mackerel stripes and tail rings that read at 1x, hazel-green eyes.
- One head for every pose: tabby mask around the eyes, white blaze down to the muzzle, the white head spot as a clean oval on the crown, bigger pink ears, forehead M; front pose no longer wall-eyed.
- Taller canvas (24x26) with headroom: the run is the vanilla 4-px hop (contact, airborne, pass) and the ear tips are never clipped; the tail lags the body by a frame instead of flickering; the dodge ball no longer wobbles; the death tail lies beside the body; idle gets an ear flick.
- Removed the automatic rim shading (it was banding); shadows are hand-placed.
- Tooling: strict canvas checks, an art lint in the build, game-like previews (runtime outline, floor, Pilot-size box, animated clips).

## 2.8.1
- Fix: bullets passed through Coco. His companion body ignores all collisions by design; a separate bullet-blocker body now rides on him.
- Pluto now has two active-item slots, so he starts with both the Wet Food Can and the Squeaky Toy (swap with the active-swap key).
- Petting Coco during a fight also sends him out as a decoy.
- Bathtub moved: it now stands two tiles above Pluto in the Breach (new config key `BathtubOffset`, relative to him).

## 2.8.0
- The Squeaky Toy is now a B-quality item in chests and Trorc's shop: any Gungeoneer who picks it up gets Coco Blue as a companion, and loses him if they drop the toy. Pluto still starts with it and can never drop it.
- New Squeaky Toy icon: a little blue Coco-shaped toy.

## 2.7.0
- Coco Blue can be knocked out: after blocking 8 bullets he flops onto his back for 10 s, blocks nothing and cannot decoy until he recovers. Petting him brings him round early. Stuffing regenerates one point every 4 s. All configurable.

## 2.6.0
- Coco Blue blocks enemy bullets that touch him (squish animation and a spark); Pluto's own shots pass through.
- New starting active **Squeaky Toy**: Coco goes decoy for 8 s: every enemy in the room targets him while he runs around dodging bullets and enemies. He cannot be hurt.
- Petting uses the proper "other" animation slot (no more chance of the idle showing the pet wiggle).

## 2.5.0
- Puffed Up rebuilt: the fur now follows Pluto's own outline frame by frame in every direction (idle, run, roll, item get, table kick, jetpack, slide), bristles up over the first frames, shivers with a shudder and drifting fur while angry, and settles back down. Tail goes bottlebrush.
- Fix: the Wet Pluto bathtub never appeared in the Breach because the alt-costume unlock flag was never set; it is set at load now.

## 2.4.1
- Art: rim shading on every body frame (shadow bottom/right, highlight top-left, shaded chin), matching the face card; Wet Pluto shaded too.
- Nine Lives keeps its count across save-and-continue.
- Pluto's own speed boosts (zoomies, anger, petting) are capped together (`MaxSpeedBonus`, default 4).
- Puffed Up trigger is guarded so it can never break the damage path.

## 2.4.0
- Coco Blue can be petted: stand next to him and interact. He wiggles, hearts rise, and Pluto gets three seconds of zoomies.

## 2.3.1
- Puffed Up: larger fur halo so the bristling fur shows all around the enlarged body.

## 2.3.0
- New starting passive **Puffed Up**: every hit (including one Nine Lives cancels) makes Pluto bristle for 6 s: bigger body, a ring of standing fur behind him, anger marks over his head, and +50 % damage, +30 % rate of fire, +1 speed. All tunable in the config.

## 2.2.0
- **Coco Blue**, Pluto's plush cat, is a starting companion: follows him and drops a kibble crumb whenever he takes a hit.
- **Nine Lives** now shows an on-screen banner with lives left and a puff of fur.
- **Wet Pluto** carries his own alt gun, the Royal Canin Gravy Pouch (slow gravy globs, small charm chance).
- Enemies that die while in love sometimes drop a **kibble bowl** that heals half a heart.
- Custom fur-puff (Nine Lives, tail whip) and love-burst (can splash) effects; the select card pops in.
- Still no Hegemony cost.

## 2.1.1
- Fix: hairball never fired (wrong reload hook); it now triggers on every empty-clip reload.
- Art: new shaded, frame-filling face card (HUD, select card, boss card, icon); Royal Canin bag redrawn at 32x18 with gusset, zip, crown, band and label; Ammonomicon bag redrawn; wet-food can redrawn at 20x20 with gold lid, pull ring and label; new splash frames.

## 2.1.0
- Config file `BepInEx/config/bogdan.etg.plutothecat.cfg`: lives, kibble damage/clip/crit, charm radius/duration, boss stun, can recharge, tail whip, zoomies, hairball, roll i-frames, Breach positions.
- Every load step is isolated; a broken optional feature logs `[Pluto] step "..." failed` and the rest still loads.
- `pluto_check.sh` ships in the package: greps the BepInEx log and prints PASS/FAIL.
- Tail whip: rolling through an enemy hurts and knocks it back. Zoomies: speed burst after a room clear. Hairball: reloading an empty clip coughs up a slow stunning lump.
- Art: one-hand and two-hand body variants now show the arm reaching for the gun.

## 2.0.3
- Run cycle: shorter trot stride, feet stay under the body.

## 2.0.2
- Fix: the mod failed to load because two synergy item ids were wrong (`cheese_wheel` → `partially_eaten_cheese`, `cardboard_box` → `box`). Synergies now register one by one after the character is built, so a bad id can only lose that synergy.

## 2.0.1
- Run cycles rebuilt on the vanilla hop rhythm: stretched legs on contact frames, body lifts two pixels with tucked legs when airborne, forward lean.

## 2.0.0
- New starting passive **Nine Lives**: the first time a hit would kill Pluto it is cancelled, he stands back up with one heart and loses one of nine lives (per run).
- Cat reflexes: longer dodge roll with 6 of 9 invulnerable frames.
- Royal Kibble Sack: two kibble per pawful, 1-in-20 big chunk, crumbs on the floor top up your other gun's ammo.
- Wet Food Can: lovestruck enemies take 20 % more damage; bosses get a fixed 3 s stun instead of AI-dependent charm; faster recharge.
- Synergies: Complete Feline Nutrition (homing kibble), Dinner Time (longer, wider charm), Laser Pointer (dodge rolls drop a red dot enemies chase), Box Fort (Cardboard Box has no cooldown).
- Alt skin **Wet Pluto** (fresh out of the bath), swapped at the bathtub in the Breach.
- New Breach idles: loaf, groom, and knocking a bowl off a ledge. Co-op death shows Pluto's ghost.
- Logs the Punch-Out sprite names so 2.1 can ship Pluto's boxing sprites.

## 1.0.1
- Fix: character build failed on Alexandria 0.5.10 because the `<altGuns>` block was missing (altGun is NULL). Added it.
- The plugin now reports a failed character build instead of printing "ready".

## 1.0.0
- First release: Pluto the Cat character, Royal Kibble Sack starter gun, Wet Food Can active.
