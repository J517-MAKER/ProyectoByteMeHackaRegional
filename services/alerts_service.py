from models.alert import EmergencyAlert
from services import store
from services.users_service import require


def get_alerts():
    return store.alerts


def get_alert(alert_id):
    return next((a for a in store.alerts if a.id==alert_id),None)


def get_alert_event(alert):
    return next(v for v in store.voice_events if v.id==alert.voice_event_id)


def create_voice_alert(event):
    existing = next((a for a in store.alerts if a.voice_event_id==event.id),None)
    if existing:
        return existing
    alert = EmergencyAlert(f'ALT-{len(store.alerts)+1:03d}',event.id)
    store.alerts.insert(0,alert)
    store.audit('Sistema','Voz','Posible solicitud de auxilio',camera_id=event.camera_id,result='Pendiente de revisión')
    return alert


def review_alert(alert_id,status):
    actor = require('review')
    alert = get_alert(alert_id)
    alert.status, alert.reviewed_by, alert.reviewed_at = status, actor, store.now()
    event = get_alert_event(alert)
    event.status = status
    store.audit(actor,'Alerta',f'{alert.id}: {status}',camera_id=event.camera_id,result=status)


def confirm_alert(alert_id):
    review_alert(alert_id,'Evento confirmado por operador')


def reject_alert(alert_id):
    review_alert(alert_id,'Descartada')


def send_to_review(alert_id):
    review_alert(alert_id,'En revisión')


def start_alert_tracking(alert_id):
    actor = require('track')
    alert = get_alert(alert_id)
    alert.tracking_started = True
    store.audit(actor,'Seguimiento',f'Seguimiento de evento {alert.id} iniciado',camera_id=get_alert_event(alert).camera_id)
