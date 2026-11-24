# Función Germán Reproducibility Package v1.2.0

This package adds the finite off-critical-line exclusion predicate to the reproducible Riemann graph audit script.

## Función Germán

```tex
\mathfrak{G}(T)=
N_{\mathrm{strip}}(T)-N_{1/2}(T)=\# Z_{\mathrm{off}}(T)
```

The current name is **función Germán**. The symbol is \(\mathfrak{G}\), with the machine-readable JSON name `G_German`. Version 1.2.0 uses positive ordinates throughout, validates input ordinates and count consistency, reports a conservative correction for epsilon selection, and adds a fail-closed canonical verifier.

## One-command reproduction

After installing `requirements.txt`, run:

```bash
python reproduce.py
```

This creates `canonical_audit_reproduced.json` from the included frozen
15-ordinate dataset and invokes `verify_reproducibility.py --self-test`. The
verifier fails if any `global_RH_proved` field is changed from `false`, and it
requires the bridge status to remain `NV_unproved_methodological_lemma`. See
`REPRODUCIBILITY.md` for the expected output and scope.

where

```tex
Z_{\mathrm{off}}(T)=
\{\rho=\beta+i\gamma:
\zeta(\rho)=0,\ 0<\beta<1,\ \beta\ne1/2,\ 0<\gamma\le T\}.
```

All counts in this package use **positive ordinates only**. A symmetric
convention using `0<|gamma|<=T` would require counting both signs and is not
used here.

## Interpretation

- If only critical-line zeros are supplied, the script does not certify `Z_off(T)=empty`.
- If a valid external total strip count `N_strip_plus(T)` is supplied and equals the counted critical-line zeros, the script reports `G_German(T)=0`; the conclusion is conditional on the validity of that supplied count, which the script does not authenticate.
- RH is not proved by any finite run. RH would require `G_German(T)=0` for every finite `T`.

## Función Germán Primo-Limitada

The modified function can also carry a finite prime channel:

```tex
\mathfrak{G}(T;P)
=\left(
N_{\mathrm{strip}}(T)-N_{1/2}(T),
\Sigma_\pi(P),
\widehat{\Sigma}_\pi(P),
\psi(P),
A_P|_{\Gamma_T}
\right).
```

Here

```tex
\Sigma_\pi(P)=\sum_{p\le P}p,
\qquad
\widehat{\Sigma}_\pi(P)
=\frac{\Sigma_\pi(P)}{1+\Sigma_\pi(P)}.
```

The raw prime sum \(\Sigma_\pi(P)\) is the finite prime-limit marker requested in the función Germán. Since the raw sum grows without bound as `P` increases, the bounded marker \(\widehat{\Sigma}_\pi(P)\in[0,1)\) is also reported so the numerical channel does not blow up.

```tex
\psi(P)=\sum_{p^m\le P}\log p
=\sum_{n\le P}\Lambda(n),
```

and

```tex
A_P(t)=
\sum_{p^m\le P}
\frac{\log p}{\sqrt{p^m}}
\cos(t\,m\log p).
```

The script reports this as `German_function.prime_limit_extension` whenever `--prime-limit P` is supplied. The visible name is `función Germán primo-limitada`. The count component remains the finite certification channel for `Z_off(T)=empty`; the prime components are finite arithmetic detectors linked to the standard Chebyshev/von Mangoldt route and the explicit formula.

This is still a truncation. A proof-level statement would require a uniform theorem controlling the prime channel as both `P` and `T` grow.

The JSON also records the finite diagnostic

```tex
B_\epsilon(P)=\max_{2\le x\le P,\ x\in\mathbb Z}
\frac{|\psi(x)-x|}{x^{1/2+\epsilon}}.
```

Every finite value is expected and is not evidence of a uniform bound. The
RH-equivalent obligation is boundedness independent of `P`, for every
`epsilon>0`.

## Función Germán Bridge Lemma

The script now adds `German_bridge_lemma` inside `Z_off_finite_audit`. Its visible name is `lema puente de la función Germán`. Its status is intentionally marked as:

```text
NV_unproved_methodological_lemma
```

The proposed bridge is:

```tex
\left(
\Sigma_\pi(P),
\widehat{\Sigma}_\pi(P),
\psi(P),
A_P|_{\Gamma_T}
\right)
\Longrightarrow
N_{\mathrm{strip}}(T)=N_{1/2}(T)
```

uniformly in the finite height parameter `T`, with a controlled choice of prime cutoff `P=P(T)`.

If such a non-circular theorem were proved for every finite `T`, then:

```tex
\mathfrak{G}(T)=0
\quad\text{for every finite }T,
```

which is equivalent to the absence of off-critical-line zeros. The current script does not prove this lemma; it only records the finite inputs and the missing proof obligations.

## Adjoint Mirror

The script now also reports the mirror-adjoint operator

```tex
R^\ast(\rho)=1-\overline{\rho}.
```

For \(\rho=\beta+i\gamma\),

```tex
R^\ast(\beta+i\gamma)=(1-\beta)+i\gamma.
```

The fixed locus is exactly the critical line:

```tex
\rho=R^\ast(\rho) \iff \Re(\rho)=1/2.
```

The mirror-augmented función Germán is

```tex
\mathfrak{G}^{\ast}(T)
=\sum_{\rho\in Z_{\mathrm{strip}}(T)}
|\rho-R^\ast(\rho)|^2
=\sum_{\rho\in Z_{\mathrm{strip}}(T)}
|2\Re(\rho)-1|^2.
```

It is zero exactly when every zero in the finite strip segment is fixed by the mirror. As with the count form, it requires an independent total strip enumeration or count; listed critical-line zeros alone only verify that the listed points are fixed.

## Mobius Start Marker

The script also records a finite start/closure marker:

```tex
\mathfrak{M}(T).
```

This implements the idea of marking the finite path before traversing the folded band. In the script this is reported as `Mobius_start_marker`:

- the start mark is the first listed critical-line zero in `0<gamma<=T`;
- the finite end mark is the cap at `T`, with the last listed zero below `T` and the next listed zero above `T`;
- the band coordinate is written as `v=beta-1/2`, with the Mobius identification `(0,v)~(1,-v)`;
- on the center line `v=0`, the endpoint is identified with the starting side, while an oriented transverse marker needs two turns to recover the same orientation;
- off-line points with `v!=0` are paired by the fold, not erased.

Therefore the marker is accepted as an arithmetic closure only when the independently certified total strip count equals the counted critical-line zeros:

```tex
\mathfrak{G}(T)=0.
```

This remains a finite statement. RH would require this closure with no off-line remainder for every finite `T`.

## Monte Carlo Selector

The script can also estimate finite null probabilities:

```bash
--mc-samples 2000 --mc-seed 2510
```

This adds `monte_carlo_selector` to the JSON output. It compares the observed unfolded-zero Rips graph against two predeclared null models:

- `uniform_unfolded_range`: draws the same number of points uniformly over the same unfolded interval.
- `bootstrap_rescaled_empirical_gaps`: resamples the observed unfolded gaps with replacement and rescales them to the same total range.

For each epsilon in the fixed grid, the script reports the observed `beta0`, null mean, null quantiles, and Monte Carlo tail probabilities. The selection rule is:

```tex
\epsilon^\ast
=\arg\min_\epsilon
\Pr_{\mathrm{null}}\{\beta_0^{\mathrm{null}}(\epsilon)
\le \beta_0^{\mathrm{obs}}(\epsilon)\}.
```

This is a finite model-selection tool. It estimates probabilities under stated null assumptions; it does not enumerate all possible zeros, does not replace an independent count `N_strip(T)`, and does not prove RH.

Because the displayed epsilon is selected by minimizing the raw left-tail
probability, version 1.1.0 also reports a Bonferroni-adjusted family-wise value
over the fixed epsilon grid.

## Requirements

- Python 3.12 or later
- NumPy 2.3.5
- mpmath 1.4.1, unless `--zeros-data` supplies the ordinates

Install with:

```bash
python -m pip install -r requirements.txt
```

## Example Runs

Local-only audit:

```bash
python Riemann_graph_method_reproducible_with_German_function.py --n 15 --zoff-T 50 --out riemann_graph_audit_with_zoff_german_T50_local.json
```

Audit with external total-count evidence:

```bash
python Riemann_graph_method_reproducible_with_German_function.py --n 15 --zoff-T 50 --supplied-total-count 10 --certification-source "Published finite count for positive ordinates; supplied externally and not authenticated by this script" --out riemann_graph_audit_with_zoff_german_T50_external_count.json
```

Mirror sample:

```bash
python Riemann_graph_method_reproducible_with_German_function.py --n 15 --zoff-T 50 --supplied-total-count 10 --mirror-beta 0.7 --mirror-gamma 20 --out riemann_graph_audit_with_zoff_german_mirror_T50.json
```

Monte Carlo + mirror sample:

```bash
python Riemann_graph_method_reproducible_with_German_function.py --n 15 --zoff-T 50 --supplied-total-count 10 --mirror-beta 0.7 --mirror-gamma 20 --mc-samples 2000 --mc-seed 2510 --out riemann_graph_audit_with_zoff_german_montecarlo_T50.json
```

Prime-limit función Germán sample:

```bash
python Riemann_graph_method_reproducible_with_German_function.py --n 15 --zoff-T 50 --supplied-total-count 10 --mirror-beta 0.7 --mirror-gamma 20 --mc-samples 2000 --mc-seed 2510 --prime-limit 100 --out riemann_graph_audit_with_zoff_german_prime_limit_T50.json
```
