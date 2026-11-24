# Operational Symmetry Group

Status: validation/explanation utility, not a German Gamma core module.

## Definition

For a structural signature `K(X)` and a declared transformation family `G_set`:

```text
Sym(X) = { G in G_set : d(K(X), K(G(X))) <= epsilon }
```

Under a declared horizon:

```text
Sym_H(X) = { G in G_set : d(K(Pi_H(X)), K(Pi_H(G(X)))) <= epsilon }
```

Lost symmetries:

```text
DeltaSym = Sym(X) \\ Sym_H(X)
```

Interpretation:

```text
DeltaSym != empty
```

means:

```text
the declared horizon changed which transformations preserve K.
```

## Output Classes

```text
preserved
lost_by_horizon
induced_by_horizon
broken_in_both
```

## Boundary

This is an operational symmetry test over declared transformations and a
declared structural signature. It is not a proof of universal physical symmetry.

