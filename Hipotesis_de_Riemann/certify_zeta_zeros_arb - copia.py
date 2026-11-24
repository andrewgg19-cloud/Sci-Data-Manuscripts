#!/usr/bin/env python3
"""Produce a rigorous interval certificate for consecutive zeta zeros.

Requires python-flint.  acb.zeta_zeros uses FLINT/Arb ball arithmetic and
Turing's method to certify the indices of the returned critical-line zeros.
"""

import csv
import hashlib
import json
import sys
from datetime import datetime, timezone

from flint import acb, acb_series, ctx


COUNT = int(sys.argv[1]) if len(sys.argv) > 1 else 10_000
OUTPUT = sys.argv[2] if len(sys.argv) > 2 else "certified_zeta_zeros_1_10000.csv"
ctx.dps = 30
ctx.cap = 2

zeros = acb.zeta_zeros(1, COUNT)
real_exact_half = all(z.real.is_exact() and z.real == 0.5 for z in zeros)
ordered_disjoint = all(
    zeros[k].imag.upper() < zeros[k + 1].imag.lower()
    for k in range(COUNT - 1)
)
derivatives = []
for z in zeros:
    s = acb(z.real, z.imag)
    derivatives.append(acb_series([s, 1]).zeta()[1])
all_derivatives_exclude_zero = all(not derivative.contains(0) for derivative in derivatives)

if not (real_exact_half and ordered_disjoint and all_derivatives_exclude_zero):
    raise RuntimeError("The requested interval certification checks failed")

with open(OUTPUT, "w", newline="", encoding="utf-8") as stream:
    writer = csv.writer(stream)
    writer.writerow([
        "index_n",
        "real_part_exact",
        "imaginary_part_certified_ball",
        "zeta_prime_certified_ball",
        "zeta_prime_excludes_zero",
    ])
    for n, (z, derivative) in enumerate(zip(zeros, derivatives), start=1):
        writer.writerow([n, "1/2", z.imag.str(30), derivative.str(20), "true"])

with open(OUTPUT, "rb") as stream:
    digest = hashlib.sha256(stream.read()).hexdigest()

summary = {
    "generated_utc": datetime.now(timezone.utc).isoformat(),
    "software": "python-flint 0.9.0 / FLINT-Arb",
    "precision_decimal_digits": 30,
    "first_index": 1,
    "last_index": COUNT,
    "all_real_parts_exactly_one_half": real_exact_half,
    "all_imaginary_balls_pairwise_ordered_and_disjoint": ordered_disjoint,
    "all_zeta_derivative_balls_exclude_zero": all_derivatives_exclude_zero,
    "last_zero": zeros[-1].str(30),
    "csv_sha256": digest,
}

with open(OUTPUT + ".json", "w", encoding="utf-8") as stream:
    json.dump(summary, stream, indent=2)
    stream.write("\n")

print(json.dumps(summary, indent=2))
