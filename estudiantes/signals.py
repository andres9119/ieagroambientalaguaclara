from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Estudiante, Calificacion, Matricula, PERIODOS
from academico.models import CursoMateria

@receiver(post_save, sender=Matricula)
def inicializar_boletin_matricula(sender, instance, created, **kwargs):
    """
    Cuando un estudiante se matricula en un curso para un año lectivo,
    creamos automáticamente los registros de Calificacion para todas
    las materias de ese curso en ese año lectivo y para los 4 periodos.
    """
    if created and instance.activo:
        # Buscar las materias asignadas a este curso para el mismo año lectivo
        materias_curso = CursoMateria.objects.filter(
            curso=instance.curso, 
            anio_lectivo=instance.anio_lectivo
        )
        for cm in materias_curso:
            for p_code, p_nombre in PERIODOS:
                Calificacion.objects.get_or_create(
                    estudiante=instance.estudiante,
                    curso_materia=cm,
                    periodo=p_code
                )

@receiver(post_save, sender=CursoMateria)
def inicializar_boletin_nueva_materia(sender, instance, created, **kwargs):
    """
    Cuando se asigna una nueva materia a un curso (CursoMateria),
    creamos los registros de Calificacion para todos los estudiantes
    matriculados en ese curso para ese año lectivo.
    """
    if created:
        matriculas = Matricula.objects.filter(
            curso=instance.curso, 
            anio_lectivo=instance.anio_lectivo,
            activo=True
        )
        for mat in matriculas:
            for p_code, p_nombre in PERIODOS:
                Calificacion.objects.get_or_create(
                    estudiante=mat.estudiante,
                    curso_materia=instance,
                    periodo=p_code
                )
