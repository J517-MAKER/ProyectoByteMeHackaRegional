import config
from models.audit_log import AuditLog
from services import store


def get_history():
    """Historial compartido por todo el equipo: se lee de la base de datos
    cuando está disponible para que los registros de cualquier dispositivo
    aparezcan aquí, incluso tras cerrar y volver a abrir el software. Si la
    base no está disponible, se muestra la bitácora local en memoria."""
    if config.HISTORY_DB_ENABLED:
        try:
            from services import db_service
            rows = db_service.obtener_historial()
            if rows:
                return [_row_to_audit_log(row) for row in rows]
        except Exception as exc:
            print(f'[historial] No se pudo leer la base de datos compartida, usando memoria local: {exc}')
    return sorted(store.logs, key=lambda item: item.timestamp, reverse=True)


def _row_to_audit_log(row):
    fecha_hora, usuario, tipo, descripcion, caso_id, camara_id, resultado, dispositivo = row
    timestamp = fecha_hora.strftime('%Y-%m-%d %H:%M:%S') if hasattr(fecha_hora, 'strftime') else str(fecha_hora)
    return AuditLog(timestamp, usuario, tipo, descripcion, caso_id, camara_id, resultado, dispositivo or '—')
