from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse

from django.contrib.auth.decorators import login_required

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode


from django.core.mail import send_mail

from .models import *


import json, random, string
import base64


# Create your views here.

def index_view(request):
    return render(request, 'app/index.html')


def horarios_view(request):
    return render(request, 'app/horarios.html')


@login_required
def disciplinas_view(request):

    aluno = Aluno.objects.get(user = request.user)

    if request.method == 'POST':
        disciplina_id = request.POST['disciplina']
        disciplina = Disciplina.objects.get(id=disciplina_id)

        accao = request.POST['accao']

        if accao == "desinscrever":

            for turma in disciplina.turmas.all():
                if aluno in turma.alunos.all():
                    turma.alunos.remove(aluno)

            disciplina.alunos.remove(aluno)


        else:
            disciplina.alunos.add(aluno)

        disciplina.save()


    context = {
        'disciplinas': Disciplina.objects.filter(semestre=1).order_by('ano', 'semestre', 'nome'),
        'aluno': aluno,
    }

    return render(request, 'app/disciplinas.html', context)



@login_required
def disciplina_view(request, disciplina_id):

    aluno = Aluno.objects.get(user = request.user)

    if request.method == 'POST':
        turma_id = request.POST['turma']
        turma = Turma.objects.get(id=turma_id)

        if turma.inscritos < turma.lotacao:

            # desinscrever da outra turma, se estiver inscrito
            for turma_aux in Turma.objects.filter(disciplina=turma.disciplina):
                if aluno in turma_aux.alunos.all():
                    turma_aux.alunos.remove(aluno)

            # inscrever nesta turma
            turma.alunos.add(aluno)

            return redirect('horarios:disciplinas')


    context = {
        'disciplina': Disciplina.objects.get(id=disciplina_id),
        'turmas': Turma.objects.filter(disciplina=disciplina_id).order_by('nome'),
        'aluno': aluno,
    }

    return render(request, 'app/disciplina.html', context)



@login_required
def inscrever_disciplina_view(request, disciplina_id):

    aluno = Aluno.objects.get(user = request.user)

    disciplina = Disciplina.objects.get(id=turma_id)
    disciplina.alunos.add(aluno)


    context = {
        'disciplinas': Disciplina.objects.filter(semestre=1).order_by('ano', 'semestre', 'nome'),
        'aluno': Aluno.objects.get(user = request.user),
    }

    return render(request, 'app/disciplinas.html', context)



@login_required
def horario_view(request):
    pass




######################################

@login_required
def delegacao_view(request):
    pass


@login_required
def utentes_view(request):

    form = UtenteForm(request.POST or None)
    if form.is_valid():
        form.save()

    colaborador = Colaborador.objects.get(user=request.user)
    context= {
        'utentes':Utente.objects.filter(delegacao=colaborador.delegacao).order_by('nome'),
        'form': form,
    }

    return render(request, 'app/utentes.html', context)


@login_required
def utente_view(request, utente_id):

    utente=Utente.objects.get(id=utente_id)

    form = OcorrenciaForm(request.POST or None, request.FILES)

    if request.method == 'POST' and form.is_valid():
        ocorrencia = form.save(commit=False) # https://docs.djangoproject.com/en/4.2/topics/forms/modelforms/#selecting-the-fields-to-use

        # adiciona ao objeto ocorrencia os campos em falta
        ocorrencia.utente = utente
        ocorrencia.colaborador = Colaborador.objects.get(nome="Daniel Fernandes")
        form.save()

        return redirect('horarios:utente', utente_id=utente_id)

    context = {
        'utente': utente,
        'form': form
    }


    return render(request, 'app/utente.html', context)



@login_required
def edita_utente_view(request, utente_id):

    utente=Utente.objects.get(id=utente_id)

    form = UtenteForm(request.POST or None, instance=utente)

    if form.is_valid():
        form.save()
        return redirect('horarios:utente', utente_id=utente.id)

    context= {
        'form': form,
        'utente':utente,
    }

    return render(request, 'app/edita_utente.html', context)




@login_required
def ocorrencia_view(request, utente_id, ocorrencia_id):
    return render(request, 'app/ocorrencia.html', {
        'utente':Utente.objects.get(id=utente_id),
        'ocorrencia':Ocorrencia.objects.get(id=ocorrencia_id),
        })



@login_required
def apagar_ocorrencia_view(request, utente_id, ocorrencia_id):
    Ocorrencia.objects.get(id=ocorrencia_id).delete()

    return redirect('horarios:utente', utente_id=utente_id)



@login_required
def edita_ocorrencia_view(request, utente_id, ocorrencia_id):

    utente = Utente.objects.get(id=utente_id)

    ocorrencia = Ocorrencia.objects.get(id=ocorrencia_id)

    form = OcorrenciaForm(request.POST or None, request.FILES, instance=ocorrencia)

    if request.method == 'POST' and form.is_valid():
        ocorrencia = form.save(commit=False) # https://docs.djangoproject.com/en/4.2/topics/forms/modelforms/#selecting-the-fields-to-use

        # adiciona ao objeto ocorrencia os campos em falta e guarda
        ocorrencia.utente = utente
        ocorrencia.colaborador = Colaborador.objects.get(nome="Daniel Fernandes")
        form.save()

        return redirect('horarios:utente', utente_id=utente_id)

    context = {
            'utente': utente,
            'ocorrencia': ocorrencia,
            'form': form,
        }

    return render(request, 'app/edita_ocorrencia.html', context)



def login_view(request):


    if request.method == 'POST':
        credential = request.POST['credential'] # poderá ser email ou username
        password = request.POST['password']

        if credential and password:

            # testa se é um email
            user = authenticate(request, email=credential, password=password)

            if user is not None:
                login(request, user)
                return redirect('info')

            else:

                # testa se é um username
                user = authenticate(request, username=credential, password=password)

                if user is not None:
                    login(request, user)
                    return redirect('info')

            return render(request, 'app/login.html', {
                'message': 'Credenciais inválidas'
            })

    return render(request, 'app/login.html')


def logout_view(request):
    logout(request)
    return redirect('info')


def forgot_password(request):

  email = request.POST.get('email')

  if not email:
    return render(request, 'app/forgot.html', {'error': 'Insert the email where you receive information from your University.'})

  user = User.objects.filter(email=email).first()

  if not user:
    return render(request, 'app/forgot.html', {'error': 'The email you entered is not registered. Contact <a href="mailto:pweb.profs@gmail.com">pweb.profs@gmail.com</a>, sending your full name, student number, course and institution, so that you can be registered on the platform.'})

  token = token = default_token_generator.make_token(user)
  uidb64 = urlsafe_base64_encode(user.pk.to_bytes(4, 'big'))

  reset_link = request.build_absolute_uri(f'/geral/reset/{uidb64}/{token}/')

  send_mail(
        'Password reset',
        f'Hello,\n\nYou requested a password reset, please click on the following link:\n\n{reset_link}',
        'pweb.profs@gmail.com',
        [email]
  )

  return render(request, 'app/forgot.html', {'success': 'An email was sent with a link to reset your password.'})



def password_reset_confirm(request, uidb64, token):

    try:
        uid = base64.urlsafe_b64decode(uidb64 + '==')
        uid = int.from_bytes(uid, 'big')

        user = User.objects.get(pk=uid)

        if default_token_generator.check_token(user, token):
            if request.method == 'POST':
                form = SetPasswordForm(user, request.POST)
                if form.is_valid():
                    form.save()
                    return render(request, 'app/login.html')
            else:
                form = SetPasswordForm(user)
            return render(request, 'app/password_reset_confirm.html', {'form':form, 'token':token, 'uidb64':uidb64})
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        pass

    form = SetPasswordForm(user)
    return render(request, 'app/password_reset_confirm.html', {'form':form, 'token':token, 'uidb64':uidb64})


