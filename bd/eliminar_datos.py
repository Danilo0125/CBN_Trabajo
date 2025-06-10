"""
Ejemplo de eliminación de datos en la base de datos
"""
try:
    from database import create_app
    from Modelos import db, MaquinasCerveceria, Usuario, SimulacionEstado, Ejercicio
except ImportError:
    from .database import create_app
    from .Modelos import db, MaquinasCerveceria, Usuario, SimulacionEstado, Ejercicio

def eliminar_datos():
    app = create_app()
    
    with app.app_context():
        # 1. Eliminar una simulación específica
        print("Eliminando una simulación...")
        
        # Buscar la simulación con la temperatura más alta
        simulacion = SimulacionEstado.query.order_by(SimulacionEstado.Temperatura.desc()).first()
        
        if simulacion:
            print(f"Eliminando simulación ID: {simulacion.id_simulacion}")
            print(f"  Temperatura: {simulacion.Temperatura}, Fecha: {simulacion.Fecha}")
            
            # Guardar ID para verificación posterior
            sim_id = simulacion.id_simulacion
            
            # Eliminar la simulación
            db.session.delete(simulacion)
            db.session.commit()
            
            # Verificar que se haya eliminado
            sim_verificacion = SimulacionEstado.query.get(sim_id)
            if sim_verificacion is None:
                print(f"✅ Simulación ID {sim_id} eliminada correctamente")
            else:
                print(f"❌ Error: La simulación ID {sim_id} no se eliminó correctamente")
        else:
            print("No se encontraron simulaciones para eliminar")
        
        # 2. Eliminar usuario (verificando primero relaciones)
        print("\nEliminando usuario...")
        
        # Encontrar usuario
        usuario = Usuario.query.filter_by(Usuario="mgonzalez").first()
        
        if usuario:
            print(f"Preparando eliminación de usuario: {usuario.Nombre} {usuario.ApelP_pater} (ID: {usuario.id_usuario})")
            
            # Verificar si tiene simulaciones asociadas
            simulaciones_asociadas = SimulacionEstado.query.filter_by(usuario_id=usuario.id_usuario).all()
            
            if simulaciones_asociadas:
                print(f"  El usuario tiene {len(simulaciones_asociadas)} simulaciones asociadas")
                print("  Eliminando simulaciones asociadas...")
                
                for sim in simulaciones_asociadas:
                    db.session.delete(sim)
                
                print(f"  {len(simulaciones_asociadas)} simulaciones eliminadas")
            
            # Verificar si tiene ejercicios asociados
            ejercicios_asociados = Ejercicio.query.filter_by(id_usuario=usuario.id_usuario).all()
            
            if ejercicios_asociados:
                print(f"  El usuario tiene {len(ejercicios_asociados)} ejercicios asociados")
                print("  Eliminando ejercicios asociados...")
                
                for ejercicio in ejercicios_asociados:
                    db.session.delete(ejercicio)
                
                print(f"  {len(ejercicios_asociados)} ejercicios eliminados")
            
            # Ahora podemos eliminar el usuario
            usuario_id = usuario.id_usuario
            db.session.delete(usuario)
            db.session.commit()
            
            # Verificar eliminación
            usuario_verificacion = Usuario.query.get(usuario_id)
            if usuario_verificacion is None:
                print(f"✅ Usuario ID {usuario_id} eliminado correctamente")
            else:
                print(f"❌ Error: El usuario ID {usuario_id} no se eliminó correctamente")
        else:
            print("No se encontró el usuario especificado")
        
        # 3. Eliminar ejercicio de Markov
        print("\nEliminando ejercicio de cadena de Markov...")
        
        # Buscar el ejercicio más antiguo
        ejercicio = Ejercicio.query.order_by(Ejercicio.fecha_creacion.asc()).first()
        
        if ejercicio:
            maquina = MaquinasCerveceria.query.get(ejercicio.id_maquina)
            usuario = Usuario.query.get(ejercicio.id_usuario)
            print(f"Eliminando ejercicio ID: {ejercicio.id}")
            print(f"  Creado por: {usuario.Usuario}")
            print(f"  Máquina: {maquina.nombre}")
            print(f"  Fecha: {ejercicio.fecha_creacion}")
            
            # Guardar ID para verificación posterior
            ejercicio_id = ejercicio.id
            
            # Eliminar el ejercicio
            db.session.delete(ejercicio)
            db.session.commit()
            
            # Verificar que se haya eliminado
            ejercicio_verificacion = Ejercicio.query.get(ejercicio_id)
            if ejercicio_verificacion is None:
                print(f"✅ Ejercicio ID {ejercicio_id} eliminado correctamente")
            else:
                print(f"❌ Error: El ejercicio ID {ejercicio_id} no se eliminó correctamente")
        else:
            print("No se encontraron ejercicios para eliminar")

if __name__ == "__main__":
    eliminar_datos()
