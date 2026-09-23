from nicegui import ui
from services.alerts_service import get_alert_event
from services.cameras_service import get_camera
from components.states import EmptyState


def AlertTable(alerts,on_select):
    if not alerts:
        EmptyState()
        return
    rows=[]
    for alert in alerts:
        event=get_alert_event(alert)
        rows.append({'id':alert.id,'time':event.timestamp,'camera':event.camera_id,'location':get_camera(event.camera_id).location,
                     'phrase':event.transcript,'type':'Posible solicitud de auxilio','confidence':event.confidence,'status':alert.status})
    columns=[{'name':key,'label':label,'field':key,'align':'left','sortable':True} for key,label in
             [('time','Fecha / hora'),('camera','Cámara'),('location','Ubicación'),('phrase','Frase detectada'),('type','Tipo de evento'),('confidence','Confianza'),('status','Estado')]]
    columns.append({'name':'actions','label':'Acciones','field':'id','align':'left'})
    table=ui.table(columns=columns,rows=rows,row_key='id',pagination=8).classes('w-full')
    table.add_slot('body-cell-actions','<q-td :props="props"><q-btn flat dense no-caps color="primary" label="Revisar" @click="$parent.$emit(\'review\', props.row.id)" /></q-td>')
    table.on('review',lambda e:on_select(e.args))
