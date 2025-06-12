from flask import Flask, render_template, request
from flask_socketio import SocketIO
import os
import sys
import random
import time
from datetime import datetime

from config import Config
from routes.sensores_routes import web_blueprint
from routes.api_routes import api_blueprint
from routes.maquina_routes import maquina_blueprint
from routes.markov_routes import markov_blueprint
from routes.monitoreo_routes import monitoreo_blueprint  # Nuevo import
from socket_events import setup_socket_events
from database.database import get_database_uri, ensure_database_exists

# Load the predictive model
from modelo_predictivo import modelo_prediccion

# Variables globales (se pueden mover a un módulo de estado si crece más)
datos_recientes = []
sensor_activo = False
maquina_encendida = True
proximo_envio = 0
ultimo_heartbeat = 0
TIMEOUT_SENSOR = 5  # seconds before considering sensor disconnected

# Asegurar que la base de datos existe
ensure_database_exists()

# Crear la aplicación Flask con la carpeta estática configurada
app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'secret_key_for_socketio'
app.config['SQLALCHEMY_DATABASE_URI'] = get_database_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Importar e inicializar la base de datos
from database.Modelos import db
db.init_app(app)

# Registrar blueprints con nombres únicos para evitar conflictos
app.register_blueprint(web_blueprint)
app.register_blueprint(api_blueprint, url_prefix='/api')
app.register_blueprint(maquina_blueprint, name='maquinas')
app.register_blueprint(markov_blueprint, name='markov')
app.register_blueprint(monitoreo_blueprint, name='monitoreo')  # Nuevo blueprint

# Importar el registrador de rutas de simulación
from routes.simulacion_rutas import registrar_rutas_simulacion

# Registrar rutas (agregar esto donde registras otras rutas)
registrar_rutas_simulacion(app)

# Inicializar Socket.IO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Configurar eventos de socket
setup_socket_events(socketio, datos_recientes, sensor_activo, maquina_encendida, 
                    proximo_envio, ultimo_heartbeat, TIMEOUT_SENSOR)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('CadenaMarkov.html', mensaje="Página no encontrada"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('CadenaMarkov.html', mensaje="Error interno del servidor"), 500

# Asegurar que las tablas existen
with app.app_context():
    db.create_all()
    print("Tablas de base de datos verificadas/creadas")

def generar_datos_simulacion():
    """
    Genera datos simulados para los sensores y los guarda en la variable global
    datos_recientes para que estén disponibles a través de la API
    """
    # Generar datos simulados
    timestamp = datetime.now().isoformat()
    temperatura = round(random.uniform(50, 80), 1)  # Temperatura entre 50°C y 80°C
    vibracion = round(random.uniform(2, 8), 2)      # Vibración entre 2 y 8 mm/s
    presion = round(random.uniform(100, 300), 0)    # Presión entre 100 y 300 bar
    
    # Crear predicción simulada de IA
    is_critical = random.random() < 0.05  # 5% de probabilidad de estado crítico
    action = 1 if random.random() < 0.3 else 0  # 30% de probabilidad de recomendar mantenimiento
    
    prediccion = {
        "action": action,
        "is_critical": is_critical,
        "raw_data": [temperatura, vibracion, presion],
        "confidence": random.random()
    }
    
    # Crear datos del sensor
    datos = {
        "timestamp": timestamp,
        "temperatura": temperatura,
        "vibracion": vibracion,
        "presion": presion,
        "prediccion": prediccion
    }
    
    # Guardar en datos_recientes
    datos_recientes.append(datos)
    
    # Mantener solo los últimos 1000 datos
    if len(datos_recientes) > 1000:
        datos_recientes.pop(0)
    
    return datos

### Iniciar el servidor Flask-SocketIO
if __name__ == '__main__':
    # Ensure required directories exist
    os.makedirs(os.path.join(os.path.dirname(__file__), 'static', 'js'), exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), 'templates'), exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), 'routes'), exist_ok=True)
    
    print(f"Iniciando servidor en http://{Config.HOST}:{Config.PORT}")
    print(f"Accede al dashboard en tu navegador con la URL http://localhost:{Config.PORT}")
    print(f"Modelo predictivo cargado: {'Sí' if modelo_prediccion.model is not None else 'No'}")
    
    # Iniciar el servidor Flask-SocketIO
    socketio.run(app, host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
