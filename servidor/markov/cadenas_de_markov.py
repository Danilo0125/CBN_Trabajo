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

    def calculo_futuro(self) -> np.ndarray:
        valores, vectores = np.linalg.eig(self.matriz_transicion)
        indice = np.argmin(np.abs(valores -1))
        estacionario = np.real(vectores [:,indice])
        estacionario = estacionario /estacionario.sum()
        return estacionario

