from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from app.models import Aluno   

from django import forms
from django.forms import ModelForm
from .models import Sessao
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

# Formulário para criar Aluno e User juntos
class AlunoCreateForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(label='First Name', max_length=150)
    last_name = forms.CharField(label='Last Name', max_length=150)
    username = forms.CharField(label='Student Number (Username)', max_length=100)

    class Meta:
        model = Aluno
        fields = ['numero', 'curso', 'ano']
        labels = {
            'numero': 'Student Number',
            'curso': 'Course',
            'ano': 'Year',
        }
        widgets = {
            'ano': forms.Select(),
        }

    def save(self, commit=True):
        # Cria User primeiro, sem password definida
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            password=None  # Sem password definida
        )
        aluno = super().save(commit=False)
        aluno.user = user
        if commit:
            aluno.save()
        return aluno
    

from django.contrib.auth.models import User

class AlunoUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(label='First Name', max_length=150)
    last_name = forms.CharField(label='Last Name', max_length=150)
    username = forms.CharField(label='Student Number (Username)', max_length=100)

    class Meta:
        model = Aluno
        fields = ['numero', 'curso', 'ano']
        widgets = {
            'ano': forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Pre-fill user fields if editing
        if self.instance and self.instance.pk:
            user = self.instance.user
            self.fields['email'].initial = user.email
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['username'].initial = user.username

    def save(self, commit=True):
        aluno = super().save(commit=False)

        # Update related User
        user = aluno.user
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.username = self.cleaned_data['username']

        if commit:
            user.save()
            aluno.save()

        return aluno

class SessaoForm(ModelForm):
    class Meta:
        model = Sessao
        fields = '__all__'
        labels = {
            'data': 'Session Date',
            'objetivo': 'Session Objectives',
            'recursos': 'Resources Used',
            'avaliacao_mentor': 'Evaluation of the session by the mentor',
            'avaliacao_mentorando': 'Evaluation of the session by the mentee',
            'observacoes': 'Observations / Difficulties Encountered',
            'planificacao_proxima_sessao': 'Homework',
            'sumario': 'Session Summary',
        }
        widgets = {
            'diade': forms.HiddenInput(),
            'avaliacao_mentor': forms.NumberInput(
                attrs={
                    'type': 'range',
                    'min': '1',
                    'max': '5',
                    'step': '1',
                    'id': 'id_avaliacao_mentor',
                    'style': 'padding:0',
                    'oninput': 'this.nextElementSibling.value = this.value',  
                }
            ),
            'avaliacao_mentorando': forms.HiddenInput(),
            'data': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'sumario': forms.Textarea(attrs={'rows': '5','cols': '30','style':'width:100%;height:50px;'}),
            'confirmado': forms.HiddenInput(),
            'reportado': forms.HiddenInput(),
            'objetivo': forms.Textarea(attrs={'rows': '5','cols': '30','style':'width:100%;height:50px;'}),
            'recursos': forms.Textarea(attrs={'rows': '5','cols': '30','style':'width:100%;height:50px;'}),
            'observacoes': forms.Textarea(attrs={'rows': '5','cols': '30','style':'width:100%;height:50px;'}),
            'planificacao_proxima_sessao': forms.Textarea(attrs={'rows': '5','cols': '30','style':'width:100%;height:50px;'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Formata data para compatibilidade com datetime-local
            self.fields['data'].initial = self.instance.data.strftime('%Y-%m-%dT%H:%M')

    def clean_data(self):
        data = self.cleaned_data.get('data')
        if data:
            now = timezone.now()
            min_date = now - timedelta(days=5)
            if data < min_date:
                raise ValidationError("The session date cannot be earlier than 5 days before today.")
        return data
