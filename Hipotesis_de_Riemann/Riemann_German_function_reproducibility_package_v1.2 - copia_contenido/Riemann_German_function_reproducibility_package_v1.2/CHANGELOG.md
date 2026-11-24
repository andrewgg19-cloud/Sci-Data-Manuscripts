# Changelog

## 1.2.0 - 2026-09-04

- Added `reproduce.py` as the canonical one-command reproduction entry point.
- Added a frozen 15-ordinate dataset so the canonical audit does not require
  recalculating zeros with `mpmath`.
- Added `verify_reproducibility.py`, which checks the finite invariants,
  requires the bridge to remain unproved, and rejects any global RH claim.
- Added an internal tamper test demonstrating that
  `global_RH_proved=true` is rejected.
- Added `REPRODUCIBILITY.md` with the exact command and expected result.

## 1.1.0 - 2026-09-04

- Standardized all finite zero counts to the positive-ordinate convention
  `0 < gamma <= T`.
- Renamed the preferred external-count option to `--supplied-total-count`;
  the legacy spelling remains available for compatibility.
- Added validation for positive, strictly increasing, nonduplicated zero
  ordinates and for consistency of the externally supplied total count.
- Clarified that external counts are recorded but not authenticated by the
  script and that no finite computation proves RH.
- Added the finite Chebyshev/von Mangoldt diagnostic `B_epsilon(P)`, endpoint
  ratios, and upper-half tail maxima.
- Added a Bonferroni correction for selection over the epsilon grid in the
  Monte Carlo report.
- Added runtime-version metadata, pinned requirements, citation metadata, and
  separate software/documentation licenses.
- Corrected the command examples to use the included script filename.
