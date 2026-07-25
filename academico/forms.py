from django import forms
from .models import Curso, Materia, CursoMateria
from docentes.models import Docente
from django import forms as djforms

PERIODOS = (
    ('1','Periodo 1'),
    ('2','Periodo 2'),
    ('3','Periodo 3'),
    ('4','Periodo 4'),
)

class MateriaEditForm(forms.ModelForm):
    class Meta:
        model = Materia
        fields = ['nombre', 'descripcion', 'area', 'docentes']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': '3'}),
            'area': forms.TextInput(attrs={'class': 'form-control'}),
            'docentes': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '6'}),
        }


class MateriaForm(forms.ModelForm):
    docentes = forms.ModelMultipleChoiceField(queryset=Docente.objects.all(), required=False,
                                              widget=forms.SelectMultiple(attrs={'class':'form-select','size':'6'}))
    class Meta:
        model = Materia
        fields = ['nombre','descripcion','creditos','area','docentes']
        widgets = {
            'nombre': forms.TextInput(attrs={'class':'form-control'}),
            'descripcion': forms.Textarea(attrs={'class':'form-control','rows':'3'}),
            'creditos': forms.NumberInput(attrs={'class':'form-control','min':'0'}),
            'area': forms.TextInput(attrs={'class':'form-control'}),
        }

class CursoCreateForm(forms.ModelForm):
    materias = forms.ModelMultipleChoiceField(queryset=Materia.objects.all(), required=False,
                                              widget=forms.SelectMultiple(attrs={'class':'form-select','size':'8'}),
                                              help_text='Selecciona materias a asignar al curso (no obligatorio para preescolar)')
    periodo_academico = djforms.ChoiceField(choices=PERIODOS, initial='1', widget=djforms.Select(attrs={'class':'form-select'}))
    anio_lectivo = djforms.IntegerField(initial=2026, widget=djforms.NumberInput(attrs={'class':'form-control'}))
    docente_universal = forms.ModelChoiceField(queryset=Docente.objects.all(), required=False, widget=forms.Select(attrs={'class':'form-select'}), help_text='Asignar un mismo docente a todas las materias seleccionadas')
    tutor = forms.ModelChoiceField(queryset=Docente.objects.all(), required=False, widget=forms.Select(attrs={'class':'form-select'}), help_text='Tutor responsable del curso (útil para Preescolar)')
    class Meta:
        model = Curso
        fields = ['nombre','descripcion','nivel','materias','tutor']
        widgets = {
            'nombre': forms.TextInput(attrs={'class':'form-control'}),
            'descripcion': forms.Textarea(attrs={'class':'form-control','rows':'2'}),
            'nivel': forms.TextInput(attrs={'class':'form-control'}),
        }


class CursoEditForm(forms.ModelForm):
    nivel = forms.ChoiceField(choices=[
        ('PREESCOLAR', 'Preescolar'),
        ('BASICA_PRIMARIA', 'Básica Primaria'),
        ('BACHILLERATO', 'Bachillerato'),
    ], widget=forms.Select(attrs={'class': 'form-select'}))
    materias = forms.ModelMultipleChoiceField(
        queryset=Materia.objects.all(), required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        help_text='Selecciona las materias que pertenecen a este curso'
    )
    hora_inicio_jornada = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}), label="Inicio de jornada")
    hora_fin_jornada = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}), label="Fin de jornada")

    class Meta:
        model = Curso
        fields = ['nombre', 'descripcion', 'nivel', 'sede', 'tutor', 'materias',
                  'hora_inicio_jornada', 'hora_fin_jornada', 'duracion_clase', 'num_descansos',
                  'descanso1_min', 'descanso2_min', 'descanso3_min']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': '3'}),
            'nivel': forms.TextInput(attrs={'class': 'form-control'}),
            'sede': forms.Select(attrs={'class': 'form-select'}),
            'tutor': forms.Select(attrs={'class': 'form-select'}),
            'duracion_clase': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'num_descansos': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'id': 'id_num_descansos'}),
            'descanso1_min': forms.NumberInput(attrs={'class': 'form-control descanso-min', 'min': '1'}),
            'descanso2_min': forms.NumberInput(attrs={'class': 'form-control descanso-min', 'min': '1'}),
            'descanso3_min': forms.NumberInput(attrs={'class': 'form-control descanso-min', 'min': '1'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['materias'].initial = self.instance.curso_materias.values_list('materia_id', flat=True)

    def save(self, commit=True):
        curso = super().save(commit=commit)
        if commit:
            ids_sel = {m.id for m in self.cleaned_data.get('materias', [])}
            ids_actuales = set(CursoMateria.objects.filter(curso=curso).values_list('materia_id', flat=True))
            for m_id in ids_sel - ids_actuales:
                CursoMateria.objects.get_or_create(curso=curso, materia_id=m_id, periodo_academico='1', anio_lectivo=2026)
            CursoMateria.objects.filter(curso=curso, materia_id__in=ids_actuales - ids_sel).delete()
        return curso
