# K(X) Invariance Result Summary

Status:

```text
passed under declared transformations
```

## Structural Signature

```text
K(X) = {
  radius_mean,
  radius_std,
  radius_entropy,
  mean_L_norm,
  rotation_coherence
}
```

## Transformation Test

Tested transformations:

```text
I
P_mirror_x
C_sign
T_reverse
Rz_90
```

Result on minimal orbit:

```text
conserved_transforms = I, P_mirror_x, C_sign, T_reverse, Rz_90
broken_transforms    = none
```

Result on random-walk noise:

```text
conserved_transforms = I, P_mirror_x, C_sign, T_reverse, Rz_90
broken_transforms    = none
```

Interpretation:

```text
This K is intentionally invariant to sign, mirror, time reversal, and rotation
because it measures structural magnitudes rather than raw orientation.
```

## Horizon Sensitivity Test

Declared horizon:

```text
Pi_H(X) = { x in X : x1 > 0 }
```

Observed distances:

```text
orbit_vs_horizon distance = 0.3986728007818515
noise_vs_horizon distance = 0.22389632073129875
epsilon                   = 0.05
```

Result:

```text
K is conserved under declared structure-preserving transformations.
K changes when the horizon cuts support.
```

## Conclusion

The test supports the limited claim:

```text
K(X) exists as a structural signature candidate for this validation setup.
```

It does not prove:

```text
universal invariance
domain truth
causality
physical conservation law
```
