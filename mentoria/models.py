from django.db import models
from app.models import *
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

class AnoLectivo(models.Model):
    ano = models.CharField(max_length=5)

    def __str__(self):
        return self.ano


class Mentor(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='mentorias')
    ano_lectivo = models.ForeignKey(AnoLectivo, on_delete=models.CASCADE, related_name='mentorias')
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE, related_name='mentorias')
    nota = models.IntegerField(null=True, blank=True, default=None)
    ativo = models.BooleanField(null=True, blank=True, default=True)

    def __str__(self):
        return f"{self.aluno}, mentor de {self.disciplina}"


class Mentorando(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='mentorandias')
    ano_lectivo = models.ForeignKey(AnoLectivo, on_delete=models.CASCADE, related_name='mentorandias')
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE, related_name='mentorandias')
    ativo = models.BooleanField(null=True, blank=True, default=True)

    def __str__(self):
        return f"{self.aluno}, mentorando de {self.disciplina}"


class Diade(models.Model):
    ano_lectivo = models.ForeignKey(AnoLectivo, on_delete=models.CASCADE, related_name='diades', default=1)
    mentor =  models.ForeignKey(Mentor, on_delete=models.CASCADE, related_name='diades_mentor')
    mentorando =  models.ForeignKey(Mentorando, on_delete=models.CASCADE, related_name='diades_mentorando')
    ativo = models.BooleanField(null=True, blank=True, default=True)
    data_criacao = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.mentor.aluno}, mentor de {self.mentorando.aluno} em  {self.mentorando.disciplina}"


class Sessao(models.Model):
    diade = models.ForeignKey(Diade, on_delete=models.CASCADE, related_name='sessoes')
    data = models.DateTimeField()
    sumario = models.CharField(max_length=200)
    objetivo = models.CharField(max_length=200)
    recursos = models.CharField(max_length=200)
    avaliacao_mentor = models.IntegerField(null=True, blank=True, default=1,validators=[
            MaxValueValidator(5),
            MinValueValidator(1)
        ])
    avaliacao_mentorando = models.IntegerField(null=True, blank=True, default=1,validators=[
            MaxValueValidator(5),
            MinValueValidator(1)
        ])
    observacoes = models.CharField(max_length=200)
    planificacao_proxima_sessao = models.CharField(max_length=200)
    confirmado = models.BooleanField(default=False)
    reportado = models.BooleanField(default=False)

    def __str__(self):
        return f"sessão de {self.diade} no dia {self.data}. Sumário: {self.sumario}"
