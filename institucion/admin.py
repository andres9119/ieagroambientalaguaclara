from django.contrib import admin
from .models import InformacionInstitucional, PilarEducativo, DocumentoInteres, CertificadoEmitido

@admin.register(DocumentoInteres)
class DocumentoInteresAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria', 'fecha_publicacion', 'publico')
    list_filter = ('categoria', 'publico')
    search_fields = ('titulo',)

@admin.register(InformacionInstitucional)
class InformacionInstitucionalAdmin(admin.ModelAdmin):
    list_display = ('nombre_colegio', 'dane', 'nit', 'lema')
    fieldsets = (
        ('Identificación', {
            'fields': ('nombre_colegio', 'dane', 'nit', 'resolucion', 'lema')
        }),
        ('Ubicación', {
            'fields': ('departamento', 'municipio', 'sede_principal')
        }),
        ('Información Académica', {
            'fields': ('calendario', 'jornada', 'horario')
        }),
        ('Rectoría', {
            'fields': ('nombre_rector', 'rector_cc', 'foto_rector', 'mensaje_rectoria')
        }),
        ('Documentos', {
            'fields': ('codigo_documento', 'version_documento')
        }),
        ('Contenido Institucional', {
            'fields': ('historia', 'foto_historia', 'mision', 'vision', 'valores')
        }),
        ('Privacidad', {
            'fields': ('politica_privacidad', 'aviso_privacidad_corto')
        }),
    )

@admin.register(PilarEducativo)
class PilarEducativoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'orden')
    ordering = ('orden',)

@admin.register(CertificadoEmitido)
class CertificadoEmitidoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'estudiante_nombre', 'grado', 'anio', 'fecha_emision', 'valido')
    list_filter = ('valido', 'anio')
    search_fields = ('codigo', 'estudiante_nombre', 'estudiante_documento')
    readonly_fields = ('codigo', 'estudiante_nombre', 'estudiante_documento', 'tipo_documento', 'grado', 'nivel', 'anio', 'sede', 'fecha_emision')
