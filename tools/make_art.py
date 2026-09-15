"""Generate every PNG (and gun .jtk2d attach files) for the Pluto mod.

Usage: python3 tools/make_art.py   (from the project root)
Writes into PlutoTheCat/Characters/Pluto, PlutoTheCat/Resources and thunderstore/.
"""
import os
import json
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)

from pixel import save, img_from_rows, sheet, PALETTE, strip_outline, pad, outline_img, Image  # noqa: E402
import lint_art  # noqa: E402
import preview as V  # noqa: E402
import character_anims as A  # noqa: E402
import ui_and_items as U  # noqa: E402
import poses as P  # noqa: E402
import art_v4 as V4  # noqa: E402
import art_yasupen as PEN  # noqa: E402
import art_v5 as V5  # noqa: E402
import fur as FUR  # noqa: E402
import weapon_layout as WL  # noqa: E402

CHAR = os.path.join(ROOT, 'PlutoTheCat', 'Characters', 'Pluto')
RES = os.path.join(ROOT, 'PlutoTheCat', 'Resources')
SPRITE_ROOT = os.path.join(RES, 'SpriteRoot')
TS = os.path.join(ROOT, 'thunderstore')
PREVIEW = os.path.join(ROOT, 'docs', 'art-preview')

PLACEHOLDER = ['.' * 4] * 4  # cc_sprite_placeholder.png: fully transparent 4x4


def clean(d):
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(d, exist_ok=True)


def write_clip(folder, frames, prefix, body=False):
    """body=True: player body frames ship without the outline (the game draws it at runtime)."""
    os.makedirs(folder, exist_ok=True)
    for i, f in enumerate(frames, 1):
        save(strip_outline(f) if body else f, os.path.join(folder, f'{prefix}_{i:03d}.png'))


def character():
    clean(os.path.join(CHAR, 'newspritesetup'))
    clean(os.path.join(CHAR, 'foyercard'))
    clean(os.path.join(CHAR, 'loadoutsprites'))
    nss = os.path.join(CHAR, 'newspritesetup')
    for clip, frames in A.CLIPS.items():
        folder = os.path.join(nss, clip)
        if frames is None:
            os.makedirs(folder, exist_ok=True)
            save(PLACEHOLDER, os.path.join(folder, 'cc_sprite_placeholder.png'))
        else:
            write_clip(folder, frames, f'pluto_{clip}', body=True)
    for clip, frames in A.BREACH_IDLES.items():
        write_clip(os.path.join(nss, 'breach_idles', clip), frames, f'pluto_select_{clip}', body=True)
    save(strip_outline(P.HAND), os.path.join(nss, 'hand_001.png'))

    # 2.16.0 alt skin: the samurai costume (replaces Wet Pluto). Same clip layout under newaltspritesetup/, built by
    # tools/samurai.py from the kimono head/body parts; hand_alt_001 is a white paw with an indigo sleeve cuff.
    import samurai
    sam_clips, sam_breach, sam_hand = samurai.build()
    clean(os.path.join(CHAR, 'newaltspritesetup'))
    alt = os.path.join(CHAR, 'newaltspritesetup')
    for clip, frames in sam_clips.items():
        folder = os.path.join(alt, clip)
        if frames is None:
            os.makedirs(folder, exist_ok=True)
            save(PLACEHOLDER, os.path.join(folder, 'cc_sprite_placeholder.png'))
        else:
            write_clip(folder, frames, f'plutowet_{clip}', body=True)   # sprite prefix kept: names only need to be unique
    for clip, frames in sam_breach.items():
        write_clip(os.path.join(alt, 'breach_idles', clip), frames, f'plutowet_select_{clip}', body=True)
    save(strip_outline(sam_hand), os.path.join(alt, 'hand_alt_001.png'))
    # Breach costume swapper: the kimono stand (approved pluto-artist frames), bathtub only if the art is missing
    stand = os.path.join(ROOT, 'reference', 'art', 'kimono_stand')
    for i, fallback in ((1, U.BATHTUB), (2, U.BATHTUB_2)):
        src = os.path.join(stand, f'alt_skin_obj_sprite_00{i}.png')
        if os.path.exists(src):
            shutil.copy(src, os.path.join(CHAR, f'alt_skin_obj_sprite_00{i}.png'))
        else:
            save(fallback, os.path.join(CHAR, f'alt_skin_obj_sprite_00{i}.png'))

    # UI
    save(U.FACE_34, os.path.join(CHAR, 'facecard.png'))
    write_clip(os.path.join(CHAR, 'foyercard'), U.FOYER_IDLE, 'pluto_facecard_idle')
    write_clip(os.path.join(CHAR, 'foyercard'), U.FOYER_APPEAR, 'pluto_facecard_appear')
    save(U.ICON_9, os.path.join(CHAR, 'icon.png'))
    save(U.COOP_DEATH, os.path.join(CHAR, 'coop_page_death.png'))
    # Boss intro card: the game draws the player's card OVER the boss art (BossCardUIController.playerSprite), so it
    # is a cut-out on transparency. The art is the approved pluto-artist bust (Gemini, pixelized, reviewed); the source
    # of truth is reference/art/bosscard/. The samurai costume card is samuraicard_* (never "bosscard_", or Alexandria
    # appends it to this list); PlutoPatches picks the set by costume when the card shows.
    card_dir = os.path.join(ROOT, 'reference', 'art', 'bosscard')
    normal_src = os.path.join(card_dir, 'normal.png')
    if not os.path.exists(normal_src):
        raise FileNotFoundError(normal_src)          # check the source before removing the old cards
    for f in os.listdir(CHAR):
        if (f.startswith('bosscard_') or f.startswith('samuraicard_')) and f.endswith('.png'):
            os.remove(os.path.join(CHAR, f))
    shutil.copy(normal_src, os.path.join(CHAR, 'bosscard_001.png'))
    if os.path.exists(os.path.join(card_dir, 'samurai.png')):
        shutil.copy(os.path.join(card_dir, 'samurai.png'), os.path.join(CHAR, 'samuraicard_001.png'))
    U.win_pic().save(os.path.join(CHAR, 'win_pic_001.png'))
    U.win_pic().save(os.path.join(CHAR, 'win_pic_junkan.png'))
    save(U.GUN_AMMONOMICON, os.path.join(CHAR, 'loadoutsprites', 'a_kibblesack.png'))
    save(U.CAN_ICON, os.path.join(CHAR, 'loadoutsprites', 'b_wetfoodcan.png'))
    # punchout face cards (used if the Rat fight ever picks them up)
    os.makedirs(os.path.join(CHAR, 'punchout'), exist_ok=True)
    save(U.FACE_34, os.path.join(CHAR, 'punchout', 'facecard1.png'))
    save(U.FACE_34_HURT, os.path.join(CHAR, 'punchout', 'facecard2.png'))
    save(U.FACE_34_HURT, os.path.join(CHAR, 'punchout', 'facecard3.png'))


def jtk2d(width, height, hand_px, casing_px):
    return {
        "name": None, "x": 0, "y": 0, "width": width, "height": height, "flip": 1,
        "attachPoints": [
            {".": "arraytype", "name": "array", "size": 2},
            {"name": "PrimaryHand", "position": {"x": hand_px[0] / 16, "y": hand_px[1] / 16, "z": 0.0}, "angle": 0.0},
            {"name": "Casing", "position": {"x": casing_px[0] / 16, "y": casing_px[1] / 16, "z": 0.0}, "angle": 0.0},
        ],
    }


def gun_and_items():
    clean(SPRITE_ROOT)
    clean(os.path.join(RES, 'Items'))
    wc = os.path.join(SPRITE_ROOT, 'WeaponCollection')
    pc = os.path.join(SPRITE_ROOT, 'ProjectileCollection')
    # Attach points (PrimaryHand = grip, Casing = muzzle) come from tools/weapon_layout.py, which also generates
    # src/WeaponLayout.cs for the gun classes, so the art and the runtime share one set of numbers.
    sack = WL.WEAPONS['kibble_sack']
    if (U.GUN_W, U.GUN_H) != sack['canvas']:
        raise ValueError(f"kibble sack canvas {(U.GUN_W, U.GUN_H)} != weapon_layout {sack['canvas']}")
    frames = {'idle': [U.GUN_IDLE], 'fire': U.GUN_FIRE, 'reload': U.GUN_RELOAD}
    for anim, fr in frames.items():
        for i, f in enumerate(fr, 1):
            name = f'{sack["sprite"]}_{anim}_{i:03d}'
            save(f, os.path.join(wc, name + '.png'))
            with open(os.path.join(wc, name + '.jtk2d'), 'w') as fh:
                json.dump(jtk2d(U.GUN_W, U.GUN_H, sack['hand'], sack['muzzle']), fh, indent=2)
    save(U.KIBBLE, os.path.join(pc, 'pluto_kibble_001.png'))
    # 2.16.0 samurai costume weapons: approved pluto-artist frames live in reference/art/<weapon>/ and are copied as-is.
    for folder in ('taiyaki_cannon', 'katana'):
        spec = WL.WEAPONS[folder]
        gun_name = spec['sprite']
        src = os.path.join(ROOT, 'reference', 'art', folder)
        for f in sorted(os.listdir(src)):
            if f.startswith(gun_name + '_') and f.endswith('.png') and '_wave' not in f:
                shutil.copy(os.path.join(src, f), os.path.join(wc, f))
                w, h = Image.open(os.path.join(src, f)).size
                with open(os.path.join(wc, f[:-4] + '.jtk2d'), 'w') as fh:
                    json.dump(jtk2d(w, h, spec['hand'], spec['muzzle']), fh, indent=2)
    WL.write()
    shutil.copy(os.path.join(ROOT, 'reference', 'art', 'taiyaki_cannon', 'pluto_mini_taiyaki_001.png'), os.path.join(pc, 'pluto_mini_taiyaki_001.png'))
    # Churu drop: the Taiyaki Cannon's empty-reload finisher (reference/gemini/taiyaki_cannon/reload_v2.py)
    shutil.copy(os.path.join(ROOT, 'reference', 'art', 'taiyaki_cannon', 'pluto_churu_drop_001.png'), os.path.join(pc, 'pluto_churu_drop_001.png'))
    shutil.copy(os.path.join(ROOT, 'reference', 'art', 'katana', 'pluto_katana_wave_001.png'), os.path.join(pc, 'pluto_katana_wave_001.png'))
    # Same sprite name in the Ammonomicon collection = the picture shown on the gun's Ammonomicon page.
    save(U.GUN_AMMONOMICON, os.path.join(SPRITE_ROOT, 'Ammonomicon Encounter Icon Collection', 'pluto_kibble_sack_idle_001.png'))
    # The samurai guns' pages use their approved idle sprite, the vanilla convention (2.16.4: they had no page icon).
    for folder, gun_name in (('taiyaki_cannon', 'pluto_taiyaki_cannon'), ('katana', 'pluto_katana')):
        shutil.copy(os.path.join(ROOT, 'reference', 'art', folder, gun_name + '_idle_001.png'),
                    os.path.join(SPRITE_ROOT, 'Ammonomicon Encounter Icon Collection', gun_name + '_idle_001.png'))

    items = os.path.join(RES, 'Items')
    save(U.CAN_ICON, os.path.join(items, 'wet_food_can_icon.png'))
    write_clip(pc, U.CAN_TOSS, 'pluto_wet_food_can')   # the thrown can tumbles through these
    save(U.NINE_LIVES_ICON, os.path.join(items, 'nine_lives_icon.png'))
    save(U.CRUMB, os.path.join(items, 'kibble_crumb.png'))
    save(U.LASER_DOT, os.path.join(items, 'laser_dot.png'))
    save(U.HAIRBALL, os.path.join(pc, 'pluto_hairball_001.png'))
    # 2.2: Coco Blue companion frames, VFX, bowl pickup, coco icon
    comp = os.path.join(RES, 'Companions', 'coco')
    clean(comp)
    # Coco is an AIActor: AIActor.Start() adds the runtime outline (procedurallyOutlined defaults to
    # true and Alexandria's CompanionBuilder never clears it), so his frames ship without one too.
    # Every frame gets a 1-px margin so the runtime outline has room (canvas 18x15 / 18x18); the C#
    # hitbox and bullet-blocker offsets are (3,2) to match.
    def margin(frames):
        return [pad(f, len(f[0]) + 2, len(f) + 2, 1, 1) for f in frames]
    write_clip(os.path.join(comp, 'idle'), margin(V4.COCO_IDLE), 'coco_idle', body=True)
    write_clip(os.path.join(comp, 'move'), margin(V4.COCO_MOVE), 'coco_move', body=True)
    write_clip(os.path.join(comp, 'pet'), margin(V4.COCO_PET), 'coco_pet', body=True)
    write_clip(os.path.join(comp, 'block'), margin(V4.COCO_BLOCK), 'coco_block', body=True)
    write_clip(os.path.join(comp, 'ko'), margin(V4.COCO_KO), 'coco_ko', body=True)
    # 2.15 Knighted (Coco + Ser Junkan as a Holy Knight): helmeted clip set, swapped in by name like Junkan's armour
    for clip, frames in (('idle', V4.COCO_KNIGHT_IDLE), ('move', V4.COCO_KNIGHT_MOVE), ('pet', V4.COCO_KNIGHT_PET),
                         ('block', V4.COCO_KNIGHT_BLOCK), ('ko', V4.COCO_KNIGHT_KO)):
        write_clip(os.path.join(comp, 'knight_' + clip), margin(frames), 'coco_knight_' + clip, body=True)
    # 2.18.0 Yasupen companion (same margin and outline stripping as Coco)
    pen = os.path.join(RES, 'Companions', 'yasupen')
    clean(pen)
    for clip, frames in (('idle', PEN.PEN_IDLE), ('move', PEN.PEN_MOVE), ('slide', PEN.PEN_SLIDE),
                         ('pet', PEN.PEN_PET), ('cheer', PEN.PEN_CHEER)):
        write_clip(os.path.join(pen, clip), margin(frames), 'yasupen_' + clip, body=True)
    save(PEN.PEN_ICON, os.path.join(items, 'yasupen_icon.png'))
    save(V4.SQUEAKER_ICON, os.path.join(items, 'squeaker_icon.png'))
    vfx = os.path.join(RES, 'VFX')
    clean(vfx)
    write_clip(vfx, V4.FUR_PUFF, 'furpuff')
    write_clip(vfx, V4.LOVE_BURST, 'loveburst')
    write_clip(vfx, U.GRAVY_BURST, 'gravyburst')   # wet food can burst
    for i in range(1, 5):   # 2.16.0 Taiyaki Cannon hit puff (approved pluto-artist frames)
        shutil.copy(os.path.join(ROOT, 'reference', 'art', 'taiyaki_cannon', f'bonito_{i:03d}.png'), os.path.join(vfx, f'bonito_{i:03d}.png'))
    write_clip(vfx, V4.BLOCK_SPARK, 'spark')
    save(V4.BOWL_PICKUP, os.path.join(items, 'kibble_bowl_001.png'))
    save(V4.BOWL_PICKUP_2, os.path.join(items, 'kibble_bowl_002.png'))
    save(V4.COCO_IDLE_1, os.path.join(items, 'coco_blue_icon.png'))
    # 2.3: Puffed Up
    save(V5.FUR_HALO[0], os.path.join(items, 'fur_halo_001.png'))
    save(V5.FUR_HALO[1], os.path.join(items, 'fur_halo_002.png'))
    save(V5.PUFFED_ICON, os.path.join(items, 'puffed_up_icon.png'))
    write_clip(vfx, V5.ANGER_MARKS, 'anger')
    # 2.17 cat items: approved art in reference/art/cat_items/ (reference/gemini/cat_items/draw_items.py, draw_world.py)
    cat = os.path.join(ROOT, 'reference', 'art', 'cat_items')
    for f in ('ball_of_yarn_icon', 'catnip_pouch_icon', 'jingle_bell_collar_icon', 'hairball_item_icon', 'scratching_post_icon',
              'scratching_post_placed'):
        shutil.copy(os.path.join(cat, f + '.png'), os.path.join(items, f + '.png'))
    for f in ('pluto_yarn_ball_001', 'pluto_yarn_ball_002', 'pluto_hairball_item_001'):
        shutil.copy(os.path.join(cat, f + '.png'), os.path.join(pc, f + '.png'))
    for prefix in ('jingle', 'catnip'):
        for i in range(1, 5):
            shutil.copy(os.path.join(cat, f'{prefix}_{i:03d}.png'), os.path.join(vfx, f'{prefix}_{i:03d}.png'))
    # 2.5: frame-following fur layers for Puffed Up
    furdir = os.path.join(RES, 'Fur')
    clean(furdir)
    n = 0
    for clip, frames in FUR.all_fur().items():
        for fi, variants in enumerate(frames, 1):
            for v, rows in enumerate(variants):
                save(rows, os.path.join(furdir, clip, f'fur_{clip}_{fi:03d}_{v}.png'))
                n += 1
    # samurai costume: the same layers grown from the kimono frames, fur only where fur shows (tools/fur.py KIMONO)
    for clip, frames in FUR.all_samurai_fur().items():
        for fi, variants in enumerate(frames, 1):
            for v, rows in enumerate(variants):
                save(rows, os.path.join(furdir, 'sam_' + clip, f'fur_sam_{clip}_{fi:03d}_{v}.png'))
                n += 1
    print(f'fur layers: {n}')


def thunderstore():
    os.makedirs(TS, exist_ok=True)
    U.thunderstore_icon().save(os.path.join(TS, 'icon.png'))


def previews():
    os.makedirs(PREVIEW, exist_ok=True)
    V.main()   # character sheet, breach/variants sheet, scale check, APNG clips (with the runtime outline simulated)
    sheet([[U.GUN_IDLE] + U.GUN_FIRE + U.GUN_RELOAD + [U.GUN_AMMONOMICON], [U.KIBBLE, U.CAN_ICON] + U.CAN_TOSS + U.GRAVY_BURST],
          os.path.join(PREVIEW, 'items-sheet.png'), scale=6)
    sheet([[U.FACE_34, U.FACE_34_BLINK, U.FACE_34_HURT] + U.FOYER_IDLE[3:] + U.FOYER_APPEAR[2:3], [U.ICON_9, U.COOP_DEATH, P.HAND, U.NINE_LIVES_ICON, U.CRUMB, U.LASER_DOT, U.BATHTUB],
           [U.HAIRBALL] + V4.COCO_IDLE[:2] + V4.COCO_MOVE + [V4.BOWL_PICKUP] + V4.FUR_PUFF + V4.LOVE_BURST + U.FOYER_APPEAR,
           V5.FUR_HALO + [V5.PUFFED_ICON] + V5.ANGER_MARKS],
          os.path.join(PREVIEW, 'ui-sheet.png'), scale=5)
    # Coco with Ser Junkan (Squire): plain / gold plumed knight helmet, runtime outline simulated
    V.strip_sheet([('coco_idle', V4.COCO_IDLE), ('coco_knight_idle', V4.COCO_KNIGHT_IDLE), ('coco_knight_move', V4.COCO_KNIGHT_MOVE),
                   ('coco_knight_pet', V4.COCO_KNIGHT_PET), ('coco_knight_block', V4.COCO_KNIGHT_BLOCK), ('coco_knight_ko', V4.COCO_KNIGHT_KO)],
                  os.path.join(PREVIEW, 'coco-helmets.png'), scale=4)
    V.scale_check([V4.COCO_IDLE_1, V4.KNIGHT_IDLE_1], os.path.join(PREVIEW, 'coco-helmets-scale.png'))
    V.strip_sheet([('yasupen_idle', PEN.PEN_IDLE), ('yasupen_move', PEN.PEN_MOVE), ('yasupen_slide', PEN.PEN_SLIDE),
                   ('yasupen_pet', PEN.PEN_PET), ('yasupen_cheer', PEN.PEN_CHEER)],
                  os.path.join(PREVIEW, 'yasupen.png'), scale=4)
    V.scale_check([V4.COCO_IDLE_1, PEN.PEN_IDLE_1], os.path.join(PREVIEW, 'yasupen-scale.png'))
    import weapon_preview   # weapon alignment sheets (grip, muzzle, aim, reach) from tools/weapon_layout.py
    weapon_preview.main()


if __name__ == '__main__':
    if lint_art.main():
        sys.exit('art lint failed')
    character()
    gun_and_items()
    thunderstore()
    previews()
    n = sum(len(fs) for _, _, fs in os.walk(CHAR))
    print(f'character files: {n}')
    print('done')
