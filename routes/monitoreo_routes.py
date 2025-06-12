from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
import os
import sys

# Agregar directorio padre a la ruta para importaciones
directorio_padre = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if directorio_padre not in sys.path:
    sys.path.append(directorio_padre)

# Crear blueprint para rutas de monitoreo
monitoreo_blueprint = Blueprint('monitoreo', __name__)

@monitoreo_blueprint.route('/monitoreo')
def mostrar_monitoreo():
    """Ruta para mostrar el panel de monitoreo."""
    return render_template('monitoreo.html')

@monitoreo_blueprint.route('/seguimiento')
def mostrar_seguimiento():
    """Ruta para mostrar el seguimiento de máquinas."""
    return render_template('seguimiento.html')
