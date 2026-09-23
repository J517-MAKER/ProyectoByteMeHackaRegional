import asyncio
from nicegui import ui
from components.layout import notify_action
from services.voice_service import simulate_voice_event
from services.cameras_service import get_cameras


def VoiceConsole():
    state={'generation':0,'running':False}
    ui.label('Consola de pruebas de voz').classes('section-title')
    ui.label('Simulación reemplazable. No accede al micrófono ni transcribe audio real.').classes('subtitle')
    with ui.row().classes('w-full gap-3'):
        transcript=ui.input('Transcripción de prueba',value='ayuda, me están siguiendo').props('outlined dense').classes('flex-1')
        camera=ui.select({c.id:f'{c.id} · {c.name}' for c in get_cameras() if c.audio and c.status!='Desconectada'},value='CAM-008',label='Cámara con audio').props('outlined dense').classes('w-64')
    labels=[]
    with ui.element('div').classes('voice-flow'):
        for index,step in enumerate(['Micrófono','Audio recibido','Transcripción','Intención','Evento','Resultado']):
            if index:
                ui.icon('arrow_forward',size='15px',color='blue-grey-4')
            labels.append(ui.label(step).classes('voice-step'))
    with ui.row().classes('items-center gap-4'):
        ui.label('Nivel de audio simulado').classes('text-xs muted')
        with ui.element('div').classes('level-bars'):
            for height in [6,13,9,20,33,18,42,29,16,37,25,13,30,45,23,11,19,31,16,8]:
                ui.element('span').style(f'height:{height}px')
    output=ui.label('LISTO\nEntrada de audio: servicio mock\nPresiona «Iniciar prueba» para ejecutar la secuencia.').classes('console-output')
    async def start():
        if state['running']:
            return
        state['generation']+=1
        generation=state['generation']
        state['running']=True
        start_button.disable()
        transcript.disable()
        camera.disable()
        stop_button.enable()
        for label in labels:
            label.classes(remove='done')
        lines=['MICRÓFONO / Fuente de prueba disponible','AUDIO RECIBIDO / Señal simulada',f'TRANSCRIPCIÓN / "{transcript.value}"','INTENCIÓN / Analizando frases configuradas','EVENTO / Preparando resultado']
        try:
            for index,line in enumerate(lines):
                if state['generation']!=generation:
                    return
                labels[index].classes(add='done')
                output.set_text('\n'.join(lines[:index+1]))
                await asyncio.sleep(.65)
            if state['generation']!=generation:
                return
            event=simulate_voice_event(transcript.value,camera.value)
            if event:
                output.set_text(f'AUDIO RECIBIDO / Prueba sintética\nTRANSCRIPCIÓN / "{event.transcript}"\nINTENCIÓN / {event.intent}\nSUBTIPO / {event.subtype}\nCÁMARA / {event.camera_id}\nRESULTADO / Evento enviado correctamente. Pendiente de revisión.')
                ui.notify('Posible solicitud de auxilio enviada a revisión.',position='bottom-right',type='positive')
            else:
                output.set_text(f'TRANSCRIPCIÓN / "{transcript.value}"\nINTENCIÓN / NO_RECONOCIDA\nRESULTADO / No se generó un evento. Ninguna frase configurada coincide.')
            labels[-1].classes(add='done')
        except (ValueError,PermissionError,ConnectionError) as error:
            output.set_text(f'ERROR / {error}\nNo se generó un evento.')
            ui.notify(str(error),type='warning')
        finally:
            if state['generation']==generation:
                state['running']=False
                start_button.enable()
                transcript.enable()
                camera.enable()
                stop_button.disable()
    def stop():
        state['generation']+=1
        state['running']=False
        output.set_text('PRUEBA DETENIDA / No se generó ningún evento.')
        start_button.enable()
        transcript.enable()
        camera.enable()
        stop_button.disable()
    with ui.row().classes('mt-4 gap-3'):
        start_button=ui.button('Iniciar prueba',icon='play_arrow',on_click=start).props('unelevated no-caps').mark('voice-start')
        stop_button=ui.button('Detener',icon='stop',on_click=stop).props('outline no-caps').mark('voice-stop')
        stop_button.disable()
        ui.button('Ver alertas',on_click=lambda:ui.navigate.to('/alerts')).props('flat no-caps')
