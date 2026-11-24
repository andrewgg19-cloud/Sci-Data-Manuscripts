# Preparación para Zenodo - 17 noviembre 2026

Tres depósitos propuestos: 01_Rotor, 02_Multiescala y 03_Gravedad_triadica.
Estado: archivos preparados; NO subidos ni publicados, sin DOI asignado.
Autor: Andrés Germán García, investigador independiente.

Leer primero Revision/Nota_tecnica_y_correcciones.pdf. Los PDF originales se conservan íntegros y deben distribuirse junto a esa nota: contienen afirmaciones que esta revisión corrige o delimita. Los metadatos de cada carpeta son propuestas y requieren la selección de licencia por el autor. No se confiere una licencia nueva a datos ajenos.

## Verificación realizada
Las dos canalizaciones empíricas originales se reejecutaron con sus datos y terminaron correctamente. Se incluyen sus salidas nuevas por separado. Es reproducción computacional, no replicación independiente ni auditoría estadística exhaustiva.
Los scripts nuevos comprueban el rotor y una familia FLRW restringida; no prueban el potencial periódico gravitatorio, la transición 41.1→22 ni una abundancia bariónica.

## Ejecución
Instalar numpy, pandas, scipy, matplotlib y sympy. Consultar versiones_entorno.json.
python 01_Rotor/verificar_rotor.py
python 03_Gravedad_triadica/verificar_compatibilidad_FLRW.py
python 02_Multiescala/material_original/demostracion_exoplanetas_multiescala.py --output-dir resultados_planetas
python 02_Multiescala/material_original/demostracion_capacidad_multiescala.py --output-dir resultados_cosmologia

Cada carpeta puede adjuntarse como contenido de un registro distinto. Vincular los tres registros únicamente mediante DOI reales cuando existan. Confirmar primero si ya hay depósitos de estos trabajos para evitar duplicados y utilizar nuevas versiones cuando corresponda.
