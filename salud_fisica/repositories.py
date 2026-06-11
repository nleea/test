"""Acceso a datos (CRUD) para cada entidad.

Cada repositorio recibe una conexión SQLite ya abierta y traduce entre
filas de la base y dataclasses del módulo models.
"""

import sqlite3
from typing import List, Optional

from .models import EvaluacionFisica, Rutina, Seguimiento, Usuario


class UsuarioRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def crear(self, usuario: Usuario, contrasena_hash: str) -> int:
        cur = self.conn.execute(
            "INSERT INTO Usuario (nombre, apellido, correo, contrasena, rol) "
            "VALUES (?, ?, ?, ?, ?)",
            (usuario.nombre, usuario.apellido, usuario.correo, contrasena_hash, usuario.rol),
        )
        self.conn.commit()
        return cur.lastrowid

    def modificar(self, usuario: Usuario) -> None:
        self.conn.execute(
            "UPDATE Usuario SET nombre = ?, apellido = ?, correo = ?, rol = ? "
            "WHERE id_usuario = ?",
            (usuario.nombre, usuario.apellido, usuario.correo, usuario.rol, usuario.id_usuario),
        )
        self.conn.commit()

    def actualizar_contrasena(self, id_usuario: int, contrasena_hash: str) -> None:
        self.conn.execute(
            "UPDATE Usuario SET contrasena = ? WHERE id_usuario = ?",
            (contrasena_hash, id_usuario),
        )
        self.conn.commit()

    def eliminar(self, id_usuario: int) -> None:
        self.conn.execute("DELETE FROM Usuario WHERE id_usuario = ?", (id_usuario,))
        self.conn.commit()

    def obtener(self, id_usuario: int) -> Optional[Usuario]:
        row = self.conn.execute(
            "SELECT * FROM Usuario WHERE id_usuario = ?", (id_usuario,)
        ).fetchone()
        return self._to_model(row) if row else None

    def obtener_por_correo(self, correo: str) -> Optional[sqlite3.Row]:
        return self.conn.execute(
            "SELECT * FROM Usuario WHERE correo = ?", (correo,)
        ).fetchone()

    def listar(self) -> List[Usuario]:
        rows = self.conn.execute("SELECT * FROM Usuario ORDER BY apellido, nombre").fetchall()
        return [self._to_model(r) for r in rows]

    @staticmethod
    def _to_model(row: sqlite3.Row) -> Usuario:
        return Usuario(
            id_usuario=row["id_usuario"],
            nombre=row["nombre"],
            apellido=row["apellido"],
            correo=row["correo"],
            rol=row["rol"],
        )


class EvaluacionRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def crear(self, e: EvaluacionFisica) -> int:
        cur = self.conn.execute(
            "INSERT INTO EvaluacionFisica (fecha, peso, altura, imc, grasa_corporal, id_usuario) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (e.fecha, e.peso, e.altura, e.imc, e.grasa_corporal, e.id_usuario),
        )
        self.conn.commit()
        return cur.lastrowid

    def listar_por_usuario(self, id_usuario: int) -> List[EvaluacionFisica]:
        rows = self.conn.execute(
            "SELECT * FROM EvaluacionFisica WHERE id_usuario = ? ORDER BY fecha",
            (id_usuario,),
        ).fetchall()
        return [
            EvaluacionFisica(
                id_evaluacion=r["id_evaluacion"], fecha=r["fecha"], peso=r["peso"],
                altura=r["altura"], imc=r["imc"], grasa_corporal=r["grasa_corporal"],
                id_usuario=r["id_usuario"],
            )
            for r in rows
        ]


class RutinaRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def crear(self, r: Rutina) -> int:
        cur = self.conn.execute(
            "INSERT INTO Rutina (nombre, descripcion, duracion) VALUES (?, ?, ?)",
            (r.nombre, r.descripcion, r.duracion),
        )
        self.conn.commit()
        return cur.lastrowid

    def modificar(self, r: Rutina) -> None:
        self.conn.execute(
            "UPDATE Rutina SET nombre = ?, descripcion = ?, duracion = ? WHERE id_rutina = ?",
            (r.nombre, r.descripcion, r.duracion, r.id_rutina),
        )
        self.conn.commit()

    def obtener(self, id_rutina: int) -> Optional[Rutina]:
        row = self.conn.execute(
            "SELECT * FROM Rutina WHERE id_rutina = ?", (id_rutina,)
        ).fetchone()
        if not row:
            return None
        return Rutina(
            id_rutina=row["id_rutina"], nombre=row["nombre"],
            descripcion=row["descripcion"], duracion=row["duracion"],
        )

    def listar(self) -> List[Rutina]:
        rows = self.conn.execute("SELECT * FROM Rutina ORDER BY nombre").fetchall()
        return [
            Rutina(id_rutina=r["id_rutina"], nombre=r["nombre"],
                   descripcion=r["descripcion"], duracion=r["duracion"])
            for r in rows
        ]

    def asignar(self, id_usuario: int, id_rutina: int, fecha: str) -> None:
        self.conn.execute(
            "INSERT INTO AsignacionRutina (id_usuario, id_rutina, fecha) VALUES (?, ?, ?)",
            (id_usuario, id_rutina, fecha),
        )
        self.conn.commit()

    def listar_asignadas(self, id_usuario: int) -> List[Rutina]:
        rows = self.conn.execute(
            "SELECT r.* FROM Rutina r "
            "JOIN AsignacionRutina a ON a.id_rutina = r.id_rutina "
            "WHERE a.id_usuario = ? ORDER BY a.fecha DESC",
            (id_usuario,),
        ).fetchall()
        return [
            Rutina(id_rutina=r["id_rutina"], nombre=r["nombre"],
                   descripcion=r["descripcion"], duracion=r["duracion"])
            for r in rows
        ]


class SeguimientoRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def crear(self, s: Seguimiento) -> int:
        cur = self.conn.execute(
            "INSERT INTO Seguimiento (fecha, observacion, peso_actual, id_usuario) "
            "VALUES (?, ?, ?, ?)",
            (s.fecha, s.observacion, s.peso_actual, s.id_usuario),
        )
        self.conn.commit()
        return cur.lastrowid

    def listar_por_usuario(self, id_usuario: int) -> List[Seguimiento]:
        rows = self.conn.execute(
            "SELECT * FROM Seguimiento WHERE id_usuario = ? ORDER BY fecha",
            (id_usuario,),
        ).fetchall()
        return [
            Seguimiento(
                id_seguimiento=r["id_seguimiento"], fecha=r["fecha"],
                observacion=r["observacion"], peso_actual=r["peso_actual"],
                id_usuario=r["id_usuario"],
            )
            for r in rows
        ]
