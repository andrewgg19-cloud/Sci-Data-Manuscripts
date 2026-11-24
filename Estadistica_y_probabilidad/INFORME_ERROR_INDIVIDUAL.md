# German Gamma, Forecaster y una combinación puntual: resta individual de incertidumbre de radio

## Datos y método

Se alinearon por nombre de planeta y sistema los 897 registros de `resultados_forecaster_897.csv` y `datos_897_gg.csv` (775 sistemas). Ambos modelos se evaluaron con la misma incertidumbre de radio reportada por objeto. La columna `radius_err_frac` representa una incertidumbre relativa aproximada del radio, simetrizada; **no puede identificarse rigurosamente como el error estándar muestral de cada planeta**, porque no disponemos de su número de mediciones independientes ni de las distribuciones originales de ajuste.

En cada planeta i, definimos:

- `u_R,i = R_obs,i × radius_err_frac,i`, en radios terrestres: margen observacional aproximadamente 1 sigma.
- Error porcentual original `APE_i = 100 × |R_pred,i - R_obs,i| / R_obs,i`.
- **Resta literal solicitada** `APE_i − 100 × u_R,i / R_obs,i`, incluso si resulta negativa.
- **Error excedente descriptivo** `100 × max(0, |R_pred,i - R_obs,i| − u_R,i) / R_obs,i`.

Se aplicó a German Gamma, Forecaster y a una **combinación puntual** definida por el promedio 50/50 de las dos predicciones centrales. Esta tercera columna **NO** representa la mediana de una mezcla de distribuciones posterior ni constituye una evaluación probabilística híbrida. Las puntuaciones CRPS originales no se modificaron: no corresponde restarles una incertidumbre expresada en otras unidades ni transformar el resultado en un supuesto CRPS corregido.

## Resultados (897 planetas)

| Modelo | MdAPE original | Mediana del error excedente de 1σ | Planetas con error puntual ≤ 1σ |
|---|---:|---:|---:|
| German Gamma | 14.73% | **9.78%** | 17.73% |
| Forecaster probabilístico (mediana puntual) | 15.35% | 10.58% | 17.73% |
| Híbrido **puntual** 50/50 | 15.24% | 10.33% | 18.28% |

Mediana de incertidumbre individual de radio: 0.3365 radios terrestres, equivalente a 4.13% relativo.

La diferencia entre medianas de exceso (GG − Forecaster) es −0.80 puntos porcentuales, IC 95% bootstrap agrupado por los 775 sistemas estelares **[−1.85, +0.30]** (6,000 remuestreos). Incluye cero: **no hay ventaja estadísticamente concluyente**.

La diferencia en la mediana del error excedente entre híbrido puntual y GG es +0.55 puntos porcentuales, con IC 95% [−0.32, +1.12]. Por tanto, tampoco se demuestra superioridad del híbrido puntual.

## Ejemplo individual

CoRoT-11 b: radio medido 16.03 R⊕, incertidumbre ≈ 0.34 R⊕ (2.121%). El error porcentual German Gamma pasa de 15.558% a 13.437% tras restar la incertidumbre individual. Para Forecaster pasa de 18.411% a 16.290%. **La diferencia entre errores individuales permanece exactamente igual cuando se resta el mismo margen sin truncar**.

## Limitaciones

1. El margen 1σ de un radio medido no equivale necesariamente al `SE = s / sqrt(n)` de una media muestral.
2. Esta resta es un análisis de sensibilidad descriptivo. No es un estimador validado de error de predicción y no debe usarse como criterio principal del artículo.
3. La versión con truncamiento en cero cambia de modo no lineal las diferencias, por lo que no debe interpretarse como una prueba de significación.
4. Parte de la incertidumbre observacional ya pudo entrar en los modelos probabilísticos. Restarla otra vez al CRPS o a las predicciones puede duplicar el tratamiento del error.
5. Las comparaciones probabilísticas originales siguen siendo: CRPS GG 0.141223 frente a Forecaster 0.143131, con intervalo de la diferencia que incluye cero.
6. La combinación puntual por promedio no sustituye al híbrido probabilístico; este último requiere realizar una mezcla de muestras de ambas distribuciones y puntuarla correctamente.

**Conclusión:** la resta individual reduce numéricamente ambos errores, pero no demuestra superioridad de German Gamma ni del híbrido. La comparación con y sin margen de error queda disponible para inspección planeta por planeta, sin alterar los datos fuente.
