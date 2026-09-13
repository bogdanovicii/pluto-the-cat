"""Static validation of the mod package: art folders, sizes, ids, embedded resources.

Run from the project root: python3 tools/validate.py
Exits non-zero on any failure.
"""
import os
import re
import sys
import json
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAR = os.path.join(ROOT, 'PlutoTheCat', 'Characters', 'Pluto')
NSS = os.path.join(CHAR, 'newspritesetup')
RES = os.path.join(ROOT, 'PlutoTheCat', 'Resources')
DLL = os.path.join(ROOT, 'PlutoTheCat', 'bin', 'Release', 'PlutoTheCat.dll')

sys.path.insert(0, os.path.join(ROOT, 'tools'))
from PIL import Image  # noqa: E402

# Alexandria SpriteHandler.playerAnimInfo keys (the clip names the loader knows about).
REQUIRED_CLIPS = """chest_recover death death_coop death_shot dodge dodge_bw dodge_left dodge_left_bw doorway
ghost_idle_back ghost_idle_back_left ghost_idle_back_right ghost_idle_front ghost_idle_left ghost_idle_right
ghost_sneeze_left ghost_sneeze_right idle idle_backward idle_backward_hand idle_backward_twohands idle_bw
idle_bw_twohands idle_forward idle_forward_hand idle_forward_twohands idle_hand idle_twohands item_get
jetpack_down jetpack_down_hand jetpack_right jetpack_right_bw jetpack_right_hand jetpack_up pet pitfall
pitfall_down pitfall_return run_down run_down_hand run_down_twohands run_right run_right_hand run_right_twohands
run_right_bw run_right_bw_twohands run_up run_up_hand run_up_twohands slide_right slide_up slide_down spinfall
spit_out tablekick_down tablekick_down_hand tablekick_right tablekick_right_hand tablekick_up timefall""".split()

FIXED_SIZES = {
    'facecard.png': (34, 34), 'icon.png': (9, 9), 'bosscard_001.png': (427, 240),
    'win_pic_001.png': (115, 71), 'win_pic_junkan.png': (115, 71), 'coop_page_death.png': (11, 13),
    os.path.join('newspritesetup', 'hand_001.png'): (4, 4),
}

errors = []


def err(msg):
    errors.append(msg)
    print('FAIL', msg)


def ok(msg):
    print(' ok ', msg)


# 1. animation folders
missing = [c for c in REQUIRED_CLIPS if not os.path.isdir(os.path.join(NSS, c))]
if missing:
    err(f'missing clip folders: {missing}')
else:
    ok(f'all {len(REQUIRED_CLIPS)} clip folders present')

for clip in REQUIRED_CLIPS:
    d = os.path.join(NSS, clip)
    files = sorted(f for f in os.listdir(d) if f.endswith('.png'))
    if not files:
        err(f'{clip}: empty folder')
        continue
    if files == ['cc_sprite_placeholder.png']:
        if not (clip.endswith('_hand') or clip.endswith('_twohands') or clip == 'death_coop'):
            err(f'{clip}: placeholder used for a clip without a fallback')
        continue
    if any('.' in f[:-4] for f in files):
        err(f'{clip}: frame names must not contain dots: {files}')
    if not all(re.match(r'^[a-z0-9_]+_\d{3}\.png$', f) for f in files):
        err(f'{clip}: bad frame names {files}')
    sizes = {Image.open(os.path.join(d, f)).size for f in files}
    if sizes != {(24, 20)}:
        err(f'{clip}: frame sizes {sizes} != 24x20')

# breach idles must include select_idle and select_choose
for b in ('select_idle', 'select_choose'):
    if not os.path.isdir(os.path.join(NSS, 'breach_idles', b)):
        err(f'breach_idles/{b} missing')
ok('breach idles present')

# 1b. alt skin mirrors the main clip set
ALT = os.path.join(CHAR, 'newaltspritesetup')
alt_missing = [c for c in REQUIRED_CLIPS if not os.path.isdir(os.path.join(ALT, c))]
if alt_missing:
    err(f'alt skin missing clip folders: {alt_missing}')
if not os.path.exists(os.path.join(ALT, 'hand_alt_001.png')):
    err('alt skin missing hand_alt_001.png')
for f in ('alt_skin_obj_sprite_001.png', 'alt_skin_obj_sprite_002.png'):
    if not os.path.exists(os.path.join(CHAR, f)):
        err(f'missing {f} (alt skin swapper object)')
ok('alt skin clip set')
for cid, fname in (('pluto:nine_lives', 'nine_lives_icon.png'), ('kibble_crumb', 'kibble_crumb.png'), ('laser_dot', 'laser_dot.png')):
    if not os.path.exists(os.path.join(RES, 'Items', fname)):
        err(f'item art missing: {fname}')

# 2. fixed-size UI art
for rel, size in FIXED_SIZES.items():
    p = os.path.join(CHAR, rel)
    if not os.path.exists(p):
        err(f'missing {rel}')
    elif Image.open(p).size != size:
        err(f'{rel}: size {Image.open(p).size} != {size}')
ok('UI art sizes')
foyer = sorted(os.listdir(os.path.join(CHAR, 'foyercard')))
if not any('idle' in f for f in foyer) or not any('appear' in f for f in foyer):
    err('foyercard needs idle and appear frames')
if {Image.open(os.path.join(CHAR, 'foyercard', f)).size for f in foyer} != {(38, 38)}:
    err('foyercard frames must be 38x38')
ok(f'foyercard: {len(foyer)} frames')

# 3. gun sprites + jtk2d
wc = os.path.join(RES, 'SpriteRoot', 'WeaponCollection')
pngs = sorted(f for f in os.listdir(wc) if f.endswith('.png'))
for f in pngs:
    if not os.path.exists(os.path.join(wc, f[:-4] + '.jtk2d')):
        err(f'{f}: missing .jtk2d attach-point file (Gun.Initialize needs PrimaryHand)')
    j = json.load(open(os.path.join(wc, f[:-4] + '.jtk2d')))
    names = [a.get('name') for a in j['attachPoints']]
    if 'PrimaryHand' not in names:
        err(f'{f}: jtk2d lacks PrimaryHand')
if 'pluto_kibble_sack_idle_001.png' not in pngs:
    err('gun idle sprite missing')
for prefix in ('pluto_kibble_sack', 'pluto_gravy_pouch'):
    gun_sizes = {Image.open(os.path.join(wc, f)).size for f in pngs if f.startswith(prefix)}
    if len(gun_sizes) != 1:
        err(f'{prefix} frames must share one canvas size, got {gun_sizes}')
for f in pngs:
    j = json.load(open(os.path.join(wc, f[:-4] + '.jtk2d')))
    if (j['width'], j['height']) != Image.open(os.path.join(wc, f)).size:
        err(f'{f}: jtk2d width/height does not match the PNG')
if not os.path.exists(os.path.join(RES, 'SpriteRoot', 'Ammonomicon Encounter Icon Collection', 'pluto_kibble_sack_idle_001.png')):
    err('ammonomicon page sprite missing')
if not os.path.exists(os.path.join(RES, 'SpriteRoot', 'ProjectileCollection', 'pluto_kibble_001.png')):
    err('projectile sprite missing')
ok(f'gun: {len(pngs)} frames with attach points')

# 4. item art
items = os.path.join(RES, 'Items')
for f in ['wet_food_can_icon.png'] + [f'wet_food_can_toss_00{i}.png' for i in range(1, 5)] + [f'wet_food_can_splash_00{i}.png' for i in range(1, 4)]:
    if not os.path.exists(os.path.join(items, f)):
        err(f'item art missing: {f}')
for f in ['coco_blue_icon.png', 'kibble_bowl_001.png', 'kibble_bowl_002.png']:
    if not os.path.exists(os.path.join(items, f)):
        err(f'item art missing: {f}')
for sub, n in (('idle', 4), ('move', 6), ('pet', 4), ('block', 3), ('ko', 2)):
    d = os.path.join(RES, 'Companions', 'coco', sub)
    if not os.path.isdir(d) or len([f for f in os.listdir(d) if f.endswith('.png')]) != n:
        err(f'companion clip {sub} should have {n} frames')
for f in ['fur_halo_001.png', 'fur_halo_002.png', 'puffed_up_icon.png']:
    if not os.path.exists(os.path.join(items, f)):
        err(f'item art missing: {f}')
fur_root = os.path.join(RES, 'Fur')
fur_n = sum(len(fs) for _, _, fs in os.walk(fur_root)) if os.path.isdir(fur_root) else 0
if fur_n < 100:
    err(f'fur layers missing or too few ({fur_n})')
if not os.path.exists(os.path.join(items, 'squeaker_icon.png')):
    err('item art missing: squeaker_icon.png')
if len([f for f in os.listdir(os.path.join(RES, 'VFX')) if f.startswith('spark')]) != 3:
    err('VFX spark should have 3 frames')
for prefix in ('furpuff', 'loveburst', 'anger'):
    if len([f for f in os.listdir(os.path.join(RES, 'VFX')) if f.startswith(prefix)]) != 4:
        err(f'VFX {prefix} should have 4 frames')
if not os.path.exists(os.path.join(RES, 'SpriteRoot', 'ProjectileCollection', 'pluto_gravy_001.png')):
    err('gravy projectile sprite missing')
ok('item art')

# 5. characterdata ids match the C# ids
cd = open(os.path.join(CHAR, 'characterdata.txt')).read()
src = ''.join(open(os.path.join(ROOT, 'PlutoTheCat', 'src', f)).read() for f in os.listdir(os.path.join(ROOT, 'PlutoTheCat', 'src')))
for cid in re.findall(r'^\s*(pluto:[a-z_]+)', cd, re.M):
    if f'"{cid}"' not in src:
        err(f'characterdata references {cid} but no C# file registers it')
if 'pluto:wet_food_can' in cd and '"Wet Food Can"' not in src:
    err('active item GameObject name must normalise to wet_food_can')
ok('loadout ids match registered ids')

# 5b. vanilla console ids used by synergies exist in the game's id map
idmap = set(l.split()[1] for l in open(os.path.join(ROOT, 'docs', 'research', 'gungeon_items_idmap.txt')) if l[:1].isdigit())
syn = open(os.path.join(ROOT, 'PlutoTheCat', 'src', 'PlutoSynergies.cs')).read()
used = set(re.findall(r'"([a-z0-9_]+)"', syn)) - {'pluto'}
bad = sorted(i for i in used if ':' not in i and i not in idmap and not i.startswith('Play_'))
if bad:
    err(f'synergy ids not in the vanilla id map: {bad}')
ok(f'synergy ids verified ({len(used - set(bad))} vanilla ids)')

# 6. embedded resources inside the DLL (if built)
if os.path.exists(DLL):
    try:
        man = subprocess.run(['monodis', '--manifest', DLL], capture_output=True, text=True).stdout
        need = ['PlutoTheCat.Characters.Pluto.characterdata.txt',
                'PlutoTheCat.Characters.Pluto.newspritesetup.idle.pluto_idle_001.png',
                'PlutoTheCat.Characters.Pluto.newspritesetup.hand_001.png',
                'PlutoTheCat.Characters.Pluto.facecard.png',
                'PlutoTheCat.Resources.SpriteRoot.WeaponCollection.pluto_kibble_sack_idle_001.png',
                'PlutoTheCat.Resources.SpriteRoot.WeaponCollection.pluto_kibble_sack_idle_001.jtk2d',
                'PlutoTheCat.Resources.SpriteRoot.ProjectileCollection.pluto_kibble_001.png',
                'PlutoTheCat.Resources.Items.wet_food_can_icon.png',
                'PlutoTheCat.Resources.SpriteRoot.Ammonomicon_Encounter_Icon_Collection.pluto_kibble_sack_idle_001.png']
        for n in need:
            if n not in man:
                err(f'DLL lacks embedded resource {n}')
        ok(f'DLL embeds {man.count(".png")} PNGs')
    except FileNotFoundError:
        print('skip  monodis not available')
else:
    print('skip  DLL not built yet')

# 7. thunderstore
ts = os.path.join(ROOT, 'thunderstore')
m = json.load(open(os.path.join(ts, 'manifest.json')))
if not re.match(r'^[A-Za-z0-9_]+$', m['name']):
    err('manifest name has invalid characters')
if len(m['description']) > 250:
    err('manifest description > 250 chars')
if Image.open(os.path.join(ts, 'icon.png')).size != (256, 256):
    err('thunderstore icon must be 256x256')
if not os.path.exists(os.path.join(ts, 'README.md')):
    err('thunderstore README.md missing')
ok('thunderstore manifest/icon/readme')

if errors:
    print(f'\n{len(errors)} problem(s)')
    sys.exit(1)
print('\nall checks passed')
