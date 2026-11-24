# Actualización de los manuscritos: partitura prima, sonificación y decodificación reproducible

## 1. Marco conceptual que debe incorporarse

La secuencia ordenada de los primos

\[
\mathbb P=(p_1,p_2,p_3,\ldots)
\]

puede tratarse como una **partitura aritmética**. La regla de sonificación es

\[
f_p=f_0\frac{\log p}{\log 2},
\qquad f_0=220\ {\rm Hz},
\]

de modo que \(p=2\) corresponde a 220 Hz y cada primo posterior ocupa una posición frecuencial determinada únicamente por su valor.

La partitura completa, en sentido matemático, es infinita porque existen infinitos primos. Toda grabación es necesariamente un prefijo finito de esa partitura. Por ello, el audio de 10,001 primos constituye una realización finita reproducible del algoritmo, no una enumeración de todos los primos existentes.

Para el prefijo de 10,001 primos:

- \(p_1=2\);
- \(p_{10001}=104743\);
- duración: \(450.045\) s;
- \(f_2=220\) Hz;
- \(f_{104743}=3668.828747\) Hz;
- sin plegado por octavas en la tabla matemática.

El manuscrito v17 ya define el algoritmo general como un mapa de cada primo hacia frecuencia, amplitud y fase. Esta actualización añade una comprobación experimental directa de que la codificación puede recuperarse del WAV finito.

## 2. Nuevo resultado experimental: decodificación del WAV

El WAV original de cinco tonos se procesó sin proporcionar al estimador una lista de frecuencias candidatas.

### Paso 1. Lectura

Se leyó el PCM de 16 bits y, en caso de señal multicanal, se promedió la señal entre canales.

### Paso 2. Segmentación

Los cinco tonos individuales se analizaron en los intervalos declarados:

\[
[0.15,1.85],\ [2.15,3.85],\ [4.15,5.85],\
[6.15,7.85],\ [8.15,9.85]\ {\rm s}.
\]

La mezcla se analizó en \(11.4-18.6\) s.

### Paso 3. Estimación espectral

Se eliminó la media, se aplicó una ventana de Hann y se calculó una FFT real con al menos ocho veces la longitud original mediante relleno de ceros.

Se buscaron automáticamente máximos locales entre 50 y 5000 Hz, reteniendo picos por encima del 10 % del máximo espectral y con separación mínima de 2 Hz.

### Paso 4. Refinamiento

Cada máximo se refinó mediante interpolación parabólica de los tres valores logarítmicos vecinos.

### Paso 5. Decodificación

A cada frecuencia estimada se aplicó

\[
p_{\rm dec}=2^{f/220}.
\]

El entero más cercano se obtuvo solamente después de la estimación.

### Paso 6. Validación independiente

La lista \(\{2,3,5,7,11\}\) se utilizó únicamente al final para comprobar la recuperación.

La mezcla produjo cinco picos sin imponer previamente el número de canales.

### Resultados

El cambio entre dos ventanas de análisis produjo como máximo

\[
\boxed{\Delta f_{\max}=2.208\times10^{-7}\ {\rm Hz}}.
\]

El ajuste simultáneo de cinco sinusoides, utilizando las frecuencias estimadas y no las frecuencias teóricas, produjo

\[
\boxed{\varepsilon_{L^2}=3.515\times10^{-5}}.
\]

Los dos procedimientos recuperaron

\[
\boxed{2,\ 3,\ 5,\ 7,\ 11}.
\]

Cada entero recuperado fue comprobado posteriormente como primo mediante división entera.

## 3. Interpretación del resultado

El resultado establece una propiedad concreta de la representación:

\[
{\rm WAV}
\rightarrow
f_p
\rightarrow
2^{f_p/220}
\rightarrow p.
\]

La estabilidad frente al cambio de ventana y el ajuste temporal independiente muestran que la información frecuencial codificada en la mezcla es recuperable mediante dos procedimientos complementarios.

El resultado se incorpora como una validación de la **codificación y recuperación de canales primos**. No se utiliza como sustituto de la construcción espectral de \(\Xi\), ni como una afirmación independiente sobre la localización de los ceros.

## 4. Texto para incorporar al v17

### Reproducible decoding of logarithmic prime channels

The logarithmic prime encoding was independently recovered from the original PCM WAV file without supplying the estimator with a candidate-frequency list. The signal was mean-centered, Hann-windowed, and transformed using a real FFT with at least eightfold zero padding. Local maxima between 50 and 5000 Hz were detected automatically using a 10% relative-amplitude threshold and a minimum separation of 2 Hz. Each retained maximum was refined by parabolic interpolation of the logarithms of the three neighboring spectral amplitudes.

The encoded integer was recovered through

\[
p_{\rm dec}=2^{f/220}.
\]

The expected sequence \(\{2,3,5,7,11\}\) was used only after decoding as an independent validation step. In the mixed section, five spectral peaks were recovered without imposing the number of channels in advance.

Changing the analysis window altered the estimated frequencies by at most

\[
2.208\times10^{-7}\ {\rm Hz}.
\]

A simultaneous least-squares fit of five sinusoids using the estimated frequencies gave a relative \(L^2\) residual of

\[
3.515\times10^{-5}.
\]

Both spectral analyses recovered the same sequence \(2,3,5,7,11\), and the recovered integers were independently verified as prime.

This experiment validates the recoverability and numerical stability of the logarithmic prime-channel encoding in a finite mixed signal. It constitutes a signal-level validation of the arithmetic channel representation and is kept logically separate from the spectral realization of the completed Riemann function.

## 5. Texto para Operadores de canales primos — compacto ES

### Decodificación experimental de los canales primos

Añadir después de la sección de sonificación:

> La codificación logarítmica se sometió además a una prueba de recuperación sobre el WAV PCM original. El estimador no recibió una lista de frecuencias candidatas. Se aplicó ventana de Hann, FFT con relleno de ceros de al menos ocho veces la longitud original, detección automática de máximos entre 50 y 5000 Hz, umbral relativo del 10 % y refinamiento parabólico sobre tres valores logarítmicos vecinos. La transformación inversa \(p=2^{f/220}\) se aplicó únicamente después de estimar las frecuencias.
>
> En la mezcla se recuperaron cinco picos sin imponer previamente el número de canales. El cambio de ventana modificó las frecuencias estimadas en un máximo de \(2.208\times10^{-7}\) Hz. El ajuste temporal simultáneo de cinco sinusoides, utilizando las frecuencias estimadas, produjo un residuo relativo \(L^2=3.515\times10^{-5}\). Ambos análisis recuperaron \(2,3,5,7,11\), y los enteros recuperados fueron verificados independientemente como primos.
>
> Este resultado añade una validación directa de la codificación y recuperación de los canales \(p\mapsto\log p\) en una señal finita.

## 6. Texto para Hamiltoniano primo y localización coherente

Añadir a “Resultados numéricos reproducibles”:

> **Decodificación experimental del canal primo.** La representación frecuencial \(f_p=220\log(p)/\log 2\) fue recuperada del WAV original mediante detección espectral ciega a la lista de frecuencias candidatas. La estimación utilizó ventana de Hann, FFT con relleno de ceros, interpolación parabólica y umbral relativo del 10 %. La inversión \(p=2^{f/220}\) recuperó los cinco enteros codificados. El análisis en una segunda ventana cambió las frecuencias como máximo \(2.208\times10^{-7}\) Hz. Un ajuste temporal independiente de cinco sinusoides produjo un residuo relativo \(L^2=3.515\times10^{-5}\). El resultado conecta experimentalmente el nivel \(m\log p\) del Hamiltoniano con su representación audible y su recuperación inversa.

## 7. Pie de figura común

**Figura X. Recuperación reproducible de canales primos logarítmicos.** La señal WAV mezclada contiene cinco canales codificados mediante \(f_p=220\log(p)/\log(2)\). Los máximos espectrales se detectan sin proporcionar una lista de frecuencias candidatas. La transformación inversa \(p=2^{f/220}\) recupera \(2,3,5,7,11\). La repetición con una segunda ventana modifica las frecuencias en un máximo de \(2.208\times10^{-7}\) Hz. Un ajuste temporal independiente de las cinco componentes, utilizando las frecuencias estimadas, produce un residuo relativo \(L^2=3.515\times10^{-5}\).

## 8. Material reproducible

Se generó además una realización audible finita de los primeros 10,001 primos siguiendo la regla logarítmica, con 45 ms por canal y sin plegado por octavas:

- `partitura_10001_primos_logaritmica.wav`
- `partitura_10001_primos_logaritmica.csv`
- `partitura_10001_primos_logaritmica.json`

Se generó también un extracto de 100 canales para escucha inmediata:

- `partitura_primos_primeros_100_excerpt.wav`

El WAV de 10,001 canales tiene exactamente 450.045 s, desde 220 Hz para \(p=2\) hasta 3668.828747 Hz para \(p=104743\).

