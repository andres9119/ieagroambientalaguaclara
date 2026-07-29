from django.urls import path
from . import views
from .views import MisCursosView, actividades_lista, actividad_crear, actividad_calificar, crear_docente
from .views import DocenteListView, DocenteUpdateView, eliminar_docente

urlpatterns = [
    path('mis-cursos/', MisCursosView.as_view(), name='mis_cursos'),
    path('asignacion/<int:asignacion_id>/notas/', views.gestionar_notas, name='gestionar_notas'),
    path('notas/exportar/<int:asignacion_id>/', views.exportar_notas_csv, name='exportar_notas_csv'),
    path('crear-docente/', crear_docente, name='crear_docente'),
    path('lista-docentes/', DocenteListView.as_view(), name='docentes_list'),
    path('docente/<int:pk>/editar/', DocenteUpdateView.as_view(), name='docente_editar'),
    path('docente/<int:pk>/eliminar/', eliminar_docente, name='eliminar_docente'),
    path('asignacion/<int:asignacion_id>/panel/', views.panel_control_curso, name='panel_control_curso'),
    path('asignacion/<int:asignacion_id>/calificar/', views.calificar_periodos, name='calificar_periodos'),
    path('asignacion/<int:asignacion_id>/asistencia/', views.gestionar_asistencia, name='gestionar_asistencia'),
    path('actividades/<int:asignacion_id>/', actividades_lista, name='actividades_lista'),
    path('actividades/crear/<int:asignacion_id>/', actividad_crear, name='actividad_crear'),
    path('actividades/calificar/<int:actividad_id>/', actividad_calificar, name='actividad_calificar'),
    path('curso/<int:curso_id>/disciplina/', views.calificar_disciplina, name='calificar_disciplina'),
]
