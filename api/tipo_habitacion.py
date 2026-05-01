from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ConfigDict


try:
    from .deps import DbSession
except ImportError:
    from deps import DbSession

from crud.tipo_habitacion_crud import TipoHabitacionCRUD
from entities.tipo_habitacion import Tipo_Habitacion

router = APIRouter(prefix="/tipo_habitacion", tags=["tipo_habitacion"])


class TipoHabitacionCreate(BaseModel):
    """
    Esquema de validación para la creación de un nuevo tipo de habitación.

    Atributos:
        nombre_tipo (str): Nombre de la categoría (ej. Suite, Sencilla).
        descripcion (str): Detalle de las características de la habitación.
        id_usuario_crea (UUID): Identificador del usuario que realiza el registro.
    """

    nombre_tipo: str
    descripcion: str
    id_usuario_crea: UUID


class TipoHabitacionRead(BaseModel):
    """
    Esquema de respuesta para la lectura de tipos de habitación.

    Incluye la configuración para permitir la conversión desde modelos de SQLAlchemy.
    """

    model_config = ConfigDict(from_attributes=True)

    id_tipo: UUID
    nombre_tipo: str
    descripcion: str
    id_usuario_crea: UUID
    id_usuario_edita: Optional[UUID] = None


class TipoHabitacionUpdate(BaseModel):
    """
    Modelo de datos para la creación de un servicio adicional.

    Atributos:
        nombre_servicio (str): Nombre del servicio adicional.
        precio (float): Precio asociado al servicio.
        descripcion (str): Descripción detallada del servicio.
        id_usuario_crea (UUID): Identificador del usuario que crea el servicio.
    """
    nombre_tipo: Optional[str] = None
    descripcion: Optional[str] = None
    id_usuario_edita: UUID

# --- ENDPOINTS (RUTAS) ---


@router.get("", response_model=List[TipoHabitacionRead])
def listar_tipos_habitacion(db: DbSession) -> List[Tipo_Habitacion]:
    """
    Recupera el listado completo de todos los tipos de habitación registrados.

    Retorna una lista de objetos de tipo habitación con su información básica.
    """
    return TipoHabitacionCRUD.obtener_tipos_habitacion(db)


@router.get("/{id_tipo}", response_model=TipoHabitacionRead)
def obtener_tipo_habitacion(db: DbSession, id_tipo: UUID) -> Tipo_Habitacion:
    """
    Busca y retorna un tipo de habitación específico según su identificador único.

    Args:
        id_tipo (UUID): El identificador único del tipo de habitación a consultar.

    Raises:
        HTTPException: Error 404 si el tipo de habitación no existe en la base de datos.
    """
    try:
        return TipoHabitacionCRUD.obtener_tipo_habitacion(db, id_tipo)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{id_tipo}", response_model=TipoHabitacionRead)
def actualizar_tipo_habitacion(
    db: DbSession, id_tipo: UUID, body: TipoHabitacionUpdate
) -> TipoHabitacionRead:
    """
    Actualiza un tipo de habitación existente.

    Args:
        db (DbSession): Sesión de base de datos.
        id_tipo (UUID): Identificador del tipo a actualizar.
        body (TipoHabitacionUpdate): Datos a actualizar.

    Raises:
        HTTPException: Si el tipo no existe.

    Returns:
        TipoHabitacionRead: Tipo actualizado.
    """

    id_edita = body.id_usuario_edita
    data = body.model_dump(exclude_unset=True, exclude={"id_usuario_edita"})

    tipo = TipoHabitacionCRUD.actualizar_tipo_habitacion(
        db, id_tipo, id_usuario_edita=id_edita, **data
    )

    if not tipo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tipo de habitación no encontrado",
        )

    return tipo

@router.post("", response_model=TipoHabitacionRead, status_code=status.HTTP_201_CREATED)
def crear_tipo_habitacion(
    db: DbSession, body: TipoHabitacionCreate
) -> Tipo_Habitacion:
    """
    Crea un nuevo registro de tipo de habitación en el sistema.

    Este proceso valida que el nombre no esté duplicado y normaliza los datos de entrada.

    Args:
        body (TipoHabitacionCreate): Datos requeridos para la creación del registro.

    Raises:
        HTTPException: Error 400 si hay un conflicto de datos o validación fallida.
    """
    nuevo_tipo = Tipo_Habitacion(
        nombre_tipo=body.nombre_tipo,
        descripcion=body.descripcion,
        id_usuario_crea=body.id_usuario_crea,
    )

    try:
        return TipoHabitacionCRUD.crear_tipo_habitacion(db, nuevo_tipo)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{id_tipo}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_tipo_habitacion(db: DbSession, id_tipo: UUID) -> None:
    """
    Elimina un tipo de habitación existente del sistema.

    Args:
        id_tipo (UUID): Identificador único del registro que se desea eliminar.

    Raises:
        HTTPException: Error 404 si el registro no pudo ser localizado.
    """
    try:
        TipoHabitacionCRUD.eliminar_tipo_habitacion(db, id_tipo)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
