"""Reference-image processing and facial similarity search.

The descriptor is intentionally kept behind this service so it can be replaced by
an approved 512-dimensional face-embedding model without changing the UI. The
current implementation creates a deterministic 512-value visual descriptor from
the uploaded image and is suitable for the demo database only; it must not be
used as a definitive identity decision.
"""
import base64
import io

import numpy as np
from PIL import Image

from services import store
from services.users_service import require
from services.db_service import buscar_coincidencias_rostro, guardar_captura_rostro


def embedding_from_bytes(content):
    """Return a normalized 512-value descriptor for an uploaded image."""
    try:
        image = Image.open(io.BytesIO(content)).convert('L').resize((32, 16))
    except Exception as exc:
        raise ValueError('No se pudo leer la fotografía de referencia.') from exc
    vector = np.asarray(image, dtype=np.float32).reshape(-1) / 255.0
    norm = float(np.linalg.norm(vector))
    return (vector / norm if norm else vector).tolist()


def embedding_from_data_url(source):
    if not source or ',' not in source:
        return []
    try:
        return embedding_from_bytes(base64.b64decode(source.split(',', 1)[1]))
    except (ValueError, TypeError, base64.binascii.Error):
        return []


def search_case_reference(case_id, threshold=0.70, limit=10):
    """Compare a case reference image with captures stored by the cameras."""
    case = next((item for item in store.cases if item.id == case_id), None)
    if not case:
        raise ValueError('No se encontró este expediente.')
    if not case.reference_embedding:
        raise ValueError('El expediente todavía no tiene una foto de referencia válida.')
    return buscar_coincidencias_rostro(case.reference_embedding, umbral=threshold, limite=limit)


def get_detection(detection_id):
    return next((d for d in store.detections if d.id == detection_id), None)


def get_matches(case_id=None, vector_busqueda=None):
    if vector_busqueda:
        return buscar_coincidencias_rostro(vector_busqueda, umbral=0.70)
    return [m for m in store.matches if case_id is None or
            (get_detection(m.detection_id) and get_detection(m.detection_id).case_id == case_id)]


def review_match(match_id, status):
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
    return guardar_captura_rostro(codigo_camara, embedding_rostro, ruta_imagen, tipo_evento)
