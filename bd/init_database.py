"""
Script para inicializar la base de datos
"""
from database import init_db

if __name__ == "__main__":
    import sys
    # Check if --reset flag is passed to drop all tables and recreate them
    drop_all = "--reset" in sys.argv
    
    print(f"Inicializando base de datos {'(reiniciando tablas)' if drop_all else ''}...")
    init_db(drop_all=drop_all)
    
    print("Base de datos inicializada correctamente.")
    if drop_all:
        print("\n¡ATENCIÓN! Se han eliminado y recreado todas las tablas.")
    print("\nPara recrear completamente la base de datos, ejecute este script con la opción --reset")
