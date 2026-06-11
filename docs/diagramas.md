# Diagramas — Sistema de Gestión de Salud Física

Diagramas en formato **Mermaid** (se renderizan automáticamente en GitHub y en
VS Code con la extensión *Markdown Preview Mermaid*). Reflejan la implementación
real: capa de modelos, repositorios, servicios y API HTTP.

Índice:
1. [Diagrama de casos de uso](#1-diagrama-de-casos-de-uso)
2. [Diagramas de flujo](#2-diagramas-de-flujo)
3. [Diagrama de clases](#3-diagrama-de-clases)
4. [Diagramas de secuencia](#4-diagramas-de-secuencia)

---

## 1. Diagrama de casos de uso

```mermaid
flowchart LR
    admin(["👤 Administrador"])
    entren(["👤 Entrenador"])
    user(["👤 Usuario"])

    subgraph SISTEMA["Sistema de Gestión de Salud Física"]
        UC1(["Iniciar sesión"])
        UC2(["Recuperar contraseña"])
        UC3(["Gestionar usuarios<br/>(crear/editar/eliminar)"])
        UC4(["Registrar evaluación física"])
        UC5(["Calcular IMC"])
        UC6(["Crear rutina"])
        UC7(["Asignar rutina"])
        UC8(["Registrar avance / seguimiento"])
        UC9(["Consultar historial físico"])
        UC10(["Consultar rutinas asignadas"])
        UC11(["Generar reportes<br/>(peso / IMC / progreso)"])
        UC12(["Actualizar información personal"])
    end

    admin --- UC1
    admin --- UC3
    admin --- UC11

    entren --- UC1
    entren --- UC4
    entren --- UC6
    entren --- UC7
    entren --- UC8
    entren --- UC9

    user --- UC1
    user --- UC2
    user --- UC10
    user --- UC9
    user --- UC12

    UC4 -.->|«include»| UC5
```

> **Nota:** `Registrar evaluación física` siempre **incluye** `Calcular IMC`
> (el IMC se calcula automáticamente al guardar peso y altura).

---

## 2. Diagramas de flujo

### 2.1 Autenticación (login)

```mermaid
flowchart TD
    A([Inicio]) --> B[/Usuario ingresa correo y contraseña/]
    B --> C{¿Correo existe?}
    C -->|No| E[Mostrar error de credenciales]
    C -->|Sí| D{¿Hash de contraseña coincide?}
    D -->|No| E
    D -->|Sí| F[Crear sesión / devolver usuario]
    F --> G{Rol del usuario}
    G -->|administrador| H[Menú Administrador]
    G -->|entrenador| I[Menú Entrenador]
    G -->|usuario| J[Menú Usuario]
    E --> K([Fin])
    H --> K
    I --> K
    J --> K
```

### 2.2 Registrar evaluación física y calcular IMC (RF02)

```mermaid
flowchart TD
    A([Inicio]) --> B[/Entrenador ingresa peso, altura, % grasa/]
    B --> C{¿altura > 0?}
    C -->|No| D[Error: altura inválida]
    C -->|Sí| E["Calcular IMC = peso / altura²"]
    E --> F[Clasificar IMC según OMS]
    F --> G[(Guardar evaluación en BD)]
    G --> H[/Devolver IMC y clasificación/]
    D --> Z([Fin])
    H --> Z
```

### 2.3 Generar reporte de progreso (RF05)

```mermaid
flowchart TD
    A([Inicio]) --> B[/Seleccionar usuario/]
    B --> C[(Leer evaluaciones y seguimientos)]
    C --> D{¿Existen registros?}
    D -->|No| E[Reporte vacío: 0 registros]
    D -->|Sí| F[Calcular peso inicial, actual y variación]
    F --> G[Calcular IMC promedio y clasificación]
    G --> H[/Devolver reporte/]
    E --> Z([Fin])
    H --> Z
```

---

## 3. Diagrama de clases

```mermaid
classDiagram
    direction LR

    %% ---------- Modelos (dominio) ----------
    class Usuario {
        +int id_usuario
        +str nombre
        +str apellido
        +str correo
        +str rol
        +nombre_completo() str
    }
    class EvaluacionFisica {
        +int id_evaluacion
        +str fecha
        +float peso
        +float altura
        +float imc
        +float grasa_corporal
        +int id_usuario
    }
    class Rutina {
        +int id_rutina
        +str nombre
        +str descripcion
        +int duracion
    }
    class Seguimiento {
        +int id_seguimiento
        +str fecha
        +str observacion
        +float peso_actual
        +int id_usuario
    }

    %% ---------- Repositorios (acceso a datos) ----------
    class UsuarioRepository {
        +crear(usuario, hash) int
        +modificar(usuario)
        +eliminar(id)
        +obtener(id) Usuario
        +obtener_por_correo(correo)
        +listar() list~Usuario~
    }
    class EvaluacionRepository {
        +crear(evaluacion) int
        +listar_por_usuario(id) list
    }
    class RutinaRepository {
        +crear(rutina) int
        +modificar(rutina)
        +asignar(id_usuario, id_rutina, fecha)
        +listar() list~Rutina~
        +listar_asignadas(id) list~Rutina~
    }
    class SeguimientoRepository {
        +crear(seguimiento) int
        +listar_por_usuario(id) list
    }

    %% ---------- Servicios (lógica de negocio) ----------
    class AuthService {
        +login(correo, contrasena) Usuario
        +recuperar_contrasena(correo, nueva)
    }
    class UsuarioService {
        +registrar(...) int
        +modificar(usuario)
        +eliminar(id)
        +listar() list~Usuario~
    }
    class EvaluacionService {
        +registrar(...) EvaluacionFisica
        +historial(id) list
    }
    class RutinaService {
        +crear(...) int
        +asignar(id_usuario, id_rutina)
        +listar_asignadas(id) list
    }
    class SeguimientoService {
        +registrar_avance(...) int
        +historial(id) list
    }
    class ReporteService {
        +reporte_peso(id) dict
        +reporte_imc(id) dict
        +reporte_progreso(id) dict
    }

    %% ---------- Relaciones ----------
    Usuario "1" --> "0..*" EvaluacionFisica : tiene
    Usuario "1" --> "0..*" Seguimiento : tiene
    Usuario "0..*" --> "0..*" Rutina : asignada

    AuthService --> UsuarioRepository
    UsuarioService --> UsuarioRepository
    EvaluacionService --> EvaluacionRepository
    RutinaService --> RutinaRepository
    SeguimientoService --> SeguimientoRepository
    ReporteService --> EvaluacionRepository
    ReporteService --> SeguimientoRepository

    UsuarioRepository ..> Usuario : devuelve
    EvaluacionRepository ..> EvaluacionFisica : devuelve
    RutinaRepository ..> Rutina : devuelve
    SeguimientoRepository ..> Seguimiento : devuelve
```

---

## 4. Diagramas de secuencia

### 4.1 Inicio de sesión

```mermaid
sequenceDiagram
    actor U as Usuario
    participant API as FastAPI (/auth/login)
    participant Auth as AuthService
    participant Repo as UsuarioRepository
    participant DB as SQLite

    U->>API: POST /auth/login {correo, contrasena}
    API->>Auth: login(correo, contrasena)
    Auth->>Repo: obtener_por_correo(correo)
    Repo->>DB: SELECT * FROM Usuario WHERE correo=?
    DB-->>Repo: fila usuario (o nulo)
    Repo-->>Auth: usuario
    Auth->>Auth: verify_password(contrasena, hash)
    alt credenciales válidas
        Auth-->>API: Usuario
        API-->>U: 200 OK {datos del usuario}
    else inválidas
        Auth-->>API: AuthError
        API-->>U: 401 Unauthorized
    end
```

### 4.2 Registrar evaluación física (cálculo de IMC)

```mermaid
sequenceDiagram
    actor E as Entrenador
    participant API as FastAPI
    participant Sec as require_roles
    participant Svc as EvaluacionService
    participant Repo as EvaluacionRepository
    participant DB as SQLite

    E->>API: POST /usuarios/{id}/evaluaciones {peso, altura, grasa}
    API->>Sec: verificar rol (admin/entrenador)
    Sec-->>API: autorizado
    API->>Svc: registrar(id, peso, altura, grasa)
    Svc->>Svc: calcular_imc(peso, altura)
    Svc->>Repo: crear(evaluacion)
    Repo->>DB: INSERT INTO EvaluacionFisica
    DB-->>Repo: id_evaluacion
    Repo-->>Svc: id_evaluacion
    Svc-->>API: EvaluacionFisica (con IMC)
    API->>API: clasificar_imc(imc)
    API-->>E: 201 Created {imc, clasificacion}
```

### 4.3 Crear y asignar rutina

```mermaid
sequenceDiagram
    actor E as Entrenador
    participant API as FastAPI
    participant Svc as RutinaService
    participant Repo as RutinaRepository
    participant DB as SQLite

    E->>API: POST /rutinas {nombre, descripcion, duracion}
    API->>Svc: crear(nombre, descripcion, duracion)
    Svc->>Repo: crear(rutina)
    Repo->>DB: INSERT INTO Rutina
    DB-->>Repo: id_rutina
    Repo-->>API: Rutina creada
    API-->>E: 201 Created {id_rutina}

    E->>API: POST /rutinas/asignar {id_usuario, id_rutina}
    API->>Svc: asignar(id_usuario, id_rutina)
    Svc->>Repo: asignar(id_usuario, id_rutina, fecha)
    Repo->>DB: INSERT INTO AsignacionRutina
    DB-->>Repo: ok
    Repo-->>API: ok
    API-->>E: 201 Created {mensaje: "Rutina asignada"}
```

### 4.4 Consultar reporte de progreso

```mermaid
sequenceDiagram
    actor A as Administrador
    participant API as FastAPI
    participant Svc as ReporteService
    participant RE as EvaluacionRepository
    participant RS as SeguimientoRepository
    participant DB as SQLite

    A->>API: GET /usuarios/{id}/reportes/progreso
    API->>Svc: reporte_progreso(id)
    Svc->>RS: listar_por_usuario(id)
    RS->>DB: SELECT * FROM Seguimiento WHERE id_usuario=?
    DB-->>RS: registros
    RS-->>Svc: lista de seguimientos
    Svc->>Svc: calcular peso inicial, actual y progreso
    Svc-->>API: dict {registros, peso_inicial, peso_actual, progreso}
    API-->>A: 200 OK {reporte}
```
