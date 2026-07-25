from django import forms
from estudiantes.models import Actividad, NotaActividad
from django.contrib.auth import get_user_model

User = get_user_model()


class ActividadForm(forms.ModelForm):
    class Meta:
        model = Actividad
        fields = ['nombre', 'tipo', 'periodo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Taller 1, Evaluación 2'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'periodo': forms.Select(attrs={'class': 'form-select'}),
        }


class DocenteCreateForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class':'form-control'}))
    first_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={'class':'form-control'}))
    last_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={'class':'form-control'}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class':'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}), required=False)
    telefono = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'class':'form-control'}))

    especialidad = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}))
    titulo = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}))

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('El nombre de usuario ya existe')
        return username
