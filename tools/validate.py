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
    if sizes != {(24, 26)}:
        err(f'{clip}: frame sizes {sizes} != 24x26')

# body frames ship without the outline colour (the game draws it): no #1E1614 pixels allowed
OUTLINE = (0x1E, 0x16, 0x14, 255)
for d in [os.path.join(NSS, c) for c in ('idle', 'run_right', 'dodge')] + [os.path.join(RES, 'Companions', 'coco', c) for c in ('idle', 'ko')]:
    for f in sorted(os.listdir(d))[:1]:
        with Image.open(os.path.join(d, f)) as im:
            pixels = set(im.convert('RGBA').get_flattened_data())
        if OUTLINE in pixels:
            err(f'{os.path.basename(d)}/{f}: actor frame contains the baked outline colour')
ok('body and companion frames carry no baked outline')

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
for need in ('pluto_taiyaki_cannon_idle_001.png', 'pluto_katana_idle_001.png'):
    if need not in pngs:
        err(f'samurai gun sprite missing: {need}')
for need in ('pluto_mini_taiyaki_001.png', 'pluto_katana_wave_001.png', 'pluto_churu_drop_001.png'):
    if not os.path.exists(os.path.join(RES, 'SpriteRoot', 'ProjectileCollection', need)):
        err(f'samurai projectile sprite missing: {need}')
for prefix in ('pluto_kibble_sack', 'pluto_taiyaki_cannon', 'pluto_katana_idle', 'pluto_katana_reload'):
    gun_sizes = {Image.open(os.path.join(wc, f)).size for f in pngs if f.startswith(prefix)}
    if len(gun_sizes) != 1:
        err(f'{prefix} frames must share one canvas size, got {gun_sizes}')
# Attachment numbers: tools/weapon_layout.py is the one source; the jtk2d files and src/WeaponLayout.cs must match it.
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import weapon_layout as WL  # noqa: E402
if open(WL.CS_PATH).read() != WL.layout_cs():
    err('WeaponLayout.cs is stale (run tools/make_art.py)')
for f in pngs:
    spec = WL.spec_for_frame(f)
    if spec is None:
        continue
    pts = {a['name']: a['position'] for a in json.load(open(os.path.join(wc, f[:-4] + '.jtk2d')))['attachPoints'] if isinstance(a, dict) and 'position' in a}
    if (pts['PrimaryHand']['x'] * 16, pts['PrimaryHand']['y'] * 16) != spec['hand'] or (pts['Casing']['x'] * 16, pts['Casing']['y'] * 16) != spec['muzzle']:
        err(f'{f}: jtk2d attach points differ from tools/weapon_layout.py')
# 2.16.1 katana swing: the fire frames use a taller canvas; KatanaGun.cs shifts them by WeaponLayout.KATANA_SWING_GRIP_OFFSET
# so the grip stays at the idle grip.
_kat = WL.WEAPONS['katana']
_katana_fire = sorted(f for f in pngs if f.startswith('pluto_katana_fire_'))
if len(_katana_fire) < 6:
    err(f'katana swing needs at least 6 fire frames, got {len(_katana_fire)}')
if {Image.open(os.path.join(wc, f)).size for f in _katana_fire} != {_kat['swing_canvas']}:
    err(f"katana fire frames must all be {_kat['swing_canvas']} (swing canvas)")
_katana_src = open(os.path.join(ROOT, 'PlutoTheCat', 'src', 'KatanaGun.cs')).read()
if 'SwingGripOffsetPixels = WeaponLayout.KATANA_SWING_GRIP_OFFSET' not in _katana_src:
    err('KatanaGun.cs must shift the fire frames by WeaponLayout.KATANA_SWING_GRIP_OFFSET')
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
if not os.path.exists(os.path.join(items, 'wet_food_can_icon.png')):
    err('item art missing: wet_food_can_icon.png')
for i in range(1, 5):   # the thrown can tumbles through four projectile sprites
    if not os.path.exists(os.path.join(RES, 'SpriteRoot', 'ProjectileCollection', f'pluto_wet_food_can_00{i}.png')):
        err(f'wet food can projectile frame missing: pluto_wet_food_can_00{i}.png')
for f in ['coco_blue_icon.png', 'kibble_bowl_001.png', 'kibble_bowl_002.png']:
    if not os.path.exists(os.path.join(items, f)):
        err(f'item art missing: {f}')
for sub, n in (('idle', 4), ('move', 6), ('pet', 4), ('block', 3), ('ko', 2),
               ('knight_idle', 4), ('knight_move', 6), ('knight_pet', 4), ('knight_block', 3), ('knight_ko', 2)):
    d = os.path.join(RES, 'Companions', 'coco', sub)
    if not os.path.isdir(d) or len([f for f in os.listdir(d) if f.endswith('.png')]) != n:
        err(f'companion clip {sub} should have {n} frames')
# Coco's clips keep headroom for the hop and the pet wiggle (17x16 drawn + 1-px margin); 2.15.1 fixed clipped ears
for sub in ('idle', 'move', 'pet', 'block'):
    d = os.path.join(RES, 'Companions', 'coco', sub)
    sizes = {Image.open(os.path.join(d, f)).size for f in os.listdir(d) if f.endswith('.png')} if os.path.isdir(d) else set()
    if sizes != {(19, 18)}:
        err(f'companion clip {sub}: frame sizes {sizes} != 19x18')
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
for prefix in ('furpuff', 'loveburst', 'anger', 'gravyburst'):
    if len([f for f in os.listdir(os.path.join(RES, 'VFX')) if f.startswith(prefix)]) != 4:
        err(f'VFX {prefix} should have 4 frames')
ok('item art')

# 4b. boss intro card: the game draws the player's card over the boss art (BossCardUIController.playerSprite),
# so it must be a cut-out on transparency like vanilla/Kotonoha cards (~12 % opaque), never a full opaque panel.
_cards = sorted(f for f in os.listdir(CHAR) if f.startswith('bosscard_') and f.endswith('.png'))
if not _cards:
    err('boss intro card missing: Characters/Pluto/bosscard_001.png')
for f in _cards:
    _im = Image.open(os.path.join(CHAR, f)).convert('RGBA')
    _alpha = _im.getchannel('A').tobytes()
    _opaque = sum(1 for v in _alpha if v) / len(_alpha)
    if _im.size != (427, 240):
        err(f'{f}: boss card must be 427x240, got {_im.size}')
    if _opaque > 0.30:
        err(f'{f}: boss card is {_opaque:.0%} opaque; it would cover the boss art (keep it a cut-out, <= 30 %)')
# Samurai costume card (2.16.0): own file names (never "bosscard_"), same frame count, same cut-out rules.
_samurai = sorted(f for f in os.listdir(CHAR) if f.startswith('samuraicard_') and f.endswith('.png'))
if len(_samurai) != len(_cards):
    err(f'samurai card frames ({len(_samurai)}) must match the boss card frames ({len(_cards)})')
for f in _samurai:
    _im = Image.open(os.path.join(CHAR, f)).convert('RGBA')
    _a = _im.getchannel('A').tobytes()
    if _im.size != (427, 240) or sum(1 for v in _a if v) / len(_a) > 0.30:
        err(f'{f}: samurai card must be a 427x240 cut-out (<= 30 % opaque)')
ok(f'boss card: {len(_cards)} frame(s), cut-out')

# 5. characterdata ids match the C# ids
cd = open(os.path.join(CHAR, 'characterdata.txt')).read()
src = ''.join(open(os.path.join(ROOT, 'PlutoTheCat', 'src', f)).read() for f in os.listdir(os.path.join(ROOT, 'PlutoTheCat', 'src')))
for cid in re.findall(r'^\s*(pluto:[a-z_]+)', cd, re.M):
    if f'"{cid}"' not in src:
        err(f'characterdata references {cid} but no C# file registers it')
if 'pluto:wet_food_can' in cd and '"Wet Food Can"' not in src:
    err('active item GameObject name must normalise to wet_food_can')
ok('loadout ids match registered ids')

# 5a. samurai costume loadout and unlock (2.16.0)
_alt = re.search(r'<altGuns>(.*?)</altGuns>', cd, re.S | re.I)
_alt_ids = [l.split()[0] for l in (_alt.group(1).splitlines() if _alt else []) if l.strip() and not l.strip().startswith('#')]
if _alt_ids != ['pluto:taiyaki_cannon', 'pluto:katana']:
    err(f'<altGuns> must be pluto:taiyaki_cannon, pluto:katana (got {_alt_ids})')
_plugin = open(os.path.join(ROOT, 'PlutoTheCat', 'src', 'Plugin.cs')).read().splitlines()
if any('KILLED_PAST_ALTERNATE_COSTUME' in l for l in _plugin):
    err('Plugin.cs still forces KILLED_PAST_ALTERNATE_COSTUME (the costume must unlock by beating the past)')
for i, l in enumerate(_plugin):
    if 'SetCharacterSpecificFlag' in l and not any('UnlockSamuraiCostume' in x for x in _plugin[max(0, i - 3):i + 1]):
        err(f'Plugin.cs:{i + 1} sets a character flag outside the UnlockSamuraiCostume debug key')
ok('samurai loadout and unlock gate')

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
