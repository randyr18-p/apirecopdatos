from pydantic import BaseModel
from typing import  Optional
from datetime import date, datetime

# Esquema para el cliente

# Esquema para el Cliente
class ClienteBase(BaseModel):
    nombre: str
    telefono: bytes  # Es VARBINARY, representado como bytes en Python
    correo_electronico: bytes
    fecha_nacimiento: Optional[date] = None
    activo: Optional[bool] = True

    class Config:
        orm_mode = True


class ClienteCreate(ClienteBase):
    pass


class ClienteResponse(ClienteBase):
    id: int
    fecha_registro: datetime


# Esquema para Consentimiento
class ConsentimientoBase(BaseModel):
    acepta_terminos: bool

    class Config:
        orm_mode = True


class ConsentimientoCreate(ConsentimientoBase):
    cliente_id: int


class ConsentimientoResponse(ConsentimientoBase):
    id: int
    fecha_consentimiento: datetime
    cliente_id: int


# Esquema para Auditoría
class AuditoriaBase(BaseModel):
    accion: str

    class Config:
        orm_mode = True


class AuditoriaCreate(AuditoriaBase):
    cliente_id: int


class AuditoriaResponse(AuditoriaBase):
    id: int
    fecha: datetime
    cliente_id: int