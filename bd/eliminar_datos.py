"""
Ejemplo de eliminación de datos en la base de datos
"""
try:
    from database import create_app
    from Modelos import db, MaquinasCerveceria, ProductoCerveza, InsumosCerveza, Usuario, SimulacionEstado
except ImportError:
    from .database import create_app
    from .Modelos import db, MaquinasCerveceria, ProductoCerveza, InsumosCerveza, Usuario, SimulacionEstado

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
        
        # 2. Eliminar un insumo
        print("\nEliminando un insumo...")
        
        # Buscar un insumo específico
        insumo = InsumosCerveza.query.filter_by(nombre="Lúpulo Saaz").first()
        
        if insumo:
            print(f"Eliminando insumo: {insumo.nombre} (ID: {insumo.id_insumo})")
            
            # Guardar ID para verificación
            insumo_id = insumo.id_insumo
            
            # Eliminar el insumo
            db.session.delete(insumo)
            db.session.commit()
            
            # Verificar eliminación
            insumo_verificacion = InsumosCerveza.query.get(insumo_id)
            if insumo_verificacion is None:
                print(f"✅ Insumo ID {insumo_id} eliminado correctamente")
            else:
                print(f"❌ Error: El insumo ID {insumo_id} no se eliminó correctamente")
        else:
            print("No se encontró el insumo especificado")
        
        # 3. Eliminar todos los productos de cierto tipo
        print("\nEliminando productos por tipo...")
        
        # Contar productos de tipo Stout antes de eliminar
        productos_stout = ProductoCerveza.query.filter_by(tipo_cerveza="Stout").all()
        
        if productos_stout:
            print(f"Encontrados {len(productos_stout)} productos tipo Stout")
            
            # Primero debemos eliminar los insumos asociados para evitar violaciones de restricciones de clave foránea
            for producto in productos_stout:
                # Obtener y eliminar insumos asociados
                insumos_asociados = InsumosCerveza.query.filter_by(producto_id=producto.id_producto).all()
                for insumo in insumos_asociados:
                    print(f"  Eliminando insumo asociado: {insumo.nombre}")
                    db.session.delete(insumo)
                
                # Ahora podemos eliminar el producto
                print(f"  Eliminando producto: {producto.nombre}")
                db.session.delete(producto)
            
            # Commit para confirmar todas las eliminaciones
            db.session.commit()
            
            # Verificar eliminación
            productos_verificacion = ProductoCerveza.query.filter_by(tipo_cerveza="Stout").all()
            if len(productos_verificacion) == 0:
                print(f"✅ Todos los productos Stout fueron eliminados correctamente")
            else:
                print(f"❌ Error: Algunos productos Stout no se eliminaron. Quedan: {len(productos_verificacion)}")
        else:
            print("No se encontraron productos tipo Stout")
        
        # 4. Eliminar usuario (verificando primero relaciones)
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

if __name__ == "__main__":
    eliminar_datos()
