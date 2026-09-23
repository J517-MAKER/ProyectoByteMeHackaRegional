# pyrefly: ignore [missing-import]
from nicegui import ui
import json
from services.cameras_service import get_cameras

COLORS = {'En línea':'#487965','Desconectada':'#8d999f','Alerta':'#b4544c','Posible coincidencia':'#bc9246'}

def MapView(cameras=None,detections=None,selected=None,on_select=None,height=None):
    cameras = get_cameras() if cameras is None else cameras
    detection_list = [event.detection for event in (detections or [])]
    
    # Preparamos los datos de las cámaras para inyectarlos en JS
    markers_data = []
    for camera in cameras:
        # Interpolamos X,Y (0-100) a Lat,Lng dentro de México
        # Lat: 14.53 a 32.71 -> Rango = 18.18 (y invertido: 100=sur, 0=norte)
        # Lng: -118.4 a -86.7 -> Rango = 31.7
        lat = 32.718655 - (camera.y / 100.0) * 18.186557
        lng = -118.407986 + (camera.x / 100.0) * 31.697581
        
        detection = next((d for d in reversed(detection_list) if d.camera_id==camera.id), None)
        status = detection.status if detection else camera.status
        color = '#487965' if status == 'Validada por operador' else '#8d999f' if status == 'Descartada' else '#bc9246' if detection else COLORS.get(camera.status, '#000000')
        if selected == camera.id:
            color = '#245f83'
            
        markers_data.append({
            'id': camera.id,
            'name': camera.name,
            'lat': lat,
            'lng': lng,
            'status': status,
            'color': color,
            'selected': selected == camera.id
        })
        
    px_height = height if height else 500
    markers_json = json.dumps(markers_data)

    map_id = f'mapbox-map-{abs(hash(markers_json)) % 999999}'

    mapbox_head = """
    <script src='https://api.mapbox.com/mapbox-gl-js/v3.1.2/mapbox-gl.js'></script>
    <link href='https://api.mapbox.com/mapbox-gl-js/v3.1.2/mapbox-gl.css' rel='stylesheet' />
    <style>
      .mapbox-marker-user {
        width: 16px; height: 16px;
        background: #4285F4;
        border: 3px solid #fff;
        border-radius: 50%;
        box-shadow: 0 0 0 4px rgba(66,133,244,0.35);
        animation: pulse-ring 1.8s ease-out infinite;
      }
      .mapbox-marker-camera {
        width: 20px; height: 20px;
        border: 2px solid #fff;
        border-radius: 50%;
        box-shadow: 0 2px 4px rgba(0,0,0,0.5);
      }
      .mapbox-marker-camera.selected {
        width: 28px; height: 28px;
        border-width: 3px;
        z-index: 10;
      }
      @keyframes pulse-ring {
        0%   { box-shadow: 0 0 0 0   rgba(66,133,244,0.5); }
        70%  { box-shadow: 0 0 0 12px rgba(66,133,244,0); }
        100% { box-shadow: 0 0 0 0   rgba(66,133,244,0); }
      }
      /* Custom Popup Style */
      .mapboxgl-popup-content {
        background: #242f3e;
        color: #fff;
        border-radius: 8px;
        padding: 10px 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
      }
      .mapboxgl-popup-anchor-bottom .mapboxgl-popup-tip {
        border-top-color: #242f3e;
      }
    </style>
    """

    map_div = f'<div id="{map_id}" style="width:100%;height:{px_height}px;border-radius:8px;z-index:0;"></div>'

    map_script = f"""
    <script>
    (function() {{
      var MAP_ID       = "{map_id}";
      var MARKERS_DATA = {markers_json};
      var MAPBOX_TOKEN = "pk.eyJ1IjoicGVwaW5pbGxveGQwMiIsImEiOiJjbXVlaG5sYTEwM3ltMndwd3I2MmZsdnRkIn0.AhOAZHe825gJhc4Y_uiwDg";

      function initMap() {{
        var el = document.getElementById(MAP_ID);
        if (!el || el._mapboxMap) return;

        mapboxgl.accessToken = MAPBOX_TOKEN;

        var defaultCenter = [-102.5528, 23.6345]; // Lng, Lat
        var defaultZoom  = 4.5;

        // Centrar en cámara seleccionada si existe
        var sel = MARKERS_DATA.find(function(m) {{ return m.selected; }});
        if (sel) {{ defaultCenter = [sel.lng, sel.lat]; defaultZoom = 10; }}

        var map = new mapboxgl.Map({{
          container: MAP_ID,
          style: 'mapbox://styles/mapbox/dark-v11', // Dark style
          center: defaultCenter,
          zoom: defaultZoom
        }});
        el._mapboxMap = map;

        // Navigation controls
        map.addControl(new mapboxgl.NavigationControl(), 'top-right');

        // Marcadores de cámaras
        MARKERS_DATA.forEach(function(data) {{
          var el = document.createElement('div');
          el.className = 'mapbox-marker-camera' + (data.selected ? ' selected' : '');
          el.style.backgroundColor = data.color;

          var popup = new mapboxgl.Popup({{ offset: 25 }}).setHTML(
            '<b>' + data.id + '</b><br>' + data.name + '<br><span style="color:' + data.color + '">' + data.status + '</span>'
          );

          var marker = new mapboxgl.Marker(el)
            .setLngLat([data.lng, data.lat])
            .setPopup(popup)
            .addTo(map);

          if (data.selected) {{
            marker.togglePopup();
          }}
        }});

        // Ubicación actual del usuario
        if (navigator.geolocation) {{
          navigator.geolocation.getCurrentPosition(
            function(pos) {{
              var lat = pos.coords.latitude;
              var lng = pos.coords.longitude;

              var el = document.createElement('div');
              el.className = 'mapbox-marker-user';

              var popup = new mapboxgl.Popup({{ offset: 15 }}).setHTML(
                '<b>Tu ubicación actual</b><br>Precisión: ' + Math.round(pos.coords.accuracy) + ' m'
              );

              new mapboxgl.Marker(el)
                .setLngLat([lng, lat])
                .setPopup(popup)
                .addTo(map);

              // Solo centra en el usuario si no hay cámara seleccionada
              if (!MARKERS_DATA.some(function(m) {{ return m.selected; }})) {{
                map.flyTo({{ center: [lng, lat], zoom: 12, essential: true }});
              }}
            }},
            function(err) {{ console.warn('Geolocalización no disponible:', err.message); }},
            {{ enableHighAccuracy: true, timeout: 10000 }}
          );
        }}
      }}

      function waitAndInit() {{
        if (document.getElementById(MAP_ID) && typeof mapboxgl !== 'undefined') {{
          initMap();
        }} else {{
          setTimeout(waitAndInit, 150);
        }}
      }}
      waitAndInit();
    }})();
    </script>
    """

    ui.add_head_html(mapbox_head)
    with ui.element('div').classes('map-stage').style(f'height:{px_height}px; position:relative;'):
        ui.html(map_div).style('width:100%;height:100%;')
        ui.add_body_html(map_script)
        ui.label('MAPA INTERACTIVO · MÉXICO').classes('map-note').style('position:absolute;bottom:10px;right:10px;z-index:1000;')
