import sys
import os
import json
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.exc import SQLAlchemyError
import numpy as np

# Agregar directorio padre a la ruta para importaciones
directorio_padre = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if directorio_padre not in sys.path:
    sys.path.append(directorio_padre)

from database.Modelos import Ejercicio, db
from markov.cadenas_de_markov import CadenaMarkov

class ServicioEjercicio:
    """
    Servicio para gestionar operaciones relacionadas con los ejercicios de Markov en la base de datos.
    """
    
    @staticmethod
    def listar_ejercicios() -> List[Ejercicio]:
        """
        Obtiene todos los ejercicios de la base de datos.
        
        Returns:
            Lista de objetos Ejercicio
        """
        try:
            return Ejercicio.query.order_by(Ejercicio.fecha_creacion.desc()).all()
        except SQLAlchemyError as e:
            print(f"Error al listar ejercicios: {str(e)}")
            return []
    
    @staticmethod
    def buscar_por_id(id_ejercicio: int) -> Optional[Ejercicio]:
        """
        Busca un ejercicio por su ID.
        
        Args:
            id_ejercicio: ID del ejercicio a buscar
            
        Returns:
            Objeto Ejercicio o None si no se encuentra
        """
        try:
            return Ejercicio.query.get(id_ejercicio)
        except SQLAlchemyError as e:
            print(f"Error al buscar ejercicio por ID: {str(e)}")
            return None
    
    @staticmethod
    def buscar_por_maquina(id_maquina: int) -> List[Ejercicio]:
        """
        Busca ejercicios por ID de máquina.
        
        Args:
            id_maquina: ID de la máquina relacionada
            
        Returns:
            Lista de objetos Ejercicio
        """
        try:
            return Ejercicio.query.filter_by(id_maquina=id_maquina).order_by(Ejercicio.fecha_creacion.desc()).all()
        except SQLAlchemyError as e:
            print(f"Error al buscar ejercicios por máquina: {str(e)}")
            return []
    
    @staticmethod
    def validar_datos_ejercicio(datos: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Valida los datos de un ejercicio antes de crear o actualizar.
        
        Args:
            datos: Diccionario con los datos del ejercicio
            
        Returns:
            Tupla (es_valido, mensaje_error)
        """
        # Validar matriz_estados (debe ser 4x4)
        matriz = datos.get('matriz_estados')
        if not matriz or len(matriz) != 4:
            return False, "La matriz de estados debe ser 4x4."
        
        for fila in matriz:
            if len(fila) != 4:
                return False, "La matriz de estados debe ser 4x4."
            
            # Cada fila debe sumar 1
            suma_fila = sum(fila)
            if abs(suma_fila - 1.0) > 0.001:  # Tolerancia para errores de punto flotante
                return False, f"Cada fila de la matriz debe sumar 1 (fila suma {suma_fila})."
        
        # Validar vector_inicial (debe ser de longitud 4 y sumar 1)
        vector = datos.get('vector_inicial')
        if not vector or len(vector) != 4:
            return False, "El vector inicial debe tener 4 elementos."
        
        suma_vector = sum(vector)
        if abs(suma_vector - 1.0) > 0.001:  # Tolerancia para errores de punto flotante
            return False, f"El vector inicial debe sumar 1 (suma actual: {suma_vector})."
        
        # Validar nombres_estados (debe tener 4 elementos)
        nombres = datos.get('nombres_estados')
        if not nombres or len(nombres) != 4:
            return False, "Debe proporcionar nombres para los 4 estados."
        
        return True, ""
    
    @staticmethod
    def crear_ejercicio(datos: Dict[str, Any]) -> Tuple[Optional[Ejercicio], str]:
        """
        Crea un nuevo ejercicio en la base de datos.
        
        Args:
            datos: Diccionario con los datos del ejercicio
            
        Returns:
            Tupla (objeto_ejercicio, mensaje)
        """
        # Validar datos
        es_valido, mensaje = ServicioEjercicio.validar_datos_ejercicio(datos)
        if not es_valido:
            return None, mensaje
        
        try:
            nuevo_ejercicio = Ejercicio(
                id_usuario=datos.get('id_usuario', 1),  # Default a 1 si no se proporciona
                id_maquina=datos.get('id_maquina'),
                num_pasos=datos.get('num_pasos', 5),
                descripcion=datos.get('descripcion', '')
            )
            
            # Convertir a JSON para almacenamiento
            nuevo_ejercicio.set_matriz_estados(datos.get('matriz_estados'))
            nuevo_ejercicio.set_vector_inicial(datos.get('vector_inicial'))
            nuevo_ejercicio.set_nombres_estados(datos.get('nombres_estados'))
            
            # Calcular resultado
            matriz = np.array(datos.get('matriz_estados'), dtype=float)
            vector = np.array(datos.get('vector_inicial'), dtype=float)
            pasos = datos.get('num_pasos', 5)
            
            try:
                markov = CadenaMarkov(matriz, vector)
                resultado_pasos = markov.propagar(pasos).tolist()
                
                # Calcular estado estacionario y convergencia
                convergencia = markov.calcular_convergencia(max_pasos=50)
                estado_estacionario = convergencia["estado_estacionario"]
                
                # Guardar todos los datos calculados
                resultado = {
                    'resultado_pasos': resultado_pasos,
                    'estado_estacionario': estado_estacionario,
                    'convergencia': convergencia
                }
                
                nuevo_ejercicio.set_resultado(resultado)
            except Exception as e:
                return None, f"Error al calcular el resultado de Markov: {str(e)}"
        
            db.session.add(nuevo_ejercicio)
            db.session.commit()
            return nuevo_ejercicio, "Ejercicio creado y resuelto exitosamente."
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return None, f"Error al crear el ejercicio: {str(e)}"
    
    @staticmethod
    def eliminar_ejercicio(id_ejercicio: int) -> Tuple[bool, str]:
        """
        Elimina un ejercicio de la base de datos.
        
        Args:
            id_ejercicio: ID del ejercicio a eliminar
            
        Returns:
            Tupla (exito, mensaje)
        """
        try:
            ejercicio = Ejercicio.query.get(id_ejercicio)
            if not ejercicio:
                return False, f"No se encontró ejercicio con ID {id_ejercicio}."
            
            db.session.delete(ejercicio)
            db.session.commit()
            return True, "Ejercicio eliminado exitosamente."
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return False, f"Error al eliminar el ejercicio: {str(e)}"
