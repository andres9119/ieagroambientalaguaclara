from django.contrib import admin
from .models import Docente
from academico.models import CursoMateria

@admin.register(Docente)
class DocenteAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'especialidad', 'titulo')
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name', 'especialidad')
    autocomplete_fields = ['usuario']
