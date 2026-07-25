from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.db.models import Q, Count
from academico.models import Curso, Materia, Sede
from docentes.models import Docente
from estudiantes.models import Estudiante

User = get_user_model()

class CustomLoginView(LoginView):
    template_name = 'usuarios/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        if getattr(user, 'must_change_password', False):
            return reverse_lazy('password_change')
        return reverse_lazy('dashboard')

class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'usuarios/password_change.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        user = self.request.user
        if hasattr(user, 'must_change_password') and user.must_change_password:
            user.must_change_password = False
            user.save()
        messages.success(self.request, 'ContraseÃ±a cambiada exitosamente.')
        return super().form_valid(form)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'usuarios/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['rol'] = user.rol

        if user.rol == 'admin' or user.is_superuser:
            context['total_estudiantes'] = Estudiante.objects.filter(usuario__rol='estudiante').count()
            context['total_docentes'] = Docente.objects.count()
            context['total_cursos'] = Curso.objects.count()
            context['total_materias'] = Materia.objects.count()

        if user.rol == 'estudiante':
            if hasattr(user, 'perfil_estudiante'):
                context['perfil'] = user.perfil_estudiante
        elif user.rol == 'docente':
            if hasattr(user, 'perfil_docente'):
                context['perfil'] = user.perfil_docente

        return context


class DashboardPagoCertificadoView(LoginRequiredMixin, TemplateView):
    template_name = 'usuarios/dashboard.html'

    def get(self, request, *args, **kwargs):
        if not (request.user.rol == 'admin' or request.user.is_superuser):
            return redirect('dashboard')
        q = request.GET.get('q', '').strip()
        if not q:
            return redirect('dashboard')

        estudiante = Estudiante.objects.filter(
            Q(usuario__username__icontains=q) |
            Q(usuario__first_name__icontains=q) |
            Q(usuario__last_name__icontains=q)
        ).select_related('usuario').first()

        if not estudiante:
            messages.error(request, 'Estudiante no encontrado.')
            return redirect('dashboard')

        mat = estudiante.matriculas.filter(activo=True).first()
        context = self.get_context_data()
        context['resultado_pago'] = {
            'id': estudiante.id,
            'nombre': estudiante.usuario.get_full_name() or estudiante.usuario.username,
            'documento': estudiante.usuario.username,
            'tipo_doc': estudiante.get_tipo_documento_display(),
            'curso': mat.curso.nombre if mat else 'Sin Curso',
            'pagado': estudiante.pago_certificado,
        }
        return render(request, self.template_name, context)


class DashboardSedeView(LoginRequiredMixin, TemplateView):
    template_name = 'usuarios/dashboard_sede.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sedes'] = Sede.objects.annotate(
            total_cursos=Count('cursos'),
        ).order_by('nombre')

        sede_id = self.request.GET.get('sede')
        context['sede_seleccionada'] = None

        if sede_id:
            try:
                sede = Sede.objects.get(id=sede_id)
                context['sede_seleccionada'] = sede
                cursos = Curso.objects.filter(sede=sede)
                context['cursos_sede'] = cursos
                estudiantes_ids = Estudiante.objects.filter(
                    matriculas__curso__in=cursos,
                    matriculas__activo=True
                ).values_list('id', flat=True).distinct()
                context['total_estudiantes_sede'] = estudiantes_ids.count()
                docentes_ids = Curso.objects.filter(
                    sede=sede
                ).values_list('curso_materias__docente_id', flat=True).distinct()
                context['total_docentes_sede'] = Docente.objects.filter(id__in=docentes_ids).count()
            except (ValueError, Sede.DoesNotExist):
                pass

        return context


def toggle_pago_certificado(request, pk):


    if not (request.user.is_authenticated and (request.user.rol == 'admin' or request.user.is_superuser)):
        return redirect('dashboard')

    if request.method == 'POST':
        estudiante = get_object_or_404(Estudiante, pk=pk)
        estudiante.pago_certificado = not estudiante.pago_certificado
        estudiante.save()
        estado = 'bloqueado' if not estudiante.pago_certificado else 'habilitado'
        messages.success(request, f'Certificado {estado} para {estudiante.usuario.get_full_name() or estudiante.usuario.username}.')

    return redirect('dashboard')
