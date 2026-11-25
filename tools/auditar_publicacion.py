#!/usr/bin/env python3
"""Verify published bytes and file containers; never execute manuscript code."""
import ast
import collections
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import wave
import zipfile
import base64
import struct
import zlib
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
if not (ROOT / 'catalogo/manifest.json').exists():
    ROOT = Path.cwd()
issues = []
warnings = []
png_diagnostics = []
counts = collections.Counter()

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def contained(name):
    p = (ROOT / name).resolve()
    if ROOT.resolve() not in p.parents:
        raise ValueError('Unsafe path: ' + name)
    return p

def check_bytes(path, record, kind):
    if not path.is_file():
        issues.append({'kind': kind, 'path': str(path.relative_to(ROOT)), 'error': 'missing'})
        return False
    if path.stat().st_size != record['size'] or digest(path) != record['sha256']:
        issues.append({'kind': kind, 'path': str(path.relative_to(ROOT)), 'error': 'size or SHA256 mismatch'})
        return False
    counts[kind] += 1
    return True

def inspect_format(path):
    ext = path.suffix.lower()
    name = str(path.relative_to(ROOT))
    try:
        if ext == '.pdf':
            import fitz
            with fitz.open(path) as d:
                if d.needs_pass:
                    warnings.append({'path': name, 'warning': 'PDF requires password'})
                    return
                if not len(d):
                    raise ValueError('PDF has no pages')
                for page in d:
                    page.get_text()
                for i in set([0, len(d) - 1]):
                    d[i].get_pixmap(matrix=fitz.Matrix(.35, .35), alpha=False)
                counts['pdf_pages_read'] += len(d)
        elif ext in {'.zip', '.docx', '.xlsx', '.pptx', '.npz'}:
            with zipfile.ZipFile(path) as z:
                bad = z.testzip()
                if bad:
                    raise ValueError('CRC failure: ' + bad)
                if ext in {'.docx', '.xlsx', '.pptx'}:
                    for member in z.namelist():
                        if member.endswith('.xml'):
                            ET.fromstring(z.read(member))
                if ext == '.docx' and 'word/document.xml' not in z.namelist():
                    raise ValueError('Missing Word document part')
                if ext == '.xlsx' and 'xl/workbook.xml' not in z.namelist():
                    raise ValueError('Missing workbook part')
        elif ext in {'.png', '.jpg', '.jpeg', '.gif', '.tif', '.tiff', '.webp'}:
            from PIL import Image
            with Image.open(path) as im:
                im.verify()
            with Image.open(path) as im:
                im.load()
        elif ext == '.wav':
            with wave.open(str(path), 'rb') as w:
                total = 0
                frame_size = w.getnchannels() * w.getsampwidth()
                while True:
                    data = w.readframes(65536)
                    if not data:
                        break
                    total += len(data)
                if total != w.getnframes() * frame_size:
                    raise ValueError('Truncated WAV payload')
        elif ext in {'.m4a', '.mp3', '.mp4', '.flac', '.ogg'}:
            result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', str(path)], capture_output=True, text=True)
            if result.returncode:
                raise ValueError(result.stderr[:200])
        elif ext == '.json':
            json.loads(path.read_text(encoding='utf-8-sig'))
        elif ext == '.jsonl':
            with path.open(encoding='utf-8-sig') as f:
                for line in f:
                    if line.strip():
                        json.loads(line)
        elif ext == '.csv':
            with path.open(encoding='utf-8-sig', newline='') as f:
                for _ in csv.reader(f, strict=True):
                    pass
        elif ext == '.py':
            import tokenize
            with tokenize.open(path) as f:
                source = f.read()
            try:
                ast.parse(source)
            except SyntaxError as e:
                warnings.append({'path': name, 'warning': 'Original Python syntax: ' + str(e)})
        else:
            counts['byte_checks_only'] += 1
            return
        counts['format_' + ext] += 1
    except Exception as e:
        issues.append({'kind': 'format', 'path': name, 'error': str(e)[:300]})
        if ext == '.png':
            png_diagnostics.append(diagnose_png(path))

def diagnose_png(path):
    data = path.read_bytes()
    info = {'path': str(path.relative_to(ROOT)), 'bytes': len(data), 'chunks': []}
    chunks = []
    pos = 8
    complete = data[:8] == b'\x89PNG\r\n\x1a\n'
    while complete and pos + 8 <= len(data):
        n = struct.unpack('>I', data[pos:pos+4])[0]
        tag = data[pos+4:pos+8]
        payload = data[pos+8:pos+8+n]
        crc = data[pos+8+n:pos+12+n]
        info['chunks'].append({'type': tag.decode('ascii', errors='replace'), 'declared': n, 'available': len(payload), 'crc_bytes': len(crc)})
        if len(payload) != n:
            complete = False
            break
        chunks.append((tag, payload))
        pos += n + 12
    try:
        compressed = b''.join(v for k, v in chunks if k == b'IDAT')
        dec = zlib.decompressobj()
        raw = dec.decompress(compressed) + dec.flush()
        info['zlib_eof'] = dec.eof
        info['decoded_bytes'] = len(raw)
        if not complete or not dec.eof or not any(k == b'IHDR' for k,v in chunks):
            info['repair'] = 'Not recoverable without replacing missing data'
            return info
        if not any(k == b'IEND' for k,v in chunks):
            chunks.append((b'IEND', b''))
        fixed = b'\x89PNG\r\n\x1a\n' + b''.join(struct.pack('>I',len(v)) + k + v + struct.pack('>I', zlib.crc32(k+v)&0xffffffff) for k,v in chunks)
        from PIL import Image
        with Image.open(io.BytesIO(fixed)) as im:
            im.verify()
        with Image.open(io.BytesIO(fixed)) as im:
            im.load()
        out = ROOT / 'verification-results/recovered'
        out.mkdir(parents=True, exist_ok=True)
        filename = path.stem + '_reparada.png'
        (out / filename).write_bytes(fixed)
        info.update({'repair': 'Only PNG checksums and end marker rebuilt; compressed pixel bytes unchanged', 'repaired_filename': filename, 'repaired_sha256': hashlib.sha256(fixed).hexdigest(), 'repaired_base64': base64.b64encode(fixed).decode()})
    except Exception as e:
        info['repair'] = 'Unable to reconstruct complete pixel stream: ' + str(e)[:250]
    return info

def main():
    manifest = json.loads((ROOT / 'catalogo/manifest.json').read_text())
    bundle = json.loads((ROOT / 'catalogo/paquetes.json').read_text())
    for rec in manifest:
        contained(rec['path'])
    for item in bundle['files']:
        for name in item['paths']:
            contained(name)
    for part in bundle['parts']:
        check_bytes(contained(part['path']), part, 'bundle_parts_verified')
    if issues:
        raise RuntimeError('Package-part integrity failed')
    restoration = subprocess.run([sys.executable, str(ROOT / 'restaurar_archivos_grandes.py')], cwd=ROOT, capture_output=True, text=True)
    if restoration.returncode:
        issues.append({'kind': 'restoration', 'error': restoration.stderr[-1000:]})
    else:
        counts['restoration_passed'] = 1
    for rec in manifest:
        check_bytes(contained(rec['path']), rec, 'original_paths_verified')
    tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    paths = {r['path'] for r in manifest}
    paths.update(n for n in tracked if n and not n.startswith(('_paquetes/', '.github/')))
    seen = set()
    for name in sorted(paths):
        p = contained(name)
        if not p.is_file():
            continue
        key = digest(p)
        if key in seen:
            continue
        seen.add(key)
        inspect_format(p)
    counts['catalogue_originals'] = len(manifest)
    counts['unique_contents_inspected'] = len(seen)
    report = {'commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), 'counts': dict(counts), 'issues': issues, 'warnings': warnings, 'png_diagnostics': png_diagnostics, 'scope': 'Byte preservation, reconstruction and format parsing; not scientific peer review or execution of original programs.'}
    out = ROOT / 'verification-results'
    out.mkdir(exist_ok=True)
    (out / 'audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print('AUDIT_RESULT_JSON=' + json.dumps(report, ensure_ascii=False))
    summary = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary:
        with open(summary, 'a') as f:
            f.write('# Verificación de publicación\n\n```json\n' + json.dumps(report, ensure_ascii=False, indent=2) + '\n```\n')
    return bool(issues)

if __name__ == '__main__':
    sys.exit(main())
