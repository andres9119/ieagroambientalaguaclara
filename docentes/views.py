import csv
from django.http import HttpResponse
from django.views.generic import ListView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django import forms
from django.forms import modelformset_factory
from django.utils import timezone
from django.urls import reverse_lazy, reverse
from .models import Docente
from django.contrib.auth import get_user_model
from .forms import ActividadForm, DocenteEditForm
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django import forms as djforms

def crear_docente(request):
    if not (request.user.is_authenticated and (request.user.rol == 'admin' or request.user.is_superuser)):
        return redirect('dashboard')

    from .forms import DocenteCreateForm
    User = get_user_model()

    if request.method == 'POST':
        form = DocenteCreateForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            username = data['username']
            password = data['password'] or User.objects.make_random_password()
            user = User.objects.create_user(username=username, email=data.get('email',''))
            user.first_name = data.get('first_name','')
            user.last_name = data.get('last_name','')
            user.set_password(password)
            user.rol = 'docente'
            user.must_change_password = True
            user.save()

            docente = Docente.objects.create(usuario=user, especialidad=data.get('especialidad',''), titulo=data.get('titulo',''))
            messages.success(request, f'Docente {user.get_full_name() or user.username} creado. Usuario: {username}')
            return redirect('dashboard')
        else:
            messages.error(request, 'Corrija los errores en el formulario.')
    else:
        form = DocenteCreateForm()

    return render(request, 'docentes/crear_docente.html', {'form': form})
from academico.models import Curso, CursoMateria
from estudiantes.models import Calificacion, Estudiante, Asistencia, Actividad, NotaActividad, Disciplina

def actividades_lista(request, asignacion_id):
    """Lista las actividades (Saber/Hacer) de una materia y periodo"""
    asignacion = get_object_or_404(CursoMateria, id=asignacion_id, docente__usuario=request.user)
    periodo = request.GET.get('periodo', '1')
    actividades = Actividad.objects.filter(curso_materia=asignacion, periodo=periodo)
    
    return render(request, 'docentes/actividades_lista.html', {
        'asignacion': asignacion,
        'actividades': actividades,
        'periodo': periodo
    })

def actividad_crear(request, asignacion_id):
    """Crea una nueva actividad (Saber/Hacer)"""
    asignacion = get_object_or_404(CursoMateria, id=asignacion_id, docente__usuario=request.user)
    periodo = request.GET.get('periodo', '1')
    
    if request.method == 'POST':
        form = ActividadForm(request.POST)
        if form.is_valid():
            actividad = form.save(commit=False)
            actividad.curso_materia = asignacion
            actividad.save()
            messages.success(request, f'Actividad "{actividad.nombre}" creada.')
            return redirect(f"{reverse_lazy('actividades_lista', kwargs={'asignacion_id': asignacion_id})}?periodo={actividad.periodo}")
    else:
        form = ActividadForm(initial={'periodo': periodo})
        
    return render(request, 'docentes/actividad_form.html', {
        'form': form,
        'asignacion': asignacion,
        'titulo': 'Crear Actividad'
    })

def actividad_calificar(request, actividad_id):
    """Califica a todos los estudiantes en una actividad específica"""
    actividad = get_object_or_404(Actividad, id=actividad_id, curso_materia__docente__usuario=request.user)
    # Filtrar estudiantes matriculados en el curso y año de la actividad
    estudiantes = Estudiante.objects.filter(
        matriculas__curso=actividad.curso_materia.curso,
        matriculas__anio_lectivo=actividad.curso_materia.anio_lectivo,
        matriculas__activo=True
    ).select_related('usuario')
    
    # Asegurar que existan registros de nota
    for est in estudiantes:
        NotaActividad.objects.get_or_create(actividad=actividad, estudiante=est)
        
    NotaFormSet = modelformset_factory(
        NotaActividad,
        fields=('nota',),
        extra=0,
        widgets={'nota': forms.NumberInput(attrs={'class': 'form-control text-center fw-bold', 'step': '0.1', 'min': '0', 'max': '5'})}
    )
    
    queryset = NotaActividad.objects.filter(actividad=actividad).select_related('estudiante__usuario').order_by('estudiante__usuario__first_name')
    
    if request.method == 'POST':
        formset = NotaFormSet(request.POST, queryset=queryset)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Calificaciones guardadas correctamente.')
            return redirect(f"{reverse_lazy('actividades_lista', kwargs={'asignacion_id': actividad.curso_materia.id})}?periodo={actividad.periodo}")
    else:
        formset = NotaFormSet(queryset=queryset)
        
    return render(request, 'docentes/actividad_calificar.html', {
        'actividad': actividad,
        'formset': formset
    })


from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

class MisCursosView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = CursoMateria
    template_name = 'docentes/mis_cursos.html'
    context_object_name = 'asignaciones'

    def test_func(self):
        return self.request.user.rol == 'docente' or self.request.user.is_superuser

    def get_queryset(self):
        if not hasattr(self.request.user, 'perfil_docente'):
            return CursoMateria.objects.none()
        return CursoMateria.objects.filter(
            docente=self.request.user.perfil_docente
        ).select_related('curso', 'materia').order_by('curso__nombre', 'materia__nombre')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Group asignaciones by curso for the accordion view
        from collections import OrderedDict
        from estudiantes.models import Calificacion, Estudiante, Disciplina
        
        cursos_dict = OrderedDict()
        for asig in self.get_queryset():
            curso = asig.curso
            if curso.id not in cursos_dict:
                num_estudiantes = Estudiante.objects.filter(
                    matriculas__curso=curso,
                    matriculas__anio_lectivo=asig.anio_lectivo,
                    matriculas__activo=True
                ).count()
                cursos_dict[curso.id] = {
                    'curso': curso,
                    'anio_lectivo': asig.anio_lectivo,
                    'num_estudiantes': num_estudiantes,
                    'materias': []
                }
            # Count how many students have at least one grade in any period
            total_notas = Calificacion.objects.filter(
                curso_materia=asig,
                nota__gt=0
            ).count()
            porcentaje = 0
            n_est = cursos_dict[curso.id]['num_estudiantes']
            if n_est > 0:
                # Max possible = 4 periods × n_estudiantes
                porcentaje = min(100, round((total_notas / (n_est * 4)) * 100))
            cursos_dict[curso.id]['materias'].append({
                'asignacion': asig,
                'total_notas': total_notas,
                'progreso': porcentaje,
            })

        context['cursos_agrupados'] = list(cursos_dict.values())
        context['total_cursos'] = len(cursos_dict)
        context['total_materias'] = sum(len(c['materias']) for c in cursos_dict.values())

        # Cursos donde el docente es titular
        if hasattr(self.request.user, 'perfil_docente'):
            context['cursos_titular'] = Curso.objects.filter(
                tutor=self.request.user.perfil_docente
            ).select_related('sede')
        else:
            context['cursos_titular'] = Curso.objects.none()
        return context

def gestionar_notas(request, asignacion_id):
    """Resumen de notas y gestión de Saber Final, Comportamiento y Autoevaluación"""
    asignacion = get_object_or_404(
        CursoMateria.objects.select_related('curso', 'materia'), 
        id=asignacion_id, 
        docente__usuario=request.user
    )
    
    estudiantes = Estudiante.objects.filter(
        matriculas__curso=asignacion.curso,
        matriculas__anio_lectivo=asignacion.anio_lectivo,
        matriculas__activo=True
    ).select_related('usuario')
    periodo = request.GET.get('periodo', '1')
    
    # Asegurar que existan registros de calificación y que los promedios estén al día
    for estudiante in estudiantes:
        calif, created = Calificacion.objects.get_or_create(
            estudiante=estudiante,
            curso_materia=asignacion,
            periodo=periodo
        )
        calif.recalcular_promedios()

    # FormSet para los campos que el docente sí gestiona aquí (Final y Comportamiento)
    CalificacionFormSet = modelformset_factory(
        Calificacion, 
        fields=('nota_saber_final', 'nota_ser_comportamiento', 'observaciones'), 
        extra=0,
        widgets={
            'nota_saber_final': forms.NumberInput(attrs={'class': 'form-control form-control-sm text-center fw-bold', 'step': '0.1', 'min': '0', 'max': '5'}),
            'nota_ser_comportamiento': forms.NumberInput(attrs={'class': 'form-control form-control-sm text-center fw-bold', 'step': '0.1', 'min': '0', 'max': '5'}),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control form-control-sm',
                'rows': '1',
                'placeholder': 'Comentario...'
            })
        }
    )

    queryset = Calificacion.objects.filter(
        curso_materia=asignacion,
        periodo=periodo
    ).select_related('estudiante__usuario').order_by('estudiante__usuario__first_name', 'estudiante__usuario__last_name')

    if request.method == 'POST':
        formset = CalificacionFormSet(request.POST, queryset=queryset)
        if formset.is_valid():
            formset.save()
            messages.success(request, f'Consolidado guardado para el período {periodo}.')
            return redirect('mis_cursos')
    else:
        formset = CalificacionFormSet(queryset=queryset)

    return render(request, 'docentes/gestionar_notas.html', {
        'asignacion': asignacion,
        'formset': formset,
        'periodo': periodo
    })

def panel_control_curso(request, asignacion_id):
    """
    Panel unificado para gestionar notas por periodos y asistencia.
    Redirige al nuevo sistema simplificado de calificación por periodos.
    """
    return redirect(f"{reverse('calificar_periodos', args=[asignacion_id])}")


from django.contrib.auth.decorators import login_required, user_passes_test

def is_docente(user):
    return user.is_authenticated and (user.rol == 'docente' or user.is_superuser)

@login_required
@user_passes_test(is_docente)
def calificar_periodos(request, asignacion_id):
    """
    Vista simplificada: el docente ingresa UNA nota por estudiante por cada periodo académico.
    Muestra todos los estudiantes en una tabla con columnas P1, P2, P3, P4.
    """
    asignacion = get_object_or_404(
        CursoMateria.objects.select_related('curso', 'materia'),
        id=asignacion_id,
        docente__usuario=request.user
    )

    PERIODOS = ['1', '2', '3', '4']

    estudiantes = Estudiante.objects.filter(
        matriculas__curso=asignacion.curso,
        matriculas__anio_lectivo=asignacion.anio_lectivo,
        matriculas__activo=True
    ).select_related('usuario').order_by('usuario__first_name', 'usuario__last_name')

    # Asegurar que existan registros de calificación para todos los periodos
    for estudiante in estudiantes:
        for periodo in PERIODOS:
            Calificacion.objects.get_or_create(
                estudiante=estudiante,
                curso_materia=asignacion,
                periodo=periodo
            )

    if request.method == 'POST':
        errores = False

        for periodo in PERIODOS:
            campo_obj = f"objetivo_p{periodo}"
            obj_val = request.POST.get(campo_obj, '').strip()
            setattr(asignacion, f'objetivo_p{periodo}', obj_val)
        asignacion.save()

        for estudiante in estudiantes:
            for periodo in PERIODOS:
                campo = f"nota_{estudiante.id}_{periodo}"
                campo_obs = f"obs_{estudiante.id}_{periodo}"
                valor = request.POST.get(campo, '').strip()
                observacion = request.POST.get(campo_obs, '').strip()
                if valor:
                    try:
                        nota_val = float(valor)
                        nota_val = max(0.0, min(5.0, round(nota_val, 2)))
                        calif = Calificacion.objects.get(
                            estudiante=estudiante,
                            curso_materia=asignacion,
                            periodo=periodo
                        )
                        calif.nota = nota_val
                        if observacion:
                            calif.observaciones = observacion
                        calif.save()
                    except (ValueError, Calificacion.DoesNotExist):
                        errores = True

        if not errores:
            messages.success(request, f'Calificaciones de {asignacion.materia.nombre} guardadas correctamente.')
        else:
            messages.warning(request, 'Algunas notas no pudieron guardarse. Verifica los valores ingresados.')
        return redirect(reverse('calificar_periodos', args=[asignacion_id]))

    # Construir tabla de datos para el template
    tabla = []
    for estudiante in estudiantes:
        row = {'estudiante': estudiante, 'cols': []}
        for periodo in PERIODOS:
            try:
                calif = Calificacion.objects.get(
                    estudiante=estudiante,
                    curso_materia=asignacion,
                    periodo=periodo
                )
            except Calificacion.DoesNotExist:
                calif = None
            row['cols'].append({'periodo': periodo, 'calif': calif})
        # Promedio anual: suma de las 4 notas / 4
        notas = [c['calif'].nota for c in row['cols'] if c['calif'] and c['calif'].nota > 0]
        row['promedio_anual'] = round(sum(notas) / 4, 2) if notas else 0.0
        tabla.append(row)

    return render(request, 'docentes/calificar_periodos.html', {
        'asignacion': asignacion,
        'tabla': tabla,
        'periodos': PERIODOS,
    })

@login_required
@user_passes_test(is_docente)
def gestionar_asistencia(request, asignacion_id):
    """Gestiona la asistencia de los estudiantes del curso"""
    asignacion = get_object_or_404(
        CursoMateria.objects.select_related('curso', 'materia'),
        id=asignacion_id, 
        docente__usuario=request.user
    )
    
    # Fecha actual y cálculo de la semana (Lunes a Viernes)
    hoy = timezone.now().date()
    fecha_str = request.GET.get('fecha', hoy.isoformat())
    fecha_seleccionada = timezone.datetime.strptime(fecha_str, '%Y-%m-%d').date()
    
    # Calcular lunes de la semana actual
    lunes = fecha_seleccionada - timezone.timedelta(days=fecha_seleccionada.weekday())
    semana = []
    nombres_dias = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie']
    for i in range(5):
        dia = lunes + timezone.timedelta(days=i)
        semana.append({
            'fecha': dia.isoformat(),
            'nombre': nombres_dias[i],
            'numero': dia.day,
            'activa': dia == fecha_seleccionada
        })

    estudiantes = Estudiante.objects.filter(
        matriculas__curso=asignacion.curso,
        matriculas__anio_lectivo=asignacion.anio_lectivo,
        matriculas__activo=True
    ).select_related('usuario')
    
    # Crear registros por defecto como 'Presente' (asistio=True)
    for estudiante in estudiantes:
        Asistencia.objects.get_or_create(
            estudiante=estudiante,
            curso_materia=asignacion,
            fecha=fecha_seleccionada,
            defaults={'asistio': True}
        )

    AsistenciaFormSet = modelformset_factory(
        Asistencia, 
        fields=('asistio', 'observacion'), 
        extra=0,
        widgets={
            'asistio': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observacion': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Nota...'})
        }
    )

    queryset = Asistencia.objects.filter(
        curso_materia=asignacion,
        fecha=fecha_seleccionada
    ).select_related('estudiante__usuario').order_by('estudiante__usuario__first_name', 'estudiante__usuario__last_name')

    if request.method == 'POST':
        formset = AsistenciaFormSet(request.POST, queryset=queryset)
        if formset.is_valid():
            formset.save()
            messages.success(request, f'Asistencia del {fecha_str} guardada correctamente.')
            return redirect('mis_cursos')
    else:
        formset = AsistenciaFormSet(queryset=queryset)

    return render(request, 'docentes/gestionar_asistencia.html', {
        'asignacion': asignacion,
        'formset': formset,
        'fecha': fecha_str,
        'semana': semana,
        'hoy': hoy.isoformat()
    })

def exportar_notas_csv(request, asignacion_id):
    """Exporta las notas del curso y periodo a un archivo CSV"""
    asignacion = get_object_or_404(CursoMateria, id=asignacion_id, docente__usuario=request.user)
    periodo = request.GET.get('periodo', '1')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="notas_{asignacion.materia.nombre}_{asignacion.curso.nombre}_P{periodo}.csv"'
    
    # Escribir con codificación para Excel
    response.write(u'\ufeff'.encode('utf8'))
    writer = csv.writer(response)
    writer.writerow(['Estudiante', 'Saber Acum. (25%)', 'Saber Final (20%)', 'Hacer (45%)', 'Ser Auto (5%)', 'Ser Compor. (5%)', 'Total'])
    
    calificaciones = Calificacion.objects.filter(
        curso_materia=asignacion, 
        periodo=periodo
    ).select_related('estudiante__usuario').order_by('estudiante__usuario__first_name')
    
    for c in calificaciones:
        writer.writerow([
            c.estudiante.display_name,
            c.nota_saber_acumulada,
            c.nota_saber_final,
            c.nota_hacer,
            c.nota_ser_auto,
            c.nota_ser_comportamiento,
            c.nota
        ])
    
    return response


class DocenteListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Docente
    template_name = 'docentes/docentes_list.html'
    context_object_name = 'docentes'

    def test_func(self):
        return self.request.user.rol == 'admin' or self.request.user.is_superuser


class DocenteUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Docente
    form_class = DocenteEditForm
    template_name = 'docentes/docente_form.html'

    def get_success_url(self):
        return reverse('docentes_list')

    def test_func(self):
        return self.request.user.rol == 'admin' or self.request.user.is_superuser

    def form_invalid(self, form):
        from django.contrib import messages
        messages.error(self.request, 'Corrija los errores en el formulario.')
        return super().form_invalid(form)


@login_required
@user_passes_test(lambda u: u.is_authenticated and (u.rol == 'admin' or u.is_superuser))
def eliminar_docente(request, pk):
    docente = get_object_or_404(Docente, pk=pk)
    nombre = docente.usuario.get_full_name() or docente.usuario.username
    if request.method == 'POST':
        docente.usuario.delete()
        messages.success(request, f'Docente "{nombre}" eliminado correctamente.')
        return redirect('docentes_list')
    return render(request, 'academico/confirmar_eliminar.html', {
        'object': docente,
        'titulo': 'Eliminar Docente',
        'mensaje': f'¿Estás seguro de eliminar al docente "{nombre}"? También se eliminará su usuario.',
        'cancelar_url': 'docentes_list',
    })

@login_required
def calificar_disciplina(request, curso_id):
    if not (request.user.rol == 'docente' or request.user.is_superuser):
        return HttpResponse("No autorizado", status=403)

    curso = get_object_or_404(Curso.objects.filter(tutor__usuario=request.user), id=curso_id)
    anio = timezone.now().year
    periodo = request.GET.get('periodo', '1')

    estudiantes = Estudiante.objects.filter(
        matriculas__curso=curso, matriculas__anio_lectivo=anio, matriculas__activo=True
    ).select_related('usuario').order_by('usuario__first_name', 'usuario__last_name')

    for e in estudiantes:
        Disciplina.objects.get_or_create(
            estudiante=e, periodo=periodo, anio_lectivo=anio,
            defaults={'nota': 5.0}
        )

    if request.method == 'POST':
        for e in estudiantes:
            d, _ = Disciplina.objects.get_or_create(
                estudiante=e, periodo=periodo, anio_lectivo=anio
            )
            nota = request.POST.get(f'nota_{e.id}', '').strip()
            obs = request.POST.get(f'obs_{e.id}', '').strip()
            if nota:
                try:
                    d.nota = max(1.0, min(5.0, float(nota)))
                except ValueError:
                    pass
            if obs:
                d.observacion = obs
            d.save()
        messages.success(request, f'Disciplina guardada para {curso.nombre} - Periodo {periodo}.')
        return redirect('mis_cursos')

    disc_map = {d.estudiante_id: d for d in Disciplina.objects.filter(estudiante__in=estudiantes, periodo=periodo, anio_lectivo=anio)}
    filas = [{'estudiante': e, 'disciplina': disc_map.get(e.id)} for e in estudiantes]

    return render(request, 'docentes/calificar_disciplina.html', {
        'curso': curso,
        'filas': filas,
        'periodo': periodo,
        'anio': anio,
    })

