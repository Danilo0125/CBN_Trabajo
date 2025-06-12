from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
import os
import sys

# Agregar directorio padre a la ruta para importaciones
directorio_padre = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if directorio_padre not in sys.path:
    sys.path.append(directorio_padre)

from database.Servicios.MaquinaServicio import ServicioMaquina

# Crear blueprint para rutas de máquinas
maquina_blueprint = Blueprint('maquinas', __name__)

@maquina_blueprint.route('/maquinas')
def listar_maquinas():
    """Ruta para mostrar todas las máquinas."""
    maquinas = ServicioMaquina.listar_maquinas()
    return render_template('listadoMaquinas.html', maquinas=maquinas)

@maquina_blueprint.route('/maquinas/<int:id_maquina>')
def ver_maquina(id_maquina):
    """Ruta para ver detalles de una máquina específica."""
    maquina = ServicioMaquina.buscar_por_id(id_maquina)
    if not maquina:
        flash('Máquina no encontrada', 'error')
        return redirect(url_for('maquinas.listar_maquinas'))
    return render_template('detalleMaquina.html', maquina=maquina)

@maquina_blueprint.route('/cargar-maquinas', methods=['GET'])
def mostrar_formulario_maquina():
    """Ruta para mostrar el formulario de carga de máquinas."""
    return render_template('cargarMaquinas.html')

@maquina_blueprint.route('/registrar-maquina', methods=['POST'])
def registrar_maquina():
    """Ruta para procesar la creación de una nueva máquina."""
    datos = {
        'nombre': request.form.get('nombre'),
        'descripcion': request.form.get('descripcion'),
        'tipo_maquina': request.form.get('tipo_maquina'),
        'frec_manteni': request.form.get('frec_manteni')
    }
    
    maquina, mensaje = ServicioMaquina.crear_maquina(datos)
    
    if maquina:
        flash(mensaje, 'success')
        return redirect(url_for('maquinas.listar_maquinas'))
    else:
        flash(mensaje, 'error')
        return redirect(url_for('maquinas.mostrar_formulario_maquina'))

@maquina_blueprint.route('/editar-maquina/<int:id_maquina>', methods=['GET', 'POST'])
def editar_maquina(id_maquina):
    """Ruta para editar una máquina existente."""
    if request.method == 'GET':
        maquina = ServicioMaquina.buscar_por_id(id_maquina)
        if not maquina:
            flash('Máquina no encontrada', 'error')
            return redirect(url_for('maquinas.listar_maquinas'))
        return render_template('editarMaquina.html', maquina=maquina)
    
    # Método POST - actualizar la máquina
    datos = {
        'nombre': request.form.get('nombre'),
        'descripcion': request.form.get('descripcion'),
        'tipo_maquina': request.form.get('tipo_maquina'),
        'frec_manteni': request.form.get('frec_manteni')
    }
    
    maquina, mensaje = ServicioMaquina.actualizar_maquina(id_maquina, datos)
    
    if maquina:
        flash(mensaje, 'success')
        return redirect(url_for('maquinas.ver_maquina', id_maquina=id_maquina))
    else:
        flash(mensaje, 'error')
        return redirect(url_for('maquinas.editar_maquina', id_maquina=id_maquina))

@maquina_blueprint.route('/eliminar-maquina/<int:id_maquina>', methods=['POST'])
def eliminar_maquina(id_maquina):
    """Ruta para eliminar una máquina."""
    exito, mensaje = ServicioMaquina.eliminar_maquina(id_maquina)
    
    if exito:
        flash(mensaje, 'success')
    else:
        flash(mensaje, 'error')
    
    return redirect(url_for('maquinas.listar_maquinas'))

@maquina_blueprint.route('/estadisticas-maquinas')
def estadisticas_maquinas():
    """Ruta para mostrar estadísticas de máquinas."""
    estadisticas = ServicioMaquina.obtener_estadisticas()
    return render_template('estadisticasMaquinas.html', estadisticas=estadisticas)

# API endpoints para máquinas (para uso con AJAX o aplicaciones externas)
@maquina_blueprint.route('/api/maquinas', methods=['GET'])
def api_listar_maquinas():
    """API endpoint para listar todas las máquinas."""
    maquinas = ServicioMaquina.listar_maquinas()
    return jsonify([{
        'id': m.id,
        'nombre': m.nombre,
        'tipo_maquina': m.tipo_maquina,
    } for m in maquinas])

@maquina_blueprint.route('/api/maquinas/<int:id_maquina>', methods=['GET'])
def api_ver_maquina(id_maquina):
    """API endpoint para ver detalles de una máquina específica."""
    maquina = ServicioMaquina.buscar_por_id(id_maquina)
    if not maquina:
        return jsonify({'error': 'Máquina no encontrada'}), 404
    
    return jsonify({
        'id': maquina.id,
        'nombre': maquina.nombre,
        'descripcion': maquina.descripcion,
        'tipo_maquina': maquina.tipo_maquina,
        'frec_manteni': maquina.frec_manteni
    })
