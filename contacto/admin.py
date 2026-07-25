from django.contrib import admin
from .models import MensajeContacto

class MensajeContactoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'asunto', 'fecha_envio', 'leido')
    list_filter = ('leido', 'fecha_envio')

admin.site.register(MensajeContacto, MensajeContactoAdmin)
