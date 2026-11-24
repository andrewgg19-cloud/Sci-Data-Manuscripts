# Función Germán: intento auditado de demostracion del lema puente

## Objetivo

Queremos cerrar el paso:

```tex
\left(
\Sigma_\pi(P),
\widehat{\Sigma}_\pi(P),
\psi(P),
A_P|_{\Gamma_T}
\right)
\Longrightarrow
N_{\mathrm{strip}}(T)=N_{1/2}(T)
```

para todo `T` finito, con una eleccion controlada de `P=P(T)`.

## Definiciones

El conjunto de ceros fuera de la recta critica hasta altura `T` es:

```tex
Z_{\mathrm{off}}(T)=
\{\rho=\beta+i\gamma:
\zeta(\rho)=0,\ 0<\beta<1,\ \beta\ne 1/2,\ 0<\gamma\le T\}.
```

All zero counts below use positive ordinates only.

La función Germán de conteo es:

```tex
\mathfrak G(T)=
N_{\mathrm{strip}}(T)-N_{1/2}(T)
=\# Z_{\mathrm{off}}(T).
```

La version primo-limitada es:

```tex
\mathfrak G(T;P)=
\left(
\mathfrak G(T),
\Sigma_\pi(P),
\widehat{\Sigma}_\pi(P),
\psi(P),
A_P|_{\Gamma_T}
\right),
```

donde

```tex
\Sigma_\pi(P)=\sum_{p\le P}p,
\qquad
\widehat{\Sigma}_\pi(P)=
\frac{\Sigma_\pi(P)}{1+\Sigma_\pi(P)},
```

```tex
\psi(P)=
\sum_{p^m\le P}\log p
=\sum_{n\le P}\Lambda(n),
```

y

```tex
A_P(t)=
\sum_{p^m\le P}
\frac{\log p}{\sqrt{p^m}}
\cos(t\,m\log p).
```

## Teorema conocido usado como puente academico

DLMF 25.16 da la formula explicita:

```tex
\psi(x)=x-\frac{\zeta'(0)}{\zeta(0)}
-\sum_\rho \frac{x^\rho}{\rho}+o(1),
\qquad x\to\infty,
```

donde la suma corre sobre los ceros no triviales de zeta.

Tambien registra la equivalencia:

```tex
\mathrm{RH}
\Longleftrightarrow
\psi(x)=x+O(x^{1/2+\epsilon})
\quad\text{para todo }\epsilon>0.
```

Por tanto, una forma academica del lema puente no debe intentar deducir RH desde la suma cruda de primos sola. Debe probar que los canales de la función Germán controlan el error de Chebyshev:

```tex
E_\psi(x)=\psi(x)-x.
```

## Proposicion condicional

**Proposicion.** Supongamos que existe una regla efectiva `P=P(x)` y constantes `C_epsilon` tales que, para todo `x>=x0` y todo `epsilon>0`, los canales primo-limitados de la función Germán satisfacen:

```tex
|\psi(x)-x|
\le C_\epsilon x^{1/2+\epsilon}.
```

Entonces RH es verdadera.

**Demostracion.** Por la equivalencia citada en DLMF 25.16, la cota

```tex
\psi(x)=x+O(x^{1/2+\epsilon})
```

para todo `epsilon>0` es equivalente a RH. La hipotesis de la proposicion da exactamente esa cota. Luego todos los ceros no triviales satisfacen

```tex
\Re(\rho)=1/2.
```

Por tanto, para todo `T<infty`,

```tex
Z_{\mathrm{off}}(T)=\emptyset
\quad\text{y}\quad
\mathfrak G(T)=0.
```

Fin de la demostracion condicional.

## Donde esta el hueco real

El paso todavia no demostrado es:

```tex
\left(
\Sigma_\pi(P),
\widehat{\Sigma}_\pi(P),
\psi(P),
A_P|_{\Gamma_T}
\right)
\Longrightarrow
|\psi(x)-x|\le C_\epsilon x^{1/2+\epsilon}
```

uniformemente en `x`, con `P=P(x)` controlado.

Ese es el corazon del problema. Sin esa desigualdad uniforme, el canal primo es un detector finito reproducible, pero no una prueba global.

El diagnostico computable de altura prima finita es

```tex
B_\epsilon(P)=\max_{2\le x\le P,\ x\in\mathbb Z}
\frac{|\psi(x)-x|}{x^{1/2+\epsilon}}.
```

Todo valor finito de `B_epsilon(P)` es solamente diagnostico. La obligacion
demostrativa es una cota independiente de `P`, para cada `epsilon>0`.

## Verificado

- El script calcula `Sigma_pi(P)`, `Sigma_hat_pi(P)`, `psi(P)` y `A_P`.
- Para la corrida de ejemplo `T=50`, `P=100`, se obtuvo `G_German(T)=0` con conteo externo.
- La salida conserva `global_RH_proved=false`.

## Deduccion

Si se prueba la cota uniforme sobre `psi(x)-x`, entonces RH sigue por una equivalencia conocida.

Si RH sigue, entonces:

```tex
\forall T<\infty,\quad
\mathfrak G(T)=0.
```

## NV

No se ha probado que `Sigma_pi(P)` determine la distribucion completa de ceros.
No se ha probado que `A_P` excluya pares espejo fuera de la recta critica.
No se ha probado la cota uniforme `O(x^{1/2+epsilon})`.
No se ha probado RH.

## Dictamen

La función Germán ya esta en una forma matematicamente util: separa el certificado finito de conteo, el canal primo-limitado, el espejo adjunto, el marcador tipo Mobius y la seleccion Monte Carlo.

El siguiente avance real debe concentrarse en una sola desigualdad:

```tex
|\psi(x)-x|
\le C_\epsilon x^{1/2+\epsilon}.
```

Si esa desigualdad sale de la función Germán sin circularidad, el puente queda cerrado. Mientras no salga, el estado correcto es:

```text
candidate_framework = true
finite_audit_reproducible = true
global_RH_proved = false
```

## Fuentes

- DLMF 25.16: https://dlmf.nist.gov/25.16
- DLMF 25.10: https://dlmf.nist.gov/25.10
- Clay Mathematics Institute, Riemann Hypothesis: https://www.claymath.org/millennium/Riemann-Hypothesis/
- Titchmarsh and Heath-Brown, The Theory of the Riemann Zeta-function, 2nd ed., Oxford/Clarendon, 1986.
