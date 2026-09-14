"""Taiyaki Cannon: crops of the chosen Gemini sheets -> pixel-perfect frames on shared canvases.
Run from the repo root: python3 reference/gemini/taiyaki_cannon/convert.py
Gun/fire/reload/projectile come from sheet_c2.png, the bonito puff from sheet.png (see README)."""
import os, subprocess, sys
from PIL import Image
D = 'reference/gemini/taiyaki_cannon'
B = D + '/build'
PX = '.claude/skills/pluto-artist/scripts/pixelize.py'
os.makedirs(B, exist_ok=True)

def px(src, crop, grid, out, colors=10, keep=('6b1f24',), tol=95, palette=None):
    cmd = [sys.executable, PX, f'{D}/{src}', '--crop', crop, '--grid', grid, '--bg', 'auto', '--bg-tol', str(tol),
           '--colors', str(colors), '--out', f'{B}/{out}'] + (['--palette', palette] if palette else [])
    for k in keep:
        cmd += ['--keep', k]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr)
    print(r.stdout.strip().splitlines()[-1])
    return Image.open(f'{B}/{out}').convert('RGBA')

S = 1.024  # display -> source pixels (sheet shown at 2000 px for a 2048 px image)
def box(x0, y0, x1, y1):
    return ','.join(str(int(v * S)) for v in (x0, y0, x1, y1))

# one scale for every gun frame: the idle gun (660 display px wide) becomes 32 px
k = 36 / (660 * S)   # 36 px keeps the waffle pattern readable
def grid_for(x0, y0, x1, y1):
    return f'{round((x1 - x0) * S * k)}x{round((y1 - y0) * S * k)}'

idle_box = (55, 75, 715, 580)
fire_box = (790, 75, 1625, 580)
reload_box = (480, 735, 1430, 1275)
idle = px('sheet_c2.png', box(*idle_box), grid_for(*idle_box), 'idle_art.png', keep=('6b1f24', 'e8b04a'))
fire = px('sheet_c2.png', box(*fire_box), grid_for(*fire_box), 'fire_art.png', keep=('6b1f24', 'e8b04a', 'e0e0e0'), tol=120)
reload = px('sheet_c2.png', box(*reload_box), grid_for(*reload_box), 'reload_art.png', keep=('6b1f24', 'e8b04a', 'f06080', 'f0f0f0'))
mini = px('sheet_c2.png', box(1700, 230, 1875, 365), '14x10', 'mini_taiyaki_001.png', colors=6, keep=('e8b04a', '6b1f24', '5a3514'))
puffs = [px('sheet.png', box(*b), '16x16', f'puff_art_{i}.png', keep=(), tol=110, palette=D + '/puff_palette.txt')
         for i, b in enumerate(((150, 1470, 425, 1705), (580, 1465, 910, 1780), (1060, 1445, 1375, 1745)))]

# shared gun canvas: the idle gun at GX, GY; fire extends right, reload's tube bleeds left into the margin
GX, GY = 10, 2
CW, CH = GX + fire.width + 1, GY + max(idle.height, fire.height) + 1

def canvas():
    return Image.new('RGBA', (CW, CH), (0, 0, 0, 0))

def place(img, x, y):
    c = canvas(); c.paste(img, (x, y), img); return c

frames = {
    'idle': [place(idle, GX, GY)],
    'fire': [place(fire, GX, GY), place(idle, GX - 1, GY), place(idle, GX, GY)],   # burst, recoil, settle
    # reload: gun dips, tube squeezed into the tail (right edges aligned), squeeze again one pixel up, back to idle
    'reload': [place(idle, GX, GY + 1),
               place(reload, GX + idle.width - reload.width, GY + idle.height - reload.height + 1),
               place(reload, GX + idle.width - reload.width, GY + idle.height - reload.height),
               place(idle, GX, GY)],
}
for anim, fr in frames.items():
    for i, f in enumerate(fr, 1):
        f.save(f'{B}/pluto_taiyaki_cannon_{anim}_{i:03d}.png')
fade = puffs[2].copy()
for y in range(fade.height):
    for x in range(fade.width):
        if (x + 2 * y) % 3 == 0:
            fade.putpixel((x, y), (0, 0, 0, 0))
for i, p in enumerate(puffs + [fade], 1):
    p.save(f'{B}/bonito_{i:03d}.png')
# Hand clean-up: the Gemini mini taiyaki is too small to convert. Build the bullet from the approved gun's own
# fish body (rows above the grip), 3x3 block majority, so the bullet matches the gun exactly.
from collections import Counter
body = idle.crop((0, 0, idle.width, 19))
mini = Image.new('RGBA', (body.width // 3, body.height // 3), (0, 0, 0, 0))
for by in range(mini.height):
    for bx in range(mini.width):
        cells = [body.getpixel((bx * 3 + dx, by * 3 + dy)) for dx in range(3) for dy in range(3)]
        solid = [c for c in cells if c[3] == 255]
        if len(solid) >= 4:
            mini.putpixel((bx, by), Counter(solid).most_common(1)[0][0])
mini.save(f'{B}/pluto_mini_taiyaki_001.png')
print('canvas', (CW, CH), 'gun', idle.size, 'fire', fire.size, 'reload', reload.size)

# preview sheet, 10x
rows = [frames['idle'] + frames['fire'], frames['reload'], [mini] + puffs + [fade]]
Z, PAD = 10, 4
W = max(sum(im.width + PAD for im in r) for r in rows) * Z
H = sum(max(im.height for im in r) + PAD for r in rows) * Z
sheet = Image.new('RGBA', (W, H), (70, 66, 80, 255)); y = 0
for r in rows:
    x = 0
    for im in r:
        big = im.resize((im.width * Z, im.height * Z), Image.NEAREST)
        sheet.alpha_composite(big, (x, y)); x += big.width + PAD * Z
    y += (max(im.height for im in r) + PAD) * Z
sheet.save(f'{B}/preview.png'); print('preview', sheet.size)
