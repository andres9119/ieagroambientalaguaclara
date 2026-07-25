from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    ROLES = (
        ('admin', 'Administrador'),
        ('docente', 'Docente'),
        ('estudiante', 'Estudiante'),
    )
    rol = models.CharField(max_length=20, choices=ROLES, default='estudiante')
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    foto = models.ImageField(upload_to='usuarios/', blank=True, null=True)
    must_change_password = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_superuser and self.rol != 'admin':
            self.rol = 'admin'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} - {self.get_rol_display()}"

class Notificacion(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='notificaciones')
    mensaje = models.CharField(max_length=255)
    link = models.CharField(max_length=255, blank=True, null=True)
    leido = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.usuario.username}: {self.mensaje[:30]}..."
