# Manual de Usuario

## I.E Agroambiental Agua Clara — Plataforma Educativa

---

## Índice

1. [Introducción](#1-introducción)
2. [Acceso al Sistema](#2-acceso-al-sistema)
3. [Roles de Usuario](#3-roles-de-usuario)
4. [Administrador](#4-administrador)
5. [Docente](#5-docente)
6. [Estudiante](#6-estudiante)
7. [Visitante (Sin sesión)](#7-visitante-sin-sesión)
8. [Sistema de Notas](#8-sistema-de-notas)
9. [Certificados de Estudio](#9-certificados-de-estudio)
10. [Preguntas Frecuentes](#10-preguntas-frecuentes)

---

## 1. Introducción

La plataforma educativa de la **I.E Agroambiental Agua Clara** es un sistema web para la gestión académica que permite:

- **Administradores:** gestionar estudiantes, docentes, cursos, materias, horarios, notas y certificados.
- **Docentes:** registrar calificaciones, asistencia, actividades y notas disciplinarias.
- **Estudiantes:** consultar notas, horarios, asistencia, descargar boletines y certificados.
- **Visitantes:** ver información institucional, noticias, documentos públicos y verificar certificados.

**URL del sitio:** [https://ieagroambientalaguaclara.com](https://ieagroambientalaguaclara.com)

---

## 2. Acceso al Sistema

### Iniciar sesión
1. Ir a [https://ieagroambientalaguaclara.com](https://ieagroambientalaguaclara.com)
2. Hacer clic en **Iniciar Sesión** (botón en la barra de navegación, lado derecho)
3. Ingresar **usuario** y **contraseña**
4. Hacer clic en **Ingresar**

![Login](https://ui-avatars.com/api/?name=Login&background=0ea5e9&color=fff)

### Primera vez
- Los estudiantes reciben: **Usuario = número de documento**, **Contraseña = `{documento}*`** (ej: `12345*`).
- Los docentes reciben: **Usuario = username asignado**, **Contraseña = generada aleatoriamente**.
- Al iniciar sesión por primera vez, el sistema pedirá **cambiar la contraseña**.

### Recuperar acceso
Si olvidó su contraseña, contacte al administrador del sistema para que le genere una nueva.

### Cerrar sesión
Haga clic en su nombre (esquina superior derecha) → **Salir**.

---

## 3. Roles de Usuario

| Rol | ¿Qué puede hacer? |
|-----|-------------------|
| **Administrador** | Gestionar todo: estudiantes, docentes, cursos, materias, horarios, notas, certificados. Accede al panel de administración de Django. |
| **Docente** | Ver sus cursos asignados, calificar por periodos, registrar asistencia, crear actividades, calificar disciplina (si es tutor). |
| **Estudiante** | Ver sus notas, horario, asistencia, descargar boletín PDF, solicitar certificados de estudio, autoevaluarse. |
| **Visitante** | Ver información del colegio, noticias, documentos públicos, verificar certificados. |

---

## 4. Administrador

### 4.1 Dashboard

![Dashboard Admin]

Al iniciar sesión como administrador, verá:

**Estadísticas:** total de estudiantes, docentes, cursos y materias.

**Acceso rápido:**
- Estudiantes por Curso
- Matricular estudiante
- Importar Excel
- Ver Cursos / Materias / Docentes
- Nuevo Curso / Materia / Docente
- Información Académica
- Solicitudes de Admisión
- Vista por Sedes

### 4.2 Gestionar Estudiantes

#### Ver estudiantes por curso
1. Ir a **Estudiantes por Curso** en el dashboard
2. Seleccionar un curso para ver sus estudiantes
3. Puede buscar por nombre o documento

#### Matricular un estudiante
1. Ir a **Matricular** en el dashboard
2. Llenar el formulario: documento, nombres, apellidos, fecha de nacimiento, acudiente, curso
3. Hacer clic en guardar
4. El sistema crea automáticamente el usuario del estudiante

#### Importar estudiantes desde Excel
1. Ir a **Importar Excel** en el dashboard
2. Seleccionar archivo Excel con formato SIMAT
3. El sistema crea estudiantes, usuarios y matrículas automáticamente

**Formato del Excel:**
- Columnas requeridas: DOC, TIPODOC, NOMBRE1, APELLIDO1, GRUPO, GRADO_COD
- Ver documentación técnica para columnas opcionales

#### Editar estudiante
1. Ir a **Estudiantes por Curso**
2. Seleccionar un curso
3. Hacer clic en el lápiz (editar) junto al estudiante
4. Modificar los datos necesarios
5. Guardar

### 4.3 Gestionar Docentes

#### Crear docente
1. Ir a **Nuevo Docente** en el dashboard
2. Ingresar: username, nombres, apellidos, email, especialidad, título
3. Guardar — se crea el usuario automáticamente

#### Editar docente
1. Ir a **Ver Docentes**
2. Hacer clic en editar
3. Modificar datos

#### Eliminar docente
1. Ir a **Ver Docentes**
2. Hacer clic en eliminar
3. Confirmar — se elimina docente y su usuario

### 4.4 Gestionar Cursos

#### Crear curso
1. Ir a **Nuevo Curso**
2. Seleccionar: grado (letras), nivel, sede
3. Opcional: asignar materias, docente universal, tutor
4. Guardar

#### Editar curso
1. Ir a **Ver Cursos**
2. Hacer clic en editar
3. Modificar: nombre, nivel, sede, materias, horarios de jornada, descansos
4. Guardar

#### Asignar docentes a materias
1. Ir a **Ver Cursos**
2. Hacer clic en "Asignar Docentes" del curso
3. Para cada materia, seleccionar un docente
4. Guardar

#### Horarios
1. Ir a **Ver Cursos**
2. Hacer clic en "Horarios" del curso
3. Configurar las horas y asignar materias a cada espacio
4. Guardar

#### Promocionar estudiantes
1. Ir a **Ver Cursos**
2. Hacer clic en "Promocionar"
3. Seleccionar curso de destino, año lectivo
4. Marcar estudiantes a promocionar
5. Opcional: desactivar matrícula actual
6. Confirmar

### 4.5 Gestionar Materias

#### Crear materia
1. Ir a **Nueva Materia**
2. Ingresar: nombre, descripción, área, docentes
3. Guardar

### 4.6 Pago de Certificados

1. En el dashboard, sección **Pago de Certificados**
2. Buscar estudiante por nombre o documento
3. Usar el botón **Marcar Pagado / Desmarcar Pago** para habilitar o bloquear certificados

### 4.7 Admin de Django

Para funciones avanzadas, ir a **Administración** en el dashboard o `/admin/`:

- CRUD completo de todos los modelos
- Promoción de cursos
- Aprobación/rechazo de preinscripciones (admisiones)
- Exportación de datos
- Conversión de preinscripciones aprobadas en estudiantes

---

## 5. Docente

### 5.1 Mis Cursos

1. Iniciar sesión como docente
2. Ir a **Mis Cursos** (menú lateral o dashboard)
3. Verá los cursos y materias asignadas agrupados por curso

### 5.2 Calificar por Periodos (flujo principal)

1. En **Mis Cursos**, hacer clic en **Calificar** de la materia
2. Verá una tabla con todos los estudiantes y columnas P1, P2, P3, P4
3. Ingresar la **nota** (0.0 - 5.0) para cada estudiante en cada periodo
4. Opcional: agregar observaciones
5. También puede editar los **objetivos** de cada periodo
6. Guardar

### 5.3 Gestionar Actividades

#### Crear actividades
1. En **Mis Cursos**, hacer clic en **Actividades** de la materia
2. Hacer clic en **Nueva Actividad**
3. Ingresar: nombre, tipo (Saber o Hacer), periodo
4. Guardar

#### Calificar actividades
1. Desde la lista de actividades, hacer clic en **Calificar**
2. Ingresar nota (0.0 - 5.0) para cada estudiante
3. Guardar — los promedios se actualizan automáticamente

### 5.4 Asistencia

1. En **Mis Cursos**, hacer clic en **Asistencia** de la materia
2. Seleccionar una fecha (navegación semanal)
3. Marcar/desmarcar **asistió** para cada estudiante
4. Opcional: agregar observaciones
5. Guardar

### 5.5 Disciplina (solo tutores)

1. Ir a la materia donde es tutor
2. Hacer clic en **Disciplina**
3. Seleccionar periodo
4. Ingresar nota disciplinaria (1.0 - 5.0) para cada estudiante
5. Guardar

### 5.6 Exportar notas

1. En la vista de notas de una materia
2. Hacer clic en **Exportar CSV**
3. Descarga un archivo CSV con las notas del periodo

---

## 6. Estudiante

### 6.1 Mis Notas

1. Iniciar sesión como estudiante
2. Ir a **Mis Notas** (menú lateral)
3. Verá un boletín con todas las materias y sus notas por periodo
4. Se muestra el promedio anual de cada materia

### 6.2 Autoevaluación

1. Ir a **Mis Notas**
2. Para cada materia, hacer clic en **Autoevaluarse**
3. Ingresar su autocalificación (0.0 - 5.0)
4. Guardar

### 6.3 Mi Horario

1. Ir a **Mi Horario** (menú lateral)
2. Verá su horario de clases organizado por días

### 6.4 Mi Asistencia

1. Ir a **Mi Asistencia** (menú lateral)
2. Verá el registro de asistencias y el porcentaje total

### 6.5 Descargar Boletín PDF

1. Ir a **Mis Notas**
2. Hacer clic en **Descargar Boletín PDF**
3. Se descarga un archivo PDF con todas las notas

### 6.6 Certificados de Estudio

Ver sección [Certificados de Estudio](#9-certificados-de-estudio).

---

## 7. Visitante (Sin sesión)

### Información institucional
- `/` — Página principal con información general
- `/institucion/` — Historia, misión, visión, valores
- `/noticias/` — Noticias publicadas por la institución
- `/contacto/` — Formulario de contacto

### Documentos públicos
- `/institucion/documentos/` — Documentos de interés público (manuales, decretos, circulares)

### Verificar certificados
- `/institucion/certificados/verificar/` — Ingrese el código de 10 dígitos para verificar un certificado

---

## 8. Sistema de Notas

### Pesos por periodo

| Componente | Peso |
|-----------|------|
| Saber (evaluaciones) | 45% |
| Hacer (tareas/trabajos) | 45% |
| Ser (autoevaluación + comportamiento) | 10% |

### Escala

| Rango | Valoración |
|-------|-----------|
| 4.6 - 5.0 | **Superior** |
| 4.0 - 4.5 | **Alto** |
| 3.0 - 3.9 | **Básico** |
| 0.0 - 2.9 | **Bajo** |

### Nota final anual
Promedio de los 4 periodos: `(P1 + P2 + P3 + P4) / 4`

---

## 9. Certificados de Estudio

### Solicitar certificado
1. Iniciar sesión como **estudiante**
2. Ir a **Documentos** en el menú de navegación
3. Hacer clic en **Solicitar Certificado**
4. Se genera el certificado y aparece un enlace de descarga
5. Hacer clic en **Descargar PDF**

### Límite
- **Máximo 3 certificados por mes** por estudiante
- El contador se reinicia el día 1 de cada mes

### Requisitos
- El estudiante debe tener `pago_certificado=True` (todos lo tienen por defecto)
- Si está bloqueado, contactar al administrador

### Verificar certificado
Cualquier persona puede verificar un certificado:
1. Ir a `/institucion/certificados/verificar/`
2. Ingresar el código de 10 dígitos que aparece en el PDF
3. Si es válido, se muestran los datos del certificado

---

## 10. Preguntas Frecuentes

### ¿Olvidé mi contraseña?
Contacte al administrador para que le genere una nueva contraseña.

### ¿No puedo descargar un certificado?
Verifique que:
1. Su cuenta tiene `pago_certificado=True` (si no, pida al administrador que lo habilite)
2. No ha excedido el límite de 3 certificados este mes
3. Tiene una matrícula activa

### ¿Cómo sé mi usuario?
- **Estudiante:** su número de documento
- **Docente:** el username asignado por el administrador

### ¿Puedo ver mis notas de años anteriores?
Por ahora el sistema muestra solo el año lectivo actual. Consulte al administrador si necesita notas de años anteriores.

### ¿Los padres pueden acceder al sistema?
Actualmente el sistema está diseñado para estudiantes, docentes y administradores. Los acudientes pueden solicitar información al correo institucional.

---

*Documento generado el 29 de julio de 2026. Para soporte técnico: agroambientalaguaclara@gmail.com*
