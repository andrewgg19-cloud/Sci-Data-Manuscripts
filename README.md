# Sci-Data-Manuscripts

Colección de trabajos de **Andrés Germán García**, también firmado como **Germán García Andrés**. Investigador independiente, México.

Manuscritos, ensayos, código, datos, figuras y realizaciones sonoras reunidos en las cuatro carpetas iniciales y las incorporaciones de Ciencias Biológicas aportadas por el autor. Se conservan los textos, resultados y versiones originales; los ZIP interiores se despliegan en carpetas terminadas en `_contenido`.

## Explorar los trabajos

| Carpeta | Archivos originales | Índice |
|---|---:|---|
| [Memorias y ensayos](Memorias/) | 6 | [Ver archivos](Memorias/INDICE_PUBLICACION.md) |
| [Estadística y probabilidad](Estadistica_y_probabilidad/) | 899 | [Ver archivos](Estadistica_y_probabilidad/INDICE_PUBLICACION.md) |
| [Física, astronomía, cuántica y relatividad](Fisica_Astronomia_Cuantica_Relativista/) | 1172 | [Ver archivos](Fisica_Astronomia_Cuantica_Relativista/INDICE_PUBLICACION.md) |
| [Hipótesis de Riemann](Hipotesis_de_Riemann/) | 177 | [Ver archivos](Hipotesis_de_Riemann/INDICE_PUBLICACION.md) |
| [Ciencias Biológicas](Ciencias_Biologicas/) | 2 | [Ver archivos](Ciencias_Biologicas/INDICE_PUBLICACION.md) |

## Descargar y recuperar los archivos grandes

El código, la documentación y numerosos PDF se pueden consultar directamente. El material complementario y los archivos de mayor tamaño se reúnen en paquetes **sin pérdida** para facilitar su publicación. El restaurador recupera los PDF, figuras, tablas y audios restantes en sus rutas originales. El catálogo conserva el tamaño y SHA-256 de cada archivo.

Descarga el repositorio completo con **Code → Download ZIP**, descomprímelo y ejecuta con Python 3:

```sh
python restaurar_archivos_grandes.py
```

También puedes clonar este repositorio:

```sh
git clone https://github.com/andrewgg19-cloud/Sci-Data-Manuscripts.git
cd Sci-Data-Manuscripts
python restaurar_archivos_grandes.py
```

El restaurador no necesita paquetes externos. Verifica los fragmentos y reconstruye exactamente los bytes originales. Permite seleccionar una carpeta, por ejemplo `python restaurar_archivos_grandes.py --carpeta Rosetta_10000`.

## Catálogo y procedencia

- [Inventario de archivos y versiones](catalogo/inventario.csv).
- [Manifiesto de integridad y almacenamiento](catalogo/manifest.json).
- [Registro de exclusiones técnicas y referencias](catalogo/exclusiones.json). Se omiten metadatos Git interiores y cachés. El texto de Alberto Güijosa incluido como `campos.pdf` en el material recibido se registra como referencia de tercero y no se distribuye como obra del autor de esta colección. Referencia: *Campos cuánticos: El universo a partir de gelatinas*, Instituto de Ciencias Nucleares, UNAM, http://www.nucleares.unam.mx/~alberto/.

## Versiones y uso

La colección reúne documentos de distintas fechas y estados de elaboración. Las afirmaciones y conclusiones de cada documento pertenecen a sus autores y versiones correspondientes. La fecha de publicación de este archivo en GitHub no modifica la fecha de creación indicada dentro de cada trabajo.

Se conservan las licencias y avisos existentes dentro de cada proyecto. No se aplica una licencia nueva y general a toda la colección. Para citar un trabajo, utiliza los datos del documento y su DOI cuando esté indicado; para identificar una versión concreta de esta colección, incluye el enlace al archivo y al commit correspondiente.

## Verificación técnica de la publicación

La comprobación del 25 de noviembre de 2026 recuperó los 2,256 archivos originales del catálogo y confirmó sus tamaños y SHA-256. Se completó la descarga ZIP y se abrieron los formatos principales. Se detectaron una PNG truncada y un script original con errores de sintaxis; se conservan los originales y se proporcionan copias técnicas separadas.

[Consultar resultados, incidencias y archivos de sustitución](catalogo/VERIFICACION_2026-11-25.md).

[Tabla biológica: edición didáctica, actividades y guía docente](Ciencias_Biologicas/Revision_Didactica_2026-11-25/).
