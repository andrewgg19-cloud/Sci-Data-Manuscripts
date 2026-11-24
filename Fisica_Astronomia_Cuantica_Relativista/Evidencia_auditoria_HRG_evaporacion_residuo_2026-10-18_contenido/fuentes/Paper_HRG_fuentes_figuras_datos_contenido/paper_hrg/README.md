# Reconstrucción del sector barión-antibarión a 50 MeV

Versión concluida del manuscrito: 9 de octubre de 2026. Artículos en español e inglés, a dos columnas, organizados conforme al manual compartido: título, resumen, palabras clave, introducción, métodos, resultados, discusión, conclusiones y referencias.

## Resultado central y alcance

Con PDG2025 y eta=(6.12±0.04)e−10 como entrada cosmológica, a la referencia bibliográfica aproximada de 50 MeV se obtuvieron 2.726089504e30 bariones y 2.717213050e30 antibariones por cm³; el exceso fue 8.876454327e27 cm⁻³. El cociente antibariones/exceso es 306.114688. Los nucleones y sus antipartículas aportaron 95.2176%.

El cruce R=n_antiB/(n_B−n_antiB)=1 se calculó a 38.203738689 MeV, que redondea al hito publicado de 38.2 MeV. Variar sólo eta dentro de su incertidumbre de entrada produjo 38.192814–38.214598 MeV. No es un intervalo de incertidumbre física total.

Las masas de reposo, espín y cargas son propiedades tabuladas; no se midieron firmas espectrales originales. Se reconstruyeron estados de equilibrio condicionados a temperatura, inventario y conservación, con mu_Q=mu_S=0. Esta condición deja carga y extrañeza netas distintas de cero; los balances completos no se resolvieron. No se contó regeneración física ni eventos acumulados, no se obtuvo una historia única y no se establece una nueva observación o mecanismo de bariogénesis.

## Archivos actuales

- `manuscripts/`: artículos finales ES y EN.
- `paper_es.tex`, `paper_en.tex`, `body_*.tex`, `intro_*.tex`, `methods_*.tex`, `results_*.tex`, `discussion_*.tex`, `closing_*.tex`: fuentes del texto final.
- `preamble.tex`, `references.tex`: formato y bibliografía compartidos.
- `table_states_*.tex`, `table_nucleons50_*.tex`, `table_crosscatalogs_*.tex`: tablas generadas de resultados.
- `figures/final_cross_*.pdf` y `.png`: figura final por idioma, PDF vectorial y PNG a 450 dpi. Panel izquierdo: R(T); derecho: temperatura de cruce frente a eta. Las líneas entre los tres puntos de sensibilidad son guías visuales.
- `calculos_50MeV_cruce/`: código Python del cálculo, lanzador PowerShell, entradas fijadas, resultados y controles.
- `data/cosmological_reference.json`: conversión de entradas actuales y propagación de sus incertidumbres.
- `data/final_derived_quantities.json`: cantidades comóviles y cargas netas obtenidas de los resultados por especie.
- `data/manuscript_validation.json`: comprobaciones del cierre editorial y numérico documentado.
- `make_final_assets.py`: genera tablas, figuras y conversiones desde los datos del cálculo.
- `build_manuscripts.py`: compila ambos manuscritos con LaTeX.
- `antecedentes/Paper_HRG_antes_del_cierre.zip`: copia íntegra de la entrega anterior, identificada como antecedente. Sus evaluaciones de 150–40 MeV y de temperatura de transición no son el punto inicial adoptado en este cierre.

## Ejecución en Windows

Lee `calculos_50MeV_cruce/WINDOWS_POWERSHELL.md`. El lanzador `.ps1` comprueba inventarios y llama a Python; la matemática se ejecuta en Python. Los cálculos fueron comprobados en Linux/Python 3.12 y el PowerShell se revisó estáticamente, sin ejecutar Windows. La guía incluye la instalación oficial de PowerShell 7 y Python 3.12, extracción y ejecución local.

## Reproducción en Python y generación de los PDF

Desde `paper_hrg/calculos_50MeV_cruce`:

```bash
python3 -m pip install -r requirements.txt
python3 comparar_50MeV.py
```

Desde la carpeta raíz `paper_hrg`:

```bash
python3 make_final_assets.py
python3 build_manuscripts.py
```

Las versiones de NumPy, SciPy y Matplotlib están fijadas en requirements.txt. Para recompilar el artículo se requiere `pdflatex` y los paquetes declarados en preamble.tex. Los PDF terminados ya están incluidos; ejecutar el cálculo no requiere instalar LaTeX. Se utilizan archivos de Thermal-FIST, no su programa C++.

## Inventario y normalización

La revisión de los catálogos es 4086191e952285cd572ba2bbbefb2fdc55401c9b. Se mantienen las masas nominales, degeneraciones y cargas, con estados de carga y antipartículas separados. Las listas cubren u,d,s y no toda la colección del PDG: PDG2025 tiene 443 especies activas, incluidas 146 bariónicas, 146 antibariónicas y 151 mesónicas. No se añadieron núcleos ni otros sectores.

El cálculo principal conserva 18 estados agregados, 1329 registros por especie de partícula para PDG2025, 24 controles numéricos, tres cruces por catálogo y tres evaluaciones de sensibilidad a eta. La convergencia y las integrales independientes verifican la implementación, sin determinar la exactitud física.

Los rendimientos Y=n/s son adimensionales en unidades naturales; al emplear densidades físicas, s/k_B se expresa en las mismas unidades de volumen. El factor 7.04 relaciona entropía y fotones del presente; no se impone al plasma de 50 MeV. Comparar épocas requiere rendimientos o una misma región comóvil, no volúmenes físicos iguales a ambas temperaturas.

La región que hoy corresponde a 1 m³ contiene un exceso medio de 0.251364831 unidades bariónicas. En ella, a 50 MeV se infieren 77.197831783 bariones y 76.946466951 antibariones, suma 154.144298734. Son cantidades medias normalizadas a una región; no un censo de todo el Universo. H, He y D son una composición primordial equivalente de la densidad media actual a partir de abundancias externas, sin procesamiento estelar o ionización; no son predicciones de nucleosíntesis del HRG.

## Fuentes bibliográficas y estructura

Satarov, Mishustin y Greiner (2013), Physical Review C 88, 024908, DOI 10.1103/PhysRevC.88.024908, sección III, figura 3 y p. 11 del PDF arXiv:1305.4046: referencia aproximada de 50 MeV para la disminución de la proporción de antibariones. Yang y Rafelski (2022), Physics Letters B 827, 136944, DOI 10.1016/j.physletb.2022.136944, p. 3: ventana 50–30 MeV y criterio de cruce de 38.2 MeV. Sus condiciones químicas y entradas no son idénticas a las nuestras; la comparación es de consistencia, sin replicar toda su evolución.

El manual orienta la estructura editorial: Farji-Brener, A. G., y Arroyo-Rodríguez, V. (2025), Manual de redacción científica: cómo escribir manuscritos de forma eficiente y efectiva. UNAM, ISBN 978-607-587-923-9; estructura IMRYD, capítulo 3. Las referencias físicas completas figuran en references.tex. Se conserva la licencia de los catálogos en calculos_50MeV_cruce/catalogs/LICENSE_ThermalFIST.txt.
