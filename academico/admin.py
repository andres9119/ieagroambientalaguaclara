from django.contrib import admin, messages
from django.shortcuts import render, redirect
from django.urls import path, reverse
from django.db import transaction
from django.utils import timezone
from .models import Curso, Materia, CursoMateria, Sede
from estudiantes.models import Estudiante, Matricula


@admin.register(Sede)
class SedeAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo_dane', 'zona')
    search_fields = ('nombre', 'codigo_dane')


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'nivel', 'sede', 'get_estudiantes_count', 'promocionar_link')
    list_filter = ('nivel', 'sede')
    search_fields = ('nombre', 'descripcion')

    def get_estudiantes_count(self, obj):
        return obj.get_estudiantes_count()
    get_estudiantes_count.short_description = 'Estudiantes'

    def promocionar_link(self, obj):
        url = reverse('admin:promocionar_curso', args=[obj.id])
        return f'<a href="{url}" class="button" style="background:#17a2b8;color:#fff;padding:3px 10px;border-radius:3px;text-decoration:none;">Promocionar</a>'
    promocionar_link.short_description = 'Accion'
    promocionar_link.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:curso_id>/promocionar/', self.admin_site.admin_view(self.promocionar_view), name='promocionar_curso'),
        ]
        return custom_urls + urls

    def promocionar_view(self, request, curso_id):
        curso_origen = Curso.objects.get(id=curso_id)
        cursos_destino = Curso.objects.exclude(id=curso_id).order_by('nivel', 'nombre')
        prox_anio = timezone.now().year + 1

        if request.method == 'POST':
            curso_destino_id = request.POST.get('curso_destino')
            anio_destino = request.POST.get('anio_destino', str(prox_anio))
            desactivar_origen = request.POST.get('desactivar_origen') == 'on'

            if not curso_destino_id:
                messages.error(request, 'Debes seleccionar un curso de destino.')
                return redirect('admin:promocionar_curso', curso_id=curso_id)

            curso_destino = Curso.objects.get(id=curso_destino_id)
            estudiantes = Estudiante.objects.filter(matriculas__curso=curso_origen, matriculas__activo=True)
            count = 0

            with transaction.atomic():
                for e in estudiantes:
                    mat_actual = e.matriculas.filter(curso=curso_origen, activo=True).first()
                    if not mat_actual:
                        continue

                    if desactivar_origen:
                        mat_actual.activo = False
                        mat_actual.save()

                    _, created = Matricula.objects.get_or_create(
                        estudiante=e,
                        curso=curso_destino,
                        anio_lectivo=int(anio_destino),
                        defaults={'activo': True}
                    )
                    if created:
                        count += 1

            messages.success(
                request,
                f'{count} estudiante(s) promocionado(s) de "{curso_origen.nombre}" a "{curso_destino.nombre}" ({anio_destino}).'
            )
            return redirect('admin:academico_curso_changelist')

        estudiantes_count = Estudiante.objects.filter(
            matriculas__curso=curso_origen, matriculas__activo=True
        ).count()

        context = {
            'title': f'Promocionar: {curso_origen.nombre}',
            'curso_origen': curso_origen,
            'cursos_destino': cursos_destino,
            'prox_anio': prox_anio,
            'estudiantes_count': estudiantes_count,
            'opts': self.model._meta,
            'app_label': self.model._meta.app_label,
            'has_change_permission': self.has_change_permission(request),
        }
        return render(request, 'admin/promocionar_curso.html', context)


@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'area', 'creditos')
    list_filter = ('area',)
    search_fields = ('nombre', 'descripcion')


@admin.register(CursoMateria)
class CursoMateriaAdmin(admin.ModelAdmin):
    list_display = ('curso', 'materia', 'docente', 'horas_semanales', 'periodo_academico')
    list_filter = ('curso', 'materia', 'periodo_academico')
    search_fields = ('curso__nombre', 'materia__nombre', 'docente__usuario__first_name', 'docente__usuario__last_name')
    autocomplete_fields = ['curso', 'materia', 'docente']
