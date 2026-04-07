"""
Módulo de API Router para la gestión de relaciones entre Reservas y Servicios.

Este módulo define los endpoints de FastAPI para realizar operaciones CRUD sobre la
entidad asociativa 'ReservaServicios', permitiendo vincular servicios específicos
a reservas existentes mediante sus respectivos identificadores únicos (UUID).
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database.config import get_db
from entities.reserva_servicios import ReservaServicios
from crud.reserva_servicios_crud import ReservaServiciosCRUD
from pydantic import BaseModel

router = APIRouter(prefix="/reserva-servicios", tags=["reserva-servicios"])


class ReservaServicioBase(BaseModel):
    """
    Esquema Pydantic para la transferencia de datos de Reserva-Servicio.

    Attributes:
        id_reserva (UUID): Identificador único de la reserva.
        id_servicio (UUID): Identificador único del servicio.
    """

    id_reserva: UUID
    id_servicio: UUID


class ReservaServicioResponse(ReservaServicioBase):
    """
    Esquema de respuesta para las operaciones de Reserva-Servicio.
    Habilita la compatibilidad con modelos de SQLAlchemy (ORM).
    """

    class Config:
        from_attributes = True


def get_crud(db: Session = Depends(get_db)):
    """
    Factory function para obtener una instancia del CRUD de ReservaServicios.

    Args:
        db (Session): Sesión de base de datos inyectada.

    Returns:
        ReservaServiciosCRUD: Instancia con la lógica de persistencia.
    """
    return ReservaServiciosCRUD(db)


@router.post(
    "/", response_model=ReservaServicioResponse, status_code=status.HTTP_201_CREATED
)
async def asignar_servicio_a_reserva(
    datos: ReservaServicioBase,
    db: Session = Depends(get_db),
    crud: ReservaServiciosCRUD = Depends(get_crud),
):
    """
    Crea una nueva vinculación entre una reserva y un servicio.

    Args:
        datos (ReservaServicioBase): Objeto con id_reserva e id_servicio.
        db (Session): Dependencia de la sesión de base de datos.
        crud (ReservaServiciosCRUD): Dependencia de la lógica de negocio.

    Raises:
        HTTPException: 400 si hay un error de integridad (FK inexistente).
        HTTPException: 500 para errores internos no controlados.

    Returns:
        ReservaServicios: El registro creado en la base de datos.
    """
    try:
        nueva_relacion = ReservaServicios(**datos.model_dump())
        return crud.crear_reserva_servicio(nueva_relacion)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de integridad: La reserva o el servicio no existen en la base de datos.",
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {str(e)}",
        )


@router.get("/reserva/{id_reserva}", response_model=List[ReservaServicioResponse])
async def obtener_servicios_de_reserva(
    id_reserva: UUID, crud: ReservaServiciosCRUD = Depends(get_crud)
):
    """
    Obtiene la lista de todos los servicios asociados a una reserva específica.

    Args:
        id_reserva (UUID): El ID de la reserva a consultar.
        crud (ReservaServiciosCRUD): Instancia de la capa CRUD.

    Returns:
        List[ReservaServicioResponse]: Lista de objetos vinculados.
    """
    return crud.obtener_servicios_por_reserva(id_reserva)


@router.delete("/{id_reserva}/{id_servicio}")
async def desvincular_servicio(
    id_reserva: UUID, id_servicio: UUID, crud: ReservaServiciosCRUD = Depends(get_crud)
):
    """
    Elimina la relación existente entre una reserva y un servicio.

    Args:
        id_reserva (UUID): ID de la reserva.
        id_servicio (UUID): ID del servicio.
        crud (ReservaServiciosCRUD): Instancia de la capa CRUD.

    Raises:
        HTTPException: 404 si la relación no existe en la base de datos.

    Returns:
        dict: Mensaje de confirmación de éxito.
    """
    if not crud.eliminar_relacion(id_reserva, id_servicio):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La relación entre esta reserva y este servicio no existe",
        )
    return {"exito": True, "mensaje": "Servicio desvinculado con éxito"}
