"""Compile the Spanish and English manuscripts; fail on unresolved refs or overflow."""
from pathlib import Path
import subprocess,shutil,tempfile
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"manuscripts";OUT.mkdir(exist_ok=True)
for lang,title in [("es","Destino_Termodinamico_Barion_Antibarion_ES"),("en","Baryon_Antibaryon_Thermal_Audit_EN")]:
    build_root=ROOT/"build";build_root.mkdir(exist_ok=True)
    cache=Path(tempfile.mkdtemp(prefix=f'{lang}_',dir=build_root))
    args=["pdflatex","-interaction=nonstopmode","-halt-on-error",f"-output-directory={cache}",f"paper_{lang}.tex"]
    for _ in range(2):
        p=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,errors='replace')
        (cache/"build_stdout.txt").write_text(p.stdout+p.stderr)
        if p.returncode:raise RuntimeError(f"LaTeX failed; inspect {cache}")
    log=(cache/f"paper_{lang}.log").read_text(errors='replace')
    if "Overfull" in log or "undefined" in log.lower() or "Overfull" in p.stdout or "undefined" in p.stdout.lower():raise RuntimeError(f"Unresolved layout/reference issue: {cache}")
    assert (cache/f"paper_{lang}.pdf").read_bytes().rstrip().endswith(b'%%EOF')
    shutil.copy2(cache/f"paper_{lang}.pdf",OUT/f"{title}.pdf")
    print(OUT/f"{title}.pdf")

