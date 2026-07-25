from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import ContactoForm
from .models import MensajeContacto

class ContactoView(CreateView):
    model = MensajeContacto
    form_class = ContactoForm
    template_name = 'contacto/formulario.html'
    success_url = reverse_lazy('contacto')

    def form_valid(self, form):
        messages.success(self.request, 'Tu mensaje ha sido enviado correctamente.')
        return super().form_valid(form)
