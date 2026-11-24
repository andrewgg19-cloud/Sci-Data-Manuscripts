# German Gamma - Set-Theoretic Foundation

## 1. Dominio, horizonte y filtro

Sea:

```text
Omega = conjunto total de estados posibles
H subset Omega = horizonte observable
Gamma subset H = filtro aplicado dentro del horizonte
F subset Gamma = conjunto finalmente analizado
```

En datos reales, `Omega` rara vez se observa completo. Por eso German Gamma no
afirma medir la realidad absoluta. Mide deformacion dentro del horizonte
observable declarado.

## 2. Operadores

Definimos dos operadores de restriccion:

```text
Pi_H: Omega -> H
Pi_Gamma: H -> Gamma
```

La secuencia operacional es:

```text
Omega -> H -> Gamma -> F
```

En palabras:

```text
dominio posible -> observable -> filtrado -> analizado
```

## 3. Medidas condicionales

Sea `P` una medida de probabilidad sobre `Omega`.

El estado natural observable es:

```text
D_N^H = P(X | X in H)
```

El estado filtrado observable es:

```text
D_F = P(X | X in H intersection Gamma)
```

La deformacion inducida por el filtro se mide como:

```text
Delta_HGamma = d( P(X | X in H), P(X | X in H intersection Gamma) )
```

donde `d` puede ser Jensen-Shannon, KL, Wasserstein, distancia de histogramas,
distancia topologica o una metrica definida para el dominio.

## 4. Perdida de soporte

Sea `supp(D)` el soporte de una distribucion.

Hay perdida de soporte si:

```text
supp(D_F) proper_subset supp(D_N^H)
```

Hay perdida de soporte expresado si existe una region observable `A subset H` tal
que:

```text
P(A | H) > 0
```

pero:

```text
P(A | H intersection Gamma) = 0
```

Interpretacion:

```text
Una region observable con masa positiva desaparece tras el filtro.
```

Regla operativa:

```text
Cuando hay perdida de soporte, el resultado raw no debe forzarse con EPS.
Debe reportarse como no evaluable o como perdida de soporte.
```

## 5. Dependencia inducida

Sean `X1` y `X2` variables definidas sobre `H`.

Si dentro del horizonte son independientes:

```text
P(X1, X2 | H) = P(X1 | H) P(X2 | H)
```

pero despues del filtro:

```text
P(X1, X2 | H intersection Gamma)
!=
P(X1 | H intersection Gamma) P(X2 | H intersection Gamma)
```

entonces German Gamma define:

```text
dependencia inducida por filtrado dentro del horizonte H.
```

Esto no implica fraude, intencion ni causalidad. Implica que la independencia
observable no se conserva bajo la restriccion `Gamma`.

## 6. Horizonte-espejo

Sea `M` una transformacion de espejo o simetria definida sobre el espacio de
representacion.

El coeficiente horizonte-espejo compara dos rutas:

```text
Ruta 1: M(Pi_H(X))
Ruta 2: Pi_H(M(X))
```

La diferencia operacional es:

```text
C_H(X) = d( M(Pi_H(X)), Pi_H(M(X)) )
```

Interpretacion:

```text
Si C_H es alto bajo calibracion nula, el horizonte no conserva simetria respecto
al espejo definido.
```

## 7. Lamina temporal

Sea una ventana temporal:

```text
T_i subset H
```

Cada lamina temporal se analiza como subconjunto local congelado:

```text
T_i = X[t_i, t_i + Delta t]
```

Dentro de esa lamina:

```text
T_i^Gamma = T_i intersection Gamma
```

El indice de energia de lamina temporal es:

```text
A_T(i) = C_T(i) * log(1 + E_res(i)) * |Delta_S(i)| * [-log(P_i)]
```

donde:

```text
C_T(i)   = asimetria espejo-temporal
E_res(i) = energia residual entre T_i y T_i^Gamma
Delta_S  = cambio de entropia
P_i      = probabilidad empirica bajo nulo/permutacion
```

## 8. Proposicion operacional

**Proposicion.**

Si un filtro `Gamma` es informativo respecto a variables de `H`, entonces puede
modificar la medida condicional sobre `H` y producir:

```text
1. perdida de soporte;
2. cambio de tasas locales;
3. dependencia inducida;
4. ruptura de simetria horizonte-espejo;
5. desplazamiento energia-entropia;
6. laminas temporales raras bajo un modelo nulo.
```

**Lectura.**

German Gamma no afirma que estas senales prueben fraude o intencion. Afirma que
son condiciones matematicamente auditables bajo las cuales un filtro deja de ser
neutral respecto al horizonte observable declarado.

## 9. Frase central

```text
German Gamma es una teoria operacional de subconjuntos observables:
define el horizonte H dentro del dominio Omega, define el filtro Gamma dentro de
H, y mide como cambia la medida de probabilidad al condicionar sobre
H intersection Gamma.
```

