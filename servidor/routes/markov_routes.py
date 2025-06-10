from flask import Blueprint, jsonify, request, render_template
from models.equipos import Equipo
from markov.cadenas_de_markov import CadenaMarkov
import numpy as np
# Crear blueprint
markov_blueprint = Blueprint('api', __name__)

# Almacén en memoria de todos los equipos creados
equipos_store = [] # Implementar con base de datos en el futuro

@markov_blueprint.route('/cadena-markov', methods=['GET', 'POST'])
def cadena_markov():
    if request.method == 'POST':
        nombres = request.form.getlist('nombre_equipo')
        funciones = request.form.getlist('funcion_maquina')
        tiempos_list = request.form.getlist('tiempos_uso')
        fechas = request.form.getlist('fecha')
        estados = request.form.getlist('estado_equipo')
        nuevos = []
        
        for nombre, func, t_str, fecha, est in zip(nombres, funciones, tiempos_list, fechas, estados):
            if nombre and func and t_str:  # Solo procesar entradas completas
                try:
                    lista_tiempos = [float(x) for x in t_str.split(',') if x.strip()]
                    eq = Equipo(nombre, func, lista_tiempos, fecha)
                    eq.estado = est
                    nuevos.append(eq)
                except ValueError:
                    pass  # Ignorar errores de conversión
        
        global equipos_store
        equipos_store.extend(nuevos)
        
        return render_template('CadenaMarkov.html', equipos=equipos_store, guardados=len(equipos_store))
    
    return render_template('CadenaMarkov.html', equipos=equipos_store)

@markov_blueprint.route('/aplicar-markov', methods=['POST'])
def aplicar_markov():
    if request.method == 'POST':
        nombre_maquina = request.form.get('machineSelect')
        pasos = int(request.form.get('predictionSteps', 5))
        
        # Buscar la máquina seleccionada
        maquina = next((eq for eq in equipos_store if eq.nombre_equipo == nombre_maquina), None)
        
        if maquina:
            try:
                # Obtener matriz y vector desde el formulario si se proporcionaron
                matriz_transicion = None
                vector_inicial = None
                
                if 'matriz_transicion' in request.form and 'vector_inicial' in request.form:
                    import json
                    matriz_transicion = np.array(json.loads(request.form.get('matriz_transicion')))
                    vector_inicial = np.array(json.loads(request.form.get('vector_inicial')))
                # Si no hay matriz/vector en el form, usar los existentes o crear uno predeterminado
                elif not hasattr(maquina, 'matriz') or maquina.matriz is None:
                    # Matriz de ejemplo para estados: bueno, medio, malo
                    matriz_transicion = np.array([
                        [0.7, 0.2, 0.1],  # De bueno a (bueno, medio, malo)
                        [0.3, 0.5, 0.2],  # De medio a (bueno, medio, malo)
                        [0.1, 0.3, 0.6]   # De malo a (bueno, medio, malo)
                    ])
                    
                    # Vector inicial basado en el estado actual
                    if maquina.estado == "muy_bueno" or maquina.estado == "bueno":
                        vector_inicial = np.array([1.0, 0.0, 0.0])  # Comienza en estado bueno
                    elif maquina.estado == "medio":
                        vector_inicial = np.array([0.0, 1.0, 0.0])  # Comienza en estado medio
                    else:  # malo
                        vector_inicial = np.array([0.0, 0.0, 1.0])  # Comienza en estado malo
                else:
                    matriz_transicion = maquina.matriz
                    vector_inicial = np.array([1.0, 0.0, 0.0])  # Por defecto
                
                # Crear la cadena de Markov y calcular probabilidades
                try:
                    cadena = CadenaMarkov(matriz_transicion, vector_inicial)
                    probabilidades = cadena.propagar(pasos)
                    
                    # Si la matriz es válida, asignarla al objeto Equipo para futuros cálculos
                    if matriz_transicion is not None and vector_inicial is not None:
                        maquina.matriz = matriz_transicion
                        maquina.asignar_matriz(matriz_transicion, vector_inicial)
                    
                    # Determinar recomendación según probabilidades
                    prob_malo = probabilidades[2]
                    if prob_malo > 0.6:
                        recomendacion = "Alerta: Alta probabilidad de fallo. Se recomienda mantenimiento inmediato."
                    elif prob_malo > 0.2:
                        recomendacion = "Precaución: Probabilidad moderada de fallo. Programar mantenimiento próximamente."
                    else:
                        recomendacion = "La máquina mantiene buenas condiciones de operación."
                    
                    # Formatear resultados para la respuesta JSON
                    resultados = {
                        'currentState': maquina.estado,
                        'probGood': f"{probabilidades[0]*100:.1f}%",
                        'probMedium': f"{probabilidades[1]*100:.1f}%",
                        'probBad': f"{probabilidades[2]*100:.1f}%",
                        'recommendation': recomendacion
                    }
                    return jsonify(resultados)
                except ValueError as e:
                    return jsonify({'error': f'Error de validación: {str(e)}'})
            except Exception as e:
                return jsonify({'error': f'Error en cálculo de Markov: {str(e)}'})
        
    return jsonify({'error': 'Máquina no encontrada o parámetros incorrectos'})

@markov_blueprint.route('/carga-matriz', methods=['GET', 'POST'])
def carga_matriz():
    if request.method == 'POST':
        nombre_eq = request.form['maquinaria']

        # Parseo de matriz
        p_bb = float(request.form.get('p_bb', 0))
        p_bm = float(request.form.get('p_bm', 0))
        p_ba = float(request.form.get('p_ba', 0))
        p_mb = float(request.form.get('p_mb', 0))
        p_mm = float(request.form.get('p_mm', 0))
        p_ma = float(request.form.get('p_ma', 0))
        p_ab = float(request.form.get('p_ab', 0))
        p_am = float(request.form.get('p_am', 0))
        p_aa = float(request.form.get('p_aa', 0))

        matriz = [
            [p_bb, p_bm, p_ba],
            [p_mb, p_mm, p_ma],
            [p_ab, p_am, p_aa],
        ]

        # Parseo de vector
        v_bueno = float(request.form.get('v_bueno', 0))
        v_medio = float(request.form.get('v_medio', 0))
        v_malo  = float(request.form.get('v_malo', 0))
        vector = [v_bueno, v_medio, v_malo]

        # Asignación al objeto Equipo
        for eq in equipos_store:
            if eq.nombre_equipo == nombre_eq:
                eq.asignar_matriz(matriz, vector)
                mensaje = f"Matriz y vector asignados a {nombre_eq}"
                return jsonify({'success': True, 'mensaje': mensaje})
        
        return jsonify({'success': False, 'mensaje': f"No se encontró el equipo {nombre_eq}"})
    
    return render_template('CadenaMarkov.html', equipos=equipos_store, seccion='ia-sistema')

@markov_blueprint.route('/probabilidades', methods=['GET', 'POST'])
def probabilidades():
    resultados = None
    mensaje = None
    sel = None

    if request.method == 'POST':
        sel = request.form.get('maquinaria')
        if not sel:
            mensaje = "Por favor selecciona una maquinaria."
        else:
            # buscar el objeto Equipo
            eq = next((e for e in equipos_store if e.nombre_equipo == sel), None)
            if not eq:
                mensaje = f"No existe la maquinaria {sel}."
            elif eq.cadena_markov is None:
                mensaje = f"No has cargado la matriz/vector para {sel}."
            else:
                # calcular por día
                if 'calcular_dia' in request.form:
                    pasos = int(request.form.get('pasos_dia', 1))
                    vec_res = eq.calcular_estados(pasos)
                # calcular a futuro (estado estacionario)
                else:
                    vec_res = eq.cadena_markov.calculo_futuro()
                resultados = eq.matriz.flatten().tolist() + vec_res.tolist()

    return render_template('CadenaMarkov.html', 
                          equipos=equipos_store,
                          resultados=resultados,
                          mensaje=mensaje,
                          sel=sel,
                          seccion='monitoreo')

@markov_blueprint.route('/api/equipos', methods=['GET'])
def api_equipos():
    """Endpoint API para obtener los equipos en formato JSON"""
    equipos_json = [eq.to_dict() for eq in equipos_store]
    return jsonify(equipos_json)
