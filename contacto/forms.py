from django import forms
from .models import MensajeContacto

class ContactoForm(forms.ModelForm):
    class Meta:
        model = MensajeContacto
        fields = ['nombre', 'email', 'asunto', 'mensaje', 'acepta_politica']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'asunto': forms.TextInput(attrs={'class': 'form-control'}),
            'mensaje': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.urls import reverse
        from django.utils.safestring import mark_safe
        url_politica = reverse('politica_privacidad')
        self.fields['acepta_politica'].label = mark_safe(
            f'Autorizo el tratamiento de mis datos personales de acuerdo con la <a href="{url_politica}" target="_blank">Política de Privacidad</a>.'
        )
        self.fields['acepta_politica'].required = True
