from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ConfigDict, EmailStr

from .deps import DbSession
from crud.servicios_adicioneles_crud import ServiciosAdicionalesCRUD


router = APIRouter(prefix="/servicios_adicionales", tags=["servicios_adicionales"])


class ServiciosAdicionalesCreate(BaseModel):
    """
    Modelo de datos para la creación de un servicio adicional.

    Atributos:
        nombre_servicio (str): Nombre del servicio adicional.
        precio (float): Precio asociado al servicio.
        descripcion (str): Descripción detallada del servicio.
        id_usuario_crea (UUID): Identificador del usuario que crea el servicio.
    """

    nombre_servicio: str
    precio: float
    descripcion: str
    id_usuario_crea: UUID


class ServiciosAdicionalesUpdate(BaseModel):
    """
    Modelo de datos para la creación de un servicio adicional.

    Atributos:
        nombre_servicio (str): Nombre del servicio adicional.
        precio (float): Precio asociado al servicio.
        descripcion (str): Descripción detallada del servicio.
        id_usuario_crea (UUID): Identificador del usuario que crea el servicio.
    """

    nombre_servicio: Optional[str] = None
    precio: Optional[float] = None
    descripcion: Optional[str] = None
    id_usuario_edita: UUID


class ServiciosAdicionalesRead(BaseModel):
    """
    Modelo de respuesta para representar un servicio adicional.

    Este modelo se utiliza para retornar la información del servicio desde la API.

    Atributos:
        id_servicio (UUID): Identificador único del servicio.
        nombre_servicio (str): Nombre del servicio.
        precio (float): Precio del servicio.
        descripcion (str): Descripción del servicio.
        id_usuario_creacion (UUID): Usuario que creó el servicio.
        id_usuario_edita (Optional[UUID]): Usuario que realizó la última edición (si aplica).
    """

    model_config = ConfigDict(from_attributes=True)
    id_servicio: UUID
    nombre_servicio: str
    precio: float
    descripcion: str
    id_usuario_crea: UUID
    id_usuario_edita: Optional[UUID] = None


@router.get("", response_model=List[ServiciosAdicionalesRead])
def listar_servicios(
    db: DbSession, skip: int = 0, limit: int = 100
) -> List[ServiciosAdicionalesRead]:
    """
    Obtiene una lista de servicios adicionales con paginación.

    Args:
        db (DbSession): Sesión de base de datos.
        skip (int): Número de registros a omitir (offset).
        limit (int): Número máximo de registros a retornar.

    Returns:
        List[ServiciosAdicionalesRead]: Lista de servicios adicionales.
    """

    return ServiciosAdicionalesCRUD.listar(db, skip=skip, limit=limit)


@router.get("/{id_servicio}", response_model=ServiciosAdicionalesRead)
def obtener_servicio_adicional(
    db: DbSession, id_usuario: UUID
) -> ServiciosAdicionalesRead:
    """
    Obtiene un servicio adicional por su identificador.

    Args:
        db (DbSession): Sesión de base de datos.
        id_usuario (UUID): Identificador del servicio

    Raises:
        HTTPException: Si el servicio no existe.

    Returns:
        ServiciosAdicionalesRead: Información del servicio encontrado.
    """

    servicio = ServiciosAdicionalesCRUD.obtener_servicio(db, id_usuario)
    if not servicio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )
    return servicio


@router.post(
    "", response_model=ServiciosAdicionalesRead, status_code=status.HTTP_201_CREATED
)
def crear_servicio_adicional(
    db: DbSession, body: ServiciosAdicionalesCreate
) -> ServiciosAdicionalesRead:
    """
    Crea un nuevo servicio adicional.

    Args:
        db (DbSession): Sesión de base de datos.
        body (ServiciosAdicionalesCreate): Datos necesarios para crear el servicio.

    Returns:
        ServiciosAdicionalesRead: Servicio creado.
    """

    servicio = ServiciosAdicionalesCRUD.crear_servicio(
        db,
        nombre_servicio=body.nombre_servicio,
        precio=body.precio,
        descripcion=body.descripcion,
        id_usuario_crea=body.id_usuario_crea,
    )
    return servicio


@router.put("/{id_servicio}", response_model=ServiciosAdicionalesRead)
def actualizar_servicio_adicional(
    db: DbSession, id_servicio: UUID, body: ServiciosAdicionalesUpdate
) -> ServiciosAdicionalesRead:
    """
    Actualiza un servicio adicional existente.

    Args:
        db (DbSession): Sesión de base de datos.
        id_servicio (UUID): Identificador del servicio a actualizar.
        body (ServiciosAdicionalesUpdate): Datos a actualizar.

    Raises:
        HTTPException: Si el servicio no existe.

    Returns:
        ServiciosAdicionalesRead: Servicio actualizado.
    """

    id_edita = body.id_usuario_edita
    data = body.model_dump(exclude_unset=True, exclude={"id_usuario_edita"})
    servicio = ServiciosAdicionalesCRUD.actualizar_servicio(
        db, id_servicio, id_usuario_edita=id_edita, **data
    )
    if not servicio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Servicio no encontrado"
        )
    return servicio


@router.delete("/{id_servicio}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_servicio_adicional(db: DbSession, id_servicio: UUID) -> None:
    """
    Elimina un servicio adicional por su identificador.

    Args:
        db (DbSession): Sesión de base de datos.
        id_servicio (UUID): Identificador del servicio a eliminar.

    Raises:
        HTTPException: Si el servicio no existe.
    """

    if not ServiciosAdicionalesCRUD.eliminar_servicio(db, id_servicio):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Servicio no encontrado"
        )