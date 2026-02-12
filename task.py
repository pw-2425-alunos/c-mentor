import os
import django

from django.core.mail import send_mail


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projeto.settings') 
django.setup()


from datetime import datetime, timedelta
from mentoria.models import *
from django.conf import settings
from django.utils import timezone

amanha = timezone.now() + timedelta(days=1)
amanha = amanha.replace(hour=0, minute=0, second=0, microsecond=0)

sessoes = Sessao.objects.filter(data__date=amanha.date())


for sessao in sessoes:

    email = sessao.diade.mentorando.aluno.user.email
    hora = str(sessao.data.hour).zfill(2)
    minutos = str(sessao.data.minute).zfill(2) 

    send_mail(
    'Lembrente de Sessão',
    f'Olá,\nEste email serve para te relembrar que amanhã tens uma sessão de {sessao.diade.mentor.disciplina} com o mentor {sessao.diade.mentor.aluno} ás {hora}:{minutos}.\n',
    'mentoriadeisi@gmail.com',
    [email]
    )
