"""
Ejemplo de creación de datos en la base de datos
"""
try:
    from database import create_app
    from Modelos import db, MaquinasCerveceria, ProductoCerveza, InsumosCerveza, Usuario, SimulacionEstado
except ImportError:
    from .database import create_app
    from .Modelos import db, MaquinasCerveceria, ProductoCerveza, InsumosCerveza, Usuario, SimulacionEstado

import datetime

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
        
        # Realizar primer commit para obtener IDs
        db.session.commit()
        
        # Crear productos asociados a máquinas
        print("Creando productos...")
        productos = [
            ProductoCerveza(
                nombre="Cerveza Pilsener",
                tipo_cerveza="Pilsner",
                volumen=330.0,
                envase="Botella",
                maquina_id=maquinas[0].id
            ),
            ProductoCerveza(
                nombre="Cerveza Negra",
                tipo_cerveza="Stout",
                volumen=500.0,
                envase="Botella",
                maquina_id=maquinas[0].id
            ),
            ProductoCerveza(
                nombre="Cerveza Dorada",
                tipo_cerveza="Lager",
                volumen=1000.0,
                envase="Botella",
                maquina_id=maquinas[1].id
            )
        ]
        
        for producto in productos:
            db.session.add(producto)
        
        # Realizar segundo commit para obtener IDs de productos
        db.session.commit()
        
        # Crear insumos asociados a productos
        print("Creando insumos...")
        insumos = [
            InsumosCerveza(
                nombre="Malta Pilsner",
                tipo="Malta",
                producto_id=productos[0].id_producto
            ),
            InsumosCerveza(
                nombre="Lúpulo Saaz",
                tipo="Lúpulo",
                producto_id=productos[0].id_producto
            ),
            InsumosCerveza(
                nombre="Malta Tostada",
                tipo="Malta",
                producto_id=productos[1].id_producto
            ),
            InsumosCerveza(
                nombre="Lúpulo Cascade",
                tipo="Lúpulo",
                producto_id=productos[2].id_producto
            )
        ]
        
        for insumo in insumos:
            db.session.add(insumo)
        
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
        
        # Commit final
        db.session.commit()
        print("Datos de ejemplo creados con éxito.")

if __name__ == "__main__":
    crear_datos_ejemplo()
