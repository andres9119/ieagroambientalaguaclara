from django.db import models

class MensajeContacto(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre Completo")
    email = models.EmailField(verbose_name="Correo Electrónico")
    asunto = models.CharField(max_length=200, verbose_name="Asunto")
    mensaje = models.TextField(verbose_name="Mensaje")
    fecha_envio = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)
    acepta_politica = models.BooleanField(default=False, verbose_name="Autorización Tratamiento de Datos")

    def __str__(self):
        return f"{self.nombre} - {self.asunto}"
