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

Se abre **http://127.0.0.1:8080** en el navegador, con redirección al centro de monitoreo. No requiere claves de API ni una base de datos. Si ya existe el entorno `.venv` preparado en este equipo, puede ejecutarse directamente con:

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
| `/alerts` | Eventos de voz, detalle, revisión y seguimiento independiente |
| `/voice` | Frases configuradas, comandos de autoridad y consola de pruebas |
| `/history` | Bitácora filtrable con usuario, cámara, caso y resultado |
| `/users` | Usuarios y permisos por rol |
| `/settings` | Preferencias de referencia y puntos de integración |

Los parámetros `case_id`, `match_id`, `camera_id` y `alert_id` permiten enlaces directos desde otros módulos.

## Demostración de principio a fin

1. Abrir `/monitor` y seleccionar **Elena Robles (ficticia)**, folio `BUS-2026-0184`.
2. Consultar sus referencias y las detecciones: `CAM-003` a las 10:21:14, `CAM-007` a las 10:23:02 y `CAM-012` a las 10:25:41.
3. Abrir una detección en **Coincidencias**. Comparar referencia y captura; validar como posible coincidencia, descartar o solicitar revisión. Usuario, estado y hora quedan registrados en la bitácora.
4. Abrir **Mapa y seguimiento**. La secuencia muestra puntos de detección y relaciones temporales discontinuas. **No representa un recorrido físico ni una posición actual.** Las detecciones descartadas permanecen consultables y se excluyen del resumen de posibles coincidencias.
5. Ir a `/voice` → **Pruebas**. Conservar `CAM-008` y la frase `ayuda, me están siguiendo`. Pulsar **Iniciar prueba**. La consola muestra audio simulado, transcripción, intención, subtipo y resultado.
6. **Detener** cancela la prueba antes de crear el evento. Una prueba finalizada genera `SOLICITUD_AUXILIO` / `POSIBLE_SEGUIMIENTO` y una alerta pendiente de revisión.
7. Abrir `/alerts`, pulsar **Revisar** y confirmar el evento, descartarlo o enviarlo a revisión. **Iniciar seguimiento** abre el contexto de esa alerta y las cámaras cercanas, sin asociarlo automáticamente a una persona buscada.
8. En `/voice` → **Comandos de autoridad**, simular `mostrar última detección del folio 184`. Se interpreta como `MOSTRAR_ULTIMA_DETECCION` y `BUS-2026-0184`. **Abrir resultado** lleva al seguimiento.
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

`services/store.py` concentra el repositorio temporal. Las páginas y componentes **no importan `mocks` ni el repositorio**. Los datos iniciales incluyen cuatro casos, dieciséis cámaras, diez detecciones, seis coincidencias, cinco eventos de voz, cuatro alertas y registros de historial.

| Integración | Archivos principales |
| --- | --- |
| Gestión de reportes | `services/cases_service.py`, `models/person.py`, `models/search_case.py` |
| Reconocimiento facial | `services/facial_service.py`, `models/detection.py`, `models/match.py` |
| Cámaras | `services/cameras_service.py`, `models/camera.py`, `components/camera_feed.py` |
| Reidentificación / seguimiento | `services/tracking_service.py`, `components/map_view.py` |
| Voz e intenciones | `services/voice_service.py`, `models/voice_event.py` |
| Alertas y revisión | `services/alerts_service.py`, `models/alert.py` |
| Usuarios, auditoría y backend | `services/users_service.py`, `services/history_service.py`, `services/store.py` |

Para conectar un módulo real, conserva las funciones públicas y los tipos de retorno del servicio correspondiente. Por ejemplo, reemplaza la consulta de `get_matches(case_id)` por el adaptador al módulo facial, y conserva `validate_match`, `reject_match` y `request_review` como decisiones explícitas del operador. `get_tracking_history` devuelve `TrackingEvent` ordenados cronológicamente. La voz debe entregar `VoiceEvent` al servicio de alertas; `create_voice_alert` es idempotente respecto al identificador del evento.

Las operaciones de cámara/IA que tarden deben implementarse como funciones asíncronas o tareas fuera del hilo de UI; los componentes `LoadingState`, `ErrorState` y `EmptyState` están disponibles. Para una geografía real, reemplaza el plano local dentro de `MapView` por el proveedor cartográfico elegido y amplía `Camera` con coordenadas geográficas. No interpretes los porcentajes `x`/`y` de este plano como latitud/longitud.

FastAPI está disponible a través de `nicegui.app` si después se necesitan endpoints internos. En esta versión no se agregan endpoints de integración ficticios ni conexiones externas innecesarias.

## Datos, sesiones y límites de esta versión

- Todos los nombres son ficticios. Los retratos y capturas son **ilustraciones vectoriales sintéticas**, no fotografías de personas reales. El audio reproducible es un tono de prueba, sin palabras grabadas. La transcripción es una entrada de texto simulada.
- No se utiliza el micrófono ni se ejecutan algoritmos de IA. Los estados y similitudes son ejemplos para revisión humana. Confirmar un evento no confirma un delito.
- Los cambios y la bitácora viven en memoria del proceso, compartidos por las sesiones de demostración. **Se restablecen al reiniciar.** El almacenamiento de sesión de NiceGUI está en `.nicegui/`, excluido de Git.
- El selector de cuenta sirve para demostrar roles; **no es autenticación de producción**. La app no incluye SSO, gestión de credenciales, retención de evidencias ni auditoría inmutable. Estos puntos deben implementarse en los adaptadores de seguridad/backend antes de usar datos reales.
- Las preferencias de configuración se guardan como valores de referencia; no activan servicios ni políticas reales. La edición de frases sí afecta las pruebas de voz.
- Las escenas CCTV son estáticas. La actualización del monitor consulta los servicios simulados cada 15 segundos y la tabla de alertas cada 10 segundos.
- Las fechas iniciales de la demo son del 23 de septiembre de 2026. Las acciones del operador registran la hora local del equipo. El seguimiento muestra tiempo entre detecciones, sin sugerir que una captura de prueba sea una ubicación en vivo.

## Verificación

```bash
python -m unittest discover -s tests -v
```

La prueba utiliza el simulador de usuarios de NiceGUI y `unittest`, sin dependencias de desarrollo adicionales. Recorre las once vistas, filtra casos, registra uno nuevo, cambia revisiones, prueba la cámara desconectada, cancela y completa una prueba de voz, revisa la alerta, inicia seguimiento, interpreta un comando y verifica restricciones de permisos y entradas inválidas. Los datos del test están aislados del servidor en ejecución.

El arranque y las once rutas también fueron comprobados mediante HTTP. La revisión visual automatizada en un navegador real queda pendiente cuando se disponga de una sesión de navegador conectada.

Referencia del framework: [documentación oficial de NiceGUI](https://nicegui.io/documentation).
