import time
from config import Config

def setup_socket_events(socketio, datos_recientes, sensor_activo, maquina_encendida, 
                        proximo_envio, ultimo_heartbeat, TIMEOUT_SENSOR):
    """Configurar todos los eventos de Socket.IO"""
    
    @socketio.on('connect')
    def handle_connect():
        """Manejar la conexión de un cliente"""
        print('Cliente conectado')
        
        # Enviar estado actual de la máquina al cliente que se conecta
        socketio.emit('estado_maquina', {'encendida': maquina_encendida})
        
        # Enviar estado actual del sensor al cliente que se conecta
        socketio.emit('estado_sensores', {'activos': sensor_activo, 'cantidad': 1 if sensor_activo else 0})
        
        # Si hay datos recientes, enviar el último dato
        if datos_recientes:
            socketio.emit('nuevos_datos', datos_recientes[-1])

    @socketio.on('disconnect')
    def handle_disconnect():
        print('Cliente desconectado')

    @socketio.on('sensor_activo')
    def handle_sensor_status(data):
        """Manejar el estado de activación del sensor"""
        nonlocal sensor_activo, proximo_envio
        
        if data.get('estado', False):
            # Sensor activado
            sensor_activo = True
            print("Sensor activado")
        else:
            # Sensor desactivado
            sensor_activo = False
            print("Sensor desactivado")
            # Actualizar el tiempo del próximo envío
            proximo_envio = time.time() + 1.0  
        
        # Enviar inmediatamente el estado del sensor a todos los clientes
        socketio.emit('estado_sensores', {'activos': sensor_activo, 'cantidad': 1 if sensor_activo else 0})

    @socketio.on('datos_sensor')
    def handle_sensor_data(datos):
        """Manejar datos recibidos del sensor"""
        nonlocal sensor_activo
        
        # Solo procesamos datos si el sensor está activo
        if sensor_activo:
            # Agregar a la lista de datos recientes
            datos_recientes.append(datos)
            
            # Mantener solo los últimos N puntos
            if len(datos_recientes) > Config.MAX_DATA_POINTS:
                datos_recientes.pop(0)
            
            # Enviar datos a todos los clientes conectados
            socketio.emit('nuevos_datos', datos)

    @socketio.on('cambiar_estado_maquina')
    def handle_machine_state(data):
        """Manejar cambios en el estado de la máquina (encendido/apagado)"""
        nonlocal maquina_encendida
        
        # Solo permitir cambios si el sensor está activo
        if not sensor_activo:
            return {'success': False, 'mensaje': 'No se puede cambiar el estado: sensor inactivo'}
        
        # Obtener el nuevo estado deseado
        nuevo_estado = data.get('encender', False)
        
        # Solo hacer cambios si el estado es diferente
        if maquina_encendida != nuevo_estado:
            maquina_encendida = nuevo_estado
            
            print(f"Estado de la máquina cambiado a: {'ENCENDIDA' if maquina_encendida else 'APAGADA'}")
            
            # Notificar a todos los clientes conectados sobre el cambio
            socketio.emit('estado_maquina', {'encendida': maquina_encendida})
            
            # Notificar al sensor sobre el cambio
            socketio.emit('comando_sensor', {'encender': maquina_encendida})
            
            # Devolver confirmación al cliente que envió el comando
            return {'success': True, 'estado': 'encendida' if maquina_encendida else 'apagada'}
        
        return {'success': False, 'mensaje': 'La máquina ya está en ese estado'}

    @socketio.on('heartbeat')
    def handle_heartbeat():
        """Manejar los heartbeats del sensor para detectar desconexiones"""
        nonlocal ultimo_heartbeat
        
        ultimo_heartbeat = time.time()
        # Quietly acknowledge the heartbeat
        return {'recibido': True}

    return socketio
