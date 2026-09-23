import asyncio
from nicegui import ui
from components.layout import PageLayout,Panel,notify_action
from components.voice_console import VoiceConsole
from components.status_badge import StatusBadge
from services.voice_service import get_voice_events,get_phrases,set_phrases,process_voice_command
from services.cameras_service import get_cameras
from services.history_service import get_history
from services.users_service import can

COMMANDS=['Iniciar búsqueda del folio 184','Detener búsqueda del folio 184','Mostrar última detección del folio 184','Mostrar coincidencias del folio 184','Mostrar cámaras cercanas del folio 184','Continuar seguimiento del folio 184','Marcar coincidencia como incorrecta del folio 184']


@ui.page('/voice')
def voice_page():
    with PageLayout('/voice','Comandos de voz','Detección de auxilio y asistencia a la operación mediante servicios de voz.'):
        with ui.tabs().classes('w-full border-b border-[#dce2e7] justify-start') as tabs:
            detection_tab=ui.tab('Detección de auxilio')
            command_tab=ui.tab('Comandos de autoridad')
            test_tab=ui.tab('Pruebas')
        with ui.tab_panels(tabs,value=detection_tab).classes('w-full'):
            with ui.tab_panel(detection_tab):
                with ui.row().classes('items-center gap-6 mb-6'):
                    StatusBadge('Activo')
                    ui.label('Servicio de voz: SIMULADO').classes('text-xs')
                    ui.label(f'Cámaras con audio: {sum(c.audio for c in get_cameras())}').classes('text-xs muted')
                    event_count=ui.label(f'Eventos de demostración: {len(get_voice_events())}').classes('text-xs muted')
                with ui.element('div').classes('workspace-grid'):
                    with Panel('Eventos recientes','SOLICITUD_AUXILIO'):
                        @ui.refreshable
                        def events():
                            event_count.set_text(f'Eventos de demostración: {len(get_voice_events())}')
                            rows=[{'id':v.id,'time':v.timestamp[11:],'camera':v.camera_id,'text':v.transcript,'type':v.intent,'state':v.status} for v in get_voice_events()]
                            ui.table(columns=[{'name':key,'field':key,'label':label,'align':'left'} for key,label in [('time','Hora'),('camera','Cámara'),('text','Transcripción'),('type','Intención'),('state','Estado')]],rows=rows,row_key='id',pagination=6).classes('w-full')
                        events()
                        ui.button('Actualizar eventos',icon='refresh',on_click=events.refresh).props('flat no-caps').classes('m-3')
                    with Panel('Frases de auxilio','UNA POR LÍNEA'):
                        with ui.column().classes('panel-body'):
                            phrases=ui.textarea(value='\n'.join(get_phrases())).props('outlined autogrow').classes('w-full')
                            phrases.set_enabled(can('settings'))
                            ui.button('Guardar frases',on_click=lambda:notify_action(lambda:set_phrases(phrases.value),'Frases actualizadas.')).props('outline no-caps').set_enabled(can('settings'))
                            if not can('settings'):
                                ui.label('Edición disponible para Supervisor o Administrador.').classes('text-xs muted')
            with ui.tab_panel(command_tab):
                with ui.element('div').classes('workspace-grid'):
                    with Panel('Asistente del operador','ENTRADA SIMULADA'):
                        with ui.column().classes('panel-body gap-4'):
                            mic=ui.label('Micrófono disponible · fuente de prueba').classes('text-sm font-medium')
                            transcription=ui.input('Transcripción',value='mostrar última detección del folio 184').props('outlined').classes('w-full')
                            output=ui.label('En espera de un comando.').classes('console-output')
                            result={'route':None}
                            async def recognize():
                                button.disable()
                                open_button.disable()
                                result['route']=None
                                try:
                                    mic.set_text('Escuchando · simulación')
                                    await asyncio.sleep(.5)
                                    mic.set_text('Procesando')
                                    await asyncio.sleep(.5)
                                    interpreted=process_voice_command(transcription.value)
                                    if interpreted['recognized']:
                                        mic.set_text('Comando reconocido')
                                        output.set_text(f'TRANSCRIPCIÓN\n"{transcription.value}"\n\nACCIÓN / {interpreted["action"]}\nFOLIO / {interpreted["case_id"]}')
                                        result['route']=interpreted['route']
                                        open_button.enable()
                                        command_history.refresh()
                                    else:
                                        mic.set_text('Comando no reconocido')
                                        output.set_text(interpreted['message'])
                                except (PermissionError,ValueError) as error:
                                    mic.set_text('No fue posible procesar el comando')
                                    output.set_text(str(error))
                                finally:
                                    button.enable()
                            with ui.row():
                                button=ui.button('Simular comando',icon='mic',on_click=recognize).props('unelevated no-caps')
                                open_button=ui.button('Abrir resultado',icon='arrow_forward',on_click=lambda:ui.navigate.to(result['route'])).props('outline no-caps')
                                open_button.disable()
                            ui.label('Las decisiones de revisión abren el expediente correspondiente para confirmación humana.').classes('text-xs muted')
                    with ui.column().classes('gap-5 w-full'):
                        with Panel('Comandos disponibles'):
                            with ui.column().classes('panel-body gap-1'):
                                for command in COMMANDS:
                                    ui.button(command,on_click=lambda text=command:transcription.set_value(text)).props('flat no-caps dense align=left').classes('text-left text-xs')
                        with Panel('Historial de comandos'):
                            @ui.refreshable
                            def command_history():
                                records=[r for r in get_history() if r.kind=='Comando de voz']
                                if not records:
                                    ui.label('Todavía no se han ejecutado comandos.').classes('text-xs muted p-4')
                                for record in records[:5]:
                                    ui.label(f'{record.timestamp[11:16]} · {record.description}').classes('text-xs p-3 border-b border-[#edf0f2]')
                            command_history()
            with ui.tab_panel(test_tab):
                with ui.column().classes('panel p-6 gap-3'):
                    VoiceConsole()
