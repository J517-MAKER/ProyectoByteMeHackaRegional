from models.voice_event import VoiceEvent

PHRASES = ['ayuda', 'auxilio', 'necesito ayuda', 'me están siguiendo', 'alguien me sigue', 'déjame', 'aléjate de mí', 'llama a la policía']


def seed_voice_events():
    return [VoiceEvent(f'VOZ-{i+1:03d}', f'2026-09-23 09:{39-i*5:02d}:03',
                       ['CAM-008','CAM-002','CAM-005','CAM-011','CAM-014'][i], phrase,
                       subtype='POSIBLE_SEGUIMIENTO' if i==0 else 'AUXILIO_GENERAL')
            for i,phrase in enumerate(['ayuda, me están siguiendo','necesito ayuda','auxilio','llama a la policía','ayuda'])]
