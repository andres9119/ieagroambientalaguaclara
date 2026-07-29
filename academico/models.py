from django.db import models
from django.conf import settings


class Sede(models.Model):
    nombre = models.CharField(max_length=200, unique=True, verbose_name="Nombre de la Sede")
    codigo_dane = models.CharField(max_length=50, blank=True, verbose_name="Código DANE")
    zona = models.CharField(max_length=50, blank=True, verbose_name="Zona", help_text="Rural / Urbana")
    direccion = models.TextField(blank=True, verbose_name="Dirección")

    class Meta:
        verbose_name = "Sede"
        verbose_name_plural = "Sedes"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Curso(models.Model):
    nombre = models.CharField(max_length=50, verbose_name="Grado")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    nivel = models.CharField(max_length=50, verbose_name="Nivel")
    tutor = models.ForeignKey('docentes.Docente', on_delete=models.SET_NULL, null=True, blank=True, related_name='cursos_tutor', verbose_name="Titular del Curso")
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE, related_name='cursos', null=True, blank=True, verbose_name="Sede")
    hora_inicio_jornada = models.TimeField(null=True, blank=True, verbose_name="Hora de inicio de jornada")
    hora_fin_jornada = models.TimeField(null=True, blank=True, verbose_name="Hora de fin de jornada")
    duracion_clase = models.PositiveSmallIntegerField(default=50, verbose_name="Duración de clase (minutos)", help_text="Ej: 45, 50 o 60 minutos")
    duracion_descanso = models.PositiveSmallIntegerField(default=10, verbose_name="Duración del descanso (minutos)")
    num_descansos = models.PositiveSmallIntegerField(default=2, verbose_name="Número de descansos")
    descanso1_min = models.PositiveSmallIntegerField(default=10, verbose_name="Duración descanso 1 (min)")
    descanso2_min = models.PositiveSmallIntegerField(default=10, verbose_name="Duración descanso 2 (min)")
    descanso3_min = models.PositiveSmallIntegerField(default=30, verbose_name="Duración descanso 3 (min)")

    class Meta:
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"
        ordering = ['nombre']
        unique_together = ('nombre', 'sede')

    def __str__(self):
        sede_str = f" - {self.sede.nombre}" if self.sede else ""
        return f"{self.nombre}{sede_str}"
    
    def get_materias(self):
        """Retorna todas las materias asignadas a este curso"""
        return self.curso_materias.select_related('materia', 'docente__usuario')
    
    def get_estudiantes_count(self):
        """Retorna el número de estudiantes matriculados actualmente en este curso"""
        return self.matriculas.filter(activo=True).count()

class Materia(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre de la Materia")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    creditos = models.PositiveIntegerField(default=1, verbose_name="Créditos")
    area = models.CharField(max_length=50, blank=True, verbose_name="Área", help_text="Ej: Ciencias, Humanidades, Artes")
    docentes = models.ManyToManyField('docentes.Docente', blank=True, related_name='materias', verbose_name="Docentes")

    class Meta:
        verbose_name = "Materia"
        verbose_name_plural = "Materias"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class CursoMateria(models.Model):
    """Relación entre Curso y Materia, con docente asignado"""
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='curso_materias', verbose_name="Curso")
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name='materia_cursos', verbose_name="Materia")
    docente = models.ForeignKey('docentes.Docente', on_delete=models.SET_NULL, null=True, blank=True, related_name='asignaciones', verbose_name="Docente Asignado")
    horas_semanales = models.PositiveIntegerField(default=2, verbose_name="Horas Semanales")
    periodo_academico = models.CharField(max_length=20, default="1", verbose_name="Periodo")
    anio_lectivo = models.PositiveIntegerField(default=2026, verbose_name="Año Lectivo")
    objetivo_p1 = models.TextField(blank=True, verbose_name="Objetivo Periodo 1")
    objetivo_p2 = models.TextField(blank=True, verbose_name="Objetivo Periodo 2")
    objetivo_p3 = models.TextField(blank=True, verbose_name="Objetivo Periodo 3")
    objetivo_p4 = models.TextField(blank=True, verbose_name="Objetivo Periodo 4")

    class Meta:
        unique_together = ('curso', 'materia', 'periodo_academico', 'anio_lectivo')
        verbose_name = "Materia del Curso"
        verbose_name_plural = "Materias de los Cursos"
        ordering = ['curso', 'materia']

    def __str__(self):
        docente_nombre = self.docente.usuario.get_full_name() if self.docente else "Sin asignar"
        return f"{self.curso} - {self.materia} ({docente_nombre})"
    
    def get_estudiantes(self):
        """Retorna todos los estudiantes matriculados en este curso para su año lectivo"""
        from estudiantes.models import Estudiante
        return Estudiante.objects.filter(
            matriculas__curso=self.curso,
            matriculas__anio_lectivo=self.anio_lectivo,
            matriculas__activo=True
        )


DIAS_CICLO = [
    ('1', 'Día 1'),
    ('2', 'Día 2'),
    ('3', 'Día 3'),
    ('4', 'Día 4'),
    ('5', 'Día 5'),
]


class Horario(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, null=True, blank=True, related_name='horarios', verbose_name="Curso")
    curso_materia = models.ForeignKey(CursoMateria, on_delete=models.CASCADE, null=True, blank=True, related_name='horarios', verbose_name="Materia del Curso")
    es_descanso = models.BooleanField(default=False, verbose_name="Es descanso")
    dia = models.CharField(max_length=10, choices=DIAS_CICLO, verbose_name="Día")
    hora_inicio = models.TimeField(verbose_name="Hora de Inicio")
    hora_fin = models.TimeField(verbose_name="Hora de Fin")
    aula = models.CharField(max_length=100, blank=True, verbose_name="Aula / Salón")

    class Meta:
        verbose_name = "Horario"
        verbose_name_plural = "Horarios"
        ordering = ['dia', 'hora_inicio']

    def __str__(self):
        return f"{self.curso_materia} - {self.get_dia_display()} {self.hora_inicio}-{self.hora_fin}"
