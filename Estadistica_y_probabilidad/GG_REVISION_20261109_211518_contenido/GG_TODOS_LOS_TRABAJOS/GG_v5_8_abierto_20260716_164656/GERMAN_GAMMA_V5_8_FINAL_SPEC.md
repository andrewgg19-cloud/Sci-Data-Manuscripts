# German Gamma v5.8 - Final Technical Specification

## Estado

German Gamma queda congelado en v5.8.

No se agregan mas modulos, formulas ni nombres operativos. A partir de esta
version, el trabajo debe concentrarse en depuracion, validacion, documentacion y
ejemplos reproducibles.

## Nombre publico recomendado

```text
German Gamma v5.8
Filter-Induced Structure Diagnostic
```

## Proposito

German Gamma es una herramienta exploratoria para estudiar como un horizonte de
observabilidad y un filtro pueden modificar la estructura observable de un
conjunto de datos.

No es un detector de fraude.
No prueba intencion.
No prueba causalidad.
No invalida experimentos por si solo.

## Base formal

Sea:

```text
Omega = dominio total posible
H subset Omega = horizonte observable
Gamma subset H = filtro dentro del horizonte
F subset Gamma = conjunto finalmente analizado
```

El estado natural observable es:

```text
D_N^H = P(X | X in H)
```

El estado filtrado observable es:

```text
D_F = P(X | X in H intersection Gamma)
```

La deformacion inducida por el filtro es:

```text
Delta_HGamma = d(P(X | X in H), P(X | X in H intersection Gamma))
```

## Arquitectura cerrada

```text
1. Horizonte observable
2. Filtro
3. Soporte
4. Sombra 2D / sombra cubica
5. Espejo 2D / espejo cubico
6. Energia residual + entropia
7. Lamina temporal
8. Probabilidad empirica
9. Reversibilidad
```

## Regla de soporte

Si una celda o region pierde soporte:

```text
raw_evaluable = false
```

No se debe usar `EPS` para forzar un resultado finito.

La regularizacion de Laplace puede reportarse solo como auxiliar:

```text
raw primero
regularizado separado
```

## Indices principales

### Deformacion por filtro

```text
Delta_HGamma = d(D_N^H, D_F)
```

### Sombra cubica

```text
p_abc = n_abc / N_abc
```

```text
I_3 = (p000 * p011 * p101 * p110) /
      (p001 * p010 * p100 * p111)
```

```text
D_3 = |ln(I_3)|
```

### Energia residual-entropia

```text
E_res = ||mu_N - mu_F||^2
```

```text
Delta_S = S_N - S_F
```

```text
R_EH = log(1 + E_res) * |Delta_S|
```

### Lamina temporal

```text
A_T(i) = C_T(i) * log(1 + E_res(i)) * |Delta_S(i)| * [-log(P_i)]
```

### Reversibilidad

```text
X_0, X_1, ..., X_T
```

contra:

```text
X_T, X_{T-1}, ..., X_0
```

La capa de reversibilidad mide diferencias de trayectoria, entropia y
transiciones entre lectura hacia adelante y lectura reversa.

## Lectura correcta

German Gamma puede decir:

```text
hay perdida de soporte;
hay senal compatible con filtrado diferencial;
hay ruptura de simetria bajo el horizonte definido;
hay cambio energia-entropia;
hay una lamina temporal rara bajo permutacion;
hay asimetria de reversibilidad.
```

German Gamma no debe decir:

```text
hay fraude;
hay intencion;
hay causalidad demostrada;
el experimento es invalido;
la realidad absoluta fue medida.
```

## Scripts principales

### v5.5.2 audit-grade

```text
german_gamma_v5_5_2_audit_grade.py
```

Uso:

```powershell
py -3 german_gamma_v5_5_2_audit_grade.py shadow --n00 53 --N00 1143 --n01 79 --N01 1197 --n10 62 --N10 1202 --n11 51 --N11 1204 --bootstrap 10000
```

### v5.6 3D / Hilbert / Laplace

```text
german_gamma_v5_6_3d_hilbert_laplace.py
```

Comandos:

```text
cubic_shadow
cubic_mirror
energy_entropy
laplace_temporal
```

### v5.7 temporal sheet

```text
german_gamma_v5_7_temporal_sheet.py
```

Uso:

```powershell
py -3 german_gamma_v5_7_temporal_sheet.py --input datos_prueba_gamma.xlsx --columns x1,x2,x3 --filter "x1 > 0" --window-size 120 --step 60 --permutations 200
```

### v5.8 reversibility

```text
german_gamma_v5_8_reversibility.py
```

Uso:

```powershell
py -3 german_gamma_v5_8_reversibility.py --input datos_prueba_gamma.xlsx --columns x1,x2,x3 --window-size 120 --step 60
```

## Reglas futuras

Toda idea nueva debe ir a:

```text
FUTURE_WORK.md
```

No entra al nucleo v5.8.

Solo se permite:

```text
depurar
unificar
validar
renombrar con sobriedad
documentar
crear pruebas reproducibles
```

## Frase final

```text
German Gamma v5.8 no intenta reemplazar la estadistica clasica.
Integra herramientas clasicas en una arquitectura de auditoria para estudiar
si un filtro cambia soporte, geometria, entropia, probabilidad temporal y
reversibilidad dentro de un horizonte observable declarado.
```

