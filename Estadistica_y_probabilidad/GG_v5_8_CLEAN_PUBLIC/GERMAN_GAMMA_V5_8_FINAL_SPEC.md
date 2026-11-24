# German Gamma v5.8 - Final Technical Specification

## Estado

German Gamma queda congelado en v5.8.

No se agregan mas modulos, formulas ni nombres operativos. A partir de esta
version, el trabajo debe concentrarse en depuracion, validacion, documentacion y
ejemplos reproducibles.

## Nombre publico recomendado

```text
German Gamma v5.8
Filter-Induced Structure Diagnostic
```

## Proposito

German Gamma es una herramienta exploratoria para estudiar como un horizonte de
observabilidad y un filtro pueden modificar la estructura observable de un
conjunto de datos.

No es un detector de fraude.
No prueba intencion.
No prueba causalidad.
No invalida experimentos por si solo.

## Base formal

Sea:

```text
Omega = dominio total posible
H subset Omega = horizonte observable
Gamma subset H = filtro dentro del horizonte
F subset Gamma = conjunto finalmente analizado
```

El estado natural observable es:

```text
D_N^H = P(X | X in H)
```

El estado filtrado observable es:

```text
D_F = P(X | X in H intersection Gamma)
```

La deformacion inducida por el filtro es:

```text
Delta_HGamma = d(P(X | X in H), P(X | X in H intersection Gamma))
```

## Arquitectura cerrada

```text
1. Horizonte observable
2. Filtro
3. Soporte
4. Sombra 2D / sombra cubica
5. Espejo 2D / espejo cubico
6. Energia residual + entropia
7. Lamina temporal
8. Probabilidad empirica
9. Reversibilidad
```

## Gobierno jerarquico de interpretacion

German Gamma separa generacion de asociaciones y determinacion final.

```text
G  = revisor gramatical
V1 = verificador primario de veracidad
A  = generador de asociaciones
V2 = verificador comparativo de asociaciones
J  = jurado integrador
D  = juez determinador
```

Flujo:

```text
entrada -> G -> V1 -> A -> V2 -> J -> D
```

Procesamiento paralelo:

```text
G, V1, A, V2, S, T, R pueden operar en paralelo;
la determinacion sigue siendo jerarquica.
```

```text
paralelo para procesar;
jerarquico para determinar.
```

Regla:

```text
el modulo de asociaciones no puede emitir conclusion;
el juez no puede exceder la evidencia;
el jurado integra coincidencias, contradicciones e incertidumbre.
```

Regla anti-confabulacion:

```text
el sistema puede rellenar estructura;
no puede rellenar verdad.
```

Toda salida liberada por jerarquia debe portar una etiqueta epistemologica:

```text
dato
calculo
fuente
hipotesis
analogia
ruido_contextual
no_verificado
no_evaluable
vacio
```

Bloqueo:

```text
si falta evidencia -> marcar vacio;
si es inferencia -> marcar hipotesis;
si es comparacion -> marcar analogia;
si es ruido -> marcar ruido_contextual;
si esta verificado -> marcar dato/fuente/calculo.
```

Ninguna salida marcada como `hipotesis`, `analogia`, `ruido_contextual`,
`no_verificado`, `no_evaluable` o `vacio` puede subir como evidencia confirmada.

Compuertas NAND:

```text
NAND(hipotesis, confirmado)
NAND(analogia, evidencia)
NAND(ruido_contextual, prueba)
NAND(no_verificado, conclusion)
NAND(no_evaluable, veredicto)
```

Regla equivalente:

```text
confirmed_with_evidence =
verificado
AND NOT(hipotesis)
AND NOT(analogia)
AND NOT(ruido_contextual)
AND NOT(no_verificado)
AND NOT(no_evaluable)
AND NOT(vacio)
```

Aprendizaje seguro:

```text
el sistema aprende confiabilidad de rutas y modulos;
no aprende verdad sin verificacion.
```

Actualizacion conceptual:

```text
w_m(t+1) = w_m(t) + eta * feedback_m
```

Reglas:

```text
ruta verificada -> peso sube;
ruta bloqueada -> peso baja;
ruta confabulada -> peso baja fuerte;
ruta exploratoria util -> peso sube levemente sin volverse verdad.
```

Niveles de determinacion:

```text
confirmed_with_evidence
bounded_interpretation
exploratory_hypothesis
analogy_only
not_supported
discarded
```

## Universalidad para tareas de complejidad

La arquitectura puede reutilizarse para tareas complejas cuando el problema
puede descomponerse en modulos, procesarse en paralelo, etiquetarse
epistemologicamente, bloquear saltos invalidos, integrarse por jurado,
delimitarse por juez y ajustarse por aprendizaje seguro.

Forma compacta:

```text
Y = Judge(Jury(NAND(Parallel(Decompose(X)))))
```

Con aprendizaje de rutas:

```text
W(t+1) = W(t) + eta * feedback
```

Limite:

```text
universalidad estructural;
no omnisciencia;
no verdad automatica;
no conclusion sin evidencia.
```

## Capa explicativa fisico-matematica

Esta capa no agrega modulos al nucleo v5.8. Organiza analogias y fundamentos
para interpretar el modelo sin convertirlos en afirmaciones fisicas nuevas.

Regla:

```text
el dato no es solo x;
el dato es (t, x_t) dentro de una nube de posibilidades.
```

Lecturas separadas:

```text
cilindro Gamma = despliegue temporal abierto por laminas;
toroide Gamma  = retorno, ciclo y retroalimentacion;
espectro       = firma multidimensional de observacion;
invariante     = patron que sobrevive a transformaciones declaradas.
```

Noether operativo:

```text
simetria preservada bajo transformacion -> candidato a estructura conservada
simetria rota por horizonte/filtro      -> candidato a deformacion inducida
```

Ejemplo estructural:

```text
carbono en diamante y carbono en grafito tienen el mismo elemento,
pero distinta conectividad; por eso muestran propiedades observables distintas.
```

Traduccion al modelo:

```text
mismos nodos + diferentes enlaces -> diferente espectro estructural
```

Limite:

```text
estas analogias no prueban leyes fisicas nuevas;
solo delimitan como leer punto, nube, centro, horizonte, trayectoria,
ruido, simetria, reversibilidad e invariantes.
```

## Descomposicion de fuente de asimetria

Una ruptura de simetria no implica automaticamente sesgo.

Regla:

```text
A_M = A_int + A_H + A_eta
```

donde:

```text
A_M   = asimetria espejo medida
A_int = asimetria intrinseca del sistema
A_H   = asimetria inducida por horizonte/filtro
A_eta = asimetria por ruido, muestreo o inestabilidad de medicion
```

Criterio:

```text
asimetria antes del horizonte  -> posible propiedad interna
asimetria solo despues         -> posible efecto inducido por horizonte
asimetria inestable            -> posible ruido o muestreo
perdida de soporte             -> no evaluable de forma completa
```

Regla conservadora:

```text
German Gamma no debe castigar toda ruptura de simetria;
debe clasificar el origen probable de la ruptura.
```

## Equivalencia transformada y manifestacion

Una diferencia visible no implica ruptura estructural.

Regla:

```text
forma distinta != estructura rota
```

Para una familia de transformaciones:

```text
G in { I, P, T, C, CP, CT, PT, CPT }
```

se define:

```text
A_G(X) = d(K(X), K(G(X)))
```

La estructura se considera candidata a equivalencia transformada si:

```text
exists G such that A_G(X) <= epsilon
```

La ruptura estructural solo se considera candidata si:

```text
for all G, A_G(X) > epsilon
```

Lectura:

```text
lo que parece distinto puede ser la misma estructura bajo otra manifestacion.
```

Limite:

```text
C, P, T y CPT son usados aqui como transformaciones formales declaradas;
no constituyen una prueba fisica de antimateria ni de simetria CPT real salvo
que los datos correspondan a ese dominio fisico.
```

## Ecuaciones maestras de observabilidad

La formulacion consolidada del modelo se resume como:

```text
Gamma(X) = {
  Delta_HGamma,
  Inv,
  H_t,
  R_t,
  C_H,
  gamma_t,
  eta_t,
  A_G,
  L_Gamma,
  R_hidden
}
```

donde:

```text
Delta_HGamma = deformacion por horizonte/filtro
Inv          = invariantes operativos
H_t          = entropia por lamina temporal
R_t          = reversibilidad
C_H          = no-conmutatividad horizonte-espejo
gamma_t      = trayectoria espacio-temporal
eta_t        = ruido como escala de discernimiento
A_G          = asimetria bajo familia de transformaciones
L_Gamma      = momento-angular-like de trayectoria
R_hidden     = residuo estable compatible con componente no modelado
```

Lectura final:

```text
estructura candidata = lo que persiste bajo transformaciones declaradas
dependencia inducida candidata = lo que aparece por horizonte/filtro
componente oculto candidato = residuo estable no explicado por el modelo base
```

## Regla de soporte

Si una celda o region pierde soporte:

```text
raw_evaluable = false
```

No se debe usar `EPS` para forzar un resultado finito.

La regularizacion de Laplace puede reportarse solo como auxiliar:

```text
raw primero
regularizado separado
```

## Indices principales

### Deformacion por filtro

```text
Delta_HGamma = d(D_N^H, D_F)
```

### Sombra cubica

```text
p_abc = n_abc / N_abc
```

```text
I_3 = (p000 * p011 * p101 * p110) /
      (p001 * p010 * p100 * p111)
```

```text
D_3 = |ln(I_3)|
```

### Energia residual-entropia

```text
E_res = ||mu_N - mu_F||^2
```

```text
Delta_S = S_N - S_F
```

```text
R_EH = log(1 + E_res) * |Delta_S|
```

### Lamina temporal

```text
A_T(i) = C_T(i) * log(1 + E_res(i)) * |Delta_S(i)| * [-log(P_i)]
```

### Reversibilidad

```text
X_0, X_1, ..., X_T
```

contra:

```text
X_T, X_{T-1}, ..., X_0
```

La capa de reversibilidad mide diferencias de trayectoria, entropia y
transiciones entre lectura hacia adelante y lectura reversa.

## Lectura correcta

German Gamma puede decir:

```text
hay perdida de soporte;
hay senal compatible con filtrado diferencial;
hay ruptura de simetria bajo el horizonte definido;
hay cambio energia-entropia;
hay una lamina temporal rara bajo permutacion;
hay asimetria de reversibilidad.
```

German Gamma no debe decir:

```text
hay fraude;
hay intencion;
hay causalidad demostrada;
el experimento es invalido;
la realidad absoluta fue medida.
```

## Scripts principales

### v5.5.2 audit-grade

```text
german_gamma_v5_5_2_audit_grade.py
```

Uso:

```powershell
py -3 german_gamma_v5_5_2_audit_grade.py shadow --n00 53 --N00 1143 --n01 79 --N01 1197 --n10 62 --N10 1202 --n11 51 --N11 1204 --bootstrap 10000
```

### v5.6 3D / Hilbert / Laplace

```text
german_gamma_v5_6_3d_hilbert_laplace.py
```

Comandos:

```text
cubic_shadow
cubic_mirror
energy_entropy
laplace_temporal
```

### v5.7 temporal sheet

```text
german_gamma_v5_7_temporal_sheet.py
```

Uso:

```powershell
py -3 german_gamma_v5_7_temporal_sheet.py --input datos_prueba_gamma.xlsx --columns x1,x2,x3 --filter "x1 > 0" --window-size 120 --step 60 --permutations 200
```

### v5.8 reversibility

```text
german_gamma_v5_8_reversibility.py
```

Uso:

```powershell
py -3 german_gamma_v5_8_reversibility.py --input datos_prueba_gamma.xlsx --columns x1,x2,x3 --window-size 120 --step 60
```

## Reglas futuras

Toda idea nueva debe ir a:

```text
FUTURE_WORK.md
```

No entra al nucleo v5.8.

Solo se permite:

```text
depurar
unificar
validar
renombrar con sobriedad
documentar
crear pruebas reproducibles
```

## Frase final

```text
German Gamma v5.8 no intenta reemplazar la estadistica clasica.
Integra herramientas clasicas en una arquitectura de auditoria para estudiar
si un filtro cambia soporte, geometria, entropia, probabilidad temporal y
reversibilidad dentro de un horizonte observable declarado.
```
