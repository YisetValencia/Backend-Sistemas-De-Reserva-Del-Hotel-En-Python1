"""
Módulo CRUD para la gestión de la tabla asociativa ReservaServicios.

Este módulo provee la lógica de persistencia para vincular servicios a reservas,
permitiendo la creación, consulta y eliminación de estas relaciones en la base de datos.
"""

from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from entities.reserva_servicios import ReservaServicios


class ReservaServiciosCRUD:
    """
    Clase encargada de las operaciones de base de datos para ReservaServicios.

    Provee métodos para gestionar la relación entre las reservas y los
    servicios adicionales mediante SQLAlchemy.

    Attributes:
        db (Session): Sesión activa de SQLAlchemy para realizar transacciones.
    """

    def __init__(self, db: Session):
        """
        Inicializa el CRUD con una sesión de base de datos.

        Args:
            db (Session): Instancia de la sesión de base de datos.
        """
        self.db = db

    def crear_reserva_servicio(
        self, reserva_servicio: ReservaServicios
    ) -> ReservaServicios:
        """
        Registra una nueva relación entre una reserva y un servicio.

        Args:
            reserva_servicio (ReservaServicios): Instancia de la entidad a persistir.

        Returns:
            ReservaServicios: La instancia persistida y refrescada con los datos de la DB.
        """
        self.db.add(reserva_servicio)
        self.db.commit()
        self.db.refresh(reserva_servicio)
        return reserva_servicio

    def obtener_servicios_por_reserva(self, id_reserva: UUID) -> List[ReservaServicios]:
        """
        Consulta todos los servicios asociados a una reserva específica.

        Args:
            id_reserva (UUID): Identificador único de la reserva.

        Returns:
            List[ReservaServicios]: Lista de objetos que vinculan la reserva con servicios.
        """
        return (
            self.db.query(ReservaServicios)
            .filter(ReservaServicios.id_reserva == id_reserva)
            .all()
        )

    def eliminar_relacion(self, id_reserva: UUID, id_servicio: UUID) -> bool:
        """
        Elimina el vínculo específico entre una reserva y un servicio.

        Busca la entrada que coincida con ambos identificadores. Si existe,
        procede con la eliminación física del registro.

        Args:
            id_reserva (UUID): ID de la reserva involucrada.
            id_servicio (UUID): ID del servicio a desvincular.

        Returns:
            bool: True si la relación fue eliminada, False si no se encontró el registro.
        """
        rs = (
            self.db.query(ReservaServicios)
            .filter(
                ReservaServicios.id_reserva == id_reserva,
                ReservaServicios.id_servicio == id_servicio,
            )
            .first()
        )

        if not rs:
            return False

        self.db.delete(rs)
        self.db.commit()
        return True
