# German Gamma v5.8 - Symbolic Identities

Status: quality-control glossary for symbolic identities.

Rule:

```text
symbol without definition = metaphor
symbol with operation     = tool
symbol with test          = scientific component candidate
```

An identity is allowed only if its meaning, operation, limits, and status are
declared.

## Identity Table

| Symbolic identity | Definition | Equation / Operation | Allowed reading | Forbidden reading | Status |
|---|---|---|---|---|---|
| German Gamma `Gamma(X)` | Multicomponent observability spectrum. | `Gamma(X) = {Delta_HGamma, Inv, H_t, R_t, C_H, gamma_t, eta_t, A_G, L_Gamma, R_hidden}` | Diagnostic signature of conservation/deformation. | Theory of everything or absolute reality. | explanatory/formal |
| Horizon `H` | Observable subset of the possible domain. | `H subset Omega` | Declared boundary of observability. | Moral judgment or proof of manipulation. | operative |
| Filter `Gamma` | Selection rule inside horizon. | `Gamma subset H` | Declared selection mechanism. | Cause or intent by itself. | operative |
| Observable natural state `D_N^H` | Distribution conditioned on horizon. | `P(X | X in H)` | Baseline inside what can be observed. | Total natural reality. | operative |
| Filtered state `D_F` | Distribution after horizon and filter. | `P(X | X in H intersection Gamma)` | Analyzed observable state. | Complete system state. | operative |
| Induced deformation `Delta_HGamma` | Distance between observable baseline and filtered state. | `d(D_N^H, D_F)` | Filter-compatible deformation. | Fraud, intent, causality. | operative |
| Punto neutro `n_t` | Center or robust center of a temporal sheet. | `argmin_z E[||X_t-z||]` or `argmin_z E[||X_t-z||^2]` | Local reference point. | Absolute center of reality. | operative/explanatory |
| Lamina temporal `L_t` | Distributional sheet at time `t`. | State slice over `T x R^d`. | Temporal context of observations. | Independent universe or physical sheet. | explanatory |
| Cylinder Gamma | Open temporal unfolding of possibilities. | `{(t,x): ||x-n_t|| <= R_t}` | Space-time representation of trajectories. | Literal cosmological cylinder. | explanatory |
| Torus Gamma | Recurrent/cyclic representation. | `T^2 = S^1 x S^1` | Feedback, return, recurrence. | Replacement for all temporal models. | explanatory |
| Spectrum | Multidimensional signature. | Output family of `Gamma(X)`. | Pattern of observable signatures. | Direct view of hidden cause. | explanatory |
| Sombra cubica | 3D interaction imbalance in binary cube. | `D_3 = |ln(I_3)|` | Interaction diagnostic. | New physics or proof of manipulation. | operative |
| Espejo | Declared symmetry/reflection transform. | `M(X)` or `P(X)` | Test of orientation dependence. | Proof of bias by itself. | operative/explanatory |
| Noether operativo | Invariant-style conservation test. | `d(K_i(X), K_i(T_j(X))) <= epsilon` | Candidate preserved structure. | Physical Noether theorem proven on data. | explanatory/formal |
| Asymmetry source | Decomposition of measured asymmetry. | `A_G = A_int^G + A_H^G + A_eta^G` | Separates intrinsic, horizon, and noise components. | Exact causal decomposition without evidence. | explanatory/formal |
| Transformed equivalence | Same structure under declared transform. | `X ~_G Y iff Y=G(X) and d(K(X),K(Y)) <= epsilon` | Different form can preserve structure. | Physical antimatter/CPT proof unless domain-valid. | explanatory/formal |
| Operational symmetry group `Sym(X)` | Set of transformations preserving structural signature `K(X)`. | `Sym(X)={G: d(K(X),K(G(X)))<=epsilon}` | Measurable symmetry family under declared transforms. | Universal physical symmetry group. | validation/formal |
| Local noise scale `eta_t` | Robust local reference for discernment. | Neighborhood MAD/scale around local triads. | Noise as comparison scale. | Noise erased or ignored. | validation |
| Angular trajectory `L_Gamma` | Rotation-like path around neutral point. | `L_Gamma(t)=r_t x v_t` | Stable/diffuse/radial trajectory reading. | Physical angular momentum unless variables are physical. | validation |
| Torque-like change `tau_Gamma` | Change in angular trajectory vector. | `L_Gamma(t)-L_Gamma(t-1)` | Transition/rupture candidate in trajectory. | External force proven. | validation |
| Hidden residual `R_hidden` | Stable residual unexplained by base model. | `R(z)=gamma_obs(z)-gamma_0(z)` | Candidate unmodeled component. | Hidden cause identified absolutely. | explanatory/formal |
| Ethos | Responsible collective knowledge note. | Review, replicate, correct, reuse responsibly. | Project intent and conduct. | Scientific result. | ethical/documentary |

## Status Definitions

```text
operative:
implemented in executable core scripts.

validation:
implemented in validation utilities, not core.

explanatory:
organizes interpretation but does not compute by itself.

formal:
mathematically defined but not necessarily implemented as full estimator.

ethical/documentary:
states project conduct or intent.
```

## Admission Rule

A new symbolic identity must provide:

```text
name
definition
equation or operation
allowed reading
forbidden reading
status
```

If not, it stays outside the model.
