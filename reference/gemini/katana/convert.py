"""Katana: crops of sheet_c2.png -> pixel-perfect frames aligned on the handle end and the blade top.
Run from the repo root: python3 reference/gemini/katana/convert.py"""
import os, subprocess, sys
from PIL import Image
D = 'reference/gemini/katana'; B = D + '/build'
PX = '.claude/skills/pluto-artist/scripts/pixelize.py'
os.makedirs(B, exist_ok=True)
S = 1.024                     # display (2000) -> source (2048)
k = 40 / (895 * S)            # the idle katana (895 display px) becomes 40 px: keeps the wrap and guard

def px(crop, out, grid=None, colors=10, keep=(), tol=110, palette=D + '/palette.txt'):
    x0, y0, x1, y1 = crop
    g = grid or f'{max(1, round((x1 - x0) * S * k))}x{max(1, round((y1 - y0) * S * k))}'
    cmd = [sys.executable, PX, f'{D}/sheet_c2.png', '--crop', ','.join(str(int(v * S)) for v in crop), '--grid', g,
           '--bg', 'auto', '--bg-tol', str(tol), '--colors', str(colors), '--out', f'{B}/{out}'] + (['--palette', palette] if palette else [])
    for c in keep:
        cmd += ['--keep', c]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr)
    print(r.stdout.strip().splitlines()[-1])
    return Image.open(f'{B}/{out}').convert('RGBA')

STEEL = ('e8ecf4', 'a8b0c0', '707888', 'e0a830', '8a5a18', '181418', 'f8f8f8')
# (crop box, handle-end x, blade-top y) in display coordinates
FR = {
    'idle':   ((55, 55, 950, 235), 55, 55),
    'swing1': ((55, 520, 950, 795), 55, 520),
    'swing2': ((55, 870, 950, 1240), 55, 870),
    'swing3': ((985, 555, 1880, 1250), 985, 870),
    'reload1': ((40, 1310, 950, 1490), 40, 1310),
    'reload2': ((40, 1600, 950, 1780), 40, 1600),
}
arts = {n: px(box, f'{n}_art.png', keep=STEEL) for n, (box, hx, ty) in FR.items()}
offs = {n: (round((box[0] - hx) * S * k), round((box[1] - ty) * S * k)) for n, (box, hx, ty) in FR.items()}
GX = 1 - min(o[0] for o in offs.values())
GY = 1 - min(o[1] for o in offs.values())
CW = max(GX + offs[n][0] + a.width for n, a in arts.items()) + 1
CH = max(GY + offs[n][1] + a.height for n, a in arts.items()) + 1

def frame(n):
    c = Image.new('RGBA', (CW, CH), (0, 0, 0, 0))
    c.paste(arts[n], (GX + offs[n][0], GY + offs[n][1]), arts[n]); return c

GOLD = {(0xe0, 0xa8, 0x30), (0x8a, 0x5a, 0x18), (0xf0, 0xd0, 0x70)}
DARK = {(0x18, 0x14, 0x18), (0x3a, 0x34, 0x40)}

def wrap_handle(img):
    """Hand clean-up: paint the black-and-white diamond wrap on the handle (left of the gold guard) that the
    conversion merged into solid black. White marks every 3 px on the handle's middle row, offset rows above/below."""
    w, h = img.size
    px = img.load()
    # the guard is the tall gold disc: the column with the most gold pixels (the pommel cap is a single pixel)
    counts = {x: sum(1 for y in range(h) if px[x, y][3] and px[x, y][:3] in GOLD) for x in range(w)}
    guard_x = max(counts, key=lambda x: (counts[x], -x)) if any(counts.values()) else None
    if guard_x is None or counts[guard_x] < 2:
        return img
    rows = [y for y in range(h) if sum(1 for x in range(guard_x) if px[x, y][3] and px[x, y][:3] in DARK) >= 4]
    if len(rows) < 2:
        return img
    mid = rows[len(rows) // 2]
    xs = [x for x in range(guard_x) if px[x, mid][3] and px[x, mid][:3] in DARK]
    for i, x in enumerate(range(min(xs) + 2, max(xs), 3)):
        if px[x, mid][:3] in DARK:
            px[x, mid] = (0xf8, 0xf8, 0xf8, 255)
        yy = mid - 1 if i % 2 else mid + 1
        if yy in rows and px[x + 1, yy][3] and px[x + 1, yy][:3] in DARK:
            px[x + 1, yy] = (0xa8, 0xb0, 0xc0, 255)
    return img

frame_raw = frame
def frame(n):
    return wrap_handle(frame_raw(n))

frames = {'idle': [frame('idle')], 'fire': [frame('swing1'), frame('swing2'), frame('swing3')],
          'reload': [frame('reload1'), frame('reload2'), frame('idle')]}
for anim, fr in frames.items():
    for i, f in enumerate(fr, 1):
        f.save(f'{B}/pluto_katana_{anim}_{i:03d}.png')

crescent = px((1155, 1410, 1490, 1785), 'crescent_art.png', grid='12x14', colors=4, keep=('ffffff', '60e8e0'), tol=140)
petals = px((1545, 1450, 1800, 1760), 'petals_art.png', grid='6x7', colors=4, keep=('f7b7c8', 'e98aa6'), tol=120)
wave = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
# Hand clean-up: the converted crescent is too thin at 16 px; draw it as the difference of two circles
from PIL import ImageDraw
outer = Image.new('L', (16, 16), 0); ImageDraw.Draw(outer).ellipse([3, 1, 15, 14], fill=255)
inner = Image.new('L', (16, 16), 0); ImageDraw.Draw(inner).ellipse([0, 1, 11, 14], fill=255)
for y in range(16):
    for x in range(16):
        if outer.getpixel((x, y)) and not inner.getpixel((x, y)):
            edge = any(not (0 <= x + dx < 16 and 0 <= y + dy < 16) or not outer.getpixel((x + dx, y + dy))
                       for dx, dy in ((1, 0), (0, 1), (0, -1)))
            wave.putpixel((x, y), (0x60, 0xe8, 0xe0, 255) if edge else (0xf8, 0xf8, 0xf8, 255))
# Hand clean-up: petals are 2x2 squares in the two spec pinks, trailing behind (left of) the crescent
for (x, y, col) in ((1, 4, (0xf7, 0xb7, 0xc8, 255)), (0, 9, (0xe9, 0x8a, 0xa6, 255)), (3, 12, (0xf7, 0xb7, 0xc8, 255))):
    for dx in (0, 1):
        for dy in (0, 1):
            wave.putpixel((x + dx, y + dy), col)
wave.save(f'{B}/pluto_katana_wave_001.png')
print('canvas', (CW, CH), 'hand anchor (handle end)', (GX, GY), {n: a.size for n, a in arts.items()})

rows = [frames['idle'] + frames['fire'], frames['reload'] + [wave]]
Z, PAD = 10, 3
W = max(sum(im.width + PAD for im in r) for r in rows) * Z
H = sum(max(im.height for im in r) + PAD for r in rows) * Z
sheet = Image.new('RGBA', (W, H), (70, 66, 80, 255)); y = 0
for r in rows:
    x = 0
    for im in r:
        big = im.resize((im.width * Z, im.height * Z), Image.NEAREST); sheet.alpha_composite(big, (x, y)); x += big.width + PAD * Z
    y += (max(im.height for im in r) + PAD) * Z
sheet.save(f'{B}/preview.png'); print('preview', sheet.size)
