# Tambor aritmético primo

Esta construcción realiza un operador diagonal sobre la base
\(e_{p,m}\), usando los primeros 100 primos y \(1\le m\le4\):

\[
H_{\mathrm{pr}}e_{p,m}=m\log p\,e_{p,m}.
\]

Para \(\sigma=1.1>1\), el vector de excitación tiene componentes

\[
(v_\sigma)_{p,m}=\sqrt{\log p}\,p^{-m\sigma/2}.
\]

Su autocorrelación truncada es exactamente

\[
C_{\sigma;P,M}(t)=
\langle v_\sigma,e^{-itH_{\mathrm{pr}}}v_\sigma\rangle
=\sum_{p\le P}\sum_{m\le M}
\frac{\log p}{p^{m\sigma}}e^{-itm\log p}.
\]

El audio reproduce su parte real normalizada. Se aplica la escala uniforme
\(t\mapsto800t\), de modo que

\[
f_{p,m}=\frac{800m\log p}{2\pi}
\]

quede en el intervalo audible. Esta escala cambia la velocidad de reproducción,
pero no los pesos relativos ni la estructura espectral.

## Archivos

- `tambor_aritmetico.wav` y `.mp3`: respuesta sonora de 18 segundos.
- `tambor_aritmetico_operador.npz`: diagonal de \(H_{\mathrm{pr}}\), vector de
  excitación e índices \((p,m)\).
- `modos_del_tambor.csv`: los 400 modos y sus frecuencias.
- `verificacion_autocorrelacion.csv`: comparación entre el producto matricial
  y la suma prima.
- `espectrograma_tambor_aritmetico.png`: representación espectral.
- `construir_tambor_aritmetico.py`: generador reproducible.

El objeto construido es un tambor primo explícito. Sus eigenvalores son
\(m\log p\). Los ceros de zeta aparecen en la continuación meromorfa de la
respuesta completa; este archivo no los identifica automáticamente como
eigenvalores de \(H_{\mathrm{pr}}\).
