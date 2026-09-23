from services import store
from services.users_service import require


def get_matches(case_id=None):
    return [m for m in store.matches if case_id is None or get_detection(m.detection_id).case_id==case_id]


def get_detection(detection_id):
    return next(d for d in store.detections if d.id == detection_id)


def review_match(match_id, status):
    actor = require('review')
    match = next(m for m in store.matches if m.id==match_id)
    match.status, match.reviewed_by, match.reviewed_at = status, actor, store.now()
    detection = get_detection(match.detection_id)
    detection.status = status
    store.audit(actor, 'Revisión', f'{match.id}: {status}', detection.case_id, detection.camera_id, status)
    return match


def validate_match(match_id):
    return review_match(match_id,'Validada por operador')


def reject_match(match_id):
    return review_match(match_id,'Descartada')


def request_review(match_id):
    return review_match(match_id,'En revisión')
