from flask import Blueprint, jsonify

# Crear blueprint
api_blueprint = Blueprint('api', __name__)

# Variable global de datos recientes (será compartida con el archivo principal)
datos_recientes = []

@api_blueprint.route('/datos')
def obtener_datos():
    """Endpoint REST para obtener los datos más recientes"""
    return jsonify(datos_recientes[-50:] if len(datos_recientes) > 50 else datos_recientes)




