from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import UUID
from entities.reserva_servicios import ReservaServicios
from crud.reserva_crud import ReservaCRUD


class ReservaServiciosCRUD:
    """
    CRUD para ReservaServicios.

    Cada operación (crear, actualizar, eliminar) recalcula automáticamente
    el costo_total de la reserva padre.
    """

    @staticmethod
    def agregar_servicio(
        db: Session,
        id_reserva: UUID,
        id_servicio: UUID,
        cantidad: int,
    ) -> ReservaServicios:
        if cantidad < 1:
            raise ValueError("La cantidad debe ser mayor a 0")

        # Si ya existe el servicio en la reserva, sumar cantidad
        existente = db.query(ReservaServicios).filter_by(
            id_reserva=id_reserva,
            id_servicio=id_servicio,
        ).first()

        if existente:
            existente.cantidad += cantidad
            db.commit()
            db.refresh(existente)
            rs = existente
        else:
            rs = ReservaServicios(
                id_reserva=id_reserva,
                id_servicio=id_servicio,
                cantidad=cantidad,
            )
            db.add(rs)
            db.commit()
            db.refresh(rs)

       
        ReservaCRUD.recalcular_costo_total(db, id_reserva)
        return rs

    @staticmethod
    def obtener_servicios_reserva(db: Session, id_reserva: UUID):
        return db.query(ReservaServicios).filter(
            ReservaServicios.id_reserva == id_reserva
        ).all()

    @staticmethod
    def obtener_servicio(
        db: Session, id_reserva: UUID, id_servicio: UUID
    ) -> ReservaServicios:
        rs = db.query(ReservaServicios).filter_by(
            id_reserva=id_reserva,
            id_servicio=id_servicio,
        ).first()
        if not rs:
            raise ValueError("Servicio no encontrado en la reserva")
        return rs

    @staticmethod
    def actualizar_cantidad(
        db: Session,
        id_reserva: UUID,
        id_servicio: UUID,
        cantidad: int,
    ) -> ReservaServicios:
        if cantidad < 1:
            raise ValueError("La cantidad debe ser mayor a 0")

        rs = db.query(ReservaServicios).filter_by(
            id_reserva=id_reserva,
            id_servicio=id_servicio,
        ).first()
        if not rs:
            raise ValueError("Servicio no encontrado en la reserva")

        rs.cantidad = cantidad
        db.commit()
        db.refresh(rs)

       
        ReservaCRUD.recalcular_costo_total(db, id_reserva)
        return rs

    @staticmethod
    def eliminar_servicio(
        db: Session, id_reserva: UUID, id_servicio: UUID
    ) -> None:
        rs = db.query(ReservaServicios).filter_by(
            id_reserva=id_reserva,
            id_servicio=id_servicio,
        ).first()
        if not rs:
            raise ValueError("Servicio no encontrado en la reserva")

        db.delete(rs)
        db.commit()

       
        ReservaCRUD.recalcular_costo_total(db, id_reserva)