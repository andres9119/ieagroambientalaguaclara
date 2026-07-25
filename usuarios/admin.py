from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Notificacion

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'rol', 'is_staff', 'is_active')
    list_filter = ('rol', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Información Colombia', {'fields': ('rol', 'telefono', 'direccion', 'foto')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('rol', 'telefono', 'direccion', 'foto')}),
    )
    search_fields = ('username', 'first_name', 'last_name', 'email')

admin.site.register(Usuario, CustomUserAdmin)

@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'mensaje', 'leido', 'fecha_creacion')
    list_filter = ('leido', 'fecha_creacion')
    search_fields = ('usuario__username', 'mensaje')
