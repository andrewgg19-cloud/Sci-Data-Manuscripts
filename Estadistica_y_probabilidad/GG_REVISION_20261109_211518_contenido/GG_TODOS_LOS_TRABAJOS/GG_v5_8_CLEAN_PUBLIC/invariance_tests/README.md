# German Gamma v5.8 - K(X) Invariance Test

Status: validation suite for transformed structural equivalence.

This test defines a concrete structural signature:

```text
K(X) = {
  radius_mean,
  radius_std,
  radius_entropy,
  mean_L_norm,
  rotation_coherence
}
```

It then compares:

```text
d(K(X), K(G(X)))
```

under declared transformations:

```text
I
P_mirror_x
C_sign
T_reverse
Rz_90
```

## Interpretation

If:

```text
d(K(X), K(G(X))) <= epsilon
```

then:

```text
K is conserved under G
```

If:

```text
d(K(X), K(G(X))) > epsilon
```

then:

```text
K changes under G
```

This is a transformation test, not a universal proof.

## Operational Symmetry Group

The file:

```text
operational_symmetry_group.py
```

constructs:

```text
Sym(X)
Sym_H(X)
DeltaSym = Sym(X) \\ Sym_H(X)
```

and reports which symmetries are preserved, lost by horizon, induced by horizon,
or broken in both.

Correct horizon definition:

```text
Sym_H(X) = { G : d(K(Pi_H(X)), K(Pi_H(G(X)))) <= epsilon }
```
