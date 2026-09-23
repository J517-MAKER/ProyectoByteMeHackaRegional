from dataclasses import dataclass


@dataclass
class VoiceEvent:
    id: str
    timestamp: str
    camera_id: str
    transcript: str
    intent: str = 'SOLICITUD_AUXILIO'
    confidence: str = 'Alta'
    subtype: str = 'POSIBLE_SEGUIMIENTO'
    status: str = 'Pendiente de revisión'
