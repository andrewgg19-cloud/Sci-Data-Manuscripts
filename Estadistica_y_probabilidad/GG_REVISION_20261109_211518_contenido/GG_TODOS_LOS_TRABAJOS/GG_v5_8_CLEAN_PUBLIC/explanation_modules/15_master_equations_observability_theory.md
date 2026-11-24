# Master Equations for the Observability Theory

Status: formal explanatory layer only. This file consolidates the mathematical
definition of German Gamma v5.8 without adding a new operational core module.

## 1. Observed System

Let:

```text
X_t in R^d
```

A datum is not only a point. It is a situated state:

```text
z_t = (t, X_t)
```

where:

```text
t   = temporal coordinate
X_t = state vector at time t
R^d = measured variable space
```

## 2. Observable Horizon

Let:

```text
Omega = total possible domain
H subset Omega = observable horizon
Gamma subset H = filter inside the horizon
```

Observable natural state:

```text
D_N^H = P(X | X in H)
```

Filtered observable state:

```text
D_F = P(X | X in H intersection Gamma)
```

Filter-induced deformation:

```text
Delta_HGamma = d(D_N^H, D_F)
```

## 3. Neutral Point

Mean neutral point:

```text
n_t = argmin_z E[ ||X_t - z||^2 ]
```

Robust neutral point:

```text
n_t = argmin_z E[ ||X_t - z|| ]
```

Radius from neutral point:

```text
r_t = X_t - n_t
```

## 4. Trajectory

Trajectory:

```text
gamma(t) = (t, X_t)
```

Discrete velocity:

```text
v_t = X_t - X_{t-1}
```

Discrete curvature:

```text
a_t = X_{t+1} - 2X_t + X_{t-1}
```

## 5. Cylinder of Possibilities

The cylinder describes open temporal unfolding:

```text
C = { (t,x) in T x R^d : ||x - n_t|| <= R_t }
```

Reading:

```text
height   = time
sheet    = distribution at t
center   = neutral point
radius   = possible range
boundary = observable horizon
```

## 6. Entropy Per Temporal Sheet

Continuous form:

```text
H_t = - integral p_t(x) log p_t(x) dx
```

Discrete form:

```text
H_t = - sum_i p_{t,i} log p_{t,i}
```

Entropy loss:

```text
Delta_H_t = H_t^natural - H_t^filtered
```

## 7. Operational Invariants

Let:

```text
K_i = structural reading or metric
T_j = declared transformation
epsilon = tolerance
```

Invariant candidate:

```text
Inv_i(X) iff d(K_i(X), K_i(T_j(X))) <= epsilon
```

Interpretation:

```text
what survives transformation is candidate structure.
```

## 8. Asymmetry by Transformation

Transformation family:

```text
G in { I, P, T, C, CP, CT, PT, CPT }
```

Asymmetry under transformation:

```text
A_G(X) = d(K(X), K(G(X)))
```

Asymmetry source decomposition:

```text
A_G = A_int^G + A_H^G + A_eta^G
```

where:

```text
A_int^G = intrinsic asymmetry
A_H^G   = horizon-induced asymmetry
A_eta^G = noise/sampling/measurement asymmetry
```

## 9. Transformed Equivalence

Transformed equivalence:

```text
X ~_G Y iff Y = G(X) and d(K(X), K(Y)) <= epsilon
```

Candidate transformed manifestation:

```text
exists G such that A_G(X) <= epsilon
```

Candidate structural rupture:

```text
for all G, A_G(X) > epsilon
```

Rule:

```text
different form does not imply broken structure.
```

## 10. Angular-Momentum-Like Trajectory

Radius from neutral point:

```text
r_t = X_t - n_t
```

Velocity:

```text
v_t = X_t - X_{t-1}
```

Angular-momentum-like trajectory vector:

```text
L_Gamma(t) = r_t x v_t
```

Torque-like change:

```text
tau_Gamma(t) = L_Gamma(t) - L_Gamma(t-1)
```

Interpretation:

```text
stable L_Gamma axis -> recurrent/orbital structure candidate
diffuse L_Gamma     -> stochastic rotation without stable axis
high tau_Gamma      -> transition or rotational rupture candidate
```

## 11. Hidden Residual

Base trajectory:

```text
gamma_0(z)
```

Observed trajectory:

```text
gamma_obs(z)
```

Residual:

```text
R(z) = gamma_obs(z) - gamma_0(z)
```

Persistence:

```text
P_R = integral |R(z)| dz
```

or discretely:

```text
P_R = sum_i |R(z_i)| Delta z_i
```

Anisotropy by direction:

```text
A_Omega(z) = Var_Omega[R(z, Omega)]
```

Scale instability:

```text
A_s(z) = Var_s[R_s(z)]
```

Hidden-component candidate index:

```text
H_c = P_R * 1/(1 + A_Omega) * 1/(1 + A_s) * 1/(1 + eta)
```

Interpretation:

```text
high H_c = persistent, stable, low-noise residual not explained by base model
```

Limit:

```text
hidden-component candidate does not prove the identity of the hidden cause.
```

## 12. German Gamma Spectrum

The consolidated spectrum is:

```text
Gamma(X) = {
  Delta_HGamma,
  Inv,
  H_t,
  R_t,
  C_H,
  gamma_t,
  eta_t,
  A_G,
  L_Gamma,
  R_hidden
}
```

where:

```text
Delta_HGamma = horizon/filter deformation
Inv          = operational invariants
H_t          = entropy per temporal sheet
R_t          = reversibility reading
C_H          = horizon-mirror non-commutativity
gamma_t      = space-time trajectory
eta_t        = noise as discernment scale
A_G          = asymmetry under transformation family
L_Gamma      = angular-momentum-like trajectory reading
R_hidden     = stable residual compatible with an unmodeled component
```

## Final Interpretation

```text
candidate structure = what persists under declared transformations
candidate induced dependence = what appears through horizon/filter
candidate hidden component = stable residual unexplained by the base model
```

German Gamma does not claim absolute reality. It organizes the observable
signature of conservation, deformation, transformation, trajectory, and residual
structure.

