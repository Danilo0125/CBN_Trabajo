import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import json

def simular_datos_sensores(duracion_minutos=60, resolucion_segundos=1):
    """
    Genera datos simulados para 3 sensores: temperatura, vibración y presión.
    
    Parámetros:
    - duracion_minutos: duración de la simulación en minutos
    - resolucion_segundos: intervalo de muestreo en segundos
    
    Retorna:
    - dict con datos de los 3 sensores
    """
    total_puntos = int(duracion_minutos * 60 / resolucion_segundos)
    
    # Simular temperatura (20-80°C con variaciones)
    temp_base = 50
    temperatura = temp_base + np.random.normal(0, 5, total_puntos) + 10 * np.sin(np.linspace(0, 4*np.pi, total_puntos))
    
    # Simular vibración (0-10 mm/s con picos ocasionales)
    vibracion_base = 2
    vibracion = vibracion_base + np.random.exponential(1, total_puntos)
    # Agregar algunos picos de vibración
    picos_indices = np.random.choice(total_puntos, size=int(total_puntos*0.05), replace=False)
    vibracion[picos_indices] += np.random.uniform(5, 15, len(picos_indices))
    
    # Simular presión (1-5 bar con tendencia)
    presion_base = 3
    presion = presion_base + np.random.normal(0, 0.3, total_puntos) + 0.5 * np.sin(np.linspace(0, 2*np.pi, total_puntos))
    
    return {
        'temperatura': temperatura.tolist(),
        'vibracion': vibracion.tolist(),
        'presion': presion.tolist()
    }

def generar_datos_tiempo_real():
    """
    Genera un punto de datos en tiempo real para los 3 sensores.
    
    Retorna:
    - dict con timestamp y valores de sensores
    """
    timestamp = datetime.now().isoformat()
    
    # Simular valores actuales
    temperatura = 50 + np.random.normal(0, 5) + 10 * np.sin(datetime.now().timestamp() / 100)
    vibracion = 2 + np.random.exponential(1)
    presion = 3 + np.random.normal(0, 0.3)
    
    return {
        'timestamp': timestamp,
        'temperatura': round(temperatura, 2),
        'vibracion': round(vibracion, 2),
        'presion': round(presion, 2)
    }

def simular_datos_horno(duracion_horas=24, resolucion_minutos=1, 
                        temp_inicial=25, temp_objetivo=200,
                        ruido_desv=2, num_picos=3, num_caidas=3):
    """
    Genera un DataFrame con simulación de temperatura de un horno durante un periodo dado.
    Cada ejecución producirá resultados distintos (sin semilla fija).
    
    Parámetros:
    - duracion_horas: número de horas a simular (por defecto 24).
    - resolucion_minutos: intervalo de muestreo en minutos (por defecto 1).
    - temp_inicial: temperatura inicial en °C (por defecto 25).
    - temp_objetivo: temperatura de estabilización en °C (por defecto 200).
    - ruido_desv: desviación estándar del ruido gaussiano en la fase estable (por defecto 2).
    - num_picos: cantidad de picos de temperatura aleatorios después de la estabilización (por defecto 3).
    - num_caidas: cantidad de caídas bruscas de temperatura aleatorias (por defecto 3).
    
    Retorna:
    - df: DataFrame de pandas con índice de fechas (cada minuto) y columna 'Temperature (°C)'.
    """
    # No fijamos semilla: cada ejecución será distinta
    # np.random.seed(None)

    # Calcular número total de lecturas
    total_minutos = int(duracion_horas * 60 / resolucion_minutos)
    
    # Crear rango de fechas desde el inicio del día actual, con resolución de 'resolucion_minutos'
    inicio = pd.Timestamp('2025-06-01 00:00')  # puedes cambiar la fecha si lo deseas
    time_index = pd.date_range(start=inicio, periods=total_minutos, freq=f'{resolucion_minutos}T')
    
    # Inicializar arreglo de temperaturas
    temperatures = np.zeros(len(time_index))
    
    # 1) Fase de calentamiento: de temp_inicial a temp_objetivo en la primera hora
    minutos_calentamiento = int(60 / resolucion_minutos)
    temperaturas_calentamiento = np.linspace(temp_inicial, temp_objetivo, minutos_calentamiento)
    temperatures[:minutos_calentamiento] = temperaturas_calentamiento
    
    # 2) Fase estable: desde el fin del calentamiento hasta el final, con ruido gaussiano
    restante = len(time_index) - minutos_calentamiento
    temperatures[minutos_calentamiento:] = temp_objetivo + np.random.normal(0, ruido_desv, size=restante)
    
    # 3) Insertar picos aleatorios (spikes) de temperatura
    for _ in range(num_picos):
        start_idx = np.random.randint(minutos_calentamiento, len(time_index) - 15)
        duracion_spike = np.random.randint(5, 15)  # duración entre 5 y 15 minutos
        amp_spike = np.random.uniform(30, 60)      # amplitud del spike entre 30°C y 60°C
        end_idx = min(start_idx + duracion_spike, len(time_index))
        temperatures[start_idx:end_idx] += amp_spike
    
    # 4) Insertar caídas bruscas de temperatura
    for _ in range(num_caidas):
        start_idx = np.random.randint(minutos_calentamiento, len(time_index) - 15)
        duracion_drop = np.random.randint(5, 15)
        amp_drop = np.random.uniform(30, 60)       # amplitud de la caída entre 30°C y 60°C
        end_idx = min(start_idx + duracion_drop, len(time_index))
        temperatures[start_idx:end_idx] -= amp_drop
    
    # Construir DataFrame
    df = pd.DataFrame({'Temperature (°C)': temperatures}, index=time_index)
    return df

def graficar_temperatura(df):
    """
    Grafica la serie de temperatura vs hora a partir de un DataFrame.
    
    - df: DataFrame con índice de fechas y columna 'Temperature (°C)'.
    """
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['Temperature (°C)'], color='orange')
    plt.xlabel('Hora')
    plt.ylabel('Temperatura (°C)')
    plt.title('Simulación de Temperatura de un Horno')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Generar datos de ejemplo
    datos = simular_datos_sensores()
    print(f"Generados {len(datos['temperatura'])} puntos de datos para cada sensor")
    
    # Generar un punto en tiempo real
    punto_actual = generar_datos_tiempo_real()
    print(f"Datos actuales: {punto_actual}")
    
    # Generar datos sin semilla fija para que cambien en cada ejecución
    df_horno = simular_datos_horno()
    
    # Mostrar las primeras filas del DataFrame (opcional)
    print(df_horno.head()) 
    
    # Graficar la simulación
    # graficar_temperatura(df_horno)
