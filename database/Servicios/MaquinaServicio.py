import sys
import os
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.exc import SQLAlchemyError

# Agregar directorio padre a la ruta para importaciones
directorio_padre = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if directorio_padre not in sys.path:
    sys.path.append(directorio_padre)

from database.Modelos import MaquinasCerveceria, db

class ServicioMaquina:
    """
    Servicio para gestionar operaciones relacionadas con las máquinas en la base de datos.
    """
    
    @staticmethod
    def listar_maquinas() -> List[MaquinasCerveceria]:
        """
        Obtiene todas las máquinas de la base de datos.
        
        Returns:
            Lista de objetos MaquinasCerveceria
        """
        try:
            return MaquinasCerveceria.query.all()
        except SQLAlchemyError as e:
            print(f"Error al listar máquinas: {str(e)}")
            return []
    
    @staticmethod
    def buscar_por_id(id_maquina: int) -> Optional[MaquinasCerveceria]:
        """
        Busca una máquina por su ID.
        
        Args:
            id_maquina: ID de la máquina a buscar
            
        Returns:
            Objeto MaquinasCerveceria o None si no se encuentra
        """
        try:
            return MaquinasCerveceria.query.get(id_maquina)
        except SQLAlchemyError as e:
            print(f"Error al buscar máquina por ID: {str(e)}")
            return None
    
    @staticmethod
    def buscar_por_nombre(nombre: str) -> List[MaquinasCerveceria]:
        """
        Busca máquinas por nombre (búsqueda parcial).
        
        Args:
            nombre: Nombre o parte del nombre a buscar
            
        Returns:
            Lista de objetos MaquinasCerveceria que coinciden con la búsqueda
        """
        try:
            return MaquinasCerveceria.query.filter(
                MaquinasCerveceria.nombre.ilike(f'%{nombre}%')
            ).all()
        except SQLAlchemyError as e:
            print(f"Error al buscar máquina por nombre: {str(e)}")
            return []
    
    @staticmethod
    def buscar_por_tipo(tipo: str) -> List[MaquinasCerveceria]:
        """
        Busca máquinas por su tipo.
        
        Args:
            tipo: Tipo de máquina a buscar
            
        Returns:
            Lista de objetos MaquinasCerveceria del tipo especificado
        """
        try:
            return MaquinasCerveceria.query.filter_by(tipo_maquina=tipo).all()
        except SQLAlchemyError as e:
            print(f"Error al buscar máquina por tipo: {str(e)}")
            return []
    
    @staticmethod
    def validar_datos_maquina(datos: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Valida los datos de una máquina antes de crear o actualizar.
        
        Args:
            datos: Diccionario con los datos de la máquina
            
        Returns:
            Tupla (es_valido, mensaje_error)
        """
        # Validar campos requeridos
        campos_requeridos = ['nombre', 'tipo_maquina']
        for campo in campos_requeridos:
            if campo not in datos or not datos[campo]:
                return False, f"El campo {campo} es requerido."
        
        # Validar que el tipo de máquina sea uno de los permitidos
        tipos_permitidos = ['Envasadora', 'Etiquetadora', 'Pasteurizadora', 'Embotelladora', 'Fermentador', 'Otro']
        if datos.get('tipo_maquina') and datos['tipo_maquina'] not in tipos_permitidos:
            return False, f"El tipo de máquina debe ser uno de: {', '.join(tipos_permitidos)}"
        
        return True, ""
    
    @staticmethod
    def crear_maquina(datos: Dict[str, Any]) -> Tuple[Optional[MaquinasCerveceria], str]:
        """
        Crea una nueva máquina en la base de datos.
        
        Args:
            datos: Diccionario con los datos de la máquina
            
        Returns:
            Tupla (objeto_maquina, mensaje)
        """
        # Validar datos
        es_valido, mensaje = ServicioMaquina.validar_datos_maquina(datos)
        if not es_valido:
            return None, mensaje
        
        try:
            # Solo usar los campos que existen en el modelo
            nueva_maquina = MaquinasCerveceria(
                nombre=datos.get('nombre'),
                descripcion=datos.get('descripcion', ''),
                tipo_maquina=datos.get('tipo_maquina'),
                frec_manteni=datos.get('frec_manteni', '')
            )
            
            db.session.add(nueva_maquina)
            db.session.commit()
            return nueva_maquina, "Máquina creada exitosamente."
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return None, f"Error al crear la máquina: {str(e)}"
    
    @staticmethod
    def actualizar_maquina(id_maquina: int, datos: Dict[str, Any]) -> Tuple[Optional[MaquinasCerveceria], str]:
        """
        Actualiza una máquina existente.
        
        Args:
            id_maquina: ID de la máquina a actualizar
            datos: Diccionario con los datos a actualizar
            
        Returns:
            Tupla (objeto_maquina, mensaje)
        """
        # Validar datos
        es_valido, mensaje = ServicioMaquina.validar_datos_maquina(datos)
        if not es_valido:
            return None, mensaje
        
        try:
            maquina = MaquinasCerveceria.query.get(id_maquina)
            if not maquina:
                return None, f"No se encontró máquina con ID {id_maquina}."
            
            # Actualizar solo los campos que existen en el modelo
            if 'nombre' in datos:
                maquina.nombre = datos['nombre']
            if 'descripcion' in datos:
                maquina.descripcion = datos['descripcion']
            if 'tipo_maquina' in datos:
                maquina.tipo_maquina = datos['tipo_maquina']
            if 'frec_manteni' in datos:
                maquina.frec_manteni = datos['frec_manteni']
            
            db.session.commit()
            return maquina, "Máquina actualizada exitosamente."
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return None, f"Error al actualizar la máquina: {str(e)}"
    
    @staticmethod
    def eliminar_maquina(id_maquina: int) -> Tuple[bool, str]:
        """
        Elimina una máquina de la base de datos.
        
        Args:
            id_maquina: ID de la máquina a eliminar
            
        Returns:
            Tupla (exito, mensaje)
        """
        try:
            maquina = MaquinasCerveceria.query.get(id_maquina)
            if not maquina:
                return False, f"No se encontró máquina con ID {id_maquina}."
            
            db.session.delete(maquina)
            db.session.commit()
            return True, "Máquina eliminada exitosamente."
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return False, f"Error al eliminar la máquina: {str(e)}"
