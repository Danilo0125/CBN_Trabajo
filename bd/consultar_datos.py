"""
Ejemplo de consulta de datos en la base de datos
"""
try:
    from database import create_app
    from Modelos import db, MaquinasCerveceria, Usuario, SimulacionEstado, Ejercicio
except ImportError:
    from .database import create_app
    from .Modelos import db, MaquinasCerveceria, Usuario, SimulacionEstado, Ejercicio

import json
import numpy as np

def consultar_datos():
    app = create_app()
    
    with app.app_context():
        # Consultar usuarios
        print("\n=== USUARIOS ===")
        usuarios = Usuario.query.all()
        for usuario in usuarios:
            print(f"ID: {usuario.id_usuario}, Nombre: {usuario.Nombre} {usuario.ApelP_pater}, Rol: {usuario.Rol}")
        
        # Consultar máquinas
        print("\n=== MÁQUINAS ===")
        maquinas = MaquinasCerveceria.query.all()
        for maquina in maquinas:
            print(f"ID: {maquina.id}, Nombre: {maquina.nombre}, Tipo: {maquina.tipo_maquina}")
                
        # Consultar simulaciones
        print("\n=== SIMULACIONES ===")
        simulaciones = SimulacionEstado.query.all()
        for sim in simulaciones:
            maquina = MaquinasCerveceria.query.get(sim.linea_id)
            usuario = Usuario.query.get(sim.usuario_id)
            print(f"Simulación ID: {sim.id_simulacion}")
            print(f"  Máquina: {maquina.nombre}")
            print(f"  Usuario: {usuario.Nombre} {usuario.ApelP_pater}")
            print(f"  Fecha: {sim.Fecha}")
            print(f"  Temperatura: {sim.Temperatura}, Presión: {sim.Presion}, Vibración: {sim.vibracion}")
            print(f"  Acción IA: {sim.Acc_IA}")
            print(f"  Acción Final: {sim.Acc_final}")
            print(f"  Comentario: {sim.Comentario}")
            print("")
        
        # Consultas con filtros
        print("\n=== CONSULTAS CON FILTROS ===")
        
        # Máquinas de alta criticidad
        print("Máquinas de criticidad alta:")
        alta_criticidad = MaquinasCerveceria.query.filter_by(criticidad="Alta").all()
        for maquina in alta_criticidad:
            print(f"  - {maquina.nombre}")
        
        # Simulaciones con intervención humana
        print("\nSimulaciones con intervención humana:")
        intervenciones = SimulacionEstado.query.filter_by(Intervenido=True).all()
        for intervencion in intervenciones:
            maquina = MaquinasCerveceria.query.get(intervencion.linea_id)
            print(f"  - ID: {intervencion.id_simulacion}, Máquina: {maquina.nombre}, Fecha: {intervencion.Fecha}")

        # Consultar ejercicios de Markov
        print("\n=== EJERCICIOS DE CADENAS DE MARKOV ===")
        ejercicios = Ejercicio.query.all()
        for ej in ejercicios:
            maquina = MaquinasCerveceria.query.get(ej.id_maquina)
            usuario = Usuario.query.get(ej.id_usuario)
            print(f"Ejercicio ID: {ej.id}")
            print(f"  Máquina: {maquina.nombre}")
            print(f"  Usuario: {usuario.Nombre} {usuario.ApelP_pater}")
            print(f"  Fecha: {ej.fecha_creacion}")
            
            # Deserializar matriz y vector
            matriz = np.array(json.loads(ej.matriz_estados))
            vector = np.array(json.loads(ej.vector_inicial))
            
            print(f"  Matriz de transición (forma {matriz.shape}):")
            print(matriz)
            print(f"  Vector inicial:")
            print(vector)
            print("")
        
        # Consultas con filtros específicos para ejercicios
        print("\n=== CONSULTAS DE EJERCICIOS CON FILTROS ===")
        
        # Ejercicios creados por un usuario específico
        print("Ejercicios creados por usuario 'jperez':")
        usuario_jperez = Usuario.query.filter_by(Usuario="jperez").first()
        if usuario_jperez:
            ejercicios_usuario = Ejercicio.query.filter_by(id_usuario=usuario_jperez.id_usuario).all()
            print(f"  Encontrados {len(ejercicios_usuario)} ejercicios")
            for ej in ejercicios_usuario:
                maquina = MaquinasCerveceria.query.get(ej.id_maquina)
                print(f"  - ID: {ej.id}, Máquina: {maquina.nombre}, Fecha: {ej.fecha_creacion}")
        
        # Ejercicios para una máquina específica
        print("\nEjercicios para 'Línea Embotellado 1':")
        maquina_embotellado = MaquinasCerveceria.query.filter_by(nombre="Línea Embotellado 1").first()
        if maquina_embotellado:
            ejercicios_maquina = Ejercicio.query.filter_by(id_maquina=maquina_embotellado.id).all()
            print(f"  Encontrados {len(ejercicios_maquina)} ejercicios")
            for ej in ejercicios_maquina:
                usuario = Usuario.query.get(ej.id_usuario)
                print(f"  - ID: {ej.id}, Usuario: {usuario.Usuario}, Fecha: {ej.fecha_creacion}")

if __name__ == "__main__":
    consultar_datos()
