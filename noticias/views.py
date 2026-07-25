from django.views.generic import ListView, DetailView
from .models import Noticia

class NoticiaListView(ListView):
    model = Noticia
    template_name = 'noticias/lista.html'
    context_object_name = 'noticias'
    ordering = ['-fecha_publicacion']

class NoticiaDetailView(DetailView):
    model = Noticia
    template_name = 'noticias/detalle.html'
    context_object_name = 'noticia'
