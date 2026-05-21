"""
Puntos finales de la API para la gestión de habitaciones de hotel.
"""

from typing import List, Optional, Any
from uuid import UUID
from datetime import datetime
from entities.habitacion import Habitacion
from crud.habitacion_crud import HabitacionCRUD
from database.config import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

router = APIRouter(prefix="/habitaciones", tags=["habitaciones"])


class RespuestaAPI(BaseModel):
    exito: bool
    mensaje: str
    datos: Optional[Any] = None


class HabitacionBase(BaseModel):
    numero: Optional[int] = None
    id_tipo: Optional[UUID] = None
    tipo: Optional[str] = None
    precio: Optional[float] = None
    disponible: bool = True
    id_usuario_crea: Optional[UUID] = None


class HabitacionCreate(HabitacionBase):
    pass


class HabitacionUpdate(BaseModel):
    numero: Optional[int] = None
    id_tipo: Optional[UUID] = None
    tipo: Optional[str] = None
    precio: Optional[float] = None
    disponible: Optional[bool] = None
    id_usuario_edita: Optional[UUID] = None


class HabitacionResponse(HabitacionBase):
    id_habitacion: UUID
    id_tipo: UUID
    tipo: str
    fecha_creacion: datetime
    fecha_edicion: Optional[datetime]

    class Config:
        from_attributes = True


@router.get("/", response_model=List[HabitacionResponse])
async def obtener_habitaciones(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    try:
        habitacion_crud = HabitacionCRUD(db)
        habitaciones = habitacion_crud.obtener_habitaciones(db)
        return habitaciones
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener habitaciones: {str(e)}",
        )


@router.get("/estado", response_model=List[HabitacionResponse])
async def obtener_habitaciones_disponibles(db: Session = Depends(get_db)):
    try:
        habitacion_crud = HabitacionCRUD(db)
        habitaciones = habitacion_crud.obtener_habitaciones_disponibles(db)
        return habitaciones
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/", response_model=HabitacionResponse, status_code=status.HTTP_201_CREATED)
async def crear_habitacion(
    habitacion_data: HabitacionCreate, db: Session = Depends(get_db)
):
    try:
        habitacion_crud = HabitacionCRUD(db)
        habitacion = habitacion_crud.crear_habitacion(
            db=db,
            habitacion=Habitacion(
                numero=habitacion_data.numero,
                id_tipo=habitacion_data.id_tipo,
                tipo=habitacion_data.tipo,        # ← agregado
                precio=habitacion_data.precio,
                disponible=habitacion_data.disponible,
                id_usuario_crea=habitacion_data.id_usuario_crea,
            ),
        )
        return habitacion
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear habitación: {str(e)}",
        )


@router.put("/{id_habitacion}", response_model=HabitacionResponse)
async def actualizar_habitacion(
    id_habitacion: UUID,
    habitacion_data: HabitacionUpdate,
    db: Session = Depends(get_db),
):
    try:
        habitacion_crud = HabitacionCRUD(db)
        habitacion_existente = habitacion_crud.obtener_habitacion(db, id_habitacion)
        if not habitacion_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Habitación no encontrada"
            )
        campos_actualizacion = habitacion_data.model_dump(exclude_unset=True)
        if not campos_actualizacion:
            return habitacion_existente
        habitacion_actualizada = habitacion_crud.actualizar_habitacion(
            db, id_habitacion, **campos_actualizacion
        )
        return habitacion_actualizada
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar habitación: {str(e)}",
        )


@router.delete("/{id_habitacion}", response_model=RespuestaAPI)
async def eliminar_habitacion(id_habitacion: UUID, db: Session = Depends(get_db)):
    try:
        habitacion_crud = HabitacionCRUD(db)
        habitacion_existente = habitacion_crud.obtener_habitacion(db, id_habitacion)
        if not habitacion_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Habitación no encontrada"
            )
        eliminado = habitacion_crud.eliminar_habitacion(db, id_habitacion)
        if eliminado:
            return RespuestaAPI(mensaje="Habitación eliminada exitosamente", exito=True)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar habitación",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar habitación: {str(e)}",
        )


@router.patch("/{id_habitacion}/cambiar-disponible", response_model=HabitacionResponse)
async def cambiar_estado_habitacion(id_habitacion: UUID, db: Session = Depends(get_db)):
    try:
        habitacion_crud = HabitacionCRUD(db)
        habitacion = habitacion_crud.cambiar_estado_habitacion(db, id_habitacion)
        if not habitacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Habitación no encontrada"
            )
        return habitacion
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cambiar estado de habitación: {str(e)}",
        )


@router.get("/tipo/{tipo}", response_model=List[HabitacionResponse])
async def obtener_habitaciones_por_tipo(tipo: str, db: Session = Depends(get_db)):
    try:
        habitacion_crud = HabitacionCRUD(db)
        habitaciones = habitacion_crud.obtener_habitaciones_por_tipo(db, tipo)
        return habitaciones
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener habitaciones por tipo: {str(e)}",
        )


@router.get("/numero/{numero}", response_model=HabitacionResponse)
async def obtener_habitacion_por_numero(numero: int, db: Session = Depends(get_db)):
    try:
        habitacion_crud = HabitacionCRUD(db)
        habitaciones = habitacion_crud.obtener_habitacion_por_numero(db, numero)
        return habitaciones
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener habitaciones por número: {str(e)}",
        )


@router.get("/{id_habitacion}", response_model=HabitacionResponse)
async def obtener_habitacion(id_habitacion: UUID, db: Session = Depends(get_db)):
    try:
        habitacio_crud = HabitacionCRUD(db)
        habitacion = habitacio_crud.obtener_habitacion(db, id_habitacion)
        if not habitacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Habitación no encontrada"
            )
        return habitacion
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener habitación: {str(e)}",
        )