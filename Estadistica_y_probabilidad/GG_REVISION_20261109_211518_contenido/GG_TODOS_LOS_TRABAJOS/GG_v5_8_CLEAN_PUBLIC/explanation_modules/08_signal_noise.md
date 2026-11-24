# 08 - Signal and Noise

Purpose: explain how German Gamma should treat signal and noise without creating
false cleanliness.

## Principle

```text
Signal is filtered to recognize structure.
Noise is retained to measure uncertainty.
```

The goal is not to remove all noise. Removing all noise can destroy support,
reduce entropy artificially, and produce a false sense of certainty.

## Layers

```text
primary signal:
official source, direct dataset, paper, code, reproducible output

contextual noise:
discussion, repetition, disagreement, versions, weak signals

toxic noise:
spam, unsupported claims, source-less copying, non-traceable material
```

## Rule

```text
primary signal -> evidence
contextual noise -> uncertainty/context
toxic noise -> excluded
```

## Web Information

For information from the web:

```text
H = available source horizon
Gamma = admissibility filter
S = admitted signal
R = retained residual noise
```

The working state is:

```text
D_web = S + R
```

not:

```text
D_web = S only
```

because a perfectly clean web-state can be an artifact of over-filtering.

## Boundary

Noise does not become evidence. It remains labeled as uncertainty, variability,
or horizon residue.

## Sentence

```text
Noise must not be confused with evidence, but it should not be erased without
record; labeled noise measures uncertainty, boundary, and variability of the
observable horizon.
```

