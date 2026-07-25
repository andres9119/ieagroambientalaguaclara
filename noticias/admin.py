from django.contrib import admin
from .models import Noticia

@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha_publicacion', 'tiene_imagen')
    list_filter = ('fecha_publicacion',)
    search_fields = ('titulo', 'contenido')
    date_hierarchy = 'fecha_publicacion'
    
    def tiene_imagen(self, obj):
        return "✓" if obj.imagen else "✗"
    tiene_imagen.short_description = 'Imagen'
