"""Esquemas Pydantic para las peticiones y respuestas de la API."""

from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field

Rol = Literal["administrador", "entrenador", "usuario"]


# --------------------------- Usuarios (RF01) --------------------------- #
class UsuarioCrear(BaseModel):
    nombre: str
    apellido: str
    correo: EmailStr
    contrasena: str = Field(min_length=4)
    rol: Rol


class UsuarioActualizar(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    correo: Optional[EmailStr] = None
    rol: Optional[Rol] = None


class UsuarioOut(BaseModel):
    id_usuario: int
    nombre: str
    apellido: str
    correo: str
    rol: str


# ------------------------- Evaluaciones (RF02) ------------------------- #
class EvaluacionCrear(BaseModel):
    peso: float = Field(gt=0)
    altura: float = Field(gt=0)
    grasa_corporal: Optional[float] = Field(default=None, ge=0)
    fecha: Optional[str] = None


class EvaluacionOut(BaseModel):
    id_evaluacion: int
    fecha: str
    peso: float
    altura: float
    imc: float
    grasa_corporal: Optional[float]
    clasificacion: str
    id_usuario: int


# --------------------------- Rutinas (RF03) ---------------------------- #
class RutinaCrear(BaseModel):
    nombre: str
    descripcion: Optional[str] = ""
    duracion: Optional[int] = Field(default=0, ge=0)


class RutinaOut(BaseModel):
    id_rutina: int
    nombre: str
    descripcion: Optional[str]
    duracion: Optional[int]


class AsignacionCrear(BaseModel):
    id_usuario: int
    id_rutina: int


# ------------------------- Seguimiento (RF04) -------------------------- #
class SeguimientoCrear(BaseModel):
    peso_actual: float = Field(gt=0)
    observacion: Optional[str] = ""
    fecha: Optional[str] = None


class SeguimientoOut(BaseModel):
    id_seguimiento: int
    fecha: str
    observacion: Optional[str]
    peso_actual: float
    id_usuario: int


# --------------------------- Autenticación ----------------------------- #
class LoginIn(BaseModel):
    correo: EmailStr
    contrasena: str


class RecuperarIn(BaseModel):
    correo: EmailStr
    nueva_contrasena: str = Field(min_length=4)
