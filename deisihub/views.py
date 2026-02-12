from django.shortcuts import render
from app.models import Aluno
from .models import Presenca
from django.contrib.auth.decorators import login_required

# Create your views here.

def identifica_view(request):
    context = {}

    if request.method == 'POST':
        numero = request.POST.get('numero')

        if request.POST.get('registar') == "False":

            if len(Aluno.objects.filter(numero=numero)) > 0 :
                aluno = Aluno.objects.filter(numero=numero)[0]
                context = {'aluno': aluno}
            else:
                context = {'message': 'aluno inexistente'}

        else:
            aluno = Aluno.objects.get(numero=numero)
            Presenca.objects.create(aluno = aluno)
            context = {'message': 'Presença registada'}

    return render(request, 'deisihub/index.html', context)



from django.shortcuts import render
from django.db.models import Count
from django.db.models.functions import TruncDate
import json
from .models import Presenca
from datetime import timedelta
from django.utils import timezone

def presencas_view(request):
    # Ordenar presenças cronologicamente

#    presencas = Presenca.objects.all().order_by('entrada')

    hoje = timezone.now()
    inicio = hoje - timedelta(days=90)

    presencas = Presenca.objects.filter(entrada__gte=inicio)

    # Atribuir ordem dentro de cada dia
    previous_day = None
    ordem = 1
    for p in presencas:
        if previous_day != p.date:
            ordem = 1
            previous_day = p.date
        p.ordem = ordem
        ordem += 1
        p.save()

    # Dados agregados para gráfico
    dados_por_dia = (
        presencas
        .annotate(dia=TruncDate('entrada'))
        .values('dia')
        .annotate(total=Count('id'))
        .order_by('dia')
    )

    labels = [d['dia'].strftime("%d/%m/%Y") for d in dados_por_dia]
    values = [d['total'] for d in dados_por_dia]

    context = {
        'presencas': presencas.order_by('-entrada'),  # tabela decrescente
        'labels': json.dumps(labels),
        'values': json.dumps(values),
    }

    return render(request, 'deisihub/presencas.html', context)


