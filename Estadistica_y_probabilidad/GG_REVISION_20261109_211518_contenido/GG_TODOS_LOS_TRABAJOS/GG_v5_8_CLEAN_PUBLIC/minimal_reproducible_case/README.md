# German Gamma v5.8 - Minimal Reproducible Case

Status: executable quality-control example.

This case demonstrates one conservative reading:

```text
stable rotational structure candidate
```

It does not prove physical angular momentum, causality, intent, or a domain
claim. It only verifies that the validation utility can distinguish a coherent
orbital trajectory from diffuse stochastic rotation.

## Files

```text
generate_minimal_case.py
run_minimal_case.ps1
EXPECTED_READING.md
```

Generated after execution:

```text
minimal_orbit_input.csv
minimal_orbit_result.json
minimal_orbit_points.csv
```

## Run

From the repository root:

```powershell
.\minimal_reproducible_case\run_minimal_case.ps1
```

Manual equivalent:

```powershell
py -3 minimal_reproducible_case\generate_minimal_case.py
py -3 validation_twins\angular_momentum_trajectory_test.py --input minimal_reproducible_case\minimal_orbit_input.csv --columns x1,x2,x3 --json-out minimal_reproducible_case\minimal_orbit_result.json --csv-out minimal_reproducible_case\minimal_orbit_points.csv --center-radius 20
```

## Expected Reading

```text
stable_rotational_structure_candidate
```

Conservative interpretation:

```text
The trajectory has a coherent rotational axis around a rolling neutral point.
This is a signature, not a verdict.
```

