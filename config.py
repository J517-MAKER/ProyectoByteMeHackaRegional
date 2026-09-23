import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
APP_NAME = 'NEXO'
APP_SUBTITLE = 'Sistema de búsqueda y monitoreo'
HOST = os.getenv('NEXO_HOST', '127.0.0.1')
PORT = int(os.getenv('NEXO_PORT', '8080'))
DEMO_DATE = '2026-09-23'
DATA_DIR = BASE_DIR / 'data'

VOICE_MODEL = os.getenv('VOICE_MODEL', 'base')
VOICE_LANGUAGE = 'es'
VOICE_DEMO_MODE = os.getenv('VOICE_DEMO_MODE', 'true').lower() in ('true', '1', 'yes')
AUDIO_SAMPLE_RATE = 16000
AUDIO_MAX_SECONDS = 60
CONTEXT_SECONDS = 20
CONTEXT_MAX_SEGMENTS = 8
CONTEXT_MAX_TEXT = 2000
AUDIO_WINDOW_SECONDS = 6
AUDIO_OVERLAP_SECONDS = 2
AI_CONTEXT_ENABLED = os.getenv('AI_CONTEXT_ENABLED', 'true').lower() in ('true', '1', 'yes')
AI_PROVIDER = os.getenv('AI_PROVIDER', 'ollama')
AI_MODEL = os.getenv('AI_MODEL', 'qwen2.5:3b')
AI_CONTEXT_URL = os.getenv('AI_CONTEXT_URL', 'http://127.0.0.1:11434')
AI_TIMEOUT_SECONDS = 15
ACOUSTIC_CHANGE_RATIO = 2.0
VOICE_RELEVANT_HISTORY_LIMIT = 100

# Continuous monitoring and evidence retention.
EVIDENCE_DIR = BASE_DIR / 'evidence'
EVIDENCE_AUDIO_DIR = EVIDENCE_DIR / 'audio'
EVIDENCE_VIDEO_DIR = EVIDENCE_DIR / 'video'
EVIDENCE_PRE_SECONDS = 10
EVIDENCE_POST_SECONDS = 10
# Ring buffer: pre-roll + window + post-roll with margin. Nothing older is kept.
AUDIO_RING_SECONDS = EVIDENCE_PRE_SECONDS + AUDIO_WINDOW_SECONDS + EVIDENCE_POST_SECONDS + 15
DEFAULT_CAMERA_ID = os.getenv('NEXO_CAMERA', 'CAM-008')
