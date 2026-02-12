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
        'objetivo': 'Objetivos da sessão',
        'recursos': 'Recursos utilizados',
        'avaliacao_mentor': 'Avaliação do trabalho realizado pelo Mentorando',
        'avaliacao_mentorando': 'Avaliação do trabalho realizado pelo Mentor',
        'observacoes': 'Observações/Dificuldades encontradas',
        'planificacao_proxima_sessao': 'Planificação da sessão seguinte',
        'sumario': 'Sumário',
    }
        widgets = {
            'diade': forms.HiddenInput(),
            'avaliacao_mentor': forms.NumberInput(
            attrs={
                'type': 'range',
                'min': '0',
                'max': '5',
                'id': 'id_avaliacao_mentor',
                'style': ' padding:0',
            }),
            'avaliacao_mentorando': forms.HiddenInput(),
            'data': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'sumario':forms.Textarea(attrs={'rows': '5','cols': '30','style':'width:100%;height:50px;'}),
            'confirmado': forms.HiddenInput(),
            'reportado': forms.HiddenInput(),
            'objetivo':forms.Textarea(attrs={'rows': '5','cols': '30','style':'width:100%;height:50px;'}),
            'recursos':forms.Textarea(attrs={'rows': '5','cols': '30','style':'width:100%;height:50px;'}),
            'observacoes':forms.Textarea(attrs={'rows': '5','cols': '30','style':'width:100%;height:50px;'}),
            'planificacao_proxima_sessao':forms.Textarea(attrs={'rows': '5','cols': '30','style':'width:100%;height:50px;'}),

        }

    def clean_data(self):
        data = self.cleaned_data.get('data')
        if data:
            agora = timezone.now()
            limite_inferior = agora - timedelta(days=5)
            if data < limite_inferior:
                raise ValidationError("A data da sessão não pode ser anterior a 5 dias da data atual.")
        return data



