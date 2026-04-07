from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import UUID
from entities.servicios_adicionales import Servicios_Adicionales
from datetime import date
from typing import List, Optional


class ServiciosAdicionalesCRUD:
    """
    Clase que implementa las operaciones CRUD para la entidad
    Servicios_Adicionales dentro del sistema del hotel.

    Permite registrar, consultar, actualizar y eliminar los
    servicios extra disponibles para los huéspedes, asegurando
    validaciones básicas como nombre válido, precio positivo
    y que no existan duplicados.
    """

    def __init__(self, db):
        self.db = db

    @staticmethod
    def crear_servicio(
        db: Session,
        nombre_servicio: str,
        precio: float,
        descripcion: str,
        id_usuario_crea: UUID,
    ):

        if not nombre_servicio or not nombre_servicio.strip():
            raise ValueError("El nombre del servicio no puede estar vacío")

        if precio <= 0:
            raise ValueError("El precio debe ser mayor a 0")

        existente = (
            db.query(Servicios_Adicionales)
            .filter(Servicios_Adicionales.nombre_servicio == nombre_servicio)
            .first()
        )

        if existente:
            raise ValueError("El servicio ya existe")

        servicio = Servicios_Adicionales(
            nombre_servicio=nombre_servicio.strip(),
            precio=precio,
            descripcion=descripcion,
            id_usuario_crea=id_usuario_crea,
        )

        db.add(servicio)
        db.commit()
        db.refresh(servicio)

        return servicio

    @staticmethod
    def obtener_servicio(
        db: Session, id_servicio: UUID
    ) -> Optional[Servicios_Adicionales]:
        """
        Obtiene un servicio adicional específico a partir
        de su identificador único.

        Si no se encuentra el registro, se lanza un error.
        """
        return (
            db.query(Servicios_Adicionales)
            .filter(Servicios_Adicionales.id_servicio == id_servicio)
            .first()
        )

    @staticmethod
    def listar(
        db: Session, skip: int = 0, limit: int = 100
    ) -> List[Servicios_Adicionales]:
        return db.query(Servicios_Adicionales).offset(skip).limit(limit).all()

    @staticmethod
    def actualizar_servicio(
        db, id_servicio: UUID, id_usuario_edita: UUID, **kwargs: object
    ) -> Optional[Servicios_Adicionales]:
        servicio = ServiciosAdicionalesCRUD.obtener_servicio(db, id_servicio)
        if not servicio:
            return None
        for key, value in kwargs.items():
            if hasattr(servicio, str(key)) and str(key) != "id_servicio":
                setattr(servicio, str(key), value)
        servicio.id_usuario_edita = id_usuario_edita

        db.commit()
        db.refresh(servicio)
        return servicio

    @staticmethod
    def eliminar_servicio(db: Session, id_servicio: UUID) -> bool:
        """
        Elimina un servicio adicional de la base de datos
        usando su identificador.

        Devuelve True si la operación se realiza correctamente
        o genera un error si el servicio no existe.
        """
        servicio = (
        db.query(Servicios_Adicionales)
        .filter(Servicios_Adicionales.id_servicio == id_servicio)
        .first()
    )

        if not servicio:
            return False

        db.delete(servicio)
        db.commit()

        return True
