# Boss-card bust (normal skin) - pluto-artist record

Status: awaiting the user's approval (2026-09-14). Not wired into make_art yet.

- Generation round 1: `bust.png`, `bust_c2.png`, `bust_c3.png` (brief round 1). Likeness good, composition too wide.
- Generation round 2: `v2/bust*.png` from `brief.txt` (round 2 wording), refs: `boss card example.jpg`, round-1 `bust_c2.png`
  (likeness), `reference/photos/white_spot_on_head.jpeg`. Model gemini-3-pro-image, 16:9, 2K. Sidecar json per image.
- Chosen: `v2/bust_c2.png` (compact pose, pouch close to the chest).
- Conversion (card resolution, 1 art px = 1 card px):

```bash
python3 .claude/skills/pluto-artist/scripts/pixelize.py reference/gemini/bosscard_bust/v2/bust_c2.png \
  --crop 285,64,1880,1389 --grid 181x150 --bg auto --bg-tol 70 --colors 33 \
  --keep a8a058 --keep 806838 --keep 9040b0 --keep 8b5a2b --keep e0909a \
  --canvas 427x240 --place=-2,90 --out reference/gemini/bosscard_bust/bosscard_bust_candidate.png
python3 .claude/skills/pluto-artist/scripts/review_art.py reference/gemini/bosscard_bust/bosscard_bust_candidate.png \
  --kind bosscard --scale 1 --max-colours 40 --mock "Screenshot 2026-09-14 at 18.42.05.png" --mock-rect 438,0,3000,1440
```

- Why the keeps: median cut merged the olive eyes (#a8a058, #806838) into tabby tan, dropped the purple label (#9040b0),
  turned kibble olive and the nose tan; kept accents fix all four.
- Review: automated pass (37 colours, 18.3 % opaque, 0 stray pixels, name area and boss side clear); rubric pass.
  Known nit: the pouch's "ROYAL CANIN" lettering is Gemini's garbled text (reads as the red brand band at card size).
