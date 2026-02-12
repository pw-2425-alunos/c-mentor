from django.db import models
from app.models import Aluno

class Presenca(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    entrada = models.DateTimeField(auto_now_add=True, db_index=True)
    ordem = models.PositiveIntegerField(default=0, blank=True)

    def __str__(self):
        return f"{self.aluno.nome_completo} {self.entrada.strftime('%Y-%m-%d %H:%M')}"

    @property
    def date(self):
        return self.entrada.date()  # Retorna datetime.date

    @property
    def time(self):
        return self.entrada.strftime("%H:%M")  # Hora formatada HH:MM
