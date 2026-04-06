"""
Módulo de API Router para la gestión integral de Reservas.

Este módulo centraliza las operaciones CRUD para las reservas del sistema,
incluyendo la creación, consulta filtrada, actualización de costos y
eliminación lógica o física de registros.
"""

from typing import List, Optional, Any
from uuid import UUID
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from entities.reserva import Reserva
from crud.reserva_crud import ReservaCRUD
from database.config import get_db

router = APIRouter(prefix="/reserva", tags=["reserva"])


class RespuestaAPI(BaseModel):
    """
    Esquema genérico para respuestas de confirmación de operaciones.
    """

    exito: bool
    mensaje: str
    datos: Optional[Any] = None


class ReservaBase(BaseModel):
    """
    Campos base compartidos para una reserva.
    """

    id_habitacion: UUID
    fecha_entrada: date
    fecha_salida: date
    numero_de_personas: int
    estado_reserva: Optional[str] = "En proceso"


class ReservaCreate(ReservaBase):
    """
    Esquema requerido para la creación de una nueva reserva.
    Incluye los identificadores de usuario necesarios para la auditoría.
    """

    id_usuario: UUID
    id_usuario_crea: UUID


class ReservaUpdate(BaseModel):
    """
    Esquema para la actualización parcial de una reserva.
    Todos los campos son opcionales para permitir actualizaciones PATCH.
    """

    id_habitacion: Optional[UUID] = None
    fecha_entrada: Optional[date] = None
    fecha_salida: Optional[date] = None
    numero_de_personas: Optional[int] = None
    estado_reserva: Optional[str] = None
    id_usuario_edita: Optional[UUID] = None


class ReservaResponse(ReservaBase):
    """
    Esquema de respuesta detallado que incluye campos calculados y de auditoría.

    Attributes:
        noches (int): Calculado automáticamente basado en fechas.
        costo_total (float): Costo financiero total de la estancia.
        fecha_creacion (datetime): Timestamp de inserción.
    """

    id_reserva: UUID
    id_usuario: UUID
    noches: Optional[int]
    costo_total: Optional[float]
    fecha_creacion: datetime
    fecha_edicion: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


@router.get("/", response_model=List[ReservaResponse])
async def obtener_reservas(db: Session = Depends(get_db)):
    """
    Recupera todas las reservas registradas en el sistema.

    Args:
        db (Session): Sesión de base de datos.

    Returns:
        List[ReservaResponse]: Lista con todas las reservas.
    """
    return ReservaCRUD.obtener_reservas(db)


@router.get("/activas", response_model=List[ReservaResponse])
async def obtener_reservas_activas(db: Session = Depends(get_db)):
    """
    Filtra y retorna únicamente las reservas cuyo estado es 'Activa'.

    Args:
        db (Session): Sesión de base de datos.

    Returns:
        List[ReservaResponse]: Lista de reservas activas.
    """
    return ReservaCRUD.obtener_reservas_activas(db)


@router.post("/", response_model=ReservaResponse, status_code=status.HTTP_201_CREATED)
async def crear_reserva(reserva_data: ReservaCreate, db: Session = Depends(get_db)):
    """
    Registra una nueva reserva en el sistema.

    Realiza el cálculo automático de noches y validación de fechas
    a través de la capa CRUD.

    Args:
        reserva_data (ReservaCreate): Datos de la nueva reserva.
        db (Session): Sesión de base de datos.

    Raises:
        HTTPException: 400 si hay errores de validación (ej. fechas inválidas).

    Returns:
        ReservaResponse: La reserva creada con sus campos calculados.
    """
    try:
        nueva_reserva = Reserva(**reserva_data.model_dump())
        return ReservaCRUD.crear_reserva(db, nueva_reserva)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{id_reserva}/costo-extra", response_model=ReservaResponse)
async def actualizar_costo_reserva(
    id_reserva: UUID, monto_extra: float, db: Session = Depends(get_db)
):
    """
    Incrementa el costo total de una reserva existente.

    Args:
        id_reserva (UUID): Identificador de la reserva.
        monto_extra (float): Valor a sumar al costo_total actual.
        db (Session): Sesión de base de datos.

    Raises:
        HTTPException: 404 si la reserva no existe.

    Returns:
        ReservaResponse: Reserva con el costo actualizado.
    """
    try:
        return ReservaCRUD.actualizar_costo_total(db, id_reserva, monto_extra)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/{id_reserva}", response_model=ReservaResponse)
async def actualizar_reserva(
    id_reserva: UUID, reserva_edit: ReservaUpdate, db: Session = Depends(get_db)
):
    """
    Actualiza parcialmente los datos de una reserva.

    Solo se modificarán los campos incluidos en el cuerpo de la petición.

    Args:
        id_reserva (UUID): Identificador de la reserva a modificar.
        reserva_edit (ReservaUpdate): Campos a actualizar.
        db (Session): Sesión de base de datos.

    Raises:
        HTTPException: 400 si los nuevos datos violan reglas de negocio.

    Returns:
        ReservaResponse: La reserva tras la modificación.
    """
    try:
        update_data = reserva_edit.model_dump(exclude_unset=True)
        return ReservaCRUD.actualizar_reserva(db, id_reserva, **update_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{id_reserva}", response_model=RespuestaAPI)
async def eliminar_reserva(id_reserva: UUID, db: Session = Depends(get_db)):
    """
    Elimina una reserva del sistema.

    Dependiendo de la implementación del CRUD, esto puede realizar una
    eliminación física o lógica, incluyendo la limpieza de servicios vinculados.

    Args:
        id_reserva (UUID): Identificador de la reserva a eliminar.
        db (Session): Sesión de base de datos.

    Raises:
        HTTPException: 404 si la reserva no existe.

    Returns:
        RespuestaAPI: Objeto indicando el éxito de la operación.
    """
    try:
        ReservaCRUD.eliminar_reserva(db, id_reserva)
        return RespuestaAPI(exito=True, mensaje="Reserva eliminada con éxito")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
