# Bell Audit Bundle

Fecha de armado: 2026-07-27

Contenido incluido en este paquete:

1. `MASTER_PAPER.txt`
   - Marco maestro `Induced Dependence`.

2. `BELL_DERIVED_PAPER.md`
   - Version derivada para sistemas tipo Bell.
   - Incluye:
     - caso auditado de Hensen et al. 2015,
     - modelo operativo,
     - algoritmo de auditoria,
     - Taylor,
     - Monte Carlo,
     - Kalman,
     - complejidad tipo Kolmogorov.

3. `hensen2015_audit_complete.py`
   - Script autocontenido de auditoria sobre el dataset abierto oficial de Hensen 2015.
   - Reproduce:
     - baseline CHSH,
     - sensibilidad tipo Taylor,
     - Monte Carlo bootstrap,
     - Monte Carlo sobre ventana `event-ready`,
     - Kalman sobre tasa diaria de aceptacion,
     - proxy tipo Kolmogorov por compresibilidad,
     - auditoria de invarianza ciclica \(C_4\) sobre settings, tasas de win y valores \(E_{ab}\).

4. `hensen2015_audit_report.json`
   - Salida ya generada del script con los resultados reproducidos.

5. `surface_plots/`
   - Rejilla bidimensional sobre `event_ready_offset_ps` y `readout_window_length`.
   - Incluye:
     - `surface_S.png`,
     - `surface_bell_trials.png`,
     - `surface_p_value.png`,
     - `hensen2015_surface_grid.npz`.

Alcance real de la auditoria:

- Se audito el pipeline observacional publicado:
  `candidate two-photon rows at C -> valid Bell trials -> CHSH statistic`
- No se audito el flujo completo de todos los intentos fisicos brutos, porque el dataset abierto ya viene con un primer filtro grueso en `C`.

Fuentes base del caso Bell auditado:

- Hensen et al. 2015, Nature, DOI `10.1038/nature15759`
- Dataset oficial 4TU, DOI `10.4121/uuid:6e19e9b2-4a2d-40b5-8dd3-a660bf3c0a31`
- Hensen et al. 2016 additional analysis, arXiv `1603.05705`
