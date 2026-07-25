from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.urls import path
from django.db.models import Count, Q
from .models import Estudiante, Calificacion, Asistencia, DocumentoEstudiante, Matricula
from academico.models import Curso

User = get_user_model()


class CalificacionInline(admin.TabularInline):
    model = Calificacion
    extra = 1


class DocumentoInline(admin.TabularInline):
    model = DocumentoEstudiante
    extra = 1


class EstudianteForm(forms.ModelForm):
    class Meta:
        model = Estudiante
        fields = '__all__'
        widgets = {
            'direccion': forms.Textarea(attrs={'rows': 2}),
        }

    numero_documento = forms.CharField(
        max_length=150, label='N° Documento',
        widget=forms.TextInput(attrs={'class': 'vTextField'})
    )
    primer_nombre = forms.CharField(
        max_length=150, label='Primer Nombre', required=False,
        widget=forms.TextInput(attrs={'class': 'vTextField'})
    )
    segundo_nombre = forms.CharField(
        max_length=150, label='Segundo Nombre', required=False,
        widget=forms.TextInput(attrs={'class': 'vTextField'})
    )
    primer_apellido = forms.CharField(
        max_length=150, label='Primer Apellido', required=False,
        widget=forms.TextInput(attrs={'class': 'vTextField'})
    )
    segundo_apellido = forms.CharField(
        max_length=150, label='Segundo Apellido', required=False,
        widget=forms.TextInput(attrs={'class': 'vTextField'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            user = self.instance.usuario
            names = (user.first_name or '').strip().split()
            lastnames = (user.last_name or '').strip().split()
            self.fields['numero_documento'].initial = user.username
            self.fields['primer_nombre'].initial = names[0] if len(names) > 0 else ''
            self.fields['segundo_nombre'].initial = names[1] if len(names) > 1 else ''
            self.fields['primer_apellido'].initial = lastnames[0] if len(lastnames) > 0 else ''
            self.fields['segundo_apellido'].initial = lastnames[1] if len(lastnames) > 1 else ''

    def save(self, commit=True):
        instance = super().save(commit=False)
        old_username = instance.usuario.username
        new_username = self.cleaned_data['numero_documento']
        instance.usuario.username = new_username
        if new_username != old_username:
            instance.usuario.set_password(f'{new_username}*')
        p_nombre = self.cleaned_data.get('primer_nombre', '') or ''
        s_nombre = self.cleaned_data.get('segundo_nombre', '') or ''
        p_apellido = self.cleaned_data.get('primer_apellido', '') or ''
        s_apellido = self.cleaned_data.get('segundo_apellido', '') or ''
        instance.usuario.first_name = f'{p_nombre} {s_nombre}'.strip()
        instance.usuario.last_name = f'{p_apellido} {s_apellido}'.strip()
        if commit:
            instance.usuario.save()
            instance.save()
        return instance


@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    form = EstudianteForm
    inlines = [DocumentoInline]

    list_display = ('get_documento', 'get_nombre_completo', 'tipo_documento', 'get_curso_actual', 'acudiente', 'pago_certificado')
    list_editable = ('pago_certificado',)
    list_per_page = 25
    list_filter = (('matriculas__curso', admin.RelatedOnlyFieldListFilter), 'tipo_documento')
    search_fields = ('usuario__first_name', 'usuario__last_name', 'usuario__username')
    autocomplete_fields = ['usuario']
    list_select_related = ('usuario',)

    def get_curso_actual(self, obj):
        mat = obj.matriculas.filter(activo=True).first()
        return mat.curso.nombre if mat else '—'
    get_curso_actual.short_description = 'Curso'
    get_curso_actual.admin_order_field = 'matriculas__curso'
    fieldsets = (
        (None, {'fields': ('usuario',)}),
        ('Información Personal', {
            'fields': (
                'tipo_documento', 'fecha_nacimiento', 'genero', 'rh',
                'lugar_nacimiento', 'direccion', 'barrio',
                'telefono', 'celular', 'eps', 'estrato',
                'nui', 'etnia', 'discapacidad', 'jornada', 'zona',
                'pais_origen', 'estado_matricula', 'modelo_educativo',
                'fuente_recursos', 'campesino', 'categoria_aula',
            ),
        }),
        ('Pago', {'fields': ('pago_certificado',),
                   'description': 'Desmarque para bloquear la descarga de certificados al estudiante. Por defecto todos tienen acceso.'}),
        ('Datos del Usuario', {
            'fields': ('numero_documento', 'primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido'),
            'description': 'Estos campos modifican los datos del Usuario asociado (cuenta de inicio de sesión).'
        }),
    )

    def get_documento(self, obj):
        return obj.usuario.username
    get_documento.short_description = 'N° Documento'
    get_documento.admin_order_field = 'usuario__username'

    def get_nombre_completo(self, obj):
        return obj.usuario.get_full_name() or obj.usuario.username
    get_nombre_completo.short_description = 'Nombre Completo'
    get_nombre_completo.admin_order_field = 'usuario__first_name'

    def get_promedio_display(self, obj):
        return f'{obj.get_promedio():.2f}'
    get_promedio_display.short_description = 'Promedio'

    def get_asistencia_display(self, obj):
        return f'{obj.get_porcentaje_asistencia():.1f}%'
    get_asistencia_display.short_description = 'Asistencia'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('por-curso/', self.admin_site.admin_view(self.curso_list_view), name='estudiantes_por_curso'),
            path('por-curso/<int:curso_id>/', self.admin_site.admin_view(self.curso_detail_view), name='estudiantes_por_curso_detalle'),
        ]
        return custom_urls + urls

    def curso_list_view(self, request):
        cursos = Curso.objects.annotate(
            total_estudiantes=Count('matriculas', filter=Q(matriculas__activo=True))
        ).order_by('nombre')

        stats = []
        for c in cursos:
            stats.append({
                'id': c.id,
                'nombre': c.nivel + ' - ' + c.nombre if c.nivel else c.nombre,
                'total': c.total_estudiantes,
                'tutor': str(c.tutor) if c.tutor else '—',
            })

        context = {
            'title': 'Estudiantes por Curso',
            'cursos': stats,
            'opts': self.model._meta,
            'app_label': self.model._meta.app_label,
            'has_view_permission': self.has_view_permission(request),
        }
        return render(request, 'admin/estudiantes_por_curso.html', context)

    def curso_detail_view(self, request, curso_id):
        curso = Curso.objects.get(id=curso_id)
        qs = Estudiante.objects.filter(matriculas__curso=curso, matriculas__activo=True)

        search_query = request.GET.get('q', '').strip()
        if search_query:
            qs = qs.filter(
                Q(usuario__first_name__icontains=search_query) |
                Q(usuario__last_name__icontains=search_query) |
                Q(usuario__username__icontains=search_query)
            )

        estudiantes = []
        for e in qs:
            estudiantes.append({
                'id': e.id,
                'documento': e.usuario.username,
                'nombre': e.usuario.get_full_name() or e.usuario.username,
                'tipo_doc': e.get_tipo_documento_display(),
                'telefono': e.telefono or e.celular,
                'acudiente': e.acudiente,
                'promedio': e.get_promedio(),
            })

        context = {
            'title': f'Estudiantes de {curso.nombre}',
            'curso': curso,
            'estudiantes': estudiantes,
            'search_query': search_query,
            'opts': self.model._meta,
            'app_label': self.model._meta.app_label,
            'has_change_permission': self.has_change_permission(request),
        }
        return render(request, 'admin/estudiantes_por_curso_detalle.html', context)

@admin.register(Calificacion)
class CalificacionAdmin(admin.ModelAdmin):
    list_display = ('get_estudiante_nombre', 'get_materia', 'get_curso', 'nota', 'periodo', 'fecha')
    list_filter = (('curso_materia__materia', admin.RelatedOnlyFieldListFilter), 'periodo', 'fecha')
    search_fields = ('estudiante__usuario__first_name', 'estudiante__usuario__last_name', 'estudiante__usuario__username')
    list_select_related = ('estudiante__usuario', 'curso_materia__materia', 'curso_materia__curso')

    def get_estudiante_nombre(self, obj):
        nombre = obj.estudiante.usuario.get_full_name() or obj.estudiante.usuario.username
        return nombre
    get_estudiante_nombre.short_description = 'Estudiante'
    get_estudiante_nombre.admin_order_field = 'estudiante__usuario__first_name'

    def get_materia(self, obj):
        return obj.curso_materia.materia.nombre
    get_materia.short_description = 'Materia'
    get_materia.admin_order_field = 'curso_materia__materia'

    def get_curso(self, obj):
        return obj.curso_materia.curso.nombre
    get_curso.short_description = 'Curso'
    get_curso.admin_order_field = 'curso_materia__curso'


@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    list_display = ('get_estudiante_nombre', 'fecha', 'asistio', 'observacion')
    list_filter = ('asistio', 'fecha')
    search_fields = ('estudiante__usuario__first_name', 'estudiante__usuario__last_name', 'estudiante__usuario__username')
    list_select_related = ('estudiante__usuario',)

    def get_estudiante_nombre(self, obj):
        nombre = obj.estudiante.usuario.get_full_name() or obj.estudiante.usuario.username
        return nombre
    get_estudiante_nombre.short_description = 'Estudiante'
    get_estudiante_nombre.admin_order_field = 'estudiante__usuario__first_name'


@admin.register(DocumentoEstudiante)
class DocumentoEstudianteAdmin(admin.ModelAdmin):
    list_display = ('get_estudiante_nombre', 'tipo', 'descripcion', 'fecha_carga')
    list_filter = ('tipo', 'fecha_carga')
    search_fields = ('estudiante__usuario__first_name', 'estudiante__usuario__last_name', 'estudiante__usuario__username', 'descripcion')
    readonly_fields = ('fecha_carga',)
    list_select_related = ('estudiante__usuario',)

    def get_estudiante_nombre(self, obj):
        nombre = obj.estudiante.usuario.get_full_name() or obj.estudiante.usuario.username
        return nombre
    get_estudiante_nombre.short_description = 'Estudiante'
    get_estudiante_nombre.admin_order_field = 'estudiante__usuario__first_name'


@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ('get_estudiante_nombre', 'curso', 'anio_lectivo', 'activo', 'fecha_matricula')
    list_filter = ('curso', 'anio_lectivo', 'activo')
    search_fields = ('estudiante__usuario__first_name', 'estudiante__usuario__last_name', 'estudiante__usuario__username')
    autocomplete_fields = ['estudiante', 'curso']
    list_select_related = ('estudiante__usuario', 'curso')

    def get_estudiante_nombre(self, obj):
        nombre = obj.estudiante.usuario.get_full_name() or obj.estudiante.usuario.username
        return nombre
    get_estudiante_nombre.short_description = 'Estudiante'
    get_estudiante_nombre.admin_order_field = 'estudiante__usuario__first_name'
