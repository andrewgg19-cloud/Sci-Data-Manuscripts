# Asymmetry Source Decomposition

Status: explanatory and interpretive layer only. This module does not add a new
validated metric to the frozen German Gamma v5.8 core.

## Problem

A broken symmetry is not automatically evidence of bias.

Some asymmetries are real properties of the system. Others are induced by the
observable horizon, the filter, finite sampling, or noise.

German Gamma therefore separates:

```text
measured asymmetry != induced asymmetry
```

## Core Decomposition

Let:

```text
A_M = measured mirror asymmetry
```

Then:

```text
A_M = A_int + A_H + A_eta
```

where:

```text
A_int = intrinsic asymmetry of the system
A_H   = asymmetry induced by horizon/filter
A_eta = asymmetry caused by noise, sampling, or measurement instability
```

This is a classification principle, not an automatic proof.

## Mirror Test

Let:

```text
M(X) = mirror transformation of X
K(X) = structural reading or metric
Pi_H(X) = observable horizon/filter applied to X
```

Measured mirror asymmetry:

```text
A_M(X) = d(K(X), K(M(X)))
```

Post-horizon asymmetry:

```text
A_M^H(X) = d(K(Pi_H(X)), K(Pi_H(M(X))))
```

Horizon contribution:

```text
A_H approx A_M^H(X) - A_M(X)
```

with the constraint:

```text
A_H is interpretable only if stable under resampling and noise checks.
```

## Reading Rule

```text
Case 1:
A_M(X) high before horizon
and A_M^H(X) remains high
-> possible intrinsic asymmetry.

Case 2:
A_M(X) low before horizon
but A_M^H(X) high after horizon
-> possible horizon-induced asymmetry.

Case 3:
A_M^H(X) unstable under bootstrap/permutation/noise
-> possible noise or sampling artifact.

Case 4:
support is lost under the horizon
-> raw asymmetry is not fully evaluable.
```

## Physical Lesson From Weak Interaction

The weak interaction violates mirror symmetry:

```text
L_weak(x) != L_weak(-x)
```

This teaches an important rule:

```text
not every mirror asymmetry is observational bias.
```

In German Gamma terms:

```text
K(X) != K(M(X))
```

can mean:

```text
intrinsic asymmetry
horizon-induced deformation
noise
or insufficient support
```

The model must classify the likely source instead of declaring a single cause.

## Operational Output Labels

Allowed labels:

```text
intrinsic_asymmetry_candidate
horizon_induced_asymmetry_candidate
noise_unstable_asymmetry
support_limited_asymmetry
not_evaluable
```

Forbidden labels:

```text
fraud
intent
causality_proven
absolute_asymmetry
```

## Integration With German Gamma

This module protects the model from over-alerting.

It adds a conservative rule:

```text
German Gamma must not punish symmetry breaking by default.
It must ask where the asymmetry came from.
```

Summary:

```text
strong interaction -> observability restricted by allowed combinations
weak interaction   -> asymmetry can be intrinsic
Noether principle  -> conserved structure matters
German Gamma       -> classify conservation, deformation, and source of rupture
```

