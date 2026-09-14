"""Previews that look like the game: body frames are exported without an outline, so every preview
here adds the 1-px black outline the game draws at runtime, composites on a Gungeon floor tone,
and shows a Pilot-sized reference box. Also writes APNG clips at the real Alexandria frame rates.

Usage: python3 tools/preview.py   (from the project root) -> docs/art-preview/
"""
import os
import sys
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'docs', 'art-preview')

from pixel import img_from_rows, strip_outline, outline_img  # noqa: E402

FLOORS = {'stone': (74, 72, 88, 255), 'light': (150, 140, 128, 255), 'dark': (28, 26, 34, 255)}
PILOT = (16, 23)                 # vanilla Pilot visible size including the runtime outline

# Alexandria playerAnimInfo fps (see docs/research/03b); dodge is forced by the roll time (~13 fps)
FPS = {'idle': 6, 'idle_forward': 6, 'idle_backward': 6, 'run_right': 9, 'run_down': 9, 'run_up': 9,
       'dodge': 13, 'death': 12, 'death_shot': 12, 'item_get': 9, 'pitfall': 15, 'pitfall_return': 11,
       'chest_recover': 12, 'doorway': 10, 'spinfall': 16, 'timefall': 8, 'ghost_idle_front': 4,
       'tablekick_right': 8, 'jetpack_right': 6, 'pet': 6, 'select_idle': 8, 'loaf': 8, 'groom': 8, 'knock': 8}


def game_frame(rows, outlined=True):
    """Row-strings -> RGBA as the game shows a body frame (outline stripped, then re-added)."""
    im = img_from_rows(strip_outline(rows))
    return outline_img(im) if outlined else im


def strip_sheet(clips, path, scale=4, floor='stone', label=True, ref=True):
    """One filmstrip per clip: [(name, frames)] -> PNG. Frames get the runtime outline and sit on the floor."""
    rows = []
    for name, frames in clips:
        ims = [game_frame(f) for f in frames]
        rows.append((name, ims))
    fw = max(i.width for _, ims in rows for i in ims)
    fh = max(i.height for _, ims in rows for i in ims)
    gap = 3
    ref_w = (PILOT[0] + 6) if ref else 0
    cols = max(len(ims) for _, ims in rows)
    W = (ref_w + cols * (fw + gap) + gap) * scale + 90
    H = len(rows) * (fh + gap) * scale + gap * scale
    out = Image.new('RGBA', (W, H), FLOORS[floor])
    d = ImageDraw.Draw(out)
    y = gap * scale
    for name, ims in rows:
        x = 90 + gap * scale
        if ref:
            # Pilot reference box (outline size), bottom-aligned with the frames' bottom margin
            bx, by = x, y + (fh - 1 - PILOT[1]) * scale
            d.rectangle([bx, by, bx + PILOT[0] * scale - 1, by + PILOT[1] * scale - 1], outline=(220, 90, 90, 255), width=1)
            x += ref_w * scale
        for im in ims:
            big = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
            out.alpha_composite(big, (x, y))
            x += (fw + gap) * scale
        if label:
            d.text((6, y + 4), name, fill=(235, 230, 240, 255))
        y += (fh + gap) * scale
    os.makedirs(os.path.dirname(path), exist_ok=True)
    out.save(path)
    return out


def scale_check(frames, path, floors=('stone', 'light', 'dark')):
    """The same frames at 1x / 2x / 3x on three floor tones next to a Pilot-sized box."""
    ims = [game_frame(f) for f in frames]
    fw, fh = ims[0].width, ims[0].height
    row_h = fh * 3 + 8
    W = 40 + sum((fw + 2) * s for s in (1, 2, 3)) * len(ims) + 60
    out = Image.new('RGBA', (W, row_h * len(floors)), (0, 0, 0, 255))
    d = ImageDraw.Draw(out)
    for fi, floor in enumerate(floors):
        y0 = fi * row_h
        d.rectangle([0, y0, W, y0 + row_h - 1], fill=FLOORS[floor])
        x = 8
        d.rectangle([x, y0 + row_h - 4 - PILOT[1], x + PILOT[0] - 1, y0 + row_h - 5], outline=(220, 90, 90, 255))
        x += PILOT[0] + 12
        for s in (1, 2, 3):
            for im in ims:
                big = im.resize((fw * s, fh * s), Image.NEAREST)
                out.alpha_composite(big, (x, y0 + row_h - 4 - fh * s))
                x += (fw + 2) * s
            x += 10
    os.makedirs(os.path.dirname(path), exist_ok=True)
    out.save(path)
    return out


def apng(frames, path, fps, scale=4, floor='stone'):
    """Animated PNG at the real frame rate (Pillow merges identical GIF frames; APNG keeps them)."""
    ims = []
    for f in frames:
        im = game_frame(f)
        bg = Image.new('RGBA', im.size, FLOORS[floor])
        bg.alpha_composite(im)
        ims.append(bg.resize((im.width * scale, im.height * scale), Image.NEAREST))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    ims[0].save(path, save_all=True, append_images=ims[1:], duration=int(1000 / fps), loop=0, disposal=1)


def samurai_rows():
    """Samurai costume idle and run for the breach/variants sheet (built by tools/samurai.py)."""
    import samurai
    clips, _, _ = samurai.build()
    return [('samurai idle', clips['idle']), ('samurai run', clips['run_right'])]


def main():
    import character_anims as A
    os.makedirs(OUT, exist_ok=True)
    body = [(k, v) for k, v in A.CLIPS.items() if v and not k.endswith('_hand') and not k.endswith('_twohands')
            and not k.startswith('ghost_idle_back') and k not in ('dodge_bw', 'dodge_left', 'dodge_left_bw', 'idle_bw',
            'run_right_bw', 'jetpack_right_bw', 'ghost_idle_left', 'tablekick_up', 'tablekick_down', 'slide_up', 'slide_down')]
    strip_sheet(body, os.path.join(OUT, 'character-sheet.png'), scale=3)
    strip_sheet([(k, v) for k, v in A.BREACH_IDLES.items()] +
                [(k, A.CLIPS[k]) for k in ('idle_hand', 'idle_twohands', 'idle_forward_twohands', 'run_right_hand')] +
                samurai_rows(),
                os.path.join(OUT, 'breach-and-variants.png'), scale=3)
    scale_check(A.IDLE_SIDE[:1] + A.IDLE_FRONT[:1] + A.IDLE_BACK[:1] + A.RUN_SIDE[:2] + A.DODGE_SIDE[3:4],
                os.path.join(OUT, 'scale-check.png'))
    for clip in ('idle', 'run_right', 'run_down', 'run_up', 'dodge', 'death', 'item_get', 'idle_forward'):
        apng(A.CLIPS[clip], os.path.join(OUT, 'anim', clip + '.png'), FPS.get(clip, 8))
    for clip in ('loaf', 'groom', 'knock'):
        apng(A.BREACH_IDLES[clip], os.path.join(OUT, 'anim', clip + '.png'), FPS.get(clip, 8))
    print('previews written to', OUT)


if __name__ == '__main__':
    main()
