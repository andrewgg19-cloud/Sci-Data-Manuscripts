# German Gamma v5.8 - Reversibility Layer

## Objetivo

La capa de reversibilidad pregunta si una trayectoria temporal conserva su
estructura cuando se lee hacia adelante y hacia atras.

No prueba fraude, intencion ni causalidad. Evalua si existe una flecha temporal
medible bajo las variables y ventanas definidas.

## Trayectoria

Sea una trayectoria:

```text
X_0, X_1, ..., X_T
```

La trayectoria reversa es:

```text
X_T, X_{T-1}, ..., X_0
```

## Entropia por ventana

Cada ventana temporal tiene entropia:

```text
S_t = -sum p_t(x) log p_t(x)
```

La flecha entrópica se estima como:

```text
Delta S_t = S_{t+1} - S_t
```

Si los incrementos hacia adelante no se parecen a los incrementos reversos, hay
asimetria temporal.

## Desplazamiento de centroides

Cada ventana tiene un centro:

```text
mu_t = mean(X_t)
```

La longitud de trayectoria se calcula como:

```text
L = sum_t ||mu_{t+1} - mu_t||
```

La asimetria de transicion compara pasos hacia adelante contra pasos reversos.

## Lectura

```text
approximately_reversible_under_selected_features:
la trayectoria no muestra flecha fuerte bajo la representacion elegida.

weak_reversibility_asymmetry:
hay asimetria debil o parcial.

irreversible_trajectory_signal_exploratory:
hay senal exploratoria de flecha temporal estructural.
```

## Cierre del modelo

Con v5.8, German Gamma queda organizado como:

```text
1. Horizonte observable
2. Filtro
3. Soporte
4. Sombra 2D / cubica
5. Espejo 2D / cubico
6. Energia residual + entropia
7. Lamina temporal
8. Probabilidad empirica
9. Reversibilidad
```

La pregunta completa es:

```text
¿Un filtro cambia lo observable, reduce soporte, induce dependencia,
rompe simetria, altera entropia, produce laminas temporales raras
y deja una flecha temporal irreversible?
```

