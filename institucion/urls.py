from django.urls import path
from .views import (
    InstitucionView, PoliticaPrivacidadView, DocumentosListView,
    GenerarCertificadoEstudiosPDF, VerificarCertificadoView
)

urlpatterns = [
    path('', InstitucionView.as_view(), name='institucion'),
    path('politica-privacidad/', PoliticaPrivacidadView.as_view(), name='politica_privacidad'),
    path('documentos/', DocumentosListView.as_view(), name='documentos'),
    path('documentos/certificado/', GenerarCertificadoEstudiosPDF.as_view(), name='generar_certificado_estudios_pdf'),
    path('certificados/verificar/', VerificarCertificadoView.as_view(), name='verificar_certificado'),
]
