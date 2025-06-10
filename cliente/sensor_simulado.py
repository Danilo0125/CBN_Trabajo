import socketio
import time
import sys
import os
import numpy as np
import random
from datetime import datetime

# Añadir el directorio del servidor al path para importar los módulos
server_path = os.path.join(os.path.dirname(__file__), '..', 'servidor')
sys.path.append(server_path)
# Definir funciones de respaldo
class Config:
    HOST = 'localhost'
    PORT = 5000

def generar_datos_tiempo_real():
    return {
        'timestamp': datetime.now().isoformat(),
        'temperatura': random.uniform(50, 60),
        'vibracion': random.uniform(2, 4),
        'presion': random.uniform(2, 3)
    }

# Crear cliente Socket.IO
sio = socketio.Client(reconnection=True, reconnection_attempts=10, 
                     reconnection_delay=1, reconnection_delay_max=5)

# Estado de conexión
conectado = False

# Estado de la máquina
maquina_encendida = True

# Estado de simulación de falla
simulando_falla = False
tiempo_falla_restante = 0
tipo_falla = None

# Valores objetivo y actuales
valores_normales = {'temperatura': None, 'vibracion': None, 'presion': None}
valores_actuales = {'temperatura': 0, 'vibracion': 0, 'presion': 0}

@sio.event
def connect():
    global conectado
    conectado = True
    print('Conexión establecida con el servidor')

@sio.event
def disconnect():
    global conectado
    conectado = False
    print('Desconectado del servidor')

@sio.on('comando_sensor')
def handle_command(data):
    """Recibir comandos para cambiar el estado de la máquina"""
    global maquina_encendida, simulando_falla, valores_actuales
    
    # Obtener el nuevo estado de la máquina
    nuevo_estado = data.get('encender', False)
    
    # Actualizar el estado solo si es diferente
    if maquina_encendida != nuevo_estado:
        maquina_encendida = nuevo_estado
        
        print(f"Comando recibido: Máquina {'ENCENDIDA' if maquina_encendida else 'APAGADA'}")
        
        # Si se apaga la máquina, detener cualquier simulación de falla
        if not maquina_encendida:
            simulando_falla = False
            # Ya no ponemos los valores a cero inmediatamente
            # Los valores caerán gradualmente durante la simulación
            print("[COMANDO] Máquina apagada - valores disminuirán gradualmente")
        else:
            print("[COMANDO] Máquina encendida - reiniciando valores normales")
        
        # Confirmar que recibimos el comando
        return {'recibido': True, 'estado': 'encendida' if maquina_encendida else 'apagada'}

def calcular_valor_gradual(valor_actual, valor_objetivo, paso=0.1):
    """Calcula un valor intermedio para simular cambios graduales"""
    if abs(valor_actual - valor_objetivo) < paso:
        return valor_objetivo
    elif valor_actual < valor_objetivo:
        return valor_actual + paso
    else:
        return valor_actual - paso

def iniciar_falla_aleatoria():
    """Inicia una simulación de falla aleatoria"""
    global simulando_falla, tiempo_falla_restante, tipo_falla
    
    tipos_falla = ['temperatura', 'vibracion', 'presion']
    tipo_falla = random.choice(tipos_falla)
    tiempo_falla_restante = random.randint(20, 40)
    simulando_falla = True
    
    print(f"Iniciando simulación de falla: {tipo_falla}, duración: {tiempo_falla_restante}s")

def simular_valores_falla():
    """Genera valores simulados durante una falla"""
    global valores_actuales, tipo_falla
    
    nuevos_valores = valores_actuales.copy()
    
    if tipo_falla == 'temperatura':
        nuevos_valores['temperatura'] = min(85, valores_actuales['temperatura'] + random.uniform(0.5, 1.5))
        nuevos_valores['vibracion'] = min(8, valores_actuales['vibracion'] + random.uniform(0.1, 0.3))
        nuevos_valores['presion'] = min(4.5, valores_actuales['presion'] + random.uniform(0.05, 0.15))
    elif tipo_falla == 'vibracion':
        nuevos_valores['vibracion'] = min(12, valores_actuales['vibracion'] + random.uniform(0.3, 0.8))
        nuevos_valores['temperatura'] = min(70, valores_actuales['temperatura'] + random.uniform(0.2, 0.5))
    elif tipo_falla == 'presion':
        nuevos_valores['presion'] = min(5.5, valores_actuales['presion'] + random.uniform(0.1, 0.3))
        nuevos_valores['temperatura'] = min(70, valores_actuales['temperatura'] + random.uniform(0.2, 0.4))
    
    return nuevos_valores

def enviar_datos_sensores():
    """Genera y envía datos de sensores simulados al servidor cada segundo"""
    global valores_actuales, valores_normales, simulando_falla, tiempo_falla_restante, conectado
    
    # Generar valores normales de referencia
    datos_ref = generar_datos_tiempo_real()
    valores_normales = {
        'temperatura': datos_ref['temperatura'],
        'vibracion': datos_ref['vibracion'],
        'presion': datos_ref['presion']
    }
    
    # Inicializar valores actuales
    valores_actuales = valores_normales.copy()
    
    # Contador para eventos
    contador_eventos = 0
    
    # Control de tiempo
    proximo_envio = time.time() + 1.0
    
    # Agregar variable para control de heartbeats
    proximo_heartbeat = time.time()
    
    print("Enviando datos al servidor cada segundo...")
    
    while True:
        if conectado:
            tiempo_actual = time.time()
            
            # Enviar heartbeat cada 2 segundos para que el servidor sepa que estamos vivos
            if tiempo_actual >= proximo_heartbeat:
                try:
                    sio.emit('heartbeat')
                    proximo_heartbeat = tiempo_actual + 2.0  # Enviar cada 2 segundos
                except Exception as e:
                    print(f"Error enviando heartbeat: {str(e)}")
            
            if tiempo_actual >= proximo_envio:
                try:
                    contador_eventos += 1
                    
                    # Posibilidad de iniciar una falla cada 60 segundos (30% probabilidad)
                    if maquina_encendida and not simulando_falla and contador_eventos % 60 == 0 and random.random() < 0.3:
                        iniciar_falla_aleatoria()
                    
                    # Si estamos simulando una falla
                    if simulando_falla and maquina_encendida:
                        tiempo_falla_restante -= 1
                        valores_actuales = simular_valores_falla()
                        
                        if tiempo_falla_restante <= 0:
                            simulando_falla = False
                            print("Falla terminada")
                    else:
                        # Valores normales o apagado
                        if maquina_encendida:
                            # Ajustar gradualmente hacia valores normales
                            for sensor in valores_actuales:
                                paso = 0.5 if sensor == 'temperatura' else 0.2 if sensor == 'presion' else 0.3
                                valores_actuales[sensor] = calcular_valor_gradual(
                                    valores_actuales[sensor], 
                                    valores_normales[sensor], 
                                    paso
                                )
                        else:
                            # Si está apagada, disminuir gradualmente hacia cero
                            for sensor in valores_actuales:
                                # Usar pasos más grandes para que la caída sea más rápida pero aún gradual
                                paso = 1.0 if sensor == 'temperatura' else 0.4 if sensor == 'presion' else 0.6
                                valores_actuales[sensor] = calcular_valor_gradual(
                                    valores_actuales[sensor],
                                    0,  # El objetivo es cero
                                    paso
                                )
                    
                    # Generar datos actuales
                    timestamp = datetime.now().isoformat()
                    
                    # Añadir ruido aleatorio solo si los valores son suficientemente altos
                    ruido_temp = np.random.normal(0, 0.5) if valores_actuales['temperatura'] > 1 else 0
                    ruido_vib = np.random.normal(0, 0.2) if valores_actuales['vibracion'] > 0.5 else 0
                    ruido_pres = np.random.normal(0, 0.1) if valores_actuales['presion'] > 0.5 else 0
                    
                    datos = {
                        'timestamp': timestamp,
                        'temperatura': round(max(0, valores_actuales['temperatura'] + ruido_temp), 2),
                        'vibracion': round(max(0, valores_actuales['vibracion'] + ruido_vib), 2),
                        'presion': round(max(0, valores_actuales['presion'] + ruido_pres), 2)
                    }
                    
                    # Enviar datos al servidor
                    sio.emit('datos_sensor', datos)
                    
                    # Siguiente envío en 1 segundo exacto
                    proximo_envio = tiempo_actual + 1.0
                    
                except Exception as e:
                    print(f"Error: {str(e)}")
                    proximo_envio = tiempo_actual + 1.0
                    
                    # Intentar reconectar si perdimos conexión
                    if not sio.connected:
                        conectado = False
                        print("Conexión perdida. Intentando reconectar...")
                        try:
                            sio.connect(f"http://{Config.HOST}:{Config.PORT}")
                        except:
                            pass
            
            # Pausa breve para no consumir CPU
            time.sleep(0.01)
        else:
            print("Intentando conectar al servidor...")
            try:
                sio.connect(f"http://{Config.HOST}:{Config.PORT}")
                sio.emit('sensor_activo', {'estado': True})
                print("Conectado exitosamente")
                proximo_envio = time.time() + 1.0
            except Exception as e:
                print(f"Error al conectar: {str(e)}")
            time.sleep(1.0)

if __name__ == "__main__":
    server_url = f"http://{Config.HOST}:{Config.PORT}"
    
    print(f"Iniciando simulador de sensor...")
    print(f"Conectando con el servidor en {server_url}")
    print(f"Presione Ctrl+C para detener")
    
    try:
        # Conectar al servidor
        sio.connect(server_url)
        
        # Registrar como sensor activo
        sio.emit('sensor_activo', {'estado': True})
        
        # Iniciar envío de datos
        enviar_datos_sensores()
        
    except KeyboardInterrupt:
        print("Simulador detenido por el usuario")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        # Notificar desconexión de manera más robusta
        if sio.connected:
            try:
                print("Notificando desactivación del sensor")
                # Intentar 3 veces con pequeños retrasos para asegurar que el mensaje llegue
                for _ in range(3):
                    sio.emit('sensor_activo', {'estado': False})
                    time.sleep(0.2)
            except Exception as e:
                print(f"Error al notificar desactivación: {e}")
            
            try:
                sio.disconnect()
                print("Desconectado del servidor")
            except Exception as e:
                print(f"Error al desconectar: {e}")
