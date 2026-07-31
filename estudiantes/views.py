from pathlib import Path
from django.views.generic import ListView, UpdateView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from .models import Calificacion, Asistencia, NotaActividad, PERIODOS, Disciplina
from .forms import AutoevaluacionForm, EstudianteEditForm
from .utils import render_to_pdf
from .forms import MatricularEstudianteForm
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_http_methods
from academico.models import Curso
from .models import Estudiante, Matricula
from django.db import IntegrityError, transaction
from django.db.models import Count, Q


class EstudianteListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Estudiante
    template_name = 'estudiantes/estudiantes_list.html'
    context_object_name = 'estudiantes'

    def test_func(self):
        return self.request.user.rol == 'admin' or self.request.user.is_superuser


class EstudianteUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Estudiante
    form_class = EstudianteEditForm
    template_name = 'estudiantes/estudiante_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['usuario'] = self.object.usuario
        mat = self.object.matriculas.filter(activo=True).first()
        context['curso_actual'] = f'{mat.curso.nombre} / {mat.curso.nivel}' if mat else '—'
        context['curso_id'] = self.request.GET.get('curso', '')
        return context

    def get_success_url(self):
        curso_id = self.request.GET.get('curso')
        if curso_id:
            return reverse_lazy('estudiantes_por_curso_detalle', kwargs={'curso_id': curso_id})
        return reverse_lazy('estudiantes_por_curso')

    def test_func(self):
        return self.request.user.rol == 'admin' or self.request.user.is_superuser

    def form_invalid(self, form):
        messages.error(self.request, 'Corrija los errores en el formulario.')
        return super().form_invalid(form)


class EstudiantesPorCursoView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'estudiantes/estudiantes_por_curso.html'
    context_object_name = 'cursos'

    def test_func(self):
        return self.request.user.rol == 'admin' or self.request.user.is_superuser

    def get_jornada(self):
        return self.request.GET.get('jornada', '')

    def get_queryset(self):
        qs = Curso.objects.annotate(
            total_estudiantes=Count('matriculas', filter=Q(matriculas__activo=True))
        )
        jornada = self.get_jornada()
        if jornada == 'FIN_DE_SEMANA':
            qs = qs.filter(nombre__regex=r'^2\d{3}$')
        else:
            qs = qs.exclude(nombre__regex=r'^2\d{3}$')
        return qs.order_by('nombre')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['jornada_activa'] = self.get_jornada()
        return ctx


class EstudiantesCursoDetailView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return (self.request.user.rol == 'admin' or
                self.request.user.is_superuser or
                (self.request.user.rol == 'docente' and
                 hasattr(self.request.user, 'perfil_docente') and
                 Curso.objects.filter(tutor=self.request.user.perfil_docente).exists()))

    def get(self, request, curso_id):
        curso = get_object_or_404(Curso, id=curso_id)
        if request.user.rol == 'docente' and curso.tutor != getattr(request.user, 'perfil_docente', None):
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden("No autorizado")
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
                'acudiente': e.acudiente,
                'promedio': e.get_promedio(),
            })

        return render(request, 'estudiantes/estudiantes_por_curso_detalle.html', {
            'curso': curso,
            'estudiantes': estudiantes,
            'search_query': search_query,
        })


@require_http_methods(["GET", "POST"])
def matricular_estudiante(request):
    if not (request.user.is_authenticated and (request.user.rol == 'admin' or request.user.is_superuser)):
        return redirect('dashboard')

    if request.method == 'POST':
        form = MatricularEstudianteForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            User = get_user_model()
            username = data['documento']
            password = f"{data['documento']}*"
            try:
                with transaction.atomic():
                    existing_user = User.objects.filter(username=username).first()
                    if existing_user:
                        user = existing_user
                        # update basic info and password
                        user.first_name = data['first_name']
                        user.last_name = data['last_name']
                        user.set_password(password)
                        user.rol = 'estudiante'
                        user.must_change_password = True
                        user.save()
                    else:
                        user = User.objects.create_user(username=username)
                        user.first_name = data['first_name']
                        user.last_name = data['last_name']
                        user.set_password(password)
                        user.rol = 'estudiante'
                        user.must_change_password = True
                        user.save()

                    # Ensure Estudiante exists (signals may have created a stub); update or create accordingly
                    estudiante, est_created = Estudiante.objects.get_or_create(
                        usuario=user,
                        defaults={
                            'fecha_nacimiento': data['fecha_nacimiento'],
                            'acudiente': data['acudiente'],
                            'tipo_documento': data.get('tipo_documento', 'TI'),
                            'genero': data.get('genero', ''),
                            'rh': data.get('rh', ''),
                            'eps': data.get('eps', ''),
                            'barrio': data.get('barrio', ''),
                            'estrato': data.get('estrato', ''),
                            'telefono': data.get('telefono', ''),
                            'celular': data.get('celular', ''),
                            'direccion': data.get('direccion', ''),
                            'nui': data.get('nui', ''),
                            'etnia': data.get('etnia', ''),
                            'jornada': data.get('jornada', ''),
                        }
                    )
                    if not est_created:
                        estudiante.fecha_nacimiento = data['fecha_nacimiento']
                        estudiante.acudiente = data['acudiente']
                        for campo in ['tipo_documento', 'genero', 'rh', 'eps', 'barrio', 'estrato', 'telefono', 'celular', 'direccion', 'nui', 'etnia', 'jornada']:
                            val = data.get(campo)
                            if val:
                                setattr(estudiante, campo, val)
                        estudiante.save()

                    # Create matricula only if not exists for same curso and year
                    matricula, mat_created = Matricula.objects.get_or_create(
                        estudiante=estudiante,
                        curso=data['curso'],
                        anio_lectivo=2026,
                        defaults={'activo': True}
                    )
                    if not mat_created:
                        messages.info(request, 'El estudiante ya está matriculado en ese curso/año.')
                        return redirect('estudiantes_list')

                    messages.success(request, f'Estudiante {user.get_full_name() or user.username} matriculado en {data["curso"]}. Usuario: {username}')
                    return redirect('dashboard')
            except IntegrityError as e:
                messages.error(request, f'Error al crear el estudiante: {str(e)}')
                return redirect('matricular_estudiante')
    else:
        form = MatricularEstudianteForm()

    return render(request, 'estudiantes/matricular.html', {'form': form})

class MisNotasView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'estudiantes/mis_notas.html'
    context_object_name = 'boletin'

    def test_func(self):
        return self.request.user.rol == 'estudiante' or self.request.user.is_superuser

    def get_queryset(self):
        return []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self.request.user, 'perfil_estudiante'):
            estudiante = self.request.user.perfil_estudiante
            
            # Obtener las materias asignadas a su curso
            materias_curso = estudiante.get_materias()
            
            boletin = []
            for cm in materias_curso:
                # Obtener todas las calificaciones de la materia para el estudiante
                calificaciones_qs = Calificacion.objects.filter(
                    estudiante=estudiante, 
                    curso_materia=cm
                )
                
                # Mapear por periodo para el template
                c_map = {c.periodo: c for c in calificaciones_qs}
                
                # Detalle de actividades para ver el desglose
                actividades_con_notas = NotaActividad.objects.filter(
                    estudiante=estudiante,
                    actividad__curso_materia=cm
                ).select_related('actividad').order_by('actividad__periodo', 'actividad__tipo')
                
                # Agrupar por periodo
                a_map = {}
                for p_num, p_text in PERIODOS:
                    a_map[p_num] = actividades_con_notas.filter(actividad__periodo=p_num)
                
                # Obtener nota anual usando el nuevo método del modelo
                nota_anual = estudiante.get_nota_anual_materia(cm)
                
                boletin.append({
                    'materia': cm.materia,
                    'curso_materia': cm,
                    'p1': c_map.get('1'),
                    'p2': c_map.get('2'),
                    'p3': c_map.get('3'),
                    'p4': c_map.get('4'),
                    'actividades': a_map,  # Diccionario con listas por periodo
                    'nota_anual': nota_anual,
                    'docente': cm.docente,
                })

            
            context['boletin'] = boletin
            context['estudiante'] = estudiante
        return context

class RealizarAutoevaluacionView(LoginRequiredMixin, UpdateView):
    model = Calificacion
    form_class = AutoevaluacionForm
    template_name = 'estudiantes/autoevaluacion.html'
    success_url = reverse_lazy('mis_notas')

    def get_object(self, queryset=None):
        return get_object_or_404(
            Calificacion, 
            id=self.kwargs['pk'], 
            estudiante__usuario=self.request.user
        )

    def form_valid(self, form):
        messages.success(self.request, "Tu autoevaluación ha sido guardada.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['calificacion'] = self.get_object()
        return context

class MiAsistenciaView(LoginRequiredMixin, ListView):
    model = Asistencia
    template_name = 'estudiantes/mi_asistencia.html'
    context_object_name = 'asistencias'

    def get_queryset(self):
        if not hasattr(self.request.user, 'perfil_estudiante'):
            return Asistencia.objects.none()
        return Asistencia.objects.filter(estudiante=self.request.user.perfil_estudiante).order_by('-fecha')

class MiHorarioView(LoginRequiredMixin, TemplateView):
    template_name = 'estudiantes/mi_horario.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from academico.models import Horario
        DIAS_ORDER = ['1', '2', '3', '4', '5']
        if hasattr(self.request.user, 'perfil_estudiante'):
            est = self.request.user.perfil_estudiante
            mat = est.matriculas.filter(activo=True).first()
            if mat:
                horarios = Horario.objects.filter(curso=mat.curso).select_related(
                    'curso_materia__materia', 'curso_materia__docente__usuario'
                )
                semana = {d: [] for d in DIAS_ORDER}
                for h in horarios:
                    semana[h.dia].append(h)
                for d in DIAS_ORDER:
                    semana[d].sort(key=lambda x: x.hora_inicio)
                ctx['semana'] = semana
                ctx['dias'] = DIAS_ORDER
                ctx['curso'] = mat.curso
        return ctx


def generar_boletin_pdf_estudiante(estudiante, request=None):
    from pathlib import Path
    from institucion.models import InformacionInstitucional
    matricula_activa = estudiante.matriculas.filter(activo=True).first()
    curso = matricula_activa.curso if matricula_activa else None
    curso_nombre = curso.nombre if curso else 'Sin Curso'
    anio_lectivo = matricula_activa.anio_lectivo if matricula_activa else timezone.now().year
    materias_curso = estudiante.get_materias()
    ahora = timezone.now()
    mes = ahora.month
    if 2 <= mes <= 4:
        p_actual = '1'
    elif 5 <= mes <= 7:
        p_actual = '2'
    elif 8 <= mes <= 9:
        p_actual = '3'
    else:
        p_actual = '4'

    def get_escala(nota):
        if nota >= 4.6:
            return 'Superior'
        elif nota >= 4.0:
            return 'Alto'
        elif nota >= 3.0:
            return 'Básico'
        else:
            return 'Bajo'

    area_colors = {
        'TERRITORIO AGROAMBIENTAL': '#2d6a2d',
        'LENGUAJE Y COMUNICACIÓN': '#cc6b2c',
        'ORGANIZACIÓN POLÍTICA Y CULTURA': '#2b5797',
        'CONVIVENCIA': '#8b4513',
    }

    boletin_agrupado = {}
    for cm in materias_curso:
        area_nombre = cm.materia.area.strip().upper() if cm.materia.area else 'OTRAS ÁREAS'
        if area_nombre not in boletin_agrupado:
            boletin_agrupado[area_nombre] = {
                'nombre': area_nombre,
                'color': area_colors.get(area_nombre, '#555555'),
                'materias': [],
            }
        calificaciones_qs = Calificacion.objects.filter(estudiante=estudiante, curso_materia=cm)
        c_map = {c.periodo: c for c in calificaciones_qs}
        nota_anual = estudiante.get_nota_anual_materia(cm)
        faltas_materia = estudiante.asistencias.filter(curso_materia=cm, asistio=False).count()
        obj_text = getattr(cm, f'objetivo_p{p_actual}', '')
        boletin_agrupado[area_nombre]['materias'].append({
            'materia': cm.materia,
            'p1': c_map.get('1'),
            'p2': c_map.get('2'),
            'p3': c_map.get('3'),
            'p4': c_map.get('4'),
            'nota_anual': nota_anual,
            'escala': get_escala(nota_anual),
            'docente': cm.docente,
            'faltas': faltas_materia,
            'obj_periodo': obj_text,
        })

    nombre_completo = f"{estudiante.usuario.first_name} {estudiante.usuario.last_name}".strip()
    if not nombre_completo:
        nombre_completo = estudiante.usuario.username

    fallas_totales = estudiante.asistencias.filter(asistio=False).count()

    escudo_path = str(Path(__file__).resolve().parent.parent / 'static' / 'img' / 'escudo.png')

    info = InformacionInstitucional.objects.first()

    disciplina = None
    if curso:
        try:
            disciplina = Disciplina.objects.get(estudiante=estudiante, periodo=p_actual, anio_lectivo=anio_lectivo)
        except Disciplina.DoesNotExist:
            pass

    data = {
        'info': info,
        'disciplina': disciplina,
        'estudiante': estudiante,
        'nombre_completo': nombre_completo,
        'curso': curso_nombre,
        'nivel': curso.nivel if curso else '',
        'anio': anio_lectivo,
        'boletin_agrupado': list(boletin_agrupado.values()),
        'tipo_documento': estudiante.get_tipo_documento_display(),
        'numero_documento': estudiante.usuario.username,
        'fallas_totales': fallas_totales,
        'fecha': ahora,
        'escudo_path': escudo_path,
        'periodo_actual': f'Periodo {p_actual} - {anio_lectivo}',
        'p_actual': p_actual,
    }

    return render_to_pdf('estudiantes/boletin_pdf.html', data)


class GenerarBoletinPDF(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        puede_ver_todos = request.user.rol in ('admin', 'docente') or request.user.is_superuser

        if puede_ver_todos and request.GET.get('estudiante_id'):
            estudiante = get_object_or_404(Estudiante, id=request.GET['estudiante_id'])
        elif hasattr(request.user, 'perfil_estudiante'):
            estudiante = request.user.perfil_estudiante
        else:
            return redirect('dashboard')

        pdf_response = generar_boletin_pdf_estudiante(estudiante, request)
        if pdf_response:
            filename = f"Boletin_{estudiante.usuario.username}.pdf"
            content = f"inline; filename={filename}"
            pdf_response['Content-Disposition'] = content
            return pdf_response
        return HttpResponse("Error generando PDF", status=400)


from django.contrib.auth.decorators import login_required, user_passes_test

@login_required
@user_passes_test(lambda u: u.is_authenticated and (u.rol == 'admin' or u.is_superuser))
def eliminar_estudiante(request, pk):
    estudiante = get_object_or_404(Estudiante, pk=pk)
    nombre = estudiante.usuario.get_full_name() or estudiante.usuario.username
    if request.method == 'POST':
        estudiante.usuario.delete()
        messages.success(request, f'Estudiante "{nombre}" eliminado correctamente.')
        return redirect('estudiantes_por_curso')
    return render(request, 'academico/confirmar_eliminar.html', {
        'object': estudiante,
        'titulo': 'Eliminar Estudiante',
        'mensaje': f'¿Estás seguro de eliminar al estudiante "{nombre}"? También se eliminará su usuario.',
        'cancelar_url': 'estudiantes_por_curso',
    })

def admin_required(user):
    return user.is_authenticated and (user.rol == 'admin' or user.is_superuser)

@login_required
@user_passes_test(admin_required)
def importar_estudiantes_excel_view(request):
    import tempfile
    import os
    import threading
    from django.conf import settings
    from django.core.management import call_command

    resultado = None
    log_path = os.path.join(settings.BASE_DIR, 'logs', 'importacion_estudiantes.log')

    if request.method == 'POST' and request.FILES.get('archivo'):
        archivo = request.FILES['archivo']
        if not archivo.name.endswith('.xlsx'):
            messages.error(request, 'El archivo debe ser .xlsx')
        else:
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
                    for chunk in archivo.chunks():
                        tmp.write(chunk)
                    tmp_path = tmp.name

                anio = request.POST.get('anio', 2026)
                try:
                    anio = int(anio)
                except ValueError:
                    anio = 2026

                dry_run = bool(request.POST.get('dry_run'))
                os.makedirs(os.path.dirname(log_path), exist_ok=True)

                def run_import():
                    try:
                        with open(log_path, 'w', encoding='utf-8') as f:
                            cmd_args = [tmp_path, '--anio', str(anio)]
                            if dry_run:
                                cmd_args.append('--dry-run')
                            call_command('importar_estudiantes_excel', *cmd_args, stdout=f, stderr=f)
                    finally:
                        try:
                            os.unlink(tmp_path)
                        except OSError:
                            pass

                threading.Thread(target=run_import, daemon=True).start()

                if dry_run:
                    messages.info(request, 'Simulación iniciada en segundo plano. Refresca la página en unos momentos para ver el resultado en el log.')
                else:
                    messages.info(request, 'Importación iniciada en segundo plano. Se importan TODOS los estudiantes o NINGUNO: si hay errores no se guardará ningún dato. Refresca la página en unos momentos para ver el resultado.')
            except Exception as e:
                messages.error(request, f'Error al iniciar la importación: {e}')

    try:
        if os.path.exists(log_path):
            with open(log_path, 'r', encoding='utf-8') as f:
                resultado = f.read()
    except OSError:
        pass

    return render(request, 'estudiantes/importar_excel.html', {
        'resultado': resultado,
    })


def importar_progreso_view(request):
    import os
    from django.http import JsonResponse
    from django.conf import settings

    progreso_path = os.path.join(settings.BASE_DIR, 'logs', 'importacion_progreso.txt')
    running = False
    procesadas = 0
    total = 0
    estado = 'idle'

    try:
        if os.path.exists(progreso_path):
            with open(progreso_path, 'r', encoding='utf-8') as f:
                contenido = f.read().strip()
            if contenido:
                partes = contenido.split(':', 1)
                if len(partes) == 2:
                    estado = partes[0]
                    num = partes[1]
                else:
                    estado = 'procesando'
                    num = contenido
                if '/' in num:
                    p, t = num.split('/', 1)
                    procesadas = int(p or 0)
                    total = int(t or 0)
                running = estado == 'procesando'
    except (OSError, ValueError):
        pass

    return JsonResponse({
        'running': running,
        'estado': estado,
        'procesadas': procesadas,
        'total': total,
    })
