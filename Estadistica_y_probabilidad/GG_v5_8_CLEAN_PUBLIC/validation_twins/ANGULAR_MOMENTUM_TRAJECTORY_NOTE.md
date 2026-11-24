# Angular Momentum Trajectory Test

Status: validation/explanation utility, not a German Gamma core module.

## Principle

The test asks whether a temporal trajectory rotates around a rolling neutral
point.

```text
r_t = x_t - n_t
v_t = x_t - x_{t-1}
L_t = r_t x v_t
tau_t = L_t - L_{t-1}
```

where:

```text
n_t   = rolling neutral point
r_t   = radius from neutral point
v_t   = local velocity
L_t   = angular-momentum-like trajectory vector
tau_t = torque-like change in rotation
```

## Reading

```text
stable_rotational_structure_candidate:
the trajectory has a coherent rotational axis and low torque ratio.

diffuse_stochastic_rotation_no_stable_axis:
angular changes exist, but they do not align around a stable axis.

low_rotation_or_radial_motion:
the path is mostly radial, linear, or too weakly rotational.

rotational_break_or_transition_candidate:
a coherent rotating trajectory shows high torque or abrupt change.
```

## Validation Result

The first raw classifier over-alerted random controls. It was corrected by
separating angular magnitude from rotational coherence.

Observed behavior after correction:

```text
null twin:
diffuse_stochastic_rotation_no_stable_axis

temporal twin:
diffuse_stochastic_rotation_no_stable_axis

reversibility twin:
low_rotation_or_radial_motion

synthetic orbital control:
stable_rotational_structure_candidate
```

## Boundary

This is not physical angular momentum. It is a trajectory diagnostic inspired
by angular momentum:

```text
rotation around a neutral point,
axis coherence,
and torque-like transition.
```

It does not prove causality, intent, fraud, or physical conservation.

