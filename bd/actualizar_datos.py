"""
Ejemplo de actualización de datos en la base de datos
"""
try:
    from database import create_app
    from Modelos import db, MaquinasCerveceria, ProductoCerveza, Usuario, SimulacionEstado
except ImportError:
    from .database import create_app
    from .Modelos import db, MaquinasCerveceria, ProductoCerveza, Usuario, SimulacionEstado

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
        
        # 3. Actualizar múltiples registros a la vez
        print("\nActualizando múltiples productos...")
        
        # Actualizar todos los productos de tipo Pilsner
        productos_pilsner = ProductoCerveza.query.filter_by(tipo_cerveza="Pilsner").all()
        
        if productos_pilsner:
            print(f"Encontrados {len(productos_pilsner)} productos Pilsner")
            
            # Actualizar cada uno
            for producto in productos_pilsner:
                producto.tipo_cerveza = "Pilsner Premium"
            
            # Guardar cambios
            db.session.commit()
            
            # Verificar cambios
            productos_actualizados = ProductoCerveza.query.filter_by(tipo_cerveza="Pilsner Premium").all()
            print(f"Productos actualizados: {len(productos_actualizados)}")
            for p in productos_actualizados:
                print(f"  - {p.nombre}: {p.tipo_cerveza}")
        else:
            print("No se encontraron productos Pilsner")
        
        # 4. Actualizar una simulación
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

if __name__ == "__main__":
    actualizar_datos()