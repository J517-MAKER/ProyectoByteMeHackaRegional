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
        
    markers_json = json.dumps(markers_data)
    
    map_html = f"""
    <div id="google-map" style="width: 100%; height: 100%; border-radius: 8px;"></div>
    <script>
      function initMap() {{
        const mexicoBounds = {{
            north: 32.718655,
            south: 14.532098,
            west: -118.407986,
            east: -86.710405
        }};
        const mapElement = document.getElementById("google-map");
        if (!mapElement) return;
        
        const map = new google.maps.Map(mapElement, {{
          center: {{ lat: 23.6345, lng: -102.5528 }},
          zoom: 5,
          restriction: {{
            latLngBounds: mexicoBounds,
            strictBounds: false,
          }},
          mapTypeId: 'roadmap',
          styles: [
            {{ elementType: "geometry", stylers: [{{ color: "#242f3e" }}] }},
            {{ elementType: "labels.text.stroke", stylers: [{{ color: "#242f3e" }}] }},
            {{ elementType: "labels.text.fill", stylers: [{{ color: "#746855" }}] }},
            {{
              featureType: "water",
              elementType: "geometry",
              stylers: [{{ color: "#17263c" }}],
            }},
          ]
        }});
        
        // Agregar marcadores dinámicos
        const markersData = {markers_json};
        markersData.forEach(data => {{
            // Custom marker icon usando el color calculado
            const pinIcon = new google.maps.MarkerImage(
                "http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|" + data.color.replace('#', ''),
                new google.maps.Size(21, 34),
                new google.maps.Point(0,0),
                new google.maps.Point(10, 34)
            );
            
            const marker = new google.maps.Marker({{
                position: {{ lat: data.lat, lng: data.lng }},
                map: map,
                title: data.id + " · " + data.name + " (" + data.status + ")",
                icon: pinIcon
            }});
            
            if (data.selected) {{
                map.setCenter({{ lat: data.lat, lng: data.lng }});
                map.setZoom(10);
            }}
        }});
        
        if (navigator.geolocation && !markersData.some(m => m.selected)) {{
          navigator.geolocation.getCurrentPosition(
            (position) => {{
              const pos = {{
                lat: position.coords.latitude,
                lng: position.coords.longitude,
              }};
              new google.maps.Marker({{
                position: pos,
                map: map,
                title: "Tu ubicación",
                icon: "http://maps.google.com/mapfiles/ms/icons/blue-dot.png"
              }});
            }},
            () => {{ console.warn("Geolocation failed."); }}
          );
        }}
      }}
      
      if (typeof google === 'undefined' || typeof google.maps === 'undefined') {{
          const script = document.createElement('script');
          script.src = "https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY_HERE&callback=initMap";
          script.async = true;
          script.defer = true;
          window.initMap = initMap;
          document.head.appendChild(script);
      }} else {{
          setTimeout(initMap, 100);
      }}
    </script>
    """
    
    with ui.element('div').classes('map-stage').style(f'height:{height}px; position:relative;' if height else 'height: 500px; position:relative;'):
        ui.html(map_html).classes('w-full h-full')
        ui.label('MAPA INTERACTIVO · MÉXICO').classes('map-note').style('position: absolute; bottom: 10px; right: 10px; z-index: 1000;')
