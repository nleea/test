"""Punto de entrada del Sistema de Gestión de Salud Física.

Uso:
    python main.py
"""

from salud_fisica.cli import App
from salud_fisica.database import get_connection, init_db


def main() -> None:
    conn = get_connection()
    init_db(conn)
    try:
        App(conn).run()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
