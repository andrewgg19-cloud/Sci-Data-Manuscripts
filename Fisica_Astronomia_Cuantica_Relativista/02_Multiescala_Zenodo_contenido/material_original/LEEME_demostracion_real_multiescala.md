# Demostración real de capacidad explicativa multiescala

## Resultado en una frase

El método distingue dos situaciones: **no encuentra apoyo suficiente para la
transición cosmológica ensayada en Pantheon+**, pero **sí mejora de forma fuerte
y reproducible la relación masa-radio de exoplanetas mediante regímenes de
escala**, incluso fuera de muestra.

## Prueba 1: control cosmológico

- Datos: Pantheon+, 1,590 filas con `zHD > 0.01`.
- Incertidumbre: matriz oficial `STAT+SYS` completa.
- Prueba: 320 filas reservadas por CID y covarianza condicional.
- Resultado multiescala frente a Lambda-CDM:
  - `Delta BIC = +6.8765` (desfavorable).
  - Ganancia de chi-cuadrada reservada: `0.2032` (materialmente pequeña).
  - Criterio de éxito: **no superado**.

## Prueba 2: exoplanetas

- Datos: 897 planetas transitantes con masa y radio medidos.
- Calidad: sin límites; error relativo máximo de 50 % en masa y 20 % en radio.
- Comparadores: potencia única, polinomio cuadrático y ley multiescala continua
  de tres regímenes.
- Validación: cinco pliegues; cada planeta fue predicho una vez fuera de su
  ajuste.
- Resultado multiescala:
  - `Delta BIC` frente a potencia única: `-654.2718`.
  - `Delta BIC` frente a cuadrático: `-287.2428`.
  - NLL cruzada por planeta: `0.0884`, frente a `0.4511` y `0.2451`.
  - Error mediano fraccional: `15.5 %`, frente a `26.1 %` y `19.2 %`.
  - Criterio de éxito: **superado**.

## Límite principal

La frontera superior es relativamente estable entre pliegues:
`128.0 +/- 21.6 masas terrestres`. La inferior no lo es:
`14.9 +/- 11.8 masas terrestres`. El número de condición del operador
multiescala es `28.49`, por lo que la ganancia predictiva no implica que todos
los parámetros estén determinados con igual robustez.

## Ejecución

```powershell
python demostracion_capacidad_multiescala.py
python demostracion_exoplanetas_multiescala.py
```

Los scripts usan por defecto los archivos de `data/` y regeneran tablas,
figuras y resultados JSON en el mismo directorio.

## Alcance científico

La demostración establece capacidad explicativa, predictiva y selectiva para
un problema físico con regímenes observacionales. No demuestra una teoría del
todo, una cuantización de la gravedad ni que las fronteras planetarias sean
universales. Las leyes rotas masa-radio ya existen en la bibliografía; el
resultado muestra que el formalismo multiescala recupera esa estructura y la
somete a diagnósticos de cierre y estabilidad.
