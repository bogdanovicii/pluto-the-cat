# Art targets

Where each piece is drawn, and the rules that follow from that. Verify a target against the renderer before
adding it here (the decompiled game: https://raw.githubusercontent.com/FlowSand/Re-ETG/master/Assets/_RawDump/C%23/Assembly-CSharp/).

## Boss intro card - `PlutoTheCat/Characters/Pluto/bosscard_001.png` (+ `_002`... animated)
- Renderer: `BossCardUIController` draws the player's `BosscardSprites` on `playerSprite` (dfGUI ZOrder 14) OVER the
  boss art (ZOrder 6); both textures are stretched to the screen from the top-left, nothing crops. The player
  layer appears about 1 s in and slides in from the left over 0.5 s. Alexandria loads every file whose name
  contains `bosscard_` into `data.bossCard` and animates them at `BosscardSpriteFPS`.
- Canvas 427x240, transparent everywhere except the portrait. Vanilla player cards: Convict art in (8,96)-(174,240),
  ~90 % transparent; Guide (17,106)-(161,240). Boss art lives in the right half (x > 190).
- Rules: <= 30 % opaque (validate.py), nothing in the top-left name area (x < 190, y < 90), art inside the left
  45 %, bleeding off the bottom (and optionally left) edge. A detailed bust at card resolution with a bold dark
  outline and cel shading, posed with the character's weapon - see the user's `boss card example.jpg` (Pilot).
- Never a scaled-up in-game sprite: at full-screen stretch each sprite pixel becomes a huge block.
- The card font drops lowercase letters in some glyphs ("The Vet" -> "Te Vet"); names/subtitles go in capitals.

## Win picture - `win_pic_001.png`, `win_pic_junkan.png` - 115x71
## Face card - `facecard.png` 34x34 (Ammonomicon/character select face), foyer card frames `foyercard/`
## Icon - `thunderstore/icon.png` 256x256; minimap `icon.png` 9x9

## Guns (`Resources/SpriteRoot/WeaponCollection/`) - keep a drawn 1 px outline; every frame needs a `.jtk2d` with
PrimaryHand + Casing; all frames of one gun share one canvas; barrelOffset in C# matches the muzzle pixel.
## Items and projectiles - drawn outline kept; projectiles 6-16 px; item icons ~16-20 px.
## Body frames (Pluto 24x26, Coco) - NO baked outline (the game adds it at runtime); row-strings via pluto-pixel-art.

## Pluto prompt block (Gemini)
Pluto, a chubby adult cat with GREY-BROWN tabby fur (cool taupe brown with near-black mackerel stripes, NOT orange,
NOT ginger), a forehead M marking, a white blaze between the eyes running down to a white muzzle, white chest and
white paws, a small white oval spot on top of his head between the ears surrounded by tabby, big ears with pink
inner ears, hazel-green eyes with vertical slit pupils, a pink nose, and a long raccoon-ringed tail with light and
near-black bands and a dark tip. Palette anchors: tabby #8B7A66 (light #B4A180, shadow #66524A), stripes #3B2C24,
white #FAF6EE (shade #D6CEC6), eyes #9CB64E, pink #E8A0B0, outline #1E1614.
Royal Kibble Sack: a white and silver ROYAL CANIN dry-food pouch, red band with the five-dot crown, purple round
label with a grey cat, zip top torn open with kibble spilling.
