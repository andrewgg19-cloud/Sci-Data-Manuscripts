# German Gamma v5.8 - Master Interpretation Table

Status: quality-control document. This table defines how to read German Gamma
outputs conservatively.

German Gamma is diagnostic. It does not prove intent, fraud, causality, or
absolute reality.

## Interpretation Rule

```text
An output is a signature, not a verdict.
```

Every reading must answer:

```text
what it indicates
what it does not indicate
what evidence is needed
which module produced it
```

## Master Table

| Signature | Indicates | Does Not Indicate | Evidence Needed | Source |
|---|---|---|---|---|
| `Delta_HGamma high` | Observable distribution changes after horizon/filter. | Fraud, intent, invalidity, or true cause. | Declared horizon, pre/post distributions, distance metric, support check. | `german_gamma_v5_5_2_audit_grade.py`, `german_gamma_v5_6_3d_hilbert_laplace.py` |
| Support loss | Some regions/cells are no longer evaluable after filtering. | A finite corrected effect. | Raw counts, zero cells/regions, no EPS-forced primary result. | `german_gamma_v5_5_2_audit_grade.py` |
| Cubic shadow `D_3` high | 3D interaction imbalance across declared binary dimensions. | New physics, causality, or proof of manipulation. | Counts per cube cell, raw support, bootstrap/auxiliary interval if used. | `german_gamma_v5_6_3d_hilbert_laplace.py` |
| Mirror non-commutativity `C_H` high | Horizon/filter is orientation-sensitive under declared mirror. | Bias by itself, unless intrinsic asymmetry/noise/support are excluded. | Compare before/after mirror, resampling, support check. | `german_gamma_v5_6_3d_hilbert_laplace.py`, explanation modules 13-14 |
| Energy-entropy residual high | Shift in center plus entropy change after filtering. | Hidden cause proven. | Pre/post means, entropy calculation, uncertainty/noise estimate. | `german_gamma_v5_6_3d_hilbert_laplace.py` |
| Temporal sheet anomaly | A time window behaves unusually relative to permutation/null baseline. | Permanent system change or intent. | Window definition, null/permutation baseline, repeated runs. | `german_gamma_v5_7_temporal_sheet.py` |
| Reversibility asymmetry | Forward and reverse trajectories do not behave equivalently. | Time arrow proven physically. | Same data read forward/reverse, transition/entropy comparison. | `german_gamma_v5_8_reversibility.py` |
| Local oscillation above noise | A point/triad exceeds neighboring local noise behavior. | Causality or domain anomaly. | Local triad, robust neighborhood scale, threshold declaration. | `validation_twins/local_oscillation_noise_discriminator.py` |
| Diffuse stochastic rotation | Angular changes exist but without stable axis. | Stable orbit or recurrent structure. | Low coherence of mean angular vector relative to angular magnitude. | `validation_twins/angular_momentum_trajectory_test.py` |
| Stable rotational structure candidate | Trajectory rotates coherently around rolling neutral point. | Physical angular momentum or causal mechanism. | Axis coherence, low torque ratio, reproducibility under controls. | `validation_twins/angular_momentum_trajectory_test.py` |
| Rotational break/transition candidate | Coherent rotation shows abrupt torque-like change. | External force proven. | Coherent axis plus high torque ratio, temporal localization, controls. | `validation_twins/angular_momentum_trajectory_test.py` |
| Operational invariant preserved | Structural reading survives declared transformation. | Universal law. | Transformation declared, metric stable within tolerance. | `explanation_modules/12_invariants_spectrum_physical_analogies.md` |
| Asymmetry before horizon | Possible intrinsic asymmetry. | Filter-induced asymmetry by itself. | Compare raw/pre-horizon state, mirror/transform family, noise check. | `explanation_modules/13_asymmetry_source_decomposition.md` |
| Asymmetry only after horizon | Candidate horizon-induced asymmetry. | Fraud or intent. | Pre/post comparison, stable under resampling, support preserved. | `explanation_modules/13_asymmetry_source_decomposition.md` |
| Transformed equivalence candidate | Apparent difference is conserved under another declared transformation. | Identity of raw appearance. | Existence of `G` such that `A_G <= epsilon`. | `explanation_modules/14_transformed_equivalence_manifestation.md` |
| Structural rupture candidate | No declared transformation preserves the structural reading. | Cause of rupture. | Test full transformation family, rule out support/noise limits. | `explanation_modules/14_transformed_equivalence_manifestation.md` |
| Hidden residual candidate | Stable residual not explained by base model. | Identity of hidden cause. | Persistence, isotropy/directional test, scale stability, noise estimate. | `explanation_modules/15_master_equations_observability_theory.md` |

## Conservative Decision Ladder

```text
1. Is support preserved?
2. Is the metric raw or auxiliary/regularized?
3. Does the signature survive resampling/noise checks?
4. Was asymmetry present before the horizon?
5. Does another transformation preserve the structure?
6. Is the result stable across time/scale/direction?
7. Only then assign a bounded interpretation.
```

## Allowed Conclusions

```text
compatible with preserved structure
compatible with induced deformation
compatible with horizon-sensitive asymmetry
compatible with intrinsic asymmetry
compatible with transformed equivalence
compatible with local oscillation above noise
compatible with recurrent/orbital trajectory
compatible with hidden residual candidate
not evaluable because support is lost
```

## Forbidden Conclusions

```text
fraud proven
intent proven
causality proven
experiment invalidated
physical law discovered
hidden entity identified absolutely
consciousness proven
absolute reality measured
```

## Final Rule

```text
German Gamma reports disciplined signatures.
Humans must provide domain evidence before turning a signature into a claim.
```

