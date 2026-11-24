# Local Oscillation and Noise Discernment

Status: validation/explanation utility, not a German Gamma core module.

## Principle

```text
Noise is not erased.
Noise is used as the scale of discernment.
```

## Local Triad

For each temporal point:

```text
x_{t-1}, x_t, x_{t+1}
```

the utility computes:

```text
local_mean
oscillation = ||x_t - local_mean||
curvature   = ||x_{t+1} - 2x_t + x_{t-1}||
noise_scale = local residual noise around x_t
```

Then:

```text
oscillation_noise_ratio = robust local excess of oscillation over neighboring triads
curvature_noise_ratio   = robust local excess of curvature over neighboring triads
```

## Reading

```text
high oscillation with high noise:
may be ordinary fluctuation.

high oscillation with low noise:
more meaningful local structure.

high curvature relative to noise:
possible local transition or inflection.
```

## Boundary

This does not prove causality, intent, fraud, or validity.

It asks whether a local oscillation is large relative to the noise around it.

## Calibration Note

The discriminator compares each triad against neighboring triads. This avoids
flagging nearly every point in naturally noisy sequences.
