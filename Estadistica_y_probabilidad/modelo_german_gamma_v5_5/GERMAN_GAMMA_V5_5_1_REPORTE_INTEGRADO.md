# German-Gamma v5.5.1 - Reporte Integrado

Autor conceptual: Andres German Garcia

Fecha de cierre de modulo: 2026-07-16

Estado: reporte tecnico-operacional del modulo horizonte-espejo, sombra temporal
y perdida de soporte.

---

## 1. Pregunta Central

German-Gamma v5.5.1 responde una pregunta epistemologica operacional:

```text
El resultado observado pertenece al fenomeno, o fue producido/modificado por
el horizonte y el filtro que lo hicieron visible?
```

La observacion se modela como cadena:

```text
fenomeno -> horizonte observable -> filtro Gamma -> medida inducida -> trayectoria -> interpretacion
```

---

## 2. Definicion Formal

Un sistema German-Gamma se define como:

```text
GG = (Omega, F, P, H, Pi_H, Gamma, M, D, Phi, T, A)
```

donde:

```text
(Omega, F, P) = espacio probabilistico padre
H             = horizonte de observacion
Pi_H          = operador de horizonte observable
Gamma         = operador de seleccion
M             = operador espejo o transformacion de simetria
D             = funcion de distancia o divergencia
Phi           = vector de metricas de deformacion
T             = indice temporal o familia de ventanas
A             = regla de apelacion temporal
```

Forma compacta:

```text
GG_t(P) =
A_k[
  Phi_t(
    P(. | H_t = 1, Gamma_t = 1)
  ),
  D( M(Pi_{H_t}(Omega)), Pi_{H_t}(M(Omega)) ),
  N_t*
]
```

---

## 3. Horizonte Observable

El horizonte observable es:

```text
Pi_H(X) = {x_i in X : H(x_i) = 1}
```

El horizonte total no se define como ausencia de condicion, sino como identidad
explicita:

```text
H_0(x) := x_j == x_j
```

En datos computacionales:

```text
NaN != NaN
```

por lo que:

```text
Pi_H0(X) = X valido
```

Control esperado:

```text
C_H(X) = 0
```

---

## 4. No-Conmutatividad Horizonte-Espejo

La prueba formal es:

```text
C_H(X) =
D_JS(
  Hist(M(Pi_H(X))),
  Hist(Pi_H(M(X)))
)
```

Algoritmo:

```text
1. X_H = Pi_H(X)
2. R_1 = M(X_H)
3. X_M = M(X)
4. R_2 = Pi_H(X_M)
5. P_1 = Hist(R_1)
6. P_2 = Hist(R_2)
7. C_H = D_JS(P_1, P_2)
```

Lectura:

```text
C_H ~= 0  -> horizonte y espejo conmutan bajo la representacion elegida
C_H > 0   -> el orden horizonte/espejo altera la distribucion empirica
```

Implementado en:

```text
german_gamma_horizonte_espejo.py
```

---

## 5. Sombra Geometrica

Para celdas binarias:

```text
P_ab = P(Gamma = 1 | a,b)
```

El invariante de sombra es:

```text
I_S = (P_00 P_11) / (P_01 P_10)
```

La distancia de sombra:

```text
D_G = |ln(I_S)|
```

Con conteos:

```text
P_ab = n_ab / N_ab
```

por tanto:

```text
D_G =
|ln( ((n_00/N_00)(n_11/N_11)) / ((n_01/N_01)(n_10/N_10)) )|
```

Implementado en:

```text
auditoria_german_gamma_sombra.py
```

---

## 6. Entropia Temporal

Por ventana temporal:

```text
H(R_t) = - sum_i p_i(t) ln p_i(t)
```

Entropia normalizada:

```text
H*(R_t) = H(R_t) / ln(m)
```

En tabla 2x2:

```text
H*(t) =
- [sum_{a,b} p_ab(t) ln p_ab(t)] / ln(4)
```

---

## 7. Apelacion Temporal

Una senal no se confirma por un solo cruce de umbral.

Sea:

```text
Z_t = 1{D_G(t) > D_c}
```

Racha critica:

```text
R_t = Z_t(R_{t-1}+1)
```

si `Z_t = 1`, y:

```text
R_t = 0
```

si `Z_t = 0`.

Confirmacion:

```text
A_t = 1{R_t >= k}
```

Estados:

```text
sin_persistencia_critica
senal_en_apelacion
confirmada_por_persistencia
```

---

## 8. Perdida De Soporte

Para evitar confundir una explosion numerica con una sombra finita fuerte,
v5.5.1 separa soporte expresado.

Sea:

```text
N_ab(t) = total de eventos disponibles en la celda (a,b)
n_ab(t) = eventos sobrevivientes Gamma=1 en la celda (a,b)
```

Definimos:

```text
s_N(t) = min_{a,b} N_ab(t)
s_n(t) = min_{a,b} n_ab(t)
```

Estados:

```text
soporte_completo              si s_N(t) > 0 y s_n(t) > 0
perdida_soporte_expresado     si s_N(t) > 0 y s_n(t) = 0
no_evaluable_soporte_total    si s_N(t) = 0
```

Regla:

```text
D_G(t) solo alimenta apelacion temporal si soporte_estado(t) = soporte_completo
```

Lectura:

```text
La explosion de D_G por n_ab = 0 es una senal de soporte perdido.
No debe mezclarse con sombra finita fuerte.
```

---

## 9. Pruebas Ejecutadas

### 9.1 Horizonte-Espejo

| Prueba | Horizonte | Resultado |
|---|---|---|
| control normal | `x1 == x1` | `C_H = 0.000000` |
| filtro geometrico | `x1 + x2 > 0.8` | `C_H = 0.191686` |
| BIG Bell | `bitrate_bits_per_2s > bitrate_roll_mean_10` | `C_H = 0.023432` |

Lectura:

```text
El control identidad conmuta.
El horizonte geometrico introduce no-conmutatividad moderada.
BIG Bell muestra no-conmutatividad leve.
```

### 9.2 Topologia

| Prueba | Resultado |
|---|---|
| control normal | no alerta |
| filtro geometrico | alerta geometrica por H0 |
| anillo roto | alerta topologica H1 |
| BIG Bell | sin ruptura H1 significativa |

Lectura:

```text
El modelo no alerta en control.
Detecta deformaciones conocidas.
Se contiene en datos reales.
```

### 9.3 BIG Bell Temporal

Construccion 2x2:

```text
a = bitrate_bits_per_2s > bitrate_roll_mean_10
b = bitrate_delta > 0
Gamma = filtro
```

Resultados:

```text
ventanas: 87
ventanas criticas D_G > 0.25: 15
ventanas confirmadas por persistencia: 0
ventanas con perdida de soporte: 28
D_G mediana: 0.0
H mediana: 0.9233
aceptados mediana: 375
```

Lectura:

```text
Hay episodios de sombra alta.
Hay ventanas con perdida de soporte.
No hay confirmacion por persistencia tras excluir ventanas degeneradas.
```

---

## 10. Figuras

### Horizonte-Espejo

```text
v5_5_test_run/figuras/01_horizonte_espejo_CH.png
```

### Topologia

```text
v5_5_test_run/figuras/02_topologia_H0_H1.png
```

### Tasa De Horizonte / Supervivencia

```text
v5_5_test_run/figuras/03_tasa_supervivencia.png
```

### Lamina Integrada

```text
v5_5_test_run/figuras/04_lamina_intensidad.png
```

### BIG Bell Temporal

```text
v5_5_big_bell_temporal/figuras/01_big_bell_DG_temporal.png
v5_5_big_bell_temporal/figuras/02_big_bell_entropia_temporal.png
v5_5_big_bell_temporal/figuras/03_big_bell_aceptados_temporal.png
```

---

## 11. Prueba NOAA CO2

German-Gamma v5.5.1 tambien fue probado con datos reales NOAA GML Mauna Loa
CO2 mensual.

Fuente oficial:

```text
https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_mm_mlo.csv
```

Archivos:

```text
v5_5_noaa_co2/co2_mm_mlo.csv
v5_5_noaa_co2/noaa_co2_mlo_gamma_input.csv
v5_5_noaa_co2/noaa_co2_mlo_gamma_input.xlsx
```

### 11.1 Preparacion

Variables derivadas:

```text
co2_delta        = cambio mensual de CO2
co2_roll_mean_12 = media movil de 12 meses
co2_roll_std_12  = desviacion movil de 12 meses
co2_anomaly      = co2_average - co2_roll_mean_12
```

### 11.2 Horizonte-Espejo NOAA

Horizonte probado:

```text
co2_average > co2_roll_mean_12
```

Control identidad:

```text
t_index == t_index
```

Resultados:

```text
Control identidad C_H: 0.000000
Horizonte CO2 > media movil C_H: 0.844884
Lectura: no_conmutatividad_fuerte
```

Lectura:

```text
El horizonte "CO2 por encima de su media movil" introduce una asimetria fuerte
respecto al espejo centrado. Esto es esperable porque el horizonte separa una
region no simetrica de la serie.
```

### 11.3 Topologia Exploratoria NOAA

Filtro exploratorio:

```text
filtro = co2_anomaly > 0
```

Resultado:

```text
N total: 820
N post: 505
tasa supervivencia: 0.615854
costo bits: 0.699341
delta H0: -23
delta H1: 0
p bottleneck H1: 0.660000
```

Lectura:

```text
No aparece ruptura topologica H1 significativa.
```

Advertencia:

```text
El filtro topologico NOAA es derivado para prueba metodologica.
No es un filtro original declarado por NOAA.
```

### 11.4 NOAA Temporal v5.5.1

La primera version anual resulto degenerada porque la regla Gamma se solapaba
con una de las celdas de horizonte. La prueba fue corregida para evitar una
tautologia operacional.

Definicion temporal corregida:

```text
a = mes Apr-Sep
b = co2_delta > 0
Gamma = co2_average > co2_deseasonalized
ventana = bloque de 5 anos
```

Resultados:

```text
ventanas: 14
soporte_completo: 2
perdida_soporte_expresado: 9
no_evaluable_soporte_total: 3
ventanas criticas evaluables: 1
confirmadas por persistencia: 0
H mediana: 0.778328
D_G mediana evaluable: 0.169906
```

Lectura:

```text
La prueba temporal NOAA no produce una sombra finita persistente limpia.
La senal dominante es perdida de soporte expresado en muchas ventanas de 5 anos.
German-Gamma separa soporte perdido de sombra finita y evita confirmar una
deformacion persistente cuando la base local es degenerada.
```

### 11.5 Figuras NOAA

```text
v5_5_noaa_co2/figuras/01_noaa_co2_horizonte.png
v5_5_noaa_co2/figuras/02_noaa_co2_CH.png
v5_5_noaa_co2/figuras/03_noaa_co2_topologia.png
v5_5_noaa_co2_temporal/figuras/01_noaa_temporal_DG_5y.png
v5_5_noaa_co2_temporal/figuras/02_noaa_temporal_entropia_5y.png
```

### 11.6 Conclusion NOAA

```text
NOAA CO2 confirma que el modulo horizonte-espejo opera sobre datos reales y
detecta no-conmutatividad fuerte cuando se impone un horizonte asimetrico.
La topologia no muestra ruptura H1 significativa.
La prueba temporal no confirma sombra persistente; detecta perdida de soporte.
```

No debe leerse como conclusion climatologica nueva. Es una prueba metodologica
de German-Gamma sobre datos reales NOAA.

---

## 12. Limites

German-Gamma v5.5.1 no prueba por si solo:

```text
fraude
intencion
invalidez experimental
causalidad final
```

El marco detecta:

```text
deformacion compatible con horizonte
deformacion compatible con seleccion
sombra geometrica
perdida de soporte
ruptura topologica
persistencia o ausencia de persistencia temporal
```

---

## 13. Conclusion v5.5.1

German-Gamma v5.5.1 queda cerrado como modulo operacional con tres aportes:

```text
1. Horizonte-espejo computable mediante C_H.
2. Sombra temporal con entropia y apelacion.
3. Separacion formal entre sombra finita y perdida de soporte.
```

Resultado general:

```text
El modelo no fuerza alertas.
Los controles pasan.
Las deformaciones conocidas son detectadas.
Los datos reales se leen con contencion.
```

Dominios reales probados:

```text
BIG Bell
NOAA CO2
```

Frase de cierre:

```text
German-Gamma no audita solo el dato; audita la cadena que hizo visible al dato.
```
