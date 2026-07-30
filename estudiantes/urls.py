from django.urls import path
from .views import MisNotasView, MiAsistenciaView, MiHorarioView, RealizarAutoevaluacionView, GenerarBoletinPDF
from . import views

urlpatterns = [
    path('mis-notas/', MisNotasView.as_view(), name='mis_notas'),
    path('autoevaluacion/<int:pk>/', RealizarAutoevaluacionView.as_view(), name='realizar_autoevaluacion'),
    path('mi-asistencia/', MiAsistenciaView.as_view(), name='mi_asistencia'),
    path('mi-horario/', MiHorarioView.as_view(), name='mi_horario'),
    path('descargar-boletin/', GenerarBoletinPDF.as_view(), name='generar_boletin_pdf'),
    path('matricular/', views.matricular_estudiante, name='matricular_estudiante'),
    path('lista/', views.EstudianteListView.as_view(), name='estudiantes_list'),
    path('por-curso/', views.EstudiantesPorCursoView.as_view(), name='estudiantes_por_curso'),
    path('por-curso/<int:curso_id>/', views.EstudiantesCursoDetailView.as_view(), name='estudiantes_por_curso_detalle'),
    path('<int:pk>/editar/', views.EstudianteUpdateView.as_view(), name='estudiante_editar'),
    path('<int:pk>/eliminar/', views.eliminar_estudiante, name='eliminar_estudiante'),
    path('importar-excel/', views.importar_estudiantes_excel_view, name='importar_estudiantes_excel'),
]
