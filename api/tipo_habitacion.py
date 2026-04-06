from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from entities.tipo_habitacion import Tipo_Habitacion


class TipoHabitacionCRUD:
    """
    Clase proveedora de servicios CRUD para la entidad Tipo_Habitacion.

    Esta clase contiene métodos estáticos para gestionar la persistencia de las
    categorías de habitaciones (ej. Sencilla, Doble, Suite) en la base de datos,
    asegurando la integridad de los datos y evitando duplicidad de nombres.
    """

    @staticmethod
    def crear_tipo_habitacion(db: Session, tipo: Tipo_Habitacion) -> Tipo_Habitacion:
        """
        Registra un nuevo tipo de habitación en la base de datos.

        Realiza validaciones de limpieza de cadenas (strip), verifica que el nombre
        no sea nulo y que no exista otra categoría con el mismo nombre registrado.

        Args:
            db (Session): Conexión activa a la base de datos.
            tipo (Tipo_Habitacion): Instancia de la entidad con los datos a subirse.

        Returns:
            Tipo_Habitacion: El objeto persistido con su ID y fechas generadas.

        Raises:
            ValueError: Si el nombre está vacío o si la categoría ya existe.
            Exception: En caso de errores técnicos durante el commit (realiza rollback).
        """
        if not tipo.nombre_tipo or not tipo.nombre_tipo.strip():
            raise ValueError("El nombre del tipo de habitación no puede estar vacío")

        nombre_limpio = tipo.nombre_tipo.strip()
        existente = (
            db.query(Tipo_Habitacion)
            .filter(Tipo_Habitacion.nombre_tipo == nombre_limpio)
            .first()
        )

        if existente:
            raise ValueError(f"El tipo de habitación '{nombre_limpio}' ya existe")

        try:
            tipo.nombre_tipo = nombre_limpio
            db.add(tipo)
            db.commit()
            db.refresh(tipo)
            return tipo
        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def obtener_tipo_habitacion(db: Session, id_tipo: UUID) -> Tipo_Habitacion:
        """
        Busca una categoría de habitación específica por su identificador único.

        Args:
            db (Session): Conexión activa a la base de datos.
            id_tipo (UUID): Identificador universal del tipo buscado.

        Returns:
            Tipo_Habitacion: El objeto encontrado.

        Raises:
            ValueError: Si no se encuentra ningún registro con ese ID.
        """
        tipo = (
            db.query(Tipo_Habitacion).filter(Tipo_Habitacion.id_tipo == id_tipo).first()
        )
        if not tipo:
            raise ValueError("Tipo de habitación no encontrado")
        return tipo

    @staticmethod
    def obtener_tipos_habitacion(db: Session) -> List[Tipo_Habitacion]:
        """
        Recupera el listado completo de categorías de habitación disponibles.

        Args:
            db (Session): Conexión activa a la base de datos.

        Returns:
            List[Tipo_Habitacion]: Una lista con todas las entidades encontradas.
        """
        return db.query(Tipo_Habitacion).all()

    @staticmethod
    def eliminar_tipo_habitacion(db: Session, id_tipo: UUID) -> bool:
        """
        Elimina un registro de tipo de habitación del sistema.

        Args:
            db (Session): Conexión activa a la base de datos.
            id_tipo (UUID): ID del registro que se desea remover.

        Returns:
            bool: True si la operación fue exitosa.

        Raises:
            ValueError: Si el registro no existe.
            Exception: Si hay un error de integridad (ej. habitaciones vinculadas).
        """
        tipo = (
            db.query(Tipo_Habitacion).filter(Tipo_Habitacion.id_tipo == id_tipo).first()
        )
        if not tipo:
            raise ValueError("Tipo de habitación no encontrado")

        try:
            db.delete(tipo)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise e
