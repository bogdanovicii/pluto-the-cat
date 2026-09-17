# Pluto The Cat

Adds **Pluto the Cat** as a new playable Gungeoneer. He is a chunky brown tabby-and-white cat with green eyes, a white blaze, and absolutely no interest in your plans.

## What you get

- **Pluto** in the Breach, selectable like any other Gungeoneer. Slightly faster than the Pilot with a quicker dodge roll.
- **Royal Kibble Sack** (starter gun, infinite ammo): flings dry cat food by the pawful. Kibble bounces once, because kibble always ends up under the fridge. Shooting a secret-room wall cracks it and opens it after a few pawfuls.
- **Wet Food Can** (starter active): throw a tin of the good stuff straight at an enemy. The enemy it hits takes 5 damage and falls in love with Pluto for 10 seconds, fights on his side and takes 20 % more damage; the tin always bursts where it stops (enemy, wall or end of range) and charms every enemy within 2 tiles of the gravy. Bosses are stunned for 3 seconds instead. Recharges after 200 damage.
- **Nine Lives** (starter passive): Pluto has already spent six of his nine lives and starts every run on his seventh. A hit that would kill him is cancelled and the next life begins (one full heart). The ninth life is the last one: no more saves. Configurable (`StartingLife`).
- **Puffed Up** (starter passive): hit Pluto and he bristles for a few seconds, bigger and fuzzier, hitting harder and faster.
- **Cat reflexes**: a longer dodge roll with more invulnerable frames, and he lands on his feet: pits cost no health.
- **Synergies**: Complete Feline Nutrition (kibble homes in with any snack item), Dinner Time (with Charming Rounds, Charm Horn or Yellow Chamber the can's charm lasts twice as long and its gravy splash is 50 % wider), Laser Pointer (dodge rolls leave a red dot enemies chase, with any laser gun), Box Fort (Cardboard Box has no cooldown), Playdate (Squeaky Toy + Dog: squeeze the toy and the Dog bites whatever chases Coco), Squire (Coco Blue + Ser Junkan: +1 Coco stuffing per Junkan rank, Junkan charges Coco's chaser) and Knighted (Squire with a Holy Knight Junkan: Coco wears a tin helmet).
- **Coco Blue** (starter companion): Pluto's plush cat follows him, drops a kibble crumb whenever Pluto gets hurt, and stops any enemy bullet that touches him. After eight blocks he is knocked out for a while (pet him to bring him round early). Pet him (interact next to him) for hearts and a burst of speed; pet him during a fight and he goes decoy.
- **Squeaky Toy** (second starter active; Pluto has two active slots, swap with the active-swap key): sends Coco out as a decoy for a few seconds; enemies chase him while he dodges around the room. Pluto can never drop it. It also appears in chests and shops for every other character: pick it up and Coco follows you too, drop it and he leaves.
- **Samurai Pluto** alt costume: beat Pluto's past (the Vet Visit), then touch the kimono stand just above him in the Breach. Samurai Pluto starts with the **Taiyaki Cannon** and the **Katana** (Blasphemy-style: cuts bullets, sakura wave at full health, reload clears nearby bullets) instead of the kibble bag, and gets his own boss-intro card.
- Enemies that die while in love sometimes drop a kibble bowl that heals half a heart.
- **Five cat items for every Gungeoneer** (found in chests and shops): Ball of Yarn, Catnip Pouch, Jingle Bell Collar, Hairball and Scratching Post, each with an Ammonomicon story and a synergy with Pluto's own kit.
- **Yasupen** (found in the loot pool): Donpen's twin brother follows you, belly-slides into enemies, makes shops 10 % cheaper and sometimes finds a miracle bargain of 3-5 casings after a room is cleared. Pet him and Coco is happy too. Penguin Pals with Coco Blue makes him slide at the enemy chasing Coco.
- **The cat set, for every Gungeoneer** (found in chests and shops), each with an Ammonomicon story:
  - **Spray Bottle** (gun): a short-ranged mist that leaves a puddle of water on the first enemy it hits and sometimes makes it flinch out of its attack. It passes straight through harmless and charmed enemies. It never kept Pluto off the counter either.
  - **Feather Teaser** (charge gun): cast a feather lure that flies out and comes back, hitting each enemy on both legs. Enemies it catches drop everything and chase the feather for 1.5 seconds; bosses are only slowed.
  - **Toilet Paper Roll** (active): unrolls a 4-tile paper streamer across your aim that stops up to 12 enemy bullets for 5 seconds. Everyone walks straight through it.
  - **Cone of Shame** (passive): every 3 seconds the cone catches the next enemy bullet in front of you. A glint over your head says it is ready again.
  - **Coffee Mug** (active): push Bianca's favourite mug off the table. It shatters into a ring of 10 shards and leaves a coffee puddle that slows enemies standing in it for 3 seconds.
- **Cat set synergies**: Bath Time (Spray Bottle + Wet Food Can: misting a charmed enemy makes the charm last 2 s longer, up to 6 s added to that charm however long it already was, without hurting it), Playtime (Feather Teaser + Ball of Yarn: the lure also tangles what it distracts, and the tangle wins: a tangled enemy stays put instead of chasing the feather), Shredder (Toilet Paper Roll + Scratching Post: a streamer that runs its course bursts into damaging confetti), Matching Cones (Cone of Shame + Coco Blue: Coco wears a cone too and holds one more bullet) and Espresso (Coffee Mug + Catnip Pouch: coffee during zoomies adds 2 s; needs room for two actives, e.g. a Backpack).
- **Config**: every cat set number is in the `Cat Set 2.19` section of the BepInEx config (including `SprayCharmMaxBonusSeconds`, the most seconds Bath Time can add to one charm) and is range-checked at load.
- **The Shrine Stall (new in 2.20.0) — important change for existing players**: Daifuku (a ginger cat) and
  Kinsuke (a koi living in a bowl) have set up shop under a red torii gate in the Breach, right beside the
  regular shop. **The ten cat items above — Ball of Yarn, Catnip Pouch, Hairball, Scratching Post, Toilet Paper
  Roll, Coffee Mug, Jingle Bell Collar, Cone of Shame, Spray Bottle and Feather Teaser — no longer drop in
  chests, shops or rewards until you buy them from the stall.** Each unlock is a one-time purchase for your save
  (8 Hegemony credits for the first six, 15 for the last four); buying one unlocks that item permanently, and
  from then on it drops normally in the Gungeon like the rest of Pluto's loot — the purchase is the unlock, not
  a copy handed over in the Breach. The mat shows the first three still-locked items in a fixed order, so buying
  one just moves the next locked item up into the free spot. Until you unlock an item it also shows
  as undiscovered in the Ammonomicon. Daifuku and Kinsuke have their own running back-and-forth if you talk to
  them more than once. If you would rather have everything drop as before, set `StallUnlocksDisabled = true`
  under `[Shrine Stall 2.20]` in the BepInEx config — the stall stays standing as decoration and every item acts
  already unlocked. If the stall is off-screen for you, use the `pluto_stall` console command (2.20.1):
  `pluto_stall here` moves the whole thing (Daifuku included) to where you're standing, `pluto_stall <x> <y>`
  moves it to exact coordinates, `pluto_stall` alone reports the current position, and `pluto_stall save` writes
  it back into the config file so it survives a restart.

## Install (r2modman)

1. Install BepInExPack_EtG, Mod the Gungeon API and Alexandria (r2modman pulls them in as dependencies).
2. Install this mod from Thunderstore, or Settings → Import local mod → pick the zip.
3. Launch modded. Pluto stands in the Breach with the other Gungeoneers.

## Verify it loaded

Open the console (F2 or the ~ key) and look for `[Pluto] Pluto the Cat is ready. Meow.` If you see `[Pluto] Pluto the Cat failed to load`, the line after it is the error; please report it with your BepInEx log.

## Credits

Character, gun and item art drawn from photos of the real Pluto. Built on Alexandria's CharacterAPI and ItemAPI, modelled on Once More Into The Breach and Lich Items.
