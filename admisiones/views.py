from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import PreinscripcionForm
from .models import Preinscripcion

class PreinscripcionView(CreateView):
    model = Preinscripcion
    form_class = PreinscripcionForm
    template_name = 'admisiones/formulario.html'
    success_url = reverse_lazy('admisiones')

    def form_valid(self, form):
        messages.success(self.request, 'Tu solicitud de preinscripción ha sido enviada correctamente.')
        return super().form_valid(form)
