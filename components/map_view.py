from nicegui import ui
from services.cameras_service import get_cameras

COLORS = {'En línea':'#487965','Desconectada':'#8d999f','Alerta':'#b4544c','Posible coincidencia':'#bc9246'}


def MapView(cameras=None,detections=None,selected=None,on_select=None,height=None):
    cameras = get_cameras() if cameras is None else cameras
    detection_list = [event.detection for event in (detections or [])]
    with ui.element('div').classes('map-stage').style(f'height:{height}px' if height else ''):
        plane = ui.element('div').classes('map-plane')
        with plane:
            ui.image('/assets/demo/map.svg').classes('map-background').props('no-spinner fit=fill')
            if detection_list:
                coords=[]
                for detection in detection_list:
                    cam=next((c for c in cameras if c.id==detection.camera_id),None)
                    if cam:
                        coords.append(f'{cam.x*12},{cam.y*7}')
                if len(coords)>1:
                    ui.html('<svg viewBox="0 0 1200 700" preserveAspectRatio="none" width="100%" height="100%"><polyline points="'+' '.join(coords)+'" fill="none" stroke="#3c6b8d" stroke-width="3" stroke-dasharray="7 9" opacity=".7"/></svg>',sanitize=False).classes('absolute inset-0 pointer-events-none')
            for camera in cameras:
                color = COLORS[camera.status]
                detection = next((d for d in reversed(detection_list) if d.camera_id==camera.id),None)
                detection_status = None
                if detection:
                    detection_status = detection.status
                    color = '#487965' if detection.status=='Validada por operador' else '#8d999f' if detection.status=='Descartada' else '#bc9246'
                if selected==camera.id:
                    color='#245f83'
                callback = (lambda cid=camera.id:on_select(cid)) if on_select else (lambda cid=camera.id:ui.navigate.to(f'/cameras?camera_id={cid}'))
                ui.button(icon='close' if detection_status=='Descartada' else 'check' if detection_status=='Validada por operador' else 'videocam',on_click=callback).props('unelevated dense').classes('map-marker').style(f'left:{camera.x}%;top:{camera.y}%;background:{color}!important').tooltip(f'{camera.id} · {camera.name} · {detection_status or camera.status}')
                ui.label(camera.id).classes('map-marker-label').style(f'left:{camera.x}%;top:{camera.y}%')
        zoom={'value':1.0}
        def scale(delta):
            zoom['value']=max(1,min(1.8,zoom['value']+delta))
            plane.style(f'transform:scale({zoom["value"]})')
        with ui.element('div').classes('map-controls'):
            ui.button(icon='add',on_click=lambda:scale(.2)).props('dense').tooltip('Acercar')
            ui.button(icon='remove',on_click=lambda:scale(-.2)).props('dense').tooltip('Alejar')
            ui.button(icon='center_focus_strong',on_click=lambda:scale(-2)).props('dense').tooltip('Restablecer vista')
        ui.label('REGIÓN CENTRO · PLANO FICTICIO / SIN GEOLOCALIZACIÓN REAL').classes('map-note')
    with ui.element('div').classes('map-legend'):
        for status,color in COLORS.items():
            with ui.element('div').classes('legend-item'):
                ui.element('span').classes('legend-dot').style(f'background:{color}')
                ui.label(status)
        if detection_list:
            ui.label('✓ Validada por operador · × Descartada · Ámbar: posible detección').classes('text-[10px]')
            ui.label('– – Relación temporal; no representa una ruta').classes('text-[10px]')
