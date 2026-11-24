# German Gamma v5.7 - Temporal Sheet Layer

## Idea central

Cada ventana temporal se trata como una lamina congelada:

```text
T_i = X[t_i, t_i + Delta t]
```

La lamina se evalua como una unidad local, no solo como parte de una tabla global.

## Componentes

Para cada lamina temporal:

```text
C_T(i)   = ruptura espejo-temporal
E_res(i) = energia residual entre centroide base y centroide filtrado
Delta_S  = cambio de entropia entre base y filtrado
P_i      = probabilidad empirica bajo permutacion nula
```

## Indice nuevo

```text
A_T(i) = C_T(i) * log(1 + E_res(i)) * |Delta_S(i)| * [-log(P_i)]
```

## Lectura

```text
A_T bajo:
la lamina cambia poco o el cambio es esperable.

A_T medio:
hay senal exploratoria local.

A_T alto con P_i bajo:
la lamina muestra asimetria, desplazamiento, cambio de entropia y rareza probabilistica.
```

## Regla de seguridad

```text
German Gamma v5.7 no prueba fraude.
No prueba intencion.
No prueba causalidad.
Marca laminas temporales raras o estructuralmente deformadas bajo el filtro definido.
```

## Uso

```powershell
py -3 german_gamma_v5_7_temporal_sheet.py --input datos_prueba_gamma.xlsx --columns x1,x2,x3 --filter "x1 > 0" --window-size 120 --step 60 --permutations 200
```

