# NEXO · Búsqueda y monitoreo

Frontend institucional de demostración para operadores y autoridades. Desarrollado en **Python y NiceGUI**, con páginas independientes, componentes reutilizables, revisión humana de coincidencias, seguimiento entre cámaras y simulación de solicitudes de auxilio por voz.

No implementa reconocimiento facial, reidentificación ni transcripción real. Las páginas consumen servicios de Python reemplazables. No hay frontend separado, Node.js ni pasos de compilación de JavaScript. NiceGUI administra sus propias dependencias web internas.

## Requisitos e instalación

- Python **3.11 o superior**; verificado con Python 3.12.13 y NiceGUI 3.17.1.
- Navegador moderno. Diseño principal de escritorio, con adaptación a tablet.
- Conexión a Internet para instalar dependencias. Los recursos de demostración son locales.

Desde la carpeta del proyecto:

```bash
python -m venv venv
```

Windows, PowerShell:

```powershell
venv\Scripts\Activate.ps1
```

Windows, CMD:

```bat
venv\Scripts\activate
```

macOS / Linux:

```bash
source venv/bin/activate
```
               
Instalar y ejecutar:

```bash
python -m pip install -r requirements.txt
python main.py
```

Se abre **                                                                                                    ** en el navegador, con redirección al centro de monitoreo. No requiere claves de API ni una base de datos. Si ya existe el entorno `.venv` preparado en este equipo, puede ejecutarse directamente con:

```powershell
.\.venv\Scripts\python.exe main.py
```

La app escucha únicamente en `127.0.0.1` de forma predeterminada. Variables opcionales: `NEXO_PORT` (8080), `NEXO_SHOW` (1; usar 0 para evitar abrir el navegador), `NEXO_HOST` y `NEXO_STORAGE_SECRET`. Para detener el servidor: `Ctrl+C` en su terminal.

## Vistas disponibles

| Ruta | Función |
| --- | --- |
| `/monitor` | Plano de cámaras, actividad, expedientes activos y vistas de interés |
| `/cases` | Tabla administrativa con búsqueda y filtros; alta de caso |
| `/cases/{case_id}` | Referencias, información del reporte, detecciones y línea temporal |
| `/cameras` | CCTV 2 × 2, 3 × 3 y 4 × 4; filtros, grupos y panel por cámara |
| `/matches` | Comparación de imágenes, validación, descarte y revisión |
| `/tracking` | Detecciones cronológicas, estados y consulta de cámaras cercanas |
| `/alerts` | Evidencia de voz: audio, integridad, análisis, revisión y solicitudes de eliminación |
| `/voice` | Servicio de detección por micrófono, último análisis e historial reciente |
| `/history` | Bitácora filtrable con usuario, cámara, caso y resultado |
| `/users` | Usuarios y permisos por rol |
| `/settings` | Preferencias de referencia y puntos de integración |

Los parámetros `case_id`, `match_id`, `camera_id` y `alert_id` permiten enlaces directos desde otros módulos.

## Demostración de principio a fin

1. Abrir `/monitor` y seleccionar **Elena Robles (ficticia)**, folio `BUS-2026-0184`.
2. Consultar sus referencias y las detecciones: `CAM-003` a las 10:21:14, `CAM-007` a las 10:23:02 y `CAM-012` a las 10:25:41.
3. Abrir una detección en **Coincidencias**. Comparar referencia y captura; validar como posible coincidencia, descartar o solicitar revisión. Usuario, estado y hora quedan registrados en la bitácora.
4. Abrir **Mapa y seguimiento**. La secuencia muestra puntos de detección y relaciones temporales discontinuas. **No representa un recorrido físico ni una posición actual.** Las detecciones descartadas permanecen consultables y se excluyen del resumen de posibles coincidencias.
5. Ir a `/voice` y pulsar **INICIAR MONITOREO**. No se escribe ninguna frase: el sistema escucha el micrófono local.
6. Conversar con normalidad. Una narración pasada como `ayer necesité ayuda con una tarea` se clasifica NORMAL y no genera evidencia.
7. Decir una petición actual, por ejemplo `por favor déjame, me están siguiendo`. El sistema crea `EVENT-AAAAMMDD-NNNNN`, conserva el audio alrededor del momento, calcula su SHA-256 y lo envía a revisión.
8. Abrir `/alerts`, pulsar **Revisar**, escuchar la evidencia y elegir **CONFIRMAR PARA ATENCIÓN**, **MARCAR FALSO POSITIVO**, **ENVIAR A REVISIÓN** o **SOLICITAR ELIMINACIÓN**. No existe un botón de borrado: un supervisor distinto aprueba o rechaza la solicitud.
9. Probar **Nueva búsqueda**. Admite datos desconocidos y hasta cinco imágenes PNG, JPG o WebP de 5 MB cada una. Es obligatorio indicar un nombre o escribir «Persona desconocida». Las referencias se mantienen en memoria; no se generan vectores reales.
10. El menú de cuenta permite cambiar entre sesiones de prueba. El Operador puede gestionar búsquedas y revisiones; Supervisor también puede editar preferencias y frases; Administrador puede modificar permisos de otros usuarios. Las funciones de servicio comprueban el permiso antes de mutar datos.

## Arquitectura y trabajo por módulos

```text
main.py                  # arranque, archivos estáticos y registro de rutas
config.py                # configuración de ejecución
theme.py                 # tema común
pages/                   # una página NiceGUI por módulo
components/              # navegación, mapas, CCTV, tablas, perfiles y consolas
services/                # contratos que consume exclusivamente la interfaz
models/                  # dataclasses independientes de la interfaz
mocks/                   # semillas de datos ficticios
assets/css/              # estilos comunes y puntos de adaptación
assets/icons/            # identidad del sistema
assets/demo/             # plano, retratos, escenas y audio de prueba locales
assets/build_demo.py     # generador de recursos vectoriales y tono sintético
tests/                   # recorrido integral mediante simulador de NiceGUI
```

`services/store.py` concentra el repositorio temporal. Las páginas y componentes **no importan `mocks` ni el repositorio**. Los datos iniciales incluyen cuatro casos, dieciséis cámaras, diez detecciones, seis coincidencias y registros de historial. Voz y alertas comienzan vacías: sólo se llenan con audio real escuchado durante la sesión.

| Integración | Archivos principales |
| --- | --- |
| Gestión de reportes | `services/cases_service.py`, `models/person.py`, `models/search_case.py` |
| Reconocimiento facial | `services/facial_service.py`, `models/detection.py`, `models/match.py` |
| Cámaras | `services/cameras_service.py`, `models/camera.py`, `components/camera_feed.py` |
| Reidentificación / seguimiento | `services/tracking_service.py`, `components/map_view.py` |
| Voz e intenciones | `services/voice_service.py`, `models/voice_event.py` |
| Escucha continua | `services/monitoring_service.py`, `services/audio_buffer.py` |
| Evidencia y eliminación | `services/evidence_service.py`, `models/evidence_event.py`, `models/deletion_request.py` |
| Alertas y seguimiento | `services/alerts_service.py`, `models/alert.py` |
| Usuarios, auditoría y backend | `services/users_service.py`, `services/history_service.py`, `services/store.py` |

Para conectar un módulo real, conserva las funciones públicas y los tipos de retorno del servicio correspondiente. Por ejemplo, reemplaza la consulta de `get_matches(case_id)` por el adaptador al módulo facial, y conserva `validate_match`, `reject_match` y `request_review` como decisiones explícitas del operador. `get_tracking_history` devuelve `TrackingEvent` ordenados cronológicamente. La voz debe entregar `VoiceEvent` al servicio de alertas; `create_voice_alert` es idempotente respecto al identificador del evento.

Las operaciones de cámara/IA que tarden deben implementarse como funciones asíncronas o tareas fuera del hilo de UI; los componentes `LoadingState`, `ErrorState` y `EmptyState` están disponibles. Para una geografía real, reemplaza el plano local dentro de `MapView` por el proveedor cartográfico elegido y amplía `Camera` con coordenadas geográficas. No interpretes los porcentajes `x`/`y` de este plano como latitud/longitud.

FastAPI está disponible a través de `nicegui.app` si después se necesitan endpoints internos. En esta versión no se agregan endpoints de integración ficticios ni conexiones externas innecesarias.

## Datos, sesiones y límites de esta versión

- Todos los nombres son ficticios. Los retratos y capturas son **ilustraciones vectoriales sintéticas**, no fotografías de personas reales. El módulo de voz trabaja exclusivamente con audio real del micrófono: no existen campos para escribir frases de prueba.
- El módulo de voz permite micrófono local y transcripción con faster-whisper; visión y seguimiento continúan simulados. Los estados y similitudes son ejemplos para revisión humana. Confirmar un evento no confirma un delito.
- Los cambios y la bitácora viven en memoria del proceso, compartidos por las sesiones de demostración. **Se restablecen al reiniciar.** El almacenamiento de sesión de NiceGUI está en `.nicegui/`, excluido de Git.
- El selector de cuenta sirve para demostrar roles; **no es autenticación de producción**. La app no incluye SSO, gestión de credenciales, retención de evidencias ni auditoría inmutable. Estos puntos deben implementarse en los adaptadores de seguridad/backend antes de usar datos reales.
- Las preferencias de configuración se guardan como valores de referencia; no activan servicios ni políticas reales.
- Las escenas CCTV son estáticas. La actualización del monitor consulta los servicios simulados cada 15 segundos y la tabla de alertas cada 10 segundos.
- Las fechas iniciales de la demo son del 23 de septiembre de 2026. Las acciones del operador registran la hora local del equipo. El seguimiento muestra tiempo entre detecciones, sin sugerir que una captura de prueba sea una ubicación en vivo.

## Verificación

```bash
python -m unittest discover -s tests -v
```

Las pruebas usan el simulador de usuarios de NiceGUI y `unittest`, sin dependencias de desarrollo adicionales. Recorren las once vistas, filtran casos, registran uno nuevo, cambian revisiones, prueban la cámara desconectada, ejecutan el flujo de voz completo (buffer, transcripción, contexto, evidencia, integridad, revisión y eliminación autorizada) y verifican restricciones de permisos y entradas inválidas. Los datos y la carpeta de evidencia del test están aislados del servidor en ejecución.

El arranque y las once rutas también fueron comprobados mediante HTTP. La revisión visual automatizada en un navegador real queda pendiente cuando se disponga de una sesión de navegador conectada.

Referencia del framework: [documentación oficial de NiceGUI](https://nicegui.io/documentation).


## Detección de auxilio por voz (audio real)

Instala las dependencias y arranca desde el directorio del proyecto:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

Si este entorno no tiene pip, usa el instalador local existente:

```powershell
.\.tools\uv.exe pip install --python .venv/Scripts/python.exe --cache-dir .tools/cache -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

El módulo funciona **únicamente con audio capturado del micrófono**. La interfaz
no ofrece ningún campo para escribir frases ni simular eventos.

```text
Micrófono
  ↓ captura continua en un buffer circular en memoria
Ventanas de 6 s (solapamiento de 2 s)
  ↓ faster-whisper (español)
Transcripción
  ↓ contexto de los últimos 20 s de conversación
IA contextual (significado e intención) + análisis acústico
  ↓ fusión
NORMAL · AMBIGUO · POSIBLE_AUXILIO · ALTA_PRIORIDAD
  ↓ sólo si corresponde
EvidenceEvent + audio original + SHA-256
  ↓
/alerts → revisión humana
```

### Cómo probar el flujo completo

1. Abre `/voice`. La parte superior muestra el estado del servicio, si hay
   micrófono disponible y la cámara asociada (`CAM-008 — Pasillo B`).
2. Pulsa **INICIAR MONITOREO** y permite el acceso al micrófono en Windows.
   El indicador de nivel confirma que entra audio.
3. Conversen dos o tres personas con normalidad. Cada ventana analizada muestra
   transcripción, análisis, señales y resultado; nada se guarda en disco.

| Lo que se dice | Resultado esperado | Evidencia |
|---|---|---|
| «ayer comí tacos y se me atoró uno, ocupé ayuda» | NORMAL | No |
| «oye, no me sigas» tras conversación ordinaria | AMBIGUO o POSIBLE_AUXILIO | Según el análisis |
| «por favor déjame, necesito ayuda» | POSIBLE_AUXILIO | Sí |
| «suéltame, ayuda» con cambio acústico | ALTA_PRIORIDAD | Sí |

4. Cuando se crea un evento, la consola indica `EVENT-AAAAMMDD-NNNNN`, que el
   audio quedó protegido y que está pendiente de revisión.
5. Abre `/alerts`, pulsa **Revisar** y reproduce la evidencia. El panel muestra
   duración, verificación de integridad, transcripción, análisis y el estado del
   video (**Pendiente de integración**).
6. Prueba **MARCAR FALSO POSITIVO**: cambia la clasificación de revisión y el
   audio permanece.
7. Prueba **SOLICITAR ELIMINACIÓN** con un motivo. El evento pasa a
   `DELETION_REQUESTED` y aparece «Solicitud enviada para autorización».
8. Cambia de cuenta a **Supervisor01** desde el menú de sesión y vuelve a
   `/alerts`. En **Solicitudes de eliminación** puedes **APROBAR** o **RECHAZAR**.
   Quien solicita no puede autorizar su propia solicitud.
9. Consulta `/history`: creación del evento, reproducción, revisión, solicitud y
   resolución quedan registradas.

### Evidencia, integridad y video

Cuando la clasificación es POSIBLE_AUXILIO o ALTA_PRIORIDAD se crea un
`EvidenceEvent` y se escribe un único archivo WAV:

```text
evidence/
├── audio/EVENT-20260923-00001.wav
└── video/        (reservado para el módulo de cámaras)
```

- El fragmento incluye aproximadamente 10 segundos anteriores, la ventana donde
  ocurrió la posible solicitud y 10 segundos posteriores.
- El identificador es único por día y **nunca se sobrescribe un archivo**: si el
  nombre existe, se rechaza la escritura.
- Al guardarlo se calcula un **SHA-256** que se conserva en el evento. `/alerts`
  vuelve a calcularlo al abrir el detalle y muestra
  «✓ Archivo original verificado» sólo si coincide.
- El original es inmutable: la interfaz no edita, recorta ni reemplaza audio. Una
  versión procesada debe crearse como copia derivada, conservando el original.
- El evento reserva `video_file`, `video_start_timestamp`, `video_end_timestamp`
  y `video_status = "PENDING_INTEGRATION"`. El módulo de cámaras integrará el
  video con `attach_video_evidence(event_id, video_path, start_timestamp, end_timestamp)`
  de `services/evidence_service.py`; audio y video comparten el mismo `event_id`.

### Roles y control de eliminación

| Rol | Puede |
|---|---|
| Operador | Escuchar evidencia, revisar transcripción y análisis, confirmar para atención, marcar falso positivo, enviar a revisión y **solicitar** eliminación |
| Supervisor | Lo anterior, más **aprobar o rechazar** solicitudes de eliminación |
| Administrador | Lo anterior, más gestión de usuarios y consulta de auditoría completa |

Ningún rol puede borrar evidencia desde la interfaz: el botón de borrado no
existe. Los estados de revisión son `PENDIENTE_REVISION`, `EN_REVISION`,
`CONFIRMADO_PARA_ATENCION`, `FALSO_POSITIVO`, `DELETION_REQUESTED`,
`DELETION_APPROVED` y `DELETION_REJECTED`. Para el prototipo, una aprobación
registra `DELETION_APPROVED` y **no elimina el archivo físico**, de modo que una
demostración no pueda destruir evidencia por accidente. Toda solicitud guarda
quién la pidió, quién la resolvió, fecha, motivo, hash y evento; la bitácora de
esa operación permanece aunque más adelante se aplique una política de borrado.

### Privacidad: qué se conserva y qué no

- Las conversaciones ordinarias **sólo existen en memoria**. El audio vive en un
  buffer circular de unos 40 segundos que se sobrescribe continuamente y se borra
  al detener el monitoreo o al cerrar la página.
- El contexto conversacional conserva como máximo 8 segmentos de los últimos 20
  segundos; los segmentos antiguos se descartan si no pertenecen a un evento.
- **Sólo se escribe audio en disco cuando existe un posible evento de auxilio.**
  Los eventos NORMAL no generan archivo y su transcripción caduca automáticamente.
- La bitácora conserva identificadores, clasificaciones y acciones, no las
  conversaciones normales.
- La carpeta `evidence/` está excluida de Git: las grabaciones nunca se versionan.

### Micrófono y modelo

Configuración en `config.py`: `VOICE_MODEL` (`tiny`, `base` o `small`),
`VOICE_LANGUAGE='es'`, `AUDIO_SAMPLE_RATE=16000`, `AUDIO_WINDOW_SECONDS=6`,
`AUDIO_OVERLAP_SECONDS=2`, `EVIDENCE_PRE_SECONDS=10`, `EVIDENCE_POST_SECONDS=10`,
`AUDIO_RING_SECONDS` y `DEFAULT_CAMERA_ID`.

Whisper usa CPU/int8 y carga el modelo en la primera transcripción; puede
necesitar Internet para descargarlo. Se captura el dispositivo predeterminado del
equipo donde corre Python, no el micrófono de un navegador remoto. Sólo una
escucha puede usar el micrófono a la vez. No se fabrican porcentajes de
confianza: `confidence=None`; los metadatos reales de Whisper se conservan en el
evento y en `transcript_segments`.

El análisis acústico mide energía RMS, su variación y la relación frente a la
mediana reciente. `ACOUSTIC_CHANGE_RATIO=2.0` es un umbral experimental. Un
cambio acústico **no** crea alertas con semántica NORMAL o AMBIGUO, y una
petición actual dicha en voz baja sí puede crearlas: la decisión depende del
lenguaje y su contexto. No se infieren emociones; la interfaz sólo informa
«Cambio acústico significativo» o «Variación acústica moderada».

### Integración y autorización

`services/monitoring_service.py` orquesta captura, ventanas, transcripción,
contexto, fusión y evidencia. `services/voice_service.py` conserva transcripción
y clasificación, y `process_text` sigue siendo la entrada compartida.
`services/voice_integrations.py` ofrece `request_person_detection`,
`start_tracking_from_alert` y `execute_authority_command`; sus resultados
incluyen `mock=True`. No se ha implementado reconocimiento facial, video real ni
seguimiento entre cámaras: sólo quedan preparados los puntos de integración.

El selector de usuario NO autentica: es una demostración de roles. Los permisos
(`review`, `deletion.request`, `deletion.approve`, `users`) se comprueban en los
servicios de Python, no en la interfaz.

Referencias de las APIs: [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
y [sounddevice](https://python-sounddevice.readthedocs.io/).

### IA contextual y fallback real

Configuración central en `config.py`:

```python
AI_CONTEXT_ENABLED = True
AI_PROVIDER = 'ollama'
AI_MODEL = 'qwen2.5:3b'
AI_CONTEXT_URL = 'http://127.0.0.1:11434'
AI_TIMEOUT_SECONDS = 15
CONTEXT_SECONDS = 20
CONTEXT_MAX_SEGMENTS = 8
AUDIO_WINDOW_SECONDS = 6
AUDIO_OVERLAP_SECONDS = 2
```

El adaptador Ollama usa `/api/chat`, esquema JSON y validación estricta con Pydantic.
La interfaz sólo conoce `analyze_conversation_context`. Para integrar otro proveedor,
agrega un adaptador al registro `PROVIDERS` que devuelva `SemanticAnalysis`.
El prompt trata las transcripciones como datos y pide explicaciones breves;
no solicita razonamiento interno ni conclusiones legales.

No se instala ni descarga automáticamente un LLM. En este entorno no se encontró
Ollama disponible: las pruebas de los diez escenarios verifican **Fallback local**.
El contrato de IA se probó con transporte simulado, no con inferencia real de un LLM.
Para usar IA local, instala [Ollama](https://ollama.com/download), descarga el modelo
con `ollama pull qwen2.5:3b` y deja su servidor local ejecutándose. Reinicia NEXO y
comprueba que la consola muestre **IA contextual**. La carga inicial puede superar
el timeout; precarga el modelo con `ollama run qwen2.5:3b` si fuera necesario.
El modelo es intercambiable mediante `AI_MODEL`; sus resultados deben validarse
con los mismos ejemplos antes de una presentación.

Si el servicio falla, no existe modelo, vence el timeout o el JSON es inválido,
se usa **Fallback local** con motivo visible. También puedes forzarlo usando
`AI_CONTEXT_ENABLED=False`. El fallback distingue indicadores de pasado, citas,
hipótesis, ayuda cotidiana y expresiones actuales, pero no comprende todos los
matices: ironía, citas mezcladas y negaciones complejas pueden fallar. Es un
prototipo para revisión humana, no un sistema validado de detección de emergencias.

Referencia del contrato: [salida estructurada de Ollama](https://docs.ollama.com/capabilities/structured-outputs).
Modelo configurable: [Qwen2.5 3B](https://ollama.com/library/qwen2.5:3b).

### Retención del prototipo

- El audio en vivo vive en un buffer circular en memoria. Sólo se escribe en
  disco el fragmento asociado a un posible evento de auxilio; el resto se
  sobrescribe y se descarta al detener el monitoreo o cerrar la página.
- El contexto conversacional guarda como máximo 8 segmentos de los últimos 20
  segundos y 2000 caracteres por segmento.
- Los eventos NORMAL se muestran temporalmente y se eliminan del repositorio
  mediante una tarea de caducidad cada segundo, incluso sin una página abierta.
  El contexto previo no se copia al evento persistente.
- AMBIGUO se considera relevante para revisión de la demo: conserva sólo su frase
  y evaluación en el historial, limitado a 100 eventos, y no genera archivo.
- La evidencia (`EvidenceEvent`, transcripción, análisis, hash y estado de
  revisión) vive en el repositorio en memoria hasta reiniciar el proceso; el
  archivo WAV sí permanece en `evidence/audio/`. No se implementó una base de
  datos: al reiniciar, los eventos deben volver a crearse aunque el audio siga ahí.
- La bitácora conserva identificador, clasificación, prioridad y acciones, sin
  copiar conversaciones normales. Las cuentas continúan siendo de demostración.
- Por defecto el proveedor es local; cambiar `AI_CONTEXT_URL` a un servidor remoto
  implica enviarle contexto y frase. Ese proveedor deberá implementar su propia
  política de retención antes de utilizar conversaciones reales.

### Verificación

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Incluye los escenarios semánticos solicitados y las ocho pruebas del módulo de
evidencia: narración pasada sin evidencia, rechazo tras conversación ordinaria,
solicitud actual con audio protegido, prioridad alta con cambio acústico, falso
positivo, solicitud de eliminación, rechazo y aprobación por un supervisor
distinto. También cubre buffer circular, unicidad de archivos, verificación
SHA-256, el punto de integración de video y el recorrido de la interfaz.
Los tests acústicos usan arrays sintéticos; no validan emociones ni peligro real.
