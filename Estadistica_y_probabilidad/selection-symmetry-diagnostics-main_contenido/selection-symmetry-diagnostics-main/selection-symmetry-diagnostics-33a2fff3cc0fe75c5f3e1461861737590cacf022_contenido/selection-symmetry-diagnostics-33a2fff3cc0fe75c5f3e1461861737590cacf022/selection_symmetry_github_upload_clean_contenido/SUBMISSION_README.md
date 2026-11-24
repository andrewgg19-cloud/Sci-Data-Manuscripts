# Submission Package

Title: Selection Symmetry as an Operational Diagnostic for Correlations under Data Filtering

This package contains a reproducible manuscript submission bundle.

## Contents

- `paper/main.tex`: LaTeX manuscript with embedded bibliography.
- `paper/selection_symmetry_german_garcia.pdf`: generated PDF preview/version for submission.
- `paper/figures/`: figures referenced by the manuscript.
- `scripts/`: reproducibility scripts.
- `results/`: generated CSV outputs.
- `tests/`: automated reproducibility checks.
- `README.md`: project overview and instructions.
- `requirements.txt`: Python dependencies.
- `Makefile`: convenience commands.
- `COVER_LETTER_TEMPLATE.md`: editable cover letter template.
- `LICENSE`: MIT License.
- `CITATION.cff`: citation metadata for GitHub/Zenodo.

## Reproduce

```bash
pip install -r requirements.txt
python scripts/run_all.py
python -m unittest discover -s tests
latexmk -pdf paper/main.tex
```

If `latexmk` is unavailable, compile from `paper/` with:

```bash
pdflatex main.tex
pdflatex main.tex
```

## Scope Statement

The manuscript presents a methodological and reproducible diagnostic framework. It does not propose new physics and does not make quantitative claims about real experiments or real datasets without access to their internal selection mechanisms.
