from flask import Blueprint, jsonify, request, render_template, flash, redirect, url_for
import numpy as np
import json
import os
import sys

# Agregar directorio padre a la ruta para importaciones
directorio_padre = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if directorio_padre not in sys.path:
    sys.path.append(directorio_padre)

from markov.cadenas_de_markov import CadenaMarkov
from database.Servicios.EjercicioServicio import ServicioEjercicio
from database.Servicios.MaquinaServicio import ServicioMaquina

# Crear blueprint
markov_blueprint = Blueprint('markov', __name__)

@markov_blueprint.route('/cadena-markov', methods=['GET'])
def mostrar_cadena_markov():
    """Muestra la página principal de cadenas de Markov"""
    maquinas = ServicioMaquina.listar_maquinas()
    ejercicios = ServicioEjercicio.listar_ejercicios()
    
    # Obtener el ID de máquina si viene como parámetro (para preseleccionar)
    id_maquina = request.args.get('id_maquina')
    
    # Depuración para ver cuántas máquinas se están cargando
    print(f"Número de máquinas cargadas: {len(maquinas)}")
    if maquinas:
        for m in maquinas:
            print(f"Máquina: ID={m.id}, Nombre={m.nombre}, Tipo={m.tipo_maquina}")
    else:
        print("No se encontraron máquinas en la base de datos.")
    
    return render_template('CadenaMarkov.html', maquinas=maquinas, ejercicios=ejercicios, id_maquina_seleccionada=id_maquina)

@markov_blueprint.route('/aplicar-markov', methods=['POST'])
def aplicar_markov():
    """Procesa y resuelve un ejercicio de cadena de Markov"""
    try:
        # Obtener datos del formulario
        matriz_json = request.form.get('matriz_transicion')
        vector_json = request.form.get('vector_inicial')
        nombres_json = request.form.get('nombres_estados')
        id_maquina = request.form.get('id_maquina')
        descripcion = request.form.get('descripcion', '')
        num_pasos = int(request.form.get('num_pasos', 5))
        
        # Depuración
        print(f"ID de máquina recibido: '{id_maquina}'")
        
        # Validar que se proporcionó un ID de máquina válido
        if not id_maquina:
            return jsonify({"error": "Debe seleccionar una máquina"}), 400
        
        # Convertir JSON a objetos Python
        matriz = json.loads(matriz_json)
        vector = json.loads(vector_json)
        nombres = json.loads(nombres_json)
        
        # Validar datos
        if len(matriz) != 4 or any(len(fila) != 4 for fila in matriz):
            return jsonify({"error": "La matriz debe ser 4x4"}), 400
            
        if len(vector) != 4:
            return jsonify({"error": "El vector debe tener 4 elementos"}), 400
            
        if len(nombres) != 4:
            return jsonify({"error": "Debe haber 4 nombres de estados"}), 400
        
        # Crear datos para el servicio
        datos = {
            'matriz_estados': matriz,
            'vector_inicial': vector,
            'nombres_estados': nombres,
            'id_maquina': id_maquina,
            'descripcion': descripcion,
            'num_pasos': num_pasos
        }
        
        # Usar el servicio para crear y resolver el ejercicio
        ejercicio, mensaje = ServicioEjercicio.crear_ejercicio(datos)
        
        if not ejercicio:
            return jsonify({"error": mensaje}), 400
        
        # Obtener resultados
        resultado = ejercicio.get_resultado()
        
        # Preparar respuesta
        respuesta = {
            "id_ejercicio": ejercicio.id,
            "resultado_pasos": resultado['resultado_pasos'],
            "estado_estacionario": resultado['estado_estacionario'],
            "convergencia": resultado.get('convergencia', {}),  # Datos de convergencia
            "mensaje": mensaje,
            "nombres_estados": nombres
        }
        
        return jsonify(respuesta), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()  # Imprimir el traceback completo
        return jsonify({"error": f"Error al procesar el ejercicio: {str(e)}"}), 500

@markov_blueprint.route('/ejercicios', methods=['GET'])
def listar_ejercicios():
    """Lista todos los ejercicios de cadenas de Markov"""
    ejercicios = ServicioEjercicio.listar_ejercicios()
    return render_template('listaEjercicios.html', ejercicios=ejercicios)

@markov_blueprint.route('/ejercicios/<int:id_ejercicio>', methods=['GET'])
def ver_ejercicio(id_ejercicio):
    """Muestra un ejercicio específico"""
    ejercicio = ServicioEjercicio.buscar_por_id(id_ejercicio)
    if not ejercicio:
        flash('Ejercicio no encontrado', 'error')
        return redirect(url_for('markov.listar_ejercicios'))
    
    return render_template('detalleEjercicio.html', ejercicio=ejercicio)

@markov_blueprint.route('/ejercicios/<int:id_ejercicio>/eliminar', methods=['POST'])
def eliminar_ejercicio(id_ejercicio):
    """Elimina un ejercicio"""
    exito, mensaje = ServicioEjercicio.eliminar_ejercicio(id_ejercicio)
    
    if exito:
        flash(mensaje, 'success')
    else:
        flash(mensaje, 'error')
    
    return redirect(url_for('markov.listar_ejercicios'))

@markov_blueprint.route('/ejercicios/maquina/<int:id_maquina>', methods=['GET'])
def ejercicios_por_maquina(id_maquina):
    """Lista ejercicios de una máquina específica"""
    ejercicios = ServicioEjercicio.buscar_por_maquina(id_maquina)
    maquina = ServicioMaquina.buscar_por_id(id_maquina)
    
    if not maquina:
        flash('Máquina no encontrada', 'error')
        return redirect(url_for('markov.listar_ejercicios'))
    
    return render_template('ejerciciosMaquina.html', ejercicios=ejercicios, maquina=maquina)