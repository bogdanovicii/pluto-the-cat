# Changelog

## 2.20.9 (test build, not released)
Fixes for the two failures in the 2.20.8 in-game test, plus a way to test reach without anyone standing at the counter.
- **The wall behind the counter now works.** In 2.20.8 `pluto_stall bodies` showed the back fill (the invisible player-only wall behind the counter) as a 0x0 box, flagged STALE. It was added to the counter's collider after that collider had already been built, and the game never picked it up. The counter's footprint and the back fill are now built together in one step, and a finished collider is never added to afterwards. The box sizes are the same. Kinsuke's bowl still has no collider on purpose, because it stands inside the back fill's area. `pluto_stall bodies` now says that instead of calling the bowl walk-through.
- **The three items can be reached across the counter.** In 2.20.8 every plaque measured 1.125 tiles from the counter front. The game's default reach is about 1 tile (a guess, since Alexandria leaves items at the default), so all three were out of reach. A small patch raises the reach to 1.5 tiles for this stall's items only. Other shops are untouched. `pluto_stall bodies` now reports the reach the game actually uses and says whether each item is in reach.
- **New `pluto_stall stand <daifuku|0|1|2>` (Breach only).** It moves you to the counter front, 2 px in front of the counter's collider, right under Daifuku or item 0, 1 or 2. Half a second later it logs what the game itself chose to interact with: `shrine stall: stand <target>: the game selected <name> (expected <target>) -> REACH OK / NOT REACHED`, plus where you are standing. That answers the reach question without a human standing at the counter (in 2.20.8, `tp` didn't move the player). It also makes sure you can walk away afterwards, even if the move put you inside a collider.

## 2.20.8 (test build, not released)
The Shrine Stall redesign, drawn to the mockups the user approved on 2026-09-18.
- **Nothing to buy (P1):** the three items now sit on the counter top. Two of them used to hang past its right end, and the first sat over Daifuku. The game normally forces shop items to draw behind the counter; after stocking, their depth is reset so they draw in front of it. The item spots sit 2 px higher, so the crimson mats show under the plaques.
- **Flat, overlapping stall (P2):** new art in the game's 3/4 view. There is a wider counter (6.5 tiles) with a visible top face, and a taller torii whose two posts both stand clear of the counter. Daifuku stands behind the counter with his paws on it. Kinsuke's bowl is smaller and sits 1.3 tiles from him instead of covering him. Locked items show as an ema plaque instead of a blueprint. The Japanese decorations (noren, maneki-neko, stone lantern, koi banners) are dropped.
- **No collision (P3):** the counter's footprint and the torii post bases are solid. A player-only wall stops you walking round a post into the space behind the counter. The bowl sits inside the counter's footprint. Every move refreshes the colliders.
- **The stall's default position is 61.063, 18.25, the spot the user chose in game.** The two old defaults (19.7, 22.1 and 10.5, 22.1) move to it automatically. A position you chose yourself is never changed.
- **Daifuku stays talkable across the solid counter:** his talk radius is widened to 1.75 tiles. The stock probe now waits for the shop to actually stock before lifting the items in front of the counter, so returning from a run doesn't leave them sunk. Colliders refresh only when the stall actually moves. The stall position snaps to the pixel grid in memory. `pluto_stall` refuses to move the stall outside the Breach.
- `pluto_stall bodies` logs every collider, and whether Daifuku and each item are in reach from the counter front and from the player. `pluto_here` now works as another name for `pluto_where`. The stock report now says outright that empty slots are expected before character select.

## 2.20.7 (test build, not released)
- **The Shrine Stall stocks its items again.** Its loot table was created bare, which leaves the table's list of included sub-tables null. When a live shop set itself up in the Breach, compiling that table threw a NullReferenceException and no items were ever stocked. This stayed hidden until 2.20.6 because until then no live shop existed. The table is now created with Alexandria's `LootUtility.CreateLootTable()`, which initialises both lists. (Confirmed from 11 Steam-machine logs: the exception appeared in every run with a live shop and in no other run.)
- `pluto_stall stock` logs the loot table and what each item slot holds. A probe also logs the stock about 1.5 s after character select.
- New `pluto_where` console command: logs where the player is standing, for measuring the Breach shop door. It moves nothing.
- Known: items still sit at the old anchors, two of them past the counter's right edge. The stall's art and layout are being redesigned separately.

## 2.20.6 (test build, not released)
- **The Shrine Stall now appears on your first visit to the Breach**, not only after coming back from a run. The event Alexandria uses to place Breach shops is raised when the title screen's controller wakes — and the title screen *is* the Breach, so it fires at launch, before this mod has registered its shop. Alexandria placed nothing of ours, and starting a run does not reload the scene, so it never tried again. The mod now notices the Breach is already up when it registers and triggers Alexandria's own placement straight away. (Diagnosed and confirmed on the Steam machine with `load_level tt_foyer`, which placed the shop correctly on the first reload.)
- **`pluto_stall` moves now survive the next Breach load.** A move made before the shop existed was only applied to the live copy, not to the template Alexandria places from, so the next load put the stall back where it started. The template is now updated on every move, and each Breach load also re-checks the live shop against the configured position.

## 2.20.5 (test build, not released)
- **The Shrine Stall's shopkeeper finally stands at his own stall.** For five builds the mod held the wrong object: `SetUpFoyerShop` returns a *template*, which Alexandria instantiates on every Breach load, positioning the **clone** and leaving the template at the world origin forever. So `pluto_stall` moved something nothing renders, and the diagnostics measured it too — which is why 2.20.4 reported Daifuku, the three item points and the speech point all at 0,0 while the props sat correctly at the stall. Daifuku was healthy the whole time; he was standing on a template. The mod now finds the live shop in the scene and moves and inspects that.
- **The stall is composed around the shopkeeper instead of three tiles to his left.** The gate and counter are now centred on him, so he stands behind his counter and the gate frames both — previously only the gate's left pillar was visible, with its right pillar hidden behind the counter.
- **Kinsuke's bowl no longer sorts behind everything.** Depth here is `z = worldY − heightOffGround`, so raising the bowl a tile to sit on the counter also pushed it a tile backwards and swamped its depth value. Its height is now compensated for, and the draw order is bowl, counter, Daifuku, gate, front to back.
- The bowl also moved 0.9 tiles right of the counter centre, so it rests on the surface instead of hanging off the end.
- The stall's footprint report now measures the drawn sprite edges rather than just the anchors, so it no longer understates how wide the stall is.

## 2.20.4 (test build, not released)

- **Fix: Daifuku still didn't render, even after 2.20.3 placed him at the right position.** The torii
  (77x48px) and the counter (48x36px) backdrop props were plain Unity `SpriteRenderer` GameObjects at
  z=0 with no `sortingOrder`, no `sortingLayerName`, and none of this game's own tk2d depth handling -
  the same convention every other prop in this mod already uses (`CoffeeMugItem`'s puddle,
  `PuffedUpItem`'s fur layer, `ScratchingPostItem`'s placed post, all via
  `sprite.HeightOffGround = ...; sprite.UpdateZDepth()`). With both props now centered on Daifuku's own
  anchor point (per 2.20.3's counter-centering fix), a raw z=0 sprite had no defined draw order relative
  to him and could render in front, hiding him completely with nothing in the log to say so. Props are
  now built as `tk2dSprite`s with an explicit depth, back to front: torii, then the counter, then
  Kinsuke's bowl, leaving Daifuku (whose own depth this file does not touch) in front of all three.
- **Add: unconditional shrine stall diagnostics.** At foyer placement time (and after every `pluto_stall`
  move), the mod now logs each backdrop prop's resolved world position and depth, plus a line for every
  GameObject in the shopkeeper's own transform hierarchy (name, resolved position, renderer presence/
  enabled state, world-space bounds, and whether its sprite is actually bound) - this covers both "is
  Daifuku there and drawn in front of the counter" and "what is that other object" (Alexandria builds
  several besides the NPC: a blueprint prefab instance, item points, a talk point) in one pass, so the
  next report is a name and a number instead of a screenshot to guess from.

## 2.20.3 (test build, not released)

- **Fix: Daifuku was being placed twice as far from the Breach origin as intended, so he never appeared
  next to his own stall.** The 2.20.2 tester reported the torii rendering correctly but Daifuku entirely
  absent, with nothing near the stall interactable. Verified against the Alexandria 0.5.10 IL:
  `ShopAPI.SetUpFoyerShop` parents the shopkeeper's GameObject to the shop's own root and then sets the
  shopkeeper's WORLD position to the `npcPosition` argument while that root is still freshly created at
  Unity's (0,0,0) default - so `npcPosition` is really the shopkeeper's offset FROM the shop root, not a
  second copy of where the whole stall goes. `ShrineStall.cs` passed `PlutoConfig.StallPosition` for both
  the shop's placement and `npcPosition`, so once the shop root was later moved to that same position
  (Alexandria's `BreachShopTools.PlaceBreachShops`), Daifuku ended up at `StallPosition + StallPosition` -
  about 28 tiles from his own torii, counter and koi bowl. `npcPosition` is now `Vector3.zero`. This also
  fixes `pluto_stall here`/`pluto_stall <x> <y>`, which had the same doubling bug for any session where the
  shop had already built.
- **Fix: the stall counter rendered to the left of the torii gate instead of under it.** An earlier
  art-review note aligned the counter's center 6px right of the torii's LEFT EDGE rather than centering it
  under the gate as the design calls for ("Under the gate: a counter..."). Since both sprites are
  bottom-center pivoted, centering one 3-tile-wide sprite under a 4.875-tile-wide one needs no X offset at
  all; the stall's offset now matches the torii's.
- **Fix: Kinsuke's koi bowl floated about three quarters of a tile above the counter, near the torii's
  crossbeam.** The old Y offset (28/16 tiles) was a guess at "near the top of the sprite". `stall.png`
  (48x36px) was measured pixel-by-pixel this round: the counter's top lip starts 20 rows down from the top
  of a bottom-center-pivoted 36px-tall sprite, so the counter surface sits `(36 - 20) / 16 = 1.0` tile above
  the ground line, not 1.75. The bowl's Y offset is corrected to match.
- **Known still-wrong: the default `StallPosition` (19.7, 22.1).** It was derived from `FoyerPosition`
  (14.6, 22.1), which is consumed by a different coordinate space (Alexandria's `CharacterAPI`, for where
  Pluto himself stands) than the Breach shop placement this reads - the same kind of unverified-arithmetic
  mistake that produced this whole round of bugs. It is left as-is on purpose rather than replaced with
  another guess; the tester's own `pluto_stall here` readings during 2.20.2 testing put the real walkable
  Breach area around x=40-42, y=43-59, and the next `pluto_stall here` / `pluto_stall save` on this build
  should supply the real value.

## 2.20.2 (test build, not released)

- **Fix: Yasupen never actually registered since 2.18.0.** `ItemBuilder.SetupItem` derives the id an item
  registers under from the GameObject's own name, not from the `ID` constant the file declares. Yasupen's
  GameObject is named "Yasupen's Price Tag", so he registered as `pluto:yasupen's_price_tag` instead of
  `pluto:yasupen` - nothing was ever bound to `pluto:yasupen`, so `give pluto:yasupen` and the Penguin Pals
  synergy could never have worked. He is now renamed back to `pluto:yasupen` right after setup, the same way
  HairballItem already handled this, with a log line if that rename ever fails again.
- **Fix: the 2.20.0 broken `StallPosition` default is now migrated automatically.** 2.20.0 shipped with
  `StallPosition` defaulting to (10.5, 22.1), which put the Shrine Stall off-screen; 2.20.1 raised the default
  to (19.7, 22.1), but BepInEx keeps a value an existing config file already has, so anyone who ran 2.20.0
  stayed stuck on the broken position after updating and would have seen no change. The config now detects the
  exact old broken value on load and replaces it with the current default, logging that it did so; a position
  you deliberately chose is never touched.

## 2.20.1 (test build, not released)

- **Fix: the Shrine Stall was off-screen in the Breach.** The 2.20.0 `StallPosition` default (10.5, 22.1) was
  picked with no game install to check it against, and a tester reported the whole assembly (Daifuku, Kinsuke,
  the torii and the counter) running off the edge of the screen. The default is now (19.7, 22.1) — placed so
  the assembly's left edge lines up with Pluto's own known-visible spot in the Breach and runs right from there
  — but this is still an on-paper guess, not a confirmed fix.
- **New: `pluto_stall` console command** to place the stall live, without a restart. `pluto_stall here` moves
  the whole assembly (Daifuku included) to where you are standing; `pluto_stall <x> <y>` moves it to exact
  coordinates; `pluto_stall` with no arguments reports the current position and how far the assembly reaches
  left/right of it; `pluto_stall save` writes the current position back into the config file so it survives a
  restart.

## 2.20.0 (test build, not released)

- **The Shrine Stall**, in the Breach beside the regular shop: Daifuku (a ginger cat) and Kinsuke (a koi in a
  bowl) run a meta-shop under a red torii gate, selling permanent per-save unlocks for cat items in Hegemony
  credits.
- **Important change for existing players: the ten cat items from the 2.17.0/2.19.0 cat sets now need
  unlocking before they drop.** Ball of Yarn, Catnip Pouch, Hairball, Scratching Post, Toilet Paper Roll, Coffee
  Mug, Jingle Bell Collar, Cone of Shame, Spray Bottle and Feather Teaser no longer appear in any chest, shop or
  reward until bought from the stall (8 credits for the first six, 15 for the last four). Buying one **unlocks it
  permanently** — it leaves the stall's mat and from then on drops normally in the Gungeon like any other loot;
  the purchase is the unlock, it does not also hand you a copy to carry out of the Breach. The mat shows the
  first three still-locked items in a fixed order and is not re-rolled between visits: buying one just moves the
  next locked item up into the free spot, and once fewer than three remain locked the leftover spots are simply
  empty (with all ten unlocked the mat is empty and the stall stays standing).
  Locked items show as undiscovered in the Ammonomicon and flip to the full page on purchase. Unlocks are
  per-save and survive quitting to the menu; a different save slot has its own unlocks, tracked by an extended
  `GungeonFlags` value mirrored by a stable string key so the unlock survives other mods changing the game's
  flag ids.
  Testing-only escape hatch: `StallUnlocksDisabled = true` (config section `Shrine Stall 2.20`) treats every
  item as already unlocked and leaves the stall standing as decoration.
- **Daifuku and Kinsuke** have an intro line, a 25-exchange running back-and-forth (repeats after all 25 have
  been seen once, then a stopper line), and their own purchase/insufficient-credits lines.
- Config: every new number lives in the `Shrine Stall 2.20` section (`StallPriceBallOfYarn`,
  `StallPriceCatnipPouch`, `StallPriceHairball`, `StallPriceScratchingPost`, `StallPriceToiletPaperRoll`,
  `StallPriceCoffeeMug`, `StallPriceJingleBellCollar`, `StallPriceConeOfShame`, `StallPriceSprayBottle`,
  `StallPriceFeatherTeaser`, `StallPosition`, `StallUnlocksDisabled`) and is range-checked at load.
- In-game checklist `docs/shrine-stall-2200-test-checklist.md`; nothing in this round has been seen running (no
  game on the build machine), so placement, draw order, dialogue rendering and the loot gating are all open
  questions for the first in-game pass.

## 2.19.0 (test build, not released)

- **The cat set**: five new pieces in the loot pool for every character, each with its own art, Ammonomicon page and lore about Bogdan and Bianca's house:
  - **Spray Bottle** (gun, C): semi-automatic mist, 8 per clip, 4 damage and 25 knockback over 6 tiles. The first enemy each mist hits gets a small puddle of vanilla water (it conducts), and 35 % of hits make a non-boss enemy flinch out of its attack for 0.5 s. The mist passes straight through harmless and charmed enemies without hurting, pushing or wetting them. `SprayClip`, `SprayCooldown`, `SprayRange`, `SprayDamage`, `SprayKnockback`, `SprayFlinchChance`, `SprayFlinchSeconds`, `SprayReloadSeconds`.
  - **Feather Teaser** (charge gun, B): charge 0.6 s to cast a feather lure 7 tiles out and back, 7 damage on each leg. Normal enemies it catches chase the feather and hold their fire for 1.5 s; bosses are slowed for 0.5 s. You can't fire or reload until the lure returns. `FeatherChargeSeconds`, `FeatherClip`, `FeatherRange`, `FeatherDamage`, `FeatherDistractSeconds`, `FeatherBossSlowSeconds`, `FeatherReloadSeconds`.
  - **Toilet Paper Roll** (active, C): a 4-tile paper streamer across your aim stops up to 12 enemy bullets for 5 s; players and enemies walk through it. Recharges after 400 damage. `TPRechargeDamage`, `TPLength`, `TPSeconds`, `TPHits`.
  - **Cone of Shame** (passive, B): destroys the first enemy bullet within 1.5 tiles in a 70° arc toward your aim, then needs 3 s; a glint over your head marks it ready. `ConeCooldown`, `ConeArcDegrees`, `ConeRadius`.
  - **Coffee Mug** (active, C): thrown 3 tiles (or until it hits something), it shatters into a ring of 10 shards (5 damage each) and leaves a coffee puddle that slows enemies standing in it to half speed for 3 s. Recharges after 300 damage. `CoffeeRechargeDamage`, `CoffeeRange`, `CoffeeShardCount`, `CoffeeShardDamage`, `CoffeeSlowSeconds`.
- **Synergies**: Bath Time (Spray Bottle + Wet Food Can: misting an enemy charmed by the can adds 2 s to its charm, up to 6 s added to that one charm whatever its own length is (a 10 s can charm reaches 16 s, a 20 s Dinner Time charm reaches 26 s); the mist still passes through it and deals no damage; `SprayCharmBonusSeconds`, `SprayCharmMaxBonusSeconds`), Playtime (Feather Teaser + Ball of Yarn: distracted enemies are also tangled, and the tangle wins: a tangled enemy stops where it is instead of chasing the feather, and resumes the chase if the tangle ends while the distraction still has time left), Shredder (Toilet Paper Roll + Scratching Post: a streamer that runs out naturally bursts into confetti for 10 damage along its strip; `TPConfettiDamage`), Matching Cones (Cone of Shame + Coco Blue: Coco wears a cone, which wins over the knight helmet, and holds 1 more bullet; `ConeCocoStuffing`), Espresso (Coffee Mug + Catnip Pouch: using the mug during zoomies adds 2 s; `CoffeeZoomiesBonusSeconds`; both are actives, so you need room for two, e.g. a Backpack).
- **Catnip Pouch**: dropping the pouch mid-zoomies now ends the speed boost at once (before, the speed boost kept running until its timer ran out). Zoomies are one extendable timer so Espresso can lengthen them; the catnap waits until they end.
- None of the pieces hurt, flinch, distract or slow charmed or harmless enemies; the Spray Bottle's mist and the Coffee Mug's mug and shards pass right through them. Bath Time is the one exception: it only lengthens a charm the Wet Food Can already applied.
- Config: every new number lives in the `Cat Set 2.19` section and is range-checked at load.

## 2.18.0 (test build, not released)
- **Yasupen**, Donpen's twin brother, joins the loot pool as a companion (item "Yasupen's Price Tag", quality B). He follows you, belly-slides into enemies every few seconds, makes shops 10 % cheaper while he is with you, and sometimes finds a miracle bargain of 3-5 casings after a room is cleared. Pet him to make Coco happy too.
- **Penguin Pals** (Coco Blue + Yasupen): while Coco is a decoy, Yasupen slides at the enemy chasing him.
- Config section `Yasupen`: `YasupenSlideCooldown`, `YasupenSlideRange`, `YasupenSlideDamage`, `YasupenSlideKnockback`, `YasupenShopDiscount`, `YasupenBargainChance`.

## 2.17.1 (test build, not released)
- **Coco's knight helmet really shows with Ser Junkan**: the helmet swap wrote the animation name the game ignores for Coco's one-direction clips, so he never changed (the Knighted helmet had never shown since 2.15.0). He now wears the gold plumed helmet at every Junkan form.
- **Samurai Puffed Up is fluffy again**: the samurai costume gets its own standing-fur ring that stays off the kimono, alongside the red anger cue.
- **The Katana makes a sound when it swings** (it borrows Blasphemy's swing sound).

## 2.17.0 (test build, not released)

- **Five new cat items** in the loot pool for every character, each with its own Ammonomicon page and lore:
  - **Ball of Yarn** (active, C): a bouncing ball that tangles enemies it touches (stunned, then slowed; bosses only slowed). Walk into it to bat it again. `YarnSeconds`, `YarnDamage`, `YarnTangleSeconds`, `YarnSlowSeconds`, `YarnCooldownDamage`.
  - **Catnip Pouch** (active, C): zoomies (speed + rate of fire, afterimage, catnip leaves), then a short catnap at 80 % speed. `CatnipSeconds`, `CatnipSpeedBonus`, `CatnipFireRateMultiplier`, `CatnapSeconds`, `CatnipCooldownDamage`.
  - **Jingle Bell Collar** (passive, B): a dodge roll rings the bell, erasing nearby enemy bullets and startling non-boss enemies. `BellRadius`, `BellCooldownSeconds`, `BellStunSeconds`.
  - **Hairball** (active, C; id `pluto:hairball_item`, not the Kibble Sack's reload hairball): bursts into a fur cloud where enemy bullets crawl. Bullet patterns keep their shape. `HairballItemRadius`, `HairballItemSeconds`, `HairballItemBulletSpeed`, `HairballItemCooldownDamage`.
  - **Scratching Post** (active, C, once per room): place a post; standing next to it gives more damage and piercing shots. `PostRadius`, `PostDamageMultiplier`, `PostPierce`.
- **Synergies**: Cat's Cradle (Yarn + Coco Blue: the ball lasts twice as long), Nip And Tuck (Catnip + Puffed Up: zoomies start puffed up), Squeaky Clean (Collar + Squeaky Toy: wider jingle), Hack Attack (Hairball + Wet Food Can: the burst charms), Whetstone (Post + Katana: sharper claws).
- **Lore**: funnier Ammonomicon stories for the Wet Food Can, Coco Blue, Squeaky Toy, Puffed Up and Katana.
- **Ammonomicon pages for the Taiyaki Cannon and Katana** show the gun's picture (they were blank).
- Config: every new number lives in the `Cat Items` section and is range-checked at load.

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
