"""Taiyaki Cannon reload v2 (2.16.x, user: "Taiyaki reload animation should be improved; also add something at the
end like the hairball").

The old clip pasted a different Gemini fish for two frames (the gun changed shape) and ran 4 frames at 8 fps = 0.5 s
against a 0.9 s reload. This clip keeps the approved idle gun pixel-for-pixel (the grip never moves) and hand-draws
the story on top of it in row-strings, one frame per 0.1 s:

  1 a Churu stick pack appears behind the tail      6 the empty tube pulls out, the shine reaches the mouth
  2 its nozzle pushes into the tail notch           7 a bead of Churu swells in the mouth
  3-5 the tube is squeezed flat from its sealed     8 the drop falls from the jaw (the Churu drop finisher)
      end while a shine runs from tail to mouth     9 full: a glint on the top fin

Also draws the Churu drop projectile (pluto_churu_drop_001.png) and writes the previews into docs/art-preview/weapons/.
Run from the repo root: python3 reference/gemini/taiyaki_cannon/reload_v2.py
The Churu tube follows the tube in the chosen Gemini sheet (sheet_c2.png, reload row): white pack, pink label,
beige puree at the nozzle.
"""
import os
import sys

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
ART = os.path.join(ROOT, 'reference', 'art', 'taiyaki_cannon')
PREVIEW = os.path.join(ROOT, 'docs', 'art-preview', 'weapons')
FPS = 10                      # 9 frames / 10 fps = 0.9 s = TaiyakiCannonGun reloadTime

# Palette: gun tones are the approved gun's own; the tube and puree ramps are new (three tones, top-left light).
PAL = {
    'a': (0x33, 0x18, 0x07),  # gun outline, reused for the tube so both read as one drawing
    'W': (0xf6, 0xf1, 0xe8),  # tube white
    'S': (0xc4, 0xb6, 0xb0),  # tube shadow (cooler grey)
    'P': (0xea, 0x62, 0x80),  # label pink
    'D': (0xa8, 0x3c, 0x5a),  # label shadow
    'Q': (0xf2, 0xcf, 0x84),  # Churu puree
    'R': (0xc2, 0x8c, 0x48),  # puree shadow
    'H': (0xff, 0xf6, 0xd2),  # glint
    'b': (0xf3, 0xbb, 0x56),  # gun highlight
    'e': (0xcc, 0x89, 0x35),  # gun base
}
GLOW = {(0xcc, 0x89, 0x35): PAL['b'], (0xd1, 0x8e, 0x38): PAL['b'], (0xcf, 0x8b, 0x35): PAL['b'],
        (0xaf, 0x73, 0x2e): PAL['e'], (0x8f, 0x4e, 0x1d): (0xaf, 0x73, 0x2e), (0x84, 0x4b, 0x1d): (0xaf, 0x73, 0x2e),
        (0x93, 0x52, 0x1d): (0xaf, 0x73, 0x2e)}

# Churu stick pack, nozzle to the right. Body columns 1-8 squeeze flat from the sealed end (column 0).
TUBE = [
    "aaaaaaaaaa...",
    "aWWWPPPWWWa..",
    "aWWWPPPWWWWaa",
    "aWWWPPPWWWWQa",
    "aSSSDDDSSSSaa",
    "aSSSDDDSSSa..",
    "aaaaaaaaaa...",
]
MID = 3                        # the tube's centre row (nozzle row); a flattened column keeps only MID-1..MID+1
DROP = [                       # projectile, 7x8, also hangs from the jaw in frame 8
    "...a...",
    "..aQa..",
    ".aQHRa.",
    "aQHQQRa",
    "aQQQQRa",
    "aQQQRRa",
    ".aRRRa.",
    "..aaa..",
]
BEAD = [                       # frame 7: puree swelling out of the mouth
    ".aa.",
    "aQQa",
    "aHQa",
    "aQRa",
    ".aa.",
]
GLINT = [".H.", "HbH", ".H."]


def squeezed(k):
    """Tube with its first k body columns flattened to one row (the sealed end is rolled up)."""
    rows = [list(r) for r in TUBE]
    if k == 0:
        return [''.join(r) for r in rows]
    for x in range(0, k + 1):
        for y in range(len(rows)):
            if abs(y - MID) > 1:
                rows[y][x] = '.'
        rows[MID - 1][x] = 'a'
        rows[MID + 1][x] = 'a'
        rows[MID][x] = 'a' if x == 0 else ('D' if TUBE[MID][x] == 'P' else 'S')
    return [''.join(r) for r in rows]


def stamp(im, rows, x0, y0):
    for y, row in enumerate(rows):
        for x, k in enumerate(row):
            if k == '.':
                continue
            px, py = x0 + x, y0 + y
            if not (0 < px < im.width - 1 and 0 < py < im.height - 1):
                raise ValueError(f'pixel ({px},{py}) leaves the canvas margin')
            im.putpixel((px, py), PAL[k] + (255,))


def glow(im, x0, x1):
    """Shine band: body tones inside the silhouette lighten one step between columns x0..x1."""
    for y in range(im.height):
        for x in range(x0, x1 + 1):
            p = im.getpixel((x, y))
            if p[3] and p[:3] in GLOW:
                im.putpixel((x, y), GLOW[p[:3]] + (255,))


def frames():
    idle = Image.open(os.path.join(ART, 'pluto_taiyaki_cannon_idle_001.png')).convert('RGBA')
    TX, TY = 1, 14 - MID      # tube top-left as it arrives (nozzle on the tail notch, row 14); pushed in = TX + 2
    plan = [
        dict(tube=(0, TX)),
        dict(tube=(0, TX + 2)),
        dict(tube=(3, TX + 2), glow=(14, 20)),
        dict(tube=(6, TX + 2), glow=(21, 28)),
        dict(tube=(9, TX + 2), glow=(29, 35)),
        dict(tube=(9, TX), glow=(36, 42)),
        dict(bead=(45, 13)),
        dict(drop=(42, 21)),
        dict(glint=(32, 1)),
    ]
    out = []
    for step in plan:
        f = idle.copy()
        if 'glow' in step:
            glow(f, *step['glow'])
        if 'tube' in step:
            k, x = step['tube']
            stamp(f, squeezed(k), x, TY)
        if 'bead' in step:
            stamp(f, BEAD, *step['bead'])
        if 'drop' in step:
            stamp(f, DROP, *step['drop'])
        if 'glint' in step:
            stamp(f, GLINT, *step['glint'])
        out.append(f)
    return idle, out


def drop_sprite():
    im = Image.new('RGBA', (len(DROP[0]) + 2, len(DROP) + 2), (0, 0, 0, 0))
    stamp(im, DROP, 1, 1)
    return im


def on(im, bg, scale):
    c = Image.new('RGBA', im.size, bg)
    c.alpha_composite(im)
    return c.resize((im.width * scale, im.height * scale), Image.NEAREST)


FLOORS = [(74, 72, 88, 255), (150, 140, 128, 255), (28, 26, 34, 255)]


def previews(idle, clip, drop):
    os.makedirs(PREVIEW, exist_ok=True)
    # strip: 1x on three floors on top, then the frames at 6x with frame numbers and time stamps
    Z, PAD = 6, 2
    n = len(clip)
    w1 = n * (idle.width + PAD)
    big_w = n * (idle.width + PAD) * Z
    sheet = Image.new('RGBA', (big_w, 3 * (idle.height + PAD) + (idle.height + PAD) * Z + 24), (24, 22, 28, 255))
    for r, fl in enumerate(FLOORS):
        for i, f in enumerate(clip):
            sheet.alpha_composite(on(f, fl, 1), (i * (idle.width + PAD), r * (idle.height + PAD)))
    y0 = 3 * (idle.height + PAD) + 12
    d = ImageDraw.Draw(sheet)
    for i, f in enumerate(clip):
        x = i * (idle.width + PAD) * Z
        sheet.alpha_composite(on(f, FLOORS[0], Z), (x, y0))
        d.text((x + 4, y0 + 2), f'{i + 1}  {i / FPS:.1f}s', fill=(240, 235, 220, 255))
    d.text((w1 + 10, 4), f'reload {n} frames @ {FPS} fps = {n / FPS:.1f} s; 1x on stone/light/dark, then 6x', fill=(240, 235, 220, 255))
    sheet.alpha_composite(on(drop, FLOORS[0], Z), (w1 + 10, 20))
    sheet.convert('RGB').save(os.path.join(PREVIEW, 'taiyaki_cannon-reload-strip.png'), optimize=True)

    # motion at the real fps: 0.5 s idle, the reload, 0.5 s idle (APNG keeps every frame; GIF for quick viewing)
    loop = [idle] * 5 + clip + [idle] * 5
    ims = [on(f, FLOORS[0], 4) for f in loop]
    ims[0].save(os.path.join(PREVIEW, 'taiyaki_cannon-reload.png'), save_all=True, append_images=ims[1:],
                duration=int(1000 / FPS), loop=0, disposal=1)
    ims[0].convert('RGB').save(os.path.join(PREVIEW, 'taiyaki_cannon-reload.gif'), save_all=True,
                               append_images=[i.convert('RGB') for i in ims[1:]], duration=int(1000 / FPS), loop=0)
    inhand(loop)


def inhand(loop):
    """Samurai Pluto aiming right with the gun in his paw, the drop falling and splashing after the clip ends."""
    import weapon_layout as WL
    import weapon_preview as WP
    body, paw = WP.bodies()['samurai']
    spec = WL.WEAPONS['taiyaki_cannon']
    S = 4
    W, H = 150, 60
    bx, by = 14, 22
    anchor = ((bx + WP.HAND_ANCHOR[0] + 1) * S, (by + WP.HAND_ANCHOR[1] + 1) * S)
    bonito = [Image.open(os.path.join(ART, f'bonito_{i:03d}.png')).convert('RGBA') for i in range(1, 5)]
    drop = drop_sprite()
    n_clip_end = 5 + 9
    ims = []
    for i, f in enumerate(loop + [loop[-1]] * 4):
        c = Image.new('RGBA', (W * S, H * S), FLOORS[0])
        c.alpha_composite(body.resize((body.width * S, body.height * S), Image.NEAREST), (bx * S, by * S))
        to_canvas = WP.place_gun(c, f, spec['hand'], anchor, 0, False)
        c.alpha_composite(paw.resize((paw.width * S, paw.height * S), Image.NEAREST),
                          (int(anchor[0] - paw.width * S / 2), int(anchor[1] - paw.height * S / 2)))
        if i >= n_clip_end:   # finisher: the drop leaves the mouth toward the aim and splashes 3.5 u away
            t = i - n_clip_end
            mx, my = to_canvas(*spec['muzzle'])
            if t < 3:
                c.alpha_composite(drop.resize((drop.width * S, drop.height * S), Image.NEAREST),
                                  (int(mx + t * 18 * S), int(my - drop.height * S / 2 + t * 2 * S)))
            elif t - 3 < len(bonito):
                b = bonito[t - 3]
                c.alpha_composite(b.resize((b.width * S, b.height * S), Image.NEAREST),
                                  (int(mx + 56 * S), int(my - b.height * S / 2 + 6 * S)))
        ims.append(c)
    ims[0].save(os.path.join(PREVIEW, 'taiyaki_cannon-reload-inhand.png'), save_all=True, append_images=ims[1:],
                duration=int(1000 / FPS), loop=0, disposal=1)
    ims[n_clip_end - 5 + 4].convert('RGB').save(os.path.join(PREVIEW, 'taiyaki_cannon-reload-inhand-still.png'))


def main():
    idle, clip = frames()
    for old in os.listdir(ART):
        if old.startswith('pluto_taiyaki_cannon_reload_'):
            os.remove(os.path.join(ART, old))
    for i, f in enumerate(clip, 1):
        f.save(os.path.join(ART, f'pluto_taiyaki_cannon_reload_{i:03d}.png'))
    drop = drop_sprite()
    drop.save(os.path.join(ART, 'pluto_churu_drop_001.png'))
    previews(idle, clip, drop)
    print(f'{len(clip)} reload frames, drop {drop.size}, previews in {PREVIEW}')


if __name__ == '__main__':
    main()
