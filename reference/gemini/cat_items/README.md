# Cat items draft (2026-09-15)

- `ideas.md`: the five item designs (effect, subtitle, synergy).
- `brief.txt`: Gemini prompt, not run. The API returned 429 "prepayment credits are depleted" on both
  gemini-3-pro-image and gemini-3.1-flash-image. Rerun it once credits are topped up and compare against the drawn icons.
- `draw_items.py`: the icons as hand-drawn 16x16 row strings (small-sprite route). Output goes to `build/`:
  `*_icon.png` (1x), `sheet.png` (12x on green, with the existing Nine Lives and Wet Food Can for comparison, plus 1x/2x on a
  dark floor), `*_review.png` (review_art.py), `ingame_mock.png` (native-res floor next to Pluto, x5).
- Review: all five pass review_art.py `--kind item`. Ball of yarn (2,7) and hairball (3,12) each keep one
  intentional single pixel (highlight / stray hair).
- Not wired into the mod: no C#, no Resources copy. Draft only.
