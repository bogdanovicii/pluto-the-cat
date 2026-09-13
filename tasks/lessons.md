# Lessons

## 2026-09-13 — Alexandria CharacterAPI altGuns
- Alexandria 0.5.10 `HandleLoadout` iterates `altGun` without a null check; the list only exists when characterdata.txt has an `<altGuns>` block. Always include it, even with no alt skin.
- `Loader.BuildCharacter` catches its own exceptions and returns null. Check the return value before logging success; never print "ready" unconditionally.
- Static validation caught none of this. Runtime API contracts (what a loader tolerates) need a real in-game run; keep the remote Steam-machine test loop as the final gate.

## 2026-09-13 — vanilla item ids
- Never guess a vanilla console id. Every id must be looked up in `docs/research/gungeon_items_idmap.txt` (Cardboard Box is `box`, the cheese is `partially_eaten_cheese`). `tools/validate.py` now enforces this for synergy ids.
- Optional features (synergies) register last and each in its own try/catch, so one bad id costs a synergy, not the character.

## 2026-09-13 — AI art vs hand-drawn sprites
- Gemini-generated sprites pixelized to 16-34 px lost to the hand-authored row-string art in a side-by-side; the user chose hand-drawn. Do not replace sprites with generated images; at most use generations as colour/shape references.
- Before spending API calls on sprite-sized art, show a comparison sheet (AI vs current) at 7x and let the user decide. Large painted pieces (boss card, win pic, icon) are a separate decision.
- "Better graphics" now means raising the craft of the hand-drawn pipeline (palette ramps, outlines, animation timing), not swapping the source of the art.

## 2026-09-14 — read the engine before drawing for it
- Enter the Gungeon adds the 1-px black outline to player and hand sprites at runtime; vanilla body frames have no outline. A baked outline gives a double outline in game. Check the renderer's decompiled code (outline, anchor, hand semantics) before an art pass, not after.
- `_bw` clips are the back-view side sprite (aiming up-diagonal), `_hand` means the body draws its free hand (one-handed gun), `_twohands` means no gun. Names in the Alexandria table are not self-explanatory; look them up in `PlayerController.GetBaseAnimationName`.
- Frames are anchored bottom-left: hops are drawn inside the canvas, so the canvas needs headroom (24x24, not 24x20).

## 2026-09-14 — art passes A-C
- A strict canvas (`pad`/`overlay` raising on dropped pixels) found five silent clipping bugs on the first run. Keep transforms strict for body art; give item/VFX art explicit lenient aliases instead of loosening the rule.
- Lint metrics must match the craft rule they encode: a "changed pixel %" flicker check flagged every legitimate hop; the rule is "a lone pixel toggling", so the check aligns frames and looks for a single-pixel difference.
- Previews must render what the game renders: without the simulated runtime outline the outline-free frames look wrong and judgement drifts.
- Verify engine claims from the decompiled source before shipping a change that depends on them: `PlayerController.Start` and `AIActor.Start` (with `procedurallyOutlined = true` by default) both add the runtime outline, which is why Pluto and Coco ship outline-free. The Re-ETG raw dump on GitHub answers such questions in one fetch.
