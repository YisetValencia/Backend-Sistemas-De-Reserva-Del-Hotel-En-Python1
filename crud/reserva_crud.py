from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import UUID
from entities.reserva import Reserva
from entities.reserva_servicios import ReservaServicios
from entities.habitacion import Habitacion
from entities.servicios_adicionales import Servicios_Adicionales


class ReservaCRUD:
    """
    CRUD para Reserva con cálculo automático de costo_total.

    costo_total = (noches × precio_habitación) + Σ(precio_servicio × cantidad)
    """

    
    @staticmethod
    def _calcular_costo(db: Session, reserva: Reserva) -> float:
        """
        Calcula el costo total de una reserva:
          - noches × precio de la habitación
          + suma de (precio_servicio × cantidad) por cada ReservaServicios
        """
        habitacion = db.query(Habitacion).filter(
            Habitacion.id_habitacion == reserva.id_habitacion
        ).first()

        precio_hab = habitacion.precio if habitacion else 0.0
        noches = reserva.noches or 0
        costo_hab = noches * precio_hab

        servicios = db.query(ReservaServicios).filter(
            ReservaServicios.id_reserva == reserva.id_reserva
        ).all()

        costo_servicios = 0.0
        for rs in servicios:
            servicio = db.query(Servicios_Adicionales).filter(
                Servicios_Adicionales.id_servicio == rs.id_servicio
            ).first()
            if servicio:
                costo_servicios += servicio.precio * rs.cantidad

        return round(costo_hab + costo_servicios, 2)

   
    @staticmethod
    def crear_reserva(db: Session, reserva: Reserva) -> Reserva:
        if not reserva.id_usuario or not reserva.id_habitacion:
            raise ValueError(
                "La reserva debe estar asociada a un cliente y una habitación"
            )

        if reserva.fecha_entrada >= reserva.fecha_salida:
            raise ValueError("La fecha de entrada debe ser anterior a la de salida")

       
        delta = reserva.fecha_salida - reserva.fecha_entrada
        reserva.noches = delta.days

        
        if not reserva.estado_reserva:
            reserva.estado_reserva = "Activa"

       
        db.add(reserva)
        db.flush()

       
        habitacion = db.query(Habitacion).filter(
            Habitacion.id_habitacion == reserva.id_habitacion
        ).first()
        precio_hab = habitacion.precio if habitacion else 0.0
        reserva.costo_total = round(reserva.noches * precio_hab, 2)

        db.commit()
        db.refresh(reserva)
        return reserva

    @staticmethod
    def obtener_reserva(db: Session, id_reserva: UUID) -> Reserva:
        reserva = db.query(Reserva).filter(Reserva.id_reserva == id_reserva).first()
        if not reserva:
            raise ValueError("Reserva no encontrada")
        return reserva

    @staticmethod
    def obtener_reservas(db: Session):
        return db.query(Reserva).all()

    @staticmethod
    def actualizar_reserva(db: Session, id_reserva: UUID, **kwargs) -> Reserva:
        reserva = db.query(Reserva).filter(Reserva.id_reserva == id_reserva).first()
        if not reserva:
            raise ValueError("Reserva no encontrada")

        for key, value in kwargs.items():
            if hasattr(reserva, key):
                setattr(reserva, key, value)

        if (
            reserva.fecha_entrada
            and reserva.fecha_salida
            and reserva.fecha_entrada >= reserva.fecha_salida
        ):
            raise ValueError("La fecha de entrada debe ser anterior a la de salida")

        if reserva.fecha_entrada and reserva.fecha_salida:
            delta = reserva.fecha_salida - reserva.fecha_entrada
            reserva.noches = delta.days

       
        reserva.costo_total = ReservaCRUD._calcular_costo(db, reserva)

        db.commit()
        db.refresh(reserva)
        return reserva

    @staticmethod
    def eliminar_reserva(db: Session, id_reserva: UUID) -> None:
        reserva = db.query(Reserva).filter(Reserva.id_reserva == id_reserva).first()
        if not reserva:
            raise ValueError("La reserva no existe.")

        db.query(ReservaServicios).filter(
            ReservaServicios.id_reserva == id_reserva
        ).delete()

        db.delete(reserva)
        db.commit()

    @staticmethod
    def obtener_reservas_activas(db: Session):
        return db.query(Reserva).filter(Reserva.estado_reserva == "Activa").all()

    @staticmethod
    def recalcular_costo_total(db: Session, id_reserva) -> Reserva:
        """
        Recalcula y persiste el costo_total de una reserva.
        Llamar siempre que se agregue, edite o elimine un ReservaServicios.
        """
        reserva = db.query(Reserva).filter_by(id_reserva=id_reserva).first()
        if not reserva:
            raise ValueError("Reserva no encontrada")

        reserva.costo_total = ReservaCRUD._calcular_costo(db, reserva)
        db.commit()
        db.refresh(reserva)
        return reserva