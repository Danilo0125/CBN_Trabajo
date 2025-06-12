from flask import Flask, render_template, request
from flask_socketio import SocketIO
import os
import sys

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
