# German-Gamma v5.5 - Definicion Matematica Formal

Autor conceptual: Andres German Garcia

Fecha de fijacion: 2026-07-15

## Criterio De Escritura

Esta definicion no usa metaforas como fundamento. Las palabras "horizonte",
"espejo", "sombra" y "apelacion" son nombres operacionales. Cada una debe
corresponder a un operador, una funcion, una metrica o una regla formal.

Forma estricta:

```text
concepto valido <=> existe formula computable o condicion verificable
```

## Definicion 1. Sistema German-Gamma

Un sistema German-Gamma es una tupla:

```text
GG = (Omega, F, P, H, Pi_H, Gamma, M, D, Phi, T, A)
```

donde:

```text
(Omega, F, P) = espacio probabilistico padre
H             = horizonte de observacion
Pi_H          = operador de horizonte observable
Gamma         = operador de seleccion
M             = operador espejo o transformacion de simetria
D             = funcion de distancia o divergencia entre medidas/representaciones
Phi           = conjunto de metricas de deformacion
T             = indice temporal o familia de ventanas
A             = regla de apelacion temporal
```

German-Gamma audita la cadena:

```text
Omega -> Pi_H(Omega) -> Gamma(Pi_H(Omega)) -> P_Gamma -> Phi(P_Gamma) -> A
```

Forma funcional:

```text
GG_t = A_k( Phi_t( P(. | Gamma_t = 1, H_t) ), C_H(t), N_t* )
```

donde:

```text
P(. | Gamma_t = 1, H_t) = medida inducida observada en la ventana t
Phi_t                    = vector de metricas calculadas en t
C_H(t)                   = error de conmutacion horizonte-espejo en t
N_t*                     = clon neutro de control en t
A_k                      = regla temporal con persistencia k
```

---

## 1. Estado Padre

Sea:

```text
(Omega, F, P)
```

un espacio de probabilidad, donde Omega es el conjunto de estados posibles, F
es una familia de eventos y P es una medida de probabilidad.

El Estado Padre es la referencia probabilistica antes de observacion parcial,
seleccion o interpretacion.

---

## 2. Horizonte Observable

Sea H una condicion de observabilidad. Definimos:

```text
Pi_H: Omega -> Omega_H
```

donde Omega_H es el dominio accesible bajo H.

Si H se representa como funcion indicadora:

```text
H: Omega -> {0,1}
```

entonces:

```text
Omega_H = {omega in Omega : H(omega) = 1}
```

y la medida condicionada por horizonte es:

```text
P_H(A) = P(A | H = 1)
```

es decir:

```text
P_H(A) = P(A intersect {H = 1}) / P(H = 1)
```

si:

```text
P(H = 1) > 0
```

### Horizonte Total Identidad

El horizonte total no se define como ausencia de condicion, sino como condicion
identidad sobre una coordenada valida:

```text
H_0(x) := x_j == x_j
```

En computacion esta forma es util porque:

```text
NaN != NaN
```

Por tanto:

```text
Pi_H0(X) = {x_i in X : x_{ij} == x_{ij}}
```

Si no hay valores perdidos en la coordenada elegida:

```text
Pi_H0(X) = X
```

Este horizonte debe producir:

```text
C_H(X) = 0
```

cuando se compara contra el mismo dominio y la misma transformacion.

El operador Pi_H representa limites de acceso, resolucion, ventana temporal,
instrumento, disponibilidad o cualquier restriccion previa a la seleccion.

---

## 3. Operador De Seleccion

Sea:

```text
Gamma: Omega_H -> {0,1}
```

un operador binario de seleccion, donde:

```text
Gamma(omega) = 1  si omega sobrevive al filtro
Gamma(omega) = 0  si omega no entra al resultado
```

Se exige:

```text
P(Gamma = 1) > 0
```

para definir la medida inducida.

---

## 4. Medida Inducida

La medida inducida por Gamma se define como:

```text
P_Gamma(A) = P(A | Gamma = 1)
```

Con horizonte previo, la medida inducida completa es:

```text
P_{H,Gamma}(A) = P(A | H = 1, Gamma = 1)
```

equivalentemente:

```text
P_{H,Gamma}(A) =
P(A intersect {H = 1} intersect {Gamma = 1}) /
P({H = 1} intersect {Gamma = 1})
```

si:

```text
P(H = 1, Gamma = 1) > 0
```

equivalentemente:

```text
P_Gamma(A) = P(A intersect {Gamma = 1}) / P(Gamma = 1)
```

para todo evento A en F restringido al dominio observable.

Si P_Gamma es absolutamente continua respecto a P, entonces:

```text
dP_Gamma/dP (omega) = 1_Gamma(omega) / P(Gamma = 1)
```

Lectura formal:

```text
Gamma no solo reduce cardinalidad; induce una nueva medida.
```

Con horizonte y seleccion:

```text
dP_{H,Gamma}/dP (omega) =
1_H(omega) 1_Gamma(omega) / P(H = 1, Gamma = 1)
```

cuando la continuidad absoluta lo permite.

---

## 5. Operador Espejo Y Horizonte

Sea:

```text
M: Omega -> Omega
```

una transformacion estructural, espejo, contraste o simetria.

Para que M sea admisible en German-Gamma debe preservar dominio medible:

```text
M^{-1}(A) in F  para todo A in F
```

Si M actua sobre datos como transformacion matricial:

```text
M_X: X -> X'
```

entonces debe definirse explicitamente:

```text
X' = M_X(X)
```

No se admite un "espejo" sin transformacion especificada.

La estabilidad del horizonte bajo M se evalua mediante:

```text
C_H = D( M(Pi_H(Omega)), Pi_H(M(Omega)) )
```

En datos finitos, si X es la matriz de observaciones:

```text
C_H(X) = D( M_X( Pi_H(X) ), Pi_H( M_X(X) ) )
```

Si D es Jensen-Shannon sobre histogramas/probabilidades:

```text
C_H(X) = D_JS( Law(M_X(Pi_H(X))), Law(Pi_H(M_X(X))) )
```

Interpretacion:

```text
C_H = 0      -> M y Pi_H conmutan bajo D
C_H > 0      -> el horizonte introduce asimetria observacional
C_H alto     -> la deformacion puede originarse antes de Gamma
```

Esta prueba separa:

```text
deformacion por horizonte
deformacion por seleccion
deformacion por interpretacion
```

---

## 6. Vector De Deformacion

Definimos el vector de deformacion German-Gamma:

```text
Phi_t = (C_H(t), D_G(t), H*(t), C_bits(t), D_JS(t), B_t)
```

donde:

```text
C_H(t)      = no conmutatividad horizonte-espejo
D_G(t)      = distancia de sombra geometrica
H*(t)       = entropia expresada normalizada
C_bits(t)   = costo de seleccion
D_JS(t)     = divergencia Jensen-Shannon entre referencia y medida inducida
B_t         = indicadores topologicos o estructurales adicionales
```

No todas las componentes deben existir en cada auditoria. El sistema debe
reportar explicitamente cuales fueron calculadas.

Norma compuesta opcional:

```text
Omega_GG(t) =
w_1 C_H*(t) +
w_2 D_G*(t) +
w_3 (1 - H*(t)) +
w_4 C_bits*(t) +
w_5 D_JS*(t) +
w_6 B*(t)
```

con:

```text
sum_i w_i = 1
w_i >= 0
X*(t) in [0,1]
```

Regla:

```text
los pesos w_i deben fijarse antes del analisis
```

---

## 7. Sombra Geometrica

Para una estructura binaria 2x2, definimos:

```text
P_ab = P(Gamma = 1 | a,b)
```

con:

```text
a,b in {0,1}
```

El invariante de sombra local es:

```text
I_S = (P_00 P_11) / (P_01 P_10)
```

y la distancia de sombra:

```text
D_G = |ln(I_S)|
```

Con conteos:

```text
P_ab = n_ab / N_ab
```

por tanto:

```text
I_S =
(n_00/N_00)(n_11/N_11) /
((n_01/N_01)(n_10/N_10))
```

Forma logaritmica:

```text
ln(I_S) =
ln(P_00) + ln(P_11) - ln(P_01) - ln(P_10)
```

Esta forma es comparable a una interaccion log-lineal en tabla 2x2.

Interpretacion:

```text
D_G ~= 0  -> proporcionalidad local
D_G > 0   -> seleccion diferencial entre celdas
```

---

## 8. Entropia Expresada

Sea R_t la distribucion expresada en la ventana t. Definimos:

```text
H(R_t) = - sum_i p_i(t) ln p_i(t)
```

con:

```text
0 ln 0 = 0
```

La entropia normalizada es:

```text
H*(R_t) = H(R_t) / ln(m)
```

donde m es el numero de categorias o celdas consideradas.

En tabla 2x2:

```text
p_00(t) = n_00(t) / N_exp(t)
p_01(t) = n_01(t) / N_exp(t)
p_10(t) = n_10(t) / N_exp(t)
p_11(t) = n_11(t) / N_exp(t)
```

con:

```text
N_exp(t) = n_00(t) + n_01(t) + n_10(t) + n_11(t)
```

y:

```text
H*(t) =
- [sum_{a,b} p_ab(t) ln p_ab(t)] / ln(4)
```

---

## 9. Movimiento Temporal

Para una secuencia de ventanas:

```text
t = 1, 2, ..., T
```

se define:

```text
Delta D_G(t) = D_G(t) - D_G(t-1)
Delta H*(t)  = H*(t) - H*(t-1)
```

La informacion relevante no reside solo en el valor puntual, sino en la
trayectoria de deformacion.

---

## 10. Apelacion Temporal

Sea D_c un umbral critico y k un numero de ventanas consecutivas requerido.

La regla de apelacion temporal es:

```text
A_t =
1 si D_G(t-i) > D_c para todo i = 0,...,k-1
0 en caso contrario
```

Forma con vector de indicadores:

```text
Z_t = 1{D_G(t) > D_c}
```

Racha critica:

```text
R_t =
Z_t (R_{t-1} + 1)
```

si Z_t = 1, y:

```text
R_t = 0
```

si Z_t = 0.

Confirmacion:

```text
A_t = 1{R_t >= k}
```

La racha critica solo puede acumularse en ventanas con sombra finita evaluable.
Las ventanas con perdida de soporte no cuentan como confirmacion temporal.

Estados operativos:

```text
sin_persistencia_critica
senal_en_apelacion
confirmada_por_persistencia
```

Lectura:

```text
una senal aislada no basta para dictaminar reorganizacion persistente.
```

---

## 11. Divergencia Jensen-Shannon

Para dos distribuciones P y Q:

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

En German-Gamma se recomienda para comparar medidas inducidas contra controles
o referencias por ser simetrica y acotada.

---

## 12. Costo De Seleccion

Si N_total es el numero de observaciones antes de Gamma y N_post es el numero
de observaciones sobrevivientes:

```text
C_bits = log2(N_total / N_post)
```

Lectura:

```text
C_bits mide presion descriptiva de seleccion.
No es informacion mutua exacta.
```

---

## 13. Clon Neutro

Un clon neutro es una medida o muestra contrafactual:

```text
N_Gamma*
```

construida para conservar restricciones comparables al sistema observado, pero
neutralizar la composicion especifica atribuida al filtro real.

Pregunta:

```text
La firma Phi(P_Gamma) aparece tambien en Phi(N_Gamma*)?
```

Si no aparece, la firma es compatible con deformacion inducida por Gamma o por
su cadena observacional.

Prueba con clones:

```text
Z_Phi =
( Phi(P_{H,Gamma}) - E[Phi(N_Gamma*)] ) /
sd(Phi(N_Gamma*))
```

Percentil empirico:

```text
q_Phi =
Pr( Phi(N_Gamma*) <= Phi(P_{H,Gamma}) )
```

Lectura:

```text
|Z_Phi| alto o q_Phi extremo -> firma poco compatible con clon neutro
```

---

## 14. Criterio De Lectura

Un resultado German-Gamma debe reportarse en tres niveles:

```text
1. Magnitud: cuanto cambia la medida o estructura
2. Origen probable: horizonte, filtro, trayectoria o control
3. Estado epistemico: compatible, en apelacion, persistente o no evaluable
```

Regla de seguridad:

```text
German-Gamma detecta deformacion compatible con seleccion u horizonte.
No prueba por si solo fraude, intencion ni invalidez.
```

---

## 15. Perdida De Soporte

Para una tabla 2x2 temporal, sea:

```text
N_ab(t) = total de eventos disponibles en la celda (a,b)
n_ab(t) = eventos sobrevivientes Gamma=1 en la celda (a,b)
```

Definimos:

```text
s_N(t) = min_{a,b} N_ab(t)
s_n(t) = min_{a,b} n_ab(t)
```

Estados de soporte:

```text
soporte_completo              si s_N(t) > 0 y s_n(t) > 0
perdida_soporte_expresado     si s_N(t) > 0 y s_n(t) = 0
no_evaluable_soporte_total    si s_N(t) = 0
```

Regla:

```text
D_G(t) solo alimenta apelacion temporal si soporte_estado(t) = soporte_completo
```

Si:

```text
soporte_estado(t) = perdida_soporte_expresado
```

entonces la ventana se reporta como perdida de soporte expresado, no como
confirmacion de sombra finita persistente.

Lectura:

```text
La explosion de D_G por n_ab = 0 es una senal de soporte perdido.
No debe mezclarse con una sombra finita fuerte.
```

---

## 16. Definicion Compacta Final

German-Gamma v5.5 es un marco matematico-operacional que, dado un espacio
probabilistico padre, un horizonte observable y un operador de seleccion,
evalua si la medida inducida que produce el resultado observable conserva o
deforma la estructura esperada bajo transformaciones, controles y trayectoria
temporal.

Forma minima:

```text
GG(P) = A( Phi( P_Gamma ), Phi( N_Gamma* ), C_H )
```

donde:

```text
P_Gamma = P(. | Gamma = 1)
C_H     = D( M(Pi_H(Omega)), Pi_H(M(Omega)) )
Phi     = vector de deformacion
A       = regla de apelacion temporal
```

Frase de cierre:

```text
German-Gamma no audita solo el dato; audita la cadena que hizo visible al dato.
```

---

## 17. Definicion Formal En Una Linea

```text
GG_t(P) =
A_k[
  Phi_t(
    P(. | H_t = 1, Gamma_t = 1)
  ),
  D( M(Pi_{H_t}(Omega)), Pi_{H_t}(M(Omega)) ),
  N_t*
]
```

con:

```text
Phi_t = (D_G(t), H*(t), C_bits(t), D_JS(t), B_t)
```

y:

```text
D_G(t) = |ln( (P_00(t)P_11(t)) / (P_01(t)P_10(t)) )|
```

Esta es la forma matematica minima de German-Gamma v5.5.
