from models.alert import EmergencyAlert


def seed_alerts():
    return [EmergencyAlert(f'ALT-{i+1:03d}', f'VOZ-{i+1:03d}',
                           status='Pendiente de revisión' if i<2 else 'En revisión' if i==2 else 'Descartada') for i in range(4)]
