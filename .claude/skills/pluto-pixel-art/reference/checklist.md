# Before committing art

- [ ] `tools/lint_art.py`: 0 errors; every warning understood.
- [ ] Looked at `docs/art-preview/scale-check.png` at 1x on all three floors: silhouette reads as a cat,
      head spot, blaze, rings and ears visible, nothing merges with the outline.
- [ ] `character-sheet.png`: feet on the same row in every grounded frame, no clipped ear tips, tail
      visible and behind the body, no holes between parts.
- [ ] `anim/run_right.png` and `anim/idle.png` at real speed: a hop, not a sine; no stray pixel blinking.
- [ ] Hand variants: `_hand` shows one paw on the chest, `_twohands` two, base none.
- [ ] Items and guns keep their drawn outline; body/breach/hand PNGs contain no #1E1614 (validate checks).
- [ ] Fur layers regenerated (count printed by make_art), `tools/validate.py` passes, `./build.sh` passes.
- [ ] CHANGELOG entry, version bump in `PlutoTheCat/src/Plugin.cs` and `thunderstore/manifest.json`.
