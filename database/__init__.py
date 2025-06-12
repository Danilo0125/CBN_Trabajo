try:
    # Try absolute imports when run as a script
    from database import init_db, create_app
    from Modelos import db, MaquinasCerveceria, ProductoCerveza, InsumosCerveza, Usuario, PrediceEstado, SimulacionEstado
except ImportError:
    # Fall back to relative imports when imported as a module
    from .database import init_db, create_app
    from .Modelos import db, MaquinasCerveceria, ProductoCerveza, InsumosCerveza, Usuario, PrediceEstado, SimulacionEstado

def initialize_database():
    """Inicializa la base de datos eliminando las tablas existentes y creándolas nuevamente"""
    init_db(drop_all=True)

# Si este archivo se ejecuta directamente, inicializa la base de datos
if __name__ == "__main__":
    initialize_database()
