#!/usr/bin/env python3
"""Run and verify the canonical finite Función Germán audit."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "canonical_audit_reproduced.json"


def main() -> int:
    audit_command = [
        sys.executable,
        str(ROOT / "Riemann_graph_method_reproducible_with_German_function.py"),
        "--n",
        "15",
        "--zeros-data",
        str(ROOT / "critical_line_zero_ordinates_first_15.json"),
        "--zoff-T",
        "50",
        "--supplied-total-count",
        "10",
        "--certification-source",
        "Externally supplied positive-ordinate count N_plus(50)=10; not authenticated by this script",
        "--mirror-beta",
        "0.7",
        "--mirror-gamma",
        "20",
        "--mc-samples",
        "2000",
        "--mc-seed",
        "2510",
        "--prime-limit",
        "100",
        "--out",
        str(OUTPUT),
    ]
    print("Running canonical finite audit...", flush=True)
    subprocess.run(
        audit_command,
        check=True,
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
    )

    print("Running fail-closed verification...", flush=True)
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "verify_reproducibility.py"),
            str(OUTPUT),
            "--self-test",
        ],
        check=True,
        cwd=ROOT,
    )
    print(f"Canonical output: {OUTPUT.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
