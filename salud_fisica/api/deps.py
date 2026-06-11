"""Dependencias de FastAPI: conexión a la base de datos y autenticación
por rol mediante HTTP Basic.
"""

from typing import Iterator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from ..database import get_connection, init_db
from ..models import Usuario
from ..services import AuthError, AuthService

_basic = HTTPBasic()


def get_db() -> Iterator:
    """Abre una conexión SQLite por petición y la cierra al terminar."""
    conn = get_connection()
    init_db(conn)
    try:
        yield conn
    finally:
        conn.close()


def get_current_user(
    credentials: HTTPBasicCredentials = Depends(_basic),
    conn=Depends(get_db),
) -> Usuario:
    """Autentica al usuario con las credenciales HTTP Basic (correo:contraseña)."""
    try:
        return AuthService(conn).login(credentials.username, credentials.password)
    except AuthError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas.",
            headers={"WWW-Authenticate": "Basic"},
        )


def require_roles(*roles: str):
    """Genera una dependencia que exige uno de los roles indicados."""

    def checker(usuario: Usuario = Depends(get_current_user)) -> Usuario:
        if usuario.rol not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acción permitida solo para: {', '.join(roles)}.",
            )
        return usuario

    return checker
