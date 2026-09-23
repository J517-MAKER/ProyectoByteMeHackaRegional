import asyncio
import logging
import os
import tempfile
import unittest
from contextlib import asynccontextmanager
from pathlib import Path
from unittest.mock import patch

from nicegui import ui
from nicegui.testing import user_simulation
from nicegui.storage import Storage


@asynccontextmanager
async def simulation():
    # NiceGUI's test reset expects these fixture flags even with unittest.
    with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ,{'PYTEST_CURRENT_TEST':'unittest','NICEGUI_SCREEN_TEST_PORT':'8081'}), patch.object(Storage,'path',Path(directory)/'storage'):
        async with user_simulation(main_file=Path(__file__).resolve().parents[1]/'main.py') as user:
            yield user


class ErrorCollector(logging.Handler):
    def __init__(self):
        super().__init__(logging.ERROR)
        self.messages=[]

    def emit(self,record):
        self.messages.append(record.getMessage())


class DemoFlowTest(unittest.IsolatedAsyncioTestCase):
    async def test_operator_demo_end_to_end(self):
        collector=ErrorCollector()
        logging.getLogger().addHandler(collector)
        try:
            async with simulation() as user:
                from services import store
                from services.users_service import switch_demo_user,update_user
                from services.cases_service import create_case,photo_data_url
                from services.voice_service import process_voice_command

                for route,title in [('/monitor','Centro de monitoreo'),('/cases','Casos de búsqueda'),
                                    ('/cases/BUS-2026-0184','Detalle del caso'),('/cameras','Red de cámaras'),
                                    ('/matches','Revisión de coincidencias'),('/tracking','Mapa y seguimiento'),
                                    ('/alerts','Alertas de auxilio'),('/voice','Comandos de voz'),
                                    ('/history','Historial de operaciones'),('/users','Usuarios y permisos'),
                                    ('/settings','Configuración')]:
                    await user.open(route)
                    await user.should_see(content=title,marker='page-title')

                await user.open('/cases')
                user.find('Buscar nombre o folio').type('sin coincidencias de prueba')
                await user.should_see('No hay registros para los filtros seleccionados.')
                user.find('Buscar nombre o folio').clear()
                user.find('Nueva búsqueda').click()
                user.find('Nombre completo *').type('Persona de prueba QA')
                user.find('Registrar caso y procesar referencias').click()
                await asyncio.sleep(.2)
                await user.should_see('Persona de prueba QA')
                self.assertEqual(store.cases[-1].person.name,'Persona de prueba QA')
                self.assertEqual(store.cases[-1].reference_status,'Sin referencia fotográfica')

                await user.open('/matches?match_id=MAT-001')
                user.find('Validar como posible coincidencia').click()
                self.assertEqual(store.matches[0].reviewed_by,'Operador01')
                self.assertEqual(store.detections[0].status,'Validada por operador')
                await user.should_see('Revisión registrada: Operador01')
                user.find('Descartar').click()
                self.assertEqual(store.detections[0].status,'Descartada')
                user.find('Solicitar revisión').click()
                self.assertEqual(store.matches[0].status,'En revisión')

                await user.open('/cameras?camera_id=CAM-010')
                await user.should_see('Conexión perdida.')
                user.find('Reintentar conexión').click()
                await user.should_see('No fue posible conectar con la cámara.')

                await user.open('/voice')
                user.find('Pruebas').click()
                count=len(store.alerts)
                user.find(marker='voice-start').click()
                await asyncio.sleep(.15)
                user.find(marker='voice-stop').click()
                await asyncio.sleep(.75)
                self.assertEqual(len(store.alerts),count)
                await user.should_see('PRUEBA DETENIDA')
                user.find(marker='voice-start').click()
                await asyncio.sleep(3.6)
                await user.should_see('Evento enviado correctamente')
                self.assertEqual(len(store.alerts),count+1)
                alert=store.alerts[0]
                self.assertEqual(store.voice_events[0].intent,'SOLICITUD_AUXILIO')

                await user.open('/alerts')
                user.find(ui.table).trigger('review',alert.id)
                await user.should_see('Confirmar evento')
                user.find('Confirmar evento').click()
                self.assertEqual(alert.reviewed_by,'Operador01')
                user.find('Iniciar seguimiento').click()
                await asyncio.sleep(.2)
                self.assertTrue(alert.tracking_started)
                await user.should_see('Evento independiente de los casos')

                await user.open('/voice')
                user.find('Comandos de autoridad').click()
                user.find('Simular comando').click()
                await asyncio.sleep(1.2)
                await user.should_see('MOSTRAR_ULTIMA_DETECCION')
                user.find('Abrir resultado').click()
                await asyncio.sleep(.2)
                await user.should_see('Mapa y seguimiento')
                with user:
                    self.assertFalse(process_voice_command('mensaje sin intención')['recognized'])
                    with self.assertRaises(PermissionError):
                        update_user('USR-02','Supervisor','Activo')
                    with self.assertRaises(ValueError):
                        create_case({'name':''})
                    with self.assertRaises(ValueError):
                        photo_data_url(b'not an image','image/png')
                    switch_demo_user('USR-04')
                await user.open('/users')
                user.find(ui.table).trigger('edit','USR-02')
                await user.should_see('Permisos / Operador02')
                with user:
                    update_user('USR-02','Supervisor','Activo')
                    with self.assertRaises(ValueError):
                        update_user('USR-04','Operador','Activo')
                self.assertEqual(store.users[1].role,'Supervisor')
                self.assertTrue(any(log.kind=='Permisos' for log in store.logs))
                await user.open('/cases/no-existe')
                await user.should_see('No se encontró este expediente.')
                await asyncio.sleep(.2)
            self.assertEqual(collector.messages,[])
        finally:
            logging.getLogger().removeHandler(collector)


if __name__=='__main__':
    unittest.main()
