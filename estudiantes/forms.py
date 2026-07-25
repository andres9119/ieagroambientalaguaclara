from django import forms
from django.contrib.auth import get_user_model
from .models import Calificacion, Estudiante
from academico.models import Curso

User = get_user_model()


class AutoevaluacionForm(forms.ModelForm):
    class Meta:
        model = Calificacion
        fields = ['nota_ser_auto']
        widgets = {
            'nota_ser_auto': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg text-center fw-bold',
                'step': '0.1',
                'min': '0',
                'max': '5',
                'placeholder': '0.0'
            }),
        }
        labels = {
            'nota_ser_auto': 'Tu Calificación (0.0 - 5.0)',
        }


class MatricularEstudianteForm(forms.Form):
    documento = forms.CharField(label='Número de documento', max_length=60, widget=forms.TextInput(attrs={'class':'form-control'}))
    first_name = forms.CharField(label='Nombres', max_length=150, widget=forms.TextInput(attrs={'class':'form-control'}))
    last_name = forms.CharField(label='Apellidos', max_length=150, widget=forms.TextInput(attrs={'class':'form-control'}))
    fecha_nacimiento = forms.DateField(label='Fecha de nacimiento', widget=forms.DateInput(attrs={'class':'form-control','type':'date'}))
    acudiente = forms.CharField(label='Acudiente', max_length=200, widget=forms.TextInput(attrs={'class':'form-control'}))
    curso = forms.ModelChoiceField(label='Curso', queryset=Curso.objects.all(), widget=forms.Select(attrs={'class':'form-select'}))
    tipo_documento = forms.ChoiceField(label='Tipo de documento', choices=Estudiante.TIPO_DOC_CHOICES, initial='TI', widget=forms.Select(attrs={'class':'form-select'}))
    genero = forms.ChoiceField(label='Género', choices=Estudiante.GENERO_CHOICES, required=False, widget=forms.Select(attrs={'class':'form-select'}))
    rh = forms.ChoiceField(label='RH', choices=Estudiante.RH_CHOICES, required=False, widget=forms.Select(attrs={'class':'form-select'}))
    eps = forms.CharField(label='EPS', max_length=100, required=False, widget=forms.TextInput(attrs={'class':'form-control'}))
    barrio = forms.CharField(label='Barrio', max_length=100, required=False, widget=forms.TextInput(attrs={'class':'form-control'}))
    estrato = forms.ChoiceField(label='Estrato', choices=Estudiante.ESTRATO_CHOICES, required=False, widget=forms.Select(attrs={'class':'form-select'}))
    telefono = forms.CharField(label='Teléfono', max_length=20, required=False, widget=forms.TextInput(attrs={'class':'form-control'}))
    celular = forms.CharField(label='Celular', max_length=20, required=False, widget=forms.TextInput(attrs={'class':'form-control'}))
    direccion = forms.CharField(label='Dirección', required=False, widget=forms.Textarea(attrs={'class':'form-control', 'rows':2}))
    nui = forms.CharField(label='NUI', max_length=50, required=False, widget=forms.TextInput(attrs={'class':'form-control'}))
    etnia = forms.CharField(label='Etnia', max_length=100, required=False, widget=forms.TextInput(attrs={'class':'form-control'}))
    jornada = forms.CharField(label='Jornada', max_length=50, required=False, widget=forms.TextInput(attrs={'class':'form-control'}))

    def clean_documento(self):
        documento = self.cleaned_data['documento']
        if not documento.isdigit():
            raise forms.ValidationError('El documento debe contener solo dígitos')
        return documento


class EstudianteEditForm(forms.ModelForm):
    numero_documento = forms.CharField(
        max_length=150, label='N° Documento',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    primer_nombre = forms.CharField(
        max_length=150, label='Primer Nombre', required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    segundo_nombre = forms.CharField(
        max_length=150, label='Segundo Nombre', required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    primer_apellido = forms.CharField(
        max_length=150, label='Primer Apellido', required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    segundo_apellido = forms.CharField(
        max_length=150, label='Segundo Apellido', required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Estudiante
        fields = [
            'tipo_documento', 'fecha_nacimiento', 'acudiente',
            'telefono', 'celular', 'direccion', 'barrio',
            'lugar_nacimiento', 'genero', 'rh', 'eps', 'estrato',
            'pago_certificado', 'nui', 'etnia', 'discapacidad',
            'jornada', 'zona', 'pais_origen', 'estado_matricula',
            'modelo_educativo', 'fuente_recursos', 'campesino',
            'categoria_aula',
        ]
        widgets = {
            'tipo_documento': forms.Select(attrs={'class': 'form-select'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'acudiente': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'celular': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'barrio': forms.TextInput(attrs={'class': 'form-control'}),
            'lugar_nacimiento': forms.TextInput(attrs={'class': 'form-control'}),
            'genero': forms.Select(attrs={'class': 'form-select'}),
            'rh': forms.Select(attrs={'class': 'form-select'}),
            'eps': forms.TextInput(attrs={'class': 'form-control'}),
            'estrato': forms.Select(attrs={'class': 'form-select'}),
            'pago_certificado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            user = self.instance.usuario
            names = (user.first_name or '').strip().split()
            lastnames = (user.last_name or '').strip().split()
            self.fields['numero_documento'].initial = user.username
            self.fields['primer_nombre'].initial = names[0] if len(names) > 0 else ''
            self.fields['segundo_nombre'].initial = names[1] if len(names) > 1 else ''
            self.fields['primer_apellido'].initial = lastnames[0] if len(lastnames) > 0 else ''
            self.fields['segundo_apellido'].initial = lastnames[1] if len(lastnames) > 1 else ''

    def save(self, commit=True):
        instance = super().save(commit=False)
        old_username = instance.usuario.username
        new_username = self.cleaned_data['numero_documento']
        instance.usuario.username = new_username
        if new_username != old_username:
            instance.usuario.set_password(f'{new_username}*')
        p_nombre = self.cleaned_data.get('primer_nombre', '') or ''
        s_nombre = self.cleaned_data.get('segundo_nombre', '') or ''
        p_apellido = self.cleaned_data.get('primer_apellido', '') or ''
        s_apellido = self.cleaned_data.get('segundo_apellido', '') or ''
        instance.usuario.first_name = f'{p_nombre} {s_nombre}'.strip()
        instance.usuario.last_name = f'{p_apellido} {s_apellido}'.strip()
        if commit:
            instance.usuario.save()
            instance.save()
        return instance
