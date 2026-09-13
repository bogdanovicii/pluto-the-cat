# Palette (tools/pixel.py PALETTE)

Keys used on the body (≤ 14 per frame; idle uses 9):

| key | colour | use |
|-----|--------|-----|
| `o` | #1E1614 | silhouette marker on body art (stripped on export); real outline on items/guns/cards |
| `W` `w` `x` | #FAF6EE / #D6CEC6 / #B9B0A8 | white fur: base / shade / deep shade (chin, under-belly, paw rim) |
| `L` `B` `d` | #B4A180 / #8B7A66 / #66524A | tabby: light (warmer, h38) / base (grey-brown taupe, h32) / shadow (cooler, h17) |
| `b` `9` | #3B2C24 / #2A1F1A | mackerel stripes, tail rings, closed eyes / deepest fold line |
| `G` `g` | #9CB64E / #1B2A1B | hazel-green iris / vertical slit pupil |
| `P` `p` `q` | #E8A0B0 / #D46A7A / #F5C6D0 | ear pink, nose / mouth, tongue / pink highlight |
| `J` `j` `U` `u` | wet skin | Wet Pluto alt costume (WET_MAP recolour) |
| `D` `C` `c` | translucent | co-op ghost (GHOST_MAP recolour) |

Rules: shadows go cooler and greyer, highlights warmer and yellower; adjacent tones ≥ 15 value points
apart; the stripe key sits 20 points under the shadow so bars read at 1x; accents (eyes, hearts)
stay under 65 % saturation; the darkest colour is shared by every ramp. Adding a key needs a reason
in a comment. Items reuse the same ramps (kibble tan ↔ tabby light, can silver ↔ white shade).
