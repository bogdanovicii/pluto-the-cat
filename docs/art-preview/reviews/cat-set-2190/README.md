# Cat Set 2.19.0 focused art review

Reviewed at native 1x against `reference/gemini/cat_items_2/sheet.png`
(c1) and the approved c2 Spray Bottle / Feather Teaser sheets.  The committed
PNG review sheets include 1x dark/light panels and a nearest-neighbour 4x
inspection panel.  The BlockSpark sheet uses the committed native-pixel mock.

## RED / GREEN evidence

Before the fix, this focused check was red:

```sh
python3 tools/lint_art.py
python3 -m unittest tools.tests.test_weapon_layout.WeaponLayoutTests.test_validate_uses_one_shared_gun_manifest -v
```

- RED: lint reported 17 errors; every non-KO Coco cone frame changed 24
  original Coco pixels.
- RED: the unit test failed because `validate.py` had no shared
  `GUN_MANIFEST`.
- GREEN after the source fix: `lint: 286 frames, 0 error(s), 0 warning(s)`;
  the manifest test reports `Ran 1 test ... OK`.

## Exact review commands and results

```sh
python3 .claude/skills/pluto-artist/scripts/review_art.py PlutoTheCat/Resources/Items/coffee_mug_icon.png --kind item --out docs/art-preview/reviews/cat-set-2190/coffee-mug-review.png
python3 .claude/skills/pluto-artist/scripts/review_art.py PlutoTheCat/Resources/Items/cone_of_shame_icon.png --kind item --allow-stray 14 --out docs/art-preview/reviews/cat-set-2190/cone-icon-review.png
python3 .claude/skills/pluto-artist/scripts/review_art.py PlutoTheCat/Resources/SpriteRoot/WeaponCollection/pluto_spray_bottle_fire_001.png --kind sprite --allow-stray 14 --out docs/art-preview/reviews/cat-set-2190/spray-fire-review.png
python3 .claude/skills/pluto-artist/scripts/review_art.py PlutoTheCat/Resources/SpriteRoot/WeaponCollection/pluto_feather_teaser_fire_001.png --kind sprite --allow-stray 2 --out docs/art-preview/reviews/cat-set-2190/feather-fire-review.png
python3 .claude/skills/pluto-artist/scripts/review_art.py PlutoTheCat/Resources/Companions/coco/cone_idle/coco_cone_idle_001.png --kind sprite --out docs/art-preview/reviews/cat-set-2190/coco-cone-idle-review.png
python3 .claude/skills/pluto-artist/scripts/review_art.py docs/art-preview/reviews/cat-set-2190/block-spark-over-pluto.png --kind sprite --allow-stray 6 --out docs/art-preview/reviews/cat-set-2190/block-spark-review.png
```

All six commands exit 0 with `automated checks pass`.

| Asset | Size | Colours | Opaque | Stray | Allowance rationale |
| --- | ---: | ---: | ---: | ---: | --- |
| Coffee Mug | 16x16 | 6 | 44.5% | 2 | none; the two isolated brown pixels are the escaping coffee droplets |
| Cone icon | 16x16 | 5 | 46.9% | 16 | 14 beyond the default two: symmetric one-pixel taper highlights, two fasteners, and collar shading |
| Spray fire 1 | 26x20 | 10 | 36.2% | 16 | 14 beyond the default two: inherited paw-label, trigger, neck, glass and water highlights; the mist wedge adds none |
| Feather fire | 40x20 | 13 | 22.0% | 4 | 2 beyond the default two: one grip shade, one bell shade, and two feather hue accents |
| Coco cone idle | 19x22 | 8 | 40.2% | 2 | none; two authored facial/fur details |
| BlockSpark over Pluto | 48x52 | 11 | 13.1% | 8 | 6 beyond the default two: Pluto's preserved eye, muzzle, tail-band and fur details; the spark adds none |

Spray fire 2 was also inspected at 1x with:

```sh
python3 .claude/skills/pluto-artist/scripts/review_art.py PlutoTheCat/Resources/SpriteRoot/WeaponCollection/pluto_spray_bottle_fire_002.png --kind sprite --allow-stray 18 --out /tmp/cat-set-spray-fire2-review.png
```

It exits 0 (`26x20`, 10 colours, 36.7% opaque, 20 named inherited/detail
pixels; 18 beyond the default two) and visibly shows the departing puff plus
two droplets.

## Rubric verdict

Every line is **PASS** on the focused second review.

- Character accuracy: N/A for standalone objects.  Coco and Pluto use their
  exact existing source pixels; the lint assertion proves every filled Coco
  pixel retains its value and canvas position.
- Style match: PASS.  Existing palette, dark one-pixel outlines, 2-4 tones per
  material, and top-left highlights match the adjacent Gungeon assets.
- Pixel craft: PASS.  Every asset is hard alpha, native integer pixels, within
  its palette limit, and readable at 1x.  Named single-pixel details above are
  intentional rather than edge noise.
- Composition: PASS.  Coffee is canted with an escaping splash; the cone has a
  broad rim, tapered collar, and fasteners; Spray fire 1 is a connected mist
  wedge and fire 2 a departing puff/droplets; Feather is one straight connected
  grip/string/bell/feather silhouette; the Coco cone projects around the
  preserved body on the exact knight canvas.
- Review evidence: PASS.  The six committed sheets were inspected at native
  1x on dark and light backgrounds and at 4x nearest-neighbour zoom.

`block-spark-over-pluto.png` reuses existing `V4.BLOCK_SPARK[1]`; no glint art
or C# was added.  Its centre is 18 pixels above Pluto's centre, the nearest
whole-pixel placement to `(0,+1.1)` at 16 pixels per game unit.
