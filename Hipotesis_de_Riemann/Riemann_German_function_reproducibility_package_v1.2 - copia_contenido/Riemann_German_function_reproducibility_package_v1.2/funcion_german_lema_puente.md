# Función Germán: lema puente primo-cero

## Verificado

La función Germán finita contiene ahora estos canales:

```tex
\mathfrak G(T;P)=
\left(
N_{\mathrm{strip}}(T)-N_{1/2}(T),
\Sigma_\pi(P),
\widehat{\Sigma}_\pi(P),
\psi(P),
A_P|_{\Gamma_T}
\right).
```

El componente de conteo es:

```tex
\mathfrak G(T)=
N_{\mathrm{strip}}(T)-N_{1/2}(T)=\# Z_{\mathrm{off}}(T).
```

All three quantities use the positive-ordinate convention `0<gamma<=T`.

El limite primo finito pedido es:

```tex
\Sigma_\pi(P)=\sum_{p\le P}p.
```

Para que ese canal no explote numericamente, se registra tambien:

```tex
\widehat{\Sigma}_\pi(P)=
\frac{\Sigma_\pi(P)}{1+\Sigma_\pi(P)}.
```

## Deduccion

Para un `T` finito, si se tiene un conteo independiente del total de ceros en la franja critica y ese conteo coincide con los ceros contados en la recta critica, entonces:

```tex
\mathfrak G(T)=0
\quad\Longleftrightarrow\quad
Z_{\mathrm{off}}(T)=\emptyset.
```

La hipotesis de Riemann equivale a exigir esa anulacion para todo `T` finito:

```tex
\forall T<\infty,\quad \mathfrak G(T)=0.
```

The total strip count is supplied externally. The script checks the equality
but does not authenticate the external source.

## Hipotesis propuesta

El lema puente que faltaria probar es:

```tex
\left(
\Sigma_\pi(P),
\widehat{\Sigma}_\pi(P),
\psi(P),
A_P|_{\Gamma_T}
\right)
\Longrightarrow
N_{\mathrm{strip}}(T)=N_{1/2}(T),
```

con una eleccion controlada de `P=P(T)` y un error uniforme cuando `T` crece.

## NV

No esta probado aqui que la suma de primos determine todos los ceros de zeta.
No esta probado aqui que el canal primo excluya pares espejo fuera de la recta.
No esta probado aqui un control uniforme simultaneo en `P` y `T`.
No esta probado aqui RH.

The bounded marker `Sigma_hat_pi(P)` tends to 1 as `P` grows and is therefore
only a finite numerical marker. The canonical proof route is the uniform
Chebyshev error bound measured finitely by

```tex
B_\epsilon(P)=\max_{2\le x\le P}
\frac{|\psi(x)-x|}{x^{1/2+\epsilon}}.
```

El script solo deja el protocolo reproducible: calcula los canales finitos, conserva el certificado de conteo separado, y marca el lema puente como no verificado.
