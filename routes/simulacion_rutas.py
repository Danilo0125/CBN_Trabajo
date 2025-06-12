from flask import Blueprint, request, jsonify
from datetime import datetime
import sys
import os

# Agregar directorio padre a la ruta para importaciones
directorio_padre = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if directorio_padre not in sys.path:
    sys.path.append(directorio_padre)

from database.Servicios.SimulacionServicio import ServicioSimulacion

# Crear Blueprint para las rutas de simulación
simulacion_bp = Blueprint('simulacion', __name__)

@simulacion_bp.route('/api/simulaciones', methods=['GET'])
def listar_simulaciones():
    """Endpoint para listar todas las simulaciones"""
    simulaciones = ServicioSimulacion.listar_simulaciones()
    
    # Convertir objetos a diccionarios para la respuesta JSON
    resultado = []
    for sim in simulaciones:
        resultado.append({
            'id_simulacion': sim.id_simulacion,
            'linea_id': sim.linea_id,
            'usuario_id': sim.usuario_id,
            'Fecha': sim.Fecha.isoformat() if sim.Fecha else None,
            'Acc_IA': sim.Acc_IA,
            'Acc_humana': sim.Acc_humana,
            'Acc_final': sim.Acc_final,
            'Intervenido': sim.Intervenido,
            'Temperatura': sim.Temperatura,
            'Presion': sim.Presion,
            'Uso': sim.Uso,
            'Recompensa': sim.Recompensa,
            'Comentario': sim.Comentario,
            'vibracion': sim.vibracion
        })
    
    return jsonify({'simulaciones': resultado, 'total': len(resultado)})

@simulacion_bp.route('/api/simulaciones/<int:id_simulacion>', methods=['GET'])
def obtener_simulacion(id_simulacion):
    """Endpoint para obtener una simulación por su ID"""
    simulacion = ServicioSimulacion.buscar_por_id(id_simulacion)
    
    if not simulacion:
        return jsonify({'error': f'No se encontró simulación con ID {id_simulacion}'}), 404
    
    # Convertir objeto a diccionario para la respuesta JSON
    resultado = {
        'id_simulacion': simulacion.id_simulacion,
        'linea_id': simulacion.linea_id,
        'usuario_id': simulacion.usuario_id,
        'Fecha': simulacion.Fecha.isoformat() if simulacion.Fecha else None,
        'Acc_IA': simulacion.Acc_IA,
        'Acc_humana': simulacion.Acc_humana,
        'Acc_final': simulacion.Acc_final,
        'Intervenido': simulacion.Intervenido,
        'Temperatura': simulacion.Temperatura,
        'Presion': simulacion.Presion,
        'Uso': simulacion.Uso,
        'Recompensa': simulacion.Recompensa,
        'Comentario': simulacion.Comentario,
        'vibracion': simulacion.vibracion
    }
    
    return jsonify(resultado)

@simulacion_bp.route('/api/simulaciones/maquina/<int:linea_id>', methods=['GET'])
def buscar_por_maquina(linea_id):
    """Endpoint para buscar simulaciones por ID de máquina/línea"""
    simulaciones = ServicioSimulacion.buscar_por_maquina(linea_id)
    
    # Convertir objetos a diccionarios para la respuesta JSON
    resultado = []
    for sim in simulaciones:
        resultado.append({
            'id_simulacion': sim.id_simulacion,
            'linea_id': sim.linea_id,
            'usuario_id': sim.usuario_id,
            'Fecha': sim.Fecha.isoformat() if sim.Fecha else None,
            'Acc_IA': sim.Acc_IA,
            'Acc_humana': sim.Acc_humana,
            'Acc_final': sim.Acc_final,
            'Intervenido': sim.Intervenido,
            'Temperatura': sim.Temperatura,
            'Presion': sim.Presion,
            'Uso': sim.Uso,
            'Recompensa': sim.Recompensa,
            'Comentario': sim.Comentario,
            'vibracion': sim.vibracion
        })
    
    return jsonify({'simulaciones': resultado, 'total': len(resultado)})

@simulacion_bp.route('/api/simulaciones/usuario/<int:usuario_id>', methods=['GET'])
def buscar_por_usuario(usuario_id):
    """Endpoint para buscar simulaciones por ID de usuario"""
    simulaciones = ServicioSimulacion.buscar_por_usuario(usuario_id)
    
    # Convertir objetos a diccionarios para la respuesta JSON
    resultado = []
    for sim in simulaciones:
        resultado.append({
            'id_simulacion': sim.id_simulacion,
            'linea_id': sim.linea_id,
            'usuario_id': sim.usuario_id,
            'Fecha': sim.Fecha.isoformat() if sim.Fecha else None,
            'Acc_IA': sim.Acc_IA,
            'Acc_humana': sim.Acc_humana,
            'Acc_final': sim.Acc_final,
            'Intervenido': sim.Intervenido,
            'Temperatura': sim.Temperatura,
            'Presion': sim.Presion,
            'Uso': sim.Uso,
            'Recompensa': sim.Recompensa,
            'Comentario': sim.Comentario,
            'vibracion': sim.vibracion
        })
    
    return jsonify({'simulaciones': resultado, 'total': len(resultado)})

@simulacion_bp.route('/api/simulaciones/fecha', methods=['GET'])
def buscar_por_fecha():
    """Endpoint para buscar simulaciones por rango de fechas"""
    # Obtener fechas de los parámetros de consulta
    try:
        fecha_inicio_str = request.args.get('inicio', '')
        fecha_fin_str = request.args.get('fin', '')
        
        if not fecha_inicio_str or not fecha_fin_str:
            return jsonify({'error': 'Se requieren los parámetros inicio y fin con formato ISO (YYYY-MM-DD)'}), 400
        
        fecha_inicio = datetime.fromisoformat(fecha_inicio_str)
        fecha_fin = datetime.fromisoformat(fecha_fin_str)
        
        simulaciones = ServicioSimulacion.buscar_por_fecha(fecha_inicio, fecha_fin)
        
        # Convertir objetos a diccionarios para la respuesta JSON
        resultado = []
        for sim in simulaciones:
            resultado.append({
                'id_simulacion': sim.id_simulacion,
                'linea_id': sim.linea_id,
                'usuario_id': sim.usuario_id,
                'Fecha': sim.Fecha.isoformat() if sim.Fecha else None,
                'Acc_IA': sim.Acc_IA,
                'Acc_humana': sim.Acc_humana,
                'Acc_final': sim.Acc_final,
                'Intervenido': sim.Intervenido,
                'Temperatura': sim.Temperatura,
                'Presion': sim.Presion,
                'Uso': sim.Uso,
                'Recompensa': sim.Recompensa,
                'Comentario': sim.Comentario,
                'vibracion': sim.vibracion
            })
        
        return jsonify({'simulaciones': resultado, 'total': len(resultado)})
        
    except ValueError as e:
        return jsonify({'error': f'Formato de fecha inválido: {str(e)}'}), 400

@simulacion_bp.route('/api/simulaciones', methods=['POST'])
def crear_simulacion():
    """Endpoint para crear una nueva simulación"""
    datos = request.get_json()
    
    if not datos:
        return jsonify({'error': 'No se proporcionaron datos para crear la simulación'}), 400
    
    simulacion, mensaje = ServicioSimulacion.crear_simulacion(datos)
    
    if not simulacion:
        return jsonify({'error': mensaje}), 400
    
    return jsonify({
        'mensaje': mensaje,
        'id_simulacion': simulacion.id_simulacion
    }), 201

@simulacion_bp.route('/api/simulaciones/<int:id_simulacion>', methods=['PUT'])
def actualizar_simulacion(id_simulacion):
    """Endpoint para actualizar una simulación existente"""
    datos = request.get_json()
    
    if not datos:
        return jsonify({'error': 'No se proporcionaron datos para actualizar la simulación'}), 400
    
    simulacion, mensaje = ServicioSimulacion.actualizar_simulacion(id_simulacion, datos)
    
    if not simulacion:
        return jsonify({'error': mensaje}), 400
    
    return jsonify({'mensaje': mensaje})

@simulacion_bp.route('/api/simulaciones/<int:id_simulacion>', methods=['DELETE'])
def eliminar_simulacion(id_simulacion):
    """Endpoint para eliminar una simulación"""
    exito, mensaje = ServicioSimulacion.eliminar_simulacion(id_simulacion)
    
    if not exito:
        return jsonify({'error': mensaje}), 404
    
    return jsonify({'mensaje': mensaje})

# Función para registrar las rutas en la aplicación Flask
def registrar_rutas_simulacion(app):
    """Registra las rutas de simulación en la aplicación Flask"""
    app.register_blueprint(simulacion_bp)
