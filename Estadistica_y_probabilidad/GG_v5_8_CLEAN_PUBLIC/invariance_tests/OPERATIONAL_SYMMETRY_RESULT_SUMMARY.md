# Operational Symmetry Result Summary

Status:

```text
passed under corrected definition
```

## Definition Tested

```text
Sym(X) = { G : d(K(X), K(G(X))) <= epsilon }
```

Under horizon:

```text
Sym_H(X) = { G : d(K(Pi_H(X)), K(Pi_H(G(X)))) <= epsilon }
```

Lost symmetries:

```text
DeltaSym = Sym(X) \ Sym_H(X)
```

## Horizon

```text
Pi_H(X) = { x : x1 > 0 }
```

## Minimal Orbit Result

```text
n_total       = 240
n_horizon     = 122
survival_rate = 0.508333
epsilon       = 0.05
```

```text
Sym(X)   = { C_sign, I, P_mirror_x, Rz_90, T_reverse }
Sym_H(X) = { I, Rz_90, T_reverse }
```

Lost by horizon:

```text
DeltaSym = { C_sign, P_mirror_x }
```

Interpretation:

```text
The original structural signature was conserved under sign and mirror
transformations, but the declared horizon x1 > 0 removed that conservation.
```

## Noise Result

```text
n_total       = 300
n_horizon     = 154
survival_rate = 0.513333
epsilon       = 0.05
```

```text
Sym(X)   = { C_sign, I, P_mirror_x, Rz_90, T_reverse }
Sym_H(X) = { I, T_reverse }
```

Lost by horizon:

```text
DeltaSym = { C_sign, P_mirror_x, Rz_90 }
```

## Conclusion

The algorithm demonstrates the operational symmetry definition:

```text
the system has a measurable symmetry family under K(X),
and a declared horizon can remove members of that family.
```

Valid claim:

```text
Sym(X) and Sym_H(X) are computable for declared K, transformations, epsilon,
and horizon.
```

Invalid claim:

```text
universal physical symmetry proven.
```

