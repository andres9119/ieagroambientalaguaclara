from django.db import models
from django.conf import settings
from academico.models import Curso
from django.db.models import Avg

PERIODOS = (
    ('1', 'Periodo 1'),
    ('2', 'Periodo 2'),
    ('3', 'Periodo 3'),
    ('4', 'Periodo 4'),
)


class Matricula(models.Model):
    estudiante = models.ForeignKey('Estudiante', on_delete=models.CASCADE, related_name='matriculas')
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='matriculas')
    anio_lectivo = models.PositiveIntegerField(default=2026)
    fecha_matricula = models.DateField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    class Meta:
        unique_together = ('estudiante', 'curso', 'anio_lectivo')
        verbose_name = "Matrícula"
        verbose_name_plural = "Matrículas"

    def __str__(self):
        nombre = self.estudiante.usuario.get_full_name() or self.estudiante.usuario.username
        return f"{nombre} - {self.curso} ({self.anio_lectivo})"

class Estudiante(models.Model):

    TIPO_DOC_CHOICES = (
        ('TI', 'T.I'),
        ('CC', 'C.C'),
        ('CE', 'C.E'),
        ('PA', 'Pasaporte'),
        ('RC', 'R.C'),
    )

    GENERO_CHOICES = (
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    )

    RH_CHOICES = (
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
    )

    ESTRATO_CHOICES = (
        ('1', 'Estrato 1'),
        ('2', 'Estrato 2'),
        ('3', 'Estrato 3'),
        ('4', 'Estrato 4'),
        ('5', 'Estrato 5'),
        ('6', 'Estrato 6'),
    )

    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='perfil_estudiante')
    fecha_nacimiento = models.DateField(verbose_name="Fecha de Nacimiento")
    acudiente = models.CharField(max_length=200, verbose_name="Acudiente")
    tipo_documento = models.CharField(max_length=2, choices=TIPO_DOC_CHOICES, default='TI', verbose_name="Tipo de Documento")

    telefono = models.CharField(max_length=50, blank=True, verbose_name="Teléfono")
    celular = models.CharField(max_length=50, blank=True, verbose_name="Celular")
    direccion = models.TextField(blank=True, verbose_name="Dirección")
    barrio = models.CharField(max_length=100, blank=True, verbose_name="Barrio")
    lugar_nacimiento = models.CharField(max_length=200, blank=True, verbose_name="Lugar de Nacimiento")
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES, blank=True, verbose_name="Género")
    rh = models.CharField(max_length=3, choices=RH_CHOICES, blank=True, verbose_name="RH")
    eps = models.CharField(max_length=100, blank=True, verbose_name="EPS")
    estrato = models.CharField(max_length=1, choices=ESTRATO_CHOICES, blank=True, verbose_name="Estrato")
    pago_certificado = models.BooleanField(default=True, verbose_name="Pago de Certificado", help_text="Desmarcar para bloquear la descarga de certificados al estudiante. Por defecto todos pueden descargar.")
    nui = models.CharField(max_length=50, blank=True, verbose_name="NUI")
    etnia = models.CharField(max_length=100, blank=True, verbose_name="Etnia")
    discapacidad = models.CharField(max_length=100, blank=True, verbose_name="Discapacidad")
    jornada = models.CharField(max_length=50, blank=True, verbose_name="Jornada")
    zona = models.CharField(max_length=50, blank=True, verbose_name="Zona", help_text="Rural / Urbana")
    pais_origen = models.CharField(max_length=100, blank=True, verbose_name="País de Origen")
    estado_matricula = models.CharField(max_length=50, blank=True, verbose_name="Estado de Matrícula")
    modelo_educativo = models.CharField(max_length=100, blank=True, verbose_name="Modelo Educativo")
    fuente_recursos = models.CharField(max_length=50, blank=True, verbose_name="Fuente de Recursos")
    campesino = models.BooleanField(default=False, verbose_name="Campesino")
    categoria_aula = models.CharField(max_length=50, blank=True, verbose_name="Categoría de Aula")

    class Meta:
        verbose_name = "Estudiante"
        verbose_name_plural = "Estudiantes"

    def __str__(self):
        nombre = self.usuario.get_full_name() or self.usuario.username
        matricula_actual = self.matriculas.filter(activo=True).first()
        curso_nombre = matricula_actual.curso.nombre if matricula_actual else "Sin Curso"
        return f"{nombre} - {curso_nombre}"

    def display_name(self):
        return self.usuario.get_full_name() or self.usuario.username
    
    def get_materias(self):
        """Retorna las materias del curso en el que está matriculado actualmente el estudiante"""
        matricula_actual = self.matriculas.filter(activo=True).first()
        if matricula_actual:
            return matricula_actual.curso.get_materias().filter(anio_lectivo=matricula_actual.anio_lectivo)
        return []
    
    def get_promedio(self):
        """Calcula el promedio general (promedio de los promedios anuales por materia)."""
        materias = self.get_materias()
        if not materias:
            return 0.0
        notas_anuales = [self.get_nota_anual_materia(cm) for cm in materias]
        return round(sum(notas_anuales) / len(notas_anuales), 2)

    def get_nota_anual_materia(self, curso_materia):
        """Calcula el promedio anual de una materia específica (25% por periodo)"""
        notas = self.calificaciones.filter(curso_materia=curso_materia).values_list('nota', flat=True)
        if not notas:
            return 0.0
        # Sumamos las notas de hasta 4 periodos y dividimos por 4
        # (Si faltan periodos, se asume 0 para esos periodos o se divide por los existentes)
        # El requerimiento dice 25% cada uno, lo que implica suma/4.
        total = sum(notas)
        return round(total / 4, 2)
    
    def get_porcentaje_asistencia(self):
        """Calcula el porcentaje de asistencia del estudiante"""
        total = self.asistencias.count()
        if total == 0:
            return 100.0
        asistencias = self.asistencias.filter(asistio=True).count()
        return round((asistencias / total) * 100, 2)

    def get_curso_actual(self):
        """Retorna el nombre del curso activo o None"""
        mat = self.matriculas.filter(activo=True).first()
        return mat.curso if mat else None

class Actividad(models.Model):
    TIPOS = (
        ('SABER', 'Saber (Evaluación/Lección)'),
        ('HACER', 'Hacer (Tarea/Trabajo/Exposición)'),
    )
    curso_materia = models.ForeignKey('academico.CursoMateria', on_delete=models.CASCADE, related_name='actividades', verbose_name="Materia del Curso")
    periodo = models.CharField(max_length=10, choices=PERIODOS, default="1", verbose_name="Periodo")
    nombre = models.CharField(max_length=100, verbose_name="Nombre de la Actividad")
    tipo = models.CharField(max_length=10, choices=TIPOS, verbose_name="Tipo de Actividad")
    fecha = models.DateField(auto_now_add=True, verbose_name="Fecha de Creación")

    class Meta:
        verbose_name = "Actividad"
        verbose_name_plural = "Actividades"
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()}) - {self.curso_materia}"

class NotaActividad(models.Model):
    actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE, related_name='notas', verbose_name="Actividad")
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='notas_actividades', verbose_name="Estudiante")
    nota = models.FloatField(default=0.0, verbose_name="Nota")

    class Meta:
        verbose_name = "Nota de Actividad"
        verbose_name_plural = "Notas de Actividades"
        unique_together = ('actividad', 'estudiante')

    def __str__(self):
        return f"{self.estudiante} - {self.actividad}: {self.nota}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Al guardar una nota individual, intentamos actualizar el resumen de Calificacion
        calif, _ = Calificacion.objects.get_or_create(
            estudiante=self.estudiante,
            curso_materia=self.actividad.curso_materia,
            periodo=self.actividad.periodo
        )
        calif.recalcular_promedios()

class Calificacion(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='calificaciones', verbose_name="Estudiante")

    curso_materia = models.ForeignKey('academico.CursoMateria', on_delete=models.CASCADE, related_name='calificaciones', null=True, blank=True, verbose_name="Materia del Curso")
    
    # Desglose de notas (0.0 - 5.0)
    # SABER (45%)
    nota_saber_acumulada = models.FloatField(default=0.0, verbose_name="Saber Acumulado (25%)", help_text="Promedio automático de evaluaciones")
    nota_saber_final = models.FloatField(default=0.0, verbose_name="Saber Final (20%)")
    
    # HACER (45%)
    nota_hacer = models.FloatField(default=0.0, verbose_name="Hacer (45%)", help_text="Promedio automático de tareas/trabajos")
    
    # SER (10%)
    nota_ser_auto = models.FloatField(default=0.0, verbose_name="Autoevaluación (5%)")
    nota_ser_comportamiento = models.FloatField(default=0.0, verbose_name="Comportamiento (5%)")
    
    nota = models.FloatField(default=0.0, verbose_name="Nota Periodo")
    periodo = models.CharField(max_length=10, choices=PERIODOS, default="1", verbose_name="Periodo")
    fecha = models.DateField(auto_now_add=True, verbose_name="Fecha")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")

    class Meta:
        verbose_name = "Calificación"
        verbose_name_plural = "Calificaciones"
        unique_together = ('estudiante', 'curso_materia', 'periodo')
        ordering = ['-fecha']

    def __str__(self):
        nombre = self.estudiante.usuario.get_full_name() or self.estudiante.usuario.username
        materia = self.curso_materia.materia.nombre if self.curso_materia else '?'
        return f"{nombre} - {materia}: {self.nota}"

    def recalcular_promedios(self):
        """Calcula los promedios de Saber y Hacer basados en NotaActividad"""
        from django.db.models import Avg
        
        # Promedio SABER
        avg_saber = NotaActividad.objects.filter(
            estudiante=self.estudiante,
            actividad__curso_materia=self.curso_materia,
            actividad__periodo=self.periodo,
            actividad__tipo='SABER'
        ).aggregate(Avg('nota'))['nota__avg']
        self.nota_saber_acumulada = round(avg_saber, 2) if avg_saber is not None else 0.0
        
        # Promedio HACER
        avg_hacer = NotaActividad.objects.filter(
            estudiante=self.estudiante,
            actividad__curso_materia=self.curso_materia,
            actividad__periodo=self.periodo,
            actividad__tipo='HACER'
        ).aggregate(Avg('nota'))['nota__avg']
        self.nota_hacer = round(avg_hacer, 2) if avg_hacer is not None else 0.0
        
        self.save()

    def save(self, *args, **kwargs):
        # La nota del periodo es ingresada directamente por el docente.
        # Si no hay nota directa pero sí hay sub-notas heredadas, calculamos como fallback.
        # En el nuevo flujo simplificado el docente sólo ingresa `nota` por periodo.
        super().save(*args, **kwargs)

    @property
    def materia(self):
        """Propiedad de conveniencia para acceder a la materia"""
        return self.curso_materia.materia


class Asistencia(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='asistencias', verbose_name="Estudiante")
    curso_materia = models.ForeignKey('academico.CursoMateria', on_delete=models.CASCADE, null=True, blank=True, related_name='asistencias', verbose_name="Materia")
    fecha = models.DateField(verbose_name="Fecha")
    asistio = models.BooleanField(default=True, verbose_name="Asistió")
    observacion = models.TextField(blank=True, verbose_name="Observación")

    class Meta:
        verbose_name = "Asistencia"
        verbose_name_plural = "Asistencias"
        ordering = ['-fecha']
        unique_together = ('estudiante', 'curso_materia', 'fecha')

    def __str__(self):
        nombre = self.estudiante.usuario.get_full_name() or self.estudiante.usuario.username
        return f"{nombre} - {self.fecha}"

class DocumentoEstudiante(models.Model):
    TIPOS_DOCUMENTO = (
        ('cedula', 'Cédula'),
        ('certificado_nacimiento', 'Certificado de Nacimiento'),
        ('certificado_notas', 'Certificado de Notas'),
        ('foto', 'Fotografía'),
        ('otro', 'Otro'),
    )
    
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='documentos', verbose_name="Estudiante")
    tipo = models.CharField(max_length=30, choices=TIPOS_DOCUMENTO, verbose_name="Tipo de Documento")
    archivo = models.FileField(upload_to='documentos_estudiantes/', verbose_name="Archivo")
    descripcion = models.CharField(max_length=200, blank=True, verbose_name="Descripción")
    fecha_carga = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Carga")

    class Meta:
        verbose_name = "Documento de Estudiante"
        verbose_name_plural = "Documentos de Estudiantes"
        ordering = ['-fecha_carga']

    def __str__(self):
        return f"{self.estudiante.usuario.get_full_name()} - {self.get_tipo_display()}"


class Disciplina(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='disciplinas', verbose_name="Estudiante")
    periodo = models.CharField(max_length=2, choices=[('1','Periodo 1'),('2','Periodo 2'),('3','Periodo 3'),('4','Periodo 4')], verbose_name="Periodo")
    anio_lectivo = models.PositiveIntegerField(default=2026, verbose_name="Año Lectivo")
    nota = models.DecimalField(max_digits=3, decimal_places=1, default=5.0, verbose_name="Calificación Disciplinaria")
    observacion = models.TextField(blank=True, verbose_name="Observación Disciplinaria")

    class Meta:
        verbose_name = "Disciplina"
        verbose_name_plural = "Disciplinas"
        unique_together = ('estudiante', 'periodo', 'anio_lectivo')
        ordering = ['estudiante', 'periodo']

    def __str__(self):
        return f"{self.estudiante} - P{self.periodo} ({self.nota})"
