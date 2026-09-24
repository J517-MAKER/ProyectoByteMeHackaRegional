from nicegui import ui
from components.layout import PageLayout, Panel
from components.person_profile import PersonProfile
from components.map_view import MapView
from components.timeline import Timeline
from components.states import ErrorState
from services.cases_service import get_case, add_case_photo
from services.users_service import can
from services.tracking_service import get_tracking_history
from services.facial_service import get_matches, search_case_reference


@ui.page('/cases/{case_id}')
def case_detail_page(case_id: str):
    case = get_case(case_id)
    with PageLayout('/cases', 'Detalle del caso', case_id):
        ui.link('← Volver a casos de búsqueda', '/cases').classes('text-xs no-underline')
        if not case:
            ErrorState('No se encontró este expediente.')
            return
        events = get_tracking_history(case_id)

        def review(detection_id):
            match = next((m for m in get_matches(case_id) if m.detection_id == detection_id), None)
            if match:
                ui.navigate.to(f'/matches?case_id={case_id}&match_id={match.id}')
            else:
                from components.detection_detail import DetectionDetail
                DetectionDetail(detection_id)

        @ui.refreshable
        def reference_results():
            with ui.column().classes('w-full gap-2'):
                ui.label('La búsqueda compara la referencia con capturas registradas por las cámaras.').classes('text-xs muted')
                ui.label('Las coincidencias requieren validación humana; no son una identificación definitiva.').classes('text-xs muted')

        def search_cameras():
            try:
                results = search_case_reference(case_id)
                with reference_results:
                    ui.label(f'{len(results)} posible(s) coincidencia(s) encontrada(s)').classes('font-medium')
                    for result in results:
                        ui.label(f'Cámara {result[1]} · similitud {float(result[4]):.1%} · {result[2]}').classes('text-sm')
                ui.notify('Búsqueda en cámaras finalizada. Revisa las posibles coincidencias.', type='positive')
            except (ValueError, OSError, RuntimeError) as error:
                ui.notify(str(error), type='warning')

        with ui.element('div').classes('detail-grid'):
            with ui.column().classes('w-full gap-3'):
                @ui.refreshable
                def profile():
                    PersonProfile(case)
                profile()
                if can('case'):
                    async def upload(event):
                        try:
                            add_case_photo(case_id, await event.file.read(), event.file.content_type)
                            profile.refresh()
                            ui.notify('Fotografía añadida y vinculada a la búsqueda.', type='positive')
                        except (ValueError, PermissionError) as error:
                            ui.notify(str(error), type='warning')
                    ui.upload(label='Añadir referencia fotográfica', on_upload=upload, auto_upload=True,
                              max_file_size=5 * 1024 * 1024,
                              on_rejected=lambda: ui.notify('Imagen rechazada. Máximo 5 MB.', type='warning')).props(
                                  'accept=.png,.jpg,.jpeg,.webp flat bordered').classes('w-full')
                    ui.button('Buscar en cámaras', icon='face_search', on_click=search_cameras).props(
                        'unelevated no-caps').classes('w-full')
                    with ui.card().classes('w-full p-3'):
                        reference_results()
            with ui.column().classes('w-full gap-5'):
                with Panel('Mapa de detecciones', f'{len(events)} DETECCIONES'):
                    MapView(detections=events, height=350)
                with Panel('Secuencia de detecciones', 'REVISIÓN INDIVIDUAL'):
                    with ui.column().classes('panel-body'):
                        Timeline(events, on_review=review)
                ui.button('Abrir seguimiento completo', icon='route',
                          on_click=lambda: ui.navigate.to(f'/tracking?case_id={case_id}')).props('outline no-caps')
