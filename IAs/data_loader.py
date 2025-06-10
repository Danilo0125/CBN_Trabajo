import psycopg2
import numpy as np

def conectar_bd():
    """
    Establece y devuelve una conexión a la base de datos PostgreSQL
    """
    try:
        conn = psycopg2.connect(
            dbname="Inteligencia_Investigacion_Redes",
            user="postgres",
            password="12345",
            host="localhost",
            port="5432"
        )
        return conn
    except Exception as e:
        print(f"Error al conectar a la BD: {e}")
        return None


def cargar_datos_desde_bd(limit=100):
    """
    Carga datos de temperatura, uso (vibración) y presión desde la base de datos
    """
    try:
        conn = conectar_bd()  # Usamos la función de conexión
        if not conn:
            return None

        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT temperatura, uso, presion
            FROM simulacion_estado
            WHERE temperatura IS NOT NULL 
              AND uso IS NOT NULL 
              AND presion IS NOT NULL
            ORDER BY Fecha ASC
            LIMIT {limit};
        """)
        filas = cursor.fetchall()
        cursor.close()
        conn.close()

        datos = np.array(filas, dtype=np.float32)
        return datos
    except Exception as e:
        print(f"Error al consultar la BD: {e}")
        return None


if __name__ == "__main__":
    datos = cargar_datos_desde_bd()
    if datos is not None:
        print("Datos cargados desde la BD:")
        print(datos)
    else:
        print("No se pudieron cargar los datos.")