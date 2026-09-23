import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
APP_NAME = 'NEXO'
APP_SUBTITLE = 'Sistema de búsqueda y monitoreo'
HOST = os.getenv('NEXO_HOST', '127.0.0.1')
PORT = int(os.getenv('NEXO_PORT', '8080'))
DEMO_DATE = '2026-09-23'
DATA_DIR = BASE_DIR / 'data'
