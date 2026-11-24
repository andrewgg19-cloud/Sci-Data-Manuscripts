"""Compile this revised English manuscript with pdfLaTeX.

Usage: python build_english.py
Requires a TeX installation with the packages listed in each preamble.tex.
Numerical simulations are not run by this script.
"""
from pathlib import Path
import json
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'pdf'
OUT.mkdir(exist_ok=True)
jobs = [('hrg', 'HRG_50MeV_Revised_EN')]
summaries = []
for folder, name in jobs:
    source = ROOT / folder
    cache = ROOT / 'build' / folder
    cache.mkdir(parents=True, exist_ok=True)
    cmd = ['pdflatex','-interaction=nonstopmode','-halt-on-error',
           '-no-shell-escape',f'-output-directory={cache}','paper_en.tex']
    for step in range(3):
        p = subprocess.run(cmd, cwd=source, capture_output=True, text=True, errors='replace')
        (cache/f'pass_{step+1}.txt').write_text(p.stdout+p.stderr)
        if p.returncode:
            raise RuntimeError(f'Compilation failed: {cache}/pass_{step+1}.txt')
    log = (cache/'paper_en.log').read_text(errors='replace')
    issues = [line for line in log.splitlines()
              if 'Overfull' in line or 'undefined' in line.lower()
              or 'Missing character:' in line]
    shutil.copyfile(cache/'paper_en.pdf', OUT/f'{name}.pdf')
    summaries.append({'paper':name,'compilation':'succeeded','layout_or_reference_issues':issues})
    print(name, issues)
(OUT/'build_summary.json').write_text(json.dumps(summaries, indent=2)+'\n')
if any(s['layout_or_reference_issues'] for s in summaries):
    raise RuntimeError('Inspect the reported reference or layout issues before release.')
