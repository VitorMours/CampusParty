from flask import Blueprint, render_template, request, redirect, url_for
from datetime import datetime
import folium
from folium import Polygon, Marker
from shapely import geometry
from src.serializers.user_serializer import serialize_users
from ..models import collection as db

tiradentes_university_data = {
    "name": "Tiradentes University",
    "functionality": "Education",
    "geometry": geometry.Polygon(
        [   (-37.056482, -10.968238),
            (-37.057893, -10.969664),
            (-37.061729, -10.967321),
            (-37.062448, -10.968490),
            (-37.062560, -10.968443),
            (-37.061911, -10.967185),
            (-37.061697, -10.966136),
            (-37.062126, -10.965926),
            (-37.062179, -10.965799),
            (-37.062099, -10.964768),
            (-37.062024, -10.964762),
            (-37.062029, -10.965015),
            (-37.061750, -10.965115),
            (-37.060087, -10.965194),
            (-37.058773, -10.965741),
            (-37.058816, -10.966420),
            (-37.056423, -10.968174)
        ]
    )
}

bp = Blueprint('campus', __name__)

@bp.route("/", methods=['GET', 'POST'])
def show_form():
    # Se for POST, processar o formulário
    if request.method == 'POST':
        return process_checkin()
    
    # Se for GET, mostrar o formulário
    return render_form()
def render_form():
    """Função para renderizar o formulário com o mapa"""
    # Calcular o centro do polígono para centralizar o mapa
    polygon_coords = list(tiradentes_university_data["geometry"].exterior.coords)
    center_lat = sum(coord[1] for coord in polygon_coords) / len(polygon_coords)
    center_lon = sum(coord[0] for coord in polygon_coords) / len(polygon_coords)
    
    # Criar o mapa centralizado no polígono
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=16,
        tiles='OpenStreetMap'
    )
    
    # Adicionar o polígono da universidade
    folium.Polygon(
        locations=[[coord[1], coord[0]] for coord in polygon_coords],
        popup=tiradentes_university_data["name"],
        tooltip=f"{tiradentes_university_data['name']} - {tiradentes_university_data['functionality']}",
        color='blue',
        fill_color='blue',
        fill_opacity=0.3,
        weight=2
    ).add_to(m)
    
    # Adicionar um marcador no centro
    folium.Marker(
        [center_lat, center_lon],
        popup=tiradentes_university_data["name"],
        tooltip="Centro da Universidade",
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m)
    
    # Buscar usuários do banco de dados
    users = db.find({})
    serialized_users = serialize_users(users)
    
    # Adicionar marcadores para cada usuário
    user_count = 0
    bounds = [[coord[1], coord[0]] for coord in polygon_coords]  # Iniciar bounds com o polígono
    
    for user in serialized_users:
        # Verificar se o usuário tem dados de localização válidos
        if (user.get('location') and 
            user['location'].get('latitude') is not None and 
            user['location'].get('longitude') is not None):
            
            user_count += 1
            lat = user['location']['latitude']
            lon = user['location']['longitude']
            
            # Adicionar ao bounds para ajuste do zoom
            bounds.append([lat, lon])
            
            # Criar conteúdo do popup - CORRIGIDO: usar f-string em vez de Jinja2
            popup_content = f"""
            <div style="min-width: 200px; font-family: Arial, sans-serif;">
                <h4 style="margin: 0 0 8px 0; color: #2563eb; font-weight: bold; border-bottom: 2px solid #2563eb; padding-bottom: 5px;">
                    {user.get('first_name', '')} {user.get('last_name', '')}
                </h4>
                <p style="margin: 6px 0; font-size: 13px;">
                    <strong>📧 Email:</strong> {user.get('email', 'N/A')}
                </p>
                <p style="margin: 6px 0; font-size: 13px;">
                    <strong>📍 Coordenadas:</strong><br>
                    <span style="font-family: monospace; font-size: 11px;">
                    Lat: {lat:.6f}<br>
                    Lon: {lon:.6f}
                    </span>
                </p>
            """
            
            # Adicionar informações de precisão se disponível - CORRIGIDO: usar if Python
            if user['location'].get('accuracy'):
                popup_content += f"""
                <p style="margin: 6px 0; font-size: 13px;">
                    <strong>🎯 Precisão:</strong> ±{user['location']['accuracy']:.1f} metros
                </p>
                """
            
            # Adicionar timestamp se disponível - CORRIGIDO: usar if Python
            if user.get('checkin_time'):
                popup_content += f"""
                <p style="margin: 6px 0; font-size: 13px;">
                    <strong>🕒 Check-in:</strong><br>
                    <span style="font-size: 11px;">{user['checkin_time']}</span>
                </p>
                """
            
            popup_content += "</div>"
            
            # Criar conteúdo do tooltip (aparece ao passar o mouse)
            tooltip_content = f"""
            <div style="font-family: Arial, sans-serif;">
                <strong>👤 {user.get('first_name', '')} {user.get('last_name', '')}</strong><br>
                📧 {user.get('email', 'N/A')}<br>
                📍 {lat:.4f}, {lon:.4f}
            </div>
            """
            
            # Escolher cor do ícone baseado no índice do usuário
            colors = ['green', 'blue', 'purple', 'orange', 'darkred', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple', 'pink', 'lightblue', 'lightgreen', 'gray', 'black']
            color_index = user_count % len(colors)
            
            # Adicionar marcador do usuário
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=folium.Tooltip(tooltip_content, permanent=False),
                icon=folium.Icon(
                    color=colors[color_index], 
                    icon='user', 
                    prefix='fa'
                )
            ).add_to(m)
    
    # Ajustar os limites do mapa para incluir todos os marcadores
    m.fit_bounds(bounds)
    
    # Adicionar legenda se houver usuários
    if user_count > 0:
        legend_html = f'''
        <div style="
            position: fixed; 
            bottom: 50px; 
            left: 50px; 
            width: 220px; 
            height: auto; 
            background-color: white; 
            border: 2px solid grey; 
            z-index: 9999; 
            font-size: 14px;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0,0,0,0.2);
            font-family: Arial, sans-serif;
        ">
            <h4 style="margin-top: 0; margin-bottom: 10px; color: #2563eb;">🏫 Legenda do Campus</h4>
            <p style="margin: 5px 0;">🔴 <strong>Centro da Universidade</strong></p>
            <p style="margin: 5px 0;">🔵 <strong>Área do Campus</strong> (Polígono azul)</p>
            <p style="margin: 5px 0;">
                <span style="color: green;">●</span> 
                <strong>Usuários Registrados</strong> ({user_count} no total)
            </p>
            <p style="margin: 5px 0; font-size: 12px; color: #666;">
                Passe o mouse sobre os marcadores para ver informações
            </p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
    
    # Configurar dimensões para o iframe
    m.get_root().width = "100%"
    m.get_root().height = "500px"
    
    # Gerar o HTML do mapa
    iframe = m.get_root()._repr_html_()
    
    return render_template("index.html", iframe=iframe, users=serialized_users)



@bp.route("/checkin", methods=['GET', 'POST'])
def process_checkin():
    """Função para processar o check-in"""
    try:
        # Capturar dados do formulário
        nome = request.form.get('nome')
        sobrenome = request.form.get('sobrenome')
        email = request.form.get('email')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        accuracy = request.form.get('accuracy')
        
        # Validar dados
        if not all([nome, sobrenome, email]):
            return "Todos os campos são obrigatórios", 400
        
        if not all([latitude, longitude]):
            return "Localização é necessária para registrar presença", 400
        
        # Inserir no banco de dados com localização
        user_data = {
            "first_name": nome,
            "last_name": sobrenome,
            "email": email,
            "location": {
                "latitude": float(latitude),
                "longitude": float(longitude),
                "accuracy": float(accuracy) if accuracy else None
            },
            "checkin_time": datetime.now()
        }
        
        result = db.insert_one(user_data)
        
        # Redirecionar para a página principal com mensagem de sucesso
        return redirect(url_for('campus.show_form'))
        
    except Exception as e:
        return f"Erro ao processar check-in: {str(e)}", 500