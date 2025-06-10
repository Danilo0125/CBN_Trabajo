from flask import Flask, render_template, request
from flask_socketio import SocketIO
import os

# Importar módulos refactorizados
from config import Config
from routes.sensores_routes import web_blueprint
from routes.api_routes import api_blueprint
from routes.markov_routes import markov_blueprint
from socket_events import setup_socket_events

# Variables globales (se pueden mover a un módulo de estado si crece más)
datos_recientes = []
sensor_activo = False
maquina_encendida = True
proximo_envio = 0
ultimo_heartbeat = 0
TIMEOUT_SENSOR = 5  # seconds before considering sensor disconnected

# Crear la aplicación Flask con la carpeta estática configurada
app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'secret_key_for_socketio'

# Registrar blueprints
app.register_blueprint(web_blueprint)
app.register_blueprint(api_blueprint, url_prefix='/api')

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

### Iniciar el servidor Flask-SocketIO
if __name__ == '__main__':
    # Ensure required directories exist
    os.makedirs(os.path.join(os.path.dirname(__file__), 'static', 'js'), exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), 'templates'), exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), 'routes'), exist_ok=True)
    
    print(f"Iniciando servidor en http://{Config.HOST}:{Config.PORT}")
    print(f"Accede al dashboard en tu navegador con la URL http://localhost:{Config.PORT}")
    
    # Iniciar el servidor Flask-SocketIO
    socketio.run(app, host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
