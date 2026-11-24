# 09 - Hierarchical Judge

Purpose: define how German Gamma should connect grammar, truth checking,
association, comparison, jury integration, and final bounded determination.

This is a governance layer. It is not a new statistical metric.

## Roles

```text
G  = grammar reviewer
V1 = primary truth checker
A  = association generator
V2 = comparative truth checker
J  = jury/integration layer
D  = judge/determination layer
```

## Flow

```text
input
 -> G
 -> V1
 -> A
 -> V2
 -> J
 -> D
```

## Parallel Processing

Modules may process in parallel:

```text
G  grammar
V1 primary truth checking
A  association generation
V2 comparative truth checking
S  signal/noise labeling
T  transition reading
R  reversibility reading
```

Parallelism accelerates recognition. It does not authorize conclusion.

```text
parallel for processing
hierarchical for determination
```

## Function

```text
G:
checks clarity, ambiguity, grammar, and internal readability.

V1:
checks whether facts, data, files, and sources exist.

A:
generates possible associations, analogies, patterns, or hypotheses.

V2:
checks whether the associations are justified or are unsupported jumps.

J:
integrates agreement, contradiction, missing evidence, and uncertainty.

D:
determines the maximum admissible level of claim.
```

## Determination Levels

```text
confirmed_with_evidence
bounded_interpretation
exploratory_hypothesis
analogy_only
not_supported
discarded
```

## Rule

```text
The association layer cannot publish a conclusion.
The judge cannot exceed the evidence.
```

## Anti-Confabulation Rule

The system may fill structure, but it must not fill truth.

Confabulation means:

```text
filling missing evidence as fact;
turning analogy into evidence;
turning hypothesis into conclusion;
using noise as proof;
hiding uncertainty;
skipping hierarchy levels.
```

Every released item must carry an epistemic label:

```text
data
calculation
source
hypothesis
analogy
contextual_noise
not_verified
not_evaluable
empty_gap
```

Blocking rules:

```text
if evidence is missing -> mark empty_gap
if it is inferred -> mark hypothesis
if it is comparative -> mark analogy
if it is noisy -> mark contextual_noise
if it is verified -> mark source/data/calculation
```

No item marked as `hypothesis`, `analogy`, `contextual_noise`,
`not_verified`, `not_evaluable`, or `empty_gap` can be promoted to
`confirmed_with_evidence`.

## NAND Gates

NAND is used as a blocking logic:

```text
NAND(a, b) = NOT(a AND b)
```

In the governance layer:

```text
NAND(hypothesis, confirmed)
NAND(analogy, evidence)
NAND(contextual_noise, proof)
NAND(not_verified, conclusion)
NAND(not_evaluable, verdict)
```

Equivalent confirmation rule:

```text
confirmed_with_evidence =
verified
AND NOT(hypothesis)
AND NOT(analogy)
AND NOT(contextual_noise)
AND NOT(not_verified)
AND NOT(not_evaluable)
AND NOT(empty_gap)
```

NAND is the minimum anti-confabulation gate: it blocks any attempt to turn an
unverified or non-evaluable signal into confirmed evidence.

## Safe Learning

The system may learn reliability of routes and modules. It must not learn truth
without verification.

Each route or module has a weight:

```text
w_m(t)
```

Feedback updates confidence:

```text
w_m(t+1) = w_m(t) + eta * feedback_m
```

Rules:

```text
verified route -> weight increases
blocked route -> weight decreases
confabulated route -> weight decreases strongly
useful exploratory route -> weight increases slightly, without becoming truth
```

The system learns:

```text
module reliability
route reliability
common false positives
normal transitions
noise behavior
association failure modes
```

The system does not learn automatically:

```text
truth
intent
fraud
causality
consciousness
```

## Core Sentence

```text
Creativity runs in parallel with verification, but final interpretation is
hierarchical: grammar clarifies, veracity checks, association opens
possibilities, comparison closes false jumps, the jury integrates, and the judge
sets the admissible claim.
```

```text
If the system does not know, it marks the gap; it does not invent the bridge.
```

```text
Parallelism accelerates recognition; NAND blocks confabulation; hierarchy
controls determination; learning adjusts route confidence, not truth.
```
