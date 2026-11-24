# German Gamma v5.8 - Falsification Tests

Status: falsification suite for the angular-momentum-like trajectory utility.

These tests ask whether the module can fail correctly.

## Falsification Rule

```text
positive orbit -> stable_rotational_structure_candidate
radial control -> low_rotation_or_radial_motion
noise control  -> diffuse_stochastic_rotation_no_stable_axis
```

The module fails if:

```text
radial control -> stable_rotational_structure_candidate
noise control  -> stable_rotational_structure_candidate repeatedly
positive orbit -> not stable_rotational_structure_candidate
```

Acceptable noise-control outcomes:

```text
diffuse_stochastic_rotation_no_stable_axis
low_rotation_or_radial_motion
```

The critical failure is:

```text
noise control -> stable_rotational_structure_candidate
```

## Run

From the repository root:

```powershell
py -3 falsification_tests\generate_falsification_cases.py
py -3 validation_twins\angular_momentum_trajectory_test.py --input falsification_tests\01_positive_orbit.csv --columns x1,x2,x3 --json-out falsification_tests\01_positive_orbit_result.json --csv-out falsification_tests\01_positive_orbit_points.csv
py -3 validation_twins\angular_momentum_trajectory_test.py --input falsification_tests\02_negative_radial.csv --columns x1,x2,x3 --json-out falsification_tests\02_negative_radial_result.json --csv-out falsification_tests\02_negative_radial_points.csv
py -3 validation_twins\angular_momentum_trajectory_test.py --input falsification_tests\03_noise_random_walk.csv --columns x1,x2,x3 --json-out falsification_tests\03_noise_random_walk_result.json --csv-out falsification_tests\03_noise_random_walk_points.csv
```

## Boundary

Passing this suite does not validate the entire German Gamma model. It validates
one specific behavior:

```text
the angular trajectory utility separates orbit, radial motion, and diffuse noise
under declared controls.
```
