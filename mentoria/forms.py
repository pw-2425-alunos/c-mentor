from django import forms
from django.forms import ModelForm
from .models import Sessao
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

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
                    'min': '0',
                    'max': '5',
                    'id': 'id_avaliacao_mentor',
                    'style': 'padding:0',
                }
            ),
            'avaliacao_mentorando': forms.HiddenInput(),
            'data': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'sumario': forms.Textarea(attrs={'rows': '5','cols': '30','style':'width:100%;height:50px;'}),
            'confirmado': forms.HiddenInput(),
            'reportado': forms.HiddenInput(),
            'objetivo': forms.Textarea(attrs={'rows': '5','cols': '30','style':'width:100%;height:50px;'}),
            'recursos': forms.Textarea(attrs={'rows': '5','cols': '30','style':'width:100%;height:50px;'}),
            'observacoes': forms.Textarea(attrs={'rows': '5','cols': '30','style':'width:100%;height:50px;'}),
            'planificacao_proxima_sessao': forms.Textarea(attrs={'rows': '5','cols': '30','style':'width:100%;height:50px;'}),
        }

    def clean_data(self):
        data = self.cleaned_data.get('data')
        if data:
            now = timezone.now()
            min_date = now - timedelta(days=5)
            if data < min_date:
                raise ValidationError("The session date cannot be earlier than 5 days before today.")
        return data
