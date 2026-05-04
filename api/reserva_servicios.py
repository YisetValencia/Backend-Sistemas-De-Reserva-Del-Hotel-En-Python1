"""
Router para la gestión de ReservaServicios.
Cada operación recalcula automáticamente el costo_total de la reserva.
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, ConfigDict

from database.config import get_db
from crud.reserva_servicios_crud import ReservaServiciosCRUD

router = APIRouter(prefix="/reserva-servicios", tags=["reserva-servicios"])



class ReservaServicioCreate(BaseModel):
    id_reserva: UUID
    id_servicio: UUID
    cantidad: int


class ReservaServicioUpdate(BaseModel):
    cantidad: int


class ReservaServicioResponse(BaseModel):
    id_reserva: UUID
    id_servicio: UUID
    cantidad: int

    model_config = ConfigDict(from_attributes=True)


@router.post(
    "/",
    response_model=ReservaServicioResponse,
    status_code=status.HTTP_201_CREATED,
)
async def agregar_servicio(
    datos: ReservaServicioCreate,
    db: Session = Depends(get_db),
):
    """Agrega un servicio a una reserva y recalcula el costo_total."""
    try:
        return ReservaServiciosCRUD.agregar_servicio(
            db,
            id_reserva=datos.id_reserva,
            id_servicio=datos.id_servicio,
            cantidad=datos.cantidad,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La reserva o el servicio no existen en la base de datos.",
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {str(e)}",
        )


@router.get(
    "/reserva/{id_reserva}",
    response_model=List[ReservaServicioResponse],
)
async def obtener_servicios_de_reserva(
    id_reserva: UUID,
    db: Session = Depends(get_db),
):
    """Obtiene todos los servicios asociados a una reserva."""
    return ReservaServiciosCRUD.obtener_servicios_reserva(db, id_reserva)


@router.patch(
    "/{id_reserva}/{id_servicio}",
    response_model=ReservaServicioResponse,
)
async def actualizar_cantidad_servicio(
    id_reserva: UUID,
    id_servicio: UUID,
    datos: ReservaServicioUpdate,
    db: Session = Depends(get_db),
):
    """Actualiza la cantidad de un servicio en una reserva y recalcula el costo_total."""
    try:
        return ReservaServiciosCRUD.actualizar_cantidad(
            db,
            id_reserva=id_reserva,
            id_servicio=id_servicio,
            cantidad=datos.cantidad,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/{id_reserva}/{id_servicio}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def eliminar_servicio(
    id_reserva: UUID,
    id_servicio: UUID,
    db: Session = Depends(get_db),
):
    """Elimina un servicio de una reserva y recalcula el costo_total."""
    try:
        ReservaServiciosCRUD.eliminar_servicio(db, id_reserva, id_servicio)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))