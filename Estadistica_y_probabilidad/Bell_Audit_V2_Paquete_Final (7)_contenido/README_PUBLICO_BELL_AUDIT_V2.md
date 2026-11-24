# Bell Audit Reforzado v2

Auditoria reproducible del pipeline observacional abierto asociado a Hensen et al. 2015.

## Objeto auditado

- Paper base: Hensen et al. 2015, Nature, DOI `10.1038/nature15759`
- Dataset abierto: DOI `10.4121/uuid:6e19e9b2-4a2d-40b5-8dd3-a660bf3c0a31`
- Analisis adicional relevante: Hensen et al. 2016, DOI `10.1038/srep30289`, arXiv `1603.05705`

## Que hace este codigo

- Reproduce el valor base CHSH reportado desde el dataset abierto.
- Mide sensibilidad de `S` y `p-value` respecto a parametros temporales del pipeline.
- Ejecuta bootstrap, Monte Carlo sobre `event-ready offset`, Kalman diario, complejidad tipo Kolmogorov, chequeo de invarianza ciclica, test de no-signaling, pruebas simples de aleatoriedad de settings, comparacion diaria entre aceptacion y `S`, y resumen `look-elsewhere` sobre la malla de parametros.
- Genera mallas 3D para `S`, `p-value` y numero de ensayos Bell aceptados.

## Que afirma este trabajo

- El resultado base publicado de Hensen 2015 es reproducible desde el conjunto abierto oficial.
- El valor de `S`, el `p-value` y el numero de ensayos aceptados dependen de manera cuantificable del pipeline temporal abierto.
- La violacion reportada es reproducible, pero no es invariante en toda la familia de offsets y ventanas exploradas.
- En la corrida reforzada v2, la muestra filtrada no muestra evidencia fuerte de violacion de no-signaling.
- En la corrida reforzada v2, la asociacion diaria entre aceptacion y `S` no aparece como una bandera roja fuerte.

## Que NO afirma este trabajo

- No afirma que el teorema de Bell sea falso.
- No afirma fraude, manipulacion intencional ni invalidez total del experimento.
- No afirma que la poblacion fisica completa haya sido reconstruida a partir del dataset abierto.
- No afirma que la sensibilidad observada implique por si sola un artefacto de post-seleccion.
- No afirma que este analisis sustituya una revision por pares o una auditoria sobre datos mas primarios.

## Limite principal

El dataset abierto ya representa una seleccion experimental previa. Por tanto, esta auditoria trabaja sobre el pipeline observacional publicado y no sobre el flujo bruto completo de todos los intentos fisicos.

## Uso

Ejemplo de ejecucion:

```bash
python hensen2015_audit_reforzado_v2.py --data-file bell_open_data.txt --generate-plots --json-out hensen2015_audit_report_v2.json
```

Si no se pasa `--data-file`, el script intenta descargar y extraer el dataset oficial.

## Archivos esperados

- `hensen2015_audit_reforzado_v2.py`
- `hensen2015_audit_report_v2.json`
- `surface_plots_v2/`

## Posicion metodologica

Este repositorio distingue entre:

- hechos reproducidos,
- hipotesis interpretativas,
- y limites de identificabilidad impuestos por una muestra observacional truncada.

La tesis sobria del repositorio es: una realizacion experimental concreta del test de Bell puede reproducir la violacion reportada y, al mismo tiempo, exhibir sensibilidad no despreciable al operador de acceso a los datos.
