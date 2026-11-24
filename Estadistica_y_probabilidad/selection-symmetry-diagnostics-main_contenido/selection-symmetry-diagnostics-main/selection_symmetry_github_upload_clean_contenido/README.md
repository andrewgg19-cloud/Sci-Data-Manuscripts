# Selection Symmetry as an Operational Diagnostic for Correlations under Data Filtering

This repository contains reproducible simulation code and a LaTeX manuscript for:

**Selection Symmetry as an Operational Diagnostic for Correlations under Data Filtering: Reproducible Stress Tests across Bell, Biomedical, and Dataset-Shift Examples**

The project studies selection symmetry as an operational diagnostic for correlations under data filtering. It focuses on how filtering can create apparent structure in selected data, including spurious Bell-CHSH excesses, and how information bounds quantify the minimum selection information associated with such effects.

The paper does **not** propose new physics. It presents a model-independent diagnostic framework for checking whether a reported correlation is robust against selection-induced explanations.

The intended contribution is interdisciplinary: it connects selection bias, independence diagnostics, mutual information, reproducible simulation, and physical-correlation workflows in one operational vocabulary.

The framework is complementary to existing methods such as missing-data models, causal DAGs, inverse probability weighting, dataset-shift correction, dataset/model documentation, and Bell-test loophole analysis. It does not replace these approaches; it supplies a portable diagnostic target: whether \(F\) carries information about \(R\).

## Core Claim

This project develops a reproducible and interdisciplinary framework for diagnosing when a correlation is invariant under data selection and when it can be explained as information introduced by the filtering mechanism itself.

## Why Keep the Bell-CHSH Case?

The Bell-CHSH example is retained as a compact stress test for the framework. It shows, in a mathematically sharp setting, how response-dependent event selection can transform a classical unselected ensemble into a post-selected sample with apparent CHSH excess.

This is not a claim about real loophole-free Bell experiments. It is a reusable diagnostic lesson:

```text
if event selection F is informative about the reported product R, then I(R;F) > 0 and the selected CHSH statistic is not invariant under filtering.
```

Representative simulated output:

```text
bias = 0.44
p_keep = 0.551
S_observed = 3.200
I(R;F) = 0.101 nats
I_min_bound = 0.0248 nats
```

The paper connects this stress test to the Bell/CHSH, data-rejection, detection-loophole, and loophole-free Bell-test literature.

## High-Relevance Archetypes

Beyond Bell-CHSH, the repository uses synthetic archetypes from areas where selection is currently central to scientific practice:

- **AI/ML dataset filtering**: benchmark curation, dataset inclusion, and dataset shift.
- **Dataset/model documentation**: selection diagnostics that complement Datasheets for Datasets and Model Cards.
- **Single-cell omics QC**: quality-control filtering that may alter cell-type representation.
- **Biomedical dropout**: follow-up or missingness that depends on the response.

These are not analyses of real datasets. They are controlled diagnostic settings chosen because the same question is highly relevant across modern scientific workflows:

```text
does the inclusion/filtering mechanism F carry information about the reported response R?
```

For AI/ML, the framework can be read as a quantitative companion to dataset and model documentation: beyond reporting how a dataset or benchmark was filtered, it asks whether the filtering variable is informative about the reported outcome or performance measure.

## Repository Layout

```text
.
|-- README.md
|-- Makefile
|-- requirements.txt
|-- data/
|-- results/
|-- scripts/
|   |-- run_all.py
|   |-- simulate_chsh_biased_filtering.py
|   |-- compute_information_bounds_bell.py
|   |-- generate_archetypal_selection_structures.py
|   |-- simulate_biomedical_dropout_selection.py
|   `-- plotting_utils.py
|-- tests/
|   `-- test_reproducibility.py
`-- paper/
    |-- main.tex
    `-- figures/
```

## Setup

```bash
pip install -r requirements.txt
```

The scripts prefer the standard scientific Python stack (`numpy`, `pandas`, `matplotlib`) for publication-quality figures. They also include a standard-library PNG fallback so the core simulations remain runnable in constrained environments.

## Reproduce Results

Run everything from the repository root:

```bash
python scripts/run_all.py
```

Or run individual scripts:

```bash
python scripts/simulate_chsh_biased_filtering.py
python scripts/compute_information_bounds_bell.py
python scripts/generate_archetypal_selection_structures.py
python scripts/simulate_biomedical_dropout_selection.py
```

The scripts use fixed seeds and write:

- CSV files to `results/`
- PNG figures to `paper/figures/`

## Test Reproducibility

```bash
python -m unittest discover -s tests
```

The tests check that artifacts are generated, the CHSH selection-information trend is present, the information bound is exactly the stated formula, and the archetypal-selection columns are internally consistent.

## Build the Paper

```bash
latexmk -pdf paper/main.tex
```

If `latexmk` is unavailable, compile from the `paper/` directory with:

```bash
pdflatex main.tex
pdflatex main.tex
```

## Mathematical Core

Let `F in {0,1}` be a selection function and `R` an observable. Selection symmetry is expressed as:

```text
R independent of F
```

Equivalently:

```text
I(R;F) = 0
```

For a CHSH diagnostic with selected fraction `p` and observed value `S > 2`, the operational lower bound used here is:

```text
I_min >= p(S - 2)^2 / 32
```

In the paper this is stated as a diagnostic proposition under explicit assumptions:

- the unselected reference obeys the local CHSH bound,
- the CHSH excess is attributed to a response-dependent selection channel,
- the selection displacement is measured by an operational total-variation scale,
- the channel information is controlled by a conservative Pinsker-type inequality.

This makes the bound a transparent diagnostic claim rather than an unsupported universal claim.

The robust signal criterion compares the bias needed to explain a signal with the maximum admissible bias:

```text
b_req > b_max
```

When this inequality holds, the signal is operationally robust against the modeled class of selection-bias explanations.

The practical robustness index is:

```text
rho_sel = b_req / b_max
```

Interpretation:

- `rho_sel > 1`: robust against the modeled selection explanation,
- `rho_sel ~= 1`: borderline,
- `rho_sel < 1`: selection explanation remains viable.

The paper also states a general information-bound template:

```text
I_min >= p alpha^2 Delta^2 / 2
```

where `Delta` is excess over a reference bound and `alpha` calibrates how much selection displacement is needed to produce that excess.

## Scope

The repository does not apply the criterion quantitatively to existing experiments. Real application would require access to the full selection mechanism, reconstruction pipeline, calibration structure, control samples, and uncertainty model.

The Bell-like, AI/ML, single-cell, and biomedical labels are archetypal selection structures, not analyses of real experiments or datasets. Because there is no shared physical control group across those domains, the repository uses synthetic counterfactual controls. The archetype script deliberately includes:

- a symmetric control case,
- a biased false-positive case,
- a borderline case,
- a robust case,
- a non-robust toy case.

This gives the model representation on both sides of the diagnostic equilibrium instead of only showing successful/robust examples.

The repository also includes a synthetic biomedical dropout example. It simulates treatment, severity, response, and follow-up. Because follow-up depends partly on response, the observed treatment contrast differs from the full-cohort contrast. This makes the framework more naturally applicable to biological, biomedical, and observational-data settings.

## Publication Positioning

This project is best framed as a methodological or interdisciplinary preprint, not as a claim of new physics. Suitable audiences include:

- philosophy/methodology of measurement,
- causal inference and selection bias,
- information-theoretic diagnostics,
- reproducible simulation studies,
- foundations-adjacent physics discussions.

The safest claim is:

```text
Selection symmetry provides a portable operational diagnostic for asking whether a reported correlation is invariant under the data-selection mechanism.
```

The project deliberately avoids quantitative claims about real experiments unless full internal selection definitions, control samples, and uncertainty models are available.

## Citation and License

Citation metadata are provided in `CITATION.cff`. The code and reproducibility materials are released under the MIT License; see `LICENSE`.
