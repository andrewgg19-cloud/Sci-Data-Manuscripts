# NOAA CO2 - German-Gamma v5.5

Fuente oficial: NOAA GML Mauna Loa CO2 mensual.

## Horizonte-Espejo

- Control identidad C_H: 0.000000
- Horizonte `co2_average > co2_roll_mean_12` C_H: 0.844884
- Lectura: no_conmutatividad_fuerte

## Topologia Exploratoria

- Nota: el filtro usado no es un filtro original NOAA; se deriva como `co2_anomaly > 0` para prueba exploratoria.
- N total: 820
- N post: 505
- tasa supervivencia: 0.615854
- costo bits: 0.699341
- delta H0: -23
- delta H1: 0
- p bottleneck H1: 0.660000

## Lectura

La serie NOAA CO2 muestra no-conmutatividad fuerte bajo el horizonte `CO2 > media movil`, lo cual es esperable porque el horizonte separa una region asimetrica respecto al espejo centrado.
La topologia exploratoria no muestra ruptura H1 significativa.
Este resultado debe leerse como prueba de funcionamiento sobre datos NOAA reales, no como conclusion climatologica.