# Transformed Equivalence and Manifestation

Status: explanatory and interpretive layer only. This module does not add a new
validated metric to the frozen German Gamma v5.8 core.

## Central Problem

A structure can look different without being structurally broken.

German Gamma therefore separates:

```text
different form != broken structure
```

The model must test whether an observed difference is a transformed
manifestation of the same underlying structure.

## Transformation Family

Let:

```text
X = observed system
K(X) = structural reading or metric
G = transformation
```

Allowed transformation family:

```text
G in { I, P, T, C, CP, CT, PT, CPT }
```

where:

```text
I   = identity
P   = mirror / parity transformation
T   = temporal inversion
C   = sign, charge, or conjugation transformation
CPT = composed transformation
```

For ordinary datasets, `C` does not mean physical antimatter unless the variables
really encode charge-like states. Operationally it can represent a declared
sign/conjugation transformation.

## Manifestation Equation

A transformed manifestation is:

```text
M_G(X) = G(X)
```

Two states are equivalent under transformation `G` when:

```text
X ~_G Y  iff  Y = G(X)  and  d(K(X), K(Y)) <= epsilon
```

This means:

```text
same structure under a different manifestation
```

not:

```text
identical raw appearance
```

## Asymmetry Under Transformation

For each transformation:

```text
A_G(X) = d(K(X), K(G(X)))
```

If:

```text
A_G(X) <= epsilon
```

then:

```text
structure conserved under G
```

If:

```text
A_G(X) > epsilon
```

then:

```text
structure differs under G
```

but this still does not prove cause.

## Decision Rule

Before declaring structural rupture:

```text
1. Detect difference.
2. Test identity I.
3. Test mirror/parity P.
4. Test temporal inversion T.
5. Test sign/conjugation C.
6. Test composed transformations CP, CT, PT, CPT.
7. Only then classify rupture source.
```

If at least one transformation preserves structure:

```text
exists G such that A_G(X) <= epsilon
```

then:

```text
transformed_equivalence_candidate
```

If no transformation preserves structure:

```text
for all G, A_G(X) > epsilon
```

then:

```text
structural_rupture_candidate
```

The rupture must still be classified as:

```text
intrinsic
horizon-induced
noise-driven
support-limited
not evaluable
```

## Antimatter Lesson

In physics:

```text
C |p> = |p_bar>
```

and:

```text
CPT |p, q, x, t> = |p_bar, -q, -x, -t>
```

The lesson for German Gamma is restricted and formal:

```text
the opposite of a structure is not always its mirror;
sometimes it is a composed transformation.
```

Therefore:

```text
P broken does not imply structure broken.
```

One must ask whether:

```text
CPT or another declared composite transformation preserves K.
```

## Output Labels

Allowed labels:

```text
transformed_equivalence_candidate
simple_symmetry_broken_composite_preserved
structural_rupture_candidate
horizon_induced_rupture_candidate
noise_unstable_transformation
support_limited_transformation
not_evaluable
```

Forbidden labels:

```text
proof_of_antimatter
physical_CPT_test
fraud
intent
absolute_reality
```

## Summary

```text
German Gamma must not stop at visible difference.
It must test whether the difference is a conserved structure under another
declared transformation.
```

