# German Gamma v5.5.2 Audit-Grade

## Motivo de esta version

Esta version corrige los puntos debiles detectados en la revision critica de v5.5.1:

- nombres de salida demasiado dramaticos;
- uso de `EPS` para forzar resultados finitos en celdas cero;
- umbrales exploratorios sin calibracion;
- riesgo de falsos positivos si se usa como sistema de decision.

## Alcance correcto

German Gamma v5.5.2 no es un detector de fraude.

Es una herramienta exploratoria para identificar condiciones compatibles con estructura inducida por filtros:

- perdida de soporte;
- diferencias de tasas entre celdas 2x2;
- persistencia temporal de una senal;
- diferencia horizonte-espejo bajo una representacion dada.

Ninguna salida prueba intencion, causalidad, manipulacion o invalidez experimental por si sola.

## Cambios tecnicos principales

### 1. Sin EPS en el resultado principal

Si una celda aceptada vale cero, el modelo ya no fuerza un numero finito.

La salida correcta es:

```text
support_state = expressed_support_loss
finite_metric_evaluable = false
shadow_log_score = null
```

Esto evita convertir una discontinuidad de soporte en una cifra artificial.

### 2. Sombra 2x2 como metrica derivada, no como invencion aislada

La metrica principal se declara explicitamente como contraste multiplicativo de tasas de aceptacion:

```text
I = (p00 * p11) / (p01 * p10)
D = |ln(I)|
```

Tambien se reporta una razon de momios clasica cuando el soporte lo permite.

### 3. Validacion estadistica basica

La salida 2x2 puede incluir:

- Fisher exact test;
- chi-square test cuando los conteos esperados son suficientes;
- bootstrap contra tasa global nula.

La salida horizonte-espejo puede incluir:

- calibracion por permutaciones;
- intervalo empirico 95%.

### 4. Lenguaje operativo sobrio

Se reemplazan lecturas dramatizadas por etiquetas tecnicas:

```text
not_evaluable_as_finite_shadow
exploratory_selection_signal_requires_calibration
empirically_calibrated_selection_signal
not_significant_under_permutation_null
temporal_persistence_flag
```

## Script principal

```text
german_gamma_v5_5_2_audit_grade.py
```

## Ejemplos de uso

### Sombra 2x2

```powershell
py -3 german_gamma_v5_5_2_audit_grade.py shadow --n00 53 --N00 1143 --n01 79 --N01 1197 --n10 62 --N10 1202 --n11 51 --N11 1204 --bootstrap 10000
```

### Sombra 2x2 con celda cero

```powershell
py -3 german_gamma_v5_5_2_audit_grade.py shadow --n00 0 --N00 100 --n01 10 --N01 100 --n10 12 --N10 100 --n11 9 --N11 100
```

La salida esperada no debe inventar una cifra finita. Debe reportar perdida de soporte expresado.

### Horizonte-espejo

```powershell
py -3 german_gamma_v5_5_2_audit_grade.py horizon --input datos_prueba_gamma.xlsx --columns x1,x2,x3 --horizon "x1 > 0" --permutations 500
```

### Trayectoria temporal

```powershell
py -3 german_gamma_v5_5_2_audit_grade.py temporal --temporal-csv ejemplo_sombra_temporal.csv --critical-score 0.25 --k 2
```

## Criterio de lectura

Una senal solo debe considerarse fuerte si:

1. el soporte es completo;
2. la metrica finita es evaluable;
3. la senal supera una calibracion nula;
4. el dominio justifica la interpretacion.

Si falta cualquiera de esos puntos, la lectura debe mantenerse como exploratoria o no evaluable.

