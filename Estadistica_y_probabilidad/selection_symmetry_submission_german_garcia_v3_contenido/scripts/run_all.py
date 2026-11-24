"""Regenerate all reproducible results and figures."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = [
    "simulate_chsh_biased_filtering.py",
    "compute_information_bounds_bell.py",
    "generate_archetypal_selection_structures.py",
    "simulate_biomedical_dropout_selection.py",
]


def main() -> None:
    for script in SCRIPTS:
        path = ROOT / "scripts" / script
        print(f"running {path.relative_to(ROOT)}")
        subprocess.run([sys.executable, str(path)], cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
