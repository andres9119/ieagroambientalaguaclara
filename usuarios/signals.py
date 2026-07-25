from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from docentes.models import Docente
from estudiantes.models import Estudiante

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.rol == 'docente':
            Docente.objects.create(usuario=instance, especialidad="General", titulo="Licenciado")
        elif instance.rol == 'estudiante':
            # Note: Estudiante requires fields like fecha_nacimiento which we can't guess.
            # We'll create it with defaults and let them update it, or handle it in the form.
            # For now, we'll use a dummy date to avoid errors.
            Estudiante.objects.create(usuario=instance, fecha_nacimiento="2000-01-01", acudiente="Por definir")

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    if instance.rol == 'docente':
        if hasattr(instance, 'perfil_docente'):
            instance.perfil_docente.save()
    elif instance.rol == 'estudiante':
        if hasattr(instance, 'perfil_estudiante'):
            instance.perfil_estudiante.save()
