from nicegui import ui
from components.status_badge import StatusBadge


def CameraFeed(camera,on_select=None):
    with ui.element('div').classes('camera-tile '+('event' if camera.status in ('Alerta','Posible coincidencia') else '')).props('tabindex=0 role=button') as tile:
        if on_select:
            tile.on('click',lambda:on_select(camera.id))
            tile.on('keydown.enter',lambda:on_select(camera.id))
        with ui.element('div').classes('camera-stage'):
            ui.image(f'/assets/demo/cctv-{int(camera.id[-3:])%3+1}.svg').props('no-spinner')
            with ui.element('div').classes('camera-overlay'):
                with ui.element('div').classes('camera-top'):
                    ui.label(camera.id)
                    ui.label('REPRODUCCIÓN DEMO')
                with ui.element('div').classes('camera-bottom'):
                    ui.label('23 SEP 2026 / 10:28:04')
                    ui.icon('volume_up' if camera.audio else 'volume_off',size='13px')
            if camera.status=='Desconectada':
                with ui.element('div').classes('camera-offline'):
                    ui.icon('videocam_off',size='30px')
                    ui.label('Sin señal · cámara desconectada')
        with ui.element('div').classes('camera-caption'):
            ui.label(camera.name)
            StatusBadge(camera.status)
