from django.urls import path
from .views import InfoAcademicaView, exportar_estudiantes_excel
from .views import CrearCursoView, CrearMateriaView
from .views import CursoListView, CursoUpdateView, MateriaListView, MateriaUpdateView
from . import views

urlpatterns = [
    path('info-academica/', InfoAcademicaView.as_view(), name='info_academica'),
    path('exportar-estudiantes/', exportar_estudiantes_excel, name='exportar_estudiantes'),
    path('crear-curso/', CrearCursoView.as_view(), name='crear_curso'),
    path('crear-materia/', CrearMateriaView.as_view(), name='crear_materia'),
    path('cursos/', CursoListView.as_view(), name='cursos_list'),
    path('curso/<int:pk>/editar/', CursoUpdateView.as_view(), name='curso_editar'),
    path('materias/', MateriaListView.as_view(), name='materias_list'),
    path('materia/<int:pk>/editar/', MateriaUpdateView.as_view(), name='materia_editar'),
    path('curso/<int:curso_id>/asignar-docentes/', views.asignar_docentes_curso, name='asignar_docentes_curso'),
    path('curso/<int:curso_id>/promocionar/', views.promocionar_curso, name='promocionar_curso'),
    path('curso/<int:curso_id>/horarios/', views.horarios_curso, name='horarios_curso'),
]
