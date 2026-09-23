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

    # NiceGUI no permite <script> dentro de ui.html() — separamos el div del JS
    map_div = f'<div id="google-map" style="width:100%;height:{px_height}px;border-radius:8px;"></div>'

    map_script = f"""
    <script>
      (function() {{
        var MARKERS_DATA = {markers_json};
        var API_KEY = "AIzaSyClKkQmebMNSx550e2kidjW07mXxvlBgHU";

        function buildMap() {{
          var mapElement = document.getElementById("google-map");
          if (!mapElement || mapElement.dataset.mapInit) return;
          mapElement.dataset.mapInit = "1";

          var mexicoBounds = {{
            north: 32.718655, south: 14.532098,
            west: -118.407986, east: -86.710405
          }};

          var map = new google.maps.Map(mapElement, {{
            center: {{ lat: 23.6345, lng: -102.5528 }},
            zoom: 5,
            restriction: {{ latLngBounds: mexicoBounds, strictBounds: false }},
            mapTypeId: 'roadmap',
            styles: [
              {{ elementType: "geometry", stylers: [{{ color: "#242f3e" }}] }},
              {{ elementType: "labels.text.stroke", stylers: [{{ color: "#242f3e" }}] }},
              {{ elementType: "labels.text.fill", stylers: [{{ color: "#746855" }}] }},
              {{ featureType: "water", elementType: "geometry", stylers: [{{ color: "#17263c" }}] }}
            ]
          }});

          MARKERS_DATA.forEach(function(data) {{
            var marker = new google.maps.Marker({{
              position: {{ lat: data.lat, lng: data.lng }},
              map: map,
              title: data.id + " \u00b7 " + data.name + " (" + data.status + ")",
              icon: {{
                path: google.maps.SymbolPath.CIRCLE,
                scale: 8,
                fillColor: data.color,
                fillOpacity: 1,
                strokeColor: "#ffffff",
                strokeWeight: 2
              }}
            }});
            if (data.selected) {{
              map.setCenter({{ lat: data.lat, lng: data.lng }});
              map.setZoom(10);
            }}
          }});

          if (navigator.geolocation && !MARKERS_DATA.some(function(m) {{ return m.selected; }})) {{
            navigator.geolocation.getCurrentPosition(
              function(pos) {{
                new google.maps.Marker({{
                  position: {{ lat: pos.coords.latitude, lng: pos.coords.longitude }},
                  map: map,
                  title: "Tu ubicaci\u00f3n",
                  icon: {{ path: google.maps.SymbolPath.CIRCLE, scale: 10, fillColor: "#4285F4", fillOpacity: 1, strokeColor: "#ffffff", strokeWeight: 3 }}
                }});
              }},
              function() {{ console.warn("Geolocation failed."); }}
            );
          }}
        }}

        function waitForElementAndMaps() {{
          if (document.getElementById("google-map") && typeof google !== 'undefined' && google.maps) {{
            buildMap();
          }} else {{
            var observer = new MutationObserver(function() {{
              if (document.getElementById("google-map") && typeof google !== 'undefined' && google.maps) {{
                observer.disconnect();
                buildMap();
              }}
            }});
            observer.observe(document.body, {{ childList: true, subtree: true }});
          }}
        }}

        if (typeof google === 'undefined' || typeof google.maps === 'undefined') {{
          var s = document.createElement('script');
          s.src = "https://maps.googleapis.com/maps/api/js?key=" + API_KEY + "&loading=async&callback=__gmapsReady";
          s.async = true;
          s.defer = true;
          window.__gmapsReady = function() {{ waitForElementAndMaps(); }};
          document.head.appendChild(s);
        }} else {{
          waitForElementAndMaps();
        }}
      }})();
    </script>
    """

    with ui.element('div').classes('map-stage').style(f'height:{px_height}px; position:relative;'):
        ui.html(map_div).style('width:100%;height:100%;')
        ui.add_body_html(map_script)
        ui.label('MAPA INTERACTIVO · MÉXICO').classes('map-note').style('position:absolute;bottom:10px;right:10px;z-index:1000;')
