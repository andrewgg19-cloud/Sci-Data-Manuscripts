ROSETTA D2D v0.1 — prueba de concepto sin red, sin micrófono automático

REQUISITOS: Python 3, solo biblioteca estándar.
Emisor:  py rosetta_d2d.py encode --message "PRUEBA-001" --out prueba.wav
Receptor: py rosetta_d2d.py decode --wav prueba.wav

El WAV puede copiarse manualmente entre equipos, sin conexión. El decodificador actual presupone WAV mono 16-bit 22050 Hz con sincronización perfecta; NO está validado para capturas por micrófono, cambios de reloj, ruido ambiental, transmisiones OTA, o seguridad contra atacantes. Los tonos y el nivel digital NO garantizan un SPL seguro: primero calibrar acústicamente y usar volumen bajo.

Esta es una demostración FSK de referencia para la futura arquitectura Rosetta, NO implementa la sonificación de primos / Odlyzko ni representa un producto listo para personas o empresas. CRC32 detecta errores accidentales, NO proporciona confidencialidad, identidad del emisor ni autenticación. No usar con información privada, códigos bancarios, claves, e.firma o comandos sobre otros dispositivos.

Ver PROTOCOLO_SEGURIDAD_PARTICIPANTES.md y PLAN_VALIDACION.md.
