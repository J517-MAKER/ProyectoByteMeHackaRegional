import re
import unicodedata
from models.voice_event import VoiceEvent
from services import store
from services.alerts_service import create_voice_alert
from services.cases_service import get_case
from services.tracking_service import start_tracking, stop_tracking
from services.users_service import require


def get_voice_events():
    return store.voice_events


def get_phrases():
    return list(store.phrases)


def set_phrases(text):
    actor = require('settings')
    store.phrases[:] = list(dict.fromkeys(p.strip().lower() for p in text.splitlines() if p.strip()))
    store.audit(actor,'Configuración','Actualizó frases de auxilio')


def normalize(text):
    return ''.join(c for c in unicodedata.normalize('NFD',text.lower()) if unicodedata.category(c)!='Mn')


def simulate_voice_event(text='ayuda, me están siguiendo',camera_id='CAM-008'):
    require('voice')
    from services.cameras_service import get_camera
    camera = get_camera(camera_id)
    if not camera or not camera.audio or camera.status=='Desconectada':
        raise ValueError('La cámara debe estar conectada y disponer de audio.')
    if not any(normalize(p) in normalize(text) for p in store.phrases):
        return None
    event = VoiceEvent(f'VOZ-{len(store.voice_events)+1:03d}',store.now(),camera_id,text,
                       subtype='POSIBLE_SEGUIMIENTO' if 'sig' in normalize(text) else 'AUXILIO_GENERAL')
    store.voice_events.insert(0,event)
    create_voice_alert(event)
    return event


def process_voice_command(text):
    actor = require('voice')
    normalized = normalize(text)
    actions = {'iniciar busqueda':'INICIAR_BUSQUEDA','detener busqueda':'DETENER_BUSQUEDA',
               'mostrar ultima deteccion':'MOSTRAR_ULTIMA_DETECCION','mostrar coincidencias':'MOSTRAR_COINCIDENCIAS',
               'mostrar camaras cercanas':'MOSTRAR_CAMARAS_CERCANAS','continuar seguimiento':'CONTINUAR_SEGUIMIENTO',
               'marcar coincidencia como incorrecta':'REVISAR_COINCIDENCIA'}
    action = next((v for k,v in actions.items() if normalized.startswith(k)),None)
    number = re.search(r'folio\s+(?:bus-2026-)?(\d+)',normalized)
    case_id = f'BUS-2026-{int(number[1]):04d}' if number else None
    if not action or not case_id or not get_case(case_id):
        return {'recognized':False,'message':'Comando no reconocido o folio inexistente. Incluye «folio 184».'}
    if action in ('INICIAR_BUSQUEDA','CONTINUAR_SEGUIMIENTO'):
        start_tracking(case_id)
    elif action=='DETENER_BUSQUEDA':
        stop_tracking(case_id)
    route = f'/matches?case_id={case_id}' if action in ('MOSTRAR_COINCIDENCIAS','REVISAR_COINCIDENCIA') else f'/tracking?case_id={case_id}'
    if action=='MOSTRAR_CAMARAS_CERCANAS':
        from services.tracking_service import get_tracking_history
        history=[t for t in get_tracking_history(case_id) if t.detection.status!='Descartada']
        if history:
            route += f'&camera_id={history[-1].detection.camera_id}'
    store.audit(actor,'Comando de voz',text,case_id,result=action)
    return {'recognized':True,'action':action,'case_id':case_id,'route':route}
