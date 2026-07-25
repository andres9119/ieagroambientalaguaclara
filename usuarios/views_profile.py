from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Usuario
from .forms import UsuarioChangeForm

class EditarPerfilView(LoginRequiredMixin, UpdateView):
    model = Usuario
    form_class = UsuarioChangeForm
    template_name = 'usuarios/perfil.html'
    success_url = reverse_lazy('perfil')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Tu perfil ha sido actualizado correctamente.')
        return super().form_valid(form)
