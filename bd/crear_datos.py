"""
Ejemplo de creación de datos en la base de datos
"""
try:
    from database import create_app
    from Modelos import db, MaquinasCerveceria, Usuario, SimulacionEstado, Ejercicio
except ImportError:
    from .database import create_app
    from .Modelos import db, MaquinasCerveceria, Usuario, SimulacionEstado, Ejercicio

import datetime
import json
import numpy as np

def crear_datos_ejemplo():
    app = create_app()
    
    with app.app_context():
        # Crear usuarios
        print("Creando usuarios...")
        usuarios = [
            Usuario(
                Nombre="Admin",
                ApelP_pater="Sistema",
                ApelP_mater="CBN",
                Rol="Administrador",
                Usuario="admin",
                Password="admin123"
            ),
            Usuario(
                Nombre="Juan",
                ApelP_pater="Perez",
                ApelP_mater="Lopez",
                Rol="Operador",
                Usuario="jperez",
                Password="123456"
            ),
            Usuario(
                Nombre="Maria",
                ApelP_pater="Gonzalez",
                ApelP_mater="Ruiz",
                Rol="Supervisor",
                Usuario="mgonzalez",
                Password="654321"
            )
        ]
        
        # Crear máquinas
        print("Creando máquinas...")
        maquinas = [
            MaquinasCerveceria(
                nombre="Línea Embotellado 1",
                descripcion="Línea principal de embotellado de cerveza",
                tipo_maquina="Embotellado",
                frec_manteni="Mensual",
                temp_mini=5.0,
                temp_maxi=25.0,
                uso_operativo=80.0,
                presion_max=3.5,
                criticidad="Alta"
            ),
            MaquinasCerveceria(
                nombre="Fermentador A",
                descripcion="Tanque de fermentación principal",
                tipo_maquina="Fermentación",
                frec_manteni="Trimestral",
                temp_mini=15.0,
                temp_maxi=22.0,
                uso_operativo=90.0,
                presion_max=2.0,
                criticidad="Alta"
            ),
            MaquinasCerveceria(
                nombre="Pasteurizador 2",
                descripcion="Pasteurizador de cerveza",
                tipo_maquina="Pasteurización",
                frec_manteni="Bimensual",
                temp_mini=60.0,
                temp_maxi=85.0,
                uso_operativo=75.0,
                presion_max=1.8,
                criticidad="Media"
            )
        ]
        
        # Añadir a la sesión
        for usuario in usuarios:
            db.session.add(usuario)
        
        for maquina in maquinas:
            db.session.add(maquina)
        
        # Commit para obtener IDs
        db.session.commit()
        
        # Crear simulaciones
        print("Creando simulaciones...")
        simulaciones = [
            SimulacionEstado(
                linea_id=maquinas[0].id,
                usuario_id=usuarios[1].id_usuario,
                Fecha=datetime.datetime.now(),
                Acc_IA="Reducir temperatura",
                Acc_humana="Reducir temperatura",
                Acc_final="Reducir temperatura",
                Intervenido=False,
                Temperatura=22.5,
                Presion=2.8,
                Uso=78.5,
                Recompensa=0.85,
                Comentario="Simulación exitosa",
                vibracion=0.32
            ),
            SimulacionEstado(
                linea_id=maquinas[1].id,
                usuario_id=usuarios[2].id_usuario,
                Fecha=datetime.datetime.now(),
                Acc_IA="Aumentar presión",
                Acc_humana="Mantener presión",
                Acc_final="Mantener presión",
                Intervenido=True,
                Temperatura=18.2,
                Presion=1.5,
                Uso=85.0,
                Recompensa=0.65,
                Comentario="Intervención manual necesaria",
                vibracion=0.45
            )
        ]
        
        for simulacion in simulaciones:
            db.session.add(simulacion)
        
        # Crear ejercicios de Markov
        print("Creando ejercicios de cadenas de Markov...")
        
        # Matriz de ejemplo para 4 estados: Muy bueno, bueno, medio, malo
        matriz_ejemplo_1 = np.array([
            [0.7, 0.2, 0.1, 0.0],  # Transiciones desde Muy bueno
            [0.3, 0.5, 0.2, 0.0],  # Transiciones desde bueno
            [0.0, 0.3, 0.5, 0.2],  # Transiciones desde medio
            [0.0, 0.0, 0.4, 0.6]   # Transiciones desde malo
        ])
        
        # Vector inicial (empezando en estado "bueno")
        vector_inicial_1 = np.array([0.0, 1.0, 0.0, 0.0])
        
        # Segunda matriz de ejemplo con diferente comportamiento
        matriz_ejemplo_2 = np.array([
            [0.8, 0.2, 0.0, 0.0],  # Mejores probabilidades de mantener estado Muy bueno
            [0.4, 0.5, 0.1, 0.0],  # Mejores probabilidades de pasar a Muy bueno desde bueno
            [0.1, 0.4, 0.4, 0.1],  # Mejores probabilidades de mejorar desde medio
            [0.0, 0.1, 0.5, 0.4]   # Mejores probabilidades de mejorar desde malo
        ])
        
        # Vector inicial (empezando en estado "medio")
        vector_inicial_2 = np.array([0.0, 0.0, 1.0, 0.0])
        
        ejercicios = [
            Ejercicio(
                id_usuario=usuarios[1].id_usuario,  # jperez
                id_maquina=maquinas[0].id,  # Línea Embotellado 1
                fecha_creacion=datetime.datetime.now(),
                matriz_estados=json.dumps(matriz_ejemplo_1.tolist()),
                vector_inicial=json.dumps(vector_inicial_1.tolist())
            ),
            Ejercicio(
                id_usuario=usuarios[2].id_usuario,  # mgonzalez
                id_maquina=maquinas[1].id,  # Fermentador A
                fecha_creacion=datetime.datetime.now(),
                matriz_estados=json.dumps(matriz_ejemplo_2.tolist()),
                vector_inicial=json.dumps(vector_inicial_2.tolist())
            )
        ]
        
        for ejercicio in ejercicios:
            db.session.add(ejercicio)
        
        # Commit final
        db.session.commit()
        print("Datos de ejemplo creados con éxito.")

if __name__ == "__main__":
    crear_datos_ejemplo()
