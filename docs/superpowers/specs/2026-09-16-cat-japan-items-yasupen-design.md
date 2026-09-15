# Cat and Japan weapons, items and Yasupen: design

Date: 2026-09-16. Status: roster approved by the user; this spec is for review before implementation.
Base: Pluto the Cat 2.17.1 (main `7a4af33`). All work lands on `main`, one new version per round.

## Decisions

| Topic | Decision |
|---|---|
| Scope | 10 pieces (5 cat, 5 Japan) plus one companion |
| Mix | 4 guns and 6 items: per theme 2 guns and 3 items |
| Penguin | **Yasupen**, the twin brother of Don Quijote's Donpen. He looks almost exactly like Donpen, with a different name and two tells: ヤ on his belly instead of ド, and a neon 激安 ("super cheap") price tag on his nightcap |
| Rounds | 2.18.0 Yasupen; 2.19.0 cat set; 2.20.0 Japan set. Each round: art, code, tests, build, drop page, one checklist |
| Loot | Every piece is in the normal loot pool for every character (like the 2.17.0 cat items). Qualities: guns C or B, items C or B, companion B |
| Art pipeline | pluto-artist skill: brief, Gemini generation with reference images, faithful pixel-perfect copy, review with `review_art.py` and the rubric, then show |
| Model and budget | `gemini-3-pro-image` at 2K (same price as 1K, about $0.134 per image; follows references better than `gemini-3.1-flash-image`, $0.101 at 2K). 7 sheets, 2 candidates each: 14 images, about $1.88. One full re-roll keeps the batch under about $4 |
| Config | Every number below is a config key in a new section per round, read through the `PlutoConfigRules` clamp helpers (the `test_companion_kit` rule) |

Numbers are first-pass balance targets, to be tuned after the first in-game test.

## Shared implementation rules

- Items follow the 2.17.0 pattern: one `src/<Name>Item.cs` per item, shared helpers in `CatItemKit.cs`, pure decision logic in a rules file with mono-executed cases.
- Guns follow the Taiyaki Cannon and Katana: art from `reference/art/<gun>/`, grip and muzzle in `tools/weapon_layout.py` (generated `WeaponLayout.cs`), an Ammonomicon page icon in `Ammonomicon Encounter Icon Collection/` (validate.py checks it), `.jtk2d` per frame.
- Companion follows Coco: `CompanionBuilder` prefab, clips with a 1 px margin for the runtime outline, pettable. One-direction clips must be swapped through `DirectionalAnimation.Prefix` (lesson from the 2.17.1 helmet bug).
- Each piece gets one synergy (registered in `PlutoSynergies`, vanilla ids checked by validate.py), Ammonomicon lore in the house tone, and log lines for in-game checks.
- Wording in the game and checklists is written in capitals where the card font needs it; Ammonomicon text is normal case.

## Round 1 (2.18.0): Yasupen, companion

- **Item**: `pluto:yasupen` "Yasupen's Price Tag" (passive companion item, B). Subtitle: "Donpen's Twin Brother".
- **Look**: faithful Donpen twin, 18x22 px body: midnight-blue round penguin, white belly and face, yellow-orange beak and feet, floppy red Santa nightcap with white trim and pom-pom; red ヤ on the belly; a neon-yellow 激安 tag with a hot-pink border stuck crooked on the cap. Clips: `idle` (2), `move` (waddle 2), `slide` (belly slide), `pet` (happy), `cheer` (holds a POP sign). Item icon 16x16: the 激安 tag.
- **Behaviour**:
  - Follows the owner like Coco.
  - Belly slide: in combat, every `YasupenSlideCooldown` 5 s he slides at the nearest enemy within 6 tiles for 8 damage and knockback 30 (bosses take damage, no knockback).
  - Shop discount: while he is with you, shop prices are 10 % lower (`YasupenShopDiscount`).
  - Miracle bargain: after a room is cleared, a 20 % chance (`YasupenBargainChance`) that he cheers with a POP sign and 3-5 casings drop.
  - Pettable; petting him makes Coco happy too (and back).
- **Synergy**: "Penguin Pals" (Yasupen + Coco Blue): while Coco is a decoy, Yasupen slides at Coco's chaser.
- **Lore seed**: Donpen got the store, the fame and the nightcap first. Yasupen got a price-tag sticker and a lifelong grudge. He follows Pluto because a cat that knocks things off shelves is the best bargain hunter he has ever met.
- **In-game checks**: follows and waddles; slides at enemies with the slide clip; shop prices drop 10 %; a POP-sign cheer and casings after some clears; petting works; the ヤ and 激安 tag read at 1x.
- **Art sheet**: `reference/gemini/yasupen/` (reference: Coco's companion sheet `docs/art-preview/coco-helmets.png`).

## Round 2 (2.19.0): cat set

### Spray Bottle (gun, C) `pluto:spray_bottle`
- **Look**: 26x20 px translucent pale-blue plastic spray bottle, white trigger sprayer, pink paw label. Clips: idle, fire (2), reload (3: unscrew, refill, screw on). Projectile: round mist cloud 8-10 px.
- **Mechanic**: semi-auto, 8 shots per clip, 0.35 s cooldown, range 6 tiles, 4 damage, knockback 25. Hits make non-boss enemies flinch: 35 % chance to interrupt their attack and stun 0.5 s (`SprayFlinchChance`). Reload 1.0 s. Leaves a small water puddle on the first hit per shot (vanilla water goop, so electric effects combine).
- **Synergy**: "Bath Time" (Spray Bottle + Wet Food Can): charmed enemies hit by the spray stay charmed 2 s longer.
- **Lore seed**: Bogdan and Bianca bought it to keep Pluto off the kitchen counter. It has never worked. Pluto has decided to see whether it works on other people.

### Feather Teaser (gun, B) `pluto:feather_teaser`
- **Look**: 40x20 px wooden wand, pink foam grip, string with a bunch of pink, yellow and blue feathers and a tiny bell. Clips: idle, charge, fire, empty, return. Projectile: flying feather bunch, 2 rotation frames.
- **Mechanic**: charge 0.6 s, clip 1. The lure flies 7 tiles and returns like a boomerang, 7 damage each way, piercing. Enemies hit are distracted for 1.5 s: they stop firing and walk toward the lure's position (bosses: 0.5 s slow only). Reload 0.4 s once the lure is back.
- **Synergy**: "Playtime" (Feather Teaser + Ball of Yarn): distracted enemies are also tangled.
- **Lore seed**: Every cat alive knows the feather is not real. Every cat alive chases it anyway. Gundead, it turns out, are no smarter.

### Toilet Paper Roll (active, C) `pluto:toilet_paper_roll`
- **Look**: 16x16 icon of a shredded roll with a hanging strip. Effect sprites: streamer segment, paper bits.
- **Mechanic**: 400 damage recharge. Pluto unrolls a paper streamer 4 tiles long, perpendicular to the aim, in front of him. It blocks enemy bullets for 5 s (`TPSeconds`) or 12 hits (`TPHits`), whichever comes first; each hit tears a segment. Enemies can walk through it.
- **Synergy**: "Shredder" (Toilet Paper Roll + Scratching Post): when the streamer ends, it bursts into confetti that deals 10 damage to enemies touching it.
- **Lore seed**: Some cats unroll the toilet paper for fun. Pluto does it for home defence.

### Cone of Shame (passive, B) `pluto:cone_of_shame`
- **Look**: 16x16 icon of a translucent blue vet recovery cone.
- **Mechanic**: every 3 s (`ConeCooldown`), the next enemy bullet entering a 70-degree arc in front of Pluto within 1.5 tiles is destroyed with a plastic "thok" spark. The icon glints when the cone is ready (a small VFX over Pluto's head).
- **Synergy**: "Matching Cones" (Cone of Shame + Coco Blue): Coco wears a little cone too (+1 stuffing).
- **Lore seed**: A souvenir from the Vet's clinic. Pluto hated every second of it. Then a bullet bounced off it, and he started to see its point.

### Coffee Mug (active, C) "Off The Table" `pluto:coffee_mug`
- **Look**: 16x16 icon of a tipping white mug with a red heart. Effect sprites: 4 shards, coffee puddle.
- **Mechanic**: 300 damage recharge. Pluto pushes a mug off an invisible table: it flies 3 tiles in the aim direction and shatters into 10 shards (5 damage each, spread in a ring) and leaves a coffee puddle that slows enemies for 3 s.
- **Synergy**: "Espresso" (Coffee Mug + Catnip Pouch): using the mug during zoomies extends them by 2 s.
- **Lore seed**: Bianca's favourite mug, the one with the heart. Pluto looked her in the eye the whole time.

## Round 3 (2.20.0): Japan set

### Takoyaki Launcher (gun, B) `pluto:takoyaki_launcher`
- **Look**: 34x22 px black cast-iron takoyaki pan mortar with golden sauced balls, wooden grip and a small red lantern. Clips: idle (steam), fire (2), reload (2: skewer flip, sauce). Projectile: flying takoyaki with bonito, 2 rotation frames; burn flame; sauce splat.
- **Mechanic**: lobbed arcing shot of 3 takoyaki in a small spread, 6 damage each plus burn 2 s on landing (vanilla fire effect, not goop fire). Clip 12, 0.5 s cooldown, reload 1.3 s.
- **Synergy**: "Osaka Branch" (Takoyaki Launcher + Yasupen): Yasupen wears a takoyaki costume and his belly slide sets enemies on fire (a nod to Osaka's takoyaki Donpen).
- **Lore seed**: Street food from Dotonbori, fired at street-food speed. The balls are molten inside. Please let them cool before eating the Gundead.

### Ramune Bottle (gun, B) `pluto:ramune_bottle`
- **Look**: 30x16 px aqua codd-neck soda bottle with a marble in the neck and a blue cap ring. Clips: idle, shake (2), fire, marble shot, reload. Projectiles: soda bubbles (3 sizes), glass marble.
- **Mechanic**: charge gun. Hold to shake from 0.2 to 1.2 s; release a spray of 4 to 14 bubbles (scales with the charge), 3 damage each, short range. The fifth shot of every clip fires the marble instead: 30 damage, pierces 2 enemies. Clip 5, reload 1.5 s (the cap pops back on).
- **Synergy**: "Matsuri" (Ramune Bottle + Taiyaki Cannon): festival food. Both guns reload 25 % faster.
- **Lore seed**: The marble keeps the fizz in. Getting it out has defeated tourists for a century. Pluto found a way: shake very, very hard.

### Maneki-neko (passive, B) `pluto:maneki_neko`
- **Look**: 16x16 icon of a white beckoning cat with its left paw raised, red collar, gold bell and a koban coin.
- **Mechanic**: killed enemies have a 20 % chance (`ManekiCasingChance`) to drop an extra casing; shop prices are 10 % lower. With Yasupen, the two discounts stack to at most 25 %.
- **Synergy**: "Lucky Bargain" (Maneki-neko + Yasupen): the discount cap rises to 25 % and bargain casings double.
- **Lore seed**: A left paw raised invites customers; a right paw invites money. This one has its left paw up, which is why Pluto keeps finding shops.

### Daruma Doll (active, C) `pluto:daruma_doll`
- **Look**: 16x16 icon of a red daruma with only the left eye painted. Effect sprite: daruma on its side, rolling.
- **Mechanic**: 500 damage recharge. The doll rolls 8 tiles in the aim direction, bounces off one wall, deals 20 damage and knockback 40 to every enemy it rolls through, then wobbles back to Pluto. The first use in a run paints the left eye (as on the icon). If a floor boss dies while Pluto holds the doll, the right eye is painted and Pluto gets a permanent +10 % damage for the run (once per run; the icon switches to both eyes).
- **Synergy**: "Seven Falls, Eight Rises" (Daruma Doll + Nine Lives): when Nine Lives saves Pluto, the doll recharges fully.
- **Lore seed**: You paint one eye when you make a wish and the other when it comes true. Pluto's wish is private. It involves the Vet.

### Uchiwa Fan (active, C) `pluto:uchiwa_fan`
- **Look**: 16x16 icon of a round paper fan with a red sun and indigo waves on a bamboo handle. Effect sprites: 3 wind gust wisps.
- **Mechanic**: 250 damage recharge. A gust in a 90-degree cone, 4 tiles: enemy bullets inside turn around and fly back at 70 % speed (they stay enemy bullets, so they can still hurt Pluto if he walks into them), and enemies are pushed back 30. Unlike a blank, bullets are redirected, not erased.
- **Synergy**: "Fūrin" (Uchiwa Fan + Jingle Bell Collar): the gust rings the bell and erases the redirected bullets instead.
- **Lore seed**: Summer in Japan is hot, and summer in the Gungeon is hotter. A good fan solves both.

## Art sheets and prompts

Each sheet is generated with `.claude/skills/pluto-artist/scripts/gemini_image.py --model gemini-3-pro-image --size 2K --ratio 16:9 --candidates 2`, using the prompt below (also stored as `brief.txt` next to the output) and these references:
- Item and effect sheets: `reference/gemini/cat_items/ref_existing_icons_16x.png`.
- Gun sheets: `reference/gemini/taiyaki_cannon/ref_kibble_sack_16x.png` and the approved Taiyaki sheet `reference/gemini/taiyaki_cannon/sheet.png`.
- Yasupen: `docs/art-preview/coco-helmets.png`.

### Yasupen (round 1)

Output: `reference/gemini/yasupen/sheet.png` (+ `sheet_c2.png`).

```text
Pixel-art companion sprite sheet for the video game Enter the Gungeon, in exactly the same pixel style, pixel size and shading as the attached reference companion sprites of this mod (the small blue cat plush companion shown zoomed): chunky square pixels, a crisp 1-pixel dark outline (#1E1614), flat cel shading with 3 tones per material, light from the top-left, no gradients, no anti-aliasing, no blur.

The character: "YASUPEN", the twin brother of Donpen, the famous penguin mascot of the Japanese discount store Don Quijote. He must look almost exactly like Donpen: a chubby round midnight-blue penguin (blue #1F3A8A, shade #142760, highlight #3A5BC0) with a big round white belly and face patch (#F4F0E8, shade #D8D0C4), a short wide yellow-orange beak (#F2B53A, shade #C9851E) and yellow-orange flat feet, small black eyes with a white shine pixel, stubby flipper wings, and a floppy red Santa-style nightcap (#D32F2F, shade #9A1F1F) with a white fluffy trim and a white pom-pom that flops to one side. The twin's differences: on his white belly the big single katakana character ヤ in red (instead of Donpen's ド), and a bright neon-yellow handwritten price-tag sticker (#FFE14A with a hot pink #FF3D8B border) stuck crooked on his nightcap with the Japanese word 激安 written on it. He looks cheerful and a bit smug, like he just found a great bargain.

Proportions of a 18x22 pixel character sprite. Draw these separate poses in one row, spaced far apart, all the same size and facing RIGHT:
1. IDLE 1: standing, flippers down.
2. IDLE 2: slight bounce, pom-pom flopped the other way.
3. WADDLE 1: left foot forward, leaning.
4. WADDLE 2: right foot forward, leaning the other way.
5. BELLY SLIDE: lying flat on his belly sliding forward, flippers back, nightcap streaming behind, two speed lines.
6. HAPPY (being petted): eyes closed as happy arcs, flippers up, two small pink hearts.
7. CHEER: holding up a tiny neon-yellow POP price sign above his head.

Below the poses: a small item icon with the proportions of a 16x16 pixel icon: the neon-yellow 激安 price-tag sticker on its own, with a hot pink border and a tiny blue penguin silhouette in the corner.

Background: one flat solid chroma green (#00B140), no scenery, no text other than the ヤ on his belly and the 激安 on the price tags, no labels, no shadows on the background.
```

### Cat items: Toilet Paper Roll, Cone of Shame, Coffee Mug (round 2)

Output: `reference/gemini/cat_items_2/sheet.png` (+ `sheet_c2.png`).

```text
Pixel-art item icon sheet for the video game Enter the Gungeon, in exactly the same pixel style, pixel size, outline weight and shading as the attached reference icons (existing 16x16 item icons of this mod shown at 16x zoom): chunky square pixels, a crisp 1-pixel dark brown-black outline (#1E1614) around every object, flat cel shading with 3 tones per material, light from the top-left, no gradients, no anti-aliasing, no blur, no text.

Top row: THREE separate cat-themed item icons, spaced far apart, each drawn LARGE so every pixel is a clear big square, each with the proportions of a 16x16 pixel icon:
1. "TOILET PAPER ROLL": a white toilet paper roll (white #F4F0E8, shade #D8D0C4, deep shade #A89C8C) seen at a slight angle, the cardboard tube hole visible (tan #B4A180), with a torn strip of paper hanging down from the front and a few tiny shredded paper bits beside it, as if a cat has attacked it.
2. "CONE OF SHAME": a veterinary recovery cone (elizabethan collar) seen from the front, a translucent pale-blue plastic funnel (#CFE6F2, shade #9FC4D8, edge #6E97AE) with a white shine streak, a thin blue binding tape along the wide rim and small snap buttons at the narrow neck.
3. "COFFEE MUG": a white ceramic coffee mug (white #F4F0E8, shade #C9C0B4) with a hand-drawn red heart on its side (#C0392B), tipping over at a 30-degree angle with a small splash of brown coffee (#6B4A2E, light #9C7050) flying out of the rim.

Bottom row: small effect sprites for the same items, each with the proportions of a 6 to 12 pixel sprite, spaced apart:
- four different small white ceramic mug shards (jagged triangles, one with a red heart fragment),
- a short straight segment of torn toilet paper streamer (for a wall made of paper),
- a small round brown coffee puddle seen from above.

All pieces share one palette family with the reference icons (tabby browns, cream whites, soft pink, hazel green). Chunky, readable silhouettes at tiny size, like vanilla Gungeon item icons.

Background: one flat solid chroma green (#00B140), no scenery, no text, no labels, no shadows on the background.
```

### Spray Bottle (round 2)

Output: `reference/gemini/spray_bottle/sheet.png` (+ `sheet_c2.png`).

```text
Pixel-art weapon sprite sheet for the video game Enter the Gungeon, in exactly the same pixel style, pixel size, outline weight and shading as the attached reference gun sprites of this mod (shown zoomed): chunky square pixels, a crisp 1-pixel dark brown-black outline (#1E1614), flat cel shading with 3 tones per material, light from the top-left, no gradients, no anti-aliasing, no blur, no text.

The weapon: "SPRAY BOTTLE", the plastic water spray bottle cat owners use to stop a cat from jumping on the table, now used as a gun. Held sideways, nozzle pointing RIGHT, handle at the lower left where a paw holds it. Proportions of a 26x20 pixel gun sprite. Translucent pale-blue plastic body (#BFE3EE, shade #8CC3D6, deep #5E97B0) showing the water level inside (#6FB7D8) with one white shine streak, a white trigger-sprayer head (#F4F0E8, shade #C9C0B4) with a squeeze trigger in front of the grip and a short nozzle, a small handwritten-style label patch in soft pink (#F5C6D0) with a tiny paw print.

Draw these separate frames in one row, spaced far apart, all at exactly the same size and position so they can be overlaid:
1. IDLE: the bottle at rest.
2. FIRE 1: trigger squeezed, a small cone of white-cyan mist bursting from the nozzle.
3. FIRE 2: trigger releasing, the mist puff drifting away and breaking into droplets.
4. RELOAD 1: bottle tilted back, the sprayer head unscrewed and lifted.
5. RELOAD 2: water pouring in from above as a short stream of blue droplets.
6. RELOAD 3: sprayer head screwed back on with a tiny shine, water level full.

Below the frames, the projectile and effects, each with the proportions of a 6 to 12 pixel sprite: a round mist cloud projectile (white-cyan, soft 3-tone cel shading, still with a dark outline), three small water droplets, and a small splash burst for when it hits.

Background: one flat solid chroma magenta (#FF00FF), no scenery, no text, no labels, no shadows on the background.
```

### Feather Teaser (round 2)

Output: `reference/gemini/feather_teaser/sheet.png` (+ `sheet_c2.png`).

```text
Pixel-art weapon sprite sheet for the video game Enter the Gungeon, in exactly the same pixel style, pixel size, outline weight and shading as the attached reference gun sprites of this mod (shown zoomed): chunky square pixels, a crisp 1-pixel dark brown-black outline (#1E1614), flat cel shading with 3 tones per material, light from the top-left, no gradients, no anti-aliasing, no blur, no text.

The weapon: "FEATHER TEASER", a cat teaser wand toy used as a gun. Held sideways pointing RIGHT, grip at the lower left where a paw holds it. Proportions of a 40x20 pixel gun sprite. A thin flexible stick (wood #C8A266, shade #8B6A3E) with a soft pink foam grip (#F5C6D0, shade #E8A0B0) at the left end; from the tip hangs a short string (#F4F0E8) holding a bunch of three fluffy feathers in bright colours: hot pink (#E8588A), sunny yellow (#F2C94C) and sky blue (#6FB7D8), plus a tiny silver bell (#C9CED6) where the feathers are tied.

Draw these separate frames in one row, spaced far apart, all on the same canvas size with the grip in the same place:
1. IDLE: wand held level, feathers hanging and swaying slightly.
2. CHARGE: wand pulled back and bent, feathers trembling, two small motion lines.
3. FIRE: wand snapped forward, the string and feathers flung out straight to the right, a short whoosh arc.
4. EMPTY: the stick alone with an empty string end curled (the feathers have flown away as the projectile).
5. RETURN: the feathers coming back and re-attaching to the string with a little sparkle.

Below the frames, the projectile, each with the proportions of a 10 to 14 pixel sprite: the feather bunch flying on its own in two rotation frames (tilted up and tilted down) with a short string tail, and a small burst of three single loose feathers for when it hits.

Background: one flat solid chroma green (#00B140), no scenery, no text, no labels, no shadows on the background. Do not use any green in the weapon itself.
```

### Japan items: Maneki-neko, Daruma Doll, Uchiwa Fan (round 3)

Output: `reference/gemini/japan_items/sheet.png` (+ `sheet_c2.png`).

```text
Pixel-art item icon sheet for the video game Enter the Gungeon, in exactly the same pixel style, pixel size, outline weight and shading as the attached reference icons (existing 16x16 item icons of this mod shown at 16x zoom): chunky square pixels, a crisp 1-pixel dark brown-black outline (#1E1614) around every object, flat cel shading with 3 tones per material, light from the top-left, no gradients, no anti-aliasing, no blur, no text.

Top row: THREE separate Japan-themed item icons, spaced far apart, each drawn LARGE so every pixel is a clear big square, each with the proportions of a 16x16 pixel icon:
1. "MANEKI-NEKO": a small white Japanese beckoning lucky cat figurine sitting upright, white ceramic body (#F4F0E8, shade #D0C6B8), LEFT paw raised and bent forward, a red collar (#C0392B) with a round gold bell (#E8B04A, shade #B8742A), holding a gold koban coin against its chest, pink inner ears (#F5C6D0), a happy closed-eye face, one tiny calico patch of orange-brown (#C8763A) on the head.
2. "DARUMA DOLL": a round red Japanese daruma doll (red #C0392B, shade #7E2A22, highlight #E8584A) with a white face area (#F4F0E8), gold eyebrow and beard swirls (#E8B04A), and ONLY THE LEFT EYE painted in as a black dot; the right eye is a blank white circle.
3. "UCHIWA FAN": a round Japanese paper hand fan with a straight bamboo handle (#C8A266, shade #8B6A3E), the round paper face white (#F4F0E8) printed with a simple red sun circle (#C0392B) and three indigo wave lines (#2E3F6E) at the bottom, the bamboo ribs faintly visible through the paper.

Bottom row: small effect sprites, each with the proportions of a 6 to 12 pixel sprite, spaced apart:
- three curved white-and-pale-cyan wind gust wisps (#F4F0E8, #BFE3EE) of different sizes, like swooshes,
- the daruma doll rolled onto its side (same colours) for a rolling frame,
- a single gold koban coin with a shine pixel.

All pieces share one palette family with the reference icons, plus traditional Japanese red, gold, white and indigo. Chunky, readable silhouettes at tiny size, like vanilla Gungeon item icons.

Background: one flat solid chroma green (#00B140), no scenery, no text, no labels, no shadows on the background.
```

### Takoyaki Launcher (round 3)

Output: `reference/gemini/takoyaki_launcher/sheet.png` (+ `sheet_c2.png`).

```text
Pixel-art weapon sprite sheet for the video game Enter the Gungeon, in exactly the same pixel style, pixel size, outline weight and shading as the attached reference gun sprites of this mod (shown zoomed; the golden fish-shaped Taiyaki Cannon is the sister weapon of this one): chunky square pixels, a crisp 1-pixel dark brown-black outline (#1E1614), flat cel shading with 3 tones per material, light from the top-left, no gradients, no anti-aliasing, no blur, no text.

The weapon: "TAKOYAKI LAUNCHER", an Osaka street-food takoyaki grill turned into a mortar gun. Held sideways, pointing RIGHT and slightly upward, grip at the lower left where a paw holds it. Proportions of a 34x22 pixel gun sprite. A black cast-iron takoyaki pan body (#3B3438, shade #26211F, highlight #5E5660) with a row of round half-sphere cups along its top, three golden takoyaki balls sitting in the cups (#D9A441, shade #A8702E) drizzled with dark brown sauce (#5A3514) and white mayo zigzags (#F4F0E8), a short wide barrel at the front like a mortar, a wooden handle grip (#C8A266, shade #8B6A3E), and a small red paper lantern charm (#C0392B) hanging under the barrel.

Draw these separate frames in one row, spaced far apart, all on the same canvas size with the grip in the same place:
1. IDLE: loaded, steam rising gently from the balls in two small wisps.
2. FIRE 1: the barrel kicks up, a puff of steam and a takoyaki ball launching out of the muzzle.
3. FIRE 2: recoil settling, one cup now empty.
4. RELOAD 1: a wooden skewer pick (#C8A266) flipping a new raw batter ball in a cup.
5. RELOAD 2: the balls turning golden, sauce drizzled on, a little sparkle.

Below the frames, the projectile and effects, each with the proportions of a 8 to 14 pixel sprite: a single flying takoyaki ball with sauce, mayo and a few pale bonito flakes on top (two rotation frames), a small orange-red burn flame, and a splat of sauce for the landing.

Background: one flat solid chroma magenta (#FF00FF), no scenery, no text, no labels, no shadows on the background.
```

### Ramune Bottle (round 3)

Output: `reference/gemini/ramune_bottle/sheet.png` (+ `sheet_c2.png`).

```text
Pixel-art weapon sprite sheet for the video game Enter the Gungeon, in exactly the same pixel style, pixel size, outline weight and shading as the attached reference gun sprites of this mod (shown zoomed): chunky square pixels, a crisp 1-pixel dark brown-black outline (#1E1614), flat cel shading with 3 tones per material, light from the top-left, no gradients, no anti-aliasing, no blur, no text.

The weapon: "RAMUNE BOTTLE", a Japanese ramune soda bottle used as a gun. Held sideways with the neck pointing RIGHT, the round bottom at the lower left where a paw holds it. Proportions of a 30x16 pixel gun sprite. Classic codd-neck bottle of pale aqua glass (#A8E0DC, shade #6FB8B4, deep #3E8A88) with clear fizzy soda inside showing small white bubbles, the pinched neck holding a clear glass marble (#E6F4F8 with a white shine pixel), a blue plastic cap ring (#2E6FD0) at the mouth, and a small paper label with a simple red and blue wave stripe (#C0392B, #2E3F6E).

Draw these separate frames in one row, spaced far apart, all on the same canvas size with the grip in the same place:
1. IDLE: bottle at rest, a few bubbles.
2. SHAKE 1: bottle tilted up, bubbles multiplying, two short shake lines.
3. SHAKE 2: bottle tilted down, the soda foaming white inside.
4. FIRE: a wide burst of white foam and bubbles blasting out of the mouth.
5. MARBLE SHOT: the marble shooting out of the neck with a white pop star.
6. RELOAD: the blue cap pressed back on with a small "pop" burst of bubbles and the marble back in the neck.

Below the frames, the projectiles, each with the proportions of a 4 to 10 pixel sprite: three round soda bubbles of different sizes (pale aqua with a white shine), the glass marble projectile with a short motion streak, and a small foam splash for when it hits.

Background: one flat solid chroma magenta (#FF00FF), no scenery, no text, no labels, no shadows on the background.
```


## Testing and acceptance

- Per round: pure rules (charge scaling, discount caps, flinch chance, cone cooldown, eye state) in mono-executed cases; config keys clamped; validate.py checks icons, Ammonomicon page icons, synergy ids and frame counts; `./build.sh` green.
- Art: every final sprite passes `review_art.py` and the rubric and is shown in an in-game mock before the user sees it.
- In-game: one checklist per round on the drop page, built from the per-piece checks above.

## Risks

- **Donpen likeness**: the user chose a faithful twin with a different name. The belly letter, the price tag and the name keep him distinct, but he stays close to a trademarked mascot in a public mod.
- **Text at pixel size**: ヤ and 激安 must survive the copy to 18x22 and 16x16. If they do not read, the tag becomes a plain neon tag with a pink "!" and the belly letter stays.
- **Distract and flinch** are new enemy-control effects; they must never apply to bosses beyond the stated slow, and must restore enemy state on room exit (the ownership rules from 2.16.3).
