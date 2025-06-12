from stable_baselines3 import PPO
import numpy as np
import os
import sys
from IAs.EquipoEnt import EquipoEnt

class ModeloPrediccion:
    def __init__(self, model_path=None):
        """Initialize the prediction model"""
        self.model = None
        self.env = None
        # Usar la ruta correcta al archivo ZIP del modelo
        self.model_path = os.path.join("IAs", "modelo_predictivo.zip") if model_path is None else model_path
        self.load_model()
    
    def load_model(self):
        """Load the PPO model"""
        try:
            # Verificar que el archivo exista
            if not os.path.exists(self.model_path):
                print(f"Error: El archivo del modelo no existe en: {self.model_path}")
                print(f"Ruta absoluta: {os.path.abspath(self.model_path)}")
                self.model = None
                return
            
            self.model = PPO.load(self.model_path)
            print(f"Modelo cargado exitosamente desde: {self.model_path}")
        except Exception as e:
            print(f"Error al cargar el modelo: {e}")
            self.model = None
    
    def predict(self, sensor_data):
        """Make a prediction based on sensor data"""
        if self.model is None:
            # Si el modelo no está cargado, devolver un resultado con valores predeterminados
            print("Advertencia: Usando predicción por defecto (modelo no cargado)")
            return {
                "raw_data": sensor_data if isinstance(sensor_data, list) else list(sensor_data),
                "action": 0,
                "action_explanation": "Continuar operación normal (predicción por defecto)",
                "is_critical": False
            }
        
        # Convert input to proper format
        if not isinstance(sensor_data, np.ndarray):
            sensor_data = np.array([sensor_data], dtype=np.float32)
        
        # Create environment with this single data point
        try:
            self.env = EquipoEnt(sensor_data)
            obs, _ = self.env.reset()
            
            # Get model prediction
            action, _ = self.model.predict(obs, deterministic=True)
            
            # Get action explanation
            action_explanation = "Mantenimiento preventivo" if action == 1 else "Continuar operación normal"
            
            # Check for critical conditions
            is_critical = False
            if sensor_data[0][0] > 80 or sensor_data[0][1] > 8:  # temperatura > 80 o vibración > 8
                is_critical = True
            
            return {
                "raw_data": sensor_data[0].tolist(),
                "action": int(action),
                "action_explanation": action_explanation,
                "is_critical": is_critical
            }
        except Exception as e:
            print(f"Error durante la predicción: {e}")
            return {
                "raw_data": sensor_data[0].tolist() if hasattr(sensor_data, 'tolist') else list(sensor_data[0]),
                "action": 0,
                "action_explanation": "Error en predicción",
                "is_critical": False,
                "error_msg": str(e)
            }

# Singleton instance
modelo_prediccion = ModeloPrediccion()

# Si se ejecuta este archivo directamente, mostrar información del modelo
if __name__ == "__main__":
    print("\nInformación del Modelo Predictivo:")
    print(f"Ruta del modelo: {modelo_prediccion.model_path}")
    print(f"Modelo cargado: {'Sí' if modelo_prediccion.model is not None else 'No'}")
    
    if modelo_prediccion.model is None:
        print("\nVerificando directorio IAs:")
        ias_dir = os.path.join(os.getcwd(), "IAs")
        if os.path.exists(ias_dir):
            print(f"- Directorio existe: {ias_dir}")
            files = os.listdir(ias_dir)
            print(f"- Archivos encontrados: {files}")
        else:
            print(f"- Directorio no existe: {ias_dir}")
            
    # Prueba de predicción con datos de ejemplo
    print("\nEjecutando predicción de prueba:")
    test_data = [25.0, 2.0, 98.0]  # temperatura, vibración, presión
    prediction = modelo_prediccion.predict(test_data)
    print(f"Datos: {test_data}")
    print(f"Predicción: {prediction}")
