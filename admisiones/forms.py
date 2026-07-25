from django import forms
from .models import Preinscripcion

class PreinscripcionForm(forms.ModelForm):
    class Meta:
        model = Preinscripcion
        fields = ['nombre_aspirante', 'fecha_nacimiento', 'grado_interes', 
                  'nombre_acudiente', 'telefono_contacto', 'email_contacto', 
                  'observaciones_solicitante', 'acepta_politica',
                  'doc_identidad', 'recibo_servicios', 'certificado_sisben', 'certificados_academicos']
        widgets = {
            'nombre_aspirante': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo del estudiante'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'grado_interes': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('', 'Seleccione un grado'),
                ('Preescolar', 'Preescolar'),
                ('1° Primaria', '1° Primaria'),
                ('2° Primaria', '2° Primaria'),
                ('3° Primaria', '3° Primaria'),
                ('4° Primaria', '4° Primaria'),
                ('5° Primaria', '5° Primaria'),
                ('6° Bachillerato', '6° Bachillerato'),
                ('7° Bachillerato', '7° Bachillerato'),
                ('8° Bachillerato', '8° Bachillerato'),
                ('9° Bachillerato', '9° Bachillerato'),
                ('10° Bachillerato', '10° Bachillerato'),
                ('11° Bachillerato', '11° Bachillerato'),
            ]),
            'nombre_acudiente': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo del padre/madre/acudiente'}),
            'telefono_contacto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 300 123 4567'}),
            'email_contacto': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'observaciones_solicitante': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Si desea agregar alguna información adicional, puede hacerlo aquí (opcional)'
            }),
            'doc_identidad': forms.FileInput(attrs={'class': 'form-control'}),
            'recibo_servicios': forms.FileInput(attrs={'class': 'form-control'}),
            'certificado_sisben': forms.FileInput(attrs={'class': 'form-control'}),
            'certificados_academicos': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.urls import reverse
        from django.utils.safestring import mark_safe
        url_politica = reverse('politica_privacidad')
        self.fields['acepta_politica'].label = mark_safe(
            f'Autorizo el tratamiento de mis datos personales y del aspirante de acuerdo con la <a href="{url_politica}" target="_blank">Política de Privacidad</a>.'
        )
        self.fields['acepta_politica'].required = True
    
    def clean_fecha_nacimiento(self):
        """Valida que el aspirante tenga una edad razonable"""
        from datetime import date
        fecha = self.cleaned_data['fecha_nacimiento']
        today = date.today()
        edad = today.year - fecha.year - ((today.month, today.day) < (fecha.month, fecha.day))
        
        if edad < 3:
            raise forms.ValidationError("El aspirante debe tener al menos 3 años de edad.")
        if edad > 20:
            raise forms.ValidationError("Por favor verifique la fecha de nacimiento ingresada.")
        
        return fecha
