# Samurai boss-card bust - pluto-artist record

- Generation: `bust.png`, `bust_c2.png`, `bust_c3.png` from `brief.txt`; refs: `reference/gemini/bosscard_bust/v2/bust_c2.png`
  (pose, framing, likeness), `reference/gemini/samurai_costume/sheet_c2.png` (costume), `reference/gemini/katana/sheet_c2.png` (sword).
- Chosen: `bust_c2.png` (clean crest, katana close to the chest). Gemini copied the normal bust's framing, so the conversion
  uses the normal card's exact crop, grid and placement (both cards line up):

```bash
python3 .claude/skills/pluto-artist/scripts/pixelize.py reference/gemini/samurai_bust/bust_c2.png \
  --crop 285,64,1880,1389 --grid 181x150 --bg auto --bg-tol 70 --colors 30 \
  --keep a8a058 --keep 806838 --keep e0909a --keep 2b3a67 --keep 1c2648 --keep b3202a --keep 7a1418 --keep d8dce8 --keep e0a830 \
  --canvas 427x240 --place=-2,90 --out reference/gemini/samurai_bust/samurai_bust_candidate.png
```

- Review: automated pass (37 colours, 16.7 % opaque, 0 stray pixels, name area and boss side clear); rubric pass.
- Source of truth for the mod: `reference/art/bosscard/samurai.png` (make_art copies it to `samuraicard_001.png`).
