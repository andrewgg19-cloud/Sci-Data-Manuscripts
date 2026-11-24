# Invariants, Spectrum, and Physical Analogies

Status: explanatory layer only. This module does not add a new operational
metric to the frozen German Gamma v5.8 core.

## Central Rule

```text
German Gamma does not analyze only the observed point.
It analyzes the relation between point, cloud, center, horizon, trajectory,
noise, symmetry, and conserved structure.
```

The model asks:

```text
Does the observed point belong naturally to its possibility cloud,
or was it displaced by the horizon of observation?
```

## Space-Time Data Point

A datum is represented as:

```text
(t, x_t) in T x R^d
```

where:

```text
t   = temporal coordinate
x_t = observed state at time t
R^d = measured variable space
```

The neutral point of a temporal sheet is:

```text
N_t = (t, n_t)
```

with:

```text
n_t = center or robust center of the temporal sheet L_t
```

The relevant distance is therefore not only spatial:

```text
||x_t - n_t||
```

but can also be space-temporal:

```text
d_ST((t,x_t),(s,x_s)) =
sqrt(lambda_t |t-s|^2 + ||x_t - x_s||^2)
```

## Cylinder Gamma

The cylinder is for open temporal unfolding:

```text
C = { (t,x) in T x R^d : ||x - n_t|| <= R_t }
```

Reading:

```text
height   = time
sheet    = distribution at t
center   = neutral point n_t
radius   = range of possibilities
boundary = observable horizon
path     = trajectory of the datum
```

The cylinder answers:

```text
How does the system unfold through temporal sheets?
```

## Torus Gamma

The torus is separate from the cylinder. It is for recurrent systems:

```text
T^2 = S^1 x S^1
```

It answers:

```text
How does the system return to itself after feedback?
```

A recurrent trajectory satisfies:

```text
X_{t+k} approx X_t
```

Return deformation is:

```text
D_return = d(X_{t+k}, X_t)
```

Reading:

```text
small D_return = stable cycle
large D_return = drift, degradation, or transformed return
```

## Wavefunction Analogy

In quantum mechanics, a wavefunction:

```text
psi(x,t)
```

defines a probability density:

```text
P(x,t) = |psi(x,t)|^2
```

German Gamma does not claim to be quantum mechanics. The analogy is restricted:

```text
wavefunction       -> field of possibilities
|psi|^2            -> observable probability density
measurement        -> selected observed point
horizon/filter     -> restriction of what can be observed
```

The useful lesson is:

```text
An observed point is not the whole system.
It is a realized position inside a structured cloud of possibilities.
```

## Spectrum Analogy

Helium was first inferred from a spectral line before being isolated on Earth.
The general diagnostic lesson is:

```text
unknown structure can be inferred from a reliable observable signature.
```

German Gamma uses this only as an analogy:

```text
data                -> observable emission
Gamma(X) spectrum   -> multidimensional diagnostic signature
horizon             -> what permits or blocks observability
```

The spectrum does not prove intent or cause. It reports signatures:

```text
support loss
entropy change
symmetry rupture
trajectory deformation
noise-relative oscillation
reversibility asymmetry
```

## Noether-Style Operational Invariants

Noether's theorem in physics states:

```text
continuous symmetry -> conserved quantity
```

German Gamma does not claim to prove physical conservation laws. It uses an
operational analogue:

```text
symmetry preserved under transformation -> candidate invariant
symmetry broken by horizon/filter        -> candidate induced deformation
```

Let:

```text
K_i = structural reading or metric
T_j = declared transformation
epsilon = tolerance
```

Then:

```text
K_i is operationally invariant if
d(K_i(X), K_i(T_j(X))) <= epsilon
```

If:

```text
d(K_i(X), K_i(Pi_H(X))) > epsilon
```

then the horizon changed the reading.

Rule:

```text
What survives transformation is candidate structure.
What appears only after selection is candidate induced dependence.
```

## Carbon, Graphite, and Diamond

Carbon shows why isolated components are not enough.

```text
same element != same structure != same observable properties
```

Diamond:

```text
carbon network: sp3
geometry: tetrahedral
topology: rigid 3D network
property: hard, transparent, electrical insulator
```

Graphite:

```text
carbon network: sp2
geometry: planar hexagonal sheets
topology: layered 2D structure
property: soft, dark, electrically conductive in-plane
```

German Gamma translation:

```text
same nodes + different links -> different structural spectrum
```

Therefore:

```text
The observable reality of a system depends not only on what elements exist,
but on how they are connected.
```

## Integrated Model Reading

The explanatory synthesis is:

```text
Gamma(X) =
  point
  + possibility cloud
  + neutral center
  + observable horizon
  + temporal trajectory
  + noise scale
  + mirror symmetry
  + reversibility
  + operational invariants
```

Primary interpretation:

```text
German Gamma measures the tension between conserved structure and
horizon-induced deformation.
```

Valid outputs:

```text
compatible with preserved structure
compatible with induced deformation
compatible with recurrent drift
compatible with local oscillation above noise
not evaluable under the declared horizon
```

Invalid outputs:

```text
fraud proven
intent proven
consciousness proven
physical law discovered
absolute reality measured
```

