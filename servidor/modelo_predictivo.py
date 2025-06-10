from stable_baselines3 import PPO
import numpy as np
import os
import sys

# Add the IAs directory to the Python path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'IAs'))
from EquipoEnt import EquipoEnt

class ModeloPrediccion:
    def __init__(self, model_path=None):
        """Initialize the prediction model"""
        self.model = None
        self.env = None
        self.model_path = model_path or os.path.join(os.path.dirname(os.path.dirname(__file__)), 'IAs', 'modelo_predictivo')
        self.load_model()
    
    def load_model(self):
        """Load the PPO model"""
        try:
            self.model = PPO.load(self.model_path)
            print(f"Modelo cargado exitosamente desde: {self.model_path}")
        except Exception as e:
            print(f"Error al cargar el modelo: {e}")
            self.model = None
    
    def predict(self, sensor_data):
        """Make a prediction based on sensor data"""
        if self.model is None:
            return {"error": "Modelo no cargado"}
        
        # Convert input to proper format
        if not isinstance(sensor_data, np.ndarray):
            sensor_data = np.array([sensor_data], dtype=np.float32)
        
        # Create environment with this single data point
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

# Singleton instance
modelo_prediccion = ModeloPrediccion()
