from dataclasses import dataclass


@dataclass
class EmergencyAlert:
    id: str
    voice_event_id: str
    status: str = 'Pendiente de revisión'
    reviewed_by: str = ''
    reviewed_at: str = ''
    tracking_started: bool = False
