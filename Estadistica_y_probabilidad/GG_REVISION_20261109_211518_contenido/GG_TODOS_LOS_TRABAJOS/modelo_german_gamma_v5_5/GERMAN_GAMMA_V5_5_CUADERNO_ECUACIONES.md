# German-Gamma v5.5 - Cuaderno De Ecuaciones Y Definiciones

Autor conceptual: Andres German Garcia

Fecha de fijacion: 2026-07-15

Uso: referencia tecnica separada para conservar ecuaciones, simbolos y
definiciones del nucleo German-Gamma v5.5.

---

## 0. Cadena Epistemica General

### Ecuacion / Flujo

```text
fenomeno -> horizonte observable -> filtro Gamma -> medida inducida -> trayectoria -> interpretacion
```

### Definicion

La observacion no se modela como captura directa, sino como una cadena de
operaciones que hacen visible una parte del fenomeno.

### Lectura

El dato observado no se interpreta solo por su valor final, sino por la cadena
que lo hizo observable.

### Estado

Nucleo v5.5.

---

## 1. Estado Padre

### Ecuacion

```text
(Omega, F, P)
```

### Definicion

Espacio probabilistico completo antes de aplicar horizonte, filtro o regla de
seleccion.

### Simbolos

```text
Omega = espacio de estados posibles
F     = familia de eventos observables
P     = medida de probabilidad sobre Omega
```

### Lectura

El Estado Padre representa el soporte probabilistico de referencia.

### Estado

Nucleo v5.5.

---

## 2. Horizonte Observable

### Ecuacion

```text
Pi_H: Omega -> Omega_H
```

### Definicion

Operador que delimita la informacion accesible al observador bajo un horizonte
H.

### Simbolos

```text
Pi_H    = operador de horizonte
Omega_H = subconjunto o proyeccion accesible de Omega
H       = condicion de observabilidad
```

### Lectura

No todo el Estado Padre esta disponible para la auditoria. Parte de la
deformacion puede provenir del horizonte observable, no del filtro.

### Estado

Nucleo v5.5.

---

## 3. Operador Gamma

### Ecuacion

```text
Gamma: Omega_H -> {0,1}
```

### Definicion

Regla de seleccion, filtro, ventana, umbral o criterio de aceptacion aplicado
sobre lo observable.

### Simbolos

```text
Gamma(omega) = 1 si el evento sobrevive
Gamma(omega) = 0 si el evento queda fuera
```

### Lectura

Gamma no solo reduce datos; define que parte de lo observable entra al
resultado.

### Estado

Nucleo v5.5.

---

## 4. Medida Inducida

### Ecuacion

```text
P_Gamma(A) = P(A | Gamma = 1)
```

Si:

```text
P(Gamma = 1) > 0
```

entonces:

```text
P_Gamma(A) = P(A intersect {Gamma = 1}) / P(Gamma = 1)
```

### Definicion

Distribucion resultante despues de condicionar el Estado Padre u horizonte
observable por la regla de seleccion Gamma.

### Lectura

El resultado filtrado no es una muestra menor sin mas. Es una medida inducida.

### Estado

Nucleo v5.5.

---

## 5. Derivada De Radon-Nikodym De La Medida Inducida

### Ecuacion

```text
dP_Gamma/dP (omega) = 1_Gamma(omega) / P(Gamma = 1)
```

### Definicion

Forma de expresar como cambia la densidad de la medida al condicionar por
Gamma.

### Simbolos

```text
1_Gamma(omega) = 1 si Gamma(omega)=1; 0 en caso contrario
```

### Lectura

El filtro redistribuye la medida sobre los eventos sobrevivientes.

### Estado

Nucleo formal. Requiere explicacion cuidadosa en paper.

---

## 6. Operador Espejo

### Ecuacion

```text
M: Omega -> Omega
```

### Definicion

Transformacion de contraste, reflejo, simetria o control estructural usada para
evaluar estabilidad de una lectura bajo transformacion.

### Lectura

El espejo deja de ser metafora cuando se define como transformacion computable.

### Estado

Nucleo v5.5, pendiente de implementacion general.

---

## 7. Conmutacion Horizonte-Espejo

### Pregunta Formal

```text
M o Pi_H = Pi_H o M ?
```

### Medida De No Conmutatividad

```text
C_H = D( M(Pi_H(Omega)), Pi_H(M(Omega)) )
```

### Definicion

Prueba para evaluar si el horizonte observable introduce asimetria antes de que
actue el filtro Gamma.

### Lectura

```text
C_H bajo  -> la simetria es estable bajo el horizonte
C_H alto  -> el horizonte introduce asimetria observacional
```

### Estado

Nucleo teorico v5.5. Falta modulo computacional especifico.

---

## 8. Sombra Geometrica 2x2

### Tasas De Supervivencia Local

```text
P_00 = P(Gamma = 1 | 0,0)
P_01 = P(Gamma = 1 | 0,1)
P_10 = P(Gamma = 1 | 1,0)
P_11 = P(Gamma = 1 | 1,1)
```

### Invariante De Sombra

```text
I_S = (P_00 * P_11) / (P_01 * P_10)
```

### Distancia De Sombra

```text
D_G = |ln(I_S)|
```

### Definicion

Mide si la aceptacion entre celdas binarias es proporcional o presenta seleccion
diferencial.

### Lectura

```text
I_S ~= 1 -> proporcionalidad local
I_S != 1 -> sombra geometrica compatible con seleccion diferencial
D_G alto -> mayor distancia de proporcionalidad
```

### Estado

Implementado en `auditoria_german_gamma_sombra.py`.

---

## 9. Entropia Expresada

### Ecuacion

```text
H(R_t) = - sum_i p_i(t) ln p_i(t)
```

Con convencion:

```text
0 ln 0 = 0
```

### Entropia Normalizada

```text
H*(R_t) = H(R_t) / ln(m)
```

### Definicion

Mide la diversidad informacional expresada en la ventana temporal t.

### Lectura

```text
H* cercano a 1 -> expresion distribuida
H* cercano a 0 -> expresion concentrada
```

### Estado

Implementado en modo temporal del script de sombra.

---

## 10. Movimiento Temporal

### Sombra Por Ventana

```text
D_G(t)
```

### Entropia Por Ventana

```text
H(t)
```

### Cambio De Sombra

```text
Delta D_G(t) = D_G(t) - D_G(t-1)
```

### Cambio De Entropia

```text
Delta H(t) = H(t) - H(t-1)
```

### Definicion

La trayectoria temporal mide si una senal aparece, desaparece, se estabiliza o
se amplifica.

### Lectura

```text
Fotografia = una medicion aislada
Pelicula   = secuencia de deformaciones
```

### Estado

Implementado en modo temporal.

---

## 11. Apelacion Temporal

### Regla

```text
D_G(t) > D_c durante k ventanas consecutivas
```

### Definicion

Criterio para evitar confirmar una deformacion por un unico cruce de umbral.

### Estados Operativos

```text
sin_persistencia_critica
senal_en_apelacion
confirmada_por_persistencia
```

### Lectura

El tiempo funciona como instancia de apelacion. Una senal debe sostenerse para
ser tratada como persistente.

### Estado

Implementado en modo temporal.

---

## 12. Divergencia Jensen-Shannon

### Ecuacion

```text
M_PQ = (P + Q) / 2
```

```text
D_JS(P,Q) = 1/2 D_KL(P || M_PQ) + 1/2 D_KL(Q || M_PQ)
```

Con logaritmo base 2:

```text
D_JS(P,Q) in [0,1]
```

### Definicion

Distancia informacional simetrica y acotada entre dos distribuciones.

### Lectura

Conviene como metrica principal de deformacion entre medidas porque es
interpretable y no explota como KL ante perdida de soporte.

### Estado

Recomendado para modulo general de medida inducida.

---

## 13. Divergencia Kullback-Leibler

### Ecuacion

```text
D_KL(P || Q) = sum_i P_i ln(P_i / Q_i)
```

### Definicion

Mide sorpresa o divergencia informacional al representar P usando Q.

### Lectura

Si Q_i = 0 donde P_i > 0, puede tender a infinito. En German-Gamma esto puede
leerse como perdida de soporte, no como error automatico.

### Estado

Usar con cautela. Complementaria a Jensen-Shannon.

---

## 14. Costo De Seleccion

### Ecuacion

```text
C_bits = log2(N_total / N_post)
```

### Definicion

Indicador simple de presion de seleccion por perdida de muestra.

### Lectura

No es informacion mutua exacta. Es un costo descriptivo de supervivencia.

### Estado

Implementado en German Gamma v5.3/v5.4.

---

## 15. Clon Neutro

### Notacion

```text
N_Gamma*
```

### Definicion

Control contrafactual comparable al estado inducido, construido para preservar
restricciones relevantes pero neutralizar la composicion especifica del filtro
real.

### Pregunta Operativa

```text
La estructura observada aparece tambien bajo una seleccion neutral comparable?
```

### Estado

Nucleo metodologico. Implementacion separada.

---

## 16. Frontera Informacional

### Pregunta

```text
Existe B subset Omega tal que error(firma(B), firma(Omega)) < epsilon?
```

### Definicion

Hipotesis futura: un subconjunto frontera puede preservar la firma relevante de
deformacion del sistema.

### Lectura

No debe presentarse todavia como holografia. Es una posible propiedad de
compresion informacional.

### Estado

Extension futura.

---

## 17. Nucleo Actual Del Modelo

```text
1. Estado Padre: (Omega, F, P)
2. Horizonte Observable: Pi_H
3. Filtro: Gamma
4. Medida inducida: P_Gamma
5. Espejo: M
6. No conmutatividad: C_H
7. Sombra geometrica: D_G
8. Entropia expresada: H(t)
9. Movimiento temporal: Delta D_G(t), Delta H(t)
10. Apelacion temporal: persistencia durante k ventanas
```

---

## 18. Frase De Control

```text
La analogia orienta; la metrica define.
```

### Definicion

Una idea solo entra al nucleo si puede expresarse como objeto, operador,
metrica, prueba o criterio verificable.
