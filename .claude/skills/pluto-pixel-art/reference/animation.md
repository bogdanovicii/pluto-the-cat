# Animation

Alexandria fixes the fps and wrap mode per clip folder (frame counts are free):
idle family Loop 6 · run family Loop 9 · dodge Once (fps = frames / roll time ≈ 13) · death 12 ·
death_shot 12 · death_coop 16 · item_get 9 · chest_recover 12 · pitfall 15 · pitfall_return 11 ·
doorway 10 · spinfall 16 · timefall 8 · spit_out 12 · slide Loop 2 · tablekick 8 · pet 6 · jetpack 6 ·
ghost idle 4 · ghost sneeze 8 · breach idles Loop 8.

Keys used in tools/character_anims.py:
- Idle (4): rest, ear flick, squash (head sinks one row into the shoulders; belly and feet stay), rest
  with the tail catching up. Tail lags the body one frame; no two frames identical.
- Run (6): contact (feet on the ground, legs vertical under the hips, stride 1 px wider than idle) → airborne
  (body up 4, legs tucked, head sunk one row, ear tips blown back) → pass (body up 3, legs gathered), then a
  gathered contact. Never diagonal legs: at 1x two outward diagonals read as the splits. Front/back run: one
  foot plants under its hip while the other lifts. `RUN_DY = (0,-4,-3,0,-4,-3)`, `RUN_TAIL_DY = (-1,-2,-4,-1,-2,-4)`.
- Dodge (9 per clip, four clips like vanilla): `PlayerController` picks `dodge_left` when |x| ≥ 0.1
  (`dodge_left_bw` when also rolling up), else `dodge` (down, front view) / `dodge_bw` (up, back view); rolling
  left forces the sprite flip, so side rolls face right. Side: crouch, dive (paws out), four 90° clockwise
  tumbles of the 16x16 `TUCK_SIDE` (head, ears, eye and tail readable; rotate BEFORE padding), curled
  touch-down, landing squash, idle. Down/up: crouch, low, head over (`CROWN` / `BELLY_UP`), upside down
  (`BACK_UP`), back round, landing squash, idle. Never an anonymous ball; tumble parts stay 12-13 px tall
  (no `squash` below 0.8). Frames 0-4 are the invulnerable half.
- Death (8): hit knocked back +1 / -1 (body only, the tail stays), kneel, kneel lower, tip over, lying
  with the flat tail dropping over two frames, hold.
- Pit fall (5): crouch, shrink 0.7, shrink 0.45, 5-px cross, 3-px cross; return mirrors it with an overshoot.
- Squash/stretch conserves mass; anything derived by `squash`/`scale_down`/`rotate` is a base to check
  by eye, not a finished frame.
