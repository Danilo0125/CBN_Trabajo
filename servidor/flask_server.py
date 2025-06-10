from flask import Flask
from flask_socketio import SocketIO
import threading
import time
import os
from datetime import datetime

# Importar módulos refactorizados
from config import Config
from servidor.routes.sensores_routes import web_blueprint
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

def generar_datos_tiempo_real():
    return {
        'timestamp': datetime.now().isoformat(),
        'temperatura': 0,
        'vibracion': 0,
        'presion': 0
    }

def generar_y_enviar_datos():
    """Función que genera y envía datos en cero cada segundo cuando el sensor no está activo"""
    global proximo_envio, sensor_activo, ultimo_heartbeat
    
    # Inicializar la variable para el tiempo del próximo envío
    proximo_envio = time.time() + 1.0
    ultimo_heartbeat = time.time()  # Initialize heartbeat timer
    
    print("Servidor listo - esperando conexión del sensor...")
    
    while True:
        try:
            # Tiempo actual
            tiempo_actual = time.time()
            
            # Verificar si el sensor está activo pero ha dejado de enviar heartbeats
            if sensor_activo and (tiempo_actual - ultimo_heartbeat > TIMEOUT_SENSOR):
                print("⚠️ Sensor perdido - no se ha recibido heartbeat en", round(tiempo_actual - ultimo_heartbeat, 1), "segundos")
                sensor_activo = False
                # Notificar a todos los clientes que el sensor se ha desconectado
                socketio.emit('estado_sensores', {'activos': False, 'cantidad': 0})
            
            # Verificar si es momento de enviar datos (precisamente cada segundo)
            if tiempo_actual >= proximo_envio:
                # Solo enviamos datos si el sensor no está activo
                if not sensor_activo:
                    # Generar datos con valores en cero
                    timestamp = datetime.now().isoformat()
                    nuevos_datos = {
                        'timestamp': timestamp,
                        'temperatura': 0,
                        'vibracion': 0,
                        'presion': 0
                    }
                    
                    # Agregar a la lista de datos recientes
                    datos_recientes.append(nuevos_datos)
                    
                    # Mantener solo los últimos N puntos
                    if len(datos_recientes) > Config.MAX_DATA_POINTS:
                        datos_recientes.pop(0)
                    
                    # Enviar datos a todos los clientes conectados
                    socketio.emit('nuevos_datos', nuevos_datos)
                
                # Calcular el próximo tiempo de envío (exactamente 1 segundo después)
                proximo_envio = tiempo_actual + 1.0
            
            # Dormir por un tiempo corto para no consumir CPU innecesariamente
            time.sleep(0.01)
                
        except Exception as e:
            print(f"Error en el hilo de datos: {str(e)}")
            import traceback
            traceback.print_exc()  # Print the full stack trace to help diagnose issues
            proximo_envio = time.time() + 1.0

if __name__ == '__main__':
    # Ensure required directories exist
    os.makedirs(os.path.join(os.path.dirname(__file__), 'static', 'js'), exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), 'templates'), exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), 'routes'), exist_ok=True)
    
    print(f"Iniciando servidor en http://{Config.HOST}:{Config.PORT}")
    print(f"Accede al dashboard en tu navegador con la URL http://localhost:{Config.PORT}")
    
    # Iniciar el hilo para generar datos
    thread_datos = threading.Thread(target=generar_y_enviar_datos)
    thread_datos.daemon = True
    thread_datos.start()
    
    # Iniciar el servidor Flask-SocketIO
    socketio.run(app, host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
