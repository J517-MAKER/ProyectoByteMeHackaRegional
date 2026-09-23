import os
import secrets
from nicegui import app,ui
from config import BASE_DIR,HOST,PORT
from assets.build_demo import build_assets

build_assets()
app.add_static_files('/assets',str(BASE_DIR/'assets'))

from pages import monitor,cases,case_detail,cameras,matches,tracking,alerts,voice,history,users,settings  # noqa: E402,F401


@ui.page('/')
def index():
    ui.navigate.to('/monitor')


if __name__ in {'__main__','__mp_main__'}:
    ui.run(host=HOST,port=PORT,title='NEXO · Búsqueda y monitoreo',language='es',
           reload=False,show=os.getenv('NEXO_SHOW','1')=='1',
           storage_secret=os.getenv('NEXO_STORAGE_SECRET') or secrets.token_hex(32),
           favicon='assets/icons/nexo.svg')
