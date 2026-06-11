# Sistema de Gestión de Salud Física

Implementación en **Python** del sistema descrito en [`features.md`](features.md).
Expone una **API HTTP (FastAPI)** sobre una base de datos relacional **SQLite**,
con autenticación por roles y los módulos de usuarios, evaluaciones, rutinas,
seguimiento y reportes. Incluye también una interfaz de consola (`main.py`).

## Requisitos

- Python 3.10+ y [Poetry](https://python-poetry.org/).

## Instalación

```bash
poetry install
```

## Ejecución de la API

```bash
poetry run salud-api          # http://localhost:8000
```

Documentación interactiva (Swagger): **http://localhost:8000/docs**

En el primer arranque se crea un administrador por defecto:

| Correo            | Contraseña |
|-------------------|------------|
| admin@salud.com   | admin123   |

La autenticación de los endpoints protegidos usa **HTTP Basic** (`correo:contraseña`).
La base de datos se genera automáticamente en `salud_fisica.db`.

### App de consola (alternativa)

```bash
poetry run python main.py
```

## Pruebas

```bash
poetry run pytest -q
```

## Endpoints principales

| Método | Ruta | Requerimiento |
|--------|------|---------------|
| POST | `/auth/login`, `/auth/recuperar` | Autenticación |
| GET/POST/PUT/DELETE | `/usuarios`, `/usuarios/{id}` | RF01 Usuarios |
| POST/GET | `/usuarios/{id}/evaluaciones` | RF02 Evaluaciones (IMC) |
| POST/GET | `/rutinas`, `/rutinas/asignar` | RF03 Rutinas |
| POST/GET | `/usuarios/{id}/seguimiento` | RF04 Seguimiento |
| GET | `/usuarios/{id}/reportes/{peso\|imc\|progreso}` | RF05 Reportes |

## Estructura

```
pyproject.toml           Configuración de Poetry y dependencias
main.py                  App de consola (alternativa)
salud_fisica/
  database.py            Conexión SQLite y esquema (tablas)
  security.py            Hash de contraseñas (PBKDF2 + sal)
  models.py              Entidades del dominio (dataclasses)
  repositories.py        Acceso a datos (CRUD)
  services.py            Lógica de negocio (IMC, reportes, auth)
  cli.py                 Menús de consola por rol
  api/
    schemas.py           Esquemas Pydantic (validación)
    deps.py              Dependencias: BD y auth por rol
    main.py              App FastAPI y endpoints
tests/
  test_sistema.py        Pruebas de la lógica de negocio
  test_api.py            Pruebas de la API HTTP
```

## Mapeo de requerimientos (features.md)

| Requerimiento | Implementación |
|---------------|----------------|
| RF01 Gestión de usuarios | `UsuarioService` + menú Administrador |
| RF02 Evaluaciones físicas (IMC) | `EvaluacionService.calcular_imc` |
| RF03 Rutinas (crear/asignar) | `RutinaService` |
| RF04 Seguimiento | `SeguimientoService` |
| RF05 Reportes (peso/IMC/progreso) | `ReporteService` |
| Autenticación / roles | `AuthService` + `security.py` |
| Base de datos relacional | SQLite (`database.py`) |

### Roles

- **Administrador**: gestiona usuarios, consulta rutinas y reportes.
- **Entrenador**: registra evaluaciones, crea y asigna rutinas, registra avances.
- **Usuario**: consulta sus rutinas e historial, actualiza su información.
