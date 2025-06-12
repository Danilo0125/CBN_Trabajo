import sys
import os
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

# Agregar directorio padre a la ruta para importaciones
directorio_padre = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if directorio_padre not in sys.path:
    sys.path.append(directorio_padre)

from database.Modelos import SimulacionEstado, db

class ServicioSimulacion:
    """
    Servicio para gestionar operaciones relacionadas con las simulaciones de estado en la base de datos.
    """
    
    @staticmethod
    def listar_simulaciones() -> List[SimulacionEstado]:
        """
        Obtiene todas las simulaciones de estado de la base de datos.
        
        Returns:
            Lista de objetos SimulacionEstado
        """
        try:
            return SimulacionEstado.query.order_by(SimulacionEstado.Fecha.desc()).all()
        except SQLAlchemyError as e:
            print(f"Error al listar simulaciones: {str(e)}")
            return []
    
    @staticmethod
    def buscar_por_id(id_simulacion: int) -> Optional[SimulacionEstado]:
        """
        Busca una simulación por su ID.
        
        Args:
            id_simulacion: ID de la simulación a buscar
            
        Returns:
            Objeto SimulacionEstado o None si no se encuentra
        """
        try:
            return SimulacionEstado.query.get(id_simulacion)
        except SQLAlchemyError as e:
            print(f"Error al buscar simulación por ID: {str(e)}")
            return None
    
    @staticmethod
    def buscar_por_maquina(linea_id: int) -> List[SimulacionEstado]:
        """
        Busca simulaciones por ID de máquina/línea.
        
        Args:
            linea_id: ID de la máquina relacionada
            
        Returns:
            Lista de objetos SimulacionEstado
        """
        try:
            return SimulacionEstado.query.filter_by(linea_id=linea_id).order_by(SimulacionEstado.Fecha.desc()).all()
        except SQLAlchemyError as e:
            print(f"Error al buscar simulaciones por máquina: {str(e)}")
            return []
    
    @staticmethod
    def buscar_por_usuario(usuario_id: int) -> List[SimulacionEstado]:
        """
        Busca simulaciones por ID de usuario.
        
        Args:
            usuario_id: ID del usuario relacionado
            
        Returns:
            Lista de objetos SimulacionEstado
        """
        try:
            return SimulacionEstado.query.filter_by(usuario_id=usuario_id).order_by(SimulacionEstado.Fecha.desc()).all()
        except SQLAlchemyError as e:
            print(f"Error al buscar simulaciones por usuario: {str(e)}")
            return []
    
    @staticmethod
    def buscar_por_fecha(fecha_inicio: datetime, fecha_fin: datetime) -> List[SimulacionEstado]:
        """
        Busca simulaciones en un rango de fechas.
        
        Args:
            fecha_inicio: Fecha inicial del rango
            fecha_fin: Fecha final del rango
            
        Returns:
            Lista de objetos SimulacionEstado
        """
        try:
            return SimulacionEstado.query.filter(
                SimulacionEstado.Fecha >= fecha_inicio,
                SimulacionEstado.Fecha <= fecha_fin
            ).order_by(SimulacionEstado.Fecha.desc()).all()
        except SQLAlchemyError as e:
            print(f"Error al buscar simulaciones por fecha: {str(e)}")
            return []
    
    @staticmethod
    def validar_datos_simulacion(datos: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Valida los datos de una simulación antes de crear o actualizar.
        
        Args:
            datos: Diccionario con los datos de la simulación
            
        Returns:
            Tupla (es_valido, mensaje_error)
        """
        # Validar campos requeridos
        campos_requeridos = ['linea_id', 'usuario_id', 'Acc_IA', 'Temperatura', 'Presion', 'vibracion']
        for campo in campos_requeridos:
            if campo not in datos:
                return False, f"El campo {campo} es requerido."
        
        # Validar que los valores numéricos sean válidos
        campos_numericos = ['Temperatura', 'Presion', 'Uso', 'Recompensa', 'vibracion']
        for campo in campos_numericos:
            if campo in datos and datos[campo] is not None:
                try:
                    float(datos[campo])
                except (ValueError, TypeError):
                    return False, f"El campo {campo} debe ser un valor numérico."
        
        # Validar que Intervenido sea booleano
        if 'Intervenido' in datos and datos['Intervenido'] is not None:
            if not isinstance(datos['Intervenido'], bool):
                return False, "El campo Intervenido debe ser un valor booleano."
        
        return True, ""
    
    @staticmethod
    def crear_simulacion(datos: Dict[str, Any]) -> Tuple[Optional[SimulacionEstado], str]:
        """
        Crea una nueva simulación en la base de datos.
        
        Args:
            datos: Diccionario con los datos de la simulación
            
        Returns:
            Tupla (objeto_simulacion, mensaje)
        """
        # Validar datos
        es_valido, mensaje = ServicioSimulacion.validar_datos_simulacion(datos)
        if not es_valido:
            return None, mensaje
        
        try:
            nueva_simulacion = SimulacionEstado(
                linea_id=datos.get('linea_id'),
                usuario_id=datos.get('usuario_id'),
                Fecha=datos.get('Fecha', datetime.utcnow()),
                Acc_IA=datos.get('Acc_IA'),
                Acc_humana=datos.get('Acc_humana'),
                Acc_final=datos.get('Acc_final'),
                Intervenido=datos.get('Intervenido', False),
                Temperatura=datos.get('Temperatura'),
                Presion=datos.get('Presion'),
                Uso=datos.get('Uso'),
                Recompensa=datos.get('Recompensa'),
                Comentario=datos.get('Comentario', ''),
                vibracion=datos.get('vibracion')
            )
            
            db.session.add(nueva_simulacion)
            db.session.commit()
            return nueva_simulacion, "Simulación creada exitosamente."
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return None, f"Error al crear la simulación: {str(e)}"
    
    @staticmethod
    def actualizar_simulacion(id_simulacion: int, datos: Dict[str, Any]) -> Tuple[Optional[SimulacionEstado], str]:
        """
        Actualiza una simulación existente.
        
        Args:
            id_simulacion: ID de la simulación a actualizar
            datos: Diccionario con los datos a actualizar
            
        Returns:
            Tupla (objeto_simulacion, mensaje)
        """
        # Validar datos
        es_valido, mensaje = ServicioSimulacion.validar_datos_simulacion(datos)
        if not es_valido:
            return None, mensaje
        
        try:
            simulacion = SimulacionEstado.query.get(id_simulacion)
            if not simulacion:
                return None, f"No se encontró simulación con ID {id_simulacion}."
            
            # Actualizar campos si están presentes en datos
            if 'linea_id' in datos:
                simulacion.linea_id = datos['linea_id']
            if 'usuario_id' in datos:
                simulacion.usuario_id = datos['usuario_id']
            if 'Fecha' in datos:
                simulacion.Fecha = datos['Fecha']
            if 'Acc_IA' in datos:
                simulacion.Acc_IA = datos['Acc_IA']
            if 'Acc_humana' in datos:
                simulacion.Acc_humana = datos['Acc_humana']
            if 'Acc_final' in datos:
                simulacion.Acc_final = datos['Acc_final']
            if 'Intervenido' in datos:
                simulacion.Intervenido = datos['Intervenido']
            if 'Temperatura' in datos:
                simulacion.Temperatura = datos['Temperatura']
            if 'Presion' in datos:
                simulacion.Presion = datos['Presion']
            if 'Uso' in datos:
                simulacion.Uso = datos['Uso']
            if 'Recompensa' in datos:
                simulacion.Recompensa = datos['Recompensa']
            if 'Comentario' in datos:
                simulacion.Comentario = datos['Comentario']
            if 'vibracion' in datos:
                simulacion.vibracion = datos['vibracion']
            
            db.session.commit()
            return simulacion, "Simulación actualizada exitosamente."
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return None, f"Error al actualizar la simulación: {str(e)}"
    
    @staticmethod
    def eliminar_simulacion(id_simulacion: int) -> Tuple[bool, str]:
        """
        Elimina una simulación de la base de datos.
        
        Args:
            id_simulacion: ID de la simulación a eliminar
            
        Returns:
            Tupla (exito, mensaje)
        """
        try:
            simulacion = SimulacionEstado.query.get(id_simulacion)
            if not simulacion:
                return False, f"No se encontró simulación con ID {id_simulacion}."
            
            db.session.delete(simulacion)
            db.session.commit()
            return True, "Simulación eliminada exitosamente."
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return False, f"Error al eliminar la simulación: {str(e)}"
