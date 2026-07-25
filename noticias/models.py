from django.db import models
from django.utils import timezone

class Noticia(models.Model):
    titulo = models.CharField(max_length=200, verbose_name="Título")
    resumen = models.TextField(max_length=300, verbose_name="Resumen", help_text="Breve descripción que aparecerá en el listado", blank=True)
    contenido = models.TextField(verbose_name="Contenido")
    fecha_publicacion = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Publicación")
    imagen = models.ImageField(upload_to='noticias/', blank=True, null=True, verbose_name="Imagen")

    class Meta:
        verbose_name = "Noticia"
        verbose_name_plural = "Noticias"
        ordering = ['-fecha_publicacion']

    def __str__(self):
        return self.titulo
