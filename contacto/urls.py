from django.urls import path
from .views import ContactoView

urlpatterns = [
    path('', ContactoView.as_view(), name='contacto'),
]
