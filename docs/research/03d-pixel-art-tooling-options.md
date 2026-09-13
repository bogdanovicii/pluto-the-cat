# Pixel-art tooling options for the Pluto pipeline (macOS, state as of 2026-09-14)

Scope: what could complement the Python + Pillow row-string pipeline (`tools/pixel.py`, `poses.py`, `character_anims.py`; 24x20 character canvas, 61 clips, items 16-34 px, guns 32x18). Nothing was downloaded or installed; facts come from the local machine, GitHub API (`gh`), Homebrew API and vendor docs. Claims I could not verify are marked *(unverified)*.

## 0. Recommended toolset (summary)

1. Keep the row-strings as the single source of truth; add `tools/import_png.py` so any editor's 1x PNG can be snapped back to palette keys (`rows_from_img` already exists; the snap step is verified exact, section 3.4).
2. Editor for human touch-ups: **LibreSprite** (free, GPL-2, macOS arm64 zip, keeps Aseprite's `--batch/--save-as/--sheet/--data/--split-layers/--script` CLI, JavaScript scripts). Upgrade to **Aseprite** ($19.99, or a free personal source build with Xcode) only if Lua scripting, `--split-tags`, slices/pivots or modern UI matter.
3. Pure-Python additions, no new dependencies: `lint_art.py` (section 4), APNG previews at the real Alexandria fps (section 3.7), onion-skin contact sheets, a 60-line RotSprite for non-90° rotations.
4. References: study The Spriters Resource sheets online for proportions/timing; do not commit or ship rips. In-game dump needs a small custom BepInEx debug plugin (old ETGMod `Dump.cs` port) run on the Steam machine.
5. Capture all of it in a project skill `.claude/skills/pluto-pixel-art/` (section 6).

## 1. Machine state (verified 2026-09-13)

| Check | Result |
|---|---|
| `ls /Applications` | No Aseprite, LibreSprite, Pixelorama, Piskel, Pyxel Edit. Xcode.app present (needed for an Aseprite source build). |
| `which aseprite libresprite pixelorama` | none |
| `brew list` | no cmake, ninja, ffmpeg, gifsicle, imagemagick; `node` and `gh` present |
| Homebrew casks | `aseprite`, `libresprite`, `piskel`: no cask. `pixelorama`: cask exists (1.2.1) but **disabled 2026-09-01, reason `fails_gatekeeper_check`** — install from the GitHub DMG instead. |
| Python | 3.11.5, Pillow 12.1.1; **no numpy, imageio, apng** |

## 2. Editors with scripting/CLI

| Editor | Licence / price | macOS | CLI | Scripting | Fit for "touch up, keep Python source of truth" | Effort |
|---|---|---|---|---|---|---|
| **Aseprite** 1.3.x | Proprietary EULA; $19.99 (Steam/itch/Humble/Gumroad). Source on GitHub; compiling for personal use is allowed, redistribution is not. | Yes (.dmg with purchase, or self-build) | Best: `-b --save-as`, `--split-layers`, `--split-tags`, `--sheet --data --format json-array`, `--filename-format '{title}-{tag}-{frame000}'`, `--scale`, `--palette`, `--color-mode indexed`, `--trim`, `--frame-range`, `--layer/--ignore-layer`, `--script x.lua --script-param k=v` | Lua (`Image{fromFile=}`, `getPixel`, `pixels()` iterator, `app.pixelColor.rgbaR..`, `Sprite:saveAs`) | Excellent: `--data` JSON carries per-frame `duration` and slice `pivot`; a 30-line Lua script can write row-strings directly. | Buy: 10 min. Source build: macOS 15.2+, Xcode 16.3+, SDK 15.4, CMake + Ninja (not installed), prebuilt Skia `aseprite-m124`; `cmake -DLAF_BACKEND=skia -DSKIA_DIR=... -G Ninja .. && ninja aseprite` → `build/bin/aseprite`; ~1-2 h + ~1 GB downloads. |
| **LibreSprite** v1.1 (2023-12-03; v1.2 pre-release 2025-03-02) | GPL-2.0, free | `libresprite-development-macos-arm64.zip` on GitHub releases (unsigned; expect a Gatekeeper right-click-Open / `xattr -d com.apple.quarantine` step *(unverified)*) | Verified in `src/app/app_options.cpp`: `--shell --batch --save-as --scale --data --sheet --sheet-width/height/type/pack --split-layers --script` (no `--split-tags`, no `--filename-format`) | **JavaScript** (`data/scripts/*.js`; API: `app.activeSprite`, `Image.getPixel/putPixel/getImageData`, `Sprite.save`, `Dialog`) | Good and free: same batch export as 2016-era Aseprite; missing tags-per-file and JSON frame durations are irrelevant because durations come from the Alexandria fps table anyway. | Download + unzip: 10 min. |
| **Pixelorama** v1.2.2 (2026-09-09, Godot 4.7.2) | MIT, free | `Pixelorama-Mac.dmg` (GitHub releases / itch / Steam) | `Pixelorama --headless -- -e -o out.png --split-layers --frames 1-4 --scale 1 --json file.pxo` (user options: `--export/-e`, `--spritesheet/-s`, `--output/-o`, `--scale`, `--frames/-f`, `--direction/-d`, `--json`, `--split-layers`, `--size`, `--framecount`) | Extensions (GDScript), no batch scripting API | OK: `.pxo` (≥1.0) is a ZIP with `data.json` + `image_data/` (raw cel bytes), readable from Python with `zipfile` + Pillow `frombytes`; also exports `.aseprite` since 1.2.2. RotSprite was requested (discussion #563) but not implemented. | 10 min. Modern, nicest free GUI on macOS. |
| **Pyxel Edit** | Free old version + paid beta ($9 per third-party listings; official site only says "next big update will be paid") | Adobe AIR app, Windows/Mac | none | none | Poor: tile/tilemap oriented, AIR runtime, no automation. | skip |
| **GraphicsGale** | Free | **Windows only** | `.gal` batch via GUI only | none | n/a | skip |
| **Piskel** | Apache-2.0, free | Web app (piskelapp.com); desktop builds are old nw.js bundles *(unverified age)* | `cli/` in the repo: `piskel-cli file.piskel --scale 5 --frame 3` (node; needs a repo checkout + `npm install`) | none | Usable via the web app: `.piskel` is JSON (`modelVersion`, `piskel{name,fps,width,height,hiddenFrames,layers[]}`; each layer is a JSON *string* with `chunks[{layout[[frame idx]], base64PNG}]`) → 20 lines of Python decode it into frames. | 30 min for an importer. |

Round-trip design (any editor): export/save each frame as a 1x RGBA PNG named `<clip>_<NNN>.png` → `import_png.py` runs `rows_from_img` (unknown colours become `?`, snap first with the fixed-palette quantize of 3.4) → rewrite the row list in the Python source (or, better, move poses to a `.txt`/`.py` data file per clip so imports are mechanical and diffs stay readable). Never let PNGs in `PlutoTheCat/` become the source; `make_art.py` regenerates them.

## 3. Python-side techniques and libraries

### 3.1 RotSprite (pixel-perfect rotation)
- No maintained package: `pypi.org/project/rotsprite` does not exist; `rotpixels` (nesdev forum, 2010, pineight.com zip) is Python 2 + PIL, "very slow", no licence; `salmonmoose/SpriteRotator` is C + SDL, no licence. Lospec's Pixel Art Rotator is a web tool. Aseprite's "Clean Rotate" is a paid extension.
- Algorithm (Xenowhirl, per Wikipedia): (1) upscale 8x with Scale2x run three times, treating *similar* colours as equal; (2) optionally search a sub-pixel offset that avoids sampling boundary pixels; (3) rotate with nearest-neighbour while shrinking back to 1x (sample the centre of each 8x8 block); (4) restore single-pixel details lost in step 3.
- Simple implementation for this project (~60 lines, no deps): `scale2x(rows)` on palette keys (see 3.2) ×3 → `img.rotate(angle, Image.NEAREST, expand=False)` → sample every 8th pixel at offset 4 → `rows_from_img`. At 24x20 (192x160 upscaled) pure Python takes milliseconds. Only needed for non-90° angles: current `rotate()` uses 90° steps, which are already exact; `Image.transpose` is the lossless path for those.

### 3.2 Scale2x / EPX / hqx (preview only; the game does nearest)
- EPX rule per source pixel P with neighbours A(up) B(right) C(left) D(down): start with 4 copies of P; `1=A if C==A and C!=D and A!=B`; `2=B if A==B and A!=C and B!=D`; `3=C if D==C and D!=B and C!=A`; `4=D if B==D and B!=A and D!=C`; if three of A,B,C,D are equal, keep P. Works directly on key characters: 15 lines, no new colours.
- `ScaleNx` 2026.8.6 (PyPI, Unlicense, pure Python, Py≥3.4): `scaleNx(nested_list, 2|3, sfx)` on `list[list[list[int]]]` (Scale2x/3x + SFX variants).
- `hqx` 1.0 (PyPI, LGPL-2.1, Py≥3.10, Pillow): `hqx.hq2x(pil_image)`, RGB only — composite over a flat colour or handle alpha separately. Introduces blended colours, so use only for "how would it look smoothed" previews, never for assets.

### 3.3 Image-to-pixel-art tools (references only)
- `sedthh/pyxelate` (MIT, `pip install git+https://github.com/sedthh/pyxelate.git`; scikit-image/numba stack, slow). The project already has `tools/pixelize.py` (box downscale + median-cut quantize + palette snap + outline) and `tasks/lessons.md` records that generated/pixelized references lost to hand-drawn art. Low value; skip.

### 3.4 Pillow palette management (verified on Pillow 12.1.1)
```python
cols = [v[:3] for v in PALETTE.values() if v and v[3] == 255]          # 47 opaque keys
pal = Image.new('P', (1, 1)); flat = [c for rgb in cols for c in rgb]
pal.putpalette(flat + [0, 0, 0] * (256 - len(cols)))
q = im.convert('RGB').quantize(palette=pal, dither=Image.Dither.NONE)   # exact: 0 mismatches
```
`quantize(palette=…)` accepts only RGB/L, so re-apply alpha from the source; an off-by-3 tabby colour snapped to the right key. Keep RGBA output for tk2d; indexed PNG buys nothing in-game. Store ramps as ordered tuples (`RAMPS = {'tabby': 'dBLl', 'white': 'xwWK', …}`) so lint (section 4) can check hue-shifted shading instead of the ad-hoc `shade()` rules.

### 3.5 Cut-out / puppet animation in code
`character_anims.py` already is a puppet rig: parts (`SIDE_LEG`, `LEG_TUCK`, `TAIL_A/B`) placed with per-frame `(dx, dy)` and `flip_h`. Formalise it the way Spine/DragonBones do (bones = parts with a pivot, slots = z-order, keys per frame), but with integer offsets: `FRAME = [('tail', 0, 7, 'A'), ('body', 3, -2, None), ('leg_b', 8, 16, 'tuck'), …]` plus a z-order list, a per-part pivot (feet row 19), and derived directions by mirroring offsets. Aseprite-side equivalents: one layer per part + tags per clip (Dalichrome modular workflow; emb33r's joint-separated base).

### 3.6 Sub-pixel animation
Draw the moving part at 3x (72x60), shift it by one 3x pixel, `resize(…, Image.BOX)` back and snap with 3.4 — the smear pixel gets the in-between colour of the ramp. Use sparingly (tail tip, eye blink, breathing chest); this is the classic "add an in-between smear frame" technique (Oberg; Tiny Warrior Games).

### 3.7 Onion skin and real-fps previews
- Onion skin: tint previous frame red / next frame green at ~30 % (`Image.blend` on solid tints, then `alpha_composite` under the current frame) in the contact sheet; add a 1-px grid and a baseline at row 19.
- Real fps (Alexandria `SpriteHandler.playerAnimInfo`, already in `01-custom-character-research.md`): idle 6, run 9, dodge 12, death 12, death_coop 16, item_get 9, pitfall 15, pitfall_return 11, spinfall 16, timefall 8, tablekick 8, doorway 10, ghost idle 4, sneeze 8, slide 2, breach idles 8 → `duration = 1000 // fps` ms.
- APNG (verified, 4 frames, 3.4 KB at 6x): `frames[0].save('idle.png', save_all=True, append_images=frames[1:], duration=167, loop=0, disposal=1)`. RGBA preserved; browsers and GitHub render it.
- GIF gotcha (verified): Pillow **merges identical consecutive frames** (idle's 4 frames → 3, durations summed) and needs `P` mode + `transparency=` + `disposal=2` for transparent backgrounds. Use APNG for review, GIF only for chat.

## 4. Lint / QA for pixel art in code

Existing tools: **SpriteLint** (itch, $4.99, offline browser tool, closed source: stray pixels, outline gaps, transparent pinholes, banding, palette outliers; JSON/CSV/annotated PNG output). **findOrphans.lua** (MIT, Aseprite): orphan = pixel with no 8-neighbour of the same colour. **Adopt Pixels** (paid Aseprite extension). **aseprite-ai-artist MCP `validate`**: off-palette, orphans, broken/doubled outlines, banding, unintended AA, odd-pixel asymmetry, untagged frames, inconsistent timing, cross-frame volume drift. None read row-strings, so write `tools/lint_art.py` (pure Python; a prototype over 57 clips / 260 frames ran in 0.08 s):

| Check | Algorithm | Prototype result on current art |
|---|---|---|
| Palette conformance / colour budget | `rows_from_img` yields `?`; count distinct keys per frame (limit e.g. 12) | max 10 colours/frame ✔ |
| Stray pixel | opaque pixel with **no opaque** 8-neighbour; plus outline pixel with no outline 8-neighbour | naive same-colour orphan rule = 2280 hits (every 1-px eye/highlight) → useless at 24x20; use the two stricter rules |
| Open outline | non-outline opaque pixel 4-adjacent to transparent; whitelist keys (ghost `D/C/c`, tail rings) | 1928 hits, dominated by intentional soft edges → needs the whitelist |
| Doubles / jaggies | 2x2 blocks of `o`; along each outline contour, run-length sequence irregularities (…1,2,1,1,2…) | 153 2x2 outline blocks |
| Banding | colour-boundary columns identical across ≥3 consecutive rows inside a ramp; "pillow" = concentric ramp rings | not prototyped |
| Pivot / feet line | bottom-most opaque row must be 19 on grounded frames; horizontal centre-of-mass drift ≤1 px in idles | all run clips show feet at rows 17-19 — the hop is intentional, so the rule takes a per-clip airborne mask (Alexandria itself flags dodge's first half `groundedFrame=false`) |
| Flicker | changed-pixel fraction between consecutive frames, per-clip thresholds (idle ≤15 %, run ≤40 %) | 107 pairs >50 % today, mostly death/dodge tumbles (legitimate) |
| Volume drift | opaque pixel count within ±15 % inside a clip | not prototyped |
| Symmetry | front/back idles: left half vs mirrored right half, tolerance 2 px | not prototyped |

Output: text report + an annotated contact sheet (red boxes at findings), wired into `validate.py`/`build.sh` as warnings first, errors once tuned. Effort: 150-250 lines, half a day including tuning against the current clips.

## 5. Reference acquisition (vanilla sprites for proportions and timing)

| Option | How | Legal/ethical notes | Effort |
|---|---|---|---|
| The Spriters Resource | `spriters-resource.com/pc_computer/enterthegungeon/` — sheets for The Pilot, Hunter, Bullet, Bullet Kin, Items (Static), etc. View online, count frames per row, measure proportions. | Sprites are Dodge Roll/Devolver copyright; the site hosts rips for study. Study only: never commit sheets to the repo or ship any vanilla pixels in the mod. | 0 (open in browser) |
| Public custom-character repos | Already done in `01-custom-character-research.md` (23x24 CCM frames, 17x19 Alexandria frames, fps table, Shade's frame counts). | Fine — the mod authors published them. | done |
| In-game dump (Mod the Gungeon) | The **old** ETGMod (pre-BepInEx) console had `dump sprites true` (+ `dump sprites metadata`, `dump packer`) implemented in `Assembly-CSharp.Base.mm/src/Core/Assets/Dump.cs` (MIT): writes `Resources/DUMPsprites/<collection>.png` and per-definition PNGs as collections load. The `tk2ddump`/`dfdump` names on ModWorkshop belong to that era. The current BepInEx MtG API tree (SpecialAPI, MIT) has **no dump code** (tree grep + code search negative), so it is not available today. | Port `Dump.cs` into a tiny debug BepInEx plugin (iterate `tk2dSpriteCollectionData.spriteDefinitions`, `Graphics.Blit` to a RenderTexture, `ReadPixels`, crop by `uvs`, `EncodeToPNG`) and run it once on the Steam machine that owns the game. Output stays local, personal study only. | ~150 lines C#, 1-2 h, plus one in-game run |
| Unity asset extraction | **AssetRipper 2.0.0** (GPL-3, 2026-08-24, `AssetRipper_mac_arm64.tar.xz`, Unity 3.5-6000.4, web UI) on the machine that owns the game → Texture2D atlases + tk2d `MonoBehaviour` data (uvs). **AssetStudio** (MIT) is archived (2023-01-21) and Windows-only .NET. | Same as above: personal study, no redistribution. Dodge Roll aided the original Mod the Gungeon; mods are "not official". | 1 h; atlases still need slicing via the tk2d uvs, so the in-game dump is simpler |

## 6. A reusable Claude Code skill — yes, as a project skill

Rationale: the palette, canvas sizes, clip list and fps table are project-specific, and `tasks/lessons.md` already holds art rules that should be loaded whenever art is touched. Per the Claude Code skills docs: SKILL.md = YAML frontmatter (`name`, `description`, optional `paths`, `allowed-tools`, `disable-model-invocation`, `context: fork`) + body under 500 lines / ~2k tokens for a frequently loaded skill; supporting files load on demand; `scripts/` are executed, not read; reference bundled files with `${CLAUDE_SKILL_DIR}`. Local precedent: `~/.claude/skills/binancebot-trader/` (SKILL.md + `references/*.md`).

```
.claude/skills/pluto-pixel-art/          # project skill, committed
├── SKILL.md            # frontmatter: name, description ("sprite, pixel art, clip, palette, contact sheet, Pluto art…"),
│                       #   paths: "tools/*.py, PlutoTheCat/Characters/**", allowed-tools: Bash(python3 tools/*)
│                       # body: workflow (edit rows → make_art → lint → preview → validate), hard rules from lessons.md,
│                       #   the 10-line checklist, links to references
├── reference/palette.md      # keys, ramps, when to use each, hue-shift rule, translucency keys
├── reference/etg-specs.md    # canvases (24x20, 34x34, 38x38, 427x240, 9x9, gun 32x18 + .jtk2d), clip list, fps/wrap table, pivot rules
├── reference/animation.md    # frame counts per clip type, hop/contact/pass cycle, dodge invulnerable half, timing charts
├── reference/checklist.md    # pre-commit review: silhouette at 1x, outline closed, ≤N colours, feet on row 19, flicker, mirrored directions
├── scripts/lint_art.py       # section 4
├── scripts/preview.py        # contact sheet + onion skin + APNG at real fps
├── scripts/import_png.py     # PNG → rows round trip (fixed-palette snap)
├── scripts/rotsprite.py      # section 3.1
└── assets/templates/         # blank 24x20 / 16 / 34 / 32x18 row-string templates with guide comments
```
Keep generic algorithms in `scripts/` so the same skill can be copied to another pixel project by swapping `reference/`. Effort: 2-3 h to assemble once the scripts exist.

## Sources
- Aseprite CLI: https://www.aseprite.org/docs/cli/ · Lua Image API: https://github.com/aseprite/api/blob/main/api/image.md · FAQ/price/EULA: https://www.aseprite.org/faq/ · macOS build: https://github.com/aseprite/aseprite/blob/main/INSTALL.md · licence history: https://en.wikipedia.org/wiki/Aseprite
- LibreSprite: https://github.com/LibreSprite/LibreSprite (GPL-2.0; `src/app/app_options.cpp`, `data/scripts/*.js`, SCRIPTING.md) · releases: https://github.com/LibreSprite/LibreSprite/releases
- Pixelorama: https://github.com/Orama-Interactive/Pixelorama (MIT) · CLI: https://pixelorama.org/user_manual/cli/ · .pxo format: https://pixelorama.org/blog/pixelorama-1.0-is-out/ · RotSprite request: https://github.com/Orama-Interactive/Pixelorama/discussions/563 · Homebrew cask status: https://formulae.brew.sh/api/cask/pixelorama.json
- Pyxel Edit: https://pyxeledit.com/about.php · Lospec software list: https://lospec.com/pixel-art-software-list/ · GraphicsGale (Windows): https://graphicsgale.com/us/download.html
- Piskel: https://github.com/piskelapp/piskel (Apache-2.0; `cli/`, `src/js/utils/serialization/Serializer.js`)
- RotSprite/EPX/hqx: https://en.wikipedia.org/wiki/Pixel-art_scaling_algorithms · rotpixels: https://forums.nesdev.org/viewtopic.php?t=8628 · SpriteRotator: https://github.com/salmonmoose/SpriteRotator · Lospec rotator: https://lospec.com/pixel-art-rotator/
- PyPI: https://pypi.org/project/hqx/ · https://pypi.org/project/ScaleNx/ (https://github.com/Dnyarri/PixelArtScaling) · pyxelate: https://github.com/sedthh/pyxelate
- Pillow: https://pillow.readthedocs.io/en/stable/reference/Image.html (quantize, Dither) · https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html (APNG/GIF save options)
- Sub-pixel animation: https://someanimatorwannabe.substack.com/p/animator-techniques-sub-pixel-animation · https://tinywarriorgames.com/2019/01/04/game-development-pixel-art-sub-pixel-animation/ · modular workflow: https://medium.com/@dalichrome/the-best-modular-character-workflow-with-aseprite-78a29124b8c4
- Lint prior art: https://mtw1man2.itch.io/spritelint-catch-pixel-art-mistakes-before-you-ship-browser-tool · https://shemake.dev/tech/viewing/Aseprite_findOrphans · https://glama.ai/mcp/servers/with-pebbly/aseprite-ai-artist/tools/validate · doubles/jaggies: https://lospec.com/pixel-art-tutorials/3-pixelart-techniques-common-mistakes-doubles-jaggies-outline-by-mortmort
- References: https://www.spriters-resource.com/pc_computer/enterthegungeon/ · old ETGMod dump: https://github.com/ModTheGungeon/ETGMod (`Assembly-CSharp.Base.mm/src/Core/Assets/Dump.cs`, `src/ETGGUI/ETGModConsole.cs`) · current MtG API: https://github.com/SpecialAPI/ModTheGungeonAPI · ModWorkshop `tk2ddump` notes: https://modworkshop.net/mod/17528 · EtG wiki modding page: https://enterthegungeon.wiki.gg/wiki/Modding · AssetRipper: https://github.com/AssetRipper/AssetRipper · AssetStudio: https://github.com/Perfare/AssetStudio
- Skills format: https://code.claude.com/docs/en/skills · https://github.com/anthropics/skills
