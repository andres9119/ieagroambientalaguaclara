from django.db import models
from django.conf import settings
from django.utils import timezone

class Preinscripcion(models.Model):
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
        ('aplazado', 'Aplazado'),
    )
    
    # Información del Aspirante
    nombre_aspirante = models.CharField(max_length=200, verbose_name="Nombre del Aspirante")
    fecha_nacimiento = models.DateField(verbose_name="Fecha de Nacimiento")
    grado_interes = models.CharField(max_length=50, verbose_name="Grado de Interés")
    
    # Información del Acudiente
    nombre_acudiente = models.CharField(max_length=200, verbose_name="Nombre del Acudiente")
    telefono_contacto = models.CharField(max_length=20, verbose_name="Teléfono de Contacto")
    email_contacto = models.EmailField(verbose_name="Correo Electrónico")
    
    # Gestión Administrativa
    fecha_solicitud = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Solicitud")
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente', verbose_name="Estado")
    fecha_revision = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Revisión")
    revisado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Revisado por"
    )
    notas_internas = models.TextField(blank=True, verbose_name="Notas Internas", help_text="Observaciones del administrador")
    motivo_rechazo = models.TextField(blank=True, verbose_name="Motivo de Rechazo")
    observaciones_solicitante = models.TextField(blank=True, verbose_name="Observaciones del Solicitante")
    acepta_politica = models.BooleanField(default=False, verbose_name="Autorización Tratamiento de Datos")
    
    # Documentos Adjuntos
    doc_identidad = models.FileField(upload_to='admisiones/documentos/', blank=True, null=True, verbose_name="Documento de Identidad", help_text="Copia del documento de identidad del aspirante")
    recibo_servicios = models.FileField(upload_to='admisiones/documentos/', blank=True, null=True, verbose_name="Recibo de Servicios Públicos", help_text="Copia de un recibo reciente de servicios públicos")
    certificado_sisben = models.FileField(upload_to='admisiones/documentos/', blank=True, null=True, verbose_name="Certificado SISBEN", help_text="Certificado si aplica")
    certificados_academicos = models.FileField(upload_to='admisiones/documentos/', blank=True, null=True, verbose_name="Certificados Académicos", help_text="Último boletín o certificado de notas")

    class Meta:
        verbose_name = "Preinscripción"
        verbose_name_plural = "Preinscripciones"
        ordering = ['-fecha_solicitud']

    def __str__(self):
        return f"{self.nombre_aspirante} - {self.grado_interes}"
    
    def puede_ser_revisada(self):
        """Verifica si la solicitud puede ser revisada (solo si está pendiente)"""
        return self.estado == 'pendiente'
    
    def marcar_como_aprobada(self, usuario, notas=""):
        """Marca la solicitud como aprobada"""
        if self.puede_ser_revisada():
            self.estado = 'aprobado'
            self.fecha_revision = timezone.now()
            self.revisado_por = usuario
            if notas:
                self.notas_internas = notas
            self.save()
            return True
        return False
    
    def marcar_como_rechazada(self, usuario, motivo=""):
        """Marca la solicitud como rechazada"""
        if self.puede_ser_revisada():
            self.estado = 'rechazado'
            self.fecha_revision = timezone.now()
            self.revisado_por = usuario
            self.motivo_rechazo = motivo
            self.save()
            return True
        return False
    
    def marcar_como_aplazada(self, usuario, notas=""):
        """Marca la solicitud como aplazada"""
        if self.puede_ser_revisada():
            self.estado = 'aplazado'
            self.fecha_revision = timezone.now()
            self.revisado_por = usuario
            if notas:
                self.notas_internas = notas
            self.save()
            return True
        return False
    
    def get_edad(self):
        """Calcula la edad del aspirante"""
        from datetime import date
        today = date.today()
        return today.year - self.fecha_nacimiento.year - ((today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
    
    def get_estado_color(self):
        """Retorna el color asociado al estado"""
        colores = {
            'pendiente': '#ffc107',  # Amarillo
            'aprobado': '#28a745',   # Verde
            'rechazado': '#dc3545',  # Rojo
            'aplazado': '#6c757d',   # Gris
        }
        return colores.get(self.estado, '#6c757d')
