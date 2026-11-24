# HRG a 50 MeV y comparación con el cruce de 38.2 MeV

Fecha: 9 de octubre de 2026. Se repite el cálculo de equilibrio con los mismos
inventarios congelados y el mismo rendimiento neto cosmológico del análisis
anterior. La referencia **50 MeV** se adopta de la literatura científica,
no de un ajuste personal de temperatura; equivale a 5.802259 × 10¹¹ K.

**Fundamento físico:** Satarov, Mishustin y Greiner (2013), sección III,
figura 3 y página 11 del PDF de arXiv:1305.4046, describen abundancias de
bariones y antibariones casi iguales por encima de unos 50 MeV y una caída
rápida de la proporción de antibariones por debajo. Yang y Rafelski (2022),
página 3 del artículo, describen la evolución entre 50 y 30 MeV y reportan
38.2 MeV para el criterio n_antiB/n_net = 1. Por ello 50 MeV es un punto
bibliográfico aproximado dentro de esa evolución, no una medición del primer
evento de aniquilación ni una temperatura exacta de freeze-out. Los puntos
intermedios de la curva son evaluaciones numéricas para localizar ese cruce,
no nuevas épocas físicas postuladas.

## Resultado a 50 MeV, catálogo PDG2025

| Magnitud | Resultado por cm³ físico a esa temperatura |
|---|---:|
| Bariones | 2.726089504 × 10³⁰ |
| Antibariones | 2.717213050 × 10³⁰ |
| Suma de ambos | 5.443302554 × 10³⁰ |
| Exceso neto bariónico | 8.876454327 × 10²⁷ |

El cociente antibariones/exceso neto es **306.114688**. El cociente
antibariones/bariones es **0.996743887**, equivalente a unos 99.6744 antibariones
por cada 100 bariones. El exceso neto representa 0.163071 % de la suma. Los
protones, neutrones y sus antipartículas aportan **95.2176 %** de esa suma.

Estas son densidades instantáneas del modelo, no cantidades acumuladas de
reacciones ni un número absoluto para todo el Universo.

## Secuencia de enfriamiento y comparación equivalente

Se define R(T) = n_antibaryon / (n_baryon − n_antibaryon), calculando el exceso
con una expresión estable que evita restar poblaciones casi iguales.

| T (MeV) | R: antibariones/exceso neto | Antibariones/bariones |
|---|---:|---:|
| 50.000000 | 306.114688 | 0.996744 |
| 45.000000 | 44.028849 | 0.977792 |
| 40.000000 | 3.486095 | 0.777089 |
| 38.203739 | 1.000000 | 0.500000 |
| 38.200000 | 0.997012 | 0.499252 |
| 37.000000 | 0.336326 | 0.251680 |

El cruce **R = 1** se alcanza a **38.203738689 MeV**.
Yang y Rafelski (2022) publican **38.2 MeV** para el mismo criterio. La diferencia
numérica es **+0.003739 MeV**: nuestro resultado
redondea a 38.2 MeV a la precisión de la referencia publicada. No se interpreta
esa diferencia como una precisión estadística del acuerdo.

A 50 MeV estamos 11.8 MeV por encima del punto publicado de cruce. Las dos
referencias identifican hitos distintos: aproximadamente 50 MeV sitúa el
comienzo de una disminución rápida de la fracción de antibariones en la literatura;
R = 1 identifica cuándo los antibariones igualan al exceso neto. En el cruce
nB = 2 n_antiB, por lo que los antibariones todavía no han desaparecido.

Los tres catálogos dan temperaturas de cruce:

- PDG2014: 38.203596345 MeV.
- PDG2020: 38.203738666 MeV.
- PDG2025: 38.203738689 MeV.

Al variar solamente η = (6.12 ± 0.04) × 10⁻¹⁰, el cruce PDG2025 se mueve entre
**38.192814 y 38.214598 MeV**.
Este intervalo propaga un único dato de entrada; no es la incertidumbre física
total del modelo. La referencia de 38.2 MeV está reportada con un decimal.

La figura incluida muestra R(T), el punto a 50 MeV y una ampliación del cruce.
Su banda varía sólo η dentro de la incertidumbre usada como entrada. Incluye pie
de figura y está disponible en PNG y SVG.

## Qué demuestra esta reconstrucción

La coincidencia constituye **consistencia de un cálculo de equilibrio con una
referencia publicada**. El resultado puede describirse como reconstrucción
condicionada al modelo. Para afirmar una historia única o una comprobación
independiente de las poblaciones iniciales faltan restricciones adicionales.

El dato actual impone el exceso Y_net = (nB − n_antiB)/s = η/7.04. Por ejemplo,
los inventarios hipotéticos (101 bariones, 100 antibariones) y (1001 bariones,
1000 antibariones) tienen el mismo exceso de 1. Si desaparecen los pares, dejan
el mismo residuo. Es un ejemplo algebraico de información insuficiente; no
prueba que ambas historias sean físicamente realizables.

Al fijar T, equilibrio e inventario de partículas, el HRG añade la información
que selecciona una población. Para calcular cómo llegó a existir y cómo cambió,
hay que integrar producción, aniquilación y expansión. En una aproximación
homogénea, el término de evolución de antibariones tiene la forma

`dn_antiB/dt + 3 H n_antiB = <σv> (nB_eq n_antiB_eq − nB n_antiB)`.

Este paquete no integra esa ecuación cinética. El cruce tampoco identifica el
primer evento ni el final absoluto de la aniquilación.

Nuestra aproximación y la de la referencia pertenecen a la misma familia de
cálculos y comparten información cosmológica. Hay diferencias: aquí μQ = μS = 0
con inventarios completos; la referencia aplica neutralidad de carga y de
extrañeza, otro inventario y un rendimiento neto central ligeramente distinto.
Por eso la cercanía no se presenta como una nueva observación independiente.

## Métodos y verificaciones

- Masas en reposo, degeneraciones de espín y ocupaciones de cada especie, con
  resonancias de anchura cero. No se ajustan las masas para lograr el acuerdo.
- Inventarios PDG2014/2020/2025 de Thermal-FIST congelados en el commit
  `4086191e952285cd572ba2bbbefb2fdc55401c9b`, comprobados mediante SHA-256.
- Raíz de Brent para resolver μB/T con el rendimiento neto impuesto; segunda
  raíz de Brent para R(T) = 1 en el intervalo 37–40 MeV.
- Sumatorias de Bessel con 96 términos, repetidas con 192.
- Integrales de momento independientes para protones y neutrones: partículas,
  antipartículas, exceso neto y entropía del par, a 50 MeV, 38.2 MeV y el cruce.
- Sensibilidad al valor de η. No se ejecutan pruebas de significancia ni se
  calcula una incertidumbre física total.

Pasaron las 24 comprobaciones registradas. Las verificaciones numéricas
muestran convergencia de la implementación, no eliminan los supuestos físicos.
La curva y los intervalos de raíz se mantienen entre 37 y 50 MeV; no se amplía
este cálculo a temperaturas inferiores con el mismo intervalo de μB/T.

## Ejecución local con PowerShell

La parte matemática ya se ejecutó y verificó localmente en Python. La web se
utilizó para consultar fuentes científicas. PowerShell puede controlar la
misma ejecución sin depender de una interfaz web: verifica los inventarios,
crea un entorno Python local, ejecuta el cálculo y muestra los resultados.

Este entorno de trabajo es Linux y no tiene `pwsh` ni `powershell` disponibles.
Por ello `ejecutar_50MeV.ps1` se **revisó estáticamente, pero no se ejecutó**.
No se atribuye la corrida numérica a PowerShell.

Extraer toda la carpeta y abrir PowerShell dentro de ella. Se requiere Python
3.11 o posterior; el cálculo incluido se verificó con Python 3.12. Primera
corrida, para instalar las dependencias en `.venv`:

```powershell
.\ejecutar_50MeV.ps1 -InstalarDependencias
```

Una vez instaladas las dependencias:

```powershell
.\ejecutar_50MeV.ps1
```

La instalación inicial puede requerir Internet. El cálculo posterior usa los
inventarios incluidos y no consulta páginas web. También puede ejecutarse
`python comparar_50MeV.py` en un entorno que ya tenga las dependencias de
`requirements.txt`.

## Archivos

- `data/resultados_50MeV_y_entorno.csv`: 18 puntos agregados, tres catálogos.
- `data/cruces_por_catalogo.csv`: cruces y comparación con la referencia.
- `data/sensibilidad_eta.csv`: propagación del único dato cosmológico variado.
- `data/especies_PDG2025.csv`: 1329 registros, 443 especies a 50 MeV, 38.2 MeV
  y el cruce calculado, con partículas y antipartículas explícitas.
- `data/curva_R_PDG2025.csv`: valores de la curva.
- `data/resumen.json` y `data/validacion.json`: resultados completos y controles.
- `figures/cruce_50MeV.png` y `.svg`: figura con pie explicativo.
- `comparar_50MeV.py`: código de esta corrida. Los otros scripts aportan las
  funciones del análisis anterior; los archivos de procedencia heredados
  conservan las fuentes originales.
- `provenance_50MeV.json`: procedencia y alcance específico de esta corrida.
- `ejecutar_50MeV.ps1`: ejecución local desde PowerShell, revisada estáticamente.
## Fuentes primarias

Yang, C. T., & Rafelski, J. (2022). Cosmological strangeness abundance.
*Physics Letters B, 827*, 136944. https://doi.org/10.1016/j.physletb.2022.136944

Texto: https://arxiv.org/pdf/2108.01752
El criterio y el valor 38.2 MeV aparecen en el apartado de composición.

Satarov, L. M., Mishustin, I. N., & Greiner, W. (2013). Evolution of antibaryon
abundances in the early universe and in heavy-ion collisions.
*Physical Review C, 88*, 024908. https://doi.org/10.1103/PhysRevC.88.024908

Texto: https://arxiv.org/pdf/1305.4046
Distingue la disminución de abundancias por debajo de unos 50 MeV del
apartamiento del equilibrio. Estos criterios no se intercambian.

Documentación de PowerShell: https://learn.microsoft.com/powershell/
