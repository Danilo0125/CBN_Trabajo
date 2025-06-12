from flask import Blueprint, jsonify, request, abort
import sys
import os

# Agregar directorio padre a la ruta para importaciones
directorio_padre = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if directorio_padre not in sys.path:
    sys.path.append(directorio_padre)

from database.Servicios.MaquinaServicio import ServicioMaquina
from database.Servicios.SimulacionServicio import ServicioSimulacion

# Crear blueprint
api_blueprint = Blueprint('api', __name__)

# Variable global de datos recientes (será compartida con el archivo principal)
# Para la simulación, usamos una única lista que se comparte para todas las máquinas
datos_recientes = []

@api_blueprint.route('/datos')
def obtener_datos():
    """Endpoint REST para obtener datos de simulación"""
    # En modo simulación, ignoramos el parámetro id_maquina y devolvemos siempre los mismos datos
    return jsonify(datos_recientes[-50:] if len(datos_recientes) > 50 else datos_recientes)




