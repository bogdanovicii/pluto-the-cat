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

from pixel import save, img_from_rows, sheet, PALETTE  # noqa: E402
import character_anims as A  # noqa: E402
import ui_and_items as U  # noqa: E402
import poses as P  # noqa: E402
import art_v4 as V4  # noqa: E402
import art_v5 as V5  # noqa: E402
import fur as FUR  # noqa: E402

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


def write_clip(folder, frames, prefix):
    os.makedirs(folder, exist_ok=True)
    for i, f in enumerate(frames, 1):
        save(f, os.path.join(folder, f'{prefix}_{i:03d}.png'))


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
            write_clip(folder, frames, f'pluto_{clip}')
    for clip, frames in A.BREACH_IDLES.items():
        write_clip(os.path.join(nss, 'breach_idles', clip), frames, f'pluto_select_{clip}')
    save(P.HAND, os.path.join(nss, 'hand_001.png'))

    # v2 alt skin: Wet Pluto. Same clip layout under newaltspritesetup/, hand_alt_001, bathtub swapper object.
    clean(os.path.join(CHAR, 'newaltspritesetup'))
    alt = os.path.join(CHAR, 'newaltspritesetup')
    for clip, frames in A.ALT_CLIPS.items():
        folder = os.path.join(alt, clip)
        if frames is None:
            os.makedirs(folder, exist_ok=True)
            save(PLACEHOLDER, os.path.join(folder, 'cc_sprite_placeholder.png'))
        else:
            write_clip(folder, frames, f'plutowet_{clip}')
    for clip, frames in A.ALT_BREACH_IDLES.items():
        write_clip(os.path.join(alt, 'breach_idles', clip), frames, f'plutowet_select_{clip}')
    save(A.ALT_HAND, os.path.join(alt, 'hand_alt_001.png'))
    save(U.BATHTUB, os.path.join(CHAR, 'alt_skin_obj_sprite_001.png'))
    save(U.BATHTUB_2, os.path.join(CHAR, 'alt_skin_obj_sprite_002.png'))

    # UI
    save(U.FACE_34, os.path.join(CHAR, 'facecard.png'))
    write_clip(os.path.join(CHAR, 'foyercard'), U.FOYER_IDLE, 'pluto_facecard_idle')
    write_clip(os.path.join(CHAR, 'foyercard'), U.FOYER_APPEAR, 'pluto_facecard_appear')
    save(U.ICON_9, os.path.join(CHAR, 'icon.png'))
    save(U.COOP_DEATH, os.path.join(CHAR, 'coop_page_death.png'))
    U.boss_card().save(os.path.join(CHAR, 'bosscard_001.png'))
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
    frames = {'idle': [U.GUN_IDLE], 'fire': U.GUN_FIRE, 'reload': U.GUN_RELOAD}
    for anim, fr in frames.items():
        for i, f in enumerate(fr, 1):
            name = f'pluto_kibble_sack_{anim}_{i:03d}'
            save(f, os.path.join(wc, name + '.png'))
            # hand grips the sack near its closed (left) end; casing/barrel at the open right end
            with open(os.path.join(wc, name + '.jtk2d'), 'w') as fh:
                json.dump(jtk2d(U.GUN_W, U.GUN_H, (7, 5), (29, 7)), fh, indent=2)
    save(U.KIBBLE, os.path.join(pc, 'pluto_kibble_001.png'))
    # Same sprite name in the Ammonomicon collection = the picture shown on the gun's Ammonomicon page.
    save(U.GUN_AMMONOMICON, os.path.join(SPRITE_ROOT, 'Ammonomicon Encounter Icon Collection', 'pluto_kibble_sack_idle_001.png'))

    items = os.path.join(RES, 'Items')
    save(U.CAN_ICON, os.path.join(items, 'wet_food_can_icon.png'))
    write_clip(items, U.CAN_TOSS, 'wet_food_can_toss')
    write_clip(items, U.CAN_SPLASH, 'wet_food_can_splash')
    save(U.NINE_LIVES_ICON, os.path.join(items, 'nine_lives_icon.png'))
    save(U.CRUMB, os.path.join(items, 'kibble_crumb.png'))
    save(U.LASER_DOT, os.path.join(items, 'laser_dot.png'))
    save(U.HAIRBALL, os.path.join(pc, 'pluto_hairball_001.png'))
    # 2.2: gravy pouch (alt gun) + gravy glob
    for anim, fr in {'idle': [V4.GUN2_IDLE], 'fire': V4.GUN2_FIRE, 'reload': V4.GUN2_RELOAD}.items():
        for i, f in enumerate(fr, 1):
            name = f'pluto_gravy_pouch_{anim}_{i:03d}'
            save(f, os.path.join(wc, name + '.png'))
            with open(os.path.join(wc, name + '.jtk2d'), 'w') as fh:
                json.dump(jtk2d(V4.GUN2_W, V4.GUN2_H, (4, 4), (22, 6)), fh, indent=2)
    save(V4.GRAVY, os.path.join(pc, 'pluto_gravy_001.png'))
    # 2.2: Coco Blue companion frames, VFX, bowl pickup, coco icon
    comp = os.path.join(RES, 'Companions', 'coco')
    clean(comp)
    write_clip(os.path.join(comp, 'idle'), V4.COCO_IDLE, 'coco_idle')
    write_clip(os.path.join(comp, 'move'), V4.COCO_MOVE, 'coco_move')
    write_clip(os.path.join(comp, 'pet'), V4.COCO_PET, 'coco_pet')
    vfx = os.path.join(RES, 'VFX')
    clean(vfx)
    write_clip(vfx, V4.FUR_PUFF, 'furpuff')
    write_clip(vfx, V4.LOVE_BURST, 'loveburst')
    save(V4.BOWL_PICKUP, os.path.join(items, 'kibble_bowl_001.png'))
    save(V4.BOWL_PICKUP_2, os.path.join(items, 'kibble_bowl_002.png'))
    save(V4.COCO_IDLE_1, os.path.join(items, 'coco_blue_icon.png'))
    # 2.3: Puffed Up
    save(V5.FUR_HALO[0], os.path.join(items, 'fur_halo_001.png'))
    save(V5.FUR_HALO[1], os.path.join(items, 'fur_halo_002.png'))
    save(V5.PUFFED_ICON, os.path.join(items, 'puffed_up_icon.png'))
    write_clip(vfx, V5.ANGER_MARKS, 'anger')
    # 2.5: frame-following fur layers for Puffed Up
    furdir = os.path.join(RES, 'Fur')
    clean(furdir)
    n = 0
    for clip, frames in FUR.all_fur().items():
        for fi, variants in enumerate(frames, 1):
            for v, rows in enumerate(variants):
                save(rows, os.path.join(furdir, clip, f'fur_{clip}_{fi:03d}_{v}.png'))
                n += 1
    print(f'fur layers: {n}')


def thunderstore():
    os.makedirs(TS, exist_ok=True)
    U.thunderstore_icon().save(os.path.join(TS, 'icon.png'))


def previews():
    os.makedirs(PREVIEW, exist_ok=True)
    sheet([A.IDLE_SIDE + A.IDLE_FRONT + A.IDLE_BACK, A.RUN_SIDE + A.RUN_FRONT, A.RUN_BACK + A.DODGE,
           A.DEATH + A.DEATH_SHOT, A.PITFALL + A.ITEM_GET, A.GHOST_SIDE + A.GHOST_FRONT + A.SLIDE_SIDE + A.SPIT_OUT[:3]],
          os.path.join(PREVIEW, 'character-sheet.png'), scale=4)
    sheet([[U.GUN_IDLE] + U.GUN_FIRE + U.GUN_RELOAD + [U.GUN_AMMONOMICON], [U.KIBBLE, U.CAN_ICON] + U.CAN_TOSS + U.CAN_SPLASH],
          os.path.join(PREVIEW, 'items-sheet.png'), scale=6)
    sheet([[U.FACE_34, U.FACE_34_BLINK, U.FACE_34_HURT] + U.FOYER_IDLE[3:] + U.FOYER_APPEAR[2:3], [U.ICON_9, U.COOP_DEATH, P.HAND, U.NINE_LIVES_ICON, U.CRUMB, U.LASER_DOT, U.BATHTUB],
           A.LOAF + A.GROOM + A.KNOCK, A.DEATH_COOP + A.ALT_CLIPS['idle'] + A.ALT_CLIPS['run_right'][:3] + A.ALT_CLIPS['dodge'][2:4],
           A.CLIPS['idle_hand'][:2] + A.CLIPS['idle_forward_twohands'][:2] + A.CLIPS['run_right_hand'][:3] + [U.HAIRBALL],
           V4.COCO_IDLE[:2] + V4.COCO_MOVE + [V4.GUN2_IDLE, V4.GUN2_FIRE[0], V4.GRAVY, V4.BOWL_PICKUP] + V4.FUR_PUFF + V4.LOVE_BURST + U.FOYER_APPEAR,
           V5.FUR_HALO + [V5.PUFFED_ICON] + V5.ANGER_MARKS],
          os.path.join(PREVIEW, 'ui-sheet.png'), scale=5)


if __name__ == '__main__':
    character()
    gun_and_items()
    thunderstore()
    previews()
    n = sum(len(fs) for _, _, fs in os.walk(CHAR))
    print(f'character files: {n}')
    print('done')
