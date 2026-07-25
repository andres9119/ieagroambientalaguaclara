from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import CustomLoginView, CustomPasswordChangeView, DashboardView, DashboardPagoCertificadoView, DashboardSedeView, toggle_pago_certificado
from .views_profile import EditarPerfilView

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='inicio'), name='logout'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('dashboard/sedes/', DashboardSedeView.as_view(), name='dashboard_sedes'),
    path('dashboard/pago-certificado/', DashboardPagoCertificadoView.as_view(), name='dashboard_pago_certificado'),
    path('dashboard/pago-certificado/<int:pk>/toggle/', toggle_pago_certificado, name='toggle_pago_certificado'),
    path('perfil/', EditarPerfilView.as_view(), name='perfil'),
    path('password-change/', CustomPasswordChangeView.as_view(), name='password_change'),

]

