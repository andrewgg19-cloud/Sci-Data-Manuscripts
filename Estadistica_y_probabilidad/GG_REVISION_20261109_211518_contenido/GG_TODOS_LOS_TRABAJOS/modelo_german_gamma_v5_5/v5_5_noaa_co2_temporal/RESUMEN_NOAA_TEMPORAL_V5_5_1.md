# NOAA CO2 Temporal v5.5.1 - Resumen

Definicion exploratoria corregida:

```text
a = mes Apr-Sep
b = co2_delta > 0
Gamma = co2_average > co2_deseasonalized
ventana = bloque de 5 anos
```

- ventanas: 14
- soporte_completo: 2
- perdida_soporte_expresado: 9
- no_evaluable_soporte_total: 3
- ventanas criticas evaluables: 1
- confirmadas por persistencia: 0
- H mediana: 0.778328
- D_G mediana evaluable: 0.169906

## Lectura

La prueba temporal NOAA no produce una sombra finita persistente limpia.
La senal dominante es perdida de soporte expresado en muchas ventanas de 5 anos, causada por la estructura estacional de la regla Gamma exploratoria.
Esto prueba que German-Gamma separa soporte perdido de sombra finita y evita confirmar una deformacion persistente cuando la base local es degenerada.

No es una conclusion climatologica; es una prueba metodologica sobre datos NOAA reales.