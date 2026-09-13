# Changelog

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
