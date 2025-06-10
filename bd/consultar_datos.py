"""
Ejemplo de consulta de datos en la base de datos
"""
try:
    from database import create_app
    from Modelos import db, MaquinasCerveceria, ProductoCerveza, InsumosCerveza, Usuario, SimulacionEstado
except ImportError:
    from .database import create_app
    from .Modelos import db, MaquinasCerveceria, ProductoCerveza, InsumosCerveza, Usuario, SimulacionEstado

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
            
            # Consultar productos por máquina
            print(f"  Productos asociados:")
            for producto in maquina.productos:
                print(f"  - {producto.nombre} ({producto.tipo_cerveza}, {producto.volumen}ml)")
        
        # Consultar productos con insumos
        print("\n=== PRODUCTOS E INSUMOS ===")
        productos = ProductoCerveza.query.all()
        for producto in productos:
            print(f"Producto: {producto.nombre} ({producto.tipo_cerveza})")
            print(f"  Insumos:")
            for insumo in producto.insumos:
                print(f"  - {insumo.nombre} ({insumo.tipo})")
                
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

if __name__ == "__main__":
    consultar_datos()
