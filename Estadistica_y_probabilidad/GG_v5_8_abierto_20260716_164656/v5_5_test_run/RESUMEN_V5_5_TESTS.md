# German-Gamma v5.5 - Test Run Summary

| prueba | tipo | N | tasa | C_H_JS | L1 | costo_bits | delta_H0 | delta_H1 | p_bottleneck_H1 | lectura |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| control_horizonte_espejo | horizonte_espejo | 1200 | 1.0 | 0.0 | 0.0 |  |  |  |  | horizonte_espejo_compatible |
| geometric_horizonte_espejo | horizonte_espejo | 1200 | 0.2816666666666667 | 0.19168566874890952 | 0.7079224194599057 |  |  |  |  | no_conmutatividad_moderada |
| big_bell_horizonte_espejo | horizonte_espejo | 116226 | 0.5001720785366441 | 0.0234321021027657 | 0.17809946949552677 |  |  |  |  | no_conmutatividad_leve |
| control_topologia | topologia | 1200 | 1.0 |  |  | 0.0 | -2 | 0 | 0.8333333333333334 | PASS_O_MODERADO |
| geometric_topologia | topologia | 1200 | 0.2816666666666667 |  |  | 1.8279392542136965 | -81 | 1 | 0.7 | ALERTA_GEOMETRICA |
| ring_broken_topologia | topologia | 1600 | 0.849375 |  |  | 0.23552644900733335 | -4 | 1 | 0.0 | ALERTA_TOPOLOGICA |
| big_bell_topologia | topologia | 116226 | 0.5006022748782545 |  |  | 0.9982632478321138 | 4 | -1 | 0.5333333333333333 | PASS_O_MODERADO |

## Lectura

- Control horizonte-espejo: C_H = 0, compatible.
- Horizonte geometrico: C_H > 0, no conmutatividad moderada.
- BIG Bell horizonte: C_H leve, sin lectura critica automatica.
- Control topologico: no alerta.
- Geometrico topologico: deformacion H0 fuerte sin alerta H1.
- Anillo roto: alerta H1 clara.
- BIG Bell topologico: presion de seleccion moderada sin ruptura H1 significativa.

## Veredicto

La bateria sostiene el comportamiento esperado: el modelo no alerta en controles, detecta deformaciones conocidas y se contiene en datos reales.