from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Curso(models.Model):
    nome = models.CharField(max_length=200)

    def __str__(self):
        return self.nome


class Aluno(models.Model):
    ANO_CHOICES = [(1, 1), (2, 2), (3, 3)]
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None)
    numero = models.CharField(max_length=100)
    curso = models.ForeignKey(
        Curso, on_delete=models.CASCADE, related_name='alunos')
    ano = models.IntegerField(choices=ANO_CHOICES, null=True)

    @property
    def nome_completo(self):
        return self.user.first_name + ' ' + self.user.last_name.split()[-1]

    class Meta:
        ordering = ['user__first_name', 'user__last_name']

    def __str__(self):
        return self.nome_completo


class Disciplina(models.Model):
    nome = models.CharField(max_length=100)
    ano = models.IntegerField(null=True, blank=True)
    semestre = models.IntegerField(null=True, blank=True)
    alunos = models.ManyToManyField(
        Aluno, related_name='disciplinas')

    @property
    def inscritos(self):
        return len(self.alunos.all())

    def __str__(self):
        return self.nome


class Turma(models.Model):
    nome = models.CharField(max_length=100)
    disciplina = models.ForeignKey(
        Disciplina, on_delete=models.CASCADE, related_name='turmas')
    lotacao = models.IntegerField(null=True, blank=True)
    alunos = models.ManyToManyField(
        Aluno, related_name='turmas')

    @property
    def inscritos(self):
        return len(self.alunos.all())

    def __str__(self):
        return f"{self.nome}"
