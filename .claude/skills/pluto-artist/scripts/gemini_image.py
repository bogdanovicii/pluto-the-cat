#!/usr/bin/env python3
"""Generate images with the Gemini REST API, with reference images attached.

usage:
  gemini_image.py --prompt "..." | --prompt-file brief.txt
                  [--ref img.png --ref photo.jpg ...] [--ratio 16:9] [--size 2K]
                  [--model gemini-3-pro-image] [--candidates 3] --out reference/gemini/piece/piece.png

Writes <out> (candidate 1) and <out stem>_c2.png ... plus a .json sidecar per image (model, prompt, refs, ratio,
size, time). The API key comes from GEMINI_API_KEY in the environment, ~/.claude/settings.json "env", or
PlutoVetVisit/.env; it is passed to curl through a private header file and never printed or put on argv.
curl is used because this Mac's Python has no CA bundle.
"""
import argparse
import base64
import json
import os
import subprocess
import sys
import tempfile
import time

ENDPOINT = 'https://generativelanguage.googleapis.com/v1beta/models/%s:generateContent'
MIME = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp'}


def api_key():
    if os.environ.get('GEMINI_API_KEY'):
        return os.environ['GEMINI_API_KEY']
    try:
        env = json.load(open(os.path.expanduser('~/.claude/settings.json'))).get('env', {})
        if env.get('GEMINI_API_KEY'):
            return env['GEMINI_API_KEY']
    except (OSError, ValueError):
        pass
    here = os.path.dirname(os.path.abspath(__file__))
    for up in range(6):
        cand = os.path.join(here, *(['..'] * up), 'PlutoVetVisit', '.env')
        if os.path.exists(cand):
            for line in open(cand):
                if line.strip().startswith('GEMINI_API_KEY='):
                    return line.split('=', 1)[1].strip().strip('"').strip("'")
    sys.exit('GEMINI_API_KEY not found (environment, ~/.claude/settings.json env, or PlutoVetVisit/.env)')


def body(prompt, refs, ratio, size):
    parts = [{'text': prompt}]
    for ref in refs:
        ext = os.path.splitext(ref)[1].lower()
        if ext not in MIME:
            sys.exit(f'unsupported reference type: {ref}')
        with open(ref, 'rb') as fh:
            parts.append({'inlineData': {'mimeType': MIME[ext], 'data': base64.b64encode(fh.read()).decode()}})
    cfg = {'responseModalities': ['IMAGE'], 'imageConfig': {'aspectRatio': ratio}}
    if size:
        cfg['imageConfig']['imageSize'] = size
    return {'contents': [{'role': 'user', 'parts': parts}], 'generationConfig': cfg}


def call(payload, model, key, timeout):
    with tempfile.TemporaryDirectory() as tmp:
        data_path = os.path.join(tmp, 'body.json')
        hdr_path = os.path.join(tmp, 'headers.txt')
        with open(data_path, 'w') as fh:
            json.dump(payload, fh)
        fd = os.open(hdr_path, os.O_WRONLY | os.O_CREAT, 0o600)
        with os.fdopen(fd, 'w') as fh:
            fh.write('x-goog-api-key: %s\nContent-Type: application/json\n' % key)
        proc = subprocess.run(['curl', '-s', '--max-time', str(timeout), '-X', 'POST', '-H', '@' + hdr_path,
                               '--data-binary', '@' + data_path, ENDPOINT % model],
                              capture_output=True, text=True)
    if proc.returncode != 0:
        sys.exit(f'curl failed ({proc.returncode}): {proc.stderr.strip()[:300]}')
    try:
        return json.loads(proc.stdout)
    except ValueError:
        sys.exit('non-JSON response: ' + proc.stdout[:300])


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--prompt')
    g.add_argument('--prompt-file')
    ap.add_argument('--ref', action='append', default=[])
    ap.add_argument('--ratio', default='1:1')
    ap.add_argument('--size', default='2K', help='1K / 2K / 4K where the model supports it; empty to omit')
    ap.add_argument('--model', default='gemini-3-pro-image')
    ap.add_argument('--candidates', type=int, default=1)
    ap.add_argument('--out', required=True)
    ap.add_argument('--timeout', type=int, default=600)
    ap.add_argument('--force', action='store_true')
    a = ap.parse_args()

    prompt = a.prompt if a.prompt else open(a.prompt_file).read()
    key = api_key()
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    stem, ext = os.path.splitext(a.out)
    written = []
    for i in range(1, a.candidates + 1):
        path = a.out if i == 1 else f'{stem}_c{i}{ext or ".png"}'
        if os.path.exists(path) and not a.force:
            print('skip (exists):', path)
            continue
        t0 = time.time()
        resp = call(body(prompt, a.ref, a.ratio, a.size), a.model, key, a.timeout)
        if 'error' in resp:
            sys.exit('API error: ' + json.dumps(resp['error'])[:400])
        parts = [p for c in resp.get('candidates', []) for p in c.get('content', {}).get('parts', [])]
        img = next((p['inlineData']['data'] for p in parts if 'inlineData' in p), None)
        if img is None:
            texts = ' '.join(p.get('text', '') for p in parts)
            reason = resp.get('candidates', [{}])[0].get('finishReason') if resp.get('candidates') else resp.get('promptFeedback')
            sys.exit(f'no image returned (reason: {reason}) {texts[:300]}')
        with open(path, 'wb') as fh:
            fh.write(base64.b64decode(img))
        with open(os.path.splitext(path)[0] + '.json', 'w') as fh:
            json.dump({'model': a.model, 'prompt': prompt, 'refs': a.ref, 'ratio': a.ratio, 'size': a.size,
                       'seconds': round(time.time() - t0, 1), 'time': time.strftime('%Y-%m-%d %H:%M:%S')}, fh, indent=2)
        written.append(path)
        print('wrote', path, f'({time.time() - t0:.0f} s)')
    return 0 if written or a.candidates == 0 else 0


if __name__ == '__main__':
    sys.exit(main())
