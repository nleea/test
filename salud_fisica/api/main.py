"""API HTTP del Sistema de Gestión de Salud Física (FastAPI).

Expone los requerimientos funcionales como endpoints REST:
  RF01 usuarios, RF02 evaluaciones, RF03 rutinas,
  RF04 seguimiento, RF05 reportes, más autenticación.

Documentación interactiva: http://localhost:8000/docs
"""

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status

from ..database import get_connection, init_db
from ..models import Usuario
from ..services import (
    AuthError,
    AuthService,
    EvaluacionService,
    ReporteService,
    RutinaService,
    SeguimientoService,
    UsuarioService,
    clasificar_imc,
)
from . import schemas
from .deps import get_current_user, get_db, require_roles

@asynccontextmanager
async def lifespan(_: FastAPI):
    """Al iniciar: crea un administrador por defecto si la base está vacía."""
    conn = get_connection()
    init_db(conn)
    try:
        servicio = UsuarioService(conn)
        if not servicio.listar():
            servicio.registrar("Admin", "Sistema", "admin@salud.com", "admin123", "administrador")
    finally:
        conn.close()
    yield


app = FastAPI(
    title="Sistema de Gestión de Salud Física",
    description="API HTTP para usuarios, evaluaciones, rutinas, seguimiento y reportes.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/", tags=["estado"])
def raiz() -> dict:
    return {"servicio": "Salud Física API", "docs": "/docs"}


# ============================ Autenticación ============================ #
@app.post("/auth/login", tags=["autenticación"], response_model=schemas.UsuarioOut)
def login(datos: schemas.LoginIn, conn=Depends(get_db)) -> Usuario:
    try:
        return AuthService(conn).login(datos.correo, datos.contrasena)
    except AuthError as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(e))


@app.post("/auth/recuperar", tags=["autenticación"])
def recuperar(datos: schemas.RecuperarIn, conn=Depends(get_db)) -> dict:
    try:
        AuthService(conn).recuperar_contrasena(datos.correo, datos.nueva_contrasena)
        return {"mensaje": "Contraseña actualizada."}
    except AuthError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


# ========================= RF01 - Usuarios ============================ #
@app.post("/usuarios", tags=["usuarios"], response_model=schemas.UsuarioOut,
          status_code=status.HTTP_201_CREATED)
def crear_usuario(datos: schemas.UsuarioCrear, conn=Depends(get_db),
                  _: Usuario = Depends(require_roles("administrador"))):
    servicio = UsuarioService(conn)
    try:
        uid = servicio.registrar(datos.nombre, datos.apellido, datos.correo,
                                 datos.contrasena, datos.rol)
    except AuthError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, str(e))
    return servicio.obtener(uid)


@app.get("/usuarios", tags=["usuarios"], response_model=list[schemas.UsuarioOut])
def listar_usuarios(conn=Depends(get_db),
                    _: Usuario = Depends(require_roles("administrador", "entrenador"))):
    return UsuarioService(conn).listar()


@app.get("/usuarios/{id_usuario}", tags=["usuarios"], response_model=schemas.UsuarioOut)
def obtener_usuario(id_usuario: int, conn=Depends(get_db),
                    actual: Usuario = Depends(get_current_user)):
    if actual.rol == "usuario" and actual.id_usuario != id_usuario:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Solo puedes ver tu propio perfil.")
    usuario = UsuarioService(conn).obtener(id_usuario)
    if not usuario:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado.")
    return usuario


@app.put("/usuarios/{id_usuario}", tags=["usuarios"], response_model=schemas.UsuarioOut)
def modificar_usuario(id_usuario: int, datos: schemas.UsuarioActualizar,
                      conn=Depends(get_db), actual: Usuario = Depends(get_current_user)):
    if actual.rol != "administrador" and actual.id_usuario != id_usuario:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "No puedes modificar otros usuarios.")
    servicio = UsuarioService(conn)
    usuario = servicio.obtener(id_usuario)
    if not usuario:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado.")
    cambios = datos.model_dump(exclude_none=True)
    if "rol" in cambios and actual.rol != "administrador":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Solo un administrador cambia roles.")
    for campo, valor in cambios.items():
        setattr(usuario, campo, valor)
    servicio.modificar(usuario)
    return usuario


@app.delete("/usuarios/{id_usuario}", tags=["usuarios"], status_code=status.HTTP_204_NO_CONTENT)
def eliminar_usuario(id_usuario: int, conn=Depends(get_db),
                     _: Usuario = Depends(require_roles("administrador"))):
    UsuarioService(conn).eliminar(id_usuario)


# ======================= RF02 - Evaluaciones ========================== #
@app.post("/usuarios/{id_usuario}/evaluaciones", tags=["evaluaciones"],
          response_model=schemas.EvaluacionOut, status_code=status.HTTP_201_CREATED)
def registrar_evaluacion(id_usuario: int, datos: schemas.EvaluacionCrear,
                         conn=Depends(get_db),
                         _: Usuario = Depends(require_roles("administrador", "entrenador"))):
    ev = EvaluacionService(conn).registrar(
        id_usuario, datos.peso, datos.altura, datos.grasa_corporal, datos.fecha
    )
    return _evaluacion_out(ev)


@app.get("/usuarios/{id_usuario}/evaluaciones", tags=["evaluaciones"],
         response_model=list[schemas.EvaluacionOut])
def historial_evaluaciones(id_usuario: int, conn=Depends(get_db),
                           actual: Usuario = Depends(get_current_user)):
    _verificar_acceso_propio(actual, id_usuario)
    return [_evaluacion_out(e) for e in EvaluacionService(conn).historial(id_usuario)]


# ========================== RF03 - Rutinas ============================ #
@app.post("/rutinas", tags=["rutinas"], response_model=schemas.RutinaOut,
          status_code=status.HTTP_201_CREATED)
def crear_rutina(datos: schemas.RutinaCrear, conn=Depends(get_db),
                 _: Usuario = Depends(require_roles("administrador", "entrenador"))):
    servicio = RutinaService(conn)
    rid = servicio.crear(datos.nombre, datos.descripcion or "", datos.duracion or 0)
    return servicio.repo.obtener(rid)


@app.get("/rutinas", tags=["rutinas"], response_model=list[schemas.RutinaOut])
def listar_rutinas(conn=Depends(get_db), _: Usuario = Depends(get_current_user)):
    return RutinaService(conn).listar()


@app.post("/rutinas/asignar", tags=["rutinas"], status_code=status.HTTP_201_CREATED)
def asignar_rutina(datos: schemas.AsignacionCrear, conn=Depends(get_db),
                   _: Usuario = Depends(require_roles("administrador", "entrenador"))):
    RutinaService(conn).asignar(datos.id_usuario, datos.id_rutina)
    return {"mensaje": "Rutina asignada."}


@app.get("/usuarios/{id_usuario}/rutinas", tags=["rutinas"],
         response_model=list[schemas.RutinaOut])
def rutinas_asignadas(id_usuario: int, conn=Depends(get_db),
                      actual: Usuario = Depends(get_current_user)):
    _verificar_acceso_propio(actual, id_usuario)
    return RutinaService(conn).listar_asignadas(id_usuario)


# ======================== RF04 - Seguimiento ========================== #
@app.post("/usuarios/{id_usuario}/seguimiento", tags=["seguimiento"],
          response_model=schemas.SeguimientoOut, status_code=status.HTTP_201_CREATED)
def registrar_avance(id_usuario: int, datos: schemas.SeguimientoCrear,
                     conn=Depends(get_db),
                     _: Usuario = Depends(require_roles("administrador", "entrenador"))):
    servicio = SeguimientoService(conn)
    sid = servicio.registrar_avance(id_usuario, datos.peso_actual,
                                    datos.observacion or "", datos.fecha)
    return next(s for s in servicio.historial(id_usuario) if s.id_seguimiento == sid)


@app.get("/usuarios/{id_usuario}/seguimiento", tags=["seguimiento"],
         response_model=list[schemas.SeguimientoOut])
def historial_seguimiento(id_usuario: int, conn=Depends(get_db),
                          actual: Usuario = Depends(get_current_user)):
    _verificar_acceso_propio(actual, id_usuario)
    return SeguimientoService(conn).historial(id_usuario)


# ========================== RF05 - Reportes =========================== #
@app.get("/usuarios/{id_usuario}/reportes/peso", tags=["reportes"])
def reporte_peso(id_usuario: int, conn=Depends(get_db),
                 actual: Usuario = Depends(get_current_user)):
    _verificar_acceso_propio(actual, id_usuario)
    return ReporteService(conn).reporte_peso(id_usuario)


@app.get("/usuarios/{id_usuario}/reportes/imc", tags=["reportes"])
def reporte_imc(id_usuario: int, conn=Depends(get_db),
                actual: Usuario = Depends(get_current_user)):
    _verificar_acceso_propio(actual, id_usuario)
    return ReporteService(conn).reporte_imc(id_usuario)


@app.get("/usuarios/{id_usuario}/reportes/progreso", tags=["reportes"])
def reporte_progreso(id_usuario: int, conn=Depends(get_db),
                     actual: Usuario = Depends(get_current_user)):
    _verificar_acceso_propio(actual, id_usuario)
    reporte = ReporteService(conn).reporte_progreso(id_usuario)
    reporte["detalle"] = [vars(s) for s in reporte["detalle"]]
    return reporte


# ----------------------------- Auxiliares ----------------------------- #
def _verificar_acceso_propio(actual: Usuario, id_usuario: int) -> None:
    if actual.rol == "usuario" and actual.id_usuario != id_usuario:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Solo puedes consultar tus propios datos.")


def _evaluacion_out(ev) -> dict:
    return {**vars(ev), "clasificacion": clasificar_imc(ev.imc)}


def run() -> None:
    """Punto de entrada para `poetry run salud-api`."""
    import uvicorn

    uvicorn.run("salud_fisica.api.main:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    run()
