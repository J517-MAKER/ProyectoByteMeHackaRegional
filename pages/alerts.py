from nicegui import ui
from components.layout import PageLayout,notify_action
from components.alert_table import AlertTable
from components.person_profile import InfoPair
from components.camera_feed import CameraFeed
from components.status_badge import StatusBadge
from services.alerts_service import get_alerts,get_alert,get_alert_event,confirm_alert,reject_alert,send_to_review,start_alert_tracking
from services.cameras_service import get_camera,get_nearby_cameras
from services.users_service import can


@ui.page('/alerts')
def alerts_page():
    with PageLayout('/alerts','Alertas de auxilio','Eventos de voz para evaluación de una autoridad. La detección no confirma la existencia de un delito.'):
        selected={'id':None}
        with ui.right_drawer(value=False).props('width=430 bordered overlay').classes('p-0') as drawer:
            @ui.refreshable
            def detail():
                alert=get_alert(selected['id'])
                if not alert:
                    return
                event=get_alert_event(alert)
                camera=get_camera(event.camera_id)
                with ui.row().classes('panel-heading w-full'):
                    ui.label(alert.id+' / Revisión de evento').classes('section-title')
                    ui.button(icon='close',on_click=drawer.hide).props('flat dense round')
                with ui.column().classes('p-5 w-full gap-3'):
                    StatusBadge(alert.status)
                    ui.label('Posible solicitud de auxilio').classes('text-lg font-medium')
                    ui.label(f'“{event.transcript}”').classes('text-lg p-4 bg-[#f5f7f8] w-full')
                    CameraFeed(camera)
                    for label,value in [('Cámara',event.camera_id),('Hora',event.timestamp),('Ubicación',camera.location),('Confianza del reconocimiento',event.confidence),('Tipo',event.intent)]:
                        InfoPair(label,value)
                    ui.label('Audio de prueba · tono sintético, sin voz grabada').classes('text-xs muted')
                    ui.audio('/assets/demo/test-tone.wav').classes('w-full')
                    ui.label('Cámaras cercanas').classes('section-title mt-2')
                    for nearby in get_nearby_cameras(camera.id):
                        ui.link(f'{nearby.id} · {nearby.name}',f'/cameras?camera_id={nearby.id}').classes('text-xs')
                    def changed():
                        table.refresh()
                        detail.refresh()
                    with ui.row().classes('gap-2 mt-3'):
                        for label,action,message in [('Confirmar evento',confirm_alert,'Evento confirmado por operador.'),('Descartar',reject_alert,'Evento descartado.'),('Enviar a revisión',send_to_review,'Evento enviado a revisión.')]:
                            ui.button(label,on_click=lambda a=action,m=message:notify_action(lambda:a(alert.id),m,changed)).props('outline no-caps').set_enabled(can('review'))
                        def track():
                            def action():
                                start_alert_tracking(alert.id)
                                ui.navigate.to(f'/tracking?alert_id={alert.id}')
                            notify_action(action,'Seguimiento iniciado.')
                        ui.button('Iniciar seguimiento',icon='route',on_click=track).props('unelevated no-caps').set_enabled(can('track'))
                    ui.label('Confirmar el evento documenta la revisión; no determina que exista un delito.').classes('text-xs muted')
                    if alert.reviewed_by:
                        ui.label(f'{alert.reviewed_by} · {alert.reviewed_at}').classes('text-xs muted')
            detail()
        def select(alert_id):
            selected['id']=alert_id
            detail.refresh()
            drawer.show()
        @ui.refreshable
        def table():
            rows=[a for a in get_alerts() if state.value=='Todos' or a.status==state.value]
            if query.value:
                text=query.value.lower()
                rows=[a for a in rows if text in (get_alert_event(a).transcript+' '+get_alert_event(a).camera_id).lower()]
            AlertTable(rows,select)
        with ui.element('div').classes('toolbar'):
            query=ui.input('Buscar cámara o frase',on_change=lambda:table.refresh()).props('outlined dense clearable')
            state=ui.select(['Todos','Pendiente de revisión','En revisión','Evento confirmado por operador','Descartada'],value='Todos',label='Estado',on_change=lambda:table.refresh()).props('outlined dense')
            ui.button('Actualizar',icon='refresh',on_click=lambda:table.refresh()).props('outline no-caps')
        table()
        ui.timer(10,table.refresh)
