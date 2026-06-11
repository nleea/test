"""Pruebas de la API HTTP usando TestClient y una BD SQLite temporal."""

import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from salud_fisica.api import deps
from salud_fisica.api.main import app
from salud_fisica.database import get_connection, init_db

ADMIN = ("admin@salud.com", "admin123")


class TestAPI(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        self.db_path = Path(self.tmp.name)

        def override_db():
            conn = get_connection(self.db_path)
            init_db(conn)
            try:
                yield conn
            finally:
                conn.close()

        app.dependency_overrides[deps.get_db] = override_db
        # Crear admin inicial en la BD de prueba
        conn = get_connection(self.db_path)
        init_db(conn)
        from salud_fisica.services import UsuarioService
        UsuarioService(conn).registrar("Admin", "Sistema", *ADMIN[:1], ADMIN[1], "administrador")
        conn.close()
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()
        self.db_path.unlink(missing_ok=True)

    def test_login_ok_y_fallido(self):
        r = self.client.post("/auth/login", json={"correo": ADMIN[0], "contrasena": ADMIN[1]})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["rol"], "administrador")
        r = self.client.post("/auth/login", json={"correo": ADMIN[0], "contrasena": "mala"})
        self.assertEqual(r.status_code, 401)

    def test_crear_usuario_requiere_admin(self):
        nuevo = {"nombre": "Ana", "apellido": "Lopez", "correo": "ana@x.com",
                 "contrasena": "1234", "rol": "usuario"}
        # Sin credenciales -> 401
        self.assertEqual(self.client.post("/usuarios", json=nuevo).status_code, 401)
        # Con admin -> 201
        r = self.client.post("/usuarios", json=nuevo, auth=ADMIN)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()["correo"], "ana@x.com")

    def test_evaluacion_calcula_imc(self):
        self.client.post("/usuarios", auth=ADMIN, json={
            "nombre": "Ana", "apellido": "Lopez", "correo": "ana@x.com",
            "contrasena": "1234", "rol": "usuario"})
        r = self.client.post("/usuarios/2/evaluaciones", auth=ADMIN,
                             json={"peso": 70, "altura": 1.75, "grasa_corporal": 20})
        self.assertEqual(r.status_code, 201)
        body = r.json()
        self.assertEqual(body["imc"], 22.86)
        self.assertEqual(body["clasificacion"], "Peso normal")

    def test_flujo_rutina_y_reporte(self):
        self.client.post("/usuarios", auth=ADMIN, json={
            "nombre": "Ana", "apellido": "Lopez", "correo": "ana@x.com",
            "contrasena": "1234", "rol": "usuario"})
        rid = self.client.post("/rutinas", auth=ADMIN,
                               json={"nombre": "Fuerza", "duracion": 45}).json()["id_rutina"]
        self.client.post("/rutinas/asignar", auth=ADMIN,
                         json={"id_usuario": 2, "id_rutina": rid})
        # El usuario consulta sus propias rutinas
        r = self.client.get("/usuarios/2/rutinas", auth=("ana@x.com", "1234"))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()), 1)

    def test_usuario_no_ve_datos_de_otro(self):
        self.client.post("/usuarios", auth=ADMIN, json={
            "nombre": "Ana", "apellido": "Lopez", "correo": "ana@x.com",
            "contrasena": "1234", "rol": "usuario"})
        r = self.client.get("/usuarios/1/reportes/peso", auth=("ana@x.com", "1234"))
        self.assertEqual(r.status_code, 403)


if __name__ == "__main__":
    unittest.main()
