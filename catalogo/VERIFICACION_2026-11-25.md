# Verificación de descarga, integridad y apertura

25 de noviembre de 2026.

## Resultado

- Se recuperaron los **2,256 archivos originales del catálogo** y se comprobaron tamaño y SHA-256: **0 faltantes y 0 discrepancias**.
- Se verificaron las 30 partes del paquete complementario, su reconstrucción ZIP y los archivos comprimidos fragmentados.
- Se completó la descarga del repositorio desde el navegador mediante Code → Download ZIP.
- Se revisaron los destinos de los enlaces de los cinco índices de publicación: sin destinos ausentes. Los archivos empaquetados se identifican en los índices y requieren el restaurador.
- Se inspeccionaron 840 contenidos únicos, incluidos auxiliares: 141 PDF (1,799 páginas leídas, renderizado de primera y última página), 69 PNG válidos, 9 WAV, 3 MP3, 2 DOCX, 2 XLSX, 2 NPZ, 126 CSV, 126 JSON, 6 JSONL y 86 archivos Python. Otros formatos recibieron comprobación de bytes, no ejecución. Las cifras de formatos cuentan contenidos únicos, no copias repetidas en carpetas.

## Dos incidencias de los originales

1. **Imagen `final_cross_es.png` truncada.** Coincide exactamente con su SHA-256 original, por lo que no se perdió contenido durante la subida. El flujo comprimido de píxeles está incompleto y no admite una reparación sin inventar datos. Se generó una imagen nueva desde el PDF íntegro de la misma figura: [PNG regenerada desde el PDF](../Correcciones_Tecnicas_2026-11-25/final_cross_es_regenerada_desde_PDF.png). La PNG original permanece sin cambios dentro del paquete.
2. **`auditoria_german_gamma.py` contiene cuatro `:` duplicados.** El original se conserva; se añadió [una copia con sintaxis corregida](../Estadistica_y_probabilidad/auditoria_german_gamma_sintaxis_corregida.py). La copia pasa `ast.parse`. No se modificaron ni validaron sus cálculos, valores impresos o conclusiones.

La ejecución de auditoría aparece como fallida porque detecta y conserva la PNG original dañada. La descarga, restauración y las 2,256 comprobaciones de integridad sí pasaron. No se oculta esa incidencia detrás de un resultado general de éxito.

## Evidencia y reproducción

- [Ejecución completa en GitHub Actions](https://github.com/andrewgg19-cloud/Sci-Data-Manuscripts/actions/runs/45681646883).
- [Informe estructurado](verificacion_2026-11-25.json).
- [Código de la comprobación](../tools/auditar_publicacion.py).
- [Procedencia de la imagen nueva](../Correcciones_Tecnicas_2026-11-25/README.md).

## Descargar y abrir

[Descargar el repositorio completo en ZIP](https://github.com/andrewgg19-cloud/Sci-Data-Manuscripts/archive/refs/heads/main.zip), descomprimir y ejecutar desde la carpeta del repositorio:

```sh
python restaurar_archivos_grandes.py
```

Los archivos empaquetados aparecerán entonces en sus rutas originales y podrán abrirse con sus aplicaciones correspondientes. La comprobación se refiere al catálogo publicado y a las exclusiones autorizadas registradas; no incorpora trabajos que no se hayan aportado. Se comprueba preservación y apertura técnica, no validez científica ni funcionamiento completo de los programas.