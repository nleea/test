"""Entidades del dominio (modelo de datos, features.md sección 10)."""

from dataclasses import dataclass
from typing import Optional

ROLES = ("administrador", "entrenador", "usuario")


@dataclass
class Usuario:
    nombre: str
    apellido: str
    correo: str
    rol: str
    id_usuario: Optional[int] = None

    @property
    def nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellido}"


@dataclass
class EvaluacionFisica:
    fecha: str
    peso: float
    altura: float
    imc: float
    id_usuario: int
    grasa_corporal: Optional[float] = None
    id_evaluacion: Optional[int] = None


@dataclass
class Rutina:
    nombre: str
    descripcion: Optional[str] = None
    duracion: Optional[int] = None
    id_rutina: Optional[int] = None


@dataclass
class Seguimiento:
    fecha: str
    peso_actual: float
    id_usuario: int
    observacion: Optional[str] = None
    id_seguimiento: Optional[int] = None
