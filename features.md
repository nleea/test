# SISTEMA DE GESTIÓN DE SALUD FÍSICA

## 1. Introducción

El Sistema de Gestión de Salud Física es una aplicación diseñada para administrar y controlar la información relacionada con el estado físico de los usuarios. El sistema permitirá registrar evaluaciones físicas, controlar el progreso de los usuarios, gestionar planes de entrenamiento y generar reportes que faciliten el seguimiento de la condición física.

## 2. Planteamiento del Problema

Actualmente, muchos centros deportivos y entrenadores realizan el seguimiento de sus usuarios mediante registros manuales o herramientas dispersas, lo que dificulta la organización de la información y el análisis de la evolución física de cada persona.

Por esta razón, se propone desarrollar un Sistema de Gestión de Salud Física que permita centralizar la información, optimizar los procesos de seguimiento y facilitar la toma de decisiones basadas en datos reales.

## 3. Objetivo General

Desarrollar un Sistema de Gestión de Salud Física que permita administrar la información de los usuarios, registrar evaluaciones físicas, gestionar planes de entrenamiento y realizar seguimiento al progreso físico.

## 4. Objetivos Específicos

* Registrar y administrar usuarios.
* Registrar evaluaciones físicas periódicas.
* Gestionar rutinas y planes de entrenamiento.
* Realizar seguimiento al progreso físico.
* Generar reportes e indicadores de salud física.
* Garantizar la seguridad y disponibilidad de la información.

## 5. Alcance

El sistema permitirá la gestión integral de la información física de los usuarios mediante una plataforma informática accesible para administradores, entrenadores y usuarios.

## 6. Requerimientos Funcionales

### RF01. Gestión de Usuarios

* Registrar usuarios.
* Modificar usuarios.
* Eliminar usuarios.
* Consultar usuarios.

### RF02. Gestión de Evaluaciones Físicas

* Registrar peso.
* Registrar altura.
* Calcular IMC.
* Registrar porcentaje de grasa corporal.

### RF03. Gestión de Rutinas

* Crear rutinas.
* Asignar rutinas.
* Modificar rutinas.
* Consultar rutinas.

### RF04. Seguimiento

* Registrar avances físicos.
* Consultar historial.
* Visualizar progreso.

### RF05. Reportes

* Generar reportes de peso.
* Generar reportes de IMC.
* Generar reportes de progreso físico.

## 7. Requerimientos No Funcionales

* Seguridad mediante autenticación de usuarios.
* Interfaz amigable e intuitiva.
* Disponibilidad permanente del sistema.
* Integridad de los datos almacenados.
* Uso de base de datos relacional.

## 8. Actores del Sistema

### Administrador

* Gestiona usuarios.
* Gestiona entrenadores.
* Consulta reportes.

### Entrenador

* Registra evaluaciones.
* Crea rutinas.
* Consulta avances.

### Usuario

* Consulta rutinas.
* Consulta historial físico.
* Actualiza información personal.

## 9. Módulos del Sistema

### Módulo de Autenticación

* Inicio de sesión.
* Recuperación de contraseña.

### Módulo de Usuarios

* Administración de usuarios.

### Módulo de Evaluaciones

* Registro de mediciones físicas.

### Módulo de Rutinas

* Administración de entrenamientos.

### Módulo de Seguimiento

* Control de avances físicos.

### Módulo de Reportes

* Generación de informes estadísticos.

## 10. Modelo de Datos Inicial

### Usuario

* id_usuario
* nombre
* apellido
* correo
* contraseña
* rol

### EvaluacionFisica

* id_evaluacion
* fecha
* peso
* altura
* imc
* grasa_corporal
* id_usuario

### Rutina

* id_rutina
* nombre
* descripcion
* duracion

### Seguimiento

* id_seguimiento
* fecha
* observacion
* peso_actual
* id_usuario

## 11. Tecnologías Propuestas

### Frontend

* HTML5
* CSS3
* JavaScript
* Bootstrap

### Backend

* Por definir según requerimientos académicos.

### Base de Datos

* MySQL

## 12. Conclusión

La implementación del Sistema de Gestión de Salud Física permitirá optimizar el control y seguimiento de la condición física de los usuarios, facilitando la administración de la información y mejorando la eficiencia de los procesos relacionados con la salud física.