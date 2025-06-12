from flask import Blueprint, render_template, request, abort
import sys
import os

# Agregar directorio padre a la ruta para importaciones
directorio_padre = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if directorio_padre not in sys.path:
    sys.path.append(directorio_padre)

from database.Servicios.MaquinaServicio import ServicioMaquina

# Crear blueprint
web_blueprint = Blueprint('web', __name__)

@web_blueprint.route('/')
def index():
    """Ruta principal que muestra el dashboard"""
    return render_template('index.html')

@web_blueprint.route('/IA/dashboard')
@web_blueprint.route('/IA/dashboard/<int:id_maquina>')
def dashboard(id_maquina=None):
    """
    Ruta que muestra el dashboard de una máquina específica
    
    Args:
        id_maquina: ID de la máquina a monitorear (opcional)
    """
    # Si no se proporciona ID, redirigir a la página de monitoreo
    if id_maquina is None:
        return render_template('dashboard.html')
    
    # Buscar la máquina por ID
    maquina = ServicioMaquina.buscar_por_id(id_maquina)
    if not maquina:
        abort(404, description=f"Máquina con ID {id_maquina} no encontrada")
    
    # Renderizar dashboard con información de la máquina
    return render_template('dashboard.html', maquina=maquina)

@web_blueprint.route('/monitoreo')
def monitoreo():
    """Ruta que muestra la página de monitoreo con la lista de máquinas"""
    # Obtener todas las máquinas
    maquinas = ServicioMaquina.listar_maquinas()
    
    return render_template('monitoreo.html', maquinas=maquinas)

