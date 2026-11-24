# BIG Bell Temporal v5.5 - Resumen

- ventanas: 87
- ventanas_criticas_DG_gt_0_25: 15
- ventanas_confirmadas_por_persistencia: 0
- ventanas_con_perdida_soporte_n_ab_0: 28
- D_G_mediana: 0.0
- D_G_max: 23.450062080935105
- H_mediana: 0.9233051847591044
- aceptados_mediana: 375.0

## Lectura

La serie temporal muestra episodios de sombra finita alta, pero varias ventanas tienen perdida de soporte por celdas aceptadas en cero.
La regla v5.5.1 separa esas ventanas como perdida_de_soporte_expresado y no las cuenta como confirmacion temporal.
Resultado: no hay confirmacion por persistencia tras excluir ventanas degeneradas del conteo de racha.