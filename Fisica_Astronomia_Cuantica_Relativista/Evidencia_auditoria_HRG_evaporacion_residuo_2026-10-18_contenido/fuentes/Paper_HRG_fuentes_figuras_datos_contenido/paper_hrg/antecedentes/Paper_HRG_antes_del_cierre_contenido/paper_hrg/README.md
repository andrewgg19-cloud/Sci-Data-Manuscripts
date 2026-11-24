# Reconstrucción retrospectiva del sector barión-antibarión

Este paquete contiene el artículo completo en español e inglés, a dos columnas, y todos los datos, figuras y fuentes necesarios para reproducir los cálculos. El objetivo es comprobar si las propiedades de las especies de partícula y la abundancia cosmológica actual permiten reconstruir poblaciones tempranas de bariones y antibariones y contrastarlas con el conocimiento publicado.

Las masas de reposo del inventario HRG ya utilizado se conservaron. La revisión conecta esos cálculos con el exceso bariónico observado mediante una condición inversa explícita. Los resultados propios se distinguen de entradas observacionales, aproximaciones publicadas y controles del inventario. No se establece aquí un descubrimiento físico nuevo.

## Artículos y fuentes

- manuscripts/Destino_Termodinamico_Barion_Antibarion_ES.pdf: artículo completo en español. Se conserva el nombre de archivo de la entrega anterior.
- manuscripts/Baryon_Antibaryon_Thermal_Audit_EN.pdf: versión completa en inglés.
- paper_es.tex y paper_en.tex: entradas de LaTeX.
- body_*.tex, intro_*.tex, methods_*.tex, results_*.tex, discussion_*.tex, closing_*.tex: contenido.
- preamble.tex y references.tex: diseño común y bibliografía.
- table_*.tex: tablas generadas desde los resultados.
- figures/: cinco figuras por idioma, en PDF vectorial y PNG a 450 dpi.

## Reproducción

Se requieren Python, NumPy, SciPy, pandas y Matplotlib. Las versiones utilizadas constan en requirements.txt. Para el PDF se requiere pdflatex con los paquetes declarados en preamble.tex.

Desde la carpeta del paquete:

    python3 -m pip install -r requirements.txt
    python3 reproduce_hrg.py
    python3 reconstruct_populations.py
    python3 infer_early_populations.py
    python3 initial_temperature_check.py
    python3 make_tables.py
    python3 make_figures.py
    python3 build_manuscripts.py

La implementación Python es independiente. Se utilizan listas de partículas de Thermal-FIST, pero no se ejecuta ni se afirma haber ejecutado su programa C++.

## Datos y procedencia

- catalogs/: listas PDG2014, PDG2020 y PDG2025, documentación y licencia originales.
- provenance.json: supuestos del cálculo de entropía, entorno, enlaces, recuentos y SHA-256 de las listas.
- population_provenance.json: procedencia del cálculo numérico y de las conversiones cosmológicas.
- inverse_provenance.json: objetivo retrospectivo, condición inversa, método de solución, interpretación de las propiedades y límites del contraste publicado.
- data/retrospective_inference.csv: 24 estados inferidos, tres listas por ocho temperaturas, con potencial bariónico finito, densidades separadas, exceso, rendimientos y cocientes.
- data/inverse_identifiability.json: rango del mapa neto, dirección nula y cuatro candidatos algebraicos con el mismo exceso.
- data/inverse_validation.json: cierre de la condición inversa, convergencia y cuadratura independiente del exceso nucleónico.
- data/nucleon_literature_comparison.csv: nuestra evaluación del límite nucleónico de Maxwell-Boltzmann asociado a Satarov et al. (2013), comparado con Fermi-Dirac y el HRG total.
- data/initial_temperature_sensitivity.csv: 12 estados, tres listas por cuatro temperaturas de partida.
- data/initial_temperature_reference.json: fuente de la temperatura de transición, interpretación, conversiones, sensibilidad y controles.
- data/particle_densities.csv: control simétrico a potenciales nulos, con densidades, rendimientos y referencia externa neta.
- data/species_densities_PDG2025.csv: 3544 registros del control simétrico, 443 especies de partícula por ocho temperaturas, con antipartículas separadas.
- data/nucleon_densities_PDG2025.csv: protones, neutrones y sus antipartículas en el control simétrico.
- data/cosmological_reference.json: conversiones actuales de eta, temperatura CMB, Yp y D/H, con incertidumbres de entradas.
- data/number_validation.json: controles del número de partículas a potencial nulo.
- data/manuscript_validation.json: número de páginas, extensión de los resúmenes, referencias resueltas y comprobación de texto dentro de los márgenes.
- data/entropy_densities.csv y data/comparison_hrg.csv: entropías y comparación de inventarios.
- data/legacy_reduced_benchmark.csv: ocho valores previos transcritos.
- data/summary_metrics.json y data/numerical_validation.json: estadísticas descriptivas y controles de entropía.

Las listas están fijadas en la revisión de Thermal-FIST:

    4086191e952285cd572ba2bbbefb2fdc55401c9b

Se conservaron masas nominales y asignaciones de espín de los archivos. Se descartaron líneas comentadas y entradas con degeneración cero. Se incluyeron los hadrones del sector de quarks u, d, s; no se añadieron listas separadas de hadrones con quark charm ni núcleos. Las antipartículas se contaron por separado, sin duplicar una degeneración de isoespín ya representada por entradas individuales.

## Qué se infirió

La abundancia actual fija el rendimiento neto de referencia:

    eta = 6.12e-10
    Y_neto = eta/7.04 = 8.693181818181817e-11

A cada temperatura se resolvió:

    (n_B(T,mu_B) - n_antiB(T,mu_B))/s_total(T,mu_B) = Y_neto

Se mantuvieron mu_Q=mu_S=0. La solución utilizó distribuciones térmicas de Bose-Einstein y Fermi-Dirac y el método de Brent; no simulaciones aleatorias ni pruebas estadísticas sobre mediciones. El potencial bariónico permite distinguir la población de partículas y antipartículas. Los coeficientes hiperbólicos evitan perder precisión al restar dos números casi iguales.

La inferencia se condiciona a temperatura especificada, equilibrio ideal, temperatura común, anchos de resonancia nulos, conservación de entropía y conservación del número bariónico neto. No se impuso simultáneamente neutralidad eléctrica y extrañeza neta nula. No se propagaron incertidumbres observacionales ni errores físicos del HRG a las poblaciones inversas; se usaron entradas centrales.

Resultados PDG2025:

    T=150 MeV:
        n_B       = 1.722200330022494e37 cm^-3
        n_antiB   = 1.7222002899129643e37 cm^-3
        n_neto    = 4.0109529921744994e29 cm^-3
        mu_B/T    = 1.1647114399575292e-8
        Y_total   = 0.007465258481507136

    T=40 MeV:
        n_B       = 1.9166350442121484e28 cm^-3
        n_antiB   = 1.4893959522504301e28 cm^-3
        n_neto    = 4.2723909196171825e27 cm^-3
        mu_B/T    = 0.12610021537632665
        Y_total   = 6.930369268097136e-10
        antiB/B   = 0.777088969936194

El rendimiento total disminuyó 7.032288 órdenes. Es una comparación de estados de equilibrio, sin contar eventos acumulados de aniquilación o regeneración. Las densidades físicas n_i(T) y los rendimientos por entropía Y_i(T) son magnitudes distintas. Para obtener un número absoluto se requiere un volumen: N_i=n_i V.

## Temperatura de partida

La referencia de HotQCD, Bazavov et al. (2019), es Tc=156.5±1.5 MeV, DOI 10.1016/j.physletb.2019.05.013. Es una estimación de la transición de QCD mediante cálculos en red, relacionada con la formación de hadrones. No es una medición del inicio universal de aniquilación.

La malla principal conserva 150 MeV para comparar con nuestros cálculos anteriores. Se verificó además la sensibilidad a 150, 155, 156.5 y 158 MeV. A 156.5 MeV (1.8161e12 K), la evaluación inversa ideal-HRG dio:

    n_B       = 2.657499736698768e37 cm^-3
    n_antiB   = 2.6574996879458845e37 cm^-3
    n_total   = 5.314999424644652e37 cm^-3
    n_neto    = 4.875288277852582e29 cm^-3
    Y_total   = 0.009477235750727606

El total físico es 54.3084% mayor que a 150 MeV; el rendimiento aumenta 26.9512%. La proximidad a la transición exige comprobar la precisión física del HRG; este intervalo de sensibilidad no sustituye una ecuación de estado de QCD ni un análisis de errores completo.

## Qué información no recupera el presente por sí solo

El mapa neto [1,-1] tiene rango uno para dos poblaciones desconocidas. Su dirección nula es [1,1]: añadir iguales cantidades a partículas y antipartículas conserva el exceso. Los cuatro candidatos del JSON son ejemplos algebraicos bajo conservación, sin demostrar historias cinéticas factibles ni estados térmicos posibles a la misma temperatura. El equilibrio y la temperatura son información adicional para reconstruir el total.

Las propiedades utilizadas como firmas son masa de reposo, espín, distribución térmica y cargas del catálogo. No se analizaron señales espectrales originales de la época temprana.

## Contraste con lo publicado

Se evaluó el límite nucleónico que sustenta la ecuación (19) de Satarov, Mishustin y Greiner (2013), generalizado a masas distintas de protón y neutrón. Las cifras de nuestro CSV son cálculos propios, no datos tabulados por esos autores ni mediciones. No se reprodujo su evolución cinética con interacciones.

A 150 MeV, otros bariones aportaron 74.4201% del HRG simétrico; a 100 MeV, 44.1293%; a 40 MeV, 1.52546%. La diferencia Maxwell-Boltzmann/Fermi-Dirac de nucleones a 150 MeV fue 0.059156%. Estas comparaciones permiten evaluar el papel del inventario y la distribución.

El control de entropía mantuvo mu_B=mu_Q=mu_S=0. PDG2025 dio f_plasma=0.0845453323656144 a 150 MeV y 1.7970077864332437e-8 a 40 MeV. La referencia reducida representó 73.4281% y 99.8883%, respectivamente. Pearson logarítmico, Spearman y RMSE son descriptores; no validación experimental ni pruebas de hipótesis. Los puntos de temperatura usan entradas fijas y no son réplicas de mediciones.

La referencia reducida procede de García (2026), manuscrito de trabajo v0.9. Sus valores se transcribieron con cuatro cifras significativas; faltan el inventario completo y el código original. Se conserva expresamente ese alcance y no se reconstruye una lista para forzar la concordancia.

## Referencia cosmológica actual

Eta, temperatura CMB, Yp y D/H son entradas externas declaradas. Las conversiones dieron n_b0=(2.514±0.017)e-7 cm^-3 y el equivalente primordial de H=(1.898±0.015)e-7 cm^-3. No son nuevas predicciones independientes ni un censo actual de hidrógeno neutro. Se omitieron procesamiento estelar, ionización, correcciones de enlace y núcleos traza. Las incertidumbres actuales se propagaron a primer orden asumiendo entradas independientes; las salidas comparten entradas y tienen errores correlacionados. La densidad bariónica compilada comparte la referencia CMB, por lo que su concordancia verifica la conversión.

## Estructura editorial y licencias

La organización sigue el manual compartido: objetivo explícito, resumen de 200–300 palabras, palabras clave, introducción, métodos reproducibles, resultados propios, discusión que responde al objetivo, conclusiones y bibliografía.

Farji-Brener, A. G., & Arroyo-Rodríguez, V. (2025). Manual de redacción científica: cómo escribir manuscritos de forma eficiente y efectiva. Universidad Nacional Autónoma de México. ISBN 978-607-587-923-9. Capítulo 3, pp. 23–44; revisión de párrafos y oraciones, pp. 45–54.

El manual orienta la estructura, no la física. Las referencias científicas completas y sus DOI/enlaces figuran en references.tex y en los artículos. La reproducibilidad numérica no sustituye la revisión científica ni establece prioridad. Las listas y documentación de Thermal-FIST conservan su licencia en catalogs/LICENSE_ThermalFIST.txt. No se infiere autorización pública de publicación del artículo o del código independiente.
