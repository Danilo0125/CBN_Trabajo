import numpy as np
from datetime import datetime
from markov.cadenas_de_markov import CadenaMarkov

class Equipo:
    def __init__(self, nombre_equipo, funcion, tiempos_uso, fecha=None):
        """
        Inicializa un equipo con su nombre, función, tiempos de uso y fecha
        """
        self.nombre_equipo = nombre_equipo
        self.funcion = funcion
        self.tiempos_uso = tiempos_uso
        
        if fecha is None:
            self.fecha = datetime.now().strftime('%Y-%m-%d')
        else:
            self.fecha = fecha
        
        self.estado = "bueno"  # Estado por defecto
        self.cadena_markov = None
        self.matriz = None
        self.vector = None
    
    def asignar_matriz(self, matriz, vector_inicial):
        """
        Asigna una matriz de transición y un vector inicial al equipo
        """
        try:
            self.matriz = np.array(matriz)
            self.vector = np.array(vector_inicial)
            self.cadena_markov = CadenaMarkov(matriz, vector_inicial)
            return True
        except ValueError as e:
            # Si hay algún error en la validación, mostramos el error pero no asignamos
            print(f"Error al crear cadena de Markov: {str(e)}")
            return False
    
    def calcular_estados(self, n_pasos):
        """
        Calcula el estado después de n pasos
        """
        if self.cadena_markov is None:
            raise ValueError("No se ha asignado una cadena de Markov al equipo")
        
        return self.cadena_markov.propagar(n_pasos)
    
    def to_dict(self):
        """
        Convierte el objeto a un diccionario para serialización JSON
        """
        return {
            'nombre_equipo': self.nombre_equipo,
            'funcion': self.funcion,
            'tiempos_uso': self.tiempos_uso,
            'fecha': self.fecha,
            'estado': self.estado
        }

