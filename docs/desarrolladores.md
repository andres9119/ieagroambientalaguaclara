# Documentación para Desarrolladores

## I.E Agroambiental Agua Clara

---

## Índice

1. [Stack Tecnológico](#1-stack-tecnológico)
2. [Estructura del Proyecto](#2-estructura-del-proyecto)
3. [Modelos de Datos](#3-modelos-de-datos)
4. [Vistas (Views)](#4-vistas-views)
5. [URLs](#5-urls)
6. [Formularios](#6-formularios)
7. [Autenticación y Roles](#7-autenticación-y-roles)
8. [Sistema de Notas](#8-sistema-de-notas)
9. [Certificados PDF](#9-certificados-pdf)
10. [Importación Excel](#10-importación-excel)
11. [Admin de Django](#11-admin-de-django)
12. [Despliegue](#12-despliegue)
13. [Archivos Clave](#13-archivos-clave)

---

## 1. Stack Tecnológico

| Componente | Versión |
|------------|---------|
| Python | 3.12 |
| Django | 5.1 |
| Base de datos | PostgreSQL (producción) |
| Servidor WSGI | Gunicorn + systemd |
| Proxy reverso | Nginx con SSL |
| Frontend | Bootstrap 5.3 + FontAwesome 6 |
| PDF | xhtml2pdf |
| Excel | openpyxl |
| QR | qrcode |
| Almacenamiento estático | WhiteNoise |

---

## 2. Estructura del Proyecto

```
colegio_web/
├── colegio_web/          # Config principal
│   ├── settings.py       # Configuración Django
│   ├── urls.py           # URL raíz
│   ├── wsgi.py           # WSGI para Gunicorn
│   └── context_processors.py
├── academico/            # Sedes, Cursos, Materias, Horarios
├── admisiones/           # Preinscripción (oculta temporalmente)
├── contacto/             # Formulario de contacto
├── docentes/             # CRUD docentes, calificaciones, asistencia
├── estudiantes/          # Estudiantes, matrículas, notas
├── inicio/               # Home
├── institucion/          # Info institucional, certificados PDF
├── noticias/             # Noticias
├── usuarios/             # Auth, dashboard, perfiles
├── static/               # CSS, JS, imágenes
├── templates/            # Templates HTML
├── media/                # Archivos subidos
├── deploy/               # Despliegue (gunicorn, nginx)
├── docs/                 # Documentación
├── run/                  # Socket Gunicorn (creado en servidor)
└── logs/                 # Logs (creado en servidor)
```

---

## 3. Modelos de Datos

### 3.1 App `usuarios`

#### Usuario (AbstractUser)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| username | CharField | Número de documento (para estudiantes) |
| rol | CharField | `admin`, `docente`, `estudiante` |
| telefono | CharField | Opcional |
| direccion | TextField | Opcional |
| foto | ImageField | Opcional |
| must_change_password | BooleanField | True = forzar cambio de contraseña |

**Relaciones:**
- `perfil_docente` (OneToOne → Docente)
- `perfil_estudiante` (OneToOne → Estudiante)

#### Notificacion
| Campo | Tipo |
|-------|------|
| usuario | ForeignKey → Usuario |
| mensaje | CharField(255) |
| link | CharField(255) nullable |
| leido | BooleanField |
| fecha_creacion | DateTimeField auto_now_add |

### 3.2 App `academico`

#### Sede
| Campo | Tipo |
|-------|------|
| nombre | CharField(200) unique |
| codigo_dane | CharField(50) |
| zona | CharField(50) |
| direccion | TextField |

#### Curso
| Campo | Tipo | Descripción |
|-------|------|-------------|
| nombre | CharField(50) | Grado en letras: Preescolar, Primero...Once |
| nivel | CharField(50) | Básica Primaria/Secundaria/Media Técnica |
| tutor | ForeignKey → Docente | Tutor del curso |
| sede | ForeignKey → Sede | |
| hora_inicio_jornada | TimeField | |
| hora_fin_jornada | TimeField | |
| duracion_clase | PositiveSmallIntegerField | Default 50 min |
| duracion_descanso | PositiveSmallIntegerField | Default 10 min |
| num_descansos | PositiveSmallIntegerField | Default 2 |

**Métodos:** `get_materias()`, `get_estudiantes_count()`

#### Materia
| Campo | Tipo |
|-------|------|
| nombre | CharField(100) |
| descripcion | TextField |
| creditos | PositiveIntegerField |
| area | CharField(50) |
| docentes | ManyToManyField → Docente |

#### CursoMateria (relación curso-materia)
| Campo | Tipo |
|-------|------|
| curso | ForeignKey → Curso |
| materia | ForeignKey → Materia |
| docente | ForeignKey → Docente (nullable) |
| horas_semanales | PositiveIntegerField |
| periodo_academico | CharField |
| anio_lectivo | PositiveIntegerField |
| objetivo_p1..p4 | TextField |

**Unique:** `(curso, materia, periodo_academico, anio_lectivo)`

#### Horario
| Campo | Tipo |
|-------|------|
| curso | ForeignKey → Curso |
| curso_materia | ForeignKey → CursoMateria |
| es_descanso | BooleanField |
| dia | CharField (1-5) |
| hora_inicio | TimeField |
| hora_fin | TimeField |
| aula | CharField(100) |

### 3.3 App `docentes`

#### Docente
| Campo | Tipo |
|-------|------|
| usuario | OneToOneField → Usuario |
| especialidad | CharField(100) |
| titulo | CharField(100) |

### 3.4 App `estudiantes`

#### Estudiante
| Campo | Tipo | Descripción |
|-------|------|-------------|
| usuario | OneToOneField → Usuario | |
| fecha_nacimiento | DateField | |
| acudiente | CharField(200) | |
| tipo_documento | CharField(2) | TI/CC/CE/PA/RC |
| pago_certificado | BooleanField | Default True |
| telefono, celular, direccion, barrio | Varíos | Opcionales |
| lugar_nacimiento | CharField(200) | |
| genero | CharField(1) | M/F |
| rh | CharField(3) | O+, A-, etc. |
| eps | CharField(100) | |
| estrato | CharField(1) | 1-6 |
| nui | CharField(50) | |
| etnia | CharField(100) | |
| discapacidad | CharField(100) | |
| jornada | CharField(50) | |
| zona | CharField(50) | Rural/Urbana |
| pais_origen | CharField(100) | |
| estado_matricula | CharField(50) | |
| modelo_educativo | CharField(100) | |
| fuente_recursos | CharField(50) | |
| campesino | BooleanField | |
| categoria_aula | CharField(50) | |

**Métodos:** `get_materias()`, `get_promedio()`, `get_nota_anual_materia()`, `get_porcentaje_asistencia()`, `get_curso_actual()`

#### Matricula
| Campo | Tipo |
|-------|------|
| estudiante | ForeignKey → Estudiante |
| curso | ForeignKey → Curso |
| anio_lectivo | PositiveIntegerField |
| fecha_matricula | DateField auto_now_add |
| activo | BooleanField |

**Unique:** `(estudiante, curso, anio_lectivo)`

#### Actividad
| Campo | Tipo |
|-------|------|
| curso_materia | ForeignKey → CursoMateria |
| periodo | CharField (1-4) |
| nombre | CharField(100) |
| tipo | CharField | SABER / HACER |
| fecha | DateField auto_now_add |

#### NotaActividad
| Campo | Tipo |
|-------|------|
| actividad | ForeignKey → Actividad |
| estudiante | ForeignKey → Estudiante |
| nota | FloatField |

**Unique:** `(actividad, estudiante)`
**Signal:** Al guardar, actualiza `Calificacion.recalcular_promedios()`

#### Calificacion
| Campo | Tipo | Peso |
|-------|------|------|
| estudiante | ForeignKey → Estudiante | |
| curso_materia | ForeignKey → CursoMateria | |
| nota_saber_acumulada | FloatField | 25% (promedio SABER) |
| nota_saber_final | FloatField | 20% |
| nota_hacer | FloatField | 45% (promedio HACER) |
| nota_ser_auto | FloatField | 5% |
| nota_ser_comportamiento | FloatField | 5% |
| nota | FloatField | **Nota final del periodo** |
| periodo | CharField | 1-4 |
| observaciones | TextField | |

**Unique:** `(estudiante, curso_materia, periodo)`
**Método:** `recalcular_promedios()` — calcula automáticamente promedios SABER y HACER desde NotaActividad

#### Asistencia
| Campo | Tipo |
|-------|------|
| estudiante | ForeignKey → Estudiante |
| curso_materia | ForeignKey → CursoMateria |
| fecha | DateField |
| asistio | BooleanField |
| observacion | TextField |

**Unique:** `(estudiante, curso_materia, fecha)`

#### Disciplina
| Campo | Tipo |
|-------|------|
| estudiante | ForeignKey → Estudiante |
| periodo | CharField |
| anio_lectivo | PositiveIntegerField |
| nota | DecimalField (máx 5.0) |
| observacion | TextField |

#### DocumentoEstudiante
| Campo | Tipo |
|-------|------|
| estudiante | ForeignKey → Estudiante |
| tipo | CharField | cedula, certificado_nacimiento, etc. |
| archivo | FileField |
| descripcion | CharField(200) |
| fecha_carga | DateTimeField auto_now_add |

### 3.5 App `institucion`

#### InformacionInstitucional (singleton)
Campos: historia, mision, vision, valores, lema, mensaje_rectoria, nombre_rector, foto_rector, politica_privacidad, nombre_colegio, dane, nit, resolucion, sede_principal, departamento, municipio, calendario, jornada, horario, rector_cc, codigo_documento, version_documento.

#### DocumentoInteres
| Campo | Tipo |
|-------|------|
| titulo | CharField(200) |
| archivo | FileField |
| categoria | CharField | manual/decreto/circular/general |
| fecha_publicacion | DateTimeField |
| publico | BooleanField |

#### CertificadoEmitido
| Campo | Tipo | Descripción |
|-------|------|-------------|
| codigo | CharField(12) unique | 10 dígitos aleatorios |
| estudiante_nombre | CharField(300) | |
| estudiante_documento | CharField(60) | |
| tipo_documento | CharField(50) | |
| grado | CharField(100) | |
| nivel | CharField(100) | |
| anio | PositiveIntegerField | |
| sede | CharField(200) | |
| fecha_emision | DateTimeField auto_now_add | |
| valido | BooleanField | |

#### PilarEducativo
| Campo | Tipo |
|-------|------|
| titulo | CharField(100) |
| descripcion | TextField |
| icono | CharField(50) | Clase FontAwesome |
| orden | IntegerField |

### 3.6 App `admisiones`

#### Preinscripcion
Campos: nombre_aspirante, fecha_nacimiento, grado_interes, nombre_acudiente, telefono_contacto, email_contacto, estado (pendiente/aprobado/rechazado/aplazado), documentos PDF adjuntos, acepta_politica.

### 3.7 App `contacto`

#### MensajeContacto
Campos: nombre, email, asunto, mensaje, fecha_envio, leido, acepta_politica.

### 3.8 App `noticias`

#### Noticia
Campos: titulo, resumen, contenido, fecha_publicacion, imagen.

---

## 4. Vistas (Views)

### 4.1 `inicio/views.py`
- `HomeView` → TemplateView → `inicio/home.html`

### 4.2 `usuarios/views.py`
- `CustomLoginView` → LoginView (forzar password_change si must_change_password)
- `CustomPasswordChangeView` → PasswordChangeView
- `DashboardView` → TemplateView (estadísticas admin, enlaces por rol)
- `DashboardPagoCertificadoView` → TemplateView (búsqueda + toggle pago)
- `DashboardSedeView` → TemplateView (vista por sede)
- `toggle_pago_certificado` → función (POST toggle)
- `EditarPerfilView` → UpdateView (perfil de usuario)

### 4.3 `academico/views.py`
- `InfoAcademicaView` → ListView (admin)
- `CrearCursoView` → CreateView (con asignación de materias)
- `CrearMateriaView` → CreateView
- `CursoListView` → ListView
- `CursoUpdateView` → UpdateView
- `MateriaListView` → ListView
- `MateriaUpdateView` → UpdateView
- `eliminar_curso` → función (POST)
- `asignar_docentes_curso` → función (formset)
- `promocionar_curso` → función (POST)
- `horarios_curso` → función (POST)
- `exportar_estudiantes_excel` → función (openpyxl)

### 4.4 `docentes/views.py`
- `crear_docente` → función
- `MisCursosView` → ListView (cursos del docente)
- `gestionar_notas` → función (Saber Final + Comportamiento)
- `calificar_periodos` → función principal (1 nota por periodo)
- `gestionar_asistencia` → función (asistencia semanal)
- `actividades_lista` → función
- `actividad_crear` → función
- `actividad_calificar` → función (formset)
- `exportar_notas_csv` → función
- `DocenteListView` → ListView
- `DocenteUpdateView` → UpdateView
- `eliminar_docente` → función
- `calificar_disciplina` → función (solo tutor)

### 4.5 `estudiantes/views.py`
- `EstudianteListView` → ListView
- `EstudianteUpdateView` → UpdateView
- `EstudiantesPorCursoView` → ListView
- `EstudiantesCursoDetailView` → View
- `matricular_estudiante` → función
- `MisNotasView` → ListView (boletín del estudiante)
- `MiAsistenciaView` → ListView
- `MiHorarioView` → DetailView
- `RealizarAutoevaluacionView` → UpdateView
- `GenerarBoletinPDF` → View (PDF)
- `importar_estudiantes_excel_view` → función

### 4.6 `institucion/views.py`
- `InstitucionView` → TemplateView
- `PoliticaPrivacidadView` → TemplateView
- `DocumentosListView` → TemplateView (GET + POST para certificados)
- `GenerarCertificadoEstudiosPDF` → View (PDF con QR)
- `VerificarCertificadoView` → TemplateView (GET + POST)

Límite: **3 certificados por estudiante por mes calendario** (controlado por `fecha_emision >= 1er día del mes`).

### 4.7 `noticias/views.py`
- `NoticiaListView` → ListView
- `NoticiaDetailView` → DetailView

### 4.8 `contacto/views.py`
- `ContactoView` → CreateView

### 4.9 `admisiones/views.py`
- `PreinscripcionView` → CreateView (oculta temporalmente)

---

## 5. URLs

| Ruta | App | Nombre |
|------|-----|--------|
| `/` | inicio | `inicio` |
| `/admin/` | admin | admin |
| `/institucion/` | institucion | `institucion` |
| `/institucion/documentos/` | institucion | `documentos` |
| `/institucion/documentos/certificado/` | institucion | `generar_certificado_estudios_pdf` |
| `/institucion/certificados/verificar/` | institucion | `verificar_certificado` |
| `/institucion/politica-privacidad/` | institucion | `politica_privacidad` |
| `/noticias/` | noticias | `noticias_list` |
| `/contacto/` | contacto | `contacto` |
| `/admisiones/` | admisiones | `admisiones` |
| `/usuarios/login/` | usuarios | `login` |
| `/usuarios/logout/` | usuarios | `logout` |
| `/usuarios/dashboard/` | usuarios | `dashboard` |
| `/usuarios/password-change/` | usuarios | `password_change` |
| `/usuarios/perfil/` | usuarios | `perfil` |
| `/academico/cursos/` | academico | `cursos_list` |
| `/academico/crear-curso/` | academico | `crear_curso` |
| `/academico/crear-materia/` | academico | `crear_materia` |
| `/academico/materias/` | academico | `materias_list` |
| `/academico/curso/<id>/editar/` | academico | `curso_editar` |
| `/academico/curso/<id>/eliminar/` | academico | `eliminar_curso` |
| `/academico/curso/<id>/horarios/` | academico | `horarios_curso` |
| `/academico/curso/<id>/asignar-docentes/` | academico | `asignar_docentes_curso` |
| `/academico/curso/<id>/promocionar/` | academico | `promocionar_curso` |
| `/academico/info-academica/` | academico | `info_academica` |
| `/docentes/lista-docentes/` | docentes | `docentes_list` |
| `/docentes/crear-docente/` | docentes | `crear_docente` |
| `/docentes/docente/<id>/editar/` | docentes | `docente_editar` |
| `/docentes/docente/<id>/eliminar/` | docentes | `eliminar_docente` |
| `/docentes/mis-cursos/` | docentes | `mis_cursos` |
| `/docentes/asignacion/<id>/calificar/` | docentes | `calificar_periodos` |
| `/docentes/asignacion/<id>/asistencia/` | docentes | `gestionar_asistencia` |
| `/docentes/actividades/<id>/` | docentes | `actividades_lista` |
| `/estudiantes/lista/` | estudiantes | `estudiantes_list` |
| `/estudiantes/por-curso/` | estudiantes | `estudiantes_por_curso` |
| `/estudiantes/matricular/` | estudiantes | `matricular_estudiante` |
| `/estudiantes/importar-excel/` | estudiantes | `importar_estudiantes_excel` |
| `/estudiantes/mis-notas/` | estudiantes | `mis_notas` |
| `/estudiantes/mi-asistencia/` | estudiantes | `mi_asistencia` |
| `/estudiantes/mi-horario/` | estudiantes | `mi_horario` |
| `/estudiantes/descargar-boletin/` | estudiantes | `generar_boletin_pdf` |

---

## 6. Formularios

### `academico/forms.py`
- `CursoCreateForm` — GRADO_CHOICES, NIVEL_CHOICES, materias, docente_universal, tutor
- `CursoEditForm` — checkbox materias, horarios, descansos
- `MateriaForm` — con docentes M2M
- `MateriaEditForm` — similar

### `docentes/forms.py`
- `DocenteCreateForm` — username, nombres, email, password, teléfono, especialidad, título
- `DocenteEditForm` — incluye campos de User (first_name, last_name, email, telefono)
- `ActividadForm` — nombre, tipo (SABER/HACER), periodo

### `estudiantes/forms.py`
- `EstudianteEditForm` — campos de Estudiante + usuario (numero_documento, nombres, apellidos)
- `MatricularEstudianteForm` — formulario completo de matrícula
- `AutoevaluacionForm` — solo nota_ser_auto

### `usuarios/forms.py`
- `UsuarioChangeForm` — first_name, last_name, email, telefono, direccion, foto

### `institucion/forms.py`
- `SolicitarCertificadoForm` — solo CSRF (sin campos)

### `admisiones/forms.py`
- `PreinscripcionForm` — formulario completo con documentos adjuntos

### `contacto/forms.py`
- `ContactoForm` — nombre, email, asunto, mensaje, acepta_politica

---

## 7. Autenticación y Roles

**Modelo:** `Usuario` (AbstractUser) con campo `rol`.

| Rol | Acceso |
|-----|--------|
| `admin` | Django Admin, dashboard completo, CRUD todo |
| `docente` | Mis cursos, calificar, asistencia, disciplina |
| `estudiante` | Mis notas, horario, asistencia, autoevaluación, certificados |

**Flujo de login:**
1. Login → `CustomLoginView`
2. Si `must_change_password=True` → redirige a `password_change`
3. Si no → redirige a `dashboard`

**Logout:** redirige a `inicio`.

---

## 8. Sistema de Notas

### Pesos por periodo
| Componente | Peso | Cálculo |
|-----------|------|---------|
| Saber Acumulado | 25% | Promedio automático de actividades tipo SABER |
| Saber Final | 20% | Ingresado por docente |
| Hacer | 45% | Promedio automático de actividades tipo HACER |
| Ser (Autoevaluación) | 5% | Ingresado por estudiante |
| Ser (Comportamiento) | 5% | Ingresado por docente |

**Nota del periodo:** Ingresada directamente por el docente en el flujo simplificado (`calificar_periodos`).

### Nota anual
```
(P1 + P2 + P3 + P4) / 4
```

### Escala de valoración
| Rango | Valoración |
|-------|-----------|
| >= 4.6 | Superior |
| >= 4.0 | Alto |
| >= 3.0 | Básico |
| < 3.0 | Bajo |

### Flujo de calificación
1. Docente crea actividades (SABER o HACER) por periodo
2. Docente califica cada actividad (0.0 - 5.0)
3. `NotaActividad.save()` dispara `Calificacion.recalcular_promedios()`
4. Docente ingresa `nota_saber_final` y `nota_ser_comportamiento` en `gestionar_notas`
5. Estudiante ingresa `nota_ser_auto` en `autoevaluacion`
6. Docente ingresa la `nota` final del periodo en `calificar_periodos`

---

## 9. Certificados PDF

### Generación
1. Estudiante autenticado POST a `/institucion/documentos/`
2. Verifica `pago_certificado=True` en su perfil
3. Verifica límite de **3 certificados por mes calendario**
4. Genera código de 10 dígitos aleatorios único
5. Crea `CertificadoEmitido` en BD
6. Muestra enlace de descarga en la misma página
7. GET a `/institucion/documentos/certificado/?codigo=X`
8. Genera PDF con `xhtml2pdf` usando `certificado_estudios_pdf.html`
9. Incluye código QR con URL de verificación

### Verificación
- Cualquier persona (sin login) puede verificar un certificado
- GET o POST a `/institucion/certificados/verificar/`
- Ingresa el código de 10 dígitos
- Muestra datos del certificado si es válido

### Límites
- **Máximo 3 por estudiante por mes** (resetea el día 1 de cada mes)
- Controlado por `fecha_emision >= primer_dia_del_mes_actual`

### Fecha en letras
- `fecha_a_letras()` genera una fecha coherente en letras y números (ej: `treinta (30) días del mes de julio del año dos mil veintiseis (2026).`).
- `numero_a_palabras()` soporta hasta millones; la lista de decenas incluye elementos vacíos para alinear el índice (30=treinta, 90=noventa).

---

## 10. Importación Excel

**Comando:** `python manage.py importar_estudiantes_excel <archivo.xlsx>`

**Columnas requeridas:** DOC, TIPODOC, NOMBRE1, APELLIDO1, GRUPO, GRADO_COD

**Columnas opcionales:** NOMBRE2, APELLIDO2, GENERO, FECHA_NACIMIENTO, BARRIO, EPS, TIPO DE SANGRE, ESTRATO, NUI, SEDE, JORNADA, ZONA_SEDE, ETNIA, DISCAPACIDAD, MODELO, FUENTE_RECURSOS, CAMPESINO, CATEGORIA_AULA, PAIS_ORIGEN, ESTADO, CORREO, TELEFONO

**Mapeo de tipos de documento:**
- TI / T.I / TARJETA DE IDENTIDAD → `TI`
- CC / C.C / CEDULA DE CIUDADANIA → `CC`
- CE / C.E / CEDULA DE EXTRANJERIA → `CE`
- PA / PASAPORTE → `PA`
- RC / R.C / REGISTRO CIVIL → `RC`

**Opciones:** `--anio 2026` (default), `--dry-run` (solo muestra sin guardar)

**Cursos por sede:** cada curso se busca/crea por **nombre del grado + sede** (`get_or_create(nombre=grupo, sede=sede_obj)`), respetando `unique_together ('nombre','sede')`. Así un mismo grado (ej. "Preescolar") en distintas sedes genera cursos separados, y cada estudiante se matricula en el curso de su propia sede.

---

## 11. Admin de Django

### Apps registradas con configuración personalizada:

| App | Modelos |
|-----|---------|
| academico | Sede, Curso (con promoción), Materia, CursoMateria |
| estudiantes | Estudiante (con form personalizado + document inline) |
| docentes | Docente |
| institucion | InformacionInstitucional, DocumentoInteres, CertificadoEmitido, PilarEducativo |
| noticias | Noticia |
| contacto | MensajeContacto |
| admisiones | Preinscripcion (con acciones masivas: aprobar, rechazar, exportar Excel, convertir en estudiante) |

### Funcionalidades especiales en admin:
- `CursoAdmin`: botón "Promocionar" en changelist
- `EstudianteAdmin`: `pago_certificado` editable en lista, form con campos de usuario
- `PreinscripcionAdmin`: acciones masivas, exportación Excel, conversión a estudiante

---

## 12. Despliegue

### Servidor
- **Host:** VPS IONOS
- **Usuario SSH:** `andres` (sudo)
- **Ruta:** `/var/www/colegio_web`
- **Virtualenv:** `/var/www/colegio_web/env/`
- **Servicio:** `gunicorn-colegio.service` (systemd, usuario www-data)
- **Socket:** `unix:/var/www/colegio_web/run/gunicorn.sock`
- **Workers:** 2
- **Otros proyectos en mismo VPS:** `tienda_heilyn`, `suarez`

### Actualizar producción
```bash
cd /var/www/colegio_web
sudo git pull
source env/bin/activate
pip install -r requirements.txt
python manage.py migrate
sudo /var/www/colegio_web/env/bin/python manage.py collectstatic --noinput
sudo systemctl restart gunicorn-colegio
```

### Archivos de deploy
- `deploy/gunicorn.service` → `/etc/systemd/system/gunicorn-colegio.service`
- `deploy/nginx.conf` → `/etc/nginx/sites-available/colegio`
- `deploy/deploy.sh` → script de instalación inicial

### Variables de entorno (`.env`)
| Variable | Descripción |
|----------|-------------|
| DJANGO_SECRET_KEY | Secreto Django |
| DJANGO_DEBUG | False en producción |
| DJANGO_ALLOWED_HOSTS | dominios separados por coma |
| DB_ENGINE | `django.db.backends.postgresql` |
| DB_NAME | `colegio_db` |
| DB_USER | `colegio_user` |
| DB_PASSWORD | contraseña |
| DB_HOST | `localhost` |
| DB_PORT | `5432` |

### SSL
- Let's Encrypt vía certbot
- Dominios: `ieagroambientalaguaclara.com`, `www.ieagroambientalaguaclara.com`
- Redirección HTTP → HTTPS

---

## 13. Archivos Clave

| Archivo | Propósito |
|---------|-----------|
| `colegio_web/settings.py` | Configuración general |
| `colegio_web/urls.py` | Enrutamiento raíz |
| `colegio_web/context_processors.py` | Notificaciones en contexto global |
| `estudiantes/models.py` | Modelo Estudiante y sistema de notas |
| `estudiantes/utils.py` | Helper `render_to_pdf()` |
| `estudiantes/management/commands/importar_estudiantes_excel.py` | Importación Excel |
| `institucion/views.py` | Generación y verificación de certificados |
| `institucion/models.py` | CertificadoEmitido, InformacionInstitucional |
| `templates/base.html` | Layout principal (navbar, sidebar, footer) |
| `templates/institucion/certificado_estudios_pdf.html` | Template PDF |
| `deploy/gunicorn.service` | Servicio systemd |
| `deploy/nginx.conf` | Configuración Nginx |
| `docs/desarrolladores.md` | Esta documentación |
| `../AGENTS.md` | Contexto completo del proyecto (fuera del repo) |
