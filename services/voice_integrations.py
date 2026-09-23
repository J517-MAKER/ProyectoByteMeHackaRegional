"""Adapters to replace when vision and tracking are available."""


def request_person_detection(camera_id: str, alert_id: str):
    return {'success': True, 'mock': True, 'status': 'WAITING_FOR_VISION_MODULE',
            'camera_id': camera_id, 'alert_id': alert_id}


def start_tracking_from_alert(alert_id: str, camera_id: str):
    return {'success': True, 'mock': True, 'status': 'WAITING_FOR_TRACKING_MODULE',
            'camera_id': camera_id, 'alert_id': alert_id,
            'vision': request_person_detection(camera_id, alert_id)}


def execute_authority_command(action: str, parameters: dict):
    return {'success': True, 'mock': True, 'action': action, 'parameters': parameters,
            'message': 'Integración con módulo de seguimiento pendiente. No se ejecutó una operación real.'}
