"""
Ejemplo de actualización de datos en la base de datos
"""
try:
    from database import create_app
    from Modelos import db, MaquinasCerveceria, Usuario, SimulacionEstado, Ejercicio
    from servidor.markov.cadenas_de_markov import CadenaMarkov
except ImportError:
    from .database import create_app
    from .Modelos import db, MaquinasCerveceria, Usuario, SimulacionEstado, Ejercicio
    from ..servidor.markov.cadenas_de_markov import CadenaMarkov

import json
import numpy as np
from datetime import datetime

def actualizar_datos():
    app = create_app()
    
    with app.app_context():
        # 1. Actualizar información de una máquina
        print("Actualizando información de máquina...")
        
        # Encontrar máquina por nombre
        maquina = MaquinasCerveceria.query.filter_by(nombre="Línea Embotellado 1").first()
        
        if maquina:
            # Mostrar datos actuales
            print(f"Datos actuales: {maquina.nombre}, Criticidad: {maquina.criticidad}, Uso: {maquina.uso_operativo}%")
            
            # Actualizar datos
            maquina.uso_operativo = 85.5
            maquina.criticidad = "Muy Alta"
            maquina.frec_manteni = "Quincenal"
            
            # Guardar cambios
            db.session.commit()
            
            # Verificar cambios
            maquina_actualizada = MaquinasCerveceria.query.get(maquina.id)
            print(f"Datos actualizados: {maquina_actualizada.nombre}, Criticidad: {maquina_actualizada.criticidad}, Uso: {maquina_actualizada.uso_operativo}%")
        else:
            print("No se encontró la máquina")
        
        # 2. Actualizar contraseña de usuario
        print("\nActualizando contraseña de usuario...")
        
        # Encontrar usuario
        usuario = Usuario.query.filter_by(Usuario="jperez").first()
        
        if usuario:
            # Mostrar datos actuales (no mostramos la contraseña por seguridad)
            print(f"Usuario actual: {usuario.Usuario}, Rol: {usuario.Rol}")
            
            # Actualizar contraseña
            usuario.Password = "nueva_contraseña_segura"
            
            # Guardar cambios
            db.session.commit()
            
            print(f"Contraseña actualizada para el usuario: {usuario.Usuario}")
        else:
            print("No se encontró el usuario")
        
        # 3. Actualizar una simulación
        print("\nActualizando datos de simulación...")
        
        # Obtener primera simulación
        simulacion = SimulacionEstado.query.first()
        
        if simulacion:
            print(f"Simulación actual: ID {simulacion.id_simulacion}")
            print(f"  Temperatura: {simulacion.Temperatura}, Vibración: {simulacion.vibracion}")
            
            # Actualizar datos de la simulación
            simulacion.Temperatura = 23.8
            simulacion.vibracion = 0.41
            simulacion.Comentario = "Datos actualizados manualmente"
            
            # Guardar cambios
            db.session.commit()
            
            # Verificar cambios
            sim_actualizada = SimulacionEstado.query.get(simulacion.id_simulacion)
            print(f"Simulación actualizada: ID {sim_actualizada.id_simulacion}")
            print(f"  Temperatura: {sim_actualizada.Temperatura}, Vibración: {sim_actualizada.vibracion}")
            print(f"  Comentario: {sim_actualizada.Comentario}")
        else:
            print("No se encontraron simulaciones")
        
        # 4. Crear y actualizar ejercicios con matrices de Markov
        print("\nCreando ejercicio con matriz de estados de Markov...")
        
        # Encontrar usuario y máquina para asociar al ejercicio
        usuario = Usuario.query.filter_by(Usuario="jperez").first()
        maquina = MaquinasCerveceria.query.filter_by(nombre="Línea Embotellado 1").first()
        
        if usuario and maquina:
            # Crear matriz de transición para 4 estados: Muy bueno, bueno, medio, malo
            matriz_transicion = np.array([
                [0.7, 0.2, 0.1, 0.0],  # Transiciones desde Muy bueno
                [0.3, 0.5, 0.2, 0.0],  # Transiciones desde bueno
                [0.0, 0.3, 0.5, 0.2],  # Transiciones desde medio
                [0.0, 0.0, 0.4, 0.6]   # Transiciones desde malo
            ])
            
            # Vector de estado inicial (asumimos que comenzamos en estado "bueno")
            vector_inicial = np.array([0.0, 1.0, 0.0, 0.0])
            
            # Serializar matrices a formato JSON para guardar en la base de datos
            matriz_json = json.dumps(matriz_transicion.tolist())
            vector_json = json.dumps(vector_inicial.tolist())
            
            # Crear un nuevo ejercicio
            nuevo_ejercicio = Ejercicio(
                id_usuario=usuario.id_usuario,
                id_maquina=maquina.id,
                fecha_creacion=datetime.now(),
                matriz_estados=matriz_json,
                vector_inicial=vector_json
            )
            
            # Guardar en la base de datos
            db.session.add(nuevo_ejercicio)
            db.session.commit()
            
            print(f"Ejercicio creado con ID: {nuevo_ejercicio.id}")
            
            # Demostrar cómo recuperar y usar la matriz guardada
            ejercicio_guardado = Ejercicio.query.get(nuevo_ejercicio.id)
            
            # Deserializar las matrices desde JSON
            matriz_recuperada = np.array(json.loads(ejercicio_guardado.matriz_estados))
            vector_recuperado = np.array(json.loads(ejercicio_guardado.vector_inicial))
            
            print("\nMatriz de transición recuperada:")
            print(matriz_recuperada)
            print("\nVector inicial recuperado:")
            print(vector_recuperado)
            
            # Usar con la clase CadenaMarkov
            cadena = CadenaMarkov(matriz_recuperada, vector_recuperado)
            
            # Calcular probabilidades después de 5 pasos
            prob_5_pasos = cadena.propagar(5)
            print("\nProbabilidades después de 5 pasos:")
            print(f"Muy bueno: {prob_5_pasos[0]:.4f}")
            print(f"Bueno: {prob_5_pasos[1]:.4f}")
            print(f"Medio: {prob_5_pasos[2]:.4f}")
            print(f"Malo: {prob_5_pasos[3]:.4f}")
            
            # Calcular el estado estacionario
            estado_futuro = cadena.calculo_futuro()
            print("\nEstado estacionario a largo plazo:")
            print(f"Muy bueno: {estado_futuro[0]:.4f}")
            print(f"Bueno: {estado_futuro[1]:.4f}")
            print(f"Medio: {estado_futuro[2]:.4f}")
            print(f"Malo: {estado_futuro[3]:.4f}")
            
            # Actualizar un ejercicio existente
            print("\nActualizando matriz de ejercicio existente...")
            
            # Modificar la matriz para representar un mejor rendimiento
            matriz_actualizada = np.array([
                [0.8, 0.2, 0.0, 0.0],  # Mejores probabilidades de mantener estado Muy bueno
                [0.4, 0.5, 0.1, 0.0],  # Mejores probabilidades de pasar a Muy bueno desde bueno
                [0.1, 0.4, 0.4, 0.1],  # Mejores probabilidades de mejorar desde medio
                [0.0, 0.1, 0.5, 0.4]   # Mejores probabilidades de mejorar desde malo
            ])
            
            ejercicio_guardado.matriz_estados = json.dumps(matriz_actualizada.tolist())
            ejercicio_guardado.fecha_creacion = datetime.now()  # Actualizar fecha
            
            db.session.commit()
            
            print(f"Ejercicio con ID {ejercicio_guardado.id} actualizado correctamente")
        else:
            print("No se encontró el usuario o la máquina necesaria")

if __name__ == "__main__":
    actualizar_datos()