import numpy as np

class CadenaMarkov:
    def __init__(self, matriz_transicion: np.ndarray, vector_inicial: np.ndarray):
        self.matriz_transicion = np.array(matriz_transicion, dtype= float)
        self.vector_inicial = np.array(vector_inicial, dtype= float )
        self._validar_elementos()

    def _validar_elementos(self):
        if self.matriz_transicion.ndim != 2 or self.matriz_transicion.shape[0] != self.matriz_transicion.shape[1]:
            raise ValueError("la matriz de transicion debe de ser cuadrada")
        if np.any(self.matriz_transicion < 0) or np.any(self.matriz_transicion > 1):
            raise ValueError("Cada entrada de la matriz debe estar entre 0 y 1")
        sumas_filas = self.matriz_transicion.sum(axis=1)
        if not np.allclose(sumas_filas,1):
            raise ValueError(f"cada fila debe de sumasr 1 (sumas actuales:{sumas_filas})")
        if self.vector_inicial.ndim != 1 or self.vector_inicial.shape[0] != self.matriz_transicion.shape[0]:
            raise ValueError("El vector inicial debe tener la misma longitud que la dimension de la matriz")
        if np.any(self.vector_inicial < 0) or not np.isclose(self.vector_inicial.sum(), 1):
            raise ValueError("El vector inicial debe ser un vector de probabilidad >= 0 y suma =1)")

    def propagar(self, pasos: int) -> np.ndarray:
        if not isinstance(pasos, int) or pasos < 0:
            raise ValueError("el numero de pasos debe ser un entero")
        matriz_n = np.linalg.matrix_power(self.matriz_transicion, pasos)
        return self.vector_inicial @ matriz_n

    def calculo_futuro(self, metodo="eigen", max_iter=1000, tolerancia=1e-8) -> np.ndarray:
        """
        Calcula el vector de estado estacionario (distribución a largo plazo)
        
        Args:
            metodo: Método de cálculo ('eigen' para vectores propios, 'potencia' para método iterativo)
            max_iter: Máximo número de iteraciones para el método de potencia
            tolerancia: Tolerancia de convergencia para el método de potencia
            
        Returns:
            Vector estacionario normalizado
        """
        if metodo == "eigen":
            # Método de vectores propios (más rápido, pero menos intuitivo)
            valores, vectores = np.linalg.eig(self.matriz_transicion.T)  # Transpuesta para vectores por la izquierda
            indice = np.argmin(np.abs(valores - 1))
            estacionario = np.real(vectores[:, indice])
            estacionario = estacionario / estacionario.sum()
            return estacionario
            
        elif metodo == "potencia":
            # Método iterativo de potencia (más intuitivo y muestra convergencia)
            v = self.vector_inicial.copy()
            estados = [v.copy()]
            
            # Iteración hasta convergencia
            for _ in range(max_iter):
                v_nuevo = v @ self.matriz_transicion
                estados.append(v_nuevo.copy())
                
                # Verificar convergencia
                if np.linalg.norm(v_nuevo - v) < tolerancia:
                    break
                    
                v = v_nuevo
                
            # Normalizar el resultado final (por si acaso)
            v = v / v.sum()
            return v, estados
            
        else:
            raise ValueError(f"Método desconocido: {metodo}. Use 'eigen' o 'potencia'.")
    
    def calcular_convergencia(self, max_pasos=100) -> dict:
        """
        Calcula la convergencia paso a paso hacia el estado estacionario.
        
        Args:
            max_pasos: Número máximo de pasos a calcular
            
        Returns:
            Diccionario con secuencia de estados y medida de convergencia
        """
        # Calcular el verdadero estado estacionario usando eigen
        estado_estacionario = self.calculo_futuro(metodo="eigen")
        
        # Calcular la secuencia de estados
        estados = []
        distancias = []
        v = self.vector_inicial.copy()
        
        # Incluir estado inicial
        estados.append(v.copy().tolist())
        
        # Calcular distancia al estado estacionario
        distancia = np.linalg.norm(v - estado_estacionario)
        distancias.append(float(distancia))
        
        # Calcular los estados sucesivos
        for i in range(max_pasos):
            # Propagar al siguiente estado
            v = v @ self.matriz_transicion
            
            # Guardar estado actual
            estados.append(v.copy().tolist())
            
            # Calcular distancia al estado estacionario
            distancia = np.linalg.norm(v - estado_estacionario)
            distancias.append(float(distancia))
            
            # Verificar convergencia temprana (opcional)
            if distancia < 1e-6:
                print(f"Convergencia alcanzada en el paso {i+1}")
                break
        
        # Asegurarse de que el último estado sea el estacionario para visualización
        if len(estados) < 2 or np.linalg.norm(np.array(estados[-1]) - estado_estacionario) > 1e-6:
            estados.append(estado_estacionario.tolist())
            distancias.append(0.0)
        
        print(f"Generados {len(estados)} estados para la visualización de convergencia")
        
        return {
            "estados": estados,
            "distancias": distancias,
            "estado_estacionario": estado_estacionario.tolist()
        }

