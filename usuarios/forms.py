from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class UsuarioChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'telefono', 'direccion', 'foto']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
        }
