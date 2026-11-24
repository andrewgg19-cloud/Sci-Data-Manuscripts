# Falsification Result Summary

Status:

```text
passed under declared controls
```

## Results

| Case | Expected | Observed | Verdict |
|---|---|---|---|
| `01_positive_orbit` | `stable_rotational_structure_candidate` | `stable_rotational_structure_candidate` | pass |
| `02_negative_radial` | not stable orbit | `low_rotation_or_radial_motion` | pass |
| `03_noise_random_walk` | not stable orbit | `low_rotation_or_radial_motion` | pass |

## Observed Metrics

Positive orbit:

```text
rotation_coherence = 0.999783
torque_ratio       = 0.065995
reading            = stable_rotational_structure_candidate
```

Negative radial:

```text
mean_L_norm        = 0.000000
rotation_coherence = 0.000000
reading            = low_rotation_or_radial_motion
```

Noise random walk:

```text
rotation_coherence = 0.084587
torque_ratio       = 1.330199
reading            = low_rotation_or_radial_motion
```

## Interpretation

The angular trajectory utility did not confuse radial motion or random-walk
noise with a stable orbital trajectory.

This supports the limited claim:

```text
the utility separates positive orbital control from declared negative controls.
```

It does not validate the entire German Gamma model.

