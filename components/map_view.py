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

    map_id = f'leaflet-map-{abs(hash(markers_json)) % 999999}'

    # Leaflet CSS + JS — gratuito, sin API key, sin facturación
    leaflet_head = """
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" crossorigin=""/>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" crossorigin=""></script>
    <style>
      .user-dot {
        width: 16px; height: 16px;
        background: #4285F4;
        border: 3px solid #fff;
        border-radius: 50%;
        box-shadow: 0 0 0 4px rgba(66,133,244,0.35);
        animation: pulse-ring 1.8s ease-out infinite;
      }
      @keyframes pulse-ring {
        0%   { box-shadow: 0 0 0 0   rgba(66,133,244,0.5); }
        70%  { box-shadow: 0 0 0 12px rgba(66,133,244,0); }
        100% { box-shadow: 0 0 0 0   rgba(66,133,244,0); }
      }
    </style>
    """

    map_div = f'<div id="{map_id}" style="width:100%;height:{px_height}px;border-radius:8px;z-index:0;"></div>'

    map_script = f"""
    <script>
    (function() {{
      var MAP_ID       = "{map_id}";
      var MARKERS_DATA = {markers_json};

      function svgIcon(color, size) {{
        size = size || 10;
        var svg = '<svg xmlns="http://www.w3.org/2000/svg" width="' + (size*2) + '" height="' + (size*2) + '">'
          + '<circle cx="' + size + '" cy="' + size + '" r="' + (size-2) + '" fill="' + color + '" stroke="#fff" stroke-width="2"/>'
          + '</svg>';
        return L.icon({{
          iconUrl: 'data:image/svg+xml;base64,' + btoa(svg),
          iconSize: [size*2, size*2],
          iconAnchor: [size, size],
          popupAnchor: [0, -size]
        }});
      }}

      function initMap() {{
        var el = document.getElementById(MAP_ID);
        if (!el || el._leafletMap) return;

        var defaultCenter = [23.6345, -102.5528];
        var defaultZoom  = 5;

        // Centrar en cámara seleccionada si existe
        var sel = MARKERS_DATA.find(function(m) {{ return m.selected; }});
        if (sel) {{ defaultCenter = [sel.lat, sel.lng]; defaultZoom = 10; }}

        var map = L.map(MAP_ID, {{ center: defaultCenter, zoom: defaultZoom, zoomControl: true }});
        el._leafletMap = map;

        // Tiles oscuros CartoDB Dark Matter — gratuitos, sin API key
        L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
          attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/">CARTO</a>',
          subdomains: 'abcd',
          maxZoom: 19
        }}).addTo(map);

        // Marcadores de cámaras
        MARKERS_DATA.forEach(function(data) {{
          var size = data.selected ? 14 : 10;
          var marker = L.marker([data.lat, data.lng], {{ icon: svgIcon(data.color, size) }}).addTo(map);
          marker.bindPopup(
            '<b>' + data.id + '</b><br>' + data.name + '<br><span style="color:' + data.color + '">' + data.status + '</span>'
          );
          if (data.selected) {{ marker.openPopup(); }}
        }});

        // Ubicación actual del usuario — marcador pulsante azul
        if (navigator.geolocation) {{
          navigator.geolocation.getCurrentPosition(
            function(pos) {{
              var lat = pos.coords.latitude;
              var lng = pos.coords.longitude;
              var acc = pos.coords.accuracy;

              var userIcon = L.divIcon({{
                className: '',
                html: '<div class="user-dot"></div>',
                iconSize: [16, 16],
                iconAnchor: [8, 8]
              }});

              var userMarker = L.marker([lat, lng], {{ icon: userIcon, zIndexOffset: 1000 }}).addTo(map);
              userMarker.bindPopup('<b>Tu ubicación actual</b><br>Precisión: ' + Math.round(acc) + ' m');

              // Círculo de precisión
              L.circle([lat, lng], {{
                radius: acc,
                color: '#4285F4',
                fillColor: '#4285F4',
                fillOpacity: 0.08,
                weight: 1
              }}).addTo(map);

              // Solo centra en el usuario si no hay cámara seleccionada
              if (!MARKERS_DATA.some(function(m) {{ return m.selected; }})) {{
                map.setView([lat, lng], 14);
              }}
            }},
            function(err) {{ console.warn('Geolocalización no disponible:', err.message); }},
            {{ enableHighAccuracy: true, timeout: 10000 }}
          );
        }}
      }}

      function waitAndInit() {{
        if (document.getElementById(MAP_ID) && typeof L !== 'undefined') {{
          initMap();
        }} else {{
          setTimeout(waitAndInit, 150);
        }}
      }}
      waitAndInit();
    }})();
    </script>
    """

    ui.add_head_html(leaflet_head)
    with ui.element('div').classes('map-stage').style(f'height:{px_height}px; position:relative;'):
        ui.html(map_div).style('width:100%;height:100%;')
        ui.add_body_html(map_script)
        ui.label('MAPA INTERACTIVO · MÉXICO').classes('map-note').style('position:absolute;bottom:10px;right:10px;z-index:1000;')
