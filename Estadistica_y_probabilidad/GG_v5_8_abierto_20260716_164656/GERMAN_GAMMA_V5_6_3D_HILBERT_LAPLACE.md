# German Gamma v5.6 - 3D / Hilbert / Laplace Layer

## Objetivo

German Gamma v5.6 agrega una capa tridimensional y temporal al diagnostico de filtros.

No afirma que Fisher, Jensen-Shannon, entropia, Hilbert o Laplace sean nuevos.
La contribucion es operacional: integrarlos en una secuencia de auditoria para estudiar
como un filtro puede cambiar soporte, geometria, diversidad informacional y trayectoria.

## Comandos

```text
german_gamma_v5_6_3d_hilbert_laplace.py cubic_shadow
german_gamma_v5_6_3d_hilbert_laplace.py cubic_mirror
german_gamma_v5_6_3d_hilbert_laplace.py energy_entropy
german_gamma_v5_6_3d_hilbert_laplace.py laplace_temporal
```

## 1. Sombra cubica

La version 2D usa una tabla 2x2. La version 3D usa un cubo 2x2x2 con ocho celdas:

```text
000, 001, 010, 011, 100, 101, 110, 111
```

Para tasas de aceptacion:

```text
p_abc = n_abc / N_abc
```

El contraste cubico es:

```text
I_3 = (p000 * p011 * p101 * p110) /
      (p001 * p010 * p100 * p111)
```

Y la distancia:

```text
D_3 = |ln(I_3)|
```

Regla:

```text
Si falta soporte, D_3_raw no se calcula.
La version Laplace se reporta solo como auxiliar.
```

## 2. Espejo cubico

Opera sobre una nube 3D:

```text
X = (x1, x2, x3)
```

Compara dos rutas:

```text
M(Pi_H(X))
Pi_H(M(X))
```

La distancia se calcula con Jensen-Shannon sobre histogramas 3D.
La lectura debe calibrarse con permutaciones.

## 3. Energia residual y entropia

La capa Hilbert usa una representacion de caracteristicas:

```text
phi(X)
```

Por defecto:

```text
phi(x) = [x1, x2, x3, x1*x2, x1*x3, x2*x3, x1^2, x2^2, x3^2]
```

La energia residual compara centroides:

```text
E_res = ||mu_N - mu_F||^2
```

La entropia compara diversidad informacional:

```text
Delta_S = S_N - S_F
```

El acoplamiento nuevo del modelo es:

```text
R_EH = log(1 + E_res) * |Delta_S|
```

Lectura:

```text
E_res alto + |Delta_S| alto = desplazamiento geometrico con cambio informacional.
```

## 4. Laplace temporal

Para una serie temporal diagnostica:

```text
D(t)
```

se calcula una respuesta discreta:

```text
L(s) = sum_t exp(-s*t) D(t)
```

Esto resume persistencia temporal. No prueba causalidad.

## Regla de interpretacion

```text
Raw primero.
Regularizado separado.
No EPS escondido.
No fraude.
No causalidad.
No decision operativa sin calibracion externa.
```

