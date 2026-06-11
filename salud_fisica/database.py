"""Conexión y esquema de la base de datos relacional (SQLite).

Tablas derivadas del modelo de datos de features.md (sección 10):
Usuario, EvaluacionFisica, Rutina, Seguimiento. Se agrega la tabla
AsignacionRutina para soportar "Asignar rutinas" (RF03).
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "salud_fisica.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS Usuario (
    id_usuario   INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre       TEXT    NOT NULL,
    apellido     TEXT    NOT NULL,
    correo       TEXT    NOT NULL UNIQUE,
    contrasena   TEXT    NOT NULL,            -- hash, nunca texto plano
    rol          TEXT    NOT NULL CHECK (rol IN ('administrador', 'entrenador', 'usuario'))
);

CREATE TABLE IF NOT EXISTS EvaluacionFisica (
    id_evaluacion  INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha          TEXT    NOT NULL,
    peso           REAL    NOT NULL,
    altura         REAL    NOT NULL,
    imc            REAL    NOT NULL,
    grasa_corporal REAL,
    id_usuario     INTEGER NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES Usuario (id_usuario) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Rutina (
    id_rutina    INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre       TEXT    NOT NULL,
    descripcion  TEXT,
    duracion     INTEGER                       -- duración en minutos
);

CREATE TABLE IF NOT EXISTS Seguimiento (
    id_seguimiento INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha          TEXT    NOT NULL,
    observacion    TEXT,
    peso_actual    REAL    NOT NULL,
    id_usuario     INTEGER NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES Usuario (id_usuario) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS AsignacionRutina (
    id_asignacion INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario    INTEGER NOT NULL,
    id_rutina     INTEGER NOT NULL,
    fecha         TEXT    NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES Usuario (id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_rutina)  REFERENCES Rutina  (id_rutina)  ON DELETE CASCADE
);
"""


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Devuelve una conexión SQLite con claves foráneas activas y filas por nombre."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    """Crea las tablas si no existen."""
    conn.executescript(SCHEMA)
    conn.commit()
