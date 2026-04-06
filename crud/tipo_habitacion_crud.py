from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import UUID
from entities.tipo_habitacion import Tipo_Habitacion


class TipoHabitacionCRUD:
    """
    Módulo CRUD para la entidad Tipo_Habitacion.

    Permite gestionar los tipos de habitación que existen en el hotel
    (sencilla, doble, suite, etc.).

    Funciones principales:
        - crear_tipo_habitacion(db: Session, tipo: Tipo_Habitacion) -> Tipo_Habitacion
        - obtener_tipo_habitacion(db: Session, id_tipo: UUID) -> Tipo_Habitacion
        - obtener_tipos_habitacion(db: Session) -> List[Tipo_Habitacion]
        - eliminar_tipo_habitacion(db: Session, id_tipo: UUID) -> bool

    Notas:
        - Se valida que no se repitan tipos de habitación con el mismo nombre.
    """

    @staticmethod
    def crear_tipo_habitacion(db: Session, tipo: Tipo_Habitacion) -> Tipo_Habitacion:
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
    def obtener_tipo_habitacion(db: Session, id_tipo: UUID):
        tipo = (
            db.query(Tipo_Habitacion).filter(Tipo_Habitacion.id_tipo == id_tipo).first()
        )
        if not tipo:
            raise ValueError("Tipo de habitación no encontrado")
        return tipo

    @staticmethod
    def obtener_tipos_habitacion(db: Session):
        return db.query(Tipo_Habitacion).all()

    @staticmethod
    def eliminar_tipo_habitacion(db: Session, id_tipo: UUID) -> bool:
        tipo = (
            db.query(Tipo_Habitacion).filter(Tipo_Habitacion.id_tipo == id_tipo).first()
        )
        if not tipo:
            raise ValueError("Tipo de habitación no encontrado")
        db.delete(tipo)
        db.commit()
        return True
