from stable_baselines3 import PPO
from EquipoEnt import EquipoEnt
from data_loader import cargar_datos_desde_bd  # Usamos tu función de carga

# Cargar datos reales desde la base de datos
sensor_data = cargar_datos_desde_bd(limit=10)  # Puedes ajustar el límite

# Verificamos si se cargaron datos correctamente
if sensor_data is None or len(sensor_data) == 0:
    print("No se pudieron cargar datos desde la base de datos.")
else:
    # Cargar el modelo previamente entrenado
    model = PPO.load("modelo_predictivo")  # Asegúrate de que el modelo exista

    # Crear entorno personalizado con datos reales
    env = EquipoEnt(sensor_data)

    # Reiniciar el entorno y obtener el primer estado
    obs, _ = env.reset()

    for _ in range(len(sensor_data)):
        # La IA predice una acción en base al estado
        action, _ = model.predict(obs, deterministic=True)

        # Aplicamos la acción y recibimos el nuevo estado
        obs, reward, terminated, truncated, info = env.step(action)

        # Mostrar resultados
        print(f"Estado actual: {obs}")
        print(f"Acción tomada: {'Mantenimiento' if action == 1 else 'Continuar operando'}")
        print(f"Recompensa: {reward}")

        # Si el entorno se termina por condición de fallo o fin de datos
        if terminated or truncated:
            print("¡Alerta: La máquina requiere intervención!")
            break
