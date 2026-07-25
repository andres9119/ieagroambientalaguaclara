from django.urls import path
from .views import PreinscripcionView

urlpatterns = [
    path('', PreinscripcionView.as_view(), name='admisiones'),
]
