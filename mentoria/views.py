from django.shortcuts import get_object_or_404, render, redirect
from .models import *
from django.contrib.auth.decorators import login_required
from .forms import SessaoForm

from django.http import HttpResponse, JsonResponse

from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from datetime import datetime, date

from matplotlib import pyplot as plt
import io
import urllib, base64
from django.db.models import Count
from django.db.models.functions import ExtractMonth
import matplotlib
import calendar
import locale
matplotlib.use('Agg')


semestre = 2



# Create your views here.
@login_required
def __mentores_view(request):
    ano = AnoLectivo.objects.get(ano='25-26')
    print("\n\n\ngrupos do utilizador:", request.user.groups.all())

    if request.user.groups.filter(name="Gestores").exists():
        alunos_mentores = Mentor.objects.filter(ano_lectivo=ano, disciplina__semestre=semestre).values_list('aluno', flat=True).distinct()
    else:
        aluno = Aluno.objects.get(user = request.user)
        alunos_mentores = Mentor.objects.filter(ano_lectivo=ano, aluno=aluno, disciplina__semestre=semestre).values_list('aluno', flat=True).distinct()

    if len(alunos_mentores) == 0:
        alunos_mentores = [aluno.id]

    ## lista de alunos mentores com lista de mentorias
    alunos = []
    for aluno_id in alunos_mentores:

        # mentorias do mentor aluno_id
        mentorias = Mentor.objects.filter(ano_lectivo=ano, aluno=aluno_id, disciplina__semestre=semestre).order_by('disciplina__nome')

        # disciplinas que o aluno é mentor
        disciplinas_mentoria = mentorias.values_list('disciplina', flat=True)

        # mentorandos que mentor pode selecionar
        # mentorandos_potenciais_sem_diade = Mentorando.objects.filter(ano_lectivo=ano,disciplina__semestre=semestre, disciplina__in=disciplinas_mentoria).exclude(diades_mentorando__mentor__aluno=aluno_id)

        mentorandos_potenciais_sem_diade = Mentorando.objects.exclude(diades_mentorando__isnull=False).filter(ano_lectivo=ano, disciplina__semestre=semestre, disciplina__in=disciplinas_mentoria).order_by('disciplina__nome', 'aluno')


        # Disciplinas que pode selecionar ser mentor
        disciplinas_nao_mentorizadas = Disciplina.objects.filter(semestre=semestre).exclude(id__in=disciplinas_mentoria).order_by('nome')


        alunos.append(
            [
                aluno_id,
                mentorias,
                disciplinas_nao_mentorizadas,
                mentorandos_potenciais_sem_diade
            ])


    mentorandos_sem_diade = Mentorando.objects.exclude(diades_mentorando__isnull=False).filter(ano_lectivo=ano, disciplina__semestre=semestre).order_by('disciplina__nome', 'aluno')


    context = {'alunos':alunos, 'mentorandos_sem_diade':mentorandos_sem_diade, 'ano': ano, 'semestre':semestre}

    return render(request, 'mentoria/mentores_diades.html', context)

from django.db.models import Prefetch


# view otimizada
@login_required
def mentores_view(request):
    ano = AnoLectivo.objects.get(ano='25-26')
    print("\n\n\ngrupos do utilizador:", request.user.groups.all())

    # Obter aluno atual (caso não seja gestor)
    if request.user.groups.filter(name="Gestores").exists():
        alunos_mentores_ids = Mentor.objects.filter(
            ano_lectivo=ano,
            disciplina__semestre=semestre
        ).values_list('aluno_id', flat=True).distinct()
    else:
        aluno = Aluno.objects.select_related('user').get(user=request.user)
        alunos_mentores_ids = Mentor.objects.filter(
            ano_lectivo=ano,
            aluno=aluno,
            disciplina__semestre=semestre
        ).values_list('aluno_id', flat=True).distinct()
        if not alunos_mentores_ids:
            alunos_mentores_ids = [aluno.id]

    # Pré-carregamento das informações relevantes
    mentorias_qs = Mentor.objects.filter(
        ano_lectivo=ano,
        disciplina__semestre=semestre,
        aluno_id__in=alunos_mentores_ids
    ).select_related('aluno', 'disciplina').order_by('disciplina__nome')

    mentorias_por_aluno = {}
    for m in mentorias_qs:
        mentorias_por_aluno.setdefault(m.aluno_id, []).append(m)

    disciplinas_por_aluno = {
        aluno_id: [m.disciplina.id for m in mentorias]
        for aluno_id, mentorias in mentorias_por_aluno.items()
    }

    # Pré-carregar mentorandos sem diade
    mentorandos_sem_diade_qs = Mentorando.objects.filter(
        ano_lectivo=ano,
        disciplina__semestre=semestre
    ).exclude(diades_mentorando__isnull=False).select_related('disciplina', 'aluno').order_by('disciplina__nome', 'aluno')

    # Agrupar mentorandos por disciplina
    mentorandos_por_disciplina = {}
    for m in mentorandos_sem_diade_qs:
        mentorandos_por_disciplina.setdefault(m.disciplina_id, []).append(m)

    # Disciplinas já mentorizadas (para filtragem das disponíveis)
    todas_disciplinas = Disciplina.objects.filter(semestre=semestre).order_by('nome')
    disciplinas_dict = {d.id: d for d in todas_disciplinas}

    alunos = []
    for aluno_id in alunos_mentores_ids:
        mentorias = mentorias_por_aluno.get(aluno_id, [])
        disciplinas_mentoria_ids = disciplinas_por_aluno.get(aluno_id, [])

        # Mentorandos potenciais
        mentorandos_potenciais = []
        for disciplina_id in disciplinas_mentoria_ids:
            mentorandos_potenciais.extend(mentorandos_por_disciplina.get(disciplina_id, []))

        # Disciplinas que ainda pode mentorar
        disciplinas_nao_mentorizadas = [
            disciplina for did, disciplina in disciplinas_dict.items()
            if did not in disciplinas_mentoria_ids
        ]

        alunos.append([
            aluno_id,
            mentorias,
            disciplinas_nao_mentorizadas,
            mentorandos_potenciais
        ])

    context = {
        'alunos': alunos,
        'mentorandos_sem_diade': mentorandos_sem_diade_qs,
        'ano': ano,
        'semestre': semestre
    }

    return render(request, 'mentoria/mentores_diades.html', context)


#@login_required
def emails_view(request):
    ano = AnoLectivo.objects.get(ano='25-26')
    emails_mentores = set()
    for m in Mentor.objects.filter(ano_lectivo=ano, disciplina__semestre=semestre).select_related('aluno__user'):
        emails_mentores.add(f"{m.aluno} <{m.aluno.user.email}>")


    emails_mentorandos = set()
    for m in Mentorando.objects.filter(ano_lectivo=ano, disciplina__semestre=semestre):
        emails_mentorandos.add(f"{m.aluno} <{m.aluno.user.email}>")

    context = {'emails_mentorandos':emails_mentorandos, 'emails_mentores':emails_mentores, 'ano': ano, 'semestre':semestre}

    return render(request, 'mentoria/emails.html', context)



# Create your views here.
@login_required
def cria_diade_view(request):
    ano = AnoLectivo.objects.get(ano='25-26')

    if request.method == 'POST':
        mentorando = Mentorando.objects.get(id=request.POST['mentorando_id'])

        aluno_mentor = Aluno.objects.get(id=request.POST['mentor_aluno_id'])
        mentor = Mentor.objects.get(
                        aluno=aluno_mentor,
                        disciplina = mentorando.disciplina,
                        ano_lectivo = ano,
                    )

        if not Diade.objects.filter(ano_lectivo=ano, mentor = mentor, mentorando=mentorando).exists():
            diade = Diade.objects.create(ano_lectivo=ano, mentor = mentor, mentorando=mentorando)


    return redirect('mentores')


# Create your views here.
@login_required
def ___mentorandos_view(request):


    if request.user.groups.filter(name="Gestores").exists():
        alunos_mentorando = set( m.aluno for m in Mentorando.objects.filter(ano_lectivo=ano, disciplina__semestre=semestre) )
        alunoAtual = "admin"
    else:
        alunoAtual = Aluno.objects.get(user = request.user)
        alunos_mentorando = set( m.aluno for m in Mentorando.objects.filter(ano_lectivo=ano, disciplina__semestre=semestre, aluno=alunoAtual) )


    mentorandos_info = []
    disciplinas_sem_mentoria = []

    for aluno_mentorando in alunos_mentorando:
        info = {}
        info['mentorando'] = aluno_mentorando

        mentorandias = []

        for mentorando in Mentorando.objects.filter( ano_lectivo=ano, disciplina__semestre=semestre, aluno=aluno_mentorando ):
            info_ = {}

            info_['mentorando'] = mentorando
            info_['disciplina'] = mentorando.disciplina

            diades = Diade.objects.filter(ano_lectivo=ano, mentor__disciplina__semestre=semestre, mentorando = mentorando )

            for diade in diades:
                    if diade.mentorando.disciplina == mentorando.disciplina:
                        info_['mentor'] = diade.mentor
                        break
            else:
                info_['mentor'] = '-'

            mentorandias.append(info_)

        mentorandias.sort(key=lambda item:item['disciplina'].nome)
        info['mentorandias'] = mentorandias

        disciplinas_com_mentoria = [mentorandia['disciplina'] for mentorandia in mentorandias]
        info['disciplinas_sem_mentoria'] = Disciplina.objects.exclude(pk__in=[disciplina.pk for disciplina in disciplinas_com_mentoria])
        info['disciplinas_sem_mentoria'] = info['disciplinas_sem_mentoria'].filter(semestre=semestre)
        disciplinas_sem_mentoria = info['disciplinas_sem_mentoria']
        mentorandos_info.append(info)

    mentorandos_info.sort(key=lambda x:str(x['mentorando']))

    if len(disciplinas_sem_mentoria) == 0:
        disciplinas_sem_mentoria = Disciplina.objects.filter(semestre=semestre)


    alunos_mentores = Mentor.objects.filter(ano_lectivo=ano, disciplina__semestre=semestre).values_list('aluno', flat=True).distinct()


    # mentorias existentes
    mentorias = Mentor.objects.filter(ano_lectivo=ano, disciplina__semestre=semestre).order_by('disciplina__nome')


    context = { 'ano':ano, 'mentorandos_info':mentorandos_info, 'vazio':len(mentorandos_info), 'aluno': alunoAtual,
                'disciplinas':disciplinas_sem_mentoria, 'mentorias':mentorias, 'ano': ano, 'semestre':semestre}

    return render(request, 'mentoria/mentorandos.html', context)



from django.db.models import Prefetch

@login_required
def mentorandos_view(request):
    ano = AnoLectivo.objects.get(ano='25-26')
    if request.user.groups.filter(name="Gestores").exists():
        alunos_mentorando = set(
            m.aluno for m in Mentorando.objects.filter(
                ano_lectivo=ano,
                disciplina__semestre=semestre
            ).select_related('aluno')  # otimiza acesso a m.aluno
        )
        alunoAtual = "admin"
    else:
        alunoAtual = Aluno.objects.select_related('user').get(user=request.user)
        alunos_mentorando = set(
            m.aluno for m in Mentorando.objects.filter(
                ano_lectivo=ano,
                disciplina__semestre=semestre,
                aluno=alunoAtual
            ).select_related('aluno')  # idem
        )

    mentorandos_info = []
    disciplinas_sem_mentoria = []

    for aluno_mentorando in alunos_mentorando:
        info = {'mentorando': aluno_mentorando}
        mentorandias = []

        mentorando_qs = Mentorando.objects.filter(
            ano_lectivo=ano,
            disciplina__semestre=semestre,
            aluno=aluno_mentorando
        ).select_related('disciplina', 'aluno')  # evita query extra para disciplina/aluno

        # Pré-carrega diades para esses mentorandos com os relacionamentos necessários
        diade_qs = Diade.objects.filter(
            ano_lectivo=ano,
            mentor__disciplina__semestre=semestre,
            mentorando__in=mentorando_qs
        ).select_related('mentorando', 'mentor__aluno', 'mentor__disciplina')

        # organiza as diades por mentorando id para acesso rápido
        diades_por_mentorando = {}
        for diade in diade_qs:
            diades_por_mentorando.setdefault(diade.mentorando_id, []).append(diade)

        for mentorando in mentorando_qs:
            info_ = {
                'mentorando': mentorando,
                'disciplina': mentorando.disciplina
            }

            # seleciona o primeiro mentor com mesma disciplina (como antes)
            diades = diades_por_mentorando.get(mentorando.id, [])
            for diade in diades:
                if diade.mentorando.disciplina == mentorando.disciplina:
                    info_['mentor'] = diade.mentor
                    break
            else:
                info_['mentor'] = '-'

            mentorandias.append(info_)

        mentorandias.sort(key=lambda item: item['disciplina'].nome)
        info['mentorandias'] = mentorandias

        disciplinas_com_mentoria = [m['disciplina'] for m in mentorandias]
        disciplinas_ids = [d.pk for d in disciplinas_com_mentoria]

        info['disciplinas_sem_mentoria'] = Disciplina.objects.exclude(pk__in=disciplinas_ids).filter(semestre=semestre)
        disciplinas_sem_mentoria = info['disciplinas_sem_mentoria']

        mentorandos_info.append(info)

    mentorandos_info.sort(key=lambda x: str(x['mentorando']))

    if len(disciplinas_sem_mentoria) == 0:
        disciplinas_sem_mentoria = Disciplina.objects.filter(semestre=semestre)

    # Otimização com select_related para mentor.aluno e mentor.disciplina
    alunos_mentores = Mentor.objects.filter(
        ano_lectivo=ano,
        disciplina__semestre=semestre
    ).select_related('aluno').values_list('aluno', flat=True).distinct()

    mentorias = Mentor.objects.filter(
        ano_lectivo=ano,
        disciplina__semestre=semestre
    ).select_related('disciplina').order_by('disciplina__nome')

    context = {
        'ano': ano,
        'mentorandos_info': mentorandos_info,
        'vazio': len(mentorandos_info),
        'aluno': alunoAtual,
        'disciplinas': disciplinas_sem_mentoria,
        'mentorias': mentorias,
        'semestre': semestre,
    }

    return render(request, 'mentoria/mentorandos.html', context)




# Create your views here.
@login_required
def diades_view(request):
    ano = AnoLectivo.objects.get(ano='25-26')
    context = {'diades': Diade.objects.all(), 'ano': ano, 'semestre':semestre}
    return render(request, 'mentoria/diades.html', context)


@login_required
def cria_mentor_view(request):
    ano = AnoLectivo.objects.get(ano='25-26')
    if request.method == 'POST':
        aluno = Aluno.objects.get(id=request.POST['mentor_aluno_id'])
        disciplina = Disciplina.objects.get(id=request.POST['disciplina_id'])

        if disciplina.nome != "Competências Comportamentais" and not Mentor.objects.filter(ano_lectivo=ano, aluno=aluno, disciplina=disciplina).exists():
            Mentor.objects.create(ano_lectivo=ano, aluno=aluno, disciplina=disciplina)

    return redirect('mentores')


@login_required
def cria_mentorando_view(request):
    ano = AnoLectivo.objects.get(ano='25-26')
    if request.method == 'POST':
        aluno = Aluno.objects.get(id=request.POST['mentorando_aluno_id'])
        disciplina = Disciplina.objects.get(id=request.POST['disciplina_id'])

        if disciplina.nome != "Competências Comportamentais" and not Mentorando.objects.filter(ano_lectivo=ano, aluno=aluno, disciplina=disciplina).exists():
            Mentorando.objects.create(ano_lectivo=ano, aluno=aluno, disciplina=disciplina)

           # mentores = list(Mentor.objects.filter(disciplina = disciplina))

           # for para enviar email aos mentores(dessa disciplina) quando um mentorando escolhe uma disciplina

           # for a in mentores:
                #email = a.aluno.user.email

                #send_mail(
                #'Aviso para Mentores',
               # f'Olá,\nExiste um novo aluno a precisar de mentoria a {disciplina}.\nCaso esteja interessado, entre na plataforma para aceitar a mentoria.',
               # 'goncalo.coelhonunes@gmail.com',
               # [email]
        #)

    return redirect('mentorandos')


@login_required
def remover_mentorando_view(request, mentorando_id):
    ano = AnoLectivo.objects.get(ano='25-26')
    mentorando = Mentorando.objects.get(id=mentorando_id)
    diade = Diade.objects.filter(mentorando=mentorando)

    if len(diade):
        if mentorando.ativo == False & diade[0].ativo == False:
            mentorando.ativo = True
            mentorando.save()

            diade[0].ativo = True
            diade[0].save()
        else:
            mentorando.ativo = False
            mentorando.save()

            diade[0].ativo = False
            diade[0].save()
    else:
        mentorando.delete()

    return redirect('mentorandos')


@login_required
def sessoes_view(request,mentor_id,mentorando_id,sep):
    ano = AnoLectivo.objects.get(ano='25-26')


    if request.user.groups.filter(name="Gestores").exists():
        context = {'sessoes': Sessao.objects.all()}
    else:
        mentor = Mentor.objects.get(id=mentor_id)
        mentorando = Mentorando.objects.get(id=mentorando_id)
        disciplina = mentor.disciplina
        diade = Diade.objects.get(mentor=mentor,mentorando=mentorando)

        # A variavel 'sep' é usada para distinguir quem entra na view da sessão
        # Mentor -> sep = 0
        # Mentorando -> sep = 1

        context = {'sessoes': Sessao.objects.filter(diade = diade),
                'diade': diade,
                'sep': sep,
                'disciplina':disciplina,
                'mentor':mentor,
                'mentorando':mentorando,
                'ano': ano,
                'semestre':semestre}

    return render(request, 'mentoria/sessoes.html', context)


@login_required
def criar_sessao_view(request, diade_id):
    ano = AnoLectivo.objects.get(ano='25-26')
    diade = Diade.objects.get(id=diade_id)

    if request.method == 'POST':
        form = SessaoForm(request.POST)
        if form.is_valid():
            form.diade = diade
            form.save()
            return redirect('sessoes', diade.mentor_id, diade.mentorando_id, 0)
    else:
        form = SessaoForm(initial={'diade': diade})

    return render(request, 'mentoria/criar_sessao.html', { 'form': form, 'diade': diade, 'ano': ano, 'semestre':semestre})


@login_required
def edita_sessao_view(request, sessao_id):
    ano = AnoLectivo.objects.get(ano='25-26')
    sessao = get_object_or_404(Sessao, id=sessao_id)
    diade = Sessao.objects.get(id=sessao_id).diade

    if request.method == 'POST':
        form = SessaoForm(request.POST, instance=sessao)

        if form.is_valid():
            form.save()
            return redirect('sessoes', diade.mentor_id, diade.mentorando_id, 0)

    else:
        form = SessaoForm(instance=sessao)

    context = {'form': form, 'sessao_id': sessao_id, 'diade': diade, 'ano': ano, 'semestre':semestre}
    return render(request, 'mentoria/editar_sessao.html', context)


@login_required
def apaga_sessao_view(request, sessao_id):
    ano = AnoLectivo.objects.get(ano='25-26')
    diade = Sessao.objects.get(id=sessao_id).diade
    Sessao.objects.get(id=sessao_id).delete()
    return redirect('sessoes', diade.mentor_id, diade.mentorando_id, 0)

@login_required
def perfil_view(request, aluno_id):
    ano = AnoLectivo.objects.get(ano='25-26')
    aluno = Aluno.objects.get(id=aluno_id)

    return render(request, 'mentoria/perfil.html', {'aluno': aluno, 'ano': ano, 'semestre':semestre})

@login_required
def vermais_view(request, sessao_id):
    ano = AnoLectivo.objects.get(ano='25-26')
    sessao = Sessao.objects.get(id=sessao_id)

    return render(request, 'mentoria/ver_mais.html', {'sessao': sessao, 'ano': ano, 'semestre':semestre})

@login_required
def ___all_sessoes_view(request):
    ano = AnoLectivo.objects.get(ano='25-26')
    if request.user.groups.filter(name="Gestores").exists():
        sessoes = list(Sessao.objects.filter(diade__ano_lectivo=ano))

    else:
        alunoAtual = Aluno.objects.get(user = request.user)
        sessoes = list(sessao for sessao in Sessao.objects.filter(diade__mentor__aluno=alunoAtual, diade__ano_lectivo=ano))

    sessoes.sort(key=lambda x: (str(x.diade.mentor.aluno), x.data))


    sessoes_por_mentor_lista = []

    # Usado para agrupar sessões por mentor
    from collections import defaultdict
    sessoes_agrupadas = defaultdict(list)
    for sessao in sessoes:
        sessoes_agrupadas[sessao.diade.mentor.aluno.numero].append(sessao)

    # Construir a lista de dicionários
    for mentor, sessoes_mentor in sessoes_agrupadas.items():
        sessoes_por_mentor_lista.append({
            "mentor": Aluno.objects.get(numero=mentor),
            "sessoes": sessoes_mentor,
            "total_sessoes": sum(1 for sessao in sessoes_mentor if sessao.confirmado ),
            "total_sessoes_nao_reportadas": sum(1 for sessao in sessoes_mentor if not sessao.reportado and sessao.confirmado ),
        })

    return render(request, 'mentoria/all_sessoes.html', {'sessoes_por_mentor_lista': sessoes_por_mentor_lista, 'filtro': 'n', 'ano': ano, 'semestre':semestre})


from collections import defaultdict
from django.db.models import Prefetch

## codigo otimizado
@login_required
def all_sessoes_view(request):
    ano = AnoLectivo.objects.get(ano='25-26')

    # Obter sessões com joins otimizados
    if request.user.groups.filter(name="Gestores").exists():
        sessoes_qs = Sessao.objects.filter(
            diade__ano_lectivo=ano
        ).select_related(
            'diade__mentor__aluno'
        )
    else:
        aluno_atual = Aluno.objects.select_related('user').get(user=request.user)
        sessoes_qs = Sessao.objects.filter(
            diade__mentor__aluno=aluno_atual,
            diade__ano_lectivo=ano
        ).select_related(
            'diade__mentor__aluno'
        )

    # Ordenar diretamente no queryset
    sessoes = sessoes_qs.order_by(
        'diade__mentor__aluno__nome',  # ou outro campo adequado
        'data'
    )

    # Agrupar por aluno
    sessoes_agrupadas = defaultdict(list)
    for sessao in sessoes:
        mentor_aluno = sessao.diade.mentor.aluno
        sessoes_agrupadas[mentor_aluno].append(sessao)

    # Construir resultado final
    sessoes_por_mentor_lista = []
    for mentor_aluno, sessoes_mentor in sessoes_agrupadas.items():
        sessoes_por_mentor_lista.append({
            "mentor": mentor_aluno,
            "sessoes": sessoes_mentor,
            "total_sessoes": sum(1 for sessao in sessoes_mentor if sessao.confirmado),
            "total_sessoes_nao_reportadas": sum(1 for sessao in sessoes_mentor if not sessao.reportado and sessao.confirmado),
        })

    return render(
        request,
        'mentoria/all_sessoes.html',
        {
            'sessoes_por_mentor_lista': sessoes_por_mentor_lista,
            'filtro': 'n',
            'ano': ano,
            'semestre': semestre
        }
    )



@login_required
def av_mentorando_view(request, sessao_id):
    ano = AnoLectivo.objects.get(ano='25-26')

    sessao = get_object_or_404(Sessao, id=sessao_id)
    diade = Sessao.objects.get(id=sessao_id).diade

    if request.method == 'POST':

        sessao.confirmado = True
        avaliacao_mentorando = request.POST.get('avaliacao_mentorando')
        if avaliacao_mentorando is not None:
            sessao.avaliacao_mentorando = avaliacao_mentorando

        sessao.save()

        return redirect('sessoes', diade.mentor_id, diade.mentorando_id, 1)

    return render(request, 'mentoria/av_mentorando.html', {'sessao': sessao, 'diade': diade, 'ano': ano, 'semestre':semestre})

@login_required
def report_sessao_view(request, sessao_id):
    ano = AnoLectivo.objects.get(ano='25-26')
    sessao = get_object_or_404(Sessao, id=sessao_id)
    diade = Sessao.objects.get(id=sessao_id).diade
    sessao.reportado = True
    sessao.save()
    return redirect('report_sessoes_mentor', diade.mentor.aluno.id)

@login_required
def report_sessaoR_view(request):
    ano = AnoLectivo.objects.get(ano='25-26')
    sessoes = list(Sessao.objects.filter(reportado = False))
    sessoes.sort(key=lambda x: x.data,reverse=True)
    return render(request, 'mentoria/all_sessoes.html', {'sessoes': sessoes , 'filtro': 'r', 'ano': ano, 'semestre':semestre})



@login_required
def sessoes_por_reportar_view(request):
    ano = AnoLectivo.objects.get(ano='25-26')
    if request.user.groups.filter(name="Gestores").exists():
        sessoes = list(Sessao.objects.filter(diade__ano_lectivo=ano, diade__mentor__disciplina__semestre=semestre, reportado = False))

    else:
        alunoAtual = Aluno.objects.get(user = request.user)
        sessoes = list(sessao for sessao in Sessao.objects.filter(diade__mentor__aluno=alunoAtual, diade__ano_lectivo=ano, diade__mentor__disciplina__semestre=semestre, reportado = False))

    sessoes.sort(key=lambda x: (str(x.diade.mentor.aluno), x.data))


    sessoes_por_mentor_lista = []

    # Usado para agrupar sessões por mentor
    from collections import defaultdict
    sessoes_agrupadas = defaultdict(list)
    for sessao in sessoes:
        sessoes_agrupadas[sessao.diade.mentor.aluno.numero].append(sessao)

    # Construir a lista de dicionários
    for mentor, sessoes_mentor in sessoes_agrupadas.items():
        sessoes_por_mentor_lista.append({
            "mentor": Aluno.objects.get(numero=mentor),
            "sessoes": sessoes_mentor,
            "total_sessoes": sum(1 for sessao in sessoes_mentor if sessao.confirmado ),
            "total_sessoes_nao_reportadas": sum(1 for sessao in sessoes_mentor if not sessao.reportado and sessao.confirmado ),
        })

    return render(request, 'mentoria/all_sessoes.html', {'sessoes_por_mentor_lista': sessoes_por_mentor_lista, 'filtro': 'n', 'ano': ano, 'semestre':semestre})



@login_required
def reportar_sessoes_mentor_view(request, aluno_id):
    ano = AnoLectivo.objects.get(ano='25-26')
    if request.user.groups.filter(name="Gestores").exists():
        alunoAtual = Aluno.objects.get(id = aluno_id)
        sessoes = list(sessao for sessao in Sessao.objects.filter(diade__mentor__aluno=alunoAtual, diade__ano_lectivo=ano, diade__mentor__disciplina__semestre=semestre, reportado = False))
    else:
        return redirect('all_sessoes')

    sessoes.sort(key=lambda x: (str(x.diade.mentor.aluno), x.data))

    sessoes_por_mentor_lista = [{
            "mentor": alunoAtual,
            "sessoes": sessoes,
            "total_sessoes": sum(1 for sessao in sessoes if sessao.confirmado ),
            "total_sessoes_nao_reportadas": sum(1 for sessao in sessoes if not sessao.reportado and sessao.confirmado ),
    }]

    return render(request, 'mentoria/all_sessoes_mentor.html', {'sessoes_por_mentor_lista': sessoes_por_mentor_lista, 'filtro': 'n', 'ano': ano, 'semestre':semestre})




def info_view(request):
    ano = AnoLectivo.objects.get(ano='25-26')
    return render(request, 'mentoria/info.html')


def dashboard_view(request):
    ano = AnoLectivo.objects.get(ano='25-26')
    sessoes = Sessao.objects.filter(diade__ano_lectivo=ano, diade__mentor__disciplina__semestre=semestre)
    mentores = Mentor.objects.filter(ano_lectivo=ano, disciplina__semestre=semestre)
    diades = Diade.objects.filter(ano_lectivo=ano, mentor__disciplina__semestre=semestre)


    # cálculo de numero de sessoes realizadas por mentorando em cada disciplina
    mentorandos = []

    for d in Mentorando.objects.filter(ano_lectivo=ano, disciplina__semestre=semestre).values_list('disciplina__nome', flat=True).distinct().order_by('disciplina__nome'):
        mentorados_de_disciplina = []
        for m in Mentorando.objects.filter(ano_lectivo=ano, disciplina__nome=d):

            n_sessoes = Sessao.objects.filter(diade__mentorando=m, diade__mentorando__disciplina=m.disciplina).count()
            if n_sessoes > 0:

                mentorados_de_disciplina.append({
                    'nome': m.aluno.nome_completo,
                    'numero': m.aluno.numero,
                    'sessoes': n_sessoes,
                    'mentor': Sessao.objects.filter(diade__mentorando=m, diade__mentorando__disciplina=m.disciplina)[0].diade.mentor.aluno.nome_completo
                })

        mentorados_de_disciplina.sort(key = lambda m: m['sessoes'], reverse=True)
        mentorandos.append([
            d,
            mentorados_de_disciplina
        ])

    alunos_mentores = list(set(m.aluno for m in mentores)) #.sort(key= lambda i:i.user.first_name)
    alunos_mentorandos = list(set(m.aluno for m in Mentorando.objects.filter(ano_lectivo=ano, disciplina__semestre=semestre))) # mentorandos.values_list('aluno', flat=True).distinct().order_by('aluno')

    disciplinas_em_falta = Mentorando.objects.filter(diades_mentorando__isnull=True, ano_lectivo=ano, disciplina__semestre=semestre).values_list('disciplina__nome', flat=True).distinct().order_by('disciplina__nome')
    disciplinas_com_mentoria = Mentorando.objects.filter(diades_mentorando__isnull=False, ano_lectivo=ano, disciplina__semestre=semestre).values_list('disciplina__nome', flat=True).distinct().order_by('disciplina__nome')

    mentorandos_sem_diade = Mentorando.objects.exclude(diades_mentorando__isnull=False).filter(ano_lectivo=ano, disciplina__semestre=semestre).order_by('disciplina__nome', 'aluno')
    mentores_sem_diade = Mentor.objects.exclude(diades_mentor__isnull=False).filter(ano_lectivo=ano, disciplina__semestre=semestre).order_by('disciplina__nome', 'aluno')

    context = {
        'sessoes': sessoes,
        'diades': diades,
        'mentores': mentores,
        'mentorandos': mentorandos,
        'alunos_mentores': alunos_mentores,
        'alunos_mentorandos':alunos_mentorandos,
        'disciplinas_em_falta': disciplinas_em_falta,
        'disciplinas_com_mentoria': disciplinas_com_mentoria,
        'mentorandos_sem_diade': mentorandos_sem_diade,
        'mentores_sem_diade': mentores_sem_diade,
        'data': cria_grafico(),
        'ano': ano,
        'semestre':semestre}

    return render(request, 'mentoria/dashboard.html',context)



def old_cria_grafico():

    ano = AnoLectivo.objects.get(ano='25-26')
    locale.setlocale(locale.LC_TIME, 'pt_PT.UTF-8')
    ano_atual = datetime.now().year

    sessoes_por_mes = Sessao.objects.filter(data__year=ano_atual).annotate(mes=ExtractMonth('data')).values('mes').annotate(count=Count('id')).order_by('mes')



    meses = [item['mes'] for item in sessoes_por_mes]
    count = [item['count'] for item in sessoes_por_mes]
    nomes_meses = [datetime(2023, mes, 1).strftime('%B') for mes in meses]

    plt.barh(meses, count)
    plt.ylabel("Mês")
    plt.yticks(ticks=meses, labels=nomes_meses)
    plt.xlabel("Nº de Sessões")

    for index, value in enumerate(count):
        plt.text(value, meses[index], str(value))

    plt.autoscale()

    fig = plt.gcf()
    plt.close()

    buf = io.BytesIO()
    fig.savefig(buf, format='png')


    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)

    return uri



import locale
from datetime import datetime, timedelta
from django.db.models import Count
from django.db.models.functions import ExtractMonth, ExtractYear
import matplotlib.pyplot as plt
import io
import base64
import urllib

def cria_grafico():
    ano = AnoLectivo.objects.get(ano='25-26')
    # Definir o locale para português
    locale.setlocale(locale.LC_TIME, 'pt_PT.UTF-8')

    # Calcular a data limite (6 meses atrás)
    data_limite = datetime.now() - timedelta(days=12 * 30)

    # Obter sessões dos últimos 6 meses
    sessoes_por_mes = (
        Sessao.objects.filter(data__gte=data_limite)
        .annotate(
            mes=ExtractMonth('data'),
            ano=ExtractYear('data')
        )
        .values('mes', 'ano')
        .annotate(count=Count('id'))
        .order_by('ano', 'mes')  # Ordenar por ano e depois por mês
    )

    # Extrair dados para o gráfico
    meses_anos = [f"{datetime(item['ano'], item['mes'], 1).strftime('%B %Y')}" for item in sessoes_por_mes]
    counts = [item['count'] for item in sessoes_por_mes]
    indices = range(len(meses_anos))  # Índices para o eixo vertical

    # Criar o gráfico
    plt.figure(figsize=(10, 6))
    plt.barh(indices, counts, color='skyblue')
    plt.yticks(indices, meses_anos)  # Rótulos no formato "Mês Ano"
    plt.xlabel("Nº de Sessões")
    plt.ylabel("Mês e Ano")
    plt.title("Sessões dos Últimos 6 Meses")

    # Adicionar valores no gráfico
    for index, value in enumerate(counts):
        plt.text(value, indices[index], str(value))

    # Salvar o gráfico em memória como PNG
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')
    buf.seek(0)

    # Codificar o gráfico em Base64
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)

    return uri

