# Protocolo preliminar de seguridad de participantes — Rosetta D2D

**Estado**: documento de diseño; no certifica seguridad, ni reemplaza aprobación ética o evaluación acústica instrumental.

## Condiciones previas
- Ensayos iniciales entre dispositivos del investigador y mediante transferencias WAV sin emisión acústica.
- Antes de exponer participantes a audio: caracterizar SPL con medidor calibrado en el punto de escucha, picos, duración, espectro, repetición y riesgo de fatiga; cumplir criterios de escucha segura aplicables al entorno y población.
- No transmitir ultrasonidos intencionales ni frecuencias ocultas; no transmitir comandos de actuación ni datos personales.
- Reclutar solamente adultos voluntarios para el piloto; no incluir poblaciones vulnerables sin evaluación específica.
- Aprobación ética institucional cuando corresponda; consentimiento informado previo, explicado de forma comprensible.

## Derechos y control
- Botón/parada física inmediata, volumen controlado por participante, pausas ilimitadas, retirada sin penalización, no coerción.
- Informar propósito, duración, sonidos, inconvenientes previsibles, tratamiento de datos y contactos del responsable.
- Detener el ensayo ante dolor, tinnitus, cefalea, mareo, incomodidad o fatiga y registrar la incidencia sin diagnóstico.
- Evitar identificadores de personas, grabaciones de voz, ubicación y registros de fondo. Usar identificadores aleatorios y almacenamiento con acceso restringido.
- Solicitar consentimiento separado para cualquier grabación o transmisión; por defecto, no grabar micrófono ambiental.

## Registro mínimo por sesión
ID anónimo, versión software, equipo/altavoz/auricular, calibración SPL, tipo y duración del estímulo, consentimiento, incidencias, fecha, elección de retirada, sin datos de identidad en resultados.

## Seguridad informática
- Modo opt-in para transmitir y recibir; nunca escucha permanente.
- Emparejamiento voluntario y autenticación criptográfica en etapas futuras; CRC32 no autentica.
- No realizar pruebas en espacios públicos sin consentimiento de las personas potencialmente expuestas.
