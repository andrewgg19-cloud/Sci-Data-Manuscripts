# Prueba exploratoria: evaporación y cinética barión-antibarión

Ejecutada el 13 de octubre de 2026 UTC. Esta es una simulación nueva y reducida, no una reproducción completa del HRG-PDG2025 ni de un modelo negro-blanco. No demuestra ni excluye un universo cíclico. No se ha implementado una dinámica cuántica de rebote, ni un universo hijo.

## Pregunta y alcance

Se integra desde un plasma inicialmente a 50 MeV hasta su enfriamiento a 30 MeV. Se pregunta cuánto cambia la entropía, el exceso normalizado y el cruce n_antibariones/exceso=1 al añadir evaporación simétrica de una población homogénea de agujeros negros. La abundancia inicial de esos agujeros negros es una condición hipotética, no un dato observado. Se supone FLRW plano en expansión con plasma y agujeros negros no relativistas, sin término cosmológico relevante en esta ventana. No hay conversión global del Big Bang en un agujero blanco en esta implementación.

## Entradas

- Masa de cada agujero negro al inicio de la integración: M0=1e8 g. No se fija su época de formación; su tiempo restante se calcula desde esta masa.
- Cuatro cocientes iniciales f=rho_BH/rho_plasma: 0, 0.01, 0.1, 1. No confundir con la fracción primordial beta ni con la fracción de emisión bariónica.
- Evaporación: dM/dt=-alpha/M^2; alpha=5.34e25*15.35 g^3/s. Vida restante 4.066578e-4 s. Coeficiente constante, agujeros negros no rotantes, sin acreción, sin remanente, evaporación completa hasta el extremo formal M=0. La aproximación semiclasica deja de ser fiable cerca de Planck; la masa de ese extremo es despreciable para este balance macroscópico, pero esto no describe su física cuántica.
- Toda la energía perdida se deposita instantáneamente en un único baño térmico (f_dep=1): aproximación idealizada que omite pérdidas en gravitones, sectores ocultos y transporte no térmico. No se calculan cascadas de partículas ni emisión bariónica directa. La producción térmica inversa sí está incluida.
- Exceso inicial delta0=8.8765e27 cm^-3 de la auditoría aportada. Su valor no se predice: se conserva exactamente como número neto comóvil por construcción. Q_deltaB=0.
- Baño reducido: fotones, electrones/positrones sin masa, tres sabores neutrino/antineutrino sin masa, muones masivos y piones masivos. Integrales mediante sumas Bessel de 64 términos y spline termodinámico. Se omiten hadrones más pesados en energía/presión; la cinética de pares es un sector de prueba, sin su retroacción energética. Su contribución térmica es pequeña en esta ventana. No se resuelven balances eléctricos, leptónicos ni de extrañeza.
- s(50)/kB=1.01998166e38 cm^-3, 0.1083% menor que el valor deducido del HRG completo del PDF. Por eso Y inicial es 8.70260743e-11, no exactamente 8.69318e-11.
- Producto de equilibrio b0(T)^2=nB_eq*nanti_eq: interpolación PCHIP de log(sqrt(nB*nanti)) con los cinco puntos REDONDEADOS de la auditoría (37, 38.203739, 40, 45, 50 MeV). No se han obtenido los catálogos o el código del suplemento. Se usa cierre Boltzmann con |B|=1; fuera de 37--50 MeV, forma T*K2(938.92/T) empalmada en el extremo. Es una aproximación reducida explícita, no un HRG recalculado. Los cruces de todos los casos se encuentran dentro de los puntos interpolados.
- Tasa de Satarov et al., ec. (9): <sigma v>=(3.5+8.6 sqrt(T/939 MeV)) fm^2*c, aplicada a la densidad total de pares.

## Ecuaciones integradas

Con rho y p como densidades de energía, s en unidades de kB, T en MeV y Q en MeV cm^-3 s^-1:

H^2=(8 pi G/3 c^2)(rho_plasma+rho_BH), convirtiendo MeV a erg.
rho_BH=f*rho_plasma(50)*(M/M0)/a^3.
Q=f*rho_plasma(50)*[-d(M/M0)/dt]/a^3.
drhoplasma/dt+3H(rho_plasma+p_plasma)=Q.
dnanti/dt+3H*nanti=<sigma v>*(b0(T)^2-nanti*(nanti+delta0/a^3)).
Delta(t)=delta0/a^3; nB=nanti+Delta.
d(S/S0)/dt=a^3 Q/(T*s0), integrada independientemente de S=s(T)a^3.

La positividad de H se elige en la rama expansiva. La ausencia de recolapso en esta ejecución es consecuencia del modelo gravitatorio y sus componentes: NO es una prueba independiente contra la hipótesis de rebotes. No se incorpora una ley que pueda generar nuevos agujeros negros o blancos. La igualdad Q_deltaB=0 también impide generar un exceso nuevo por construcción.

## Método y comprobaciones

SciPy solve_ivp, BDF para sistema rígido. Durante evaporación se integra en u=1-M/M0; dt/du=3*tau*(1-u)^2 regulariza la potencia divergente del extremo. Después se integra en N=ln(a) hasta T=30 MeV. Se exportan 1201 muestras por caso. El cruce R=1 se interpola entre muestras: los decimales de salida no son una incertidumbre física.

- Cuatro soluciones convergieron sin densidades antibariónicas negativas.
- Control sin evaporación: S/S0=1.0000000006.
- Balance independiente de entropía: discrepancia relativa máxima menor de 9e-9 para estas tolerancias.
- Se repitió f=1 con tolerancia relativa diez veces menor: cambio relativo en S y Y menor de 5e-9. Esto verifica estabilidad numérica, no exactitud física del modelo.
- El exceso comóvil se impone analíticamente; no se presenta como una conservación emergente comprobada.
- La desviación química máxima del caso f=1 es cercana a 0.68%, localizada en la emisión final idealizada. No es un observable ni una predicción robusta del transporte, que no se resuelve.

## Resultados (precisión de exposición)

| f inicial | S final / S inicial | Y neto final | T cruce (MeV) |
|---:|---:|---:|---:|
|0|1.0000|8.703e-11|38.205|
|0.01|1.0109|8.608e-11|38.202|
|0.1|1.1093|7.845e-11|38.176|
|1|2.0798|4.184e-11|37.973|

Son salidas CONDICIONALES de esta prueba. El valor final se evalúa a 30 MeV, después de evaporar. El cruce ocurre durante la evolución, con distinta fracción evaporada según el caso. No se debe convertir Y final a una nueva densidad física a 50 MeV como si el plasma realmente volviera a esa temperatura. La temperatura final de evaporación del caso f=1 es 35.219 MeV; no vuelve a 50 MeV.

Interpretación: la energía simétrica añadida aumenta la entropía y diluye el exceso normalizado. Las reacciones reconstruyen o eliminan pares conforme cambia el baño, sin crear número bariónico neto. Para predecir el origen del exceso debe añadirse una fuente microfísica justificada. Para estudiar ciclos debe fijarse una dinámica gravitatoria que admita transiciones, conservando los balances; no basta insertar un reinicio manual.

## Reproducir

Python 3.12 o compatible:

    python -m pip install numpy scipy matplotlib
    python simular.py

En Windows con Python 3.12:

    py -3.12 -m pip install numpy scipy matplotlib
    py -3.12 simular.py

Se ejecutó en Linux, no se comprobó la ejecución en Windows. Los resultados JSON incluyen precisión de máquina para auditoría; no debe interpretarse como precisión física. Las versiones del entorno ejecutado están en entorno.json.

## Fuentes

- Archivo del usuario: Baryon_Antibaryon_Thermal_Audit_EN(1).pdf, 9 octubre 2026, tabla 2 y métodos. Entradas redondeadas transcritas en simular.py.
- Satarov, Mishustin y Greiner (2013), https://arxiv.org/abs/1305.4046 ; DOI 10.1103/PhysRevC.88.024908. Ecuaciones de tasas y parametrización (9). No se replica su EOS de volumen excluido.
- Haque et al. (2023), https://arxiv.org/abs/2305.10518 ; DOI 10.1103/PhysRevD.108.063523. Contexto de recalentamiento por evaporación; no se replica su modelo inflacionario.
- Rice y Zhang (2017), https://academic.oup.com/mnras/article/473/4/5385/4443214 . Contexto de pérdida de masa semiclasica.
- Ultrahigh-energy gamma rays and gravitational waves from primordial exotic stellar bubbles (2022), DOI 10.1140/epjc/s10052-022-10395-w, apéndice B: coeficiente 5.34e25 y factor 15.35 usados en esta prueba. No se utiliza su mecanismo de burbujas.
- Yang y Rafelski (2022), https://arxiv.org/abs/2108.01752 ; DOI 10.1016/j.physletb.2022.136944. Referencia térmica, no fuente de evaporación.
- Haggard y Rovelli, https://arxiv.org/abs/1407.0989 . Su geometría de transición NO está implementada.
