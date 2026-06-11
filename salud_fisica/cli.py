"""Interfaz de consola. Presenta menús distintos según el rol del
usuario autenticado (Administrador, Entrenador, Usuario).
"""

import sqlite3

from .models import ROLES, Usuario
from .services import (
    AuthError,
    AuthService,
    EvaluacionService,
    ReporteService,
    RutinaService,
    SeguimientoService,
    UsuarioService,
    clasificar_imc,
)


def _input_float(mensaje: str) -> float:
    while True:
        try:
            return float(input(mensaje).replace(",", "."))
        except ValueError:
            print("  Valor inválido, ingrese un número.")


def _input_int(mensaje: str) -> int:
    while True:
        try:
            return int(input(mensaje))
        except ValueError:
            print("  Valor inválido, ingrese un número entero.")


class App:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.auth = AuthService(conn)
        self.usuarios = UsuarioService(conn)
        self.evaluaciones = EvaluacionService(conn)
        self.rutinas = RutinaService(conn)
        self.seguimiento = SeguimientoService(conn)
        self.reportes = ReporteService(conn)
        self.actual: Usuario | None = None

    # ------------------------------------------------------------------ #
    # Arranque y autenticación
    # ------------------------------------------------------------------ #
    def run(self) -> None:
        self._asegurar_admin_inicial()
        print("\n=== SISTEMA DE GESTIÓN DE SALUD FÍSICA ===")
        while True:
            print("\n1) Iniciar sesión\n2) Recuperar contraseña\n0) Salir")
            opcion = input("Opción: ").strip()
            if opcion == "1":
                if self._login():
                    self._menu_principal()
            elif opcion == "2":
                self._recuperar()
            elif opcion == "0":
                print("Hasta luego.")
                return

    def _asegurar_admin_inicial(self) -> None:
        """Crea un administrador por defecto si no hay usuarios."""
        if not self.usuarios.listar():
            self.usuarios.registrar(
                "Admin", "Sistema", "admin@salud.com", "admin123", "administrador"
            )
            print("Se creó el administrador inicial: admin@salud.com / admin123")

    def _login(self) -> bool:
        correo = input("Correo: ").strip()
        contrasena = input("Contraseña: ").strip()
        try:
            self.actual = self.auth.login(correo, contrasena)
            print(f"\nBienvenido, {self.actual.nombre_completo} ({self.actual.rol}).")
            return True
        except AuthError as e:
            print(f"  {e}")
            return False

    def _recuperar(self) -> None:
        correo = input("Correo registrado: ").strip()
        nueva = input("Nueva contraseña: ").strip()
        try:
            self.auth.recuperar_contrasena(correo, nueva)
            print("  Contraseña actualizada.")
        except AuthError as e:
            print(f"  {e}")

    # ------------------------------------------------------------------ #
    # Menú según rol
    # ------------------------------------------------------------------ #
    def _menu_principal(self) -> None:
        rol = self.actual.rol
        while self.actual is not None:
            print(f"\n--- Menú {rol} ---")
            opciones = self._opciones_por_rol(rol)
            for clave, (texto, _) in opciones.items():
                print(f"{clave}) {texto}")
            print("0) Cerrar sesión")
            eleccion = input("Opción: ").strip()
            if eleccion == "0":
                self.actual = None
                return
            accion = opciones.get(eleccion)
            if accion:
                accion[1]()
            else:
                print("  Opción no válida.")

    def _opciones_por_rol(self, rol: str) -> dict:
        comunes = {}
        if rol == "administrador":
            return {
                "1": ("Gestionar usuarios", self._gestionar_usuarios),
                "2": ("Ver rutinas", self._listar_rutinas),
                "3": ("Ver reportes de un usuario", self._ver_reportes),
            }
        if rol == "entrenador":
            return {
                "1": ("Registrar evaluación física", self._registrar_evaluacion),
                "2": ("Crear rutina", self._crear_rutina),
                "3": ("Asignar rutina", self._asignar_rutina),
                "4": ("Registrar avance (seguimiento)", self._registrar_avance),
                "5": ("Consultar avances de un usuario", self._consultar_avances),
            }
        # usuario
        return {
            "1": ("Consultar mis rutinas", self._mis_rutinas),
            "2": ("Consultar mi historial físico", self._mi_historial),
            "3": ("Actualizar mi información", self._actualizar_perfil),
            **comunes,
        }

    # ------------------------------------------------------------------ #
    # RF01 - Usuarios (Administrador)
    # ------------------------------------------------------------------ #
    def _gestionar_usuarios(self) -> None:
        print("\n a) Registrar  b) Listar  c) Modificar  d) Eliminar")
        op = input(" Opción: ").strip().lower()
        if op == "a":
            nombre = input("  Nombre: ").strip()
            apellido = input("  Apellido: ").strip()
            correo = input("  Correo: ").strip()
            contrasena = input("  Contraseña: ").strip()
            rol = input(f"  Rol {ROLES}: ").strip().lower()
            if rol not in ROLES:
                print("  Rol inválido."); return
            try:
                uid = self.usuarios.registrar(nombre, apellido, correo, contrasena, rol)
                print(f"  Usuario creado con id {uid}.")
            except AuthError as e:
                print(f"  {e}")
        elif op == "b":
            self._listar_usuarios()
        elif op == "c":
            self._listar_usuarios()
            uid = _input_int("  Id a modificar: ")
            usuario = self.usuarios.obtener(uid)
            if not usuario:
                print("  No existe."); return
            usuario.nombre = input(f"  Nombre [{usuario.nombre}]: ").strip() or usuario.nombre
            usuario.apellido = input(f"  Apellido [{usuario.apellido}]: ").strip() or usuario.apellido
            usuario.correo = input(f"  Correo [{usuario.correo}]: ").strip() or usuario.correo
            self.usuarios.modificar(usuario)
            print("  Usuario actualizado.")
        elif op == "d":
            self._listar_usuarios()
            uid = _input_int("  Id a eliminar: ")
            self.usuarios.eliminar(uid)
            print("  Usuario eliminado.")

    def _listar_usuarios(self) -> None:
        print("\n  ID | Nombre | Correo | Rol")
        for u in self.usuarios.listar():
            print(f"  {u.id_usuario:>2} | {u.nombre_completo} | {u.correo} | {u.rol}")

    # ------------------------------------------------------------------ #
    # RF02 - Evaluaciones (Entrenador)
    # ------------------------------------------------------------------ #
    def _registrar_evaluacion(self) -> None:
        self._listar_usuarios()
        uid = _input_int("  Id del usuario: ")
        peso = _input_float("  Peso (kg): ")
        altura = _input_float("  Altura (m): ")
        grasa = _input_float("  % grasa corporal: ")
        ev = self.evaluaciones.registrar(uid, peso, altura, grasa)
        print(f"  Evaluación registrada. IMC = {ev.imc} ({clasificar_imc(ev.imc)})")

    # ------------------------------------------------------------------ #
    # RF03 - Rutinas (Entrenador / Administrador)
    # ------------------------------------------------------------------ #
    def _crear_rutina(self) -> None:
        nombre = input("  Nombre: ").strip()
        descripcion = input("  Descripción: ").strip()
        duracion = _input_int("  Duración (min): ")
        rid = self.rutinas.crear(nombre, descripcion, duracion)
        print(f"  Rutina creada con id {rid}.")

    def _asignar_rutina(self) -> None:
        self._listar_rutinas()
        rid = _input_int("  Id de la rutina: ")
        self._listar_usuarios()
        uid = _input_int("  Id del usuario: ")
        self.rutinas.asignar(uid, rid)
        print("  Rutina asignada.")

    def _listar_rutinas(self) -> None:
        print("\n  ID | Nombre | Duración (min)")
        for r in self.rutinas.listar():
            print(f"  {r.id_rutina:>2} | {r.nombre} | {r.duracion}")

    # ------------------------------------------------------------------ #
    # RF04 - Seguimiento (Entrenador)
    # ------------------------------------------------------------------ #
    def _registrar_avance(self) -> None:
        self._listar_usuarios()
        uid = _input_int("  Id del usuario: ")
        peso = _input_float("  Peso actual (kg): ")
        obs = input("  Observación: ").strip()
        self.seguimiento.registrar_avance(uid, peso, obs)
        print("  Avance registrado.")

    def _consultar_avances(self) -> None:
        self._listar_usuarios()
        uid = _input_int("  Id del usuario: ")
        for s in self.seguimiento.historial(uid):
            print(f"  {s.fecha} | {s.peso_actual} kg | {s.observacion}")

    # ------------------------------------------------------------------ #
    # RF05 - Reportes (Administrador)
    # ------------------------------------------------------------------ #
    def _ver_reportes(self) -> None:
        self._listar_usuarios()
        uid = _input_int("  Id del usuario: ")
        print("\n  Reporte de peso:", self.reportes.reporte_peso(uid))
        print("  Reporte de IMC: ", self.reportes.reporte_imc(uid))
        prog = self.reportes.reporte_progreso(uid)
        prog.pop("detalle", None)
        print("  Reporte de progreso:", prog)

    # ------------------------------------------------------------------ #
    # Vista del Usuario final
    # ------------------------------------------------------------------ #
    def _mis_rutinas(self) -> None:
        rutinas = self.rutinas.listar_asignadas(self.actual.id_usuario)
        if not rutinas:
            print("  No tienes rutinas asignadas."); return
        for r in rutinas:
            print(f"  - {r.nombre} ({r.duracion} min): {r.descripcion}")

    def _mi_historial(self) -> None:
        evals = self.evaluaciones.historial(self.actual.id_usuario)
        if not evals:
            print("  Sin evaluaciones registradas."); return
        for e in evals:
            print(f"  {e.fecha} | {e.peso} kg | IMC {e.imc} ({clasificar_imc(e.imc)})")

    def _actualizar_perfil(self) -> None:
        u = self.usuarios.obtener(self.actual.id_usuario)
        u.nombre = input(f"  Nombre [{u.nombre}]: ").strip() or u.nombre
        u.apellido = input(f"  Apellido [{u.apellido}]: ").strip() or u.apellido
        u.correo = input(f"  Correo [{u.correo}]: ").strip() or u.correo
        self.usuarios.modificar(u)
        self.actual = u
        print("  Información actualizada.")
