"""Pruebas de la lógica de negocio usando una base SQLite en memoria."""

import sqlite3
import unittest

from salud_fisica.database import SCHEMA
from salud_fisica.security import hash_password, verify_password
from salud_fisica.services import (
    AuthError,
    AuthService,
    EvaluacionService,
    ReporteService,
    RutinaService,
    SeguimientoService,
    UsuarioService,
    calcular_imc,
    clasificar_imc,
)


def conexion_memoria() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    return conn


class TestIMC(unittest.TestCase):
    def test_calculo(self):
        self.assertEqual(calcular_imc(70, 1.75), 22.86)

    def test_altura_invalida(self):
        with self.assertRaises(ValueError):
            calcular_imc(70, 0)

    def test_clasificacion(self):
        self.assertEqual(clasificar_imc(17), "Bajo peso")
        self.assertEqual(clasificar_imc(22), "Peso normal")
        self.assertEqual(clasificar_imc(27), "Sobrepeso")
        self.assertEqual(clasificar_imc(31), "Obesidad")


class TestSeguridad(unittest.TestCase):
    def test_hash_verifica(self):
        h = hash_password("secreta")
        self.assertNotEqual(h, "secreta")
        self.assertTrue(verify_password("secreta", h))
        self.assertFalse(verify_password("otra", h))


class TestServicios(unittest.TestCase):
    def setUp(self):
        self.conn = conexion_memoria()
        self.usuarios = UsuarioService(self.conn)
        self.auth = AuthService(self.conn)

    def test_registro_y_login(self):
        self.usuarios.registrar("Ana", "Lopez", "ana@x.com", "1234", "usuario")
        u = self.auth.login("ana@x.com", "1234")
        self.assertEqual(u.nombre, "Ana")
        with self.assertRaises(AuthError):
            self.auth.login("ana@x.com", "mala")

    def test_correo_duplicado(self):
        self.usuarios.registrar("Ana", "Lopez", "ana@x.com", "1234", "usuario")
        with self.assertRaises(AuthError):
            self.usuarios.registrar("Otra", "Persona", "ana@x.com", "1234", "usuario")

    def test_flujo_evaluacion_y_reporte(self):
        uid = self.usuarios.registrar("Ana", "Lopez", "ana@x.com", "1234", "usuario")
        evals = EvaluacionService(self.conn)
        evals.registrar(uid, 80, 1.75, 25)
        evals.registrar(uid, 78, 1.75, 24)
        reporte = ReporteService(self.conn).reporte_peso(uid)
        self.assertEqual(reporte["registros"], 2)
        self.assertEqual(reporte["variacion"], -2.0)

    def test_asignacion_rutina(self):
        uid = self.usuarios.registrar("Ana", "Lopez", "ana@x.com", "1234", "usuario")
        rutinas = RutinaService(self.conn)
        rid = rutinas.crear("Fuerza", "Pesas", 45)
        rutinas.asignar(uid, rid)
        asignadas = rutinas.listar_asignadas(uid)
        self.assertEqual(len(asignadas), 1)
        self.assertEqual(asignadas[0].nombre, "Fuerza")

    def test_seguimiento(self):
        uid = self.usuarios.registrar("Ana", "Lopez", "ana@x.com", "1234", "usuario")
        seg = SeguimientoService(self.conn)
        seg.registrar_avance(uid, 80, "inicio")
        seg.registrar_avance(uid, 77, "mes 1")
        prog = ReporteService(self.conn).reporte_progreso(uid)
        self.assertEqual(prog["progreso"], 3.0)

    def tearDown(self):
        self.conn.close()


if __name__ == "__main__":
    unittest.main()
