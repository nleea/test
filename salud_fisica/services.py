"""Lógica de negocio: autenticación, evaluaciones (IMC), rutinas,
seguimiento y reportes. Orquesta los repositorios y aplica reglas.
"""

import sqlite3
from datetime import date
from typing import List, Optional

from .models import EvaluacionFisica, Rutina, Seguimiento, Usuario
from .repositories import (
    EvaluacionRepository,
    RutinaRepository,
    SeguimientoRepository,
    UsuarioRepository,
)
from .security import hash_password, verify_password


class AuthError(Exception):
    """Error de autenticación o de regla de negocio."""


def calcular_imc(peso: float, altura: float) -> float:
    """IMC = peso(kg) / altura(m)^2, redondeado a 2 decimales."""
    if altura <= 0:
        raise ValueError("La altura debe ser mayor que cero.")
    return round(peso / (altura ** 2), 2)


def clasificar_imc(imc: float) -> str:
    """Clasificación según la OMS."""
    if imc < 18.5:
        return "Bajo peso"
    if imc < 25:
        return "Peso normal"
    if imc < 30:
        return "Sobrepeso"
    return "Obesidad"


class AuthService:
    """Módulo de Autenticación (RF/RNF seguridad)."""

    def __init__(self, conn: sqlite3.Connection):
        self.usuarios = UsuarioRepository(conn)

    def login(self, correo: str, contrasena: str) -> Usuario:
        row = self.usuarios.obtener_por_correo(correo)
        if not row or not verify_password(contrasena, row["contrasena"]):
            raise AuthError("Correo o contraseña incorrectos.")
        return UsuarioRepository._to_model(row)

    def recuperar_contrasena(self, correo: str, nueva: str) -> None:
        """Recuperación simple de contraseña por correo registrado."""
        row = self.usuarios.obtener_por_correo(correo)
        if not row:
            raise AuthError("No existe un usuario con ese correo.")
        self.usuarios.actualizar_contrasena(row["id_usuario"], hash_password(nueva))


class UsuarioService:
    """RF01. Gestión de usuarios."""

    def __init__(self, conn: sqlite3.Connection):
        self.repo = UsuarioRepository(conn)

    def registrar(self, nombre: str, apellido: str, correo: str,
                  contrasena: str, rol: str) -> int:
        if self.repo.obtener_por_correo(correo):
            raise AuthError(f"Ya existe un usuario con el correo {correo}.")
        usuario = Usuario(nombre=nombre, apellido=apellido, correo=correo, rol=rol)
        return self.repo.crear(usuario, hash_password(contrasena))

    def modificar(self, usuario: Usuario) -> None:
        self.repo.modificar(usuario)

    def eliminar(self, id_usuario: int) -> None:
        self.repo.eliminar(id_usuario)

    def obtener(self, id_usuario: int) -> Optional[Usuario]:
        return self.repo.obtener(id_usuario)

    def listar(self) -> List[Usuario]:
        return self.repo.listar()


class EvaluacionService:
    """RF02. Gestión de evaluaciones físicas (calcula el IMC)."""

    def __init__(self, conn: sqlite3.Connection):
        self.repo = EvaluacionRepository(conn)

    def registrar(self, id_usuario: int, peso: float, altura: float,
                  grasa_corporal: Optional[float] = None,
                  fecha: Optional[str] = None) -> EvaluacionFisica:
        imc = calcular_imc(peso, altura)
        evaluacion = EvaluacionFisica(
            fecha=fecha or date.today().isoformat(),
            peso=peso, altura=altura, imc=imc,
            grasa_corporal=grasa_corporal, id_usuario=id_usuario,
        )
        evaluacion.id_evaluacion = self.repo.crear(evaluacion)
        return evaluacion

    def historial(self, id_usuario: int) -> List[EvaluacionFisica]:
        return self.repo.listar_por_usuario(id_usuario)


class RutinaService:
    """RF03. Gestión de rutinas."""

    def __init__(self, conn: sqlite3.Connection):
        self.repo = RutinaRepository(conn)

    def crear(self, nombre: str, descripcion: str = "", duracion: int = 0) -> int:
        return self.repo.crear(Rutina(nombre=nombre, descripcion=descripcion, duracion=duracion))

    def modificar(self, rutina: Rutina) -> None:
        self.repo.modificar(rutina)

    def asignar(self, id_usuario: int, id_rutina: int) -> None:
        self.repo.asignar(id_usuario, id_rutina, date.today().isoformat())

    def listar(self) -> List[Rutina]:
        return self.repo.listar()

    def listar_asignadas(self, id_usuario: int) -> List[Rutina]:
        return self.repo.listar_asignadas(id_usuario)


class SeguimientoService:
    """RF04. Seguimiento del progreso físico."""

    def __init__(self, conn: sqlite3.Connection):
        self.repo = SeguimientoRepository(conn)

    def registrar_avance(self, id_usuario: int, peso_actual: float,
                         observacion: str = "", fecha: Optional[str] = None) -> int:
        seguimiento = Seguimiento(
            fecha=fecha or date.today().isoformat(),
            observacion=observacion, peso_actual=peso_actual, id_usuario=id_usuario,
        )
        return self.repo.crear(seguimiento)

    def historial(self, id_usuario: int) -> List[Seguimiento]:
        return self.repo.listar_por_usuario(id_usuario)


class ReporteService:
    """RF05. Reportes e indicadores de salud física."""

    def __init__(self, conn: sqlite3.Connection):
        self.evaluaciones = EvaluacionRepository(conn)
        self.seguimientos = SeguimientoRepository(conn)

    def reporte_peso(self, id_usuario: int) -> dict:
        evals = self.evaluaciones.listar_por_usuario(id_usuario)
        pesos = [e.peso for e in evals]
        return {
            "registros": len(pesos),
            "peso_inicial": pesos[0] if pesos else None,
            "peso_actual": pesos[-1] if pesos else None,
            "variacion": round(pesos[-1] - pesos[0], 2) if len(pesos) >= 2 else 0.0,
            "peso_minimo": min(pesos) if pesos else None,
            "peso_maximo": max(pesos) if pesos else None,
        }

    def reporte_imc(self, id_usuario: int) -> dict:
        evals = self.evaluaciones.listar_por_usuario(id_usuario)
        if not evals:
            return {"registros": 0, "imc_actual": None, "clasificacion": None}
        ultimo = evals[-1]
        return {
            "registros": len(evals),
            "imc_actual": ultimo.imc,
            "clasificacion": clasificar_imc(ultimo.imc),
            "imc_promedio": round(sum(e.imc for e in evals) / len(evals), 2),
        }

    def reporte_progreso(self, id_usuario: int) -> dict:
        seguimientos = self.seguimientos.listar_por_usuario(id_usuario)
        pesos = [s.peso_actual for s in seguimientos]
        return {
            "registros": len(seguimientos),
            "peso_inicial": pesos[0] if pesos else None,
            "peso_actual": pesos[-1] if pesos else None,
            "progreso": round(pesos[0] - pesos[-1], 2) if len(pesos) >= 2 else 0.0,
            "detalle": seguimientos,
        }
