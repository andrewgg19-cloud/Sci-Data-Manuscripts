# Validation Twins

Validation twins are paired datasets used to test German Gamma without adding
new theory.

Purpose:

```text
detect signal when a controlled deformation exists;
avoid signal when only random variation exists;
separate support loss from finite scores;
check temporal and reversibility behavior.
test whether a trajectory shows stable rotation around a neutral point.
```

These files are controls, not evidence about an external domain.

## Twin Sets

```text
01_null_twin
02_filtered_twin
03_temporal_twin
04_entropy_twin
05_reversibility_twin
```

Additional validation utilities:

```text
local_oscillation_noise_discriminator.py
vector_quantization_sequence_demo.py
angular_momentum_trajectory_test.py
```

Each set contains:

```text
base_A.csv
base_B.csv
expected_result.md
```

## Rule

Twins validate behavior of the tool. They do not validate scientific claims by
themselves.
