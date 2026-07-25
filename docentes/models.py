from django.db import models
from django.conf import settings
from academico.models import Curso, Materia

class Docente(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='perfil_docente')
    especialidad = models.CharField(max_length=100)
    titulo = models.CharField(max_length=100)

    def __str__(self):
        return self.usuario.get_full_name() or self.usuario.username

    def display_name(self):
        return self.usuario.get_full_name() or self.usuario.username

    def get_asignaciones(self):
        """Retorna las materias y cursos asignados a este docente"""
        from academico.models import CursoMateria
        return CursoMateria.objects.filter(docente=self).select_related('curso', 'materia')
