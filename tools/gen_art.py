"""Gemini image generation helper for the mod's large art and reference sheets.

Usage:
  python3 tools/gen_art.py <job> [<job> ...]     # jobs listed in JOBS; 'all' runs everything
  python3 tools/gen_art.py --list

Each job runs the image-generation skill CLI (needs GEMINI_API_KEY in the environment), saves the raw
image under docs/gen/raw/, and post-processes it to the exact in-game size under docs/gen/fit/.
Post-processing: centre-crop to the target aspect, resize with a high-quality filter for large art
(boss card, win pic, icon) or nearest-neighbour + palette snap for pixel targets.

Pluto's description below is the single source of truth for every prompt: grey-brown tabby, not orange.
"""
import os
import sys
import json
import subprocess
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RAW = os.path.join(ROOT, 'docs', 'gen', 'raw')
FIT = os.path.join(ROOT, 'docs', 'gen', 'fit')
CLI = os.path.expanduser('~/.claude/skills/image-generation/mcp-server-build/cli.bundle.js')

PLUTO = ("Pluto, a chubby adult cat with GREY-BROWN tabby fur (cool taupe brown with darker brown stripes, "
         "NOT orange, NOT ginger), a white muzzle, white blaze down the nose, white chest and belly, white paws, "
         "a distinctive small white oval spot on top of his head between the ears, bright green eyes, pink nose, "
         "pink inner ears, and a long raccoon-ringed tail with alternating light and dark brown bands and a dark tip")
COCO = ("Coco Blue, a small round plush toy cat: pale sky-blue velvet body, white oval belly patch, tiny ears with "
        "red felt inside, stubby paws, embroidered sleepy closed eyes, white muzzle with a pink nose, stitched whiskers")
BAG = ("a bag of ROYAL CANIN dry cat food: white and silver upright pouch, red band with the five-dot crown logo, "
       "purple round label with a grey cat, gusseted bottom, zip top")
CAN = ("a gold tin of ROYAL CANIN Kitten wet cat food: gold metal can with a pull-tab lid, pink label with a white "
       "panel, red band and crown logo, a small white kitten picture")
STYLE_PIXEL = ("clean 16-bit pixel art, crisp 1-pixel dark outlines, flat colours with simple 3-tone shading, "
               "no anti-aliasing, no gradients, plain solid white background")
STYLE_PAINT = ("detailed digital illustration in the style of Enter the Gungeon promotional art, bold outlines, "
               "rich colours, dramatic lighting")

JOBS = {
    # large in-game art
    'bosscard': dict(aspect='16:9', size=(427, 240), mode='paint',
                     prompt=f"{STYLE_PAINT}. Boss-intro style portrait card of {PLUTO}, standing upright like a "
                            f"gunslinger hero, holding {BAG} sideways like a gun with kibble flying out, dark "
                            f"dungeon background with warm torchlight, dramatic low angle, composition leaves the "
                            f"right third empty for a name"),
    'winpic': dict(aspect='3:2', size=(115, 71), mode='paint',
                   prompt=f"{STYLE_PAINT}. Victory scene: {PLUTO} sitting proudly next to {COCO} on a pile of "
                          f"kibble and gold coins with hearts floating up, cosy warm lighting, small painterly scene"),
    'icon': dict(aspect='1:1', size=(256, 256), mode='paint',
                 prompt=f"{STYLE_PAINT}. App icon: close-up head-and-shoulders portrait of {PLUTO} looking at the "
                        f"viewer with a slight smirk, dark warm brown background, centred, bold and readable at small size"),
    # pixel references for hand-placing sprites
    'pluto_sheet': dict(aspect='1:1', size=(512, 512), mode='pixel',
                        prompt=f"{STYLE_PIXEL}. Video-game character sprite reference of {PLUTO} standing upright on "
                               f"two legs like a Gungeoneer hero, big head and short chubby body, side view facing right, "
                               f"tail curling up behind, drawn large so every pixel is a big square"),
    'pluto_faces': dict(aspect='1:1', size=(512, 512), mode='pixel',
                        prompt=f"{STYLE_PIXEL}. Four large pixel-art portrait icons of {PLUTO}'s face in a 2x2 grid: "
                               f"neutral, blinking, angry with fur on end, and happy with closed eyes, cropped to "
                               f"fill each square, drawn large with big square pixels"),
    'coco_sheet': dict(aspect='1:1', size=(512, 512), mode='pixel',
                       prompt=f"{STYLE_PIXEL}. Video-game sprite reference of {COCO}, front view, drawn large with "
                              f"big square pixels, also a second small version of it lying on its back with stars"),
    'items_sheet': dict(aspect='1:1', size=(512, 512), mode='pixel',
                        prompt=f"{STYLE_PIXEL}. Two video-game item icons side by side, drawn large with big square "
                               f"pixels: {BAG} lying sideways with the zip opening to the right and kibble spilling "
                               f"out, and {CAN} upright"),
}


def run(job):
    spec = JOBS[job]
    os.makedirs(RAW, exist_ok=True); os.makedirs(FIT, exist_ok=True)
    raw = os.path.join(RAW, job + '.png')
    cmd = ['node', CLI, '--prompt', spec['prompt'], '--output', raw, '--aspect-ratio', spec['aspect']]
    out = subprocess.run(cmd, capture_output=True, text=True)
    last = [l for l in out.stdout.splitlines() if l.startswith('{')]
    res = json.loads(last[-1]) if last else {'success': False, 'error': out.stdout[-400:] + out.stderr[-400:]}
    if not res.get('success'):
        print(f'{job}: FAILED {res.get("error")}')
        return False
    fit(job, raw, spec)
    print(f'{job}: ok -> {os.path.join(FIT, job + ".png")}')
    return True


def fit(job, raw, spec):
    im = Image.open(raw).convert('RGBA')
    tw, th = spec['size']
    # centre-crop to the target aspect
    ta = tw / th
    w, h = im.size
    if w / h > ta:
        nw = int(h * ta); im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:
        nh = int(w / ta); im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    if spec['mode'] == 'paint':
        im = im.resize((tw, th), Image.LANCZOS)
    else:
        im = im.resize((tw, th), Image.NEAREST)
    im.save(os.path.join(FIT, job + '.png'))


if __name__ == '__main__':
    args = sys.argv[1:]
    if not args or args == ['--list']:
        print('\n'.join(JOBS)); sys.exit(0)
    jobs = list(JOBS) if args == ['all'] else args
    ok = all([run(j) for j in jobs])
    sys.exit(0 if ok else 1)
