from services import store
from services.users_service import require
from services.db_service import buscar_coincidencias_rostro, guardar_captura_rostro

def get_detection(detection_id):
    """Busca y retorna una detección dentro del store."""
    return next((d for d in store.detections if d.id == detection_id), None)

def get_matches(case_id=None, vector_busqueda=None):
    """
    Recupera las coincidencias. 
    Si se provee un vector facial, realiza la búsqueda por similitud en PostgreSQL (pgvector).
    De lo contrario, consulta las coincidencias almacenadas en memoria (store).
    """
    if vector_busqueda:
        # Búsqueda vectorial directa en la base de datos de Docker
        return buscar_coincidencias_rostro(vector_busqueda, umbral=0.70)
    
    # Búsqueda tradicional en el store en memoria
    return [
        m for m in store.matches 
        if case_id is None or (get_detection(m.detection_id) and get_detection(m.detection_id).case_id == case_id)
    ]

def review_match(match_id, status):
    """Actualiza el estado de revisión de una coincidencia y genera un registro de auditoría."""
    actor = require('review')
    match = next(m for m in store.matches if m.id == match_id)
    match.status, match.reviewed_by, match.reviewed_at = status, actor, store.now()
    
    detection = get_detection(match.detection_id)
    if detection:
        detection.status = status
        store.audit(actor, 'Revisión', f'{match.id}: {status}', detection.case_id, detection.camera_id, status)
    
    return match

def validate_match(match_id):
    return review_match(match_id, 'Validada por operador')

def reject_match(match_id):
    return review_match(match_id, 'Descartada')

def request_review(match_id):
    return review_match(match_id, 'En revisión')

def registrar_rostro_detectado(codigo_camara, embedding_rostro, ruta_imagen, tipo_evento='ALERTA_AUDIO'):
    """Guarda el vector extraído de la cámara en PostgreSQL."""
    return guardar_captura_rostro(codigo_camara, embedding_rostro, ruta_imagen, tipo_evento)